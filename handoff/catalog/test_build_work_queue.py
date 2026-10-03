import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
SCRIPT=HERE/'build_work_queue.py'
INPUT_NAMES=['candidate_catalog.jsonl','candidate_record_history.jsonl.gz','source_works.jsonl','materials_inventory.jsonl']
class WorkQueueSafetyTests(unittest.TestCase):
 def test_wrong_snapshot_counts_fail_before_output(self):
  with tempfile.TemporaryDirectory() as name:
   root=Path(name)
   for filename in INPUT_NAMES:(root/filename).symlink_to(HERE/filename)
   counts=json.loads((HERE/'counts_and_reconciliation.json').read_text())
   counts['source_approved_ids']+=1
   (root/'counts_and_reconciliation.json').write_text(json.dumps(counts))
   output=root/'new.sqlite'
   result=subprocess.run([sys.executable,str(SCRIPT),'--input-dir',str(root),'--output',str(output)],capture_output=True,text=True)
   self.assertNotEqual(result.returncode,0)
   self.assertIn('Snapshot source/Git counts do not match',result.stderr)
   self.assertFalse(output.exists())
   self.assertFalse(list(root.glob('*.building-*.sqlite')))
 def test_existing_different_destination_is_preserved(self):
  with tempfile.TemporaryDirectory() as name:
   root=Path(name);output=root/'existing.sqlite';original=b'Existing unrelated file: preserve exact bytes\n';output.write_bytes(original)
   result=subprocess.run([sys.executable,str(SCRIPT),'--output',str(output)],capture_output=True,text=True)
   self.assertNotEqual(result.returncode,0)
   self.assertIn('refused overwrite',result.stderr)
   self.assertEqual(output.read_bytes(),original)
   self.assertFalse(list(root.glob('*.building-*.sqlite')))
if __name__=='__main__':unittest.main()
