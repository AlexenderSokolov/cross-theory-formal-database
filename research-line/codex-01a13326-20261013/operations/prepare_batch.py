from pathlib import Path
import argparse,datetime,json,re,sqlite3,subprocess,sys
P=Path(__file__).resolve().parent.parent;R=P.parent.parent
assert str(R)=='/disks/sata1/yupeng/human-proof-corpus/operations/codex-work-01a13326','This entry runs only in the approved Yupeng worktree.'
PY='/disks/sata1/yupeng/human-proof-corpus/runtime/python/bin/python'
BRANCH='codex/corpus-01a13326-20261013'
a=argparse.ArgumentParser();a.add_argument('batch');args=a.parse_args()
assert re.fullmatch(r'batch-\d{3}',args.batch)
number=int(args.batch[-3:]);assert number>=1
D=P/'delivery'/args.batch
if (D/'UPLOADED.json').exists():
 print(json.dumps({'batch':args.batch,'already_uploaded':True}));sys.exit(0)
subprocess.run([PY,str(P/'operations/export_materials.py'),'--batch',args.batch,'--limit','25'],check=True)
load=lambda f:json.loads(f.read_text(encoding='utf-8-sig'))
items=[json.loads(l) for l in (D/'ITEMS.jsonl').read_text().splitlines()]
excluded=set(load(P/'delivery/EXCLUDED.json')['task_ids']);compiled=set();uploaded=set();stored=0
for root in [P/'jobs',P/'algebra-geometry/jobs',P/'combinatorics-logic/jobs',P/'analysis-probability/jobs']:
 for f in root.glob('*/r*/job-state.json'):
  x=load(f)
  if x['status']=='compiled_pending_qa' and x['task_id'].startswith('CP01A13326-') and x['task_id'] not in excluded:compiled.add(x['task_id'])
for f in (P/'delivery').glob('*/UPLOADED.json'):uploaded.update(set(load(f)['task_ids'])-excluded)
for f in (P/'delivery').glob('*/corpus.sqlite3'):
 with sqlite3.connect(f) as db:stored+=db.execute('select count(*) from problems').fetchone()[0]
s=load(P/'STATUS.json');s.update(state='batch_ready_for_upload' if len(items)==25 else 'producing_next_batch',compiled=len(compiled),stored=stored,uploaded=len(uploaded),next_batch=args.batch,observed_at=datetime.datetime.now(datetime.timezone.utc).isoformat());(P/'STATUS.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'batch':args.batch,'batch_items':len(items),'compiled_total':len(compiled),'stored_total':stored,'uploaded_total':len(uploaded)}),flush=True)
if len(items)<25:sys.exit(0)
assert len(items)==25
allitems=[]
for n in range(1,number+1):allitems.extend(json.loads(l) for l in (P/'delivery'/('batch-%03d'%n)/'ITEMS.jsonl').read_text().splitlines())
norm=lambda x:re.sub(r'(arxiv:\d{4}\.\d{4,5})v\d+',r'\1',x.lower())
total=len(uploaded)+25
assert len(allitems)==total
assert len({x['task_id'] for x in allitems})==total
assert len({(norm(x['source_id']),norm(x['claim_key'])) for x in allitems})==total
assert not ({x['task_id'] for x in allitems}&excluded)
with sqlite3.connect(D/'corpus.sqlite3') as db:
 rows=db.execute('select task_id,tex_path,pdf_path,length(statement_text),length(proof_text),length(tex_content) from problems').fetchall()
 assert len(rows)==25 and all(min(x[3:])>0 and (R/x[1]).is_file() and (R/x[2]).is_file() for x in rows)
r=subprocess.run([PY,str(P/'operations/prepare_upload.py'),args.batch],check=True,capture_output=True,text=True);report=json.loads(r.stdout.strip().splitlines()[-1]);print(json.dumps(report),flush=True)
if report['related_source_neighbors']:sys.exit('Targeted related-source comparison is still needed; no commit made.')
own=[P/'operations'/f for f in ['prepare_batch.py','mark_uploaded.py','run_prepare_batch.sh','run_mark_uploaded.sh']]
subprocess.run(['git','-C',str(R),'add','--']+[str(f.relative_to(R)) for f in own],check=True)
staged=subprocess.check_output(['git','-C',str(R),'diff','--cached','--name-only'],text=True).splitlines();assert all(x=='PROJECT.md' or x.startswith('research-line/codex-01a13326-20261013/') for x in staged)
assert subprocess.check_output(['git','-C',str(R),'symbolic-ref','--short','HEAD'],text=True).strip()==BRANCH
r=subprocess.run(['git','-C',str(R),'commit','-m','Add '+args.batch+' of 25 complete author-proof materials'],capture_output=True,text=True);assert r.returncode==0,r.stderr
commit=subprocess.check_output(['git','-C',str(R),'rev-parse','HEAD'],text=True).strip()
prior=load(P/'delivery'/('batch-%03d'%(number-1))/'UPLOADED.json')['commit']
bundle=P/'delivery'/(args.batch+'.bundle')
subprocess.run(['git','-C',str(R),'bundle','create',str(bundle),'refs/heads/'+BRANCH,'^'+prior],check=True)
print(json.dumps({'batch':args.batch,'commit':commit,'verified_batch':25,'cumulative_identity_records':total,'bundle_MiB':round(bundle.stat().st_size/1048576,2)}),flush=True)
