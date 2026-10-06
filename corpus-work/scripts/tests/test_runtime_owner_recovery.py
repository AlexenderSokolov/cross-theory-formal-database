import contextlib, json, os, subprocess, sys, tempfile, time, unittest
from pathlib import Path
from corpus_runtime import Runtime, identity
from corpus_control_protocol import save_json, transfer_owner

class Recovery(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(); self.root=Path(self.tmp.name); self.state=self.root/'state';self.state.mkdir();self.ws=self.root/'block';self.ws.mkdir()
  save_json(self.state/'owner.json',{'owner':'A','generation':1})
  save_json(self.state/'FLOW.json',{'schema_version':2,'record_type':'flow','flow_id':'test','initial_worker_slots':3,'max_worker_slots':8,'review_backlog_limit':25,'blocks':[{'block_id':'b','enabled':True,'next_block_id':None,'units':[{'problem_id':i,'work_key':'doi:10.0/test','source_packet':str(self.ws/'SOURCE_PACKET.json'),'workspace':str(self.ws)} for i in ('001','002')]}]})
  self.r=Runtime(self.state/'runtime.sqlite','A',1)
 def tearDown(self):
  for child in self.r.__dict__.get('_children',[]):
   try:child.wait(timeout=3)
   except subprocess.TimeoutExpired:child.terminate();child.wait()
  self.tmp.cleanup()
 def spec(self,ids=('001','002'),job='b-a001',attempt='a001'):
  return {'schema_version':2,'record_type':'job_spec','job_id':job,'attempt_id':attempt,'block_id':'b','actor':{'owner':'A','generation':1},'unit_ids':list(ids),'work_keys':['id:'+i for i in ids]+['doi:10.0/test'],'workspace':str(self.ws),'stages':[{'name':'worker','argv':[sys.executable,'-c','pass']}],'result_path':str(self.ws/(attempt+'-JOB_RESULT.json'))}
 def unit(self,i,disposition='unfinished'):
  return {'problem_id':i,'work_key':'doi:10.0/test','revision':'r001','disposition':disposition,'last_completed_stage':'compiled','next_stage':'page_qa','next_action':'reuse compile and review pages','reason_code':None,'reason':'','evidence_refs':{}}
 def result(self,spec,units=None):
  return {'schema_version':2,'record_type':'job_result','job_id':spec['job_id'],'attempt_id':spec['attempt_id'],'block_id':'b','finished_at':'2026-10-05T08:00:00Z','units':units or [self.unit(i) for i in spec['unit_ids']]}
 def test_R01_missing(self):
  s=self.spec();self.r.register(s);self.r.finish(s['job_id'],0);r=self.r.status()[0];self.assertEqual(r['state'],'needs_recovery');self.assertEqual(r['reason_code'],'result_missing')
 def test_R02_invalid_variants(self):
  s=self.spec();self.r.register(s)
  for change in ('attempt','missing','duplicate','extra','work'):
   v=self.result(s)
   if change=='attempt':v['attempt_id']='old'
   if change=='missing':v['units'].pop()
   if change=='duplicate':v['units'].append(v['units'][0])
   if change=='extra':v['units'].append(self.unit('003'))
   if change=='work':v['units'][0]['work_key']='doi:other'
   save_json(s['result_path'],v);self.r.finish(s['job_id'],0);self.assertEqual(self.r.status()[0]['reason_code'],'result_invalid');self.assertTrue(Path(s['result_path']).exists())
 def test_partial_immutable_scope(self):
  s=self.spec();self.r.register(s);save_json(s['result_path'],self.result(s));self.r.finish(s['job_id'],0);self.assertEqual(self.r.status()[0]['result_status'],'partial')
  with self.assertRaises(ValueError):self.r.register(dict(s,attempt_id='a002'))
 def test_O01_generation_status_readonly(self):
  s=self.spec();self.r.register(s);transfer_owner(self.state,'A',1,'B')
  for fn in (lambda:self.r.start(s['job_id']),lambda:self.r.collect(),lambda:self.r.register(s)):
   with self.assertRaises(ValueError):fn()
  before=(self.state/'runtime.sqlite').read_bytes();Runtime(self.state/'runtime.sqlite',readonly=True).status();self.assertEqual(before,(self.state/'runtime.sqlite').read_bytes())
  absent=self.root/'absent'/'runtime.sqlite';self.assertEqual(Runtime(absent,readonly=True).status(),[]);self.assertFalse(absent.parent.exists())
 def test_C01_canonical_claim(self):
  s=self.spec(ids=('001',));self.r.register(s)
  other=self.spec(ids=('002',),job='other');other['work_keys']=['id:002','https://doi.org/10.0/TEST']
  with self.assertRaises(ValueError):self.r.register(other)
  self.assertIn('id:001',self.r.status()[0]['work_keys'])
 def test_duplicate_start(self):
  s=self.spec();s['stages'][0]['argv']=[sys.executable,'-c','import time;time.sleep(.4)'];self.r.register(s);self.r.start(s['job_id']);p=self.r.status()[0]['pid'];self.r.start(s['job_id']);self.assertEqual(p,self.r.status()[0]['pid']);time.sleep(.6);self.r.collect()
 def test_R07_reused_pid(self):
  x=identity(os.getpid());from corpus_runtime import live
  self.assertFalse(live({'pid':os.getpid(),'proc_start':'wrong','proc_cwd':x['cwd']}))
 def test_O03_unknown_write(self):
  pub=self.state/'publication.json';save_json(pub,{'actor':{'owner':'A','generation':1},'started_by':{'owner':'A','generation':1},'actor_history':[],'target_commit':'f'*40,'stage':'merged'})
  save_json(self.state/'publication-external.json',{'state':'unknown'})
  with self.assertRaises(ValueError):transfer_owner(self.state,'A',1,'B',[pub])
  v=json.loads(pub.read_text());save_json(self.state/'publication-external.json',{'state':'terminal'});transfer_owner(self.state,'A',1,'B',[pub]);v=json.loads(pub.read_text());self.assertEqual(v['target_commit'],'f'*40);self.assertEqual(v['actor']['generation'],2);self.assertEqual(v['started_by']['owner'],'A')

 def ready_unit(self,i):
  unit=self.unit(i,'ready_for_review');unit.update(last_completed_stage='item_passed',next_stage=None)
  root=self.ws/i;root.mkdir(exist_ok=True);package=root/'package-r001';package.mkdir(exist_ok=True)
  save_json(package/'manifest.json',{'items':[{'problem_id':i}]});import hashlib
  manifestsha=hashlib.sha256((package/'manifest.json').read_bytes()).hexdigest();save_json(package/'delivery-evidence.json',{'package_manifest_sha256':manifestsha,'items':{i:{}}})
  save_json(root/'READY.json',{'problem_id':i,'package':str(package),'manifest_sha256':manifestsha,'accepted_report':str(root/'item.json'),'build_root':str(root/'build_root'),'receipt_root':str(root/'receipt_root')})
  save_json(root/'item.json',{'schema_version':1,'mode':'editable-delivery','editable_qualified_count':1,'package_item_count':1,'receipt_set':str((root/'receipt_root').resolve()),'items':{i:{'status':'qualified_editable','errors':[]}},'errors':[]})
  refs={'package':str(package),'ready':str(root/'READY.json'),'item_report':str(root/'item.json')}
  for k in ('build_root','receipt_root'): (root/k).mkdir(exist_ok=True);refs[k]=str(root/k)
  for k in ('page_qa','source_map','rights','difficulty'):save_json(root/(k+'.json'),{'fixture':True});refs[k]=str(root/(k+'.json'))
  unit['evidence_refs']=refs;return unit
 def worker_config(self):save_json(self.state/'worker-command.json',{'argv':[sys.executable,'-c','pass'],'workspace':str(self.ws)})
 def test_R03_partial_continuation_exact_once(self):
  self.worker_config();s=self.spec();self.r.register(s);ready=self.ready_unit('001');save_json(s['result_path'],self.result(s,[ready,self.unit('002')]));self.r.finish(s['job_id'],0)
  before=Path(ready['evidence_refs']['package']+'/manifest.json').read_bytes();self.assertEqual(self.r.schedule(),['b-a002']);self.assertEqual(self.r.schedule(),[])
  nextspec=self.r.status('b-a002')[0]['job_spec'];self.assertEqual(nextspec['unit_ids'],['002']);self.assertEqual(nextspec['previous_job_id'],'b-a001');self.assertEqual(before,Path(ready['evidence_refs']['package']+'/manifest.json').read_bytes())
 def test_R04_hold_accounted_successor_once(self):
  self.worker_config();flow=json.loads((self.state/'FLOW.json').read_text());flow['blocks'][0]['next_block_id']='next';flow['blocks'].append({'block_id':'next','enabled':True,'next_block_id':None,'units':[{'problem_id':'003','work_key':'doi:10.0/next','source_packet':str(self.ws/'next.json'),'workspace':str(self.ws)}]});save_json(self.state/'FLOW.json',flow)
  s=self.spec();self.r.register(s);hold=self.unit('002','source_hold');hold.update(next_stage=None,reason_code='difficulty_insufficient',reason='specific difficulty evidence',hold_evidence=['source.pdf:p3']);save_json(s['result_path'],self.result(s,[self.ready_unit('001'),hold]));self.r.finish(s['job_id'],0)
  self.r.schedule();self.assertEqual(self.r.schedule(),['next-a001']);self.assertEqual(self.r.schedule(),[]);self.assertEqual(json.loads(Path(s['result_path']).read_text())['units'][1]['disposition'],'source_hold')
 def test_R05_narrative_is_recovery_no_auto_sourcehold(self):
  self.worker_config();s=self.spec();self.r.register(s);(self.ws/'FINAL.txt').write_text('completed');self.r.finish(s['job_id'],0);self.assertEqual(self.r.schedule(),[]);self.assertEqual(self.r.status()[0]['reason_code'],'result_missing')
 def test_R06_child_alive_retains_claim(self):
  s=self.spec();self.r.register(s);child=subprocess.Popen([sys.executable,'-c','import time;time.sleep(3)'],cwd=self.ws)
  try:
   x=identity(child.pid)
   with self.r.tx() as c:c.execute("UPDATE jobs SET state='running',pid=-1,child_pid=?,child_start=?,child_cwd=? WHERE job_id=?",(child.pid,x['start_time'],x['cwd'],s['job_id']))
   self.r.collect();self.assertEqual(self.r.status()[0]['state'],'orphan_running')
   with self.assertRaises(ValueError):self.r.start(s['job_id'])
   nextspec=self.spec(job='b-a002',attempt='a002');nextspec['previous_job_id']=s['job_id']
   with self.assertRaises(ValueError):self.r.register(nextspec)
  finally:child.terminate();child.wait()
 def test_R08_between_stages_no_replay(self):
  first=self.ws/'first';second=self.ws/'second';s=self.spec();s['stages']=[{'name':'first','argv':[sys.executable,'-c',f"open({str(first)!r},'a').write('first')"]},{'name':'second','argv':[sys.executable,'-c',f"open({str(second)!r},'a').write('second')"]}];self.r.register(s);first.write_text('first')
  with self.r.tx() as c:c.execute("UPDATE jobs SET state='running',pid=-1,next_stage=1 WHERE job_id=?",(s['job_id'],))
  self.r.resume(s['job_id']);self.r.resume(s['job_id']);time.sleep(.4);self.r.collect();self.assertEqual(first.read_text(),'first');self.assertEqual(second.read_text(),'second')
 def test_O02_old_private_attempt_finishes_no_new_dispatch(self):
  s=self.spec();s['stages'][0]['argv']=[sys.executable,'-c','import time;time.sleep(.5)'];self.r.register(s);self.r.start(s['job_id']);time.sleep(.2);transfer_owner(self.state,'A',1,'B');time.sleep(.6)
  with self.assertRaises(ValueError):self.r.collect()
  new=Runtime(self.state/'runtime.sqlite','B',2);new.collect();self.assertEqual(new.status()[0]['next_stage'],1)
  # New owner resumes bookkeeping; original completed stage is not executed again.
  new.start(s['job_id']);time.sleep(.3);new.collect();self.assertEqual(new.status()[0]['reason_code'],'result_missing')
 def test_Q01_ready_evidence_missing(self):
  s=self.spec();self.r.register(s);ready=self.ready_unit('001');ready['evidence_refs']['rights']=str(self.ws/'absent-rights.json');save_json(s['result_path'],self.result(s,[ready,self.unit('002')]));self.r.finish(s['job_id'],0);self.assertEqual(self.r.status()[0]['reason_code'],'result_invalid')

 def test_R09_quota_new_immutable_attempt_backoff(self):
  self.worker_config();s=self.spec();s['stages'][0].update(argv=[sys.executable,'-c',"import sys;print('Concurrency limit exceeded');sys.exit(1)"],retry_on_limit=True);self.r.register(s)
  # The same trusted template is used for each new attempt; none reuses an attempt identity.
  save_json(self.state/'worker-command.json',{'argv':s['stages'][0]['argv'],'workspace':str(self.ws)})
  ids=['b-a001']
  for n,delay in enumerate((60,120,240)):
   self.r.start(ids[-1]);time.sleep(.3);self.r.collect();row=self.r.status(ids[-1])[0];self.assertEqual(row['state'],'rate_limited');self.assertAlmostEqual(row['next_attempt_at']-time.time(),delay,delta=2)
   self.assertEqual(self.r.schedule(),[])
   with self.r.tx() as c:c.execute('UPDATE jobs SET next_attempt_at=0 WHERE job_id=?',(ids[-1],))
   created=self.r.schedule();self.assertEqual(len(created),1);ids+=created
  self.r.start(ids[-1]);time.sleep(.3);self.r.collect();self.assertEqual(self.r.status(ids[-1])[0]['state'],'quota_wait');self.assertEqual(len(set(ids)),4)
 def test_M01_handoff_reference_idempotent_no_count(self):
  h=self.root/'HANDOFF_STOPPED.json';save_json(h,{'candidate_root':str(self.ws),'items':[{'problem_id':'001','state':'READY_root_review_pending'},{'problem_id':'002','state':'technical_passed_no_READY'}]})
  first=self.r.import_reference(h);second=self.r.import_reference(h);self.assertEqual(first,second);self.assertEqual(first['admission_increment'],0);self.assertEqual(self.r.status(),[])
  with contextlib.closing(self.r.connect()) as c:self.assertEqual(c.execute('SELECT COUNT(*) FROM handoff_refs').fetchone()[0],1)

 def test_O01_public_cli_matrix_readonly_status(self):
  s=self.spec();self.r.register(s);specpath=self.root/'spec.json';save_json(specpath,s);queue=self.root/'queue.json';save_json(queue,{'base':{'local_count':1065,'remote_main_count':1065},'queued_new_root_admitted':[]})
  transfer_owner(self.state,'A',1,'B');before=(self.state/'runtime.sqlite').read_bytes();env=dict(os.environ);env['PYTHONPATH']='/disks/sata1/yupeng/human-proof-corpus/repo/corpus-work/scripts'
  ctl=Path(__file__).with_name('corpusctl.py');runtime=Path(__file__).with_name('corpus_runtime.py')
  for action in ('claim','revise','run','resume','collect','serve','adopt','admit','batch','publish','verify-public','import-handoff'):
   run=subprocess.run([sys.executable,str(ctl),'--state-root',str(self.state),'--queue',str(queue),'--controller-id','A','--generation','1',action,'--spec',str(specpath)],capture_output=True,text=True,env=env)
   self.assertEqual(run.returncode,2,(action,run.stderr));self.assertIn('actor rejected',run.stderr)
  for action,rest in (('claim',['--spec',str(specpath)]),('revise',['--spec',str(specpath)]),('run',['--job-id',s['job_id']]),('resume',['--job-id',s['job_id']]),('collect',[]),('serve',[]),('adopt',['--spec',str(specpath),'--pid','1']),('import-handoff',['--handoff',str(specpath)])):
   run=subprocess.run([sys.executable,str(runtime),'--db',str(self.state/'runtime.sqlite'),'--controller-id','A','--generation','1',action,*rest],capture_output=True,text=True,env=env)
   self.assertNotEqual(run.returncode,0,action);self.assertIn('actor rejected',run.stderr)
  run=subprocess.run([sys.executable,str(ctl),'--state-root',str(self.state),'--queue',str(queue),'status'],capture_output=True,text=True,env=env);self.assertEqual(run.returncode,0,run.stderr);self.assertEqual(before,(self.state/'runtime.sqlite').read_bytes())

 def test_review_backlog_pauses_new_blocks_only(self):
  self.worker_config();self.assertEqual(self.r.schedule(review_backlog=25),[])
  s=self.spec();self.r.register(s);save_json(s['result_path'],self.result(s,[self.ready_unit('001'),self.unit('002')]));self.r.finish(s['job_id'],0);self.assertEqual(self.r.schedule(review_backlog=25),['b-a002'])

 def test_Q01_wrong_report_receipt_scope(self):
  s=self.spec();self.r.register(s);ready=self.ready_unit('001');report=Path(ready['evidence_refs']['item_report']);v=json.loads(report.read_text());v['receipt_set']=str(self.ws/'another-receipt-root');save_json(report,v);save_json(s['result_path'],self.result(s,[ready,self.unit('002')]));self.r.finish(s['job_id'],0);self.assertEqual(self.r.status()[0]['reason_code'],'result_invalid')
 def test_Q01_revision_full_boundary(self):
  s=self.spec();self.r.register(s);ready=self.ready_unit('001');old=Path(ready['evidence_refs']['package']);new=old.with_name('package-r0010');old.rename(new);ready['evidence_refs']['package']=str(new);rp=Path(ready['evidence_refs']['ready']);v=json.loads(rp.read_text());v['package']=str(new);save_json(rp,v);save_json(s['result_path'],self.result(s,[ready,self.unit('002')]));self.r.finish(s['job_id'],0);self.assertEqual(self.r.status()[0]['reason_code'],'result_invalid')
 def test_Q01_ready_manifest_identity(self):
  s=self.spec();self.r.register(s);ready=self.ready_unit('001');rp=Path(ready['evidence_refs']['ready']);v=json.loads(rp.read_text());v['manifest_sha256']='f'*64;save_json(rp,v);save_json(s['result_path'],self.result(s,[ready,self.unit('002')]));self.r.finish(s['job_id'],0);self.assertEqual(self.r.status()[0]['reason_code'],'result_invalid')
 def test_result_structure_timestamp(self):
  s=self.spec();self.r.register(s);v=self.result(s);v['finished_at']='yesterday';save_json(s['result_path'],v);self.r.finish(s['job_id'],0);self.assertEqual(self.r.status()[0]['reason_code'],'result_invalid')

 def test_runner_waits_for_parent_short_controller_lock(self):
  from corpus_control_protocol import controller_guard
  s=self.spec();marker=self.ws/'worker-started';s['stages'][0]['argv']=[sys.executable,'-c',f"open({str(marker)!r},'w').write('started')"]
  self.r.register(s)
  with controller_guard(self.state,'A',1):
   self.r.start(s['job_id']);time.sleep(.3)
   self.assertFalse(marker.exists())
  deadline=time.time()+3
  while time.time()<deadline and not marker.exists():time.sleep(.05)
  self.assertTrue(marker.exists(),(self.state/(s['job_id']+'.runner.log')).read_text())
  self.r.collect()

 def test_three_unchanged_partial_attempts_stop_automatic_dispatch(self):
  self.worker_config()
  for n in range(1,4):
   s=self.spec(job=f'b-a{n:03}',attempt=f'a{n:03}')
   if n>1:s['previous_job_id']=f'b-a{n-1:03}'
   self.r.register(s);units=[self.unit(i) for i in s['unit_ids']]
   # Revision and evidence-path renaming are deliberately not checkpoint progress.
   for u in units:u['revision']=f'r{n:03}';u['evidence_refs']={'package':str(self.ws/f'draft-r{n:03}')}
   save_json(s['result_path'],self.result(s,units));self.r.finish(s['job_id'],0)
  self.assertEqual(self.r.schedule(),[])
  self.assertEqual(self.r.schedule(),[])
  row=self.r.status('b-a003')[0];self.assertEqual(row['state'],'collected');self.assertEqual(row['reason_code'],'tool_failure');self.assertIn('unchanged checkpoint',row['detail']);self.assertEqual(len(self.r.status()),3)
 def test_checkpoint_advance_allows_partial_continuation(self):
  self.worker_config()
  for n in range(1,4):
   s=self.spec(job=f'b-a{n:03}',attempt=f'a{n:03}')
   if n>1:s['previous_job_id']=f'b-a{n-1:03}'
   self.r.register(s);units=[self.unit(i) for i in s['unit_ids']]
   if n==3:
    for u in units:u.update(last_completed_stage='page_qa',next_stage='projected')
   save_json(s['result_path'],self.result(s,units));self.r.finish(s['job_id'],0)
  self.assertEqual(self.r.schedule(),['b-a004'])

if __name__=='__main__':unittest.main()
