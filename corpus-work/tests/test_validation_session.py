import importlib.util, json, os, unittest
from pathlib import Path
from unittest.mock import patch
import test_pipeline as fixtures
ROOT=fixtures.ROOT

class ValidationSession(unittest.TestCase):
 save=fixtures.Pipeline.save
 tearDown=fixtures.Pipeline.tearDown
 def setUp(self):
  fixtures.Pipeline.setUp(self)
  spec=importlib.util.spec_from_file_location('session_validator',ROOT/'scripts/validate_corpus.py')
  self.v=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.v)
 def assert_bad(self, report, message):
  self.assertEqual(report['qualified_count'],0);self.assertIn(message,str(report))
 def test_session_reuses_bytes_and_restored_mtime_source_change_invalidates(self):
  source=self.c/'raw/s.tex';original=Path.read_bytes;reads=[]
  def read(path):
   if path.resolve()==source.resolve():reads.append(path)
   return original(path)
  with self.v.validation_session(), patch.object(Path,'read_bytes',read):
   self.assertEqual(self.v.validate_in_session(self.root)['qualified_count'],1)
   self.assertEqual(self.v.validate_in_session(self.root)['qualified_count'],1)
   self.assertEqual(len(reads),1)
   stat=source.stat();source.write_text(source.read_text().replace('A','Z',1));os.utime(source,ns=(stat.st_atime_ns,stat.st_mtime_ns))
   self.assert_bad(self.v.validate_in_session(self.root),'source hash mismatch')
 def test_wrapper_change_invalidates_in_session(self):
  with self.v.validation_session():
   self.v.validate_in_session(self.root)
   p=self.c/self.m['tex_path'];p.write_text(p.read_text()+'changed')
   self.assert_bad(self.v.validate_in_session(self.root),'compile input hash mismatch')
 def test_receipt_manifest_index_mutations_are_reparsed(self):
  for kind in ['receipt','manifest','INDEX']:
   with self.subTest(kind=kind),self.v.validation_session():
    self.assertEqual(self.v.validate_in_session(self.root)['qualified_count'],1)
    path={'receipt':self.c/'.work/compile_report.json','manifest':self.c/'item_status.json','INDEX':self.c/'INDEX.md'}[kind];before=path.read_text()
    if kind=='receipt':data=json.loads(before);data['1001']['ok']=False;path.write_text(json.dumps(data))
    elif kind=='manifest':data=json.loads(before);data['items']['1001']['status']='quarantined';path.write_text(json.dumps(data))
    else:path.write_text('')
    self.assertEqual(self.v.validate_in_session(self.root)['qualified_count'],0)
    path.write_text(before)
    self.assertEqual(self.v.validate_in_session(self.root)['qualified_count'],1)
 def test_pdf_replacement_invalidates_page_count_and_hash(self):
  from pypdf import PdfWriter
  p=self.c/'raw/context.pdf'
  def write(n):
   w=PdfWriter()
   for _ in range(n):w.add_blank_page(width=100,height=100)
   with p.open('wb') as f:w.write(f)
  write(1)
  with self.v.validation_session():
   first=self.v.sha(p);self.assertEqual(self.v.pdf_page_count(p),1)
   write(2);self.assertNotEqual(self.v.sha(p),first);self.assertEqual(self.v.pdf_page_count(p),2)
 def test_session_lifecycle_and_outside_call_rejection(self):
  with self.assertRaises(RuntimeError):self.v.validate_in_session(self.root)
  with self.v.validation_session():self.assertEqual(self.v.validate_in_session(self.root)['qualified_count'],1)
  with self.assertRaises(RuntimeError):self.v.validate_in_session(self.root)
  with self.assertRaises(ValueError):
   with self.v.validation_session():raise ValueError('fixture')
  with self.assertRaises(RuntimeError):self.v.validate_in_session(self.root)
 def test_ordinary_validate_nested_in_session_is_fresh(self):
  source=self.c/'raw/s.tex';original=Path.read_bytes;reads=[]
  def read(path):
   if path.resolve()==source.resolve():reads.append(path)
   return original(path)
  with self.v.validation_session(),patch.object(Path,'read_bytes',read):
   self.v.validate_in_session(self.root);self.v.validate(self.root);self.v.validate_in_session(self.root)
   self.assertEqual(len(reads),2)
 def test_final_gate_after_session_rereads_and_detects_mutation(self):
  source=self.c/'raw/s.tex';original=Path.read_bytes;reads=[]
  def read(path):
   if path.resolve()==source.resolve():reads.append(path)
   return original(path)
  with patch.object(Path,'read_bytes',read):
   with self.v.validation_session():self.v.validate_in_session(self.root)
   self.assertEqual(self.v.validate(self.root)['qualified_count'],1);self.assertEqual(len(reads),2)
   source.write_text(source.read_text().replace('A','Z',1))
   self.assert_bad(self.v.validate(self.root),'source hash mismatch')
