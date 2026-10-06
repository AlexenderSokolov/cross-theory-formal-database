"""Offline ordered-part reconstruction and the unchanged fail-closed CAS restore kit."""
from pathlib import Path
import argparse,hashlib,json,os,stat,tempfile
from restore_history import restore,load_bundle,file_digest,unique_json,relative_path

def load_transport(path,expected):
 p=Path(path).resolve();raw=p.read_bytes()
 if hashlib.sha256(raw).hexdigest()!=expected:raise ValueError('transport manifest digest mismatch')
 m=json.loads(raw,object_pairs_hook=unique_json)
 if m.get('schema_version')!=1 or m.get('format')!='ordered-binary-parts':raise ValueError('unsupported transport format')
 if not isinstance(m.get('parts'),list) or not m['parts']:raise ValueError('missing parts')
 seen=set();whole=hashlib.sha256();total=0
 for seq,r in enumerate(m['parts'],1):
  name=relative_path(r['name'])
  if len(name.parts)!=1 or str(name) in seen or r.get('sequence')!=seq:raise ValueError('invalid part name or order')
  seen.add(str(name));q=p.parent/name
  if q.is_symlink() or not q.is_file() or q.stat().st_size!=r['bytes'] or file_digest(q)!=r['sha256']:raise ValueError('part size or digest mismatch')
  with q.open('rb') as f:
   for b in iter(lambda:f.read(1048576),b''):whole.update(b);total+=len(b)
 if total!=m['archive_bytes'] or whole.hexdigest()!=m['archive_sha256']:raise ValueError('whole archive binding mismatch')
 return m,p.parent

def reassemble(path,expected):
 m,d=load_transport(path,expected);name=relative_path(m['archive_name'])
 if len(name.parts)!=1:raise ValueError('archive path must be a sibling basename')
 dest=d/name
 if dest.is_symlink():raise ValueError('symlink archive forbidden')
 if dest.exists():
  if dest.is_file() and dest.stat().st_size==m['archive_bytes'] and file_digest(dest)==m['archive_sha256']:return dest,m
  raise FileExistsError('refusing to replace differing reconstructed archive')
 fd,tmp=tempfile.mkstemp(prefix='.pending-cas-',dir=d);t=Path(tmp)
 try:
  with os.fdopen(fd,'wb') as out:
   for r in m['parts']:
    with (d/r['name']).open('rb') as f:
     for b in iter(lambda:f.read(1048576),b''):out.write(b)
   out.flush();os.fsync(out.fileno())
  if t.stat().st_size!=m['archive_bytes'] or file_digest(t)!=m['archive_sha256']:raise ValueError('reconstructed archive mismatch')
  t.chmod(0o444);os.link(t,dest)
 finally:t.unlink(missing_ok=True)
 return dest,m

def run(transport,expected,destination,verify_only=False):
 archive,m=reassemble(transport,expected);manifest=archive.parent/m['cas_manifest_name'];load_bundle(manifest,m['cas_manifest_sha256'])
 if verify_only:return {'all_part_and_CAS_blobs_verified':True,'files':len(json.loads(manifest.read_bytes())['files'])}
 n=restore(manifest,destination,expected_manifest_sha256=m['cas_manifest_sha256']);return {'restored_files':n,'destination':str(Path(destination).resolve())}

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--transport',type=Path,default=Path(__file__).with_name('pending-materials.transport.json'));p.add_argument('--expected-transport-sha256',required=True);p.add_argument('--destination',type=Path,default=Path(__file__).resolve().parent.parent);p.add_argument('--verify-only',action='store_true');a=p.parse_args();print(json.dumps(run(a.transport,a.expected_transport_sha256,a.destination,a.verify_only),indent=2))
