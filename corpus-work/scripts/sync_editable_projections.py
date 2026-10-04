"""Project already reviewed editable manifest metadata into a fresh package.

No source/body/comparison declarations, mathematics, licence or admission are
created. Output is prepared only; actual item and aggregate gates remain required.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sqlite3
import sys

HELPERS = ('schema.sql', 'rebuild_database.py', 'restore_database.py',
           'test_database.py', 'test_restore_database.py')
PROGRAMS = ('corpus_delivery_tools.py', 'merge_editable_packages.py', 'editable_delivery.py')


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def strict_load(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('duplicate JSON key: ' + key)
            result[key] = value
        return result
    return json.loads(Path(path).read_text(encoding='utf8'), object_pairs_hook=unique)


def pin(value):
    if not isinstance(value, str) or len(value) != 64 or any(c not in '0123456789abcdef' for c in value):
        raise ValueError('external pin must be64lowercase hexadecimal characters')
    return value


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf8')


def inventory(root):
    result = {}
    for path in root.rglob('*'):
        if path.is_symlink():
            raise ValueError('symlink in input package')
        if path.is_file():
            result[path.relative_to(root).as_posix()] = sha(path)
    return result


def sync(package, manifest_pin, master, helper_pins, helper_pins_pin, output):
    package, master = Path(package).resolve(), Path(master).resolve()
    output = Path(output).absolute()
    if output.exists() or output.is_symlink():
        raise ValueError('fresh output required; preserve different existing output')
    if output.resolve().is_relative_to(package) or output.resolve().is_relative_to(master):
        raise ValueError('output cannot be inside immutable inputs')
    if sha(package / 'manifest.json') != pin(manifest_pin):
        raise ValueError('external reviewed manifest pin mismatch')
    if sha(helper_pins) != pin(helper_pins_pin):
        raise ValueError('external helper pin record mismatch')
    pins = strict_load(helper_pins)
    helpers = pins.get('master_helper_sha256', {})
    programs = pins.get('programme_sha256', {})
    if pins.get('schema_version') != 1 or set(helpers) != set(HELPERS) or set(programs) != set(PROGRAMS):
        raise ValueError('complete fixed Repo helper/current checking programme pins required')
    scripts = master.parent / 'corpus-work/scripts'
    for name in HELPERS:
        if sha(master / name) != pin(helpers[name]):
            raise ValueError('fixed helper identity mismatch: ' + name)
    for name in PROGRAMS:
        if sha(scripts / name) != pin(programs[name]):
            raise ValueError('current checking programme identity mismatch: ' + name)
    if sha(package / 'schema.sql') != helpers['schema.sql']:
        raise ValueError('schema differs; no automatic migration')
    sys.path.insert(0, str(scripts))
    from corpus_delivery_tools import local, ordinary
    from merge_editable_packages import validate_union, local as safe_package_path
    from editable_delivery import check_bodies
    before = inventory(package)
    if 'corpus.sqlite.tmp' in before:
        raise ValueError('preexisting temporary database; preserve and investigate')
    manifest = strict_load(package / 'manifest.json')
    evidence = strict_load(package / 'delivery-evidence.json')
    # This is the existing schema identity field, not a missing declaration to invent.
    if 'package_manifest_sha256' not in evidence:
        raise ValueError('existing evidence package-manifest identity field required')
    pin(evidence['package_manifest_sha256'])
    rows = manifest['items']
    ids = [row['problem_id'] for row in rows]
    if not rows or len(ids) != len(set(ids)):
        raise ValueError('empty or duplicate stable ID')
    if set(evidence.get('items', {})) != set(ids):
        raise ValueError('existing complete item evidence required; do not auto-fill')
    if manifest.get('verified_count') != len(rows):
        raise ValueError('reviewed manifest count differs; do not auto-correct it')
    validate_union([(manifest, evidence)])
    report_relative = (Path('sources') / ids[0] / 'PROJECTION_PREPARATION.json'
                       if len(ids) == 1 else
                       Path('reports') / ('projection-preparation-' + manifest_pin + '.json'))
    safe_package_path(output, report_relative.as_posix())
    # Preserve prior preparation receipts in the fresh output, without carrying
    # an unscoped root filename or overwriting the prior canonical receipt.
    prior_reports = {}
    for relative in sorted({Path('PROJECTION_PREPARATION.json'), report_relative}):
        if (package / relative).is_file():
            prior_reports[relative] = (report_relative.parent / 'projection-preparation-history' /
                                       (sha(package / relative) + '.json'))
    for row in rows:
        ident = row['problem_id']
        if row['status'] != 'verified_editable_tex':
            raise ValueError('existing verified editable material status required')
        text = ordinary(local(package, row['item_path']))
        witness = evidence['items'][ident]
        if sha(text) != row['tex_sha256'] or witness.get('item_sha256') != row['tex_sha256']:
            raise ValueError('TeX/evidence input hash mismatch: ' + ident)
        ordinary(local(package, row['license_path']))
        for asset in row.get('asset_dependencies', []):
            if sha(ordinary(local(package, asset['path']))) != pin(asset['sha256']):
                raise ValueError('declared asset hash mismatch')
        failures = check_bodies(package, row, witness, package)
        if failures:
            raise ValueError('source/body/comparison declaration invalid: ' + '; '.join(failures))
        receipt = strict_load(ordinary(local(package, row['compile_receipt'])))
        expected_assets = {asset['path']: asset['sha256'] for asset in row.get('asset_dependencies', [])}
        if (receipt.get('problem_id') != ident or receipt.get('ok') is not True or
                type(receipt.get('passes')) is not int or not 2 <= receipt['passes'] <= 4 or
                receipt.get('shell_escape') is not False or receipt.get('input_sha256') != row['tex_sha256'] or
                receipt.get('dependency_sha256') != expected_assets or
                any(receipt.get(key) for key in ('rerun_requests', 'unresolved_references', 'missing_characters', 'multiply_defined_labels'))):
            raise ValueError('failing or inconsistent actual compile receipt: ' + ident)
        for field in ('pdf_sha256', 'compiler_log_sha256'):
            pin(receipt.get(field))
        for field in ('title', 'difficulty_level', 'item_path', 'source_url'):
            if not isinstance(row.get(field), str) or any(c in row[field] for c in ('|', '\r', '\n')):
                raise ValueError('metadata cannot be represented in the current five-column INDEX: ' + field)
    # Copy2, never hardlinks: the following derived files must not mutate inputs.
    excluded_copy_paths = {Path('corpus.sqlite'), *prior_reports}
    shutil.copytree(package, output, ignore=lambda directory, names:
                    [name for name in names
                     if Path(directory).relative_to(package) / name in excluded_copy_paths])
    for prior, history in prior_reports.items():
        target = output / history
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            if sha(target) != sha(package / prior):
                raise ValueError('conflicting preparation report history')
        else:
            shutil.copy2(package / prior, target)
    for name in HELPERS:
        if not (output / name).is_file() or sha(output / name) != helpers[name]:
            shutil.copy2(master / name, output / name)
    for row in rows:
        dump(output / ('sources/' + row['problem_id'] + '/provenance.json'), row)
    index = ['# Editable mathematical proof material projections', '',
             '| ID | Title | Difficulty | Editable TeX | Source |', '|---|---|---|---|---|']
    for row in sorted(rows, key=lambda value: int(value['problem_id'])):
        url = row.get('primary', {}).get('tag_url', row['source_url'])
        index.append('| ' + row['problem_id'] + ' | ' + row['title'] + ' | ' + row['difficulty_level'] +
                     ' | [TeX](' + row['item_path'] + ') | [source](' + url + ') [provenance](sources/' +
                     row['problem_id'] + '/provenance.json) |')
    (output / 'INDEX.md').write_text('\n'.join(index) + '\n', encoding='utf8')
    evidence['package_manifest_sha256'] = manifest_pin
    dump(output / 'delivery-evidence.json', evidence)
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location('fixed_projection_rebuild', output / 'rebuild_database.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    count = module.rebuild(output, output / 'corpus.sqlite')  # Real current API; CLI has no --package.
    allowed = {'INDEX.md', 'delivery-evidence.json', 'corpus.sqlite', *HELPERS,
               *('sources/' + ident + '/provenance.json' for ident in ids),
               *(name.as_posix() for name in prior_reports),
               *(name.as_posix() for name in prior_reports.values())}
    after = inventory(output)
    changed = {name for name in before.keys() | after.keys() if before.get(name) != after.get(name)}
    if changed - allowed or inventory(package) != before or sha(output / 'manifest.json') != manifest_pin:
        raise ValueError('unexpected immutable input/output change')
    old_evidence = strict_load(package / 'delivery-evidence.json')
    old_evidence['package_manifest_sha256'] = manifest_pin
    if strict_load(output / 'delivery-evidence.json') != old_evidence:
        raise ValueError('evidence declarations changed beyond existing identity field')
    with sqlite3.connect((output / 'corpus.sqlite').as_uri() + '?mode=ro', uri=True) as db:
        if db.execute('PRAGMA integrity_check').fetchone()[0] != 'ok' or db.execute('PRAGMA foreign_key_check').fetchall():
            raise ValueError('rebuilt SQL integrity/foreign key mismatch')
        actual_ids = {r[0] for r in db.execute('SELECT problem_id FROM problems')}
        if actual_ids != set(ids) or count != len(ids):
            raise ValueError('rebuilt SQL identity/count mismatch')
    result = dict(status='prepared_projections_not_admitted_or_gate_passed', package=str(output),
        reviewed_manifest_sha256=manifest_pin, manifest_preserved=True, mathematical_source_license_asset_receipt_bytes_preserved=True,
        evidence_changed_only_existing_package_manifest_sha256=True, items=count, changed_files=sorted(changed),
        SQLite_sha256=sha(output/'corpus.sqlite'), fixed_master_helper_sha256=helpers,
        programme_sha256=programs, fresh_compilation_performed=False, remote_delivered_increment=0,
        compile_scope='Existing receipt input/assets/PDF/log pins and warning fields checked; external actual artifacts must still pass full gate.',
        required_next_action='Run explicit actual per-item and aggregate editable-delivery with matching actual build/receipts, then separate root merge/public restoration.')
    result['report_path'] = report_relative.as_posix()
    dump(output / report_relative, result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('package', 'master-helpers', 'helper-pins', 'output'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--manifest-sha256', required=True)
    parser.add_argument('--helper-pins-sha256', required=True)
    args = parser.parse_args()
    print(json.dumps(sync(args.package, args.manifest_sha256, args.master_helpers,
                         args.helper_pins, args.helper_pins_sha256, args.output), indent=2))


if __name__ == '__main__':
    sys.dont_write_bytecode = True
    main()
