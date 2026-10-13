from pathlib import Path
import argparse,datetime,json,re,sqlite3,subprocess
P=Path(__file__).resolve().parent.parent;R=P.parent.parent
assert str(R)=='/disks/sata1/yupeng/human-proof-corpus/operations/codex-work-01a13326'
a=argparse.ArgumentParser();a.add_argument('batch');a.add_argument('commit');a.add_argument('--verified-remote-head',required=True);args=a.parse_args()
assert re.fullmatch(r'batch-\d{3}',args.batch) and re.fullmatch(r'[0-9a-f]{40}',args.commit)
assert args.commit==args.verified_remote_head
assert subprocess.check_output(['git','-C',str(R),'rev-parse','HEAD'],text=True).strip()==args.commit
D=P/'delivery'/args.batch;items=[json.loads(l) for l in (D/'ITEMS.jsonl').read_text().splitlines()];assert len(items)==25
(D/'UPLOADED.json').write_text(json.dumps({'commit':args.commit,'branch':'codex/corpus-01a13326-20261013','count':25,'task_ids':[x['task_id'] for x in items],'uploaded_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'verified_remote_head':args.commit,'production_public_increment':0},ensure_ascii=False,indent=2)+'\n')
ex=set(json.loads((P/'delivery/EXCLUDED.json').read_text())['task_ids']);up=set()
for f in (P/'delivery').glob('*/UPLOADED.json'):up.update(set(json.loads(f.read_text())['task_ids'])-ex)
total=len(up);nextbatch='batch-%03d'%(int(args.batch[-3:])+1)
f=P/'README.md';s=f.read_text();line='- '+args.batch+'：25道；提交`'+args.commit+'`。[索引](delivery/'+args.batch+'/INDEX.md)、[SQLite](delivery/'+args.batch+'/corpus.sqlite3)。累计净上传'+str(total)+'道，生产主库公开增量0。'
if line not in s:f.write_text(s+'\n'+line+'\n')
subprocess.run(['/disks/sata1/yupeng/human-proof-corpus/runtime/python/bin/python',str(P/'operations/export_materials.py'),'--batch',nextbatch,'--limit','25'],check=True)
compiled=set();stored=0
for root in [P/'jobs',P/'algebra-geometry/jobs',P/'combinatorics-logic/jobs',P/'analysis-probability/jobs']:
 for f in root.glob('*/r*/job-state.json'):
  x=json.loads(f.read_text())
  if x['status']=='compiled_pending_qa' and x['task_id'].startswith('CP01A13326-') and x['task_id'] not in ex:compiled.add(x['task_id'])
for f in (P/'delivery').glob('*/corpus.sqlite3'):
 with sqlite3.connect(f) as db:stored+=db.execute('select count(*) from problems').fetchone()[0]
f=P/'STATUS.json';s=json.loads(f.read_text());s['persistent_goal'].update(resume_from=nextbatch);s.update(state='producing_next_batch',compiled=len(compiled),stored=stored,uploaded=total,last_upload_commit=args.commit,next_batch=nextbatch,last_confirmed_complete_upload_count=total,observed_at=datetime.datetime.now(datetime.timezone.utc).isoformat());f.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'compiled':len(compiled),'stored':stored,'uploaded':total,'next_batch':nextbatch,'next_batch_ready':stored-total}),flush=True)
