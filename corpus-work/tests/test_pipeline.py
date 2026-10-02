import json, subprocess, sys, tempfile, unittest, hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
class Pipeline(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.c=self.root/'corpus'
  for p in ['tex','raw','metadata','.work/build/1001']:(self.c/p).mkdir(parents=True,exist_ok=True)
  (self.c/'raw/s.tex').write_text('\\begin{lemma}A\\end{lemma}\n\\begin{proof}B\\end{proof}\n')
  (self.c/'raw/license.txt').write_text('license')
  (self.c/'tex/1001_example.tex').write_text('\\documentclass{article}\n\\begin{document}\n\\begin{proof}B\\end{proof}\n\\end{document}')
  self.m=dict(id='1001',title='Example',author='Human',source_url='https://example.org/s',source_locator={'start_line':1,'end_line':2},source_path='raw/s.tex',source_sha256=sha(self.c/'raw/s.tex'),source_version='commit1',retrieved_at='2026-09-30',license_path='raw/license.txt',license='GFDL',proof_complete=True,proof_review=dict(reviewed=True,method='source-text-comparison',note='Compared all source lines',context_checked=True),difficulty_level='H2',difficulty_reason='Advanced full argument',dedup_key='claim-a',tex_path='tex/1001_example.tex',evidence_mode='native_tex')
  self.save();(self.c/'item_status.json').write_text(json.dumps({'schema_version':1,'items':{'1001':{'status':'active','metadata':'metadata/1001.json'}}}))
  (self.c/'INDEX.md').write_text('| 编号 | 题名 | 难度 | 来源 | 原文 |\n|---|---|---|---|---|\n| 1001 | Example | H2 | Human | https://example.org/s |\n')
  pdf=self.c/'.work/build/1001/test.pdf';pdf.write_bytes(b'%PDF-1.4\nfixture')
  (self.c/'.work/compile_report.json').write_text(json.dumps({'1001':dict(ok=True,input_sha256=sha(self.c/self.m['tex_path']),passes=2,pdf=str(pdf.relative_to(self.c)),pdf_sha256=sha(pdf),dependency_sha256={p:sha(self.c/p) for p in ['raw/s.tex','raw/license.txt']})}))
 def tearDown(self):self.tmp.cleanup()
 def save(self):(self.c/'metadata/1001.json').write_text(json.dumps(self.m))
 def run_validation(self,*args):
  r=subprocess.run([sys.executable,str(ROOT/'scripts/validate_corpus.py'),'--mode','historical-evidence','--root',str(self.root),*args],capture_output=True,text=True)
  report=self.c/'.work/validation_report.json';return r, json.loads(report.read_text()) if report.exists() else {}
 def test_four_digit_noncontiguous_item_qualifies(self):
  r,j=self.run_validation('--item','1001');self.assertEqual(r.returncode,0,r.stderr+r.stdout);self.assertEqual(j['qualified_count'],1)
 def test_conflicting_explicit_version_doi_is_fatal(self):
  self.m['source_locator']['doi']='10.30757/ALEA.v22-29';self.m['source_version']='ALEA article22-17; DOI 10.30757/ALEA.v22-17';self.save()
  r,j=self.run_validation();self.assertNotEqual(r.returncode,0);self.assertIn('source_version DOI conflicts',str(j))
 def test_matching_explicit_version_doi_qualifies(self):
  self.m['source_locator']['doi']='10.30757/ALEA.v22-29';self.m['source_version']='ALEA article22-29; DOI 10.30757/alea.v22-29.';self.save()
  r,j=self.run_validation();self.assertEqual(r.returncode,0,r.stdout+r.stderr)
 def test_version_without_explicit_doi_qualifies(self):
  self.m['source_locator']['doi']='10.30757/ALEA.v22-29';self.save()
  r,j=self.run_validation();self.assertEqual(r.returncode,0,r.stdout+r.stderr)
 def test_alea_pdf_url_conflicting_directory_and_filename_is_fatal(self):
  self.m['source_url']='https://alea.impa.br/articles/v19/18-43.pdf';self.save()
  (self.c/'INDEX.md').write_text('| 1001 | Example | H2 | Human | '+self.m['source_url']+' |\n')
  r,j=self.run_validation();self.assertNotEqual(r.returncode,0);self.assertIn('ALEA PDF URL volume conflicts',str(j))
 def test_alea_pdf_url_matching_volumes_qualifies(self):
  self.m['source_url']='https://alea.impa.br/articles/v18/18-43.pdf';self.save()
  (self.c/'INDEX.md').write_text('| 1001 | Example | H2 | Human | '+self.m['source_url']+' |\n')
  r,j=self.run_validation();self.assertEqual(r.returncode,0,r.stdout+r.stderr)
 def test_non_alea_url_with_similar_path_is_unaffected(self):
  self.m['source_url']='https://example.org/articles/v19/18-43.pdf';self.save()
  (self.c/'INDEX.md').write_text('| 1001 | Example | H2 | Human | '+self.m['source_url']+' |\n')
  r,j=self.run_validation();self.assertEqual(r.returncode,0,r.stdout+r.stderr)
 def test_active_admission_hold_is_fatal(self):
  self.m['admission_hold']='Source locator awaiting correction';self.save()
  r,j=self.run_validation();self.assertNotEqual(r.returncode,0);self.assertEqual(j['qualified_count'],0);self.assertIn('admission_hold',str(j))
 def test_missing_compile_is_fatal(self):
  (self.c/'.work/compile_report.json').unlink();r,j=self.run_validation();self.assertNotEqual(r.returncode,0);self.assertIn('compile',str(j))
 def test_stale_tex_is_fatal(self):
  with (self.c/self.m['tex_path']).open('a') as f:f.write('\nchanged')
  r,j=self.run_validation();self.assertNotEqual(r.returncode,0);self.assertIn('hash',str(j))
 def test_raw_hash_mismatch_is_fatal(self):
  (self.c/'raw/s.tex').write_text('changed');r,j=self.run_validation();self.assertNotEqual(r.returncode,0);self.assertIn('source',str(j))
 def test_unreviewed_is_fatal(self):
  self.m['proof_review']['reviewed']=False;self.save();r,j=self.run_validation();self.assertNotEqual(r.returncode,0);self.assertIn('review',str(j))
 def test_quarantine_is_not_qualified(self):
  (self.c/'INDEX.md').write_text('')
  (self.c/'item_status.json').write_text(json.dumps({'schema_version':1,'items':{'1001':{'status':'quarantined','reason':'unverified'}}}));r,j=self.run_validation();self.assertEqual(r.returncode,0);self.assertEqual(j['qualified_count'],0)
 def test_missing_manifest_fails_closed(self):
  (self.c/'item_status.json').unlink();r,j=self.run_validation();self.assertNotEqual(r.returncode,0);self.assertEqual(j.get('qualified_count'),0)
 def test_duplicate_index_is_fatal(self):
  with (self.c/'INDEX.md').open('a') as f:f.write('| 1001 | Example | H2 | Human | https://example.org/s |\n')
  r,j=self.run_validation();self.assertNotEqual(r.returncode,0);self.assertIn('INDEX',str(j))
 def test_pdf_mode_without_proof_environment(self):
  from pypdf import PdfWriter
  writer=PdfWriter();writer.add_blank_page(width=100,height=100)
  with (self.c/'raw/s.pdf').open('wb') as f:writer.write(f)
  with (self.c/self.m['tex_path']).open('a') as f:f.write('\\includepdf[pages={1}]{../raw/s.pdf}')
  self.m.update(evidence_mode='source_pdf_pages',source_path='raw/s.pdf',source_sha256=sha(self.c/'raw/s.pdf'),statement_pages=[1],proof_pages=[1]);self.save()
  rep=json.loads((self.c/'.work/compile_report.json').read_text());rep['1001']['input_sha256']=sha(self.c/self.m['tex_path']);rep['1001']['dependency_sha256'].pop('raw/s.tex');rep['1001']['dependency_sha256']['raw/s.pdf']=sha(self.c/'raw/s.pdf');(self.c/'.work/compile_report.json').write_text(json.dumps(rep))
  r,j=self.run_validation();self.assertEqual(r.returncode,0,r.stdout+r.stderr)
 def test_unmanifested_tex_fails(self):
  (self.c/'tex/1002_extra.tex').write_text('x');r,j=self.run_validation();self.assertNotEqual(r.returncode,0);self.assertIn('manifest',str(j))
 def test_compiler_missing_engine_fails(self):
  r=subprocess.run([sys.executable,str(ROOT/'scripts/compile_all.py'),'--root',str(self.root),'--item','1001','--engine','nonexistent-engine'],capture_output=True,text=True);self.assertNotEqual(r.returncode,0)
  receipt=json.loads((self.c/'.work/compile_report.json').read_text());self.assertFalse(receipt['1001']['ok'])
 def test_transitive_macro_change_is_fatal(self):
  (self.c/'tex/macro.tex').write_text('macro')
  with (self.c/self.m['tex_path']).open('a') as f:f.write('\\input{macro.tex}')
  rep=json.loads((self.c/'.work/compile_report.json').read_text());rep['1001']['input_sha256']=sha(self.c/self.m['tex_path']);rep['1001']['dependency_sha256']['tex/macro.tex']=sha(self.c/'tex/macro.tex');(self.c/'.work/compile_report.json').write_text(json.dumps(rep))
  (self.c/'tex/macro.tex').write_text('changed')
  r,j=self.run_validation();self.assertNotEqual(r.returncode,0);self.assertIn('dependency hash',str(j))
 def test_failed_receipt_cannot_use_old_pdf(self):
  rep=json.loads((self.c/'.work/compile_report.json').read_text());rep['1001']['ok']=False;(self.c/'.work/compile_report.json').write_text(json.dumps(rep))
  r,j=self.run_validation();self.assertNotEqual(r.returncode,0);self.assertIn('compile',str(j))
 def test_compiler_explicit_quarantine_item(self):
  (self.c/'item_status.json').write_text(json.dumps({'schema_version':1,'items':{'1001':{'status':'quarantined','metadata':'metadata/1001.json'}}}))
  r=subprocess.run([sys.executable,str(ROOT/'scripts/compile_all.py'),'--root',str(self.root),'--item','1001','--engine','nonexistent-engine'],capture_output=True,text=True)
  self.assertIn('engine missing',r.stdout);self.assertNotEqual(r.returncode,0)
 def test_context_excerpt_must_match_original_lines(self):
  (self.c/'raw/context.tex').write_text('original context\n')
  (self.c/'raw/context-excerpt.tex').write_text('substituted context\n')
  self.m['extra_source_paths']=['raw/context.tex']
  self.m['contexts']=[dict(file='context.tex',tag='ZZZZ',source_sha256=sha(self.c/'raw/context.tex'),start_line=1,end_line=1,excerpt_path='raw/context-excerpt.tex',excerpt_sha256=sha(self.c/'raw/context-excerpt.tex'))];self.save()
  rep=json.loads((self.c/'.work/compile_report.json').read_text());rep['1001']['dependency_sha256']['raw/context.tex']=sha(self.c/'raw/context.tex');(self.c/'.work/compile_report.json').write_text(json.dumps(rep))
  r,j=self.run_validation();self.assertNotEqual(r.returncode,0);self.assertIn('context excerpt',str(j))
 def test_context_source_hash_must_match(self):
  (self.c/'raw/context.tex').write_text('original context\n');(self.c/'raw/context-excerpt.tex').write_text('original context\n')
  self.m['extra_source_paths']=['raw/context.tex'];self.m['contexts']=[dict(file='context.tex',tag='ZZZZ',source_sha256='bad',start_line=1,end_line=1,excerpt_path='raw/context-excerpt.tex',excerpt_sha256=sha(self.c/'raw/context-excerpt.tex'))];self.save()
  r,j=self.run_validation();self.assertNotEqual(r.returncode,0);self.assertIn('context source hash',str(j))
 def test_cache_detects_same_size_source_mutation_between_calls(self):
  import importlib.util,os
  spec=importlib.util.spec_from_file_location('cache_validator',ROOT/'scripts/validate_corpus.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
  first=v.validate(self.root);self.assertEqual(first['qualified_count'],1)
  source=self.c/'raw/s.tex';stat=source.stat();data=source.read_text();source.write_text(data.replace('A','Z',1));os.utime(source,ns=(stat.st_atime_ns,stat.st_mtime_ns))
  second=v.validate(self.root);self.assertEqual(second['qualified_count'],0);self.assertIn('source hash',str(second))
 def test_cache_reads_shared_source_once_per_validation(self):
  import importlib.util
  spec=importlib.util.spec_from_file_location('cache_validator',ROOT/'scripts/validate_corpus.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
  # A provenance source is touched by sha and line checks in one validation.
  original=Path.read_bytes;reads=[]
  from unittest.mock import patch
  def read(path):
   if path.resolve()==(self.c/'raw/s.tex').resolve():reads.append(path)
   return original(path)
  with patch.object(Path,'read_bytes',read):v.validate(self.root)
  self.assertEqual(len(reads),1)

 def pdf_context_fixture(self,context,covered='1'):
  from pypdf import PdfWriter
  writer=PdfWriter()
  for _ in range(2):writer.add_blank_page(width=100,height=100)
  with (self.c/'raw/s.pdf').open('wb') as f:writer.write(f)
  tex=self.c/self.m['tex_path'];tex.write_text('\\documentclass{article}\\begin{document}\\includepdf[pages={'+covered+'}]{../raw/s.pdf}\\end{document}')
  self.m.update(evidence_mode='source_pdf_pages',source_path='raw/s.pdf',statement_pages=[1],proof_pages=[1])
  self.m['source_sha256']=sha(self.c/'raw/s.pdf');self.m['context_pages']=context;self.save()
  rep=json.loads((self.c/'.work/compile_report.json').read_text());rep['1001']['input_sha256']=sha(tex);rep['1001']['dependency_sha256'].pop('raw/s.tex',None);rep['1001']['dependency_sha256']['raw/s.pdf']=sha(self.c/'raw/s.pdf');(self.c/'.work/compile_report.json').write_text(json.dumps(rep))
 def test_declared_pdf_context_only_page_must_be_covered(self):
  self.pdf_context_fixture([2]);r,j=self.run_validation();self.assertNotEqual(r.returncode,0);self.assertIn('required source pages',str(j))
 def test_declared_pdf_context_page_covered_passes(self):
  self.pdf_context_fixture([2],'1,2');r,j=self.run_validation();self.assertEqual(r.returncode,0,r.stdout+r.stderr)
 def test_empty_pdf_context_pages_passes(self):
  self.pdf_context_fixture([]);r,j=self.run_validation();self.assertEqual(r.returncode,0,r.stdout+r.stderr)
 def test_pdf_context_page_bounds_fail(self):
  self.pdf_context_fixture([3],'1-3');r,j=self.run_validation();self.assertNotEqual(r.returncode,0);self.assertIn('out of bounds',str(j))
 def test_pdf_context_page_types_fail(self):
  for context in [None,'2',[True],[0],[-1],['2']]:
   with self.subTest(context=context):
    self.pdf_context_fixture(context,'1,2');r,j=self.run_validation();self.assertNotEqual(r.returncode,0);self.assertIn('context_pages invalid',str(j))

if __name__=='__main__':unittest.main()
