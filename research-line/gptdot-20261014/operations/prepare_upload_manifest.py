#!/usr/bin/env python3
"""Print a read-only preparation-branch upload manifest; never stage or publish.

Paths are relative to the repository root. Each file records bytes and the GitHub
blob encoding (utf-8 or base64), not its contents. Run again after changing export.
Only explicit public dependencies and selected successful products are included.
"""
import argparse
import json
from pathlib import Path
import re
import sqlite3
from urllib.parse import unquote, urlsplit

LINE = 'research-line/gptdot-20261014'
PREFIX = 'GPDOT261014-'
SECRET = re.compile(rb'(?:sk-[A-Za-z0-9_-]{24,}|gh[pousr]_[A-Za-z0-9]{25,}|github_pat_[A-Za-z0-9_]{30,}|-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----)')
FORBIDDEN = {'private', 'private-reference', 'private-references', 'tmp', 'temp', '__pycache__', 'cache', 'nonredistributable', 'non-redistributable', 'snapshots', 'identity-snapshots', 'cross-line-snapshot'}
INTERMEDIATES = {'.aux', '.log', '.out', '.toc', '.fls', '.fdb_latexmk', '.synctex', '.pyc', '.stdout', '.blg'}


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def safe_path(base, value):
    """No absolute, traversing, symlink, hidden, temporary or private paths."""
    value = Path(value)
    if value.is_absolute() or not value.parts or '..' in value.parts:
        raise ValueError(f'Unsafe path: {value}')
    path = base / value
    for part in value.parts:
        low = part.lower()
        if low.startswith('.') or low in FORBIDDEN or low.startswith(('qa-root-', 'private-', 'nonredistributable')):
            raise ValueError(f'Non-public path: {value}')
    for ancestor in (path, *path.parents):
        if ancestor == base:
            break
        if ancestor.is_symlink():
            raise ValueError(f'Symlink not allowed: {value}')
    if path.suffix.lower() in INTERMEDIATES or path.name.endswith('.synctex.gz'):
        raise ValueError(f'Build intermediate: {value}')
    return path


def prepare(root, batch='batch-001'):
    root = Path(root).resolve()
    line = root / LINE
    if not re.fullmatch(r'batch-\d{3}', batch):
        raise ValueError('Expected batch-NNN')
    delivery = line / 'delivery' / batch
    items = [json.loads(s) for s in (delivery / 'ITEMS.jsonl').read_text().splitlines() if s.strip()]
    ids = [item['task_id'] for item in items]
    selected = load(delivery / 'SELECTION.json')['task_ids']
    if not ids or len(ids) != len(set(ids)) or len(selected) != len(set(selected)) or set(ids) != set(selected):
        raise ValueError('ITEMS and SELECTION must contain the same nonempty unique tasks')
    if any(not tid.startswith(PREFIX) for tid in ids):
        raise ValueError('Foreign task prefix')
    files = set()

    def add(path):
        relative = path.relative_to(line)
        path = safe_path(line, relative)
        if not path.is_file():
            raise ValueError(f'Missing file: {path.relative_to(root)}')
        if SECRET.search(path.read_bytes()):
            raise ValueError(f'Possible secret: {path.relative_to(root)}')
        files.add(path.relative_to(root).as_posix())
        return path

    originals = {tid: [] for tid in ids}
    # Canonical task.json only; package snapshots and archived revisions are not candidates.
    for path in line.rglob('task.json'):
        if any(part.startswith('.') or part in {'jobs', 'delivery', 'operations', 'revisions'} for part in path.relative_to(line).parts):
            continue
        task = load(path)
        if task.get('task_id') in originals:
            originals[task['task_id']].append(path)

    for item in items:
        tid = item['task_id']
        if len(originals[tid]) != 1:
            raise ValueError(f'{tid}: expected exactly one original task, found {len(originals[tid])}')
        task_path = originals[tid][0]
        task = load(task_path)
        public = task.get('public_dependency_paths')
        if public is None:
            # Existing material groups may publish a separate explicit whitelist.
            candidates = [d / 'public-material-selection.json' for d in (task_path.parent, task_path.parent.parent)]
            matches = [f for f in candidates if f.is_file() and task_path.relative_to(line).as_posix() in load(f).get('explicit_public_files', [])]
            if len(matches) != 1:
                raise ValueError(f'{tid}: missing unambiguous explicit public whitelist')
            public = load(matches[0])['explicit_public_files']
            add(matches[0])
        if not isinstance(public, list) or not public or any(not isinstance(p, str) for p in public):
            raise ValueError(f'{tid}: invalid public whitelist')
        allowed = {safe_path(line, p) for p in public}

        def original(value):
            path = safe_path(line, value)
            if path not in allowed:
                raise ValueError(f'{tid}: dependency is not publicly whitelisted: {value}')
            return add(path)

        original(task_path.relative_to(line))
        for path in sorted(allowed):
            if path.relative_to(line).parts[0] in {'jobs', 'delivery', 'operations'}:
                raise ValueError(f'{tid}: public source whitelist includes generated/control files')
            if path.name == 'task.json' and load(path).get('task_id') not in ids:
                raise ValueError(f'{tid}: public source whitelist includes an unselected task')
            add(path)
        assembly = task['assembly']
        for spans in [task['statement_spans'], task['proof_spans'], task['context_spans'], assembly['preamble_spans'], assembly['body_spans']]:
            for span in spans:
                original(span['path'])
        for ref in assembly.get('external_references', []):
            if ref.get('source_span'):
                original(ref['source_span']['path'])
        original(task['license']['evidence_path'])
        job = safe_path(root, item['assembly_job'])
        if job != line / 'jobs' / tid / item['revision']:
            raise ValueError(f'{tid}: unexpected job path')
        state = load(add(job / 'job-state.json'))
        if state['status'] != 'compiled_pending_qa':
            raise ValueError(f'{tid}: job has no successful compiled state')
        package = safe_path(job, state['package'])
        snapshot = load(add(safe_path(package, state['task_snapshot'])))
        manifest = load(add(package / 'manifest.json'))
        if len(manifest['items']) != 1:
            raise ValueError(f'{tid}: expected one packaged item')
        row = manifest['items'][0]
        for obj in (task, state, snapshot, row):
            if any(obj.get(k) != item[k] for k in ('task_id', 'revision', 'source_id', 'claim_key')):
                raise ValueError(f'{tid}: task/package/export identity mismatch')
        receipt = load(add(safe_path(package, row['compile_receipt'])))
        if receipt.get('ok') is not True or any(receipt.get(k) != item[k] for k in ('task_id', 'revision', 'source_id', 'claim_key')):
            raise ValueError(f'{tid}: invalid compile receipt')
        visual = load(add(job / 'visual-qa.json'))
        pages = visual.get('pages')
        if (visual.get('task_id') != tid or visual.get('result') != 'readable'
                or type(pages) is not int or pages <= 0
                or ('pages' in receipt and pages != receipt['pages'])):
            raise ValueError(f'{tid}: missing or unsuccessful visual QA')
        tex = add(safe_path(package, row['item_path']))
        pdf = add(safe_path(job, receipt['pdf_path']))
        if tex.relative_to(root).as_posix() != item['tex_path'] or pdf.relative_to(root).as_posix() != item['pdf_path']:
            raise ValueError(f'{tid}: exported product path mismatch')
        for key in ('license_path', 'license_evidence_path'):
            add(safe_path(package, row[key]))
        for name in ('provenance.json', 'content-review.json'):
            add(package / 'sources' / tid / name)
        for name in ('source-map.json', 'delivery-evidence.json'):
            add(package / name)
        external_receipt = load(add(safe_path(job, state['receipt_root']) / (tid + '.json')))
        if external_receipt.get('ok') is not True or any(external_receipt.get(k) != item[k] for k in ('task_id', 'revision', 'source_id', 'claim_key')):
            raise ValueError(f'{tid}: invalid external compile receipt')
        for source in row['source_files']:
            original(source['original_path'])
            add(safe_path(package, source['path']))
        targets = set()
        for key in ('asset_paths', 'bibliography_paths'):
            for asset in assembly.get(key, []):
                source = asset if isinstance(asset, str) else asset['path']
                original(source)
                target = ('items/' + Path(source).name) if isinstance(asset, str) else asset.get('target', 'items/' + Path(source).name)
                targets.add(target)
                add(safe_path(package, target))
        if targets != {asset['path'] for asset in row['asset_dependencies']}:
            raise ValueError(f'{tid}: package assets differ from whitelisted task assets')

    for name in ('ITEMS.jsonl', 'SELECTION.json', 'INDEX.md', 'corpus.sqlite3'):
        add(delivery / name)
    # A whole database must not silently carry unselected/private historical rows.
    dbpath = delivery / 'corpus.sqlite3'
    if any(Path(str(dbpath) + suffix).exists() for suffix in ('-wal', '-journal')):
        raise ValueError('SQLite has a live journal; finish export before manifest preparation')
    with sqlite3.connect(dbpath.as_uri() + '?mode=ro', uri=True) as db:
        rows = db.execute('SELECT task_id, state, tex_path, pdf_path FROM problems').fetchall()
    if len(rows) != len(ids) or {r[0] for r in rows} != set(ids) or any(r[1] != 'prepared_unpublished' for r in rows):
        raise ValueError('Whole SQLite contains missing, unselected, or non-prepared rows')
    by_id = {item['task_id']: item for item in items}
    for tid, _, tex, pdf in rows:
        if (tex, pdf) != (by_id[tid]['tex_path'], by_id[tid]['pdf_path']):
            raise ValueError(f'{tid}: SQLite/export paths differ')
    for link in re.findall(r'\]\(([^)]+)\)', (delivery / 'INDEX.md').read_text()):
        url = urlsplit(link)
        if url.scheme or url.netloc or not url.path:
            continue
        target = (delivery / unquote(url.path)).resolve()
        if not target.is_relative_to(root) or target.relative_to(root).as_posix() not in files:
            raise ValueError(f'INDEX link is not selected for upload: {link}')
    for path in sorted((line / 'operations').iterdir()):
        if path.is_file() and path.suffix in {'.py', '.sh'}:
            add(path)
    entries = []
    for name in sorted(files):
        data = (root / name).read_bytes()
        try:
            data.decode('utf-8')
            encoding = 'base64' if b'\0' in data else 'utf-8'
        except UnicodeDecodeError:
            encoding = 'base64'
        entries.append({'path': name, 'bytes': len(data), 'encoding': encoding})
    return {'batch': batch, 'state': 'prepared_unpublished', 'selected_count': len(ids), 'task_ids': sorted(ids), 'file_count': len(entries), 'total_bytes': sum(f['bytes'] for f in entries), 'files': entries}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--batch', default='batch-001')
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[3])
    args = parser.parse_args()
    try:
        print(json.dumps(prepare(args.root, args.batch), ensure_ascii=False, indent=2))
    except (ValueError, KeyError, OSError, sqlite3.Error) as exc:
        parser.exit(1, f'Upload manifest refused: {exc}\n')
