import json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
sys.path.append('/disks/sata1/yupeng/human-proof-corpus/repo/corpus-work/scripts')
import corpus_batch as batch

class StepResume(unittest.TestCase):
    def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
    def tearDown(self):self.tmp.cleanup()
    def command(self,name):
        p=self.root/name
        return [sys.executable,'-c','from pathlib import Path; p=Path('+repr(str(p))+'); p.write_text(str(int(p.read_text())+1) if p.exists() else "1")']
    def test_successful_first_step_not_repeated_after_second_failure(self):
        batch.run_stage_command(self.root,0,self.command('first'))
        flag=self.root/'failed-once';counter=self.root/'second'
        argv=[sys.executable,'-c','from pathlib import Path; import sys; p=Path('+repr(str(flag))+'); exists=p.exists(); p.touch(); Path('+repr(str(counter))+').write_text("finished" if exists else "partial"); sys.exit(0 if exists else 1)']
        with self.assertRaises(ValueError):batch.run_stage_command(self.root,1,argv)
        batch.run_stage_command(self.root,0,self.command('first'));batch.run_stage_command(self.root,1,argv)
        self.assertEqual((self.root/'first').read_text(),'1');self.assertEqual(counter.read_text(),'finished')
        self.assertTrue((self.root/'1.attempt-0.json').exists())
    def test_output_complete_receipt_lost_is_reconciled(self):
        argv=self.command('already-complete');(self.root/'already-complete').write_text('1')
        (self.root/'0.started.json').write_text(json.dumps({'argv':argv,'pid':999999999,'proc_start':'missing','proc_cwd':str(self.root)}))
        batch.run_stage_command(self.root,0,argv,probe=lambda:True)
        self.assertEqual((self.root/'already-complete').read_text(),'1')
        self.assertTrue(json.loads((self.root/'0.json').read_text())['reconciled_output'])
    def test_current_live_process_cannot_relaunch(self):
        from corpus_runtime import identity
        import os
        info=identity(os.getpid());argv=self.command('never')
        (self.root/'0.started.json').write_text(json.dumps({'argv':argv,'pid':info['pid'],'proc_start':info['start_time'],'proc_cwd':info['cwd']}))
        with self.assertRaisesRegex(ValueError,'live'):batch.run_stage_command(self.root,0,argv)
        self.assertFalse((self.root/'never').exists())

if __name__=='__main__':unittest.main()
