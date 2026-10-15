#!/usr/bin/env python3
"""Rebuild a read-only human catalog from this line's verified batch receipts.

Does not compile, admit, renumber, merge production, or change any source batch.
The copied problems table preserves the existing batch schema and frozen state.
The separate publication table records preparation-branch delivery provenance.
"""
import json, os, re, sqlite3
from pathlib import Path

P = Path(__file__).resolve().parent.parent
D = P / 'delivery'
R = P.parent.parent
records = []
seen = set()
schema = None
columns = None
for marker in sorted(D.glob('batch-*/UPLOADED.json')):
    receipt = json.loads(marker.read_text())
    if receipt.get('state') != 'preparation_branch_uploaded':
        raise ValueError(f'Unverified receipt: {marker}')
    if not re.fullmatch('[0-9a-f]{40}', receipt.get('commit', '')):
        raise ValueError(f'Missing fixed publication commit: {marker}')
    ids = receipt['task_ids']
    selection = json.loads((marker.parent / 'SELECTION.json').read_text())['task_ids']
    if len(ids) != len(set(ids)) or set(ids) != set(selection) or len(ids) != receipt['count']:
        raise ValueError(f'Receipt/selection mismatch: {marker}')
    db = sqlite3.connect(f'file:{marker.parent / "corpus.sqlite3"}?mode=ro', uri=True)
    assert db.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
    this_schema = db.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='problems'").fetchone()[0]
    this_columns = [r[1] for r in db.execute('PRAGMA table_info(problems)')]
    if schema is None:
        schema, columns = this_schema, this_columns
    elif this_schema != schema or this_columns != columns:
        raise ValueError('Batch schemas differ; do not silently migrate')
    for tid in ids:
        if tid in seen:
            raise ValueError(f'Duplicate stable task ID across published batches: {tid}')
        row = db.execute('SELECT * FROM problems WHERE task_id=?', (tid,)).fetchone()
        if row is None:
            raise ValueError(f'Missing complete row: {tid}')
        item = dict(zip(columns, row))
        if any(not item[k] for k in ['statement_text', 'proof_text', 'tex_content', 'license_json', 'task_json']):
            raise ValueError(f'Incomplete material: {tid}')
        for field in ['tex_path', 'pdf_path']:
            if not (R / item[field]).is_file():
                raise ValueError(f'Missing product path: {tid}: {field}')
        seen.add(tid)
        records.append((item, row, marker.parent.name, receipt['commit']))
    db.close()
if not records:
    raise ValueError('No verified published batch to catalog')

def natural(value):
    return tuple(int(s) if s.isdigit() else s for s in re.split(r'(\d+)', value))
records.sort(key=lambda r: natural(r[0]['task_id']))
tmp = D / 'published.sqlite3.tmp'
out = sqlite3.connect(tmp)
with out:
    out.execute('DROP TABLE IF EXISTS publication')
    out.execute('DROP TABLE IF EXISTS problems')
    out.execute(schema)
    out.execute('CREATE TABLE publication (task_id TEXT PRIMARY KEY REFERENCES problems(task_id), batch TEXT NOT NULL, preparation_commit TEXT NOT NULL)')
    for item, row, batch, commit in records:
        out.execute('INSERT INTO problems VALUES (' + ','.join('?' for _ in row) + ')', row)
        out.execute('INSERT INTO publication VALUES (?,?,?)', (item['task_id'], batch, commit))
assert out.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
assert out.execute('SELECT count(*) FROM problems').fetchone()[0] == len(records)
out.close()
os.replace(tmp, D / 'published.sqlite3')
lines = ['# 已公开的作者题证准备材料', '',
         f'共 {len(records)} 道本线作者题证准备材料。展示序号仅供阅读；task_id 保持不变，不是正式 problem_id 或资格计数。', '',
         '[全文 SQLite](published.sqlite3)：problems 保留完整题面、作者证明、上下文、TeX、来源和许可；publication 记录每题的固定准备分支提交。problems.state 保留原批次冻结状态，上传状态看 publication，不据此认定正式资格。', '',
         '生产主库本线公开增量为 0；后续在途去重和准入尚未确认。本索引为独立阅读入口，不替换生产 INDEX 或原批次索引。', '',
         '| 展示序 | 稳定 task_id | 题目 | 难度记录 | 成品 |',
         '|---|---|---|---|---|']
for n, (item, row, batch, commit) in enumerate(records, 1):
    tex = os.path.relpath(R / item['tex_path'], D)
    pdf = os.path.relpath(R / item['pdf_path'], D)
    title = item['title'].replace('|', r'\|').replace('\n', ' ')
    lines.append(f"| {n} | {item['task_id']} | {title} | {item['difficulty_level']} | [TeX]({tex}) · [PDF]({pdf}) |")
(D / 'INDEX.md').write_text('\n'.join(lines) + '\n')
metadata = {'prepared_author_products': len(records), 'canonical_source_ids': len({r[0]['source_id'] for r in records}), 'production_public_increment': 0, 'formal_qualified_count': None, 'display_order': [r[0]['task_id'] for r in records], 'generation': 'python operations/build_published_catalog.py', 'scope': 'Derived catalog of this line only; original batches and production schema unchanged.'}
(D / 'CATALOG.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({k:v for k,v in metadata.items() if k!='display_order'}, ensure_ascii=False))
