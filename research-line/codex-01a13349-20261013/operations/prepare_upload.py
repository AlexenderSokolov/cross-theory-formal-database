from pathlib import Path
import json,re,argparse,subprocess
parser=argparse.ArgumentParser();parser.add_argument('batch');args=parser.parse_args()
P=Path(__file__).resolve().parent.parent;R=P.parent.parent;D=P/'delivery'/args.batch
from source_neighbors import search,norm
items=[json.loads(x) for x in (D/'ITEMS.jsonl').read_text().splitlines() if x.strip()]
assert all(x['task_id'].startswith('CP01A13349-') for x in items)
def load(f):return json.loads(f.read_text(encoding='utf-8-sig'))
queries=set(x['source_id'].removeprefix('doi:').removeprefix('arxiv:') for x in items)
allocation=P/'reference/SOURCE_ALLOCATION.json'
if allocation.exists():
 for rec in load(allocation):
  if any(norm(q) in norm(' '.join(rec['identities'])) for q in queries.copy()):queries.update(rec['identities'])
queries=sorted(queries)
near=search(queries)
duplicates=[]
for x in items:
 for hit in near['neighbors']:
  m=hit['metadata']
  if norm(m.get('claim_key',''))==norm(x['claim_key']):duplicates.append((x['task_id'],hit['origin']))
if duplicates:raise ValueError('already claimed: '+repr(duplicates))
print(json.dumps({'focused_source_neighbors':near},ensure_ascii=False))
selected=set()
def add(f):
 f=f.resolve();assert f.is_relative_to(R),str(f);assert f.is_file(),str(f);selected.add(f.relative_to(R).as_posix())
for x in items:
 tid=x['task_id'];lane={'HC':'hyperlogic-complexity','MF':'modal-fixed-points','OA':'optical-diagrammatic-algebra'}[tid.split('-')[1]]
 candidates=[P/lane/tid/'task.json',P/lane/'drafts'/tid/'task.json'];tf=next(f for f in candidates if f.is_file());add(tf);t=load(tf);a=t['assembly']
 for spans in [t['statement_spans'],t['proof_spans'],t['context_spans'],a['preamble_spans'],a['body_spans']]:
  for sp in spans:add(P/sp['path'])
 for ref in a.get('external_references',[]):
  if ref.get('source_span'):add(P/ref['source_span']['path'])
 for key in ['asset_paths','bibliography_paths']:
  for v in a.get(key,[]):add(P/(v if isinstance(v,str) else v['path']))
 add(P/t['license']['evidence_path']);j=R/x['assembly_job'];s=load(j/'job-state.json');pkg=j/s['package'];m=load(pkg/'manifest.json')['items'][0]
 for f in [j/'job-state.json',pkg/'manifest.json',pkg/s['task_snapshot'],pkg/m['item_path'],pkg/m['compile_receipt'],pkg/m['license_path'],pkg/m['license_evidence_path'],R/x['pdf_path']]:add(f)
 for v in m['source_files']+m['asset_dependencies']:add(pkg/v['path'])
 for v in m['source_files']:
  if (P/v['original_path']).is_file():add(P/v['original_path'])
for f in [R/'corpus-work/scripts/prepared_delivery.py',R/'PROJECT.md',P/'README.md',P/'STATUS.json',P/'reference/SOURCE_ALLOCATION.json',P/'operations/export_materials.py',P/'operations/source_neighbors.py',P/'operations/run_export.sh',P/'operations/run_assemble.sh',P/'operations/run_compile.sh',P/'operations/run_pending.sh',Path(__file__),D/'INDEX.md',D/'ITEMS.jsonl',D/'SELECTION.json',D/'corpus.sqlite3']:add(f)
for f in (P/'delivery').glob('*/UPLOADED.json'):add(f)
if (P/'delivery/EXCLUDED.json').exists():add(P/'delivery/EXCLUDED.json')
pattern=re.compile(r'(?:sk-[A-Za-z0-9_-]{24,}|gh[pousr]_[A-Za-z0-9]{25,}|-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----)')
hits=[s for s in selected if (R/s).suffix in ['.json','.jsonl','.md','.py','.sh','.tex','.txt'] and pattern.search((R/s).read_text(errors='replace'))];assert not hits,hits
files=sorted(selected)
for i in range(0,len(files),60):subprocess.run(['git','add','--',*files[i:i+60]],cwd=R,check=True)
print(json.dumps({'batch':args.batch,'ready':len(items),'files':len(files),'MiB':round(sum((R/x).stat().st_size for x in selected)/1048576,1),'same_identity_found':duplicates}))
