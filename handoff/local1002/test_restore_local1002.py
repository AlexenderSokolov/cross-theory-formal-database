import unittest,tempfile,json,hashlib,zipfile,io,stat
from pathlib import Path
from restore_local1002 import restore_plan
h=lambda b:hashlib.sha256(b).hexdigest()
class RestoreTests(unittest.TestCase):
 def fixture(self,root):
  base=root/'base';base.mkdir();(base/'old.txt').write_bytes(b'base');manifest=json.dumps({'items':[{'problem_id':'001'},{'problem_id':'002'}],'verified_count':2}).encode();buf=io.BytesIO()
  with zipfile.ZipFile(buf,'w',zipfile.ZIP_DEFLATED) as z:
   for data in [b'new',manifest]:
    info=zipfile.ZipInfo('blobs/'+h(data));info.external_attr=(stat.S_IFREG|0o644)<<16;z.writestr(info,data)
  raw=buf.getvalue();handoff=root/'handoff';local=handoff/'local1002';local.mkdir(parents=True);(local/'part.bin').write_bytes(raw);tr={'schema_version':1,'format':'ordered-binary-parts','archive_sha256':h(raw),'archive_bytes':len(raw),'parts':[{'name':'part.bin','sequence':1,'sha256':h(raw),'bytes':len(raw)}]};tb=json.dumps(tr).encode();(local/'transport.json').write_bytes(tb)
  files=[{'path':'old.txt','sha256':h(b'base'),'bytes':4,'mode':420,'kind':'base'},{'path':'new.txt','sha256':h(b'new'),'bytes':3,'mode':420,'kind':'overlay'},{'path':'manifest.json','sha256':h(manifest),'bytes':len(manifest),'mode':420,'kind':'overlay'}];plan={'schema_version':1,'format':'exact-base-plus-shared-cas-overlay','target_count':2,'files':files,'cas_sources':{'overlay':{'transport_path':'local1002/transport.json','transport_sha256':h(tb)}}};pb=json.dumps(plan).encode();pp=local/'plan.json';pp.write_bytes(pb);return base,handoff,pp,h(pb)
 def test_exact_base_plus_object_restore(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);base,hand,plan,sha=self.fixture(root);out=root/'out';r=restore_plan(plan,sha,hand,base,out);self.assertEqual(r['restored_files'],3);self.assertEqual((out/'old.txt').read_bytes(),b'base');self.assertEqual((out/'new.txt').read_bytes(),b'new')
 def test_changed_base_refused(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);b,hand,p,s=self.fixture(root);(b/'old.txt').write_bytes(b'evil')
   with self.assertRaises(ValueError):restore_plan(p,s,hand,b,root/'out')
 def test_missing_part_refused(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);b,hand,p,s=self.fixture(root);(hand/'local1002/part.bin').unlink()
   with self.assertRaises(ValueError):restore_plan(p,s,hand,b,root/'out')
 def test_traversal_refused(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);b,hand,p,s=self.fixture(root);r=json.loads(p.read_bytes());r['files'][0]['path']='../escape';raw=json.dumps(r).encode();p.write_bytes(raw)
   with self.assertRaises(ValueError):restore_plan(p,h(raw),hand,b,root/'out')
 def test_existing_destination_refused(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);b,hand,p,s=self.fixture(root);out=root/'out';out.mkdir();(out/'old.txt').write_bytes(b'important')
   with self.assertRaises(FileExistsError):restore_plan(p,s,hand,b,out)
   self.assertEqual((out/'old.txt').read_bytes(),b'important')
if __name__=='__main__':unittest.main()
