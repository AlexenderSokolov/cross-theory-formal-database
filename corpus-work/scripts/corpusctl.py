#!/usr/bin/env python3
"""Single SSH entry point for corpus jobs, explicit admission and batch delivery."""
from __future__ import annotations
import argparse
import contextlib
import fcntl
import json
import os
import re
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone

import corpus_batch

B = Path(__file__).resolve().parents[3]
DEFAULT_STATE = B / 'operations/corpusctl'
DEFAULT_QUEUE = B / 'repo/handoff/yupeng/PRODUCTION_QUEUE.json'

def load(path):
    return json.loads(Path(path).read_text())

def save(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode='w', dir=path.parent, prefix='.'+path.name, delete=False) as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')
        name = f.name
    os.replace(name, path)

@contextlib.contextmanager
def controller_lock(state):
    state.mkdir(parents=True, exist_ok=True)
    with (state/'controller.lock').open('a') as f:
        fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield

def admit(queue, decision, project=B):
    row = load(decision)
    fields = ('problem_id', 'package', 'build_root', 'receipt_root', 'accepted_report',
              'owner_final_ready', 'accepted_H', 'difficulty_reason', 'material_basis',
              'semantic_basis', 'rights_basis', 'admitted_by')
    for field in fields:
        if not isinstance(row.get(field), str) or not row[field].strip():
            raise ValueError('explicit admission field required: '+field)
    if row['accepted_H'] not in ('H1','H2','H3'):
        raise ValueError('invalid difficulty')
    if row.get('decision') != 'admit':
        raise ValueError('explicit admit decision required; READY is not admission')
    row.update(state='root_admitted_waiting_batch', final_revision_frozen=True,
               main_count_increment_before_batch=0)
    q = load(queue)
    existing = next((x for x in q['queued_new_root_admitted'] if x['problem_id']==row['problem_id']), None)
    if existing:
        if all(existing.get(k)==row.get(k) for k in fields):
            return {'status':'already_admitted', 'problem_id':row['problem_id']}
        raise ValueError('existing admission differs; preserve it and review a revision')
    base = load(Path(q['base']['package'])/'manifest.json')
    if row['problem_id'] in {x['problem_id'] for x in base['items']}:
        raise ValueError('already present in merged master')
    # Reuse the existing final gate and identity checks, without rerunning TeX/gate.
    corpus_batch.entry(row, project, incoming=True)
    q['queued_new_root_admitted'].append(row)
    n=len(q['queued_new_root_admitted'])
    q.update(queued_new_count=n, new_root_admitted_total_before_merge=q['base']['local_count']+n,
             remaining_new_root_admissions_for_first_release=max(0,25-(q['base']['local_count']-q['base']['remote_main_count']+n)),
             updated_at=datetime.now(timezone.utc).isoformat())
    save(queue,q)
    return {'status':'admitted_waiting_batch','problem_id':row['problem_id'],'main_count_increment':0,'queued_new_count':n}

def check_claim(queue, state, argv):
    keys=[argv[i+1] for i,x in enumerate(argv[:-1]) if x=='--work-key']
    ids={k.split(':',1)[1] for k in keys if re.fullmatch(r'id:\d+',k)}
    if not ids: raise ValueError('claim requires explicit --work-key id:ID for each candidate')
    q=load(queue);m=load(Path(q['base']['package'])/'manifest.json')
    merged={str(x['problem_id']) for x in m['items']}
    admitted={str(x['problem_id']) for x in q['queued_new_root_admitted']}
    collision=ids & (merged|admitted)
    if collision: raise ValueError('candidate already merged/admitted: '+','.join(sorted(collision)))
    source_keys={x['source_id'].lower() for x in m['items']}
    if source_keys & {k.lower() for k in keys}: raise ValueError('work already present in master; root must review claim equivalence before new selection')
    holdfile=state/'source-holds.json'
    holds=load(holdfile) if holdfile.exists() else {}
    if ids & set(holds): raise ValueError('source hold: '+','.join(sorted(ids & set(holds))))
    from corpus_runtime import Runtime
    requested_job=argv[argv.index('--job-id')+1] if '--job-id' in argv else None
    def normalize(k):return 'id:'+k if k.isdecimal() else k.lower()
    normalized={normalize(k) for k in keys}
    for job in Runtime(state/'runtime.sqlite').status():
        if job['job_id']!=requested_job and normalized & {normalize(k) for k in job['work_keys']}:
            raise ValueError('work already claimed by '+job['job_id'])

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--state-root',type=Path,default=DEFAULT_STATE)
    p.add_argument('--queue',type=Path,default=DEFAULT_QUEUE)
    p.add_argument('action',choices=['status','claim','run','resume','collect','serve','adopt','admit','batch','publish','verify-public','owner'])
    p.add_argument('--json',action='store_true')
    p.add_argument('--decision',type=Path)
    p.add_argument('--batch-dir',type=Path)
    p.add_argument('--plan',type=Path)
    p.add_argument('--commit')
    p.add_argument('--previous',type=Path)
    p.add_argument('--max-jobs',type=int,default=3)
    p.add_argument('--poll-seconds',type=float,default=10)
    p.add_argument('--threshold',type=int,default=25)
    p.add_argument('--set-owner')
    p.add_argument('--expected-owner')
    args,rest=p.parse_known_args()
    runtime=Path(__file__).with_name('corpus_runtime.py')
    db=args.state_root/'runtime.sqlite'
    if args.action in ('claim','run','resume','collect','adopt'):
        if args.action=='claim':
            with controller_lock(args.state_root):
                check_claim(args.queue,args.state_root,rest)
                return subprocess.call([sys.executable,str(runtime),'--db',str(db),args.action,*rest])
        return subprocess.call([sys.executable,str(runtime),'--db',str(db),args.action,*rest])
    if rest: p.error('unrecognized arguments: '+' '.join(rest))
    if args.action=='serve':
        from corpus_runtime import Runtime
        if not 1<=args.max_jobs<=3: raise ValueError('initial effective capacity must be 1..3')
        rt=Runtime(db)
        while True:
            rows=rt.collect()
            capacity=args.max_jobs-sum(x['state'] in ('running','starting','orphan_running') for x in rows)
            for row in rows:
                if capacity<=0: break
                if row['state']=='queued' or (row['state']=='rate_limited' and row.get('next_attempt_at',0)<=time.time()):
                    rt.start(row['job_id']);capacity-=1
            summary=corpus_batch.status(args.queue,args.state_root/'batches',args.threshold)
            if summary['status']=='batch_ready':
                try:
                    with controller_lock(args.state_root):
                        frozen=corpus_batch.prepare(args.queue,args.state_root/'batches',args.threshold,B)
                        if frozen['status']!='waiting_for_admissions':
                            blocked=args.state_root/'batch-blocked.json'
                            if not blocked.exists() or load(blocked).get('batch_id')!=frozen['batch_id']:
                                try:
                                    corpus_batch.merge(Path(frozen['batch_dir']))
                                    save(args.state_root/'pending-publication.json',{'batch_dir':frozen['batch_dir'],'status':'merged_pending_controller_publish'})
                                except Exception as e:
                                    save(blocked,{'batch_id':frozen['batch_id'],'error':str(e),'next_action':'reconcile preserved batch output before a reviewed revision'})
                except BlockingIOError:
                    pass
            time.sleep(max(1,args.poll_seconds))
    elif args.action=='status':
        r=subprocess.run([sys.executable,str(runtime),'--db',str(db),'status'],capture_output=True,text=True)
        if r.returncode: raise RuntimeError(r.stderr.strip())
        result={'production':corpus_batch.status(args.queue,args.state_root/'batches',args.threshold),
                'jobs':json.loads(r.stdout),
                'controller':load(args.state_root/'owner.json') if (args.state_root/'owner.json').exists() else {'owner':'current-session','dot_connection_verified':False},
                'pending_publication':load(args.state_root/'pending-publication.json') if (args.state_root/'pending-publication.json').exists() else None}
    else:
        with controller_lock(args.state_root):
            if args.action=='admit':
                if not args.decision: p.error('--decision required')
                result=admit(args.queue,args.decision)
            elif args.action=='batch':
                result=corpus_batch.prepare(args.queue,args.state_root/'batches',args.threshold,B)
                if result['status']!='waiting_for_admissions':
                    result=corpus_batch.merge(Path(result['batch_dir']))
            elif args.action in ('publish','verify-public'):
                if not args.batch_dir: p.error('--batch-dir required')
                if args.action=='publish': result=corpus_batch.publish(args.batch_dir,args.plan)
                else:
                    if not args.plan and (not args.commit or not args.previous): p.error('--commit and --previous required')
                    result=corpus_batch.verify_public(args.batch_dir,args.plan,args.commit,args.previous)
            else:
                target=args.state_root/'owner.json'
                old=load(target) if target.exists() else {'owner':'current-session'}
                if not args.set_owner: result=old
                else:
                    if args.expected_owner!=old['owner']: raise ValueError('owner changed; reconcile before handoff')
                    result={'owner':args.set_owner,'previous_owner':old['owner'],'updated_at':datetime.now(timezone.utc).isoformat()}
                    save(target,result)
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0

if __name__=='__main__':
    try: raise SystemExit(main())
    except (ValueError,RuntimeError,BlockingIOError) as e:
        print(json.dumps({'status':'action_required','error':str(e)},ensure_ascii=False),file=sys.stderr)
        raise SystemExit(2)
