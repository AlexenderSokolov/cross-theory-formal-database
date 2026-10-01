#!/usr/bin/env python3
"""Bounded parallel compilation; all registry, receipt, activation writes stay serial."""
import argparse,concurrent.futures,fcntl,json,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from admit_staged import reserve_id,import_metadata,write_index
from compile_all import compile_one
from validate_corpus import read_json,write_json,sha,dependencies,local,validate,validation_session,validate_in_session

def next_boundary(count):return (count//100+1)*100

def unique_specs(specs):
    seen={};unique=[];duplicates=[]
    for path,meta in specs:
        key=meta.get('dedup_key')
        if not key:raise ValueError('dedup_key required')
        if key in seen:
            old=seen[key]
            for field in ('id','source_sha256','source_locator','title','difficulty_level','difficulty_reason'):
                if old.get(field)!=meta.get(field):raise ValueError('conflicting duplicate staged identity: '+key)
            duplicates.append(str(path));continue
        seen[key]=meta;unique.append((path,meta))
    return unique,duplicates

def receipt_current(corpus,meta,receipt):
    try:
        return receipt.get('ok') is True and receipt.get('passes')==2 and receipt.get('input_sha256')==sha(local(corpus,meta['tex_path'])) and receipt.get('dependency_sha256')==dependencies(corpus,meta) and local(corpus,receipt['pdf']).read_bytes().startswith(b'%PDF-') and receipt.get('pdf_sha256')==sha(local(corpus,receipt['pdf']))
    except (OSError,ValueError,KeyError,TypeError):return False

def clean_report(report):return not report['errors'] and not any(r['status']=='failed' for r in report['items'].values())

def admit_batch(root,metadata_paths,engine='xelatex',timeout=180,workers=4,target_count=None):
    if type(workers)!=int or not 1<=workers<=4:raise ValueError('workers must be between 1 and 4')
    root=Path(root).resolve();corpus=root/'corpus';start=time.monotonic()
    specs,duplicates=unique_specs([(Path(p).resolve(),read_json(Path(p))) for p in metadata_paths])
    (corpus/'.work/build').mkdir(parents=True,exist_ok=True)
    result={'items':[],'duplicates_skipped':duplicates,'workers':workers}
    with (corpus/'.work/admission.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        manifest=read_json(corpus/'item_status.json');records=manifest['items'];initial=validate(root)
        target=target_count if target_count is not None else next_boundary(initial['qualified_count'])
        if type(target)!=int or target<0:raise ValueError('target_count must be nonnegative integer')
        result.update(initial_qualified=initial['qualified_count'],target_count=target)
        registry_path=corpus/'.work/id_registry.json';registry=read_json(registry_path) if registry_path.exists() else {}
        reserved=[]
        # All collision checks finish before persisting any reservation or changing statuses.
        for path,meta in specs:reserved.append((reserve_id(corpus,registry,meta),path,meta))
        write_json(registry_path,registry)
        receipts_path=corpus/'.work/compile_report.json';receipts=read_json(receipts_path) if receipts_path.exists() else {}
        pending=[]
        for item,path,meta in reserved:
            prior=initial['items'].get(item,{})
            if records.get(item,{}).get('status')=='active' and prior.get('status')=='qualified':
                result['items'].append({'id':item,'status':'active','qualified':True,'skipped':'stable active identity'});continue
            records[item]={'status':'quarantined','metadata':'metadata/'+item+'.json','reason':'Batch admission pending'}
            if meta.get('admission_hold'):
                records[item]['reason']='admission hold: '+str(meta['admission_hold']);result['items'].append({'id':item,'status':'quarantined','qualified':False,'reason':records[item]['reason']});continue
            try:
                m=import_metadata(corpus,path.parent,meta,item)
                if any(str(p.relative_to(corpus))!=m['tex_path'] for p in (corpus/'tex').glob(item+'_*.tex')):raise ValueError('existing id has other tex filenames; resolve explicitly')
                write_json(corpus/'metadata'/(item+'.json'),m)
                pending.append((item,m,receipt_current(corpus,m,receipts.get(item,{}))))
            except (OSError,ValueError,KeyError,TypeError) as e:
                records[item]['reason']='import: '+str(e);result['items'].append({'id':item,'status':'quarantined','qualified':False,'reason':records[item]['reason']})
        write_json(corpus/'item_status.json',manifest);write_index(corpus,records)
        # Worker threads only return receipts. They never write global JSON or INDEX.
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
            futures={pool.submit(compile_one,corpus,item,m,engine,timeout):item for item,m,reuse in pending if not reuse}
            for future in concurrent.futures.as_completed(futures):
                item=futures[future]
                try:receipt=future.result()
                except Exception as e:receipt={'ok':False,'passes':0,'err':'compiler worker: '+str(e)}
                receipts[item]=receipt;write_json(receipts_path,receipts)
        with validation_session():
            current=validate_in_session(root);count=current['qualified_count']
            for item,m,reused in pending:
                receipt=receipts.get(item,{})
                entry={'id':item,'receipt_reused':reused,'qualified':False,'status':'quarantined'}
                if not receipt_current(corpus,m,receipt):records[item]['reason']='compile: '+receipt.get('err','invalid or stale receipt')
                elif count>=target:records[item]['reason']='Ready with current compile receipt; target boundary reached';entry['ready']=True
                else:
                    records[item]={'status':'active','metadata':'metadata/'+item+'.json'}
                    write_json(corpus/'item_status.json',manifest);write_index(corpus,records)
                    # Full strict gate includes global uniqueness and all active items.
                    gate=validate_in_session(root)
                    if clean_report(gate) and gate['items'].get(item,{}).get('status')=='qualified':
                        entry.update(status='active',qualified=True);count=gate['qualified_count']
                    else:
                        records[item]={'status':'quarantined','metadata':'metadata/'+item+'.json','reason':'validation: '+json.dumps(gate['errors'] or {n:r['errors'] for n,r in gate['items'].items() if r['status']=='failed'})}
                if not entry['qualified']:entry['reason']=records[item]['reason']
                write_json(corpus/'item_status.json',manifest);write_index(corpus,records);result['items'].append(entry)
        final=validate(root);write_json(corpus/'.work/validation_report.json',final)
        result.update(final_qualified=final['qualified_count'],strict_gate_ok=clean_report(final),elapsed_seconds=round(time.monotonic()-start,3))
        write_json(corpus/'.work/admission_batch_report.json',result)
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('metadata',nargs='+',type=Path);p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--engine',default='xelatex');p.add_argument('--timeout',type=int,default=180);p.add_argument('--workers',type=int,default=4);p.add_argument('--target-count',type=int);a=p.parse_args()
    try:r=admit_batch(a.root,a.metadata,a.engine,a.timeout,a.workers,a.target_count)
    except (OSError,ValueError,KeyError,TypeError) as e:print(json.dumps({'error':str(e),'qualified':False}));return 1
    print(json.dumps(r,indent=2));return int(not r['strict_gate_ok'] or any(not x.get('qualified') and not x.get('ready') for x in r['items']))
if __name__=='__main__':sys.exit(main())
