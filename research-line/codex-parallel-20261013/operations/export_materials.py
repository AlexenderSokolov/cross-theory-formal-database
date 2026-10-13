import json,sqlite3,os,argparse
from pathlib import Path
from collections import Counter
P=Path(__file__).resolve().parent.parent
R=P.parent.parent
parser=argparse.ArgumentParser()
parser.add_argument('--batch',default='batch-001')
parser.add_argument('--limit',type=int,default=25)
args=parser.parse_args()
OUT=P/'delivery'/args.batch
OUT.mkdir(parents=True,exist_ok=True)
def load(f):return json.loads(f.read_text(encoding='utf-8-sig'))
def rel(f):return f.relative_to(R).as_posix()
def source(spans):
 return '\n\n'.join('% '+s['path']+':'+str(s['start_line'])+'-'+str(s['end_line'])+'\n'+'\n'.join((P/s['path']).read_text(encoding='utf-8-sig').splitlines()[s['start_line']-1:s['end_line']]) for s in spans)
found={}
for root in [P/'jobs',P/'combinatorics-logic/jobs',P/'analysis-probability/jobs',P/'algebra-geometry/jobs']:
 for f in root.glob('*/r*/job-state.json'):
  state=load(f)
  if state['status']!='compiled_pending_qa' or not state['task_id'].startswith('CP13-'):continue
  job=f.parent;pkg=job/state['package'];task=load(pkg/state['task_snapshot']);row=load(pkg/'manifest.json')['items'][0];receipt=load(pkg/row['compile_receipt'])
  if receipt.get('ok') is not True:continue
  tex=pkg/row['item_path'];pdf=job/receipt['pdf_path']
  if not tex.is_file() or not pdf.is_file():raise ValueError('missing product '+state['task_id'])
  found[state['task_id']]=(job,state,pkg,task,row,tex,pdf)
excluded_file=P/'delivery/EXCLUDED.json'
excluded=set(load(excluded_file).get('task_ids',[])) if excluded_file.exists() else set()
found={k:v for k,v in found.items() if k not in excluded}
uploaded=set()
for marker in (P/'delivery').glob('*/UPLOADED.json'):
 if marker.parent!=OUT:
  uploaded.update(load(marker).get('task_ids',[]))
selection=OUT/'SELECTION.json'
if selection.exists():
 selected=load(selection)['task_ids']
else:
 selected=sorted(k for k in found if k not in uploaded)[:args.limit]
 selection.write_text(json.dumps({'task_ids':selected},indent=2)+'\n')
found={k:found[k] for k in selected}
db=sqlite3.connect(OUT/'corpus.sqlite3')
columns=['task_id','title','route','difficulty_level','source_id','claim_key','source_url','source_version','authors_json','license_json','statement_text','proof_text','context_text','tex_content','tex_path','pdf_path','task_json','state']
manifest=[]
with db:
 db.execute('CREATE TABLE IF NOT EXISTS problems ('+','.join(c+' TEXT'+(' PRIMARY KEY' if c=='task_id' else '') for c in columns)+', UNIQUE(source_id,claim_key))')
 for key,(job,state,pkg,t,row,tex,pdf) in sorted(found.items()):
  values=[key,t['title'],t['route'],t['difficulty_level'],t['source_id'],t['claim_key'],t['source_url'],t['source_version'],json.dumps(t['authors'],ensure_ascii=False),json.dumps(t['license'],ensure_ascii=False),source(t['statement_spans']),source(t['proof_spans']),source(t['context_spans']),tex.read_text(encoding='utf-8'),rel(tex),rel(pdf),json.dumps(t,ensure_ascii=False),'prepared_unpublished']
  db.execute('INSERT INTO problems VALUES ('+','.join('?' for _ in columns)+') ON CONFLICT(task_id) DO UPDATE SET '+','.join(c+'=excluded.'+c for c in columns[1:]),values)
  manifest.append({'task_id':key,'revision':t['revision'],'source_id':t['source_id'],'claim_key':t['claim_key'],'state':'prepared_unpublished','preparation_basis':'author_material_collection','assembly_job':rel(job),'tex_path':rel(tex),'pdf_path':rel(pdf),'problem_id':None})
 assert db.execute('SELECT count(*) FROM problems WHERE length(statement_text)=0 OR length(proof_text)=0 OR length(tex_content)=0').fetchone()[0]==0
 count=db.execute('SELECT count(*) FROM problems WHERE state="prepared_unpublished"').fetchone()[0]
(OUT/'ITEMS.jsonl').write_text(''.join(json.dumps(m,ensure_ascii=False)+'\n' for m in manifest),encoding='utf-8')
lines=['# Codex主机并行生产：作者题证成品','',f'本地可用 {count} 道；上传情况另见批次记录。生产主库公开增量不由本索引推断。','', '遵循仓库根PROJECT.md，不认证作者数学。SQLite为corpus.sqlite3，表problems保存题面、证明、上下文及成品TeX。路径相对于仓库根。','','| 题目 | 方向 | 级别 | 成品 |','|---|---|---|---|']
for key,(job,state,pkg,t,row,tex,pdf) in sorted(found.items()):
 lines.append('| '+t['title'].replace('|','/')+' | '+t['route']+' | '+t['difficulty_level']+' | [TeX]('+os.path.relpath(tex,OUT)+') · [PDF]('+os.path.relpath(pdf,OUT)+') |')
(OUT/'INDEX.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'compiled_and_stored':count,'routes':dict(Counter(t['route'] for _,_,_,t,_,_,_ in found.values())),'production_public_increment':0},ensure_ascii=False))
db.close()
