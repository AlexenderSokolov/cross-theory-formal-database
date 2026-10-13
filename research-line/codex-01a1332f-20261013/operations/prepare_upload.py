from pathlib import Path
import json,re,argparse,subprocess
parser=argparse.ArgumentParser();parser.add_argument('batch');args=parser.parse_args()
P=Path(__file__).resolve().parent.parent;R=P.parent.parent;D=P/'delivery'/args.batch
from source_neighbors import neighbors, normalize_source
def load(f):return json.loads(f.read_text(encoding='utf-8-sig'))
items=[json.loads(x) for x in (D/'ITEMS.jsonl').read_text().splitlines()]
targets={(normalize_source(x['source_id']),x['claim_key'].lower()):x['task_id'] for x in items}
near=neighbors({v for x in items for v in [x['source_id'],*x.get('source_aliases',[])]});duplicates=[]
for x in near:
 key=(normalize_source(x.get('source_id','')),str(x.get('claim_key','')).lower())
 if key in targets:duplicates.append((targets[key],x.get('task_id',x.get('problem_id')),x.get('state',x.get('status'))))
if duplicates:raise ValueError('already claimed: '+repr(duplicates))
selected=set()
def add(f):
 f=f.resolve();assert f.is_relative_to(R),str(f);assert f.is_file(),str(f);selected.add(f.relative_to(R).as_posix())
for x in items:
 tid=x['task_id'];lane={'CC':'communication-complexity','GA':'geometry-algorithms','NT':'number-theory'}[tid.split('-')[1]]
 candidates=[P/lane/tid/'task.json',P/lane/'drafts'/tid/'task.json'];tf=next(f for f in candidates if f.is_file());add(tf);t=load(tf);a=t['assembly']
 for spans in [t['statement_spans'],t['proof_spans'],t['context_spans'],a['preamble_spans'],a['body_spans']]:
  for sp in spans:add(P/sp['path'])
 for ref in a.get('external_references',[]):
  if ref.get('source_span'):add(P/ref['source_span']['path'])
 for key in ['asset_paths','bibliography_paths']:
  for v in a.get(key,[]):add(P/(v if isinstance(v,str) else v['path']))
 add(P/t['license']['evidence_path'])
 original_root=(P/t['license']['evidence_path']).parent
 for original in original_root.glob('*.pdf'):add(original)
 for original in original_root.glob('*.html'):add(original)
 j=R/x['assembly_job'];s=load(j/'job-state.json');pkg=j/s['package'];m=load(pkg/'manifest.json')['items'][0]
 for f in [j/'job-state.json',pkg/'manifest.json',pkg/s['task_snapshot'],pkg/m['item_path'],pkg/m['compile_receipt'],pkg/m['license_path'],pkg/m['license_evidence_path'],R/x['pdf_path']]:add(f)
 for v in m['source_files']+m['asset_dependencies']:add(pkg/v['path'])
 for v in m['source_files']:
  if (P/v['original_path']).is_file():add(P/v['original_path'])
for f in [R/'PROJECT.md',P/'README.md',P/'STATUS.json',P/'operations/export_materials.py',P/'operations/source_neighbors.py',P/'operations/assemble_materials.py',P/'operations/run_assemble.sh',P/'operations/run_export.sh',Path(__file__),D/'INDEX.md',D/'ITEMS.jsonl',D/'SELECTION.json',D/'corpus.sqlite3']:add(f)
for f in (P/'delivery').glob('*/UPLOADED.json'):add(f)
if (P/'delivery/EXCLUDED.json').exists():add(P/'delivery/EXCLUDED.json')
pattern=re.compile(r'(?:sk-[A-Za-z0-9_-]{24,}|gh[pousr]_[A-Za-z0-9]{25,}|-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----)')
hits=[s for s in selected if (R/s).suffix in ['.json','.jsonl','.md','.py','.sh','.tex','.txt'] and pattern.search((R/s).read_text(errors='replace'))];assert not hits,hits
files=sorted(selected)
staged=subprocess.check_output(['git','diff','--cached','--diff-filter=ACMRT','--name-only'],cwd=R,text=True).splitlines()
for old in staged:
 if old not in selected and (old=='PROJECT.md' or old.startswith(P.relative_to(R).as_posix()+'/')):
  subprocess.run(['git','reset','-q','HEAD','--',old],cwd=R,check=True)
subprocess.run(['git','add','--',*files],cwd=R,check=True)
print(json.dumps({'batch':args.batch,'ready':len(items),'files':len(files),'MiB':round(sum((R/x).stat().st_size for x in selected)/1048576,1),'same_identity_found':duplicates,'same_source_neighbors':len(near)}))
