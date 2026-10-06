"""Run actual corpus helpers with four isolated serial worker queues.

Compilation and qualification are distinct counters; failed items stay failed.
The orchestration writes only external build/receipt/report directories.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import threading
import time

ROOT=Path('/disks/sata1/yupeng/human-proof-corpus')
LOCK=threading.Lock()
RESULTS=[]

def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for data in iter(lambda:f.read(1024*1024),b''):h.update(data)
    return h.hexdigest()

def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')

def summarize(report,start,total):
    value={'schema_version':1,'started_at':start,'updated_at':dt.datetime.now(dt.timezone.utc).isoformat(),
           'target_compile_count':total,'completed_attempts':len(RESULTS),
           'compile_ok':sum(r['compile_ok'] for r in RESULTS),
           'compile_failed_ids':[r['id'] for r in RESULTS if not r['compile_ok']],
           'pending_individual_passed':sum(r.get('individual_ok',False) for r in RESULTS),
           'pending_individual_failed_ids':[r['id'] for r in RESULTS if r.get('individual_ok') is False],
           'baseline_aggregate':'not_run','remote_delivered_count':975,'items':sorted(RESULTS,key=lambda r:int(r['id']))}
    write(report/'progress.json',value)

def worker(number,jobs,label,report,start,total):
    for phase,package,row in jobs:
        ident=row['problem_id'];build=ROOT/'builds'/label/phase/f'worker-{number}'
        receipts=ROOT/'receipts'/label/phase
        log=report/'compile'/f'{phase}-{ident}.stdout'
        log.parent.mkdir(parents=True,exist_ok=True)
        command=[str(ROOT/'runtime/bin/compile-isolated'),'--package',str(package),'--build-root',str(build),
                 '--receipt-root',str(receipts),'--item',ident,'--engine','xelatex','--timeout','180']
        began=time.monotonic()
        with log.open('w') as stream:
            process=subprocess.run(command,stdout=stream,stderr=subprocess.STDOUT,env={'PATH':os.environ['PATH']})
        path=receipts/(ident+'.json')
        receipt=json.loads(path.read_text()) if path.exists() else {'ok':False,'error':'helper did not create receipt'}
        ok=process.returncode==0 and receipt.get('ok') is True and receipt.get('passes',0)>=2 and receipt.get('input_sha256')==row['tex_sha256']
        result={'id':ident,'phase':phase,'package':str(package),'build_root':str(build),'receipt':str(path),
                'command':command,'exit_code':process.returncode,'compile_ok':ok,
                'compile_seconds':round(time.monotonic()-began,3),'passes':receipt.get('passes',0),'error':receipt.get('error')}
        if phase=='pending40' and ok:
            gate_report=report/'per-item'/(ident+'.json')
            validate=[str(ROOT/'operations/env-isolated.sh'),str(ROOT/'repo/corpus-work/scripts/validate_corpus.py'),
                      '--mode','editable-delivery','--package',str(package),'--evidence',str(package/'delivery-evidence.json'),
                      '--build-root',str(build),'--receipt-root',str(receipts),'--item',ident,'--report',str(gate_report)]
            gate_report.parent.mkdir(parents=True,exist_ok=True)
            with (report/'per-item'/(ident+'.stdout')).open('w') as stream:
                gate=subprocess.run(validate,stdout=stream,stderr=subprocess.STDOUT,env={'PATH':os.environ['PATH']})
            value=json.loads(gate_report.read_text()) if gate_report.exists() else {}
            result.update(individual_ok=gate.returncode==0 and value.get('editable_qualified_count')==1 and not value.get('errors'),
                          individual_exit=gate.returncode,individual_report=str(gate_report),individual_command=validate)
        with LOCK:
            RESULTS.append(result)
            with (report/'attempts.jsonl').open('a') as stream:stream.write(json.dumps(result,ensure_ascii=False)+'\n')
            summarize(report,start,total)
            if not ok or result.get('individual_ok') is False:
                print('HOLD',phase,ident,result.get('error') or 'individual gate failed',flush=True)
            elif len(RESULTS)%50==0:print('completed',len(RESULTS),'of',total,flush=True)

def collect_builds(label,phases,report):
    for phase,ids in phases.items():
        out=ROOT/'builds'/label/phase/'aggregate'
        if out.exists():raise RuntimeError('aggregate output already exists; preserve and use a new label')
        out.mkdir(parents=True)
        for ident in ids:
            matches=list((ROOT/'builds'/label/phase).glob(f'worker-*/{ident}'))
            if len(matches)!=1:continue
            shutil.copytree(matches[0],out/ident,copy_function=os.link)
        write(report/f'{phase}-build-materialization.json',{'phase':phase,'build_root':str(out),'actual_item_dirs':len(list(out.iterdir())),'method':'hardlink immutable actual per-worker artifacts; no recompilation asserted'})

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--base',type=Path,required=True);p.add_argument('--pending',type=Path,required=True)
    p.add_argument('--label',required=True);p.add_argument('--workers',type=int,default=4);a=p.parse_args()
    if not 1<=a.workers<=8:raise SystemExit('unsupported compile worker count')
    report=ROOT/'reports'/a.label
    if report.exists():raise SystemExit('label already exists; do not overwrite earlier attempts')
    report.mkdir(parents=True);start=dt.datetime.now(dt.timezone.utc).isoformat();jobs=[];phases={}
    for phase,package in [('pending40',a.pending.resolve()),('baseline975',a.base.resolve())]:
        rows=json.loads((package/'manifest.json').read_text())['items'];phases[phase]=[r['problem_id'] for r in rows]
        jobs.extend((phase,package,row) for row in rows)
    if len({x[2]['problem_id'] for x in jobs})!=len(jobs):raise SystemExit('duplicate IDs across compile queues')
    write(report/'run-intent.json',{'started_at':start,'workers':a.workers,'process_id':os.getpid(),'compile_items':len(jobs),
         'package_manifests':{str(a.base):digest(a.base/'manifest.json'),str(a.pending):digest(a.pending/'manifest.json')},
         'compile_helper_sha256':digest(ROOT/'repo/corpus-work/scripts/compile_editable_delivery.py'),
         'validator_sha256':digest(ROOT/'repo/corpus-work/scripts/validate_corpus.py'),
         'isolation_launcher_sha256':digest(ROOT/'operations/env-isolated.py')})
    with ThreadPoolExecutor(max_workers=a.workers) as pool:
        futures=[pool.submit(worker,n,jobs[n::a.workers],a.label,report,start,len(jobs)) for n in range(a.workers)]
        for f in futures:f.result()
    collect_builds(a.label,phases,report)
    summarize(report,start,len(jobs))
    print('finished',len(RESULTS),'actual attempts; compilation pass',sum(r['compile_ok'] for r in RESULTS),flush=True)
    return int(any(not r['compile_ok'] or r.get('individual_ok') is False for r in RESULTS))

if __name__=='__main__':raise SystemExit(main())
