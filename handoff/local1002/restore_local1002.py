"""Offline LOCAL1002 reconstruction from repo/editable-corpus and repo/handoff CAS parts.
No downloads, Git writes, production edits or full base copies. Immutable base/cache
files are hardlinked; compile only into separate fresh build/receipt directories.
"""
from pathlib import Path,PurePosixPath
import argparse,hashlib,json,io,zipfile,stat,os,errno

def digest(b):return hashlib.sha256(b).hexdigest()
def file_hash(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def unique(pairs):
 out={}
 for k,v in pairs:
  if k in out:raise ValueError('duplicate JSON key')
  out[k]=v
 return out

def relative(name):
 if not isinstance(name,str) or not name or '\\' in name:raise ValueError('invalid relative path')
 p=PurePosixPath(name)
 if p.is_absolute() or '..' in p.parts or '.' in p.parts or str(p)!=name:raise ValueError('unsafe relative path')
 return p

def safe(root,name):
 p=root/relative(name);cur=root
 for part in relative(name).parts:
  cur=cur/part
  if cur.is_symlink():raise ValueError('symlink path is forbidden')
 if not p.resolve().is_relative_to(root):raise ValueError('path escapes root')
 return p

def pinned_json(path,expected):
 if not isinstance(expected,str) or len(expected)!=64:raise ValueError('explicit SHA256 required')
 raw=Path(path).read_bytes()
 if digest(raw)!=expected:raise ValueError('manifest/plan digest mismatch')
 return json.loads(raw,object_pairs_hook=unique)

def transport_archive(handoff,ref):
 tp=safe(handoff,ref['transport_path']);t=pinned_json(tp,ref['transport_sha256'])
 if t.get('schema_version')!=1 or t.get('format')!='ordered-binary-parts':raise ValueError('unsupported transport')
 chunks=[];seen=set()
 for seq,r in enumerate(t.get('parts',[]),1):
  name=relative(r['name'])
  if len(name.parts)!=1 or str(name) in seen or r['sequence']!=seq:raise ValueError('invalid part order/name')
  seen.add(str(name));p=safe(tp.parent,str(name))
  if not p.is_file():raise ValueError('missing part')
  raw=p.read_bytes()
  if len(raw)!=r['bytes'] or digest(raw)!=r['sha256']:raise ValueError('part hash/length mismatch')
  chunks.append(raw)
 raw=b''.join(chunks)
 if len(raw)!=t['archive_bytes'] or digest(raw)!=t['archive_sha256']:raise ValueError('whole archive binding mismatch')
 z=zipfile.ZipFile(io.BytesIO(raw));names=z.namelist()
 if len(names)!=len(set(names)):raise ValueError('duplicate archive member')
 for name in names:
  relative(name);info=z.getinfo(name);mode=info.external_attr>>16
  if not name.startswith('blobs/') or not stat.S_ISREG(mode) or mode&0o7000:raise ValueError('invalid object member')
 if ref.get('manifest_path'):
  m=pinned_json(safe(handoff,ref['manifest_path']),ref['manifest_sha256'])
  if m.get('archive_sha256')!=t['archive_sha256']:raise ValueError('CAS/transport mismatch')
  allowed={r['sha256']:r['bytes'] for r in m['files']}
  if set(names)!={'blobs/'+h for h in allowed}:raise ValueError('CAS member set mismatch')
  for sha,size in allowed.items():
   data=z.read('blobs/'+sha)
   if len(data)!=size or digest(data)!=sha:raise ValueError('CAS object mismatch')
 return z

def restore_plan(plan_path,expected_plan_sha,handoff,base,destination,cache=None,verify_only=False):
 plan=pinned_json(plan_path,expected_plan_sha)
 if plan.get('schema_version')!=1 or plan.get('format')!='exact-base-plus-shared-cas-overlay':raise ValueError('unsupported plan')
 handoff=Path(handoff).resolve();base=Path(base).resolve();destination=Path(destination)
 if destination.exists() or destination.is_symlink():raise FileExistsError('destination must be new; existing data is never overwritten')
 dest=destination.resolve();cache=Path(cache).resolve() if cache else None
 if dest.is_relative_to(base) or base.is_relative_to(dest):raise ValueError('base and destination must be disjoint')
 zips={name:transport_archive(handoff,ref) for name,ref in plan['cas_sources'].items()};seen=set();validated=[]
 for e in plan['files']:
  relative(e['path'])
  if e['path'] in seen or type(e['bytes']) is not int or e['bytes']<0 or type(e['mode']) is not int or not 0<=e['mode']<=0o777:raise ValueError('invalid or duplicate file entry')
  seen.add(e['path']);kind=e['kind']
  if kind=='base':
   p=safe(base,e['path'])
   if not p.is_file() or p.stat().st_size!=e['bytes'] or file_hash(p)!=e['sha256'] or stat.S_IMODE(p.stat().st_mode)!=e['mode']:raise ValueError('base file/hash/mode mismatch: '+e['path'])
  elif kind in zips:
   data=zips[kind].read('blobs/'+e['sha256'])
   if len(data)!=e['bytes'] or digest(data)!=e['sha256']:raise ValueError('object mismatch: '+e['path'])
  else:raise ValueError('unknown source kind')
  validated.append(e)
 if verify_only:return {'verified_files':len(validated),'target_count':plan['target_count'],'publication_conditional':plan.get('base_anchor',{}).get('publication_conditional',True)}
 dest.mkdir(parents=True,exist_ok=False)
 for e in validated:
  dst=safe(dest,e['path']);dst.parent.mkdir(parents=True,exist_ok=True);src=None
  if e['kind']=='base':src=safe(base,e['path'])
  elif cache:
   candidate=safe(cache,e['path'])
   if candidate.is_file() and candidate.stat().st_size==e['bytes'] and file_hash(candidate)==e['sha256'] and stat.S_IMODE(candidate.stat().st_mode)==e['mode']:src=candidate
  if src:
   try:os.link(src,dst)
   except OSError as err:
    if err.errno==errno.EXDEV:raise ValueError('base/cache hardlink crosses filesystem; choose output on the same volume, no automatic bulk copy') from err
    raise
  else:
   data=zips[e['kind']].read('blobs/'+e['sha256']);dst.write_bytes(data);dst.chmod(e['mode'])
  if file_hash(dst)!=e['sha256']:raise ValueError('restored file identity mismatch')
 manifest=json.loads((dest/'manifest.json').read_bytes(),object_pairs_hook=unique)
 if len(manifest['items'])!=plan['target_count'] or len({r['problem_id'] for r in manifest['items']})!=plan['target_count']:raise ValueError('restored unique item count mismatch')
 return {'restored_files':len(validated),'target_count':plan['target_count'],'publication_conditional':plan.get('base_anchor',{}).get('publication_conditional',True),'base_files_hardlinked_no_full_copy':True,'destination':str(dest)}

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repo',type=Path,required=True);p.add_argument('--base',type=Path);p.add_argument('--handoff',type=Path);p.add_argument('--output',type=Path,required=True);p.add_argument('--verified-cache',type=Path);p.add_argument('--verify-only',action='store_true');p.add_argument('--expected-plan-sha256');a=p.parse_args();repo=a.repo.resolve();hand=(a.handoff or repo/'handoff').resolve();base=(a.base or repo/'editable-corpus').resolve();plan=hand/'local1002/reconstruction.plan.json';expected=a.expected_plan_sha256 or (hand/'local1002/reconstruction.plan.sha256').read_text().strip();print(json.dumps(restore_plan(plan,expected,hand,base,a.output,a.verified_cache,a.verify_only),indent=2))
