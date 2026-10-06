"""Restore exact real compile artifacts outside an immutable corpus package."""
import argparse
import hashlib
import io
import json
from pathlib import Path,PurePosixPath
import zipfile

def digest(data):return hashlib.sha256(data).hexdigest()
def canonical(value):
    if not isinstance(value,str) or not value:raise ValueError('empty/nonstring path')
    p=PurePosixPath(value)
    if p.is_absolute() or '..' in p.parts or '\\' in value or p.as_posix()!=value or value=='.':
        raise ValueError('unsafe/noncanonical path')
    return p
def restore(root,destination):
    root=root.resolve()
    destination=destination.resolve()
    d=json.loads((root/'validation-artifact-delivery.json').read_text());data=[]
    parts=d['parts']
    if [p['index'] for p in parts]!=list(range(d['part_count'])):raise ValueError('invalid ordered parts')
    for p in parts:
        name=canonical(p['path']);part=root/name
        if part.is_symlink() or not part.resolve().is_relative_to(root):raise ValueError('part escapes package')
        b=part.read_bytes()
        if len(b)!=p['bytes'] or digest(b)!=p['sha256']:raise ValueError('part identity mismatch')
        data.append(b)
    archive=b''.join(data)
    if len(archive)!=d['archive_bytes'] or digest(archive)!=d['archive_sha256']:raise ValueError('archive mismatch')
    if destination.exists():raise ValueError('destination must be new; never overwrite existing artifacts')
    with zipfile.ZipFile(io.BytesIO(archive)) as z:
        if len(z.namelist())!=len(set(z.namelist())):raise ValueError('duplicate archive entries')
        filemap=json.loads(z.read('ARTIFACT_FILEMAP.json'))
        if set(z.namelist())!=set(filemap)|{'ARTIFACT_FILEMAP.json'} or len(filemap)!=d['file_count']:raise ValueError('filemap mismatch')
        verified=[];targets=set()
        for name,pin in filemap.items():
            path=canonical(name);target=(destination/path).resolve()
            if not target.is_relative_to(destination) or target in targets:raise ValueError('duplicate/escaping artifact target')
            targets.add(target)
            b=z.read(name)
            if len(b)!=pin['bytes'] or digest(b)!=pin['sha256']:raise ValueError('artifact identity mismatch')
            verified.append((path,b))
    destination.mkdir(parents=True)
    for name,b in verified:
        p=destination/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b);p.chmod(0o644)
    result={'status':'actual_restore_complete','artifact_files':len(verified),'archive_sha256':d['archive_sha256'],'destination':str(destination)}
    (destination/'RESTORE_RECEIPT.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--destination',type=Path,required=True);a=p.parse_args()
    print(json.dumps(restore(Path(__file__).resolve().parent,a.destination.resolve()),indent=2))
