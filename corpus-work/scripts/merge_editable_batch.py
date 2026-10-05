"""Merge already accepted final packets once into a fresh package.

SPEC keeps base/incoming package and compile roots. Each incoming supplies
accepted_report (or accepted_reports), with path and the existing final
manifest_sha256 binding. Explicit paths or old reviewed_filemap keys select
copy inputs. No per-step directory fingerprints, reviews or SQL rebuilds.
"""
from __future__ import annotations
import argparse
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
import merge_editable_packages as core
from corpus_delivery_tools import check_report, load as strict_load

HELPERS = ('schema.sql', 'rebuild_database.py', 'test_database.py',
           'restore_database.py', 'test_restore_database.py')


def load(path):
    return strict_load(path)


def pin(value):
    if not isinstance(value, str) or len(value) != 64 or any(c not in '0123456789abcdef' for c in value):
        raise ValueError('SHA256 must be exactly64 lowercase hex characters')
    return value


def programme_paths():
    scripts = Path(__file__).resolve().parent
    return {name: scripts / name for name in ('merge_editable_packages.py',
        'merge_editable_batch.py', 'corpus_delivery_tools.py', 'validate_corpus.py',
        'editable_delivery.py', 'compile_editable_delivery.py')}


def accepted_reports(entry, package):
    """Consume existing successes; binding comes from final READY/transport input."""
    if 'accepted_report' in entry and 'accepted_reports' in entry:
        raise ValueError('use accepted_report or accepted_reports, not both')
    records = entry.get('accepted_reports')
    if records is None:
        records = [entry.get('accepted_report')]
    if not isinstance(records, list) or not records or any(not isinstance(r, dict) for r in records):
        raise ValueError('accepted report descriptors with path/final manifest identity required')
    ids = {row['problem_id'] for row in package[0]['items']}
    covered, reused = set(), []
    for record in records:
        if record.get('manifest_sha256') != entry['manifest_sha256']:
            raise ValueError('accepted report does not bind the final packet')
        report_path = Path(record['path'])
        report = load(report_path)
        selected = report.get('items', {})
        if not isinstance(selected, dict) or not selected:
            raise ValueError('accepted report covers no IDs')
        if set(selected) - ids or covered.intersection(selected):
            raise ValueError('wrong/duplicate accepted report ID coverage')
        if report.get('package_item_count') != len(ids):
            raise ValueError('accepted report belongs to another packet scope')
        if report.get('receipt_set') != str(Path(entry['receipt_root']).resolve()):
            raise ValueError('accepted report receipt root mismatch')
        reused.append(check_report(report_path, len(selected)))
        covered.update(selected)
    if covered != ids:
        raise ValueError('accepted reports do not cover all final packet IDs')
    return reused


def incoming_identity(root, package, entry):
    """Only existing declared material identities; never a whole-directory hash."""
    from corpus_delivery_tools import local, ordinary
    from editable_delivery import check_bodies
    manifest, evidence = package
    for row in manifest['items']:
        failures = check_bodies(root, row, evidence['items'][row['problem_id']], root)
        if failures:
            raise ValueError('changed/invalid final packet evidence: ' + '; '.join(failures))
        receipt = load(ordinary(local(root, row['compile_receipt'])))
        if (receipt.get('problem_id') != row['problem_id'] or receipt.get('ok') is not True or
                type(receipt.get('passes')) is not int or not 2 <= receipt['passes'] <= 4 or
                receipt.get('shell_escape') is not False or receipt.get('input_sha256') != row['tex_sha256'] or
                receipt.get('dependency_sha256') != {a['path']: a['sha256'] for a in row.get('asset_dependencies', [])}):
            raise ValueError('changed/invalid accepted compile input identity')
        external = local(Path(entry['receipt_root']).resolve(), row['problem_id'] + '.json')
        if external.read_bytes() != local(root, row['compile_receipt']).read_bytes():
            raise ValueError('final packet/internal and accepted external receipt differ')
        for field, path_field in (('pdf_sha256', 'pdf_path'), ('compiler_log_sha256', 'compiler_log_path')):
            artifact = ordinary(local(Path(entry['build_root']).resolve(), receipt[path_field]))
            if core.sha(artifact) != receipt[field]:
                raise ValueError('changed accepted compile artifact: ' + path_field)
        if any(receipt.get(k) for k in ('rerun_requests', 'unresolved_references', 'missing_characters', 'multiply_defined_labels')):
            raise ValueError('accepted compile receipt has unresolved warnings')


def preflight(spec, review, output):
    output = Path(output).absolute()
    if output.exists() or output.is_symlink():
        raise ValueError('output must be new; existing outputs are preserved')
    incoming = spec.get('incoming')
    if not isinstance(incoming, list) or not incoming:
        raise ValueError('explicit nonempty incoming list required')
    inputs = [spec['base'], *incoming]
    master = Path(spec['master_helpers']).resolve()
    if output.resolve().is_relative_to(master):
        raise ValueError('output cannot be inside master helper root')
    if (review.get('schema_version') != 1 or review.get('status') != 'material_review_complete' or
            review.get('holds') != [] or review.get('duplicates') != [] or
            not isinstance(review.get('basis'), str) or not review['basis'].strip() or
            not isinstance(review.get('compile_reuse_basis'), str) or not review['compile_reuse_basis'].strip()):
        raise ValueError('existing complete semantic/source and compile-reuse decision required')
    if review.get('base_manifest_sha256') != inputs[0]['manifest_sha256'] or review.get('incoming_manifest_sha256') != [e['manifest_sha256'] for e in incoming]:
        raise ValueError('review does not bind original base/incoming manifests')
    # Retain legacy fixed-interface pins when supplied; no new pin/filemap bundle.
    programs = programme_paths()
    if spec.get('compile_launcher'):
        programs['compile_launcher'] = Path(spec['compile_launcher']).resolve()
    for name, expected in review.get('programme_sha256', {}).items():
        if name not in programs or core.sha(programs[name]) != pin(expected):
            raise ValueError('programme identity mismatch: ' + name)
    for name, expected in review.get('master_helper_sha256', {}).items():
        if name not in HELPERS or core.sha(master / name) != pin(expected):
            raise ValueError('master helper identity mismatch: ' + name)
    fixed = {name: (master / name).read_bytes() for name in HELPERS}
    old_maps = review.get('reviewed_filemaps', {})
    old_artifacts = review.get('reviewed_artifact_filemaps', {})
    packages, roots, path_lists, artifact_lists, reused, retained_index = [], [], [], [], [], {}
    for n, entry in enumerate(inputs):
        for field in ('package', 'build_root', 'receipt_root'):
            raw = Path(entry[field]).absolute()
            if raw.is_symlink() or not raw.is_dir() or output.resolve().is_relative_to(raw.resolve()):
                raise ValueError('unsafe or mutable input/output root')
        root = Path(entry['package']).resolve()
        pin(entry['manifest_sha256'])
        package = core.load_package(root, validate_material=bool(n), expected_manifest=entry['manifest_sha256'])
        for name in HELPERS:
            if (root / name).is_symlink() or not (root / name).is_file() or (root / name).read_bytes() != fixed[name]:
                raise ValueError('input must already use final canonical helpers: ' + name)
        names = entry.get('paths')
        if names is None:
            if n == 0:
                names = old_maps.get('base')
            else:
                previous = old_maps.get('incoming', [])
                names = previous[n-1] if n <= len(previous) else None
        names = core.explicit_paths(root, names)
        if any(name not in names for name in ('manifest.json', 'delivery-evidence.json', 'INDEX.md', *HELPERS)):
            raise ValueError('explicit material paths omit required package metadata/helpers')
        required = set()
        for row in package[0]['items']:
            required.update((row['item_path'], row['compile_receipt'], row['license_path']))
            required.update(a['path'] for a in row.get('asset_dependencies', []))
            for source in package[1]['items'][row['problem_id']].get('sources', []):
                if source.get('root', 'source') != 'inline' and source.get('path'):
                    required.add(source['path'])
        if required - set(names):
            raise ValueError('explicit material paths omit declared input: ' + str(sorted(required - set(names))))
        artifacts = entry.get('artifact_paths')
        if artifacts is None:
            if n == 0:
                artifacts = old_artifacts.get('base')
            else:
                previous = old_artifacts.get('incoming', [])
                artifacts = previous[n-1] if n <= len(previous) else None
        if not isinstance(artifacts, dict):
            raise ValueError('explicit build/receipt paths required')
        build_paths = core.explicit_paths(Path(entry['build_root']).resolve(), artifacts.get('build'))
        receipt_paths = core.explicit_paths(Path(entry['receipt_root']).resolve(), artifacts.get('receipts'))
        expected_ids = {row['problem_id'] for row in package[0]['items']}
        if set(receipt_paths) != {ident + '.json' for ident in expected_ids}:
            raise ValueError('compile receipt paths do not match packet IDs')
        if any(Path(name).parts[0] not in expected_ids for name in build_paths):
            raise ValueError('build path does not belong to this packet ID')
        retained_index.update(core.index_rows(root, expected_ids))
        roots.append(root); packages.append(package); path_lists.append(names)
        artifact_lists.append({'build': build_paths, 'receipts': receipt_paths})
    core.validate_union(packages)
    for entry, package, root in zip(inputs[1:], packages[1:], roots[1:]):
        reused.extend(accepted_reports(entry, package))
        incoming_identity(root, package, entry)
    ids = [row['problem_id'] for m, _ in packages[1:] for row in m['items']]
    if sorted(review.get('incoming_ids', [])) != sorted(ids):
        raise ValueError('review incoming IDs differ from all incoming packets')
    # One collision preflight; no re-hashing/copying each progressively larger base.
    seen, unique_lists = {}, []
    for root, names in zip(roots, path_lists):
        selected = []
        for name in names:
            relative = Path(name)
            if relative.parts[0] == 'database-parts' or relative.name.endswith('.sqlite.tmp') or (len(relative.parts) == 1 and name in core.GLOBAL_FILES | set(HELPERS)):
                continue
            source = core.local(root, name)
            if name in seen:
                if not core.same_content(seen[name], source):
                    raise ValueError('conflicting package file: ' + name)
                continue
            seen[name] = source; selected.append(name)
        unique_lists.append(selected)
    return inputs, packages, roots, unique_lists, artifact_lists, retained_index, master, reused


def gate(package, build, receipts, report, validator=None):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    result = subprocess.run([sys.executable, '-B', str(validator or programme_paths()['validate_corpus.py']),
        '--mode', 'editable-delivery', '--package', str(package), '--evidence', str(package / 'delivery-evidence.json'),
        '--build-root', str(build), '--receipt-root', str(receipts), '--report', str(report)],
        env=env, capture_output=True, text=True)
    report.with_suffix('.stdout').write_text(result.stdout, encoding='utf8')
    report.with_suffix('.stderr').write_text(result.stderr, encoding='utf8')
    if result.returncode:
        raise ValueError('actual editable-delivery gate failed: ' + str(report))
    return check_report(report, len(load(package / 'manifest.json')['items']))


def reuse_immutable(source, target):
    if source.stat().st_dev == target.parent.stat().st_dev:
        os.link(source, target)
        return target
    return shutil.copy2(source, target)


def merge_batch(spec_path, review_path, review_sha256, output):
    started = time.monotonic()
    sys.dont_write_bytecode = True
    spec, review = load(spec_path), load(review_path)
    if review_sha256 is not None and core.sha(Path(review_path)) != pin(review_sha256):
        raise ValueError('external root review hash mismatch')
    inputs, packages, roots, paths, artifacts, indexes, master, reused = preflight(spec, review, output)
    output = Path(output).absolute()
    output.mkdir(parents=True)
    for directory in ('reports', 'build', 'receipts'):
        (output / directory).mkdir()
    counts = {'rebuild_calls': 0, 'gate_calls': 0, 'incoming_gate_reuse': len(reused)}
    package = output / 'package'
    try:
        items = core.assemble_packages(roots, packages, paths, indexes, master, package,
                                      [entry['manifest_sha256'] for entry in inputs])
        specifier = importlib.util.spec_from_file_location('fixed_batch_rebuild', master / 'rebuild_database.py')
        module = importlib.util.module_from_spec(specifier)
        specifier.loader.exec_module(module)
        counts['rebuild_calls'] += 1
        if module.rebuild(package, package / 'corpus.sqlite') != items:
            raise ValueError('rebuilt count differs from merged manifest')
        for entry, selected in zip(inputs, artifacts):
            for kind in ('build', 'receipts'):
                root = Path(entry['build_root' if kind == 'build' else 'receipt_root']).resolve()
                for name in selected[kind]:
                    target = output / kind / name
                    target.parent.mkdir(parents=True, exist_ok=True)
                    reuse_immutable(core.local(root, name), target)
        counts['gate_calls'] += 1
        aggregate = gate(package, output / 'build', output / 'receipts', output / 'reports/aggregate.json',
                         validator=master.parent / 'corpus-work/scripts/validate_corpus.py')
    except Exception as error:
        core.dump(output / 'batch-result.json', dict(status='failed_batch_partial_output_retained',
            error=str(error), elapsed=time.monotonic()-started, **counts))
        raise
    result = dict(status='actual_editable_batch_gate_passed_not_remote', package=str(package),
        build_root=str(output / 'build'), receipt_root=str(output / 'receipts'), actual_aggregate=aggregate,
        base_items=len(packages[0][0]['items']), incoming_items=items-len(packages[0][0]['items']), items=items,
        manifest_sha256=core.sha(package / 'manifest.json'), SQLite_sha256=core.sha(package / 'corpus.sqlite'),
        reused_accepted_reports=reused, fresh_compilation_performed=False, remote_delivered_increment=0,
        elapsed=time.monotonic()-started, **counts)
    core.dump(output / 'batch-result.json', result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('spec', 'semantic-review', 'output'):
        parser.add_argument('--'+name, type=Path, required=True)
    parser.add_argument('--semantic-review-sha256')  # Existing transport interface remains accepted.
    args = parser.parse_args()
    print(json.dumps(merge_batch(args.spec, args.semantic_review, args.semantic_review_sha256, args.output), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
