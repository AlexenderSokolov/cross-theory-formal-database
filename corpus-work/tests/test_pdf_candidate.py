import hashlib,importlib.util,json,tempfile,unittest
from pathlib import Path
from pypdf import PdfWriter
P=Path(__file__).parents[1]
def module():
 s=importlib.util.spec_from_file_location('pdf_candidate',P/'scripts/pdf_candidate.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
class PDFCandidateTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name);self.c=self.root/'corpus';(self.c/'raw').mkdir(parents=True)
  w=PdfWriter()
  for _ in range(6):w.add_blank_page(width=600,height=800)
  with (self.c/'raw/original.pdf').open('wb') as f:w.write(f)
  (self.c/'raw/LICENSE').write_text('CC BY 4.0')
  self.spec={'title':'定理 n>d^r','author':'Author','difficulty_level':'H2','difficulty_reason':'Reviewed structural proof','source_path':'raw/original.pdf','source_sha256':hashlib.sha256((self.c/'raw/original.pdf').read_bytes()).hexdigest(),'source_url':'https://example.com/paper.pdf','source_version':'revision123','license_path':'raw/LICENSE','license':'CC BY 4.0','statement_pages':[2],'proof_pages':[3,4],'context_pages':[1,4,6],'source_locator':{'theorem':'Theorem 3.1'},'proof_review':{'reviewed':True,'context_checked':True,'method':'original reading','note':'Statement and proof compared'},'dedup_key':'paper:theorem3.1','retrieved_at':'2026-09-30'}
 def tearDown(self):self.temp.cleanup()
 def test_exact_union_pages_and_unicode_cover(self):
  tex,meta=module().build(self.c,self.spec)
  self.assertIn('pages={1,2,3,4,6}',tex);self.assertNotIn('pages=-',tex)
  self.assertIn('Noto Serif CJK SC',tex);self.assertIn('\\XeTeXlinebreaklocale "zh"',tex);self.assertIn('\\usepackage{xurl}',tex)
  self.assertEqual(meta['source_locator'],{'theorem':'Theorem 3.1'})
  self.assertEqual(meta['source_sha256'],self.spec['source_sha256'])
 def test_out_of_range_rejected(self):
  self.spec['proof_pages']=[7]
  with self.assertRaisesRegex(ValueError,'range'):module().build(self.c,self.spec)
 def test_source_hash_mismatch_rejected(self):
  self.spec['source_sha256']='0'*64
  with self.assertRaisesRegex(ValueError,'hash'):module().build(self.c,self.spec)
 def test_hold_is_carried_and_never_claims_complete(self):
  self.spec['admission_hold']='Proof incomplete';self.spec['proof_review']['reviewed']=False
  _,m=module().build(self.c,self.spec)
  self.assertEqual(m['admission_hold'],'Proof incomplete');self.assertFalse(m['proof_complete'])
 def test_unique_locator_and_authored_difficulty_required(self):
  self.spec.pop('source_locator')
  with self.assertRaisesRegex(ValueError,'locator'):module().build(self.c,self.spec)
