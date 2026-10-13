from pathlib import Path
import json,re,argparse,subprocess
parser=argparse.ArgumentParser();parser.add_argument('batch');args=parser.parse_args()
P=Path(__file__).resolve().parent.parent;R=P.parent.parent;D=P/'delivery'/args.batch
B=Path('/disks/sata1/yupeng/human-proof-corpus/operations/codex-takeover-01a12558/corpus-repair-20261010/research-line/harness-ready-20261011')
def load(f):return json.loads(f.read_text(encoding='utf-8-sig'))
def norm(value):return re.sub(r'(arxiv:\d{4}\.\d{4,5})v\d+',r'\1',str(value).strip().lower())
items=[json.loads(x) for x in (D/'ITEMS.jsonl').read_text().splitlines()];targets={(norm(x['source_id']),norm(x['claim_key'])):x['task_id'] for x in items};duplicates=[];neighbors=[]
source_targets={key[0] for key in targets}
for x in [json.loads(l) for l in (B/'PREPARATION_WORKLIST.jsonl').read_text(encoding='utf-8-sig').splitlines() if l.strip()]:
 rel=x.get('task_path');f=B/rel if rel else None
 try:t=load(f) if f and f.is_file() else x
 except (OSError,json.JSONDecodeError):t=x
 key=(norm(t.get('source_id','')),norm(t.get('claim_key','')))
 if key in targets:duplicates.append((targets[key],x.get('task_id'),x['state']))
 elif key[0] in source_targets:neighbors.append({'source_id':t.get('source_id'),'prior_task_id':x.get('task_id'),'claim_key':t.get('claim_key'),'title':t.get('title'),'task_path':str(f) if f else None,'state':x.get('state')})
# Compare only this batch with the other Codex lane, including in-flight tasks.
OTHER=Path('/disks/sata1/yupeng/human-proof-corpus/operations/codex-parallel-work-20261013/research-line/codex-parallel-20261013')
other_records=[]
for lane in ['analysis-probability','combinatorics-logic','algebra-geometry']:
 for tf in (OTHER/lane).rglob('task.json'):
  if 'jobs' in tf.relative_to(OTHER/lane).parts:continue
  try:other_records.append(load(tf))
  except (OSError,json.JSONDecodeError):continue
for mf in (OTHER/'delivery').glob('*/ITEMS.jsonl'):
 other_records.extend(json.loads(line) for line in mf.read_text().splitlines() if line.strip())
for t in other_records:
 key=(norm(t.get('source_id','')),norm(t.get('claim_key','')))
 if key in targets:duplicates.append((targets[key],t.get('task_id'),'other_codex'))
 elif key[0] in source_targets:neighbors.append({'source_id':t.get('source_id'),'prior_task_id':t.get('task_id'),'claim_key':t.get('claim_key'),'title':t.get('title'),'state':'other_codex'})
if duplicates:raise ValueError('already claimed: '+repr(duplicates))
selected=set()
def add(f):
 f=f.resolve();assert f.is_relative_to(R),str(f);assert f.is_file(),str(f);selected.add(f.relative_to(R).as_posix())
# Preserve unmodified author originals for selected items, including earlier deliveries.
originals_file=P/'delivery/ORIGINAL_SOURCES.json'
previous_originals=load(originals_file).get('sources',[]) if originals_file.is_file() else []
committed_originals_result=subprocess.run(['git','show','HEAD:'+originals_file.relative_to(R).as_posix()],cwd=R,capture_output=True,text=True)
committed_originals=json.loads(committed_originals_result.stdout).get('sources',[]) if committed_originals_result.returncode==0 else []
committed_originals_by_source={(x['source_id'],x['lane']):x for x in committed_originals}
selected_source_ids=set()
for selected_manifest in (P/'delivery').glob('*/ITEMS.jsonl'):
 for line in selected_manifest.read_text().splitlines():
  if line.strip():selected_source_ids.add(norm(json.loads(line)['source_id']))
originals=[]
for original_lane in ['algebra-geometry','analysis-probability','combinatorics-logic']:
 original_manifest=P/original_lane/'ORIGINAL_SOURCES.json'
 if original_manifest.is_file():
  raw=load(original_manifest);entries=raw if isinstance(raw,list) else raw['sources']
 else:entries=[x for x in previous_originals if x.get('lane')==original_lane]
 for entry in entries:
  if norm(entry['source_id']) not in selected_source_ids:continue
  paths=list(entry.get('paths',[]))
  if entry.get('archive_path'):paths.append(entry['archive_path'])
  paths+=entry.get('original_native_paths',[])
  paths=sorted(set(paths))
  record={'source_id':entry['source_id'],'lane':original_lane,'paths':paths}
  for original_key in ['source_version','license']:
   if entry.get(original_key):record[original_key]=entry[original_key]
  if committed_originals_by_source.get((record['source_id'],original_lane))!=record:
   for original_path in paths:add(P/original_path)
  originals.append(record)
covered_original_sources={norm(x['source_id']) for x in originals}
missing_original_sources=sorted(selected_source_ids-covered_original_sources)
if missing_original_sources:raise ValueError('Selected author-original source records missing: '+repr(missing_original_sources))
originals_file.write_text(json.dumps({'purpose':'Unmodified author originals actually used by the selected delivered materials; no unused candidates.','sources':originals},ensure_ascii=False,indent=2)+'\n')
add(originals_file)
for x in items:
 tid=x['task_id'];lane={'AP':'analysis-probability','CL':'combinatorics-logic','AG':'algebra-geometry'}[tid.split('-')[1]]
 candidates=[P/lane/tid/'task.json',P/lane/'drafts'/tid/'task.json'];tf=next(f for f in candidates if f.is_file());add(tf);t=load(tf);a=t['assembly']
 for spans in [t['statement_spans'],t['proof_spans'],t['context_spans'],a['preamble_spans'],a['body_spans']]:
  for sp in spans:add(P/sp['path'])
 for ref in a.get('external_references',[]):
  if ref.get('source_span'):add(P/ref['source_span']['path'])
 for helper in ['run_assemble.sh','run_compile.sh']:
  if (P/lane/helper).is_file():add(P/lane/helper)
 for key in ['asset_paths','bibliography_paths']:
  for v in a.get(key,[]):add(P/(v if isinstance(v,str) else v['path']))
 add(P/t['license']['evidence_path']);j=R/x['assembly_job'];s=load(j/'job-state.json');pkg=j/s['package'];m=load(pkg/'manifest.json')['items'][0]
 for f in [j/'job-state.json',pkg/'manifest.json',pkg/s['task_snapshot'],pkg/m['item_path'],pkg/m['compile_receipt'],pkg/m['license_path'],pkg/m['license_evidence_path'],R/x['pdf_path']]:add(f)
 for v in m['source_files']+m['asset_dependencies']:add(pkg/v['path'])
 for v in m['source_files']:
  if (P/v['original_path']).is_file():add(P/v['original_path'])
for f in [R/'PROJECT.md',P/'README.md',P/'STATUS.json',P/'operations/export_materials.py',P/'operations/run_export.sh',P/'operations/run_assemble.sh',P/'operations/run_compile.sh',Path(__file__),D/'INDEX.md',D/'ITEMS.jsonl',D/'SELECTION.json',D/'corpus.sqlite3']:add(f)
for f in (P/'delivery').glob('*/UPLOADED.json'):add(f)
if (P/'delivery/EXCLUDED.json').exists():add(P/'delivery/EXCLUDED.json')
pattern=re.compile(r'(?:sk-[A-Za-z0-9_-]{24,}|gh[pousr]_[A-Za-z0-9]{25,}|-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----)')
hits=[s for s in selected if (R/s).suffix in ['.json','.jsonl','.md','.py','.sh','.tex','.txt'] and pattern.search((R/s).read_text(errors='replace'))];assert not hits,hits
files=sorted(selected)
for i in range(0,len(files),60):subprocess.run(['git','add','--',*files[i:i+60]],cwd=R,check=True)
print(json.dumps({'batch':args.batch,'ready':len(items),'files':len(files),'MiB':round(sum((R/x).stat().st_size for x in selected)/1048576,1),'same_identity_found':duplicates,'related_source_neighbors':neighbors}))
