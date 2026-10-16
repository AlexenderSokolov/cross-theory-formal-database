"""Fixed-version author works and local entry references; no proof certification.

Callers own serialization of shared writes. Author originals are read-only;
entries retain their supplied identifiers until the existing writer adopts them.
"""
from __future__ import annotations

import copy
import itertools
import json
import os
from pathlib import Path
import re
import shutil
import sqlite3
import contextlib
import tempfile
from urllib.parse import quote

STATUS = 'complete_author_material'
INDEX_VERSION = 'author-structure-v1'
IDENTITY = ('work_key', 'source_id', 'source_version', 'material_format')
MIGRATION_TYPE = 'shared_work_reference_migration'


def require(value, message):
    if not value:
        raise ValueError(message)


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def save(path, value):
    import prepared_delivery as d
    d.save(path, value)


def inside(root, relative):
    root = Path(root).resolve()
    relative = Path(relative)
    require(not relative.is_absolute() and '..' not in relative.parts, 'relative author path required')
    target = (root / relative).resolve()
    require(target.is_relative_to(root), 'author path escapes work root')
    return target


def read_registry(path):
    path = Path(path)
    if not path.exists():
        return {}
    records = [json.loads(line) for line in path.read_text(encoding='utf-8-sig').splitlines() if line.strip()]
    require(len({r['work_key'] for r in records}) == len(records), 'duplicate work identity')
    return {r['work_key']: r for r in records}


def write_registry(path, records):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile('w', encoding='utf-8', dir=path.parent,
                                     prefix='.' + path.name + '.', delete=False) as stream:
        for record in records.values():
            stream.write(json.dumps(record, ensure_ascii=False) + '\n')
        stream.flush()
        os.fsync(stream.fileno())
        temporary = stream.name
    os.replace(temporary, path)


def work_root(work, registry):
    root = Path(work['root'])
    return root.resolve() if root.is_absolute() else inside(Path(registry).parent, root)


def register_work(registry, work, *, index_root):
    """Register an explicitly located version once, reusing supplied indexes."""
    records = read_registry(registry)
    require(all(isinstance(work.get(k), str) and work[k] for k in IDENTITY), 'fixed work identity required')
    require(work['material_format'] in ('native_tex', 'native_lean'), 'native work format required')
    old = records.get(work['work_key'])
    if old is not None and old.get('state') != 'unresolved':
        require(all(old[k] == work[k] for k in IDENTITY) and
                work_root(old, registry) == work_root(work, registry), 'work identity conflict; preserve original')
        # Metadata does not invalidate a fixed-version inventory or structure index.
        merged = dict(old, **copy.deepcopy(work))
        for key in ('files', 'structure_index', 'index_version'):
            if key in old:
                merged[key] = old[key]
        records[work['work_key']] = merged
        write_registry(registry, records)
        return merged
    record = copy.deepcopy(work)
    if old:
        record = dict(old, **record, state='registered')
    root = work_root(record, registry)
    require(root.is_dir(), 'explicit author work root missing')
    record['root'] = str(root)
    files = record.get('files')
    if files is None:
        files = [p.relative_to(root).as_posix() for p in sorted(root.rglob('*'))
                 if p.is_file() and '.git' not in p.relative_to(root).parts]
    require(files and len(set(files)) == len(files), 'complete work inventory required')
    require(all(inside(root, name).is_file() for name in files), 'work inventory contains missing asset')
    record['files'] = list(files)
    record['supported_formats'] = sorted({record['material_format']} |
        ({'native_tex'} if any(Path(name).suffix == '.tex' for name in files) else set()) |
        ({'native_lean'} if any(Path(name).suffix == '.lean' for name in files) else set()))
    if record['material_format'] == 'native_lean':
        environment = record.get('environment', {})
        if environment.get('toolchain_file') and not environment.get('toolchain'):
            environment['toolchain'] = inside(root, environment['toolchain_file']).read_text(encoding='utf-8-sig').strip()
    existing = record.get('structure_index')
    if existing:
        require(Path(existing).is_file(), 'declared existing structure index missing')
    else:
        results = []
        suffix = '.lean' if record['material_format'] == 'native_lean' else '.tex'
        pattern = (r'^\s*(?:(?:private|protected|noncomputable|unsafe|public)\s+)*(?:theorem|lemma|def|instance|structure|class)\s+(\S+)' if suffix == '.lean'
                   else r'\\(?:label|section|chapter|begin)\s*\{([^}]+)\}')
        for name in files:
            if Path(name).suffix != suffix:
                continue
            with inside(root, name).open(encoding='utf-8-sig', errors='replace') as stream:
                for number, line in enumerate(stream, 1):
                    match = re.search(pattern, line)
                    if match:
                        results.append({'path': name, 'line': number, 'label': match.group(1)})
        index = Path(index_root).resolve() / (quote(record['work_key'], safe='') + '.json')
        save(index, {'work_key': record['work_key'], 'source_version': record['source_version'],
                     'index_version': INDEX_VERSION, 'results': results})
        record['structure_index'] = str(index)
    record['index_version'] = record.get('index_version', INDEX_VERSION)
    records[record['work_key']] = record
    write_registry(registry, records)
    return record


def _spans(entry, key, alias):
    spans = entry.get(key, entry.get(alias, []))
    require(isinstance(spans, list), 'explicit source span list required: ' + key)
    for span in spans:
        require(isinstance(span, dict) and isinstance(span.get('path'), str) and
                type(span.get('start_line')) is int and type(span.get('end_line')) is int and
                1 <= span['start_line'] <= span['end_line'], 'invalid source span')
    return spans


def resolve_entry(entry, registry):
    """Read only requested spans; no inventory rebuild, dependency walk or build."""
    ref = entry.get('work_ref', {'work_key': entry.get('work_key')})
    work = read_registry(registry).get(ref.get('work_key'))
    require(work is not None, 'work reference unresolved')
    allowed_identities = [(work['source_id'], work['source_version'])] + [tuple(pair) for pair in work.get('source_aliases', [])]
    require((entry.get('source_id'), entry.get('source_version')) in allowed_identities, 'entry/work fixed identity conflict')
    root = work_root(work, registry)
    material_format = entry.get('material_format') or work['material_format']
    require(material_format in work.get('supported_formats', [work['material_format']]), 'entry format not present in fixed author work')
    groups = {'statement': _spans(entry, 'statement_spans', 'primary'),
              'proof': _spans(entry, 'proof_spans', 'proof_spans'),
              'context': _spans(entry, 'context_spans', 'contexts')}
    missing, loaded = [], {}
    for spans in groups.values():
        for span in spans:
            name = span['path']
            path = inside(root, work.get('path_aliases', {}).get(name, name))
            if not path.is_file():
                missing.append(name)
                continue
            end = max(s['end_line'] for values in groups.values() for s in values if s['path'] == name)
            if name not in loaded:
                with path.open(encoding='utf-8-sig', errors='replace') as stream:
                    loaded[name] = list(itertools.islice(stream, end))
            if len(loaded[name]) < span['end_line']:
                missing.append(name + ': span exceeds retained source')
    output = {key: [dict(span, text=''.join(loaded.get(span['path'], [])[span['start_line']-1:span['end_line']]))
                    for span in spans] for key, spans in groups.items()}
    state = 'complete' if groups['statement'] and groups['proof'] and not missing else 'pending_material'
    if entry.get('proof_state') in ('placeholder', 'incomplete'):
        state = 'pending_author_proof'
    if material_format == 'native_lean':
        # Scope is the selected proof bodies, never every import in the project.
        for span in output['proof']:
            text = re.sub(r'/\-.*?\-/', '', span['text'], flags=re.S)
            text = re.sub(r'--[^\n]*|"(?:\\.|[^"\\])*"', '', text)
            if re.search(r'\b(?:sorry|admit)\b', text):
                state = 'pending_author_proof'
        environment = work.get('environment', {})
        required = environment.get('lock_files', []) + ([environment['toolchain_file']] if environment.get('toolchain_file') else [])
        missing.extend(name for name in required if not inside(root, name).is_file())
        if not environment.get('toolchain_file') or missing:
            state = 'pending_environment_reference'
    dedup = entry.get('dedup', entry.get('semantic_dedup', {}))
    decision = dedup.get('decision', dedup.get('status', dedup.get('conclusion')))
    unique = decision in ('unique', 'unique_within_reviewed_scope', 'focused_semantic_uniqueness_supported')
    readable = material_format == 'native_lean' or bool(entry.get('readability', work.get('readability', {})).get('basis'))
    eligible = (state == 'complete' and readable and entry.get('difficulty_level') in ('H2', 'H3') and
                bool(entry.get('difficulty_reason')) and unique and bool(dedup.get('scope')))
    return dict(output, material_state=state, eligible=eligible, missing_materials=sorted(set(missing)),
                run_state=entry.get('run_state', 'not_run'), material_format=material_format)


def prepare_entry(task, registry, output_root):
    """Prepare a candidate reference, preserving author data and unknown fields."""
    work_key = task.get('work_key') or task.get('work_ref', {}).get('work_key')
    work = read_registry(registry).get(work_key)
    require(work is not None, 'work reference unresolved')
    row = copy.deepcopy(task)
    ident = row.get('problem_id') or row.get('local_material_id') or row.get('task_id')
    require(isinstance(ident, str) and ident and ident not in ('.', '..') and '/' not in ident and '\\' not in ident, 'candidate identifier required')
    row['work_ref'] = {'work_key': work_key, 'source_version': work['source_version']}
    result = resolve_entry(row, registry)
    row.update({k: result[k] for k in ('material_state', 'eligible', 'run_state', 'material_format', 'missing_materials')})
    row.update(primary=copy.deepcopy(row.get('statement_spans', [])), contexts=copy.deepcopy(row.get('context_spans', [])),
               policy='reviewed-revision-v2', preparation_basis='author_material_collection',
               review_state='author_material_collection' if row['eligible'] else 'pending',
               dedup_state='unique_within_reviewed_scope' if row['eligible'] else 'pending',
               status=STATUS if row['eligible'] else row['material_state'], compile_receipt=None,
               tex_sha256=None, publication_commit=None, author='; '.join(row.get('authors', work.get('authors', []))),
               work=work.get('title', work_key), retrieved_at=work.get('retrieved_at', ''),
               license=work.get('license', ''), license_path=work.get('license_path', ''),
               origin_class='author_native_lean' if row['material_format'] == 'native_lean' else 'human_authored_native_tex',
               item_path=('lean' if row['material_format'] == 'native_lean' else 'tex') + '/entries/' + quote(ident, safe='') + '/entry.json')
    if row['material_format'] == 'native_lean':
        row['native_material'] = dict(row.get('native_material', {}), environment=work.get('environment', {}),
                                      toolchain=work.get('environment', {}).get('toolchain', ''),
                                      build_status=row['run_state'], author_completion_status=row['material_state'], work_key=work_key)
    target = Path(output_root) / quote(ident, safe='') / 'entry.json'
    save(target, row)
    return row


def merge_entry(manifest, entry, *, problem_id=None, same_problem_as=None):
    require(entry.get('eligible') is True, 'incomplete or unscreened candidate cannot be adopted')
    rows = manifest.setdefault('items', [])
    ident = same_problem_as or problem_id
    require(isinstance(ident, str) and ident, 'explicit existing/reserved ID required')
    require(ident not in set(map(str, manifest.get('retired_problem_ids', []))), 'retired ID cannot be reused')
    material = {k: copy.deepcopy(entry[k]) for k in ('task_id', 'revision', 'work_ref', 'statement_spans', 'proof_spans', 'context_spans') if k in entry}
    material['material_key'] = entry['task_id'] + '@' + entry['revision']
    previous = next((r for r in rows if r['problem_id'] == ident), None)
    if same_problem_as:
        require(previous is not None, 'alternate proof refers to unknown problem')
        materials = previous.setdefault('materials', [])
        if not any(m['material_key'] == material['material_key'] for m in materials):
            materials.append(material)
        return {'problem_id': ident, 'increment': 0, 'relation': 'alternate_proof'}
    require(previous is None, 'reserved ID already active')
    row = dict(copy.deepcopy(entry), problem_id=ident, materials=[material])
    rows.append(row)
    manifest['verified_count'] = len(rows)
    return {'problem_id': ident, 'increment': 1}


def migrate_manifest(manifest, records):
    """One metadata pass. Unknown sources/locators stay visible and unqualified."""
    result, records = copy.deepcopy(manifest), copy.deepcopy(records)
    identities = {}
    for key, record in records.items():
        for identity in [(record.get('source_id'), record.get('source_version'))] + [tuple(pair) for pair in record.get('source_aliases', [])]:
            require(identity not in identities or identities[identity] == key, 'ambiguous registered source identity')
            identities[identity] = key
    for row in result['items']:
        if row.get('work_ref'):
            continue
        identity = row.get('source_id'), row.get('source_version')
        key = identities.get(identity)
        if key is None:
            key = str(identity[0]) + '@' + str(identity[1])
            require(key not in records or (records[key].get('source_id'), records[key].get('source_version')) == identity,
                    'unresolved work identity conflict')
            records.setdefault(key, dict(work_key=key, source_id=identity[0], source_version=identity[1], root=None,
                material_format='native_lean' if row.get('origin_class') == 'author_native_lean' else 'native_tex',
                state='unresolved', title=row.get('work', ''), authors=row.get('authors', [])))
            identities[identity] = key
        row['work_ref'] = dict(work_key=key, source_version=identity[1],
                               resolution='unresolved' if records[key].get('state') == 'unresolved' else 'legacy_locator_retained')
    result.update(work_registry='work-registry.jsonl', shared_layout_version=1)
    return result, records


def migration_record(original, migrated, *, basis_public_commit, set_id, approved_by):
    require([r['problem_id'] for r in original['items']] == [r['problem_id'] for r in migrated['items']], 'migration must preserve IDs/order')
    return dict(schema_version=2, record_type=MIGRATION_TYPE, qualification_set_id=set_id, approved_by=approved_by,
                basis_public_commit=basis_public_commit, material_increment=0,
                status='approved_metadata_projection_pending_public_delivery',
                updates=[dict(problem_id=row['problem_id'], source_id=row['source_id'], source_version=row.get('source_version'),
                              work_ref=row['work_ref']) for old, row in zip(original['items'], migrated['items']) if 'work_ref' not in old])


def validate_migration_record(record):
    require(record.get('record_type') == MIGRATION_TYPE and record.get('material_increment') == 0 and
            record.get('status') == 'approved_metadata_projection_pending_public_delivery' and record.get('approved_by'),
            'explicit shared metadata migration approval required')
    rows = record.get('updates')
    require(isinstance(rows, list) and rows and len({r['problem_id'] for r in rows}) == len(rows), 'migration IDs must be unique')
    require(all(isinstance(r['problem_id'], str) and r.get('source_id') and r.get('work_ref', {}).get('work_key') and
                r['work_ref'].get('resolution') in ('unresolved', 'legacy_locator_retained') for r in rows), 'migration locator disposition missing')
    return record


def apply_migration(database, manifest, record):
    import prepared_delivery as d
    validate_migration_record(record)
    by_id = {row['problem_id']: row for row in manifest['items']}
    require(set(r['problem_id'] for r in record['updates']) <= set(by_id), 'migration cannot create or discard material')
    with contextlib.closing(sqlite3.connect(database)) as db, db:
        for update in record['updates']:
            row = by_id[update['problem_id']]
            require((row['source_id'], row.get('source_version')) == (update['source_id'], update.get('source_version')), 'migration fixed source changed')
            previous = db.execute('SELECT source_id,source_locator_json FROM problems WHERE problem_id=?', (row['problem_id'],)).fetchone()
            require(previous is not None and previous[0] == row['source_id'], 'migration database identity differs')
            old_locator = json.loads(previous[1])
            extensions = {k: v for k, v in old_locator.items() if k not in d.locator(row)}
            if extensions:
                row['locator_extensions'] = dict(row.get('locator_extensions', {}), **extensions)
            row['work_ref'] = copy.deepcopy(update['work_ref'])
            db.execute('UPDATE problems SET source_locator_json=? WHERE problem_id=?',
                       (json.dumps(d.locator(row), ensure_ascii=False), row['problem_id']))
    manifest.update(work_registry='work-registry.jsonl', shared_layout_version=1)
    return {'qualification_set_id': record['qualification_set_id'], 'updated_count': len(record['updates']), 'material_increment': 0}


def project_registry(database, records):
    """Keep a query projection; only changed work metadata is written."""
    with contextlib.closing(sqlite3.connect(database)) as db, db:
        db.execute('CREATE TABLE IF NOT EXISTS works(work_key TEXT PRIMARY KEY, record_json TEXT NOT NULL)')
        columns = {row[1] for row in db.execute('PRAGMA table_info(works)')}
        require({'work_key', 'record_json'} <= columns, 'existing works extension is incompatible; preserve it')
        old = {key: json.loads(value) for key, value in db.execute('SELECT work_key,record_json FROM works')}
        for key, record in records.items():
            canonical = copy.deepcopy(record)
            if 'public_root' in canonical:
                public_root = canonical.pop('public_root')
                if public_root is not None:
                    canonical['root'] = public_root
            if key in old:
                canonical = dict(old[key], **canonical)
                if old[key] != canonical:
                    db.execute('UPDATE works SET record_json=? WHERE work_key=?', (json.dumps(canonical, ensure_ascii=False), key))
            else:
                db.execute('INSERT INTO works(work_key,record_json) VALUES (?,?)', (key, json.dumps(canonical, ensure_ascii=False)))


def publish_work(registry, work_key, corpus):
    """Publish one work, carrying its existing index without rescanning originals."""
    work = copy.deepcopy(read_registry(registry)[work_key])
    require(work.get('public_redistribution_supported') is True, 'work public licence remains on hold')
    public_registry = Path(corpus) / 'work-registry.jsonl'
    existing = read_registry(public_registry).get(work_key)
    if existing and existing.get('state') not in ('unresolved', 'not_published'):
        require(all(existing[k] == work[k] for k in IDENTITY), 'public work identity conflict')
        aliases = copy.deepcopy(existing.get('source_aliases') or [])
        for alias in work.get('source_aliases') or []:
            require(isinstance(alias, list) and len(alias) == 2 and
                    all(isinstance(value, str) and value for value in alias),
                    'explicit fixed source alias pair required')
            if alias not in aliases:
                aliases.append(copy.deepcopy(alias))
        if aliases != (existing.get('source_aliases') or []):
            existing = dict(existing, source_aliases=aliases)
            records = read_registry(public_registry)
            records[work_key] = existing
            write_registry(public_registry, records)
        if existing.get('structure_index') or not work.get('structure_index'):
            return existing, []
    index_name = 'metadata/structure-index.json'
    index_source = work.get('structure_index')
    if index_source:
        index_source = Path(index_source)
        if not index_source.is_absolute():
            index_source = inside(work_root(work, registry), index_source)
        require(index_source.is_file(), 'declared existing structure index missing')
    relative = ('lean' if work['material_format'] == 'native_lean' else 'tex') + '/works/' + quote(work_key, safe='')
    if existing and existing.get('state') not in ('unresolved', 'not_published'):
        relative = existing.get('public_root') or relative
        dst = inside(corpus, relative + '/' + index_name)
        require(not dst.exists(), 'public index output already exists without registration')
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(index_source, dst)
        updated = copy.deepcopy(existing)
        updated['structure_index'] = index_name
        updated['files'] = list(dict.fromkeys(list(updated.get('files', [])) + [index_name]))
        records = read_registry(public_registry)
        records[work_key] = updated
        write_registry(public_registry, records)
        return updated, [relative + '/' + index_name]
    source = work_root(work, registry)
    assets = []
    asset_sources = dict(work.get('asset_sources', {}))
    if index_source:
        asset_sources.setdefault(index_name, str(index_source))
        require(Path(asset_sources[index_name]).resolve() == index_source.resolve(),
                'declared index asset differs from the registered structure index')
    for name in dict.fromkeys(list(work['files']) + list(asset_sources)):
        dst = inside(corpus, relative + '/' + name)
        require(not dst.exists(), 'public work output already exists without registration')
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(Path(asset_sources[name]) if name in asset_sources else inside(source, name), dst)
        assets.append(relative + '/' + name)
    work['files'] = list(dict.fromkeys(list(work['files']) + list(asset_sources)))
    work.pop('asset_sources', None)
    work.update(root=relative, structure_index=index_name if index_source else None, state='published')
    records = read_registry(public_registry)
    records[work_key] = work
    write_registry(public_registry, records)
    return work, assets
