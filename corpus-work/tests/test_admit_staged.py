import importlib.util,json,tempfile,unittest
from pathlib import Path
P=Path(__file__).parents[1]
def module():
 s=importlib.util.spec_from_file_location('admit',P/'scripts/admit_staged.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
class AdmissionTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name);self.c=self.root/'corpus';self.c.mkdir();(self.c/'item_status.json').write_text(json.dumps({'schema_version':1,'items':{'001':{'status':'quarantined'}}}))
 def tearDown(self):self.temp.cleanup()
 def test_id_reservations_are_stable(self):
  m=module();r={};self.assertEqual(m.reserve_id(self.c,r,{'dedup_key':'stacks:AAAA'}),'002');self.assertEqual(m.reserve_id(self.c,r,{'dedup_key':'stacks:AAAA'}),'002');self.assertEqual(m.reserve_id(self.c,r,{'dedup_key':'stacks:BBBB'}),'003')
 def test_existing_id_preserved(self):
  r={};self.assertEqual(module().reserve_id(self.c,r,{'id':'241','dedup_key':'stacks:AAAA'}),'241')
 def test_id_collision_rejected(self):
  m=module();r={};m.reserve_id(self.c,r,{'id':'241','dedup_key':'stacks:AAAA'})
  with self.assertRaisesRegex(ValueError,'collision'):m.reserve_id(self.c,r,{'id':'241','dedup_key':'stacks:BBBB'})
 def test_index_contains_only_active(self):
  (self.c/'metadata').mkdir();(self.c/'metadata/002.json').write_text(json.dumps({'id':'002','title':'A','difficulty_level':'H2','author':'Stacks','source_url':'https://example.com'}))
  module().write_index(self.c,{'001':{'status':'quarantined'},'002':{'status':'active','metadata':'metadata/002.json'}})
  t=(self.c/'INDEX.md').read_text();self.assertIn('| 002 |',t);self.assertNotIn('| 001 |',t)
 def test_source_path_escape_rejected(self):
  with self.assertRaisesRegex(ValueError,'corpus'):module().corpus_path(self.c,'/etc/passwd')
 def staged(self):
  import hashlib
  raw=self.c/'raw';raw.mkdir();(raw/'source.tex').write_text('\\begin{theorem}A.\\end{theorem}\n\\begin{proof}Author proof.\\end{proof}')
  stage=self.root/'stage';stage.mkdir();(stage/'AAAA.tex').write_text('\\documentclass{amsart}\\begin{document}A.\\end{document}')
  (stage/'AAAA.excerpt.tex').write_text((raw/'source.tex').read_text());(stage/'COPYING').write_text('License')
  m={'tag':'AAAA','dedup_key':'stacks:AAAA','source_path':str(raw/'source.tex'),'source_sha256':hashlib.sha256((raw/'source.tex').read_bytes()).hexdigest(),'tex_path':str(stage/'AAAA.tex'),'excerpt_path':str(stage/'AAAA.excerpt.tex'),'license_path':str(stage/'COPYING'),'title':'A','author':'Authors','difficulty_level':'H2','difficulty_reason':'Reviewed reason','source_url':'https://example.com','source_version':'pin','retrieved_at':'2026-09-30','proof_complete':True,'proof_review':{'reviewed':True,'context_checked':True,'method':'source-reading','note':'Full source'},'evidence_mode':'native_tex','source_locator':{'start_line':1,'end_line':2}}
  m['excerpt_sha256']=hashlib.sha256((stage/'AAAA.excerpt.tex').read_bytes()).hexdigest();p=stage/'AAAA.metadata.json';p.write_text(json.dumps(m));return p
 def test_failed_real_compiler_never_qualifies_and_retry_keeps_id(self):
  m=module();p=self.staged();r=m.admit(self.root,p,engine='definitely-no-such-tex-engine')
  self.assertEqual(r['status'],'quarantined');self.assertFalse(r['qualified'])
  self.assertNotIn('| '+r['id']+' |',(self.c/'INDEX.md').read_text())
  meta=json.loads((self.c/'metadata'/ (r['id']+'.json')).read_text())
  for field in ['tex_path','source_path','excerpt_path','license_path']:self.assertFalse(Path(meta[field]).is_absolute())
  receipt=json.loads((self.c/'.work/compile_report.json').read_text())[r['id']];self.assertFalse(receipt['ok'])
  again=m.admit(self.root,p,engine='definitely-no-such-tex-engine');self.assertEqual(again['id'],r['id'])
 def test_admission_hold_rejects_before_compile(self):
  p=self.staged();d=json.loads(p.read_text());d['admission_hold']='Incomplete proof core';p.write_text(json.dumps(d))
  with self.assertRaisesRegex(ValueError,'hold'):module().admit(self.root,p,engine='definitely-no-such-tex-engine')
  self.assertFalse((self.c/'.work/compile_report.json').exists())
 def test_pdf_import_has_generic_filename_and_content_addressed_license(self):
  p=self.staged();m=json.loads(p.read_text());m['evidence_mode']='source_pdf_pages'
  out=module().import_metadata(self.c,p.parent,m,'241')
  self.assertEqual(Path(out['tex_path']).name,'241_source_pdf.tex')
  self.assertNotIn('stacks',out['tex_path'])
  self.assertTrue(out['license_path'].startswith('assets/license-'))
