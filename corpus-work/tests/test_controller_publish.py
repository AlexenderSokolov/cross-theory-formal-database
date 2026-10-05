import importlib.util,json,subprocess,tempfile,unittest
from pathlib import Path

SCRIPTS=Path(__file__).resolve().parents[1]/'scripts'
spec=importlib.util.spec_from_file_location('relay',SCRIPTS/'publish_corpus_bundle.py')
relay=importlib.util.module_from_spec(spec);spec.loader.exec_module(relay)

class PublishTests(unittest.TestCase):
 def test_real_git_incremental_push_retry_and_concurrent_advance(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);src=root/'src';remote=root/'remote.git';cache=root/'relay.git'
   def git(*args):return relay.run(['git',*map(str,args)],cwd=src if src.exists() else root)
   git('init',src);git('config','user.email','fixture@example.invalid');git('config','user.name','Fixture')
   git('checkout','-b','corpus-progress-20261001')
   (src/'proof.txt').write_text('fixture not mathematical result');git('add','proof.txt');git('commit','-m','base')
   base=git('rev-parse','HEAD');git('init','--bare',remote);git('push',remote,'HEAD:corpus-progress-20261001')
   (src/'proof.txt').write_text('engineering fixture revision');git('commit','-am','next');head=git('rev-parse','HEAD')
   bundle=root/'next.bundle';git('bundle','create',bundle,base+'..HEAD')
   result=relay.publish(bundle,cache,'corpus-progress-20261001',base,str(remote))
   self.assertEqual(result['commit'],head);self.assertEqual(result['remote_count_increment'],0)
   self.assertEqual(relay.publish(bundle,cache,'corpus-progress-20261001',base,str(remote))['status'],'already_pushed_requires_public_restore')
   (src/'proof.txt').write_text('concurrent revision');git('commit','-am','concurrent');git('push',remote,'HEAD:corpus-progress-20261001')
   with self.assertRaises(ValueError):relay.publish(bundle,cache,'corpus-progress-20261001',base,str(remote))

if __name__=='__main__':unittest.main()
