#!/usr/bin/env python3
"""Install exact licensed test data only. Never execute upstream files or overwrite differences."""
import argparse, hashlib, json, shutil
from pathlib import Path

def install(project, manifest):
    manifest=Path(manifest).resolve(); data=json.loads(manifest.read_text())
    source=manifest.parent/data['source_dir']; project=Path(project).resolve()
    if not (project/'scripts/stacks_extract.py').is_file():
        raise ValueError('Expected an existing corpus project with scripts/stacks_extract.py')
    target=project/'corpus/raw/stacks-project'; jobs=[]
    for r in data['files']:
        rel=Path(r['path'])
        if rel.is_absolute() or '..' in rel.parts: raise ValueError('Unsafe relative path')
        src=source/rel; dst=target/rel
        if src.is_symlink() or not src.is_file(): raise ValueError('Invalid source file')
        raw=src.read_bytes()
        if len(raw)!=r['bytes'] or hashlib.sha256(raw).hexdigest()!=r['sha256']:
            raise ValueError('Source identity mismatch')
        if not dst.resolve().is_relative_to(project): raise ValueError('Destination escape')
        for parent in [dst,*dst.parents]:
            if parent==project:break
            if parent.is_symlink():raise ValueError('Symlink destination')
        if dst.exists():
            if not dst.is_file() or hashlib.sha256(dst.read_bytes()).hexdigest()!=r['sha256']:
                raise ValueError('Refuse to overwrite different existing file: '+str(rel))
        else: jobs.append((src,dst))
    for src,dst in jobs:
        dst.parent.mkdir(parents=True,exist_ok=True)
        with dst.open('xb') as f:f.write(src.read_bytes())
    return {'installed':len(jobs),'already_exact':len(data['files'])-len(jobs),'files':len(data['files'])}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project',required=True)
    p.add_argument('--manifest',default=str(Path(__file__).with_name('stacks-test-fixtures-manifest.json')))
    a=p.parse_args();print(json.dumps(install(a.project,a.manifest)))
