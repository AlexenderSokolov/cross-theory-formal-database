import gzip,hashlib,json,sqlite3,tempfile,unittest
from pathlib import Path
from restore_database import restore

sha=lambda b:hashlib.sha256(b).hexdigest()
class RestoreDatabaseTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
  text='Complete editable statement and human proof.\n';(self.root/'items').mkdir();(self.root/'items/001.tex').write_text(text)
  item={'problem_id':'001','item_path':'items/001.tex','status':'verified_editable_tex','tex_sha256':sha(text.encode()),'source_id':'source1'}
  self.manifest={'items':[item]}; self.write_manifest()
  original=self.root/'fixture.sqlite';db=sqlite3.connect(original);db.executescript('PRAGMA foreign_keys=ON; CREATE TABLE sources(source_id TEXT PRIMARY KEY); CREATE TABLE problems(problem_id TEXT PRIMARY KEY,status TEXT,tex_content TEXT,tex_sha256 TEXT,source_id TEXT REFERENCES sources(source_id));')
  db.execute('INSERT INTO sources VALUES (?)',('source1',));db.execute('INSERT INTO problems VALUES (?,?,?,?,?)',('001','verified_editable_tex',text,item['tex_sha256'],'source1'));db.commit();db.close()
  self.sqlite=original.read_bytes();original.unlink();self.pack(self.sqlite)
 def write_manifest(self):
  (self.root/'manifest.json').write_text(json.dumps(self.manifest))
 def pack(self,raw):
  z=gzip.compress(raw,mtime=0); (self.root/'corpus.sqlite.gz').write_bytes(z)
  self.delivery={'schema_version':1,'format':'gzip-compressed SQLite','gzip_sha256':sha(z),'sqlite_sha256':sha(raw),'gzip_bytes':len(z),'sqlite_bytes':len(raw),'problem_count':1,'manifest_sha256':sha((self.root/'manifest.json').read_bytes())}
  (self.root/'database-delivery.json').write_text(json.dumps(self.delivery))
 def test_exact_roundtrip_creates_valid_fulltext_database(self):
  path=restore(self.root);self.assertTrue(path.is_file(),'restore must create SQLite');self.assertEqual(path.read_bytes(),self.sqlite)
  db=sqlite3.connect(path);self.assertEqual(db.execute('select tex_content from problems').fetchone()[0],(self.root/'items/001.tex').read_text());db.close()
 def test_corrupt_compressed_input_refuses_creation(self):
  p=self.root/'corpus.sqlite.gz';p.write_bytes(p.read_bytes()[:-4]+b'bad!')
  with self.assertRaisesRegex(ValueError,'compressed'):restore(self.root)
  self.assertFalse((self.root/'corpus.sqlite').exists())
 def test_differing_existing_database_is_never_overwritten(self):
  p=self.root/'corpus.sqlite';p.write_bytes(b'existing user file')
  with self.assertRaises(FileExistsError):restore(self.root)
  self.assertEqual(p.read_bytes(),b'existing user file')
 def test_identical_existing_database_is_idempotent(self):
  p=self.root/'corpus.sqlite';p.write_bytes(self.sqlite);before=p.stat().st_mtime_ns
  self.assertEqual(restore(self.root),p);self.assertEqual(p.stat().st_mtime_ns,before)
 def test_wrong_decompressed_digest_refuses_creation(self):
  self.delivery['sqlite_sha256']='0'*64;(self.root/'database-delivery.json').write_text(json.dumps(self.delivery))
  with self.assertRaisesRegex(ValueError,'decompressed'):restore(self.root)
  self.assertFalse((self.root/'corpus.sqlite').exists())
 def test_current_manifest_and_tex_are_checked(self):
  (self.root/'items/001.tex').write_text('omitted proof')
  with self.assertRaisesRegex(ValueError,'full.text'):restore(self.root)
  self.assertFalse((self.root/'corpus.sqlite').exists())
 def test_invalid_sqlite_integrity_refuses_creation(self):
  self.pack(b'not SQLite')
  with self.assertRaises((ValueError,sqlite3.DatabaseError)):restore(self.root)
  self.assertFalse((self.root/'corpus.sqlite').exists())
if __name__=='__main__':unittest.main()
