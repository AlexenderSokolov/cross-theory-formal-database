import unittest,tempfile,json,hashlib
from pathlib import Path
from restore_pending import reassemble,load_transport
h=lambda b:hashlib.sha256(b).hexdigest()
class OrderedPartTests(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory();self.addCleanup(self.t.cleanup);self.d=Path(self.t.name);self.p=self.d/'transport.json';self.b=b'PK fixture archive exact bytes';parts=[self.b[:12],self.b[12:]];self.m={'schema_version':1,'format':'ordered-binary-parts','archive_name':'bundle.zip','archive_sha256':h(self.b),'archive_bytes':len(self.b),'parts':[]}
  for n,b in enumerate(parts,1):q=self.d/f'part-{n}.bin';q.write_bytes(b);self.m['parts'].append({'name':q.name,'sequence':n,'sha256':h(b),'bytes':len(b)})
  self.write()
 def write(self):self.p.write_text(json.dumps(self.m));self.expected=h(self.p.read_bytes())
 def test_exact_join_and_idempotent_existing(self):
  q,_=reassemble(self.p,self.expected);self.assertEqual(q.read_bytes(),self.b);self.assertEqual(reassemble(self.p,self.expected)[0],q)
 def test_corrupt_part_rejected_before_output(self):
  (self.d/'part-1.bin').write_bytes(b'bad');self.assertRaises(ValueError,reassemble,self.p,self.expected);self.assertFalse((self.d/'bundle.zip').exists())
 def test_missing_part_rejected(self):
  (self.d/'part-2.bin').unlink();self.assertRaises(ValueError,reassemble,self.p,self.expected)
 def test_sequence_reordered_rejected(self):
  self.m['parts'].reverse();self.write();self.assertRaises(ValueError,reassemble,self.p,self.expected)
 def test_traversal_rejected(self):
  self.m['parts'][0]['name']='../escape.bin';self.write();self.assertRaises(ValueError,reassemble,self.p,self.expected)
 def test_manifest_hash_rejected(self):self.assertRaises(ValueError,reassemble,self.p,'0'*64)
 def test_differing_destination_preserved(self):
  q=self.d/'bundle.zip';q.write_bytes(b'existing');self.assertRaises(FileExistsError,reassemble,self.p,self.expected);self.assertEqual(q.read_bytes(),b'existing')
 def test_symlink_destination_rejected(self):
  q=self.d/'bundle.zip';q.symlink_to(self.d/'part-1.bin');self.assertRaises(ValueError,reassemble,self.p,self.expected)
if __name__=='__main__':unittest.main()
