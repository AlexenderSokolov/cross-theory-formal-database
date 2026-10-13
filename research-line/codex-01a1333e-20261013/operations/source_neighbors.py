from pathlib import Path
import json,sys,re
from functools import cache
B=Path('/disks/sata1/yupeng/human-proof-corpus')
ALIASES=[['10.4230/lipics.socg.2025.66','2502.01120','lipschitz decompositions of finite'],['10.4230/lipics.socg.2025.41','2504.08119','decomposing multiparameter persistence modules'],['10.4230/lipics.fscd.2025.16','yeo','locally colored graphs'],['10.4230/lipics.socg.2025.16','2411.19208','signotopes with few plus signs']]
ALIASES.extend([
['10.4230/lipics.socg.2025.43','2410.21204','on spheres with k points inside'],
['10.4230/lipics.socg.2025.53','2504.02190','ptas for tsp with neighbourhoods'],
['10.3842/sigma.2025.070','2410.05846','mikami-weinstein type theorem for cosymplectic'],
['10.3842/sigma.2025.071','2504.15597'],
['10.3842/sigma.2025.072','2411.03882','ricci-flat manifolds, parallel spinors'],
['10.3842/sigma.2025.073','2304.00699','splice diagrams']])

ALIASES.extend([
['10.3842/sigma.2025.075','2404.15767','isomonodromy and painlev'],
['10.3842/sigma.2025.080','2504.08293','skew pl'],
['10.3842/sigma.2025.079','2405.03259','ising model coupled to 2d gravity'],
['10.3842/sigma.2025.088','2408.16696','perturbations of aps boundary'],
['10.3842/sigma.2025.081','2409.11306','killing (super)algebras associated'],
['10.3842/sigma.2025.083','2410.14068'],
['10.3842/sigma.2025.089','2509.17976'],
['10.3842/sigma.2025.091','2412.02042'],
['10.4230/lipics.fscd.2025.12','2505.06193','ohana trees'],
['10.4230/lipics.fscd.2025.21','2411.13125','expressive trace logic'],
['10.4230/lipics.socg.2025.54','2407.03101'],
['10.4230/lipics.socg.2025.55','2504.03942']])

ALIASES.extend([
['10.4230/lipics.socg.2025.58','2412.15419'],
['10.4230/lipics.socg.2025.59','2504.07366'],
['10.4230/lipics.socg.2025.60','2503.19365'],
['10.4230/lipics.socg.2025.61','2311.15646'],
['10.4230/lipics.socg.2025.62','2412.03332'],
['10.4230/lipics.socg.2025.63','2404.03751'],
['10.4230/lipics.fscd.2025.27','2502.15500'],
['10.4230/lipics.fscd.2025.31','2503.07881'],
['10.4230/lipics.fscd.2024.5','2402.15174']])

ALIASES.extend([['10.4230/lipics.fscd.2024.6','2405.03264','delooping generated groups','delooping presented groups']])

LANES=[('codex-parallel-work-20261013','codex-parallel-20261013'),('codex-work-01a13326','codex-01a13326-20261013'),('codex-work-01a1332f','codex-01a1332f-20261013')]
@cache
def read(p):return p.read_text(encoding='utf-8-sig')
@cache
def load(p):return json.loads(read(p))
def normalized(v):return re.sub(r'arxiv:|https?://(?:arxiv.org/(?:abs|pdf)/|doi.org/)|doi:', '',re.sub(r'v[0-9]+(?=$|\b)', '',str(v).lower()))
def query(tokens):
 terms={normalized(t) for t in tokens}
 for group in ALIASES:
  if any(a in t or t in a for a in group for t in terms):terms.update(group)
 hits=[];stats={}
 def check(row,scope,path):
  data={k:row.get(k) for k in ['task_id','problem_id','title','work','source_id','source_url','source_version','claim_key','primary','state','status','task_path'] if k in row}
  text=json.dumps(data,ensure_ascii=False).lower()
  if any(t in text for t in terms):hits.append({'scope':scope,'path':str(path),**data})
 f=B/'repo/editable-corpus/manifest.json';rows=load(f)['items'];stats['public_manifest']=len(rows)
 for row in rows:check(row,'public',f)
 H=B/'operations/codex-takeover-01a12558/corpus-repair-20261010/research-line/harness-ready-20261011'
 f=H/'PREPARATION_WORKLIST.jsonl';n=0
 for line in read(f).splitlines():
  if not line.strip():continue
  row=json.loads(line);n+=1;check(row,'preparation',f)
  tf=H/str(row.get('task_path',''))
  if tf.is_file():check(load(tf),'preparation_task',tf)
 stats['preparation_rows']=n
 f=B/'operations/corpusctl/prepared-reservations.json';reserved=load(f)
 def visit(x):
  if isinstance(x,dict):
   check(x,'reservations',f)
   for v in x.values():visit(v)
  elif isinstance(x,list):
   for v in x:visit(v)
 visit(reserved)
 for dirname,line in LANES:
  root=B/'operations'/dirname/'research-line'/line;n=0
  for tf in root.rglob('task.json'):
   if 'jobs' in tf.relative_to(root).parts:continue
   check(load(tf),dirname,tf);n+=1
  for f in (root/'delivery').glob('*/ITEMS.jsonl'):
   for text in read(f).splitlines():
    if text.strip():check(json.loads(text),dirname+'_delivered',f)
  for f in [root/'README.md']:
   if f.is_file():
    text=read(f).lower()
    if any(t in text for t in terms):hits.append({'scope':dirname+'_assigned','path':str(f),'note':'source identity appears in lane assignments; inspect relevant source'})
  stats[dirname]=n
 return {'terms':sorted(terms),'scanned':stats,'neighbors':hits}
if __name__=='__main__':
 if len(sys.argv)<2:raise SystemExit('usage: source_neighbors.py DOI [ALIAS ...]')
 print(json.dumps(query(sys.argv[1:]),ensure_ascii=False,indent=2))
