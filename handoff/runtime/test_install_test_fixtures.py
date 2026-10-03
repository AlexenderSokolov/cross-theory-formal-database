import tempfile,unittest,json,hashlib
from pathlib import Path
from install_test_fixtures import install
class Tests(unittest.TestCase):
 def test_roundtrip_and_idempotence(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);(p/'project/scripts').mkdir(parents=True);(p/'project/scripts/stacks_extract.py').write_text('');(p/'src').mkdir();(p/'src/a.tex').write_bytes(b'abc');m=p/'manifest.json';m.write_text(json.dumps({'source_dir':'src','files':[{'path':'a.tex','bytes':3,'sha256':hashlib.sha256(b'abc').hexdigest()}]}));self.assertEqual(install(p/'project',m)['installed'],1);self.assertEqual(install(p/'project',m)['installed'],0)
 def test_refuse_existing_difference(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);(p/'project/scripts').mkdir(parents=True);(p/'project/scripts/stacks_extract.py').write_text('');(p/'src').mkdir();(p/'src/a.tex').write_bytes(b'abc');m=p/'manifest.json';m.write_text(json.dumps({'source_dir':'src','files':[{'path':'a.tex','bytes':3,'sha256':hashlib.sha256(b'abc').hexdigest()}]}));q=p/'project/corpus/raw/stacks-project/a.tex';q.parent.mkdir(parents=True);q.write_bytes(b'keep');
   with self.assertRaises(ValueError):install(p/'project',m)
   self.assertEqual(q.read_bytes(),b'keep')
if __name__=='__main__':unittest.main()
