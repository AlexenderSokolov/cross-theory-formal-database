import gzip,json,random,sqlite3,unittest
from pathlib import Path
import test_restore_database as fixtures
from test_restore_database import sha
from restore_database import restore

CHUNK_BYTES=4*1024*1024
class ChunkRestoreDatabaseTests(unittest.TestCase):
 write_manifest=fixtures.RestoreDatabaseTests.write_manifest
 pack=fixtures.RestoreDatabaseTests.pack
 def setUp(self):
  fixtures.RestoreDatabaseTests.setUp(self)
  p=self.root/'fixture.sqlite';p.write_bytes(self.sqlite)
  with sqlite3.connect(p) as db:
   db.execute('CREATE TABLE fixture_padding(data BLOB)')
   db.execute('INSERT INTO fixture_padding VALUES (?)',(random.Random(684).randbytes(2*CHUNK_BYTES+1234),))
  self.sqlite=p.read_bytes();p.unlink();self.pack(self.sqlite)
  self.compressed=(self.root/'corpus.sqlite.gz').read_bytes();self.parts=[]
  (self.root/'database-parts').mkdir()
  for index,start in enumerate(range(0,len(self.compressed),CHUNK_BYTES)):
   b=self.compressed[start:start+CHUNK_BYTES];name=f'database-parts/corpus.sqlite.gz.part-{index:05d}';(self.root/name).write_bytes(b)
   self.parts.append({'index':index,'path':name,'bytes':len(b),'sha256':sha(b)})
  self.delivery.update(schema_version=2,format='ordered gzip-compressed SQLite parts',chunk_bytes=CHUNK_BYTES,part_count=len(self.parts),parts=self.parts)
  self.write_delivery()
 def write_delivery(self):
  (self.root/'database-delivery.json').write_text(json.dumps(self.delivery))
 def expect_rejection(self,pattern):
  with self.assertRaisesRegex((ValueError,FileNotFoundError),pattern):restore(self.root)
  self.assertFalse((self.root/'corpus.sqlite').exists())
 def test_exact_chunk_roundtrip_ignores_stale_single_gzip(self):
  (self.root/'corpus.sqlite.gz').write_bytes(b'legacy stale bytes must not be used')
  try:path=restore(self.root)
  except Exception as exc:self.fail('v2 chunk roundtrip unsupported: '+str(exc))
  self.assertEqual(path.read_bytes(),self.sqlite)
 def test_missing_part_rejected_even_if_single_gzip_exists(self):
  (self.root/self.parts[1]['path']).unlink();self.expect_rejection('part|No such file')
 def test_tampered_part_rejected(self):
  p=self.root/self.parts[1]['path'];b=p.read_bytes();p.write_bytes(b[:-1]+bytes([b[-1]^1]));self.expect_rejection('part')
 def test_reordered_parts_rejected(self):
  self.delivery['parts']=self.parts[::-1];self.write_delivery();self.expect_rejection('indices|order')
 def test_duplicate_indices_rejected(self):
  self.parts[1]['index']=self.parts[0]['index'];self.write_delivery();self.expect_rejection('indices|order')
 def test_noncontiguous_indices_rejected(self):
  self.parts[1]['index']=7;self.write_delivery();self.expect_rejection('indices|order')
 def test_duplicate_resolved_paths_rejected(self):
  self.parts[1]['path']=self.parts[0]['path'];self.write_delivery();self.expect_rejection('duplicate|path')
 def test_empty_parts_rejected(self):
  self.delivery['parts']=[];self.write_delivery();self.expect_rejection('empty|count')
 def test_declared_part_count_mismatch_rejected(self):
  self.delivery['part_count']+=1;self.write_delivery();self.expect_rejection('count')
 def test_declared_summed_size_mismatch_rejected(self):
  self.delivery['gzip_bytes']+=1;self.write_delivery();self.expect_rejection('size|sum')
 def test_nonfinal_fixed_chunk_size_rejected(self):
  self.parts[0]['bytes']-=1;self.write_delivery();self.expect_rejection('chunk|size')
 def test_empty_final_chunk_rejected(self):
  self.parts[-1]['bytes']=0;self.write_delivery();self.expect_rejection('chunk|size')
 def test_unsupported_chunk_size_rejected(self):
  self.delivery['chunk_bytes']-=1;self.write_delivery();self.expect_rejection('chunk|size')
 def test_unsupported_schema_version_rejected(self):
  self.delivery['schema_version']=99;self.write_delivery();self.expect_rejection('version')
 def test_wrong_full_compressed_digest_rejected(self):
  self.delivery['gzip_sha256']='0'*64;self.write_delivery();self.expect_rejection('compressed')
 def test_external_path_rejected(self):
  self.parts[0]['path']='../external.part';self.write_delivery();self.expect_rejection('path')
 def test_absolute_path_rejected(self):
  self.parts[0]['path']=str((self.root/self.parts[0]['path']).resolve());self.write_delivery();self.expect_rejection('path')
 def test_symlink_escape_rejected(self):
  target=self.root.parent/(self.root.name+'-external.part');target.write_bytes((self.root/self.parts[0]['path']).read_bytes());self.addCleanup(lambda:target.unlink(missing_ok=True));link=self.root/'database-parts/escape';link.symlink_to(target)
  self.parts[0]['path']='database-parts/escape';self.write_delivery();self.expect_rejection('path')
 def test_chunk_differing_existing_database_unchanged(self):
  (self.root/'corpus.sqlite').write_bytes(b'preserve existing user file')
  with self.assertRaises(FileExistsError):restore(self.root)
  self.assertEqual((self.root/'corpus.sqlite').read_bytes(),b'preserve existing user file')
 def test_chunk_identical_existing_database_idempotent(self):
  p=self.root/'corpus.sqlite';p.write_bytes(self.sqlite);before=p.stat().st_mtime_ns;self.assertEqual(restore(self.root),p);self.assertEqual(p.stat().st_mtime_ns,before)

if __name__=='__main__':unittest.main()
