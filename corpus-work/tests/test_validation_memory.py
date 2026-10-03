import concurrent.futures, hashlib, importlib.util, os, unittest
from pathlib import Path
from unittest.mock import patch
import test_pipeline as fixtures

ROOT=fixtures.ROOT


def retained_binary_bytes(value):
 if isinstance(value,(bytes,bytearray,memoryview)):return len(value)
 if isinstance(value,dict):return sum(retained_binary_bytes(k)+retained_binary_bytes(v) for k,v in value.items())
 if isinstance(value,(tuple,list,set)):return sum(map(retained_binary_bytes,value))
 return 0


class ValidationMemory(unittest.TestCase):
 save=fixtures.Pipeline.save
 tearDown=fixtures.Pipeline.tearDown
 pdf_context_fixture=fixtures.Pipeline.pdf_context_fixture
 def setUp(self):
  fixtures.Pipeline.setUp(self)
  spec=importlib.util.spec_from_file_location('bounded_validator',ROOT/'scripts/validate_corpus.py')
  self.v=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.v)
 def rewrite_restoring_mtime(self,path,data):
  stat=path.stat();path.write_bytes(data);os.utime(path,ns=(stat.st_atime_ns,stat.st_mtime_ns))
 def test_binary_hash_cache_retains_only_small_signatures(self):
  paths=[]
  for i in range(16):
   p=self.c/'raw'/f'{i}.pdf';p.write_bytes(b'%PDF-'+bytes([i])*1024*1024);paths.append(p)
  with self.v.validation_session():
   for p in paths:self.assertEqual(self.v.sha(p),hashlib.sha256(p.read_bytes()).hexdigest())
   cache=self.v._validation_cache.get()
   self.assertLessEqual(retained_binary_bytes(cache),len(paths)*5)
   for p in paths:self.assertTrue(self.v.pdf_signature(p))
 def test_rewritten_paths_discard_old_versions_and_detect_restored_mtime(self):
  p=self.c/'raw/rewrite.pdf';p.write_bytes(b'%PDF-'+b'a'*1024*1024)
  with self.v.validation_session():
   prior=self.v.sha(p)
   for i in range(12):
    self.rewrite_restoring_mtime(p,b'%PDF-'+bytes([65+i])*1024*1024)
    current=self.v.sha(p);self.assertNotEqual(current,prior);prior=current
   self.assertEqual(len(self.v._validation_cache.get()),1)
   self.assertLessEqual(retained_binary_bytes(self.v._validation_cache.get()),5)
 def test_pdf_page_count_reused_without_retaining_pdf_bytes(self):
  from pypdf import PdfReader, PdfWriter
  p=self.c/'raw/pages.pdf';w=PdfWriter()
  for _ in range(3):w.add_blank_page(width=100,height=100)
  with p.open('wb') as stream:w.write(stream)
  parsed=[]
  def reader(*args,**kwargs):parsed.append(1);return PdfReader(*args,**kwargs)
  with self.v.validation_session(),patch('pypdf.PdfReader',side_effect=reader):
   for _ in range(10):
    self.assertEqual(self.v.sha(p),hashlib.sha256(p.read_bytes()).hexdigest())
    self.assertEqual(self.v.pdf_page_count(p),3)
   self.assertEqual(len(parsed),1)
   self.assertLessEqual(retained_binary_bytes(self.v._validation_cache.get()),5)
 def test_pdf_parse_race_raises_and_never_caches_stale_page_count(self):
  from pypdf import PdfReader,PdfWriter
  p=self.c/'raw/pages.pdf';w=PdfWriter();w.add_blank_page(width=100,height=100)
  with p.open('wb') as stream:w.write(stream)
  before=p.read_bytes()
  def raced_reader(*args,**kwargs):
   reader=PdfReader(*args,**kwargs)
   self.rewrite_restoring_mtime(p,before.replace(b'%PDF-1.3',b'%PDF-1.4',1))
   return reader
  with self.v.validation_session():
   self.v.sha(p)
   with patch('pypdf.PdfReader',side_effect=raced_reader):
    with self.assertRaisesRegex(OSError,'file changed while reading'):self.v.pdf_page_count(p)
   self.assertEqual(self.v.sha(p),hashlib.sha256(p.read_bytes()).hexdigest());self.assertEqual(self.v.pdf_page_count(p),1)
 def test_streaming_hash_race_raises_and_does_not_publish_stale_digest(self):
  p=self.c/'raw/race.pdf';before=b'%PDF-'+b'a'*2*1024*1024;p.write_bytes(before)
  original=Path.open;fired=[]
  class Reader:
   def __init__(reader,stream):reader.stream=stream
   def __enter__(reader):return reader
   def __exit__(reader,*args):reader.stream.close()
   def __getattr__(reader,name):return getattr(reader.stream,name)
   def read(reader,*args):
    data=reader.stream.read(*args)
    if not fired:
     fired.append(True);self.rewrite_restoring_mtime(p,before.replace(b'a',b'z',1))
    return data
  def opened(path,*args,**kwargs):
   stream=original(path,*args,**kwargs)
   return Reader(stream) if path.resolve()==p.resolve() and (args[0] if args else kwargs.get('mode'))=='rb' else stream
  with self.v.validation_session():
   with patch.object(Path,'open',opened):
    with self.assertRaisesRegex(OSError,'file changed while reading'):self.v.sha(p)
   self.assertEqual(self.v.sha(p),hashlib.sha256(p.read_bytes()).hexdigest())
 def test_source_pdf_same_size_restored_mtime_mutation_fails_gate(self):
  self.pdf_context_fixture([2],'1,2');p=self.c/'raw/s.pdf'
  with self.v.validation_session():
   self.assertEqual(self.v.validate_in_session(self.root)['qualified_count'],1)
   self.rewrite_restoring_mtime(p,p.read_bytes().replace(b'%PDF-',b'%PDA-',1));report=self.v.validate_in_session(self.root)
   self.assertEqual(report['qualified_count'],0);self.assertIn('source hash mismatch',str(report));self.assertIn('source PDF signature missing',str(report))
 def test_compiled_pdf_same_size_restored_mtime_mutation_fails_gate(self):
  p=self.c/'.work/build/1001/test.pdf'
  with self.v.validation_session():
   self.assertEqual(self.v.validate_in_session(self.root)['qualified_count'],1)
   self.rewrite_restoring_mtime(p,p.read_bytes().replace(b'%PDF-',b'%PDA-',1));report=self.v.validate_in_session(self.root)
   self.assertEqual(report['qualified_count'],0);self.assertIn('compile PDF hash/signature mismatch',str(report))
 def test_thread_scopes_are_independent_and_outer_session_is_restored(self):
  def worker(_):
   self.assertIsNone(self.v._validation_cache.get())
   with self.v.validation_session():
    result=self.v.validate_in_session(self.root);self.assertEqual(result['qualified_count'],1);cache=self.v._validation_cache.get()
   self.assertIsNone(self.v._validation_cache.get());return cache
  with self.v.validation_session():
   outer=self.v._validation_cache.get();self.v.validate_in_session(self.root)
   with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:states=list(pool.map(worker,range(2)))
   self.assertIs(self.v._validation_cache.get(),outer);self.assertTrue(all(cache is not outer for cache in states));self.assertIsNot(states[0],states[1])
  self.assertIsNone(self.v._validation_cache.get())
