from pathlib import Path
import json,re,argparse
B=Path('/disks/sata1/yupeng/human-proof-corpus')
P=Path(__file__).resolve().parent.parent
def load(f):return json.loads(f.read_text(encoding='utf-8-sig'))
def rows(f):
 if not f.is_file():return []
 return [json.loads(l) for l in f.read_text(encoding='utf-8-sig').splitlines() if l.strip()]
def normalize_source(s):
 s=str(s).lower().strip()
 m=re.search(r'10\.\d{4,9}/[^\s?#]+',s)
 if m:return 'doi:'+m.group(0).rstrip('/.,;')
 m=re.search(r'(?:arxiv[:/]|arxiv.org/(?:abs|pdf)/)(\d{4}\.\d{4,5})(?:v\d+)?',s)
 if m:return 'arxiv:'+m.group(1)
 return s

def neighbors(sources):
 wanted={normalize_source(s) for s in sources};aliases=[]
 for f in [B/'repo/handoff/catalog/source_works.jsonl',B/'repo/handoff/catalog/candidate_catalog.jsonl']:
  for x in rows(f):
   ids={normalize_source(v) for v in [x.get('work_identity_key',''),x.get('doi_extracted',''),*x.get('source_urls',[]),*x.get('dedup_identity_aliases',[])] if isinstance(v,str) and v}
   aliases.append(ids)
 for _ in range(2):
  for ids in aliases:
   if ids&wanted:wanted.update(ids)
 out=[]
 def add(x,origin):
  ids={normalize_source(x.get(k,'')) for k in ['source_id','source_url','work_identity_key']}
  ids.update(normalize_source(v) for v in x.get('source_aliases',[]) if isinstance(v,str))
  if ids&wanted:out.append({**x,'lookup_origin':str(origin)})
 f=B/'repo/editable-corpus/manifest.json'
 for x in load(f)['items']:add(x,f)
 f=B/'operations/corpusctl/prepared-reservations.json'
 for x in load(f)['entries']:add(x,f)
 prep=B/'operations/codex-takeover-01a12558/corpus-repair-20261010/research-line/harness-ready-20261011'
 for x in rows(prep/'PREPARATION_WORKLIST.jsonl'):
  rel=x.get('task_path');tf=prep/rel if rel else None
  if tf and tf.is_file():add({**x,**load(tf)},tf)
  else:add(x,prep/'PREPARATION_WORKLIST.jsonl')
 for tree,name in [('codex-parallel-work-20261013','codex-parallel-20261013'),('codex-work-01a13326','codex-01a13326-20261013')]:
  root=B/'operations'/tree/'research-line'/name
  for f in root.glob('*/**/task.json'):
   if 'jobs' not in f.relative_to(root).parts:add(load(f),f)
  for f in root.glob('delivery/*/ITEMS.jsonl'):
   for x in rows(f):add(x,f)
 return out
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('sources',nargs='+');args=ap.parse_args()
 for x in neighbors(args.sources):
  print(json.dumps({k:x.get(k) for k in ['source_id','source_url','claim_key','problem_id','task_id','title','primary','statement_spans','state','status','lookup_origin']},ensure_ascii=False))
