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

ALIASES.extend([['10.4230/lipics.fscd.2024.7','2402.14485'],['10.4230/lipics.socg.2025.67','2412.03372']])

ALIASES.extend([['10.4230/lipics.socg.2025.68','2412.02591']])

ALIASES.extend([['10.4230/lipics.fscd.2024.9','04568289','laplace distributors']])

ALIASES.extend([['10.4230/lipics.fscd.2024.10','akaposi/sogat','second-order generalised algebraic theories'],['10.4230/lipics.fscd.2024.11','04568253']])

ALIASES.extend([['10.4230/lipics.socg.2025.72','2504.06079'],['10.4230/lipics.socg.2025.73','2504.06503'],['10.4230/lipics.socg.2025.74','2210.12817'],['10.4230/lipics.fscd.2025.5','2505.09242'],['10.4230/lipics.fscd.2025.6','2505.08496'],['10.4230/lipics.fscd.2024.12','04514677']])

ALIASES.extend([['10.4230/lipics.fscd.2025.24','2505.09960'],['10.4230/lipics.fscd.2025.11','2505.13495'],['10.4230/lipics.fscd.2026.4','2602.05528']])

ALIASES.extend([['10.4230/lipics.socg.2025.75','2504.07752','2504.07770'],['10.4230/lipics.socg.2025.76','2412.02866']])

ALIASES.extend([['10.4230/lipics.fscd.2026.5','inria-cambium/not-choosing-is-still-a-choice']])

ALIASES.extend([['10.4230/lipics.socg.2025.78','2503.14115'],['10.4230/lipics.fscd.2026.6','2602.09874']])

ALIASES.extend([['10.4230/lipics.socg.2026.4','2603.26585'],['10.4230/lipics.socg.2026.5','19346228','20315082','2605.21636'],['10.4230/lipics.fscd.2026.7','2401.07914']])

ALIASES.extend([['10.4230/lipics.socg.2026.6','2412.04162'],['10.4230/lipics.socg.2026.7','2603.08890'],['10.4230/lipics.socg.2026.8','2601.16468']])

ALIASES.extend([['10.4230/lipics.socg.2026.9','2601.02920'],['10.4230/lipics.socg.2026.10','2512.08652'],['10.4230/lipics.fscd.2025.14','2506.09453']])

ALIASES.extend([['10.4230/lipics.fscd.2026.11','2601.05199'],['10.4230/lipics.fscd.2026.12','2510.20452','05518918'],['10.4230/lipics.fscd.2026.13','2605.07259'],['10.4230/lipics.socg.2026.11','2512.16474']])

ALIASES.extend([['10.4230/lipics.socg.2026.12','2602.16306']])

ALIASES.extend([['10.4230/lipics.fscd.2026.15','2512.19401'],['10.4230/lipics.fscd.2026.16','2604.26059'],['10.4230/lipics.socg.2026.13','2603.23490'],['10.4230/lipics.socg.2026.14','2603.14293'],['10.4230/lipics.socg.2026.15','2602.17801'],['10.4230/lipics.socg.2026.16','2603.22262']])

ALIASES.extend([['10.4230/lipics.fscd.2026.20','2605.06533'],['10.4230/lipics.fscd.2026.21','2602.18921']])

ALIASES.extend([['10.4230/lipics.socg.2026.17','2602.09551'],['10.4230/lipics.socg.2026.18','2603.18997'],['10.4230/lipics.socg.2026.19','2602.10795'],['10.4230/lipics.fscd.2026.19','2602.04641'],['10.4230/lipics.fscd.2026.23','2609.17324']])

ALIASES.extend([['10.4230/lipics.socg.2026.20','2603.09048'],['10.4230/lipics.fscd.2026.25','2512.22930']])

ALIASES.extend([['10.4230/lipics.socg.2026.21','2511.09230']])

ALIASES.extend([['10.4230/lipics.fscd.2026.27','2605.00295'],['10.4230/lipics.socg.2026.24','19271844','19271845']])

ALIASES.extend([['10.4230/lipics.socg.2026.25','2509.26525'],['10.4230/lipics.socg.2026.26','2503.11575'],['10.4230/lipics.socg.2026.27','2507.23105'],['10.4230/lipics.fscd.2026.28','2601.23082'],['10.4230/lipics.fscd.2026.29','2603.25215','05540426'],['10.4230/lipics.fscd.2026.31','2605.00655']])

ALIASES.extend([['10.4230/lipics.fscd.2026.22','olaure01/islogic']])

ALIASES.extend([['10.4230/lipics.socg.2026.28','2603.21617'],['10.4230/lipics.socg.2026.29','2603.21790']])

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
