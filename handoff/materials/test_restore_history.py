import hashlib,json,stat,tempfile,unittest,zipfile
from pathlib import Path
from restore_history import restore
from unittest.mock import patch
h=lambda b:hashlib.sha256(b).hexdigest()
class RestoreHistoryTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name);self.dest=self.root/'destination';self.dest.mkdir();self.archive=self.root/'blobs.zip';self.manifest=self.root/'manifest.json';self.data=b'Preserved editable human proof\n';self.sha=h(self.data)
  self.members=[('blobs/'+self.sha,self.data,stat.S_IFREG|0o644)];self.entries=[{'path':'project/001.tex','sha256':self.sha,'bytes':len(self.data),'mode':0o644},{'path':'historical/001.tex','sha256':self.sha,'bytes':len(self.data),'mode':0o755}];self.write_archive();self.write_manifest()
 def write_archive(self):
  with zipfile.ZipFile(self.archive,'w',compression=zipfile.ZIP_DEFLATED) as z:
   for name,b,mode in self.members:
    i=zipfile.ZipInfo(name);i.external_attr=mode<<16;z.writestr(i,b)
 def write_manifest(self):
  self.record={'schema_version':1,'format':'sha256-content-addressed-zip','archive_name':'blobs.zip','archive_sha256':h(self.archive.read_bytes()),'archive_bytes':self.archive.stat().st_size,'files':self.entries}
  self.manifest.write_text(json.dumps(self.record));self.expected=h(self.manifest.read_bytes())
 def modify(self,change):
  change();self.write_manifest()
 def reject(self,pattern):
  with self.assertRaisesRegex((ValueError,FileExistsError),pattern):restore(self.manifest,self.dest,expected_manifest_sha256=self.expected)
 def test_shared_blob_roundtrip_preserves_paths_and_modes(self):
  result=restore(self.manifest,self.dest,expected_manifest_sha256=self.expected);self.assertEqual(result,2)
  for e in self.entries:
   p=self.dest/e['path'];self.assertEqual(p.read_bytes(),self.data);self.assertEqual(stat.S_IMODE(p.stat().st_mode),e['mode'])
 def test_existing_identical_file_is_idempotent(self):
  p=self.dest/'project/001.tex';p.parent.mkdir();p.write_bytes(self.data);p.chmod(0o644);before=p.stat().st_mtime_ns;restore(self.manifest,self.dest,expected_manifest_sha256=self.expected);self.assertEqual(p.stat().st_mtime_ns,before)
 def test_existing_different_file_is_never_overwritten(self):
  p=self.dest/'project/001.tex';p.parent.mkdir();p.write_bytes(b'existing user data');self.reject('existing|overwrite');self.assertEqual(p.read_bytes(),b'existing user data')
 def test_duplicate_manifest_paths_rejected(self):
  self.entries[1]['path']=self.entries[0]['path'];self.write_manifest();self.reject('duplicate')
 def test_duplicate_archive_members_rejected(self):
  self.members.append(self.members[0]);self.write_archive();self.write_manifest();self.reject('duplicate')
 def test_unsupported_version_rejected(self):
  self.record['schema_version']=2;self.manifest.write_text(json.dumps(self.record));self.expected=h(self.manifest.read_bytes());self.reject('version')
 def test_malformed_size_rejected(self):
  self.entries[0]['bytes']=-1;self.write_manifest();self.reject('size')
 def test_malformed_hash_rejected(self):
  self.entries[0]['sha256']='not a hash';self.write_manifest();self.reject('hash')
 def test_malformed_mode_rejected(self):
  self.entries[0]['mode']='644';self.write_manifest();self.reject('mode')
 def test_special_setuid_mode_rejected(self):
  self.entries[0]['mode']=0o4644;self.write_manifest();self.reject('mode')
 def test_absolute_path_rejected(self):
  self.entries[0]['path']='/tmp/escape';self.write_manifest();self.reject('path')
 def test_parent_traversal_path_rejected(self):
  self.entries[0]['path']='../escape';self.write_manifest();self.reject('path')
 def test_symlink_escape_rejected(self):
  other=self.root/'outside';other.mkdir();(self.dest/'project').symlink_to(other,target_is_directory=True);self.reject('symlink|path')
 def test_missing_blob_rejected(self):
  self.members=[];self.write_archive();self.write_manifest();self.reject('blob|member')
 def test_tampered_blob_rejected(self):
  self.members[0]=('blobs/'+self.sha,b'tampered',stat.S_IFREG|0o644);self.write_archive();self.write_manifest();self.reject('blob|digest|size')
 def test_nonregular_archive_member_rejected(self):
  self.members[0]=('blobs/'+self.sha,self.data,stat.S_IFLNK|0o777);self.write_archive();self.write_manifest();self.reject('regular|mode')
 def test_archive_digest_mismatch_rejected(self):
  self.archive.write_bytes(self.archive.read_bytes()+b'changed');self.reject('archive')
 def test_selected_path_restores_only_requested_file(self):
  self.assertEqual(restore(self.manifest,self.dest,'project/001.tex',expected_manifest_sha256=self.expected),1);self.assertTrue((self.dest/'project/001.tex').exists());self.assertFalse((self.dest/'historical/001.tex').exists())
 def test_valid_manifest_path_mutation_rejected_by_original_expected_digest(self):
  original=self.expected;self.entries[0]['path']='different/place.tex';self.write_manifest()
  with self.assertRaisesRegex(ValueError,'manifest.*digest'):restore(self.manifest,self.dest,expected_manifest_sha256=original)
  self.assertFalse((self.dest/'different/place.tex').exists())
 def test_wrong_expected_manifest_digest_rejected(self):
  with self.assertRaisesRegex(ValueError,'manifest.*digest'):restore(self.manifest,self.dest,expected_manifest_sha256='0'*64)
 def test_missing_expected_manifest_digest_rejected(self):
  with self.assertRaisesRegex(ValueError,'expected.*manifest'):restore(self.manifest,self.dest)

 def test_manifest_replacement_between_reads_cannot_change_restore_path(self):
  original_open=Path.open;manifest=self.manifest;count=0;changed=dict(self.record,files=[dict(self.entries[0],path='changed/place.tex'),self.entries[1]])
  def raced_open(path,*args,**kwargs):
   nonlocal count
   if path.resolve()==manifest.resolve() and (not args or 'r' in args[0]):
    count+=1
    if count==2:
     with original_open(manifest,'w') as f:f.write(json.dumps(changed))
   return original_open(path,*args,**kwargs)
  with patch.object(Path,'open',raced_open):restore(self.manifest,self.dest,expected_manifest_sha256=self.expected)
  self.assertTrue((self.dest/'project/001.tex').exists())
  self.assertFalse((self.dest/'changed/place.tex').exists())

if __name__=='__main__':unittest.main()
