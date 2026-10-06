"""Prepare a new, isolated union of canonical editable packages.

This does not admit or publish problems. Fresh editable-delivery validation of
the resulting package and remote restoration remain separate required gates.
"""
import argparse
import datetime as dt
import hashlib
import importlib.util
import json
import os
import re
import shutil
from pathlib import Path, PurePosixPath

GLOBAL_FILES = {'manifest.json', 'INDEX.md', 'delivery-evidence.json',
                'corpus.sqlite', 'database-delivery.json', 'README.md'}

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024*1024), b''): h.update(chunk)
    return h.hexdigest()

def dump(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def local(root, value):
    p = PurePosixPath(value)
    if p.is_absolute() or '..' in p.parts or '\\' in value:
        raise ValueError('unsafe package-relative path: '+value)
    result = root.joinpath(*p.parts)
    if result.is_symlink() or not result.resolve().is_relative_to(root.resolve()):
        raise ValueError('symlink/escaping package path: '+value)
    return result

def load_package(root):
    manifest_path = root/'manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    evidence = json.loads((root/'delivery-evidence.json').read_text(encoding='utf-8'))
    if evidence.get('package_manifest_sha256') != sha(manifest_path):
        raise ValueError('evidence does not bind the actual manifest')
    rows = manifest['items']
    ids = [x['problem_id'] for x in rows]
    if len(set(ids)) != len(ids): raise ValueError('duplicate ID inside input package')
    if set(evidence['items']) != set(ids): raise ValueError('incomplete item evidence')
    for item in rows:
        ident = item['problem_id']; witness = evidence['items'][ident]
        if item['status'] != 'verified_editable_tex': raise ValueError('unqualified input status: '+ident)
        if not witness.get('independent_problem_unit') or not witness.get('claim_key'):
            raise ValueError('missing independent claim/core evidence: '+ident)
        path = local(root, item['item_path'])
        if not path.is_file() or sha(path) != item['tex_sha256']:
            raise ValueError('missing/changed editable body: '+ident)
        if witness.get('item_sha256') != item['tex_sha256']:
            raise ValueError('body/evidence identity mismatch: '+ident)
        if not witness.get('bodies') or not witness.get('sources'):
            raise ValueError('missing body/source evidence: '+ident)
        for asset in item.get('asset_dependencies', []):
            p = local(root, asset['path'])
            if not p.is_file() or sha(p) != asset['sha256']:
                raise ValueError('missing/changed asset: '+ident)
        for name in ('compile_receipt', 'license_path'):
            if not local(root,item[name]).is_file(): raise ValueError('missing '+name+': '+ident)
    return manifest, evidence

def index_rows(root, ids):
    rows={}
    for line in (root/'INDEX.md').read_text(encoding='utf-8').splitlines():
        match=re.match(r'^\|\s*(\d{3,6})\s*\|',line)
        if not match:continue
        ident=match.group(1)
        if ident in rows:raise ValueError('duplicate INDEX row: '+ident)
        rows[ident]=line
    if set(rows)!=ids:raise ValueError('INDEX IDs do not match manifest')
    return rows

def verify_filemap(root, filemap):
    if not isinstance(filemap,dict) or not filemap:raise ValueError('explicit reviewed filemap required')
    actual=set()
    for source in root.rglob('*'):
        if source.is_symlink():raise ValueError('symlink in package')
        if source.is_file():actual.add(source.relative_to(root).as_posix())
    if actual!=set(filemap):raise ValueError('unreviewed/missing package file')
    for name,expected in filemap.items():
        if sha(local(root,name))!=expected:raise ValueError('reviewed file hash mismatch: '+name)

def copy_inputs(root, output, filemap):
    for name in sorted(filemap):
        source=local(root,name);relative=source.relative_to(root)
        if relative.parts[0] == 'database-parts' or relative.name.endswith('.sqlite.tmp'):
            continue
        if len(relative.parts)==1 and relative.name in GLOBAL_FILES: continue
        target = output/relative
        if target.exists():
            if sha(target) != sha(source): raise ValueError('conflicting package file: '+str(relative))
            continue
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(source,target)

def merge_packets(base, incoming, output, rebuild_script, expected_base, expected_incoming, semantic_review=None):
    base, incoming, output = (Path(p).resolve() for p in (base,incoming,output))
    if output.exists(): raise ValueError('output must be new; existing outputs are preserved')
    if output.is_relative_to(base) or output.is_relative_to(incoming):
        raise ValueError('output cannot be inside an immutable input')
    if sha(base/'manifest.json')!=expected_base or sha(incoming/'manifest.json')!=expected_incoming:
        raise ValueError('pinned manifest identity mismatch')
    bm, be = load_package(base); im, ie = load_package(incoming)
    base_ids={r['problem_id'] for r in bm['items']}; incoming_ids={r['problem_id'] for r in im['items']}
    if base_ids & incoming_ids: raise ValueError('duplicate stable ID across packages')
    rows=bm['items']+im['items']; sources={}; claims=set()
    for r in rows:
        ident=r['problem_id']; witness=(be if ident in base_ids else ie)['items'][ident]
        key=' '.join(str(witness['claim_key']).casefold().split())
        if key in claims: raise ValueError('duplicate claim key/semantic identity: '+str(key))
        claims.add(key)
        source=tuple(r[k] for k in ('author','work','source_url','source_version','retrieved_at','license','license_path'))
        if r['source_id'] in sources and sources[r['source_id']]!=source:
            raise ValueError('source identity conflict: '+r['source_id'])
        sources[r['source_id']]=source
    if semantic_review is None:
        raise ValueError('explicit bounded semantic/source review receipt required')
    review=json.loads(Path(semantic_review).read_text())
    if set(review.get('incoming_ids',[]))!=incoming_ids or review.get('base_manifest_sha256')!=expected_base or review.get('incoming_manifest_sha256')!=expected_incoming:
        raise ValueError('semantic review receipt identity mismatch')
    if review.get('holds') or review.get('duplicates') or review.get('status')!='material_review_complete':
        raise ValueError('unresolved semantic/material review')
    filemaps=review.get('reviewed_filemaps',{})
    verify_filemap(base,filemaps.get('base'));verify_filemap(incoming,filemaps.get('incoming'))
    retained_index={**index_rows(base,base_ids),**index_rows(incoming,incoming_ids)}
    output.mkdir(parents=True)
    copy_inputs(base,output,filemaps['base']);copy_inputs(incoming,output,filemaps['incoming'])
    manifest=dict(bm)
    manifest['items']=sorted(rows,key=lambda r:int(r['problem_id']))
    manifest['verified_count']=len(rows)
    manifest['material_reviewed_count']=len(rows)
    manifest['scope']='Canonical material union; current compilation/gate/publication status is recorded separately.'
    manifest['yupeng_merge_inputs']={'base_manifest_sha256':expected_base,'incoming_manifest_sha256':expected_incoming,'incoming_ids':sorted(incoming_ids,key=int)}
    dump(output/'manifest.json',manifest)
    evidence=dict(be)
    evidence['items']={**be['items'],**ie['items']}
    evidence['package_manifest_sha256']=sha(output/'manifest.json')
    evidence['derived_at']=dt.datetime.now(dt.timezone.utc).isoformat()
    evidence['derivation_scope']='Exact canonical item evidence retained from the two pinned inputs. No fresh compile, admission, publication or mathematical certification is implied.'
    evidence['merge_input_evidence']=[{'manifest_sha256':expected_base,'evidence_sha256':sha(base/'delivery-evidence.json')},{'manifest_sha256':expected_incoming,'evidence_sha256':sha(incoming/'delivery-evidence.json')}]
    dump(output/'delivery-evidence.json',evidence)
    lines=['# 完整可编辑题证材料目录','','本包为固定输入的隔离合并；当前运行与远端交付状态须查对应实际回执。','', '| 题号 | 题名 | 难度 | 可编辑 TeX | 来源及定位 |','|---|---|---|---|---|']
    for r in manifest['items']:
        lines.append(retained_index[r['problem_id']])
    (output/'INDEX.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    spec=importlib.util.spec_from_file_location('trusted_corpus_rebuild',Path(rebuild_script).resolve())
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    count=module.rebuild(output,output/'corpus.sqlite')
    receipt={'status':'prepared_not_fresh_validated_or_published','items':count,'base_items':len(base_ids),'incoming_items':len(incoming_ids),'manifest_sha256':sha(output/'manifest.json'),'sqlite_sha256':sha(output/'corpus.sqlite'),'semantic_review_sha256':sha(Path(semantic_review))}
    dump(output/'merge-preparation.json',receipt)
    return receipt

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for flag in ('base','incoming','output','rebuild-script','semantic-review'): p.add_argument('--'+flag,type=Path,required=True)
    p.add_argument('--base-manifest-sha256',required=True);p.add_argument('--incoming-manifest-sha256',required=True)
    a=p.parse_args()
    print(json.dumps(merge_packets(a.base,a.incoming,a.output,a.rebuild_script,a.base_manifest_sha256,a.incoming_manifest_sha256,a.semantic_review),ensure_ascii=False,indent=2))
if __name__=='__main__':main()
