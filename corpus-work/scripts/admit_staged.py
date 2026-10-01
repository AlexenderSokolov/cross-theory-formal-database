#!/usr/bin/env python3
"""Serial fail-closed staged admission. Never use concurrently with manual corpus edits."""
import argparse,fcntl,json,re,shutil,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from validate_corpus import read_json,write_json,sha,validate
from compile_all import compile_one

def corpus_path(corpus,name):
    p=Path(name)
    if not p.is_absolute():
        options=[corpus/p,corpus.parent/p]
        p=next((q for q in options if q.is_file()),options[0])
    p=p.resolve()
    if not p.is_relative_to(corpus.resolve()) or not p.is_file(): raise ValueError('source path must be an existing corpus file: '+str(name))
    return str(p.relative_to(corpus.resolve()))

def reserve_id(corpus,registry,meta):
    key=meta.get('dedup_key')
    if not isinstance(key,str) or not key.strip():raise ValueError('dedup_key required')
    records=read_json(corpus/'item_status.json')['items']
    # Recover stable identities from all existing metadata, including quarantined ones.
    for p in (corpus/'metadata').glob('*.json'):
        old=read_json(p)
        if old.get('dedup_key') and old.get('id'):registry.setdefault(old['dedup_key'],old['id'])
    item=registry.get(key)
    if item and meta.get('id') and meta['id']!=item:raise ValueError('requested id disagrees with stable identity')
    item=item or meta.get('id')
    if item:
        if not re.fullmatch(r'[0-9]{3,}',item):raise ValueError('invalid item id')
        if any(v==item and k!=key for k,v in registry.items()):raise ValueError('id collision')
        record=records.get(item,{})
        if record.get('metadata'):
            old=read_json(corpus/record['metadata'])
            if old.get('dedup_key')!=key:raise ValueError('existing metadata id collision')
    else:
        used={int(x) for x in records if re.fullmatch(r'[0-9]{3,}',x)}|{int(x) for x in registry.values()}
        item=str(max(used,default=0)+1).zfill(3)
    registry[key]=item
    return item

def index_fields(item,meta):
    fields=[item,meta['title'],meta['difficulty_level'],meta['author'],meta['source_url']]
    if any('|' in str(v) or '\n' in str(v) for v in fields):raise ValueError('INDEX fields cannot contain pipe/newline')
    return fields

def write_index(corpus,records):
    lines=['# Verified proof corpus','', '| Number | Title | Difficulty | Source | Original |','|---|---|---|---|---|']
    for item,record in sorted(records.items(),key=lambda x:int(x[0])):
        if record.get('status')!='active':continue
        m=read_json(corpus/record['metadata'])
        fields=index_fields(item,m)
        lines.append('| '+' | '.join(fields)+' |')
    (corpus/'INDEX.md').write_text('\n'.join(lines)+'\n')

def stage_file(stage,name):
    p=Path(name)
    if not p.is_absolute():
        options=[stage/p,stage.parent/p,Path.cwd()/p]
        p=next((q for q in options if q.is_file()),options[0])
    p=p.resolve()
    if not p.is_relative_to(stage.resolve()) or not p.is_file():raise ValueError('staged artifact must be inside staging directory: '+name)
    return p

def import_metadata(corpus,stage,meta,item):
    index_fields(item,meta)  # Fail before copying artifacts or allowing activation.
    m=dict(meta);tag=m.get('tag','proof');stem=item+('_stacks_'+tag if m.get('evidence_mode')=='native_tex' and m.get('tag') else '_source_pdf' if m.get('evidence_mode')=='source_pdf_pages' else '_proof')
    for field in ('source_path',):m[field]=corpus_path(corpus,m[field])
    m['extra_source_paths']=[corpus_path(corpus,p) for p in m.get('extra_source_paths',[])]
    # Copy standalone artifacts; retain source provenance at its pinned location.
    try: license_source=stage_file(stage,m['license_path'])
    except ValueError: license_source=corpus/corpus_path(corpus,m['license_path'])
    targets={'tex_path':'tex/'+stem+'.tex','excerpt_path':'sources/stacks_verified/'+stem+'.excerpt.tex','license_path':'assets/license-'+sha(license_source)+'.txt'}
    for field,dest in targets.items():
        name=m.get(field)
        if not name and field=='excerpt_path':continue
        try:src=stage_file(stage,name)
        except ValueError:
            if field!='license_path':raise
            src=corpus/corpus_path(corpus,name)
        dst=corpus/dest;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst);m[field]=dest
    contexts=[]
    for c in m.get('contexts',[]):
        c=dict(c); src=stage_file(stage,c['excerpt_path']);dest='sources/stacks_verified/'+stem+'.context-'+c['tag']+'.tex'
        dst=corpus/dest;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst);c['excerpt_path']=dest
        if 'source_path' not in c:
            c['source_path']=str(Path(m['source_path']).parent/c['file'])
        c['source_path']=corpus_path(corpus,c['source_path']);contexts.append(c)
        if c['source_path'] not in m['extra_source_paths']:m['extra_source_paths'].append(c['source_path'])
    m['contexts']=contexts;m['id']=item
    return m

def admit(root,metadata,engine='xelatex',timeout=180):
    root=Path(root).resolve();corpus=root/'corpus';path=Path(metadata).resolve();stage=path.parent
    (corpus/'.work/build').mkdir(parents=True,exist_ok=True)
    with (corpus/'.work/admission.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        meta=read_json(path)
        if meta.get('admission_hold'):raise ValueError('admission hold: '+str(meta['admission_hold']))
        registry_path=corpus/'.work/id_registry.json'
        registry=read_json(registry_path) if registry_path.exists() else {}
        item=reserve_id(corpus,registry,meta);write_json(registry_path,registry)
        manifest=read_json(corpus/'item_status.json');records=manifest['items']
        records[item]={'status':'quarantined','metadata':'metadata/'+item+'.json','reason':'Admission pending fresh compile and validation'}
        write_json(corpus/'item_status.json',manifest);write_index(corpus,records)
        receipts_path=corpus/'.work/compile_report.json';receipts=read_json(receipts_path) if receipts_path.exists() else {};receipts.pop(item,None);write_json(receipts_path,receipts)
        try:
            m=import_metadata(corpus,stage,meta,item)
            # Prevent old duplicate filenames from silently qualifying.
            extra=[p for p in (corpus/'tex').glob(item+'_*.tex') if str(p.relative_to(corpus))!=m['tex_path']]
            if extra:raise ValueError('existing id has other tex filenames; resolve explicitly')
            write_json(corpus/'metadata'/ (item+'.json'),m)
            receipt=compile_one(corpus,item,m,engine,timeout);receipts[item]=receipt;write_json(receipts_path,receipts)
            if not receipt['ok']:raise ValueError('compile: '+receipt['err'])
            records[item]={'status':'active','metadata':'metadata/'+item+'.json'}
            write_json(corpus/'item_status.json',manifest);write_index(corpus,records)
            report=validate(root)
            write_json(corpus/'.work/validation_report.json',report)
            if report['errors'] or any(r['status']=='failed' for r in report['items'].values()):raise ValueError('validation failed: '+json.dumps(report['errors'] or {n:r['errors'] for n,r in report['items'].items() if r['status']=='failed'}))
            return {'id':item,'status':'active','qualified':True}
        except (OSError,ValueError,KeyError,TypeError) as e:
            records[item]={'status':'quarantined','metadata':'metadata/'+item+'.json','reason':str(e)}
            write_json(corpus/'item_status.json',manifest);write_index(corpus,records)
            report=validate(root);write_json(corpus/'.work/validation_report.json',report)
            return {'id':item,'status':'quarantined','qualified':False,'reason':str(e)}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('metadata',type=Path);p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--engine',default='xelatex');p.add_argument('--timeout',type=int,default=180);a=p.parse_args()
    try:r=admit(a.root,a.metadata,a.engine,a.timeout)
    except (OSError,ValueError,KeyError,TypeError) as e:print(json.dumps({'qualified':False,'error':str(e)}));return 1
    print(json.dumps(r));return int(not r['qualified'])
if __name__=='__main__':sys.exit(main())
