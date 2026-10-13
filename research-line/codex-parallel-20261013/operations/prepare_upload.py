from pathlib import Path
import json,re,argparse,subprocess
parser=argparse.ArgumentParser();parser.add_argument('batch');args=parser.parse_args()
P=Path(__file__).resolve().parent.parent;R=P.parent.parent;D=P/'delivery'/args.batch
B=Path('/disks/sata1/yupeng/human-proof-corpus/operations/codex-takeover-01a12558/corpus-repair-20261010/research-line/harness-ready-20261011')
def load(f):return json.loads(f.read_text(encoding='utf-8-sig'))
def identity(t):
 source=str(t.get('source_id','')).lower();claim=str(t.get('claim_key','')).lower()
 # A Stacks chapter/label remains one counting object across source-key spellings.
 m=re.match(r'stacks-project:(?:stacks-)?([^:@]+\.tex)',source)
 if m:
  source='stacks-project:'+m.group(1)
  if claim.startswith('stacks:'):claim=claim.split(':',2)[-1]
 return source,claim
items=[json.loads(x) for x in (D/'ITEMS.jsonl').read_text().splitlines()];targets={identity(x):x['task_id'] for x in items};duplicates=[]
for x in [json.loads(l) for l in (B/'PREPARATION_WORKLIST.jsonl').read_text(encoding='utf-8-sig').splitlines() if l.strip()]:
 rel=x.get('task_path');f=B/rel if rel else None
 try:
  t=load(f) if f and f.is_file() else x
  if not t.get('source_id') and x.get('assembly_job'):
   for job in [B/x['assembly_job'],B.parent.parent/x['assembly_job']]:
    if job.resolve().is_relative_to(B) and (job/'job-state.json').is_file():
     state=load(job/'job-state.json');snapshot=job/state['package']/state['task_snapshot']
     if snapshot.is_file():t=load(snapshot);break
 except (OSError,KeyError,json.JSONDecodeError):t=x
 key=identity(t)
 if key in targets:duplicates.append((targets[key],x.get('task_id'),x['state']))
# Other production line: read only its existing claims and delivery records.
T=Path('/disks/sata1/yupeng/human-proof-corpus/operations/codex-work-01a1332f/research-line/codex-01a1332f-20261013')
def source_keys(t):
 keys={str(t.get('source_id','')).lower()}
 keys.update(str(a).lower() for a in t.get('source_aliases',[]))
 for value in list(keys)+[str(t.get('source_url',''))]:
  m=re.search(r'(?:arxiv:|arxiv.org/(?:abs|pdf)/)([0-9]{4}\.[0-9]{4,5})',value,re.I)
  if m:keys.add('arxiv:'+m.group(1))
 return keys-{''}
third={};uploaded_third=set()
if T.exists():
 for marker in (T/'delivery').glob('*/UPLOADED.json'):uploaded_third.update(load(marker).get('task_ids',[]))
 excluded_third=set(load(T/'delivery/EXCLUDED.json').get('task_ids',[])) if (T/'delivery/EXCLUDED.json').exists() else set()
 for ip in (T/'delivery').glob('*/ITEMS.jsonl'):
  for line in ip.read_text(encoding='utf-8-sig').splitlines():
   if line.strip():
    x=json.loads(line);third[x['task_id']]=x
 for lane in ['communication-complexity','geometry-algorithms','number-theory']:
  for tf in (T/lane).glob('*/task.json'):
   try:x=load(tf)
   except (OSError,json.JSONDecodeError):continue
   third[x['task_id']]=x
 third={k:v for k,v in third.items() if k in uploaded_third or (k not in excluded_third and not str(v.get('status','')).startswith(('duplicate','retired','withdraw')) and 'no_new_count' not in str(v.get('count_disposition','')))}
third_near=[]
for own in items:
 tid=own['task_id'];lane={'AP':'analysis-probability','CL':'combinatorics-logic','AG':'algebra-geometry'}[tid.split('-')[1]]
 tf=next(p for p in [P/lane/tid/'task.json',P/lane/'drafts'/tid/'task.json'] if p.is_file());own_full=load(tf);sk=source_keys(own_full)
 for other in third.values():
  if sk & source_keys(other):
   third_near.append({'task_id':tid,'other_task_id':other['task_id'],'source_id':other.get('source_id'),'claim_key':other.get('claim_key'),'title':other.get('title')})
   if own['claim_key'].lower()==str(other.get('claim_key','')).lower():duplicates.append((tid,other['task_id'],'other_line_claim'))
print(json.dumps({'third_line_claims_read':len(third),'third_line_same_source':third_near},ensure_ascii=False))

if duplicates:raise ValueError('already claimed: '+repr(duplicates))
selected=set()
def add(f):
 f=f.resolve();assert f.is_relative_to(R),str(f);assert f.is_file(),str(f);selected.add(f.relative_to(R).as_posix())
for x in items:
 tid=x['task_id'];lane={'AP':'analysis-probability','CL':'combinatorics-logic','AG':'algebra-geometry'}[tid.split('-')[1]]
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
for f in [R/'PROJECT.md',P/'README.md',P/'STATUS.json',P/'operations/export_materials.py',P/'operations/run_export.sh',Path(__file__),D/'INDEX.md',D/'ITEMS.jsonl',D/'SELECTION.json',D/'corpus.sqlite3']:add(f)
for f in (P/'delivery').glob('*/UPLOADED.json'):add(f)
if (P/'delivery/EXCLUDED.json').exists():add(P/'delivery/EXCLUDED.json')
pattern=re.compile(r'(?:sk-[A-Za-z0-9_-]{24,}|gh[pousr]_[A-Za-z0-9]{25,}|-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----)')
hits=[s for s in selected if (R/s).suffix in ['.json','.jsonl','.md','.py','.sh','.tex','.txt'] and pattern.search((R/s).read_text(errors='replace'))];assert not hits,hits
files=sorted(selected)
for i in range(0,len(files),60):subprocess.run(['git','add','--',*files[i:i+60]],cwd=R,check=True)
print(json.dumps({'batch':args.batch,'ready':len(items),'files':len(files),'MiB':round(sum((R/x).stat().st_size for x in selected)/1048576,1),'same_identity_found':duplicates}))
