"""Offline restoration of exact regular historical files from a hash-pinned CAS ZIP."""
import argparse,hashlib,json,os,re,stat,tempfile,zipfile
from pathlib import Path,PurePosixPath
HASH=re.compile(r'[0-9a-f]{64}')
def digest(data):return hashlib.sha256(data).hexdigest()
def file_digest(path):
 h=hashlib.sha256()
 with path.open('rb') as stream:
  for data in iter(lambda:stream.read(1024*1024),b''):h.update(data)
 return h.hexdigest()
def unique_json(pairs):
 d={}
 for k,v in pairs:
  if k in d:raise ValueError('duplicate JSON key')
  d[k]=v
 return d
def relative_path(value):
 if not isinstance(value,str) or not value or '\\' in value:
  raise ValueError('invalid relative path')
 p=PurePosixPath(value)
 if p.is_absolute() or '..' in p.parts or '.' in p.parts or str(p)!=value:
  raise ValueError('unsafe relative path')
 return p
def target_path(root,name):
 relative=relative_path(name);p=root/relative
 current=root
 for part in relative.parts:
  current=current/part
  if current.is_symlink():raise ValueError('symlink path is not permitted')
 if not p.resolve().is_relative_to(root):raise ValueError('path escapes destination')
 return p
def load_bundle(manifest_path,expected_manifest_sha256=None):
 manifest_path=Path(manifest_path).resolve()
 if not HASH.fullmatch(str(expected_manifest_sha256 or '')):raise ValueError('expected manifest digest is required')
 manifest_bytes=manifest_path.read_bytes()
 if digest(manifest_bytes)!=expected_manifest_sha256:raise ValueError('manifest digest mismatch against expected binding')
 record=json.loads(manifest_bytes.decode('utf8'),object_pairs_hook=unique_json)
 if type(record.get('schema_version')) is not int or record['schema_version']!=1:
  raise ValueError('unsupported manifest version')
 if record.get('format')!='sha256-content-addressed-zip':raise ValueError('unsupported manifest format')
 name=relative_path(record.get('archive_name'))
 if len(name.parts)!=1:raise ValueError('archive path must be one sibling filename')
 archive=manifest_path.parent/name
 if archive.is_symlink() or not archive.is_file():raise ValueError('missing or symlink archive')
 if not HASH.fullmatch(str(record.get('archive_sha256',''))) or type(record.get('archive_bytes')) is not int or record['archive_bytes']<0:
  raise ValueError('malformed archive hash/size')
 if archive.stat().st_size!=record['archive_bytes'] or file_digest(archive)!=record['archive_sha256']:
  raise ValueError('archive digest/size mismatch')
 entries=record.get('files')
 if not isinstance(entries,list) or not entries:raise ValueError('empty or invalid files list')
 seen=set();sizes={}
 for entry in entries:
  if not isinstance(entry,dict):raise ValueError('invalid file entry')
  name=str(relative_path(entry.get('path')))
  if name in seen:raise ValueError('duplicate manifest paths')
  seen.add(name);sha=entry.get('sha256');size=entry.get('bytes');mode=entry.get('mode')
  if not HASH.fullmatch(str(sha or '')):raise ValueError('malformed file hash')
  if type(size) is not int or size<0:raise ValueError('malformed file size')
  if type(mode) is not int or not 0<=mode<=0o777:raise ValueError('special or malformed file mode')
  if sha in sizes and sizes[sha]!=size:raise ValueError('inconsistent blob size')
  sizes[sha]=size
 with zipfile.ZipFile(archive) as z:
  names=z.namelist()
  if len(names)!=len(set(names)):raise ValueError('duplicate archive members')
  if set(names)!={'blobs/'+sha for sha in sizes}:raise ValueError('missing or extra blob members')
  for sha,size in sizes.items():
   info=z.getinfo('blobs/'+sha);mode=info.external_attr>>16
   if not stat.S_ISREG(mode) or mode&0o7000:raise ValueError('archive member is not an ordinary regular file')
   data=z.read(info)
   if len(data)!=size or digest(data)!=sha:raise ValueError('blob digest/size mismatch')
 return record,archive,entries
def restore_entry(z,entry,root):
 target=target_path(root,entry['path']);data=z.read('blobs/'+entry['sha256'])
 if len(data)!=entry['bytes'] or digest(data)!=entry['sha256']:raise ValueError('blob digest/size mismatch')
 if target.exists():
  if not target.is_file() or file_digest(target)!=entry['sha256'] or stat.S_IMODE(target.stat().st_mode)!=entry['mode']:
   raise FileExistsError('refusing to overwrite different existing file or mode: '+entry['path'])
  return target
 target.parent.mkdir(parents=True,exist_ok=True);target=target_path(root,entry['path'])
 fd,name=tempfile.mkstemp(prefix='.cas-restore-',dir=target.parent);temporary=Path(name)
 try:
  with os.fdopen(fd,'wb') as stream:stream.write(data);stream.flush();os.fsync(stream.fileno())
  temporary.chmod(entry['mode']);os.link(temporary,target)
 finally:temporary.unlink(missing_ok=True)
 return target
def restore(manifest_path,destination,selected_path=None,expected_manifest_sha256=None):
 record,archive,entries=load_bundle(manifest_path,expected_manifest_sha256);root=Path(destination)
 if root.is_symlink():raise ValueError('symlink destination not permitted')
 root=root.resolve();root.mkdir(parents=True,exist_ok=True)
 if selected_path is not None:
  relative_path(selected_path);entries=[e for e in entries if e['path']==selected_path]
  if not entries:raise ValueError('requested path absent')
 # Preflight every destination before writing any selected file.
 for entry in entries:
  p=target_path(root,entry['path'])
  if p.exists() and (not p.is_file() or file_digest(p)!=entry['sha256'] or stat.S_IMODE(p.stat().st_mode)!=entry['mode']):
   raise FileExistsError('refusing to overwrite different existing file or mode: '+entry['path'])
 with zipfile.ZipFile(archive) as z:
  for entry in entries:restore_entry(z,entry,root)
 return len(entries)
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--manifest',type=Path,required=True);p.add_argument('--destination',type=Path,required=True);p.add_argument('--path');p.add_argument('--expected-manifest-sha256',required=True);a=p.parse_args();print('Restored verified historical files:',restore(a.manifest,a.destination,a.path,a.expected_manifest_sha256))
