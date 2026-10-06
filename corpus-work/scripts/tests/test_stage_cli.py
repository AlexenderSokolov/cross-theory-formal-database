"""O01/P01 staging CLI contract against a real Linux publication flock."""
import json,os,shutil,subprocess,sys,unittest
from pathlib import Path
import test_delta_staging as fixtures
dump=fixtures.dump
HERE=Path(__file__).resolve().parent

@unittest.skipUnless(os.name=='posix','real publication guard uses Linux fcntl/proc')
class StageCLITests(unittest.TestCase):
 def setUp(self):
  self.fixture=fixtures.Tests();self.fixture.setUp();f=self.fixture;prep=f.prepare();self.project=f.r/'cli-project';self.repo=self.project/'repo';self.repo.mkdir(parents=True)
  subprocess.run(['git','init','-q',str(self.repo)],check=True)
  for k,v in [('user.email','fixture@example.invalid'),('user.name','Fixture'),('core.autocrlf','false')]:subprocess.run(['git','-C',str(self.repo),'config',k,v],check=True)
  for row in json.loads(f.oldlist.read_text())['files']:
   target=self.repo/'editable-corpus'/row['path'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f.base/row['path'],target)
  dump(self.repo/'handoff/yupeng/PRODUCTION_QUEUE.json',{'fixture':True});subprocess.run(['git','-C',str(self.repo),'add','--','editable-corpus','handoff'],check=True);subprocess.run(['git','-C',str(self.repo),'commit','-qm','fixture'],check=True)
  self.batch=f.r/'cli-batch';self.batch.mkdir();shutil.copytree(f.out,self.batch/'release');dump(self.batch/'batch.json',dict(expected_count=2));dump(self.batch/'merge/batch-result.json',{'fixture':True});dump(self.batch/'material-review.json',{'fixture':True})
  self.state=self.project/'operations/corpusctl';self.state.mkdir(parents=True);dump(self.state/'owner.json',dict(owner='current',generation=2))
 def tearDown(self):self.fixture.tearDown()
 def run_cli(self,*args):
  return subprocess.run([sys.executable,'-B',str(HERE/'stage_corpus_release.py'),str(self.batch),'--project',str(self.project),*args],capture_output=True,text=True)
 def test_O01_real_CLI_requires_actor_and_live_registered_guard(self):
  missing=self.run_cli();self.assertNotEqual(missing.returncode,0);self.assertFalse((self.batch/'git-staging.json').exists())
  no_token=self.run_cli('--owner','current','--generation','2','--guard-held');self.assertNotEqual(no_token.returncode,0);self.assertIn('guard token required',no_token.stderr)
  stale=self.run_cli('--owner','current','--generation','2','--guard-held','--publication-guard','999999/fixture');self.assertNotEqual(stale.returncode,0);self.assertFalse((self.batch/'git-staging.json').exists())
  code="""import fcntl,json,os,sys
from pathlib import Path
os.chdir(sys.argv[1]);f=open('publication.lock','a');fcntl.flock(f,fcntl.LOCK_EX)
s=Path('/proc/self/stat').read_text().rsplit(')',1)[1].split();token=str(os.getpid())+'/'+s[19]
Path('publication-guard.json').write_text(json.dumps({'token':token}));print(token,flush=True);sys.stdin.read()
"""
  guard=subprocess.Popen([sys.executable,'-B','-c',code,str(self.state)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
  try:
   token=guard.stdout.readline().strip();self.assertTrue(token)
   old=self.run_cli('--owner','old','--generation','1','--guard-held','--publication-guard',token);self.assertNotEqual(old.returncode,0);self.assertIn('actor rejected',old.stderr);self.assertFalse((self.batch/'git-staging.json').exists())
   current=self.run_cli('--owner','current','--generation','2','--guard-held','--publication-guard',token);self.assertEqual(current.returncode,0,current.stderr);self.assertTrue((self.batch/'git-staging.json').is_file())
  finally:guard.communicate('',timeout=10)
  gone=self.run_cli('--owner','current','--generation','2','--guard-held','--publication-guard',token);self.assertNotEqual(gone.returncode,0);self.assertIn('not live/current',gone.stderr)
if __name__=='__main__':unittest.main()
