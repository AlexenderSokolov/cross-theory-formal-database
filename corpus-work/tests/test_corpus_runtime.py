import importlib.util,json,os,sqlite3,subprocess,sys,tempfile,time,unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('corpus_runtime',Path(__file__).parents[1]/'scripts/corpus_runtime.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class RuntimeTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.r=m.Runtime(self.root/'runtime.sqlite')
 def tearDown(self): self.tmp.cleanup()
 def job(self,ident='j',code="from pathlib import Path; p=Path('calls'); p.write_text(p.read_text()+'x' if p.exists() else 'x')"):
  return self.r.claim(ident,ident,self.root,[{'name':'work','argv':[sys.executable,'-c',code]}])
 def wait(self,ident='j',state='awaiting_admission'):
  deadline=time.time()+10
  while time.time()<deadline:
   row=self.r.collect(ident)[0]
   if row['state']==state:return row
   time.sleep(.02)
  self.fail(str(self.r.status(ident)))
 def test_response_lost_start_is_idempotent(self):
  self.job();self.r.start('j');self.r.start('j');self.wait()
  self.assertEqual((self.root/'calls').read_text(),'x')
  self.r.resume('j');self.assertEqual((self.root/'calls').read_text(),'x')
 def test_claim_mutex_and_job_id(self):
  self.job()
  self.job()
  with self.assertRaises(ValueError):self.r.claim('j','different',self.root,[{'name':'x','argv':['true']}])
  with self.assertRaises(sqlite3.IntegrityError):self.r.claim('other','j',self.root,[{'name':'x','argv':['true']}])
 def test_dead_pid_unknown_stage_is_not_replayed(self):
  self.job()
  with self.r.tx() as c:
   c.execute("UPDATE jobs SET state='running',pid=999999999,proc_start='1',proc_cwd=?",(str(self.root),))
   c.execute("INSERT INTO stage_runs VALUES('j',0,'running',NULL,NULL,NULL,NULL,NULL)")
  self.assertEqual(self.r.collect('j')[0]['state'],'interrupted')
  with self.assertRaises(ValueError):self.r.resume('j')
  self.assertFalse((self.root/'calls').exists())
 def test_restart_resumes_next_stage_only(self):
  self.r.claim('j','j',self.root,[{'name':'old','argv':[sys.executable,'-c',"raise Exception('must not replay')"]},{'name':'next','argv':[sys.executable,'-c',"from pathlib import Path;Path('next').write_text('ok')"]}])
  with self.r.tx() as c:
   c.execute("UPDATE jobs SET state='running',next_stage=1,pid=999999999")
   c.execute("INSERT INTO stage_runs VALUES('j',0,'succeeded',NULL,NULL,0,NULL,NULL)")
  restarted=m.Runtime(self.r.db);self.assertEqual(restarted.collect('j')[0]['state'],'queued')
  restarted.resume('j');self.wait();self.assertEqual((self.root/'next').read_text(),'ok')
 def test_executor_restart_does_not_restart_live_runner(self):
  self.job(code="import time;time.sleep(.2);from pathlib import Path;Path('calls').write_text('x')")
  self.r.start('j')
  deadline=time.time()+5
  while not self.r.status('j')[0]['live'] and time.time()<deadline:time.sleep(.02)
  pid=self.r.status('j')[0]['pid'];fresh=m.Runtime(self.r.db);fresh.collect();fresh.resume('j')
  self.assertEqual(fresh.status('j')[0]['pid'],pid);self.wait()
 def test_adopt_process_terminal(self):
  terminal=self.root/'terminal.json'
  p=subprocess.Popen([sys.executable,'-c',"import time;time.sleep(.2)"],cwd=self.root)
  self.r.adopt('j',['a','b'],self.root,p.pid,exit_record=terminal)
  self.r.resume('j');self.assertEqual(self.r.status('j')[0]['pid'],p.pid)
  code=p.wait();terminal.write_text(json.dumps({'exit_code':code}))
  self.assertEqual(self.r.collect('j')[0]['state'],'awaiting_admission')
 def test_limit_requires_explicit_safe_policy_and_delays(self):
  self.r.claim('j','j',self.root,[{'name':'cli','argv':[sys.executable,'-c',"import sys; print('Concurrency limit exceeded');sys.exit(1)"],'retry_on_limit':True}])
  self.r.start('j');row=self.wait(state='rate_limited')
  self.assertGreater(row['next_attempt_at'],time.time());self.assertEqual(row['next_stage'],0)
  self.r.resume('j');self.assertEqual(self.r.status('j')[0]['state'],'rate_limited')
 def test_no_limit_retry_after_command_event(self):
  self.r.claim('j','j',self.root,[{'name':'cli','argv':[sys.executable,'-c',"import sys;print('command_execution Concurrency limit exceeded');sys.exit(1)"],'retry_on_limit':True}])
  self.r.start('j');self.wait(state='failed')
  with self.assertRaises(ValueError):self.r.resume('j')
 def test_max_three_and_duplicate_queued_start(self):
  for n in range(4):self.job(str(n),code="import time;time.sleep(.5)")
  for n in range(4):self.r.start(str(n))
  rows=self.r.status();self.assertEqual(sum(r['state'] in ('running','starting') for r in rows),3)
  self.assertEqual(self.r.status('3')[0]['state'],'queued')
  for n in range(3):self.wait(str(n))
  self.r.resume('3');self.wait('3')
 def test_terminal_import_and_reviewed_revision(self):
  terminal=self.root/'terminal.json';terminal.write_text(json.dumps({'exit_code':1}))
  self.r.adopt('old',['a','b'],self.root,999999999,exit_record=terminal)
  self.r.revise('new','old',self.root,[{'name':'work','argv':[sys.executable,'-c',"pass"]}],['doi:x'])
  self.assertEqual(self.r.status('new')[0]['work_keys'],['a','b','doi:x'])
  self.assertEqual(self.r.status('old')[0]['work_keys'],[])
  self.r.start('new');self.wait('new')
 def test_dead_supervisor_preserves_live_child(self):
  self.job(code="import time;time.sleep(.8)")
  self.r.start('j')
  deadline=time.time()+5
  while not self.r.status('j')[0]['child_live'] and time.time()<deadline:time.sleep(.02)
  row=self.r.status('j')[0];self.assertTrue(row['child_live'])
  os.kill(row['pid'],9)
  time.sleep(.05)
  row=self.r.collect('j')[0];self.assertEqual(row['state'],'orphan_running');self.assertTrue(row['child_live'])
  with self.assertRaises(ValueError):self.r.revise('new','j',self.root,[{'name':'work','argv':['true']}])
  with self.assertRaises(ValueError):self.r.resume('j')
  time.sleep(.9)
if __name__=='__main__':unittest.main()