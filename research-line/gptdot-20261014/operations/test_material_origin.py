"""Focused check of origin metadata preservation, without compiling any proof."""
import json, subprocess, sys, tempfile, unittest
from pathlib import Path
SCRIPT=Path(__file__).with_name('material_origin.py')
class OriginTests(unittest.TestCase):
 def test_formal_proof_origin_updates_manifest_and_provenance(self):
  with tempfile.TemporaryDirectory() as tmp:
   job=Path(tmp); pkg=job/'package-root-r001'; (pkg/'sources/material-x').mkdir(parents=True)
   state={'status':'assembled','package':pkg.name,'task_snapshot':'sources/material-x/prepared-task.json'}
   row={'problem_id':'material-x','origin_class':'human_authored_native_tex','title':'unchanged','proof_spans':[{'path':'proof.lean','start_line':1,'end_line':9}]}
   (job/'job-state.json').write_text(json.dumps(state))
   (pkg/state['task_snapshot']).write_text(json.dumps({'origin_class':'human_authored_proof_assistant_transcription'}))
   (pkg/'manifest.json').write_text(json.dumps({'schema_version':2,'items':[row]}))
   (pkg/'sources/material-x/provenance.json').write_text(json.dumps(row))
   r=subprocess.run([sys.executable,str(SCRIPT),'--job',str(job)],capture_output=True,text=True)
   self.assertEqual(r.returncode,0,r.stderr)
   expected={**row,'origin_class':'human_authored_proof_assistant_transcription'}
   self.assertEqual(json.loads((pkg/'manifest.json').read_text())['items'],[expected])
   self.assertEqual(json.loads((pkg/'sources/material-x/provenance.json').read_text()),expected)
   self.assertEqual(json.loads((job/'job-state.json').read_text()),state)
if __name__=='__main__':unittest.main()
