"""Linux native counterexample: an external child writes after its stage parent dies."""
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest
import controller_publish_pipeline as pipeline


@unittest.skipUnless(sys.platform=='linux','requires native Linux /proc and process groups')
class WriterGroupTests(unittest.TestCase):
    def test_parent_terminal_does_not_release_live_child_writer(self):
        namespace={};exec(pipeline.PROCESS_SUPPORT,namespace)
        terminal=namespace['external_writer_groups_terminal']
        fixture=Path(tempfile.mkdtemp(prefix='corpus-publication-fixture-'))
        marker=fixture/'child-writer.txt'
        writer="import pathlib,sys,time; p=pathlib.Path(sys.argv[1]); n=0\nwhile True:\n n+=1; p.write_text(str(n)); time.sleep(.05)"
        parent_code="import subprocess,sys,json,time; child=subprocess.Popen([sys.executable,'-B','-c',sys.argv[1],sys.argv[2]],start_new_session=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); print(json.dumps({'pid':child.pid}),flush=True); time.sleep(30)"
        parent=subprocess.Popen([sys.executable,'-B','-c',parent_code,writer,str(marker)],stdout=subprocess.PIPE,text=True)
        child=json.loads(parent.stdout.readline())['pid']
        try:
            deadline=time.monotonic()+5
            while not marker.exists() and time.monotonic()<deadline:time.sleep(.02)
            self.assertTrue(marker.exists())
            before=int(marker.read_text());parent.kill();parent.wait(timeout=5)
            # This is the old faulty criterion, now insufficient.
            self.assertIsNotNone(parent.returncode)
            record={'writer_groups':[{'pgid':child}]}
            self.assertFalse(terminal(record))
            time.sleep(.15);self.assertGreater(int(marker.read_text()),before)
            os.killpg(child,signal.SIGTERM)
            deadline=time.monotonic()+5
            while not terminal(record) and time.monotonic()<deadline:time.sleep(.02)
            self.assertTrue(terminal(record))
            with self.assertRaisesRegex(ValueError,'legacy stage receipt'):
                terminal({'process_identity':{'pid':parent.pid}})
            print(json.dumps({'parent_terminal':True,'child_wrote_after_parent_died':True,'child_group_terminal_confirmed':True,'fixture':str(fixture)}))
        finally:
            if parent.poll() is None:parent.kill();parent.wait()
            try:os.killpg(child,signal.SIGTERM)
            except ProcessLookupError:pass
            parent.stdout.close()


if __name__=='__main__':unittest.main()
