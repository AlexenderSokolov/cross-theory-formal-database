from pathlib import Path
import json,re,sys
B=Path('/disks/sata1/yupeng/human-proof-corpus')
P=Path(__file__).resolve().parent.parent
LANES=[B/'operations/codex-parallel-work-20261013/research-line/codex-parallel-20261013']+[B/('operations/codex-work-'+x)/('research-line/codex-'+x+'-20261013') for x in ['01a13326','01a1332f','01a1333e']]
PREP=B/'operations/codex-takeover-01a12558/corpus-repair-20261010/research-line/harness-ready-20261011'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def norm(s):return re.sub(r'(\d{4}\.\d{4,5})v\d+',r'\1',str(s).lower()).strip()
def meta(t):
 keys=['source_id','source_url','source_version','claim_key','title','work','source_aliases','primary','statement_spans','proof_spans']
 def strip(v):
  if isinstance(v,dict):return {k:strip(x) for k,x in v.items() if 'sha' not in k and 'hash' not in k}
  if isinstance(v,list):return [strip(x) for x in v]
  return v
 return strip({k:t[k] for k in keys if k in t})
def records():
 m=load(B/'repo/editable-corpus/manifest.json')
 for t in m['items']:yield t,'public:'+str(t.get('problem_id'))
 wf=PREP/'PREPARATION_WORKLIST.jsonl'
 for line in wf.read_text(encoding='utf-8-sig').splitlines():
  if not line.strip():continue
  t=json.loads(line);tf=PREP/str(t.get('task_path',''))
  if tf.is_file():t={**t,**load(tf)}
  yield t,'prepared:'+str(t.get('task_id'))
 rf=B/'operations/corpusctl/prepared-reservations.json'
 data=load(rf)
 seq=data if isinstance(data,list) else data.get('entries',data.get('reservations',data.get('items',[])))
 if isinstance(seq,dict):seq=[dict(v,task_id=k) if isinstance(v,dict) else {'task_id':k,'record':v} for k,v in seq.items()]
 for t in seq:
  if isinstance(t,dict):yield t,'reservation:'+str(t.get('task_id'))
 for root in LANES:
  for lane in root.iterdir():
   if not lane.is_dir() or lane.name in ['jobs','reference','delivery','operations']:continue
   for tf in lane.rglob('task.json'):
    if 'jobs' in tf.relative_to(root).parts:continue
    yield load(tf),str(tf)
  for jf in (root/'delivery').glob('*/ITEMS.jsonl'):
   for line in jf.read_text().splitlines():
    if line.strip():yield json.loads(line),str(jf)
def search(queries):
 qs=[norm(q) for q in queries if str(q).strip()]
 counts={};hits=[]
 for t,origin in records():
  scope=origin.split(':')[0] if ':' in origin and not origin.startswith('/') else 'other_codex'
  counts[scope]=counts.get(scope,0)+1
  info=meta(t);blob=norm(json.dumps(info,ensure_ascii=False))
  if any(q in blob for q in qs):hits.append({'origin':origin,'task_id':t.get('task_id'),'problem_id':t.get('problem_id'),'metadata':info})
 return {'queries':queries,'scanned':counts,'neighbors':hits}
if __name__=='__main__':print(json.dumps(search(sys.argv[1:]),ensure_ascii=False,indent=2))
