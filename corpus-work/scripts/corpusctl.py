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
from corpus_control_protocol import controller_guard, publication_guard, require_owner, transfer_owner, assert_publication_guard, load_json, save_json

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

def controller_lock(state,controller_id,generation=None):
    return controller_guard(state,controller_id,generation)

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
    previous=argv[argv.index('--previous-job-id')+1] if '--previous-job-id' in argv else None
    def normalize(k):return 'id:'+k if k.isdecimal() else k.lower()
    normalized={normalize(k) for k in keys}
    for job in Runtime(state/'runtime.sqlite',readonly=True).status():
        if job['job_id'] not in (requested_job,previous) and normalized & {normalize(k) for k in job['work_keys']}:
            raise ValueError('work already claimed by '+job['job_id'])

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--state-root',type=Path,default=DEFAULT_STATE);p.add_argument('--queue',type=Path,default=DEFAULT_QUEUE)
    p.add_argument('--controller-id');p.add_argument('--generation',type=int)
    p.add_argument('action',choices=['status','claim','revise','run','resume','collect','serve','adopt','admit','batch','publish','verify-public','owner','import-handoff'])
    p.add_argument('--json',action='store_true');p.add_argument('--decision',type=Path);p.add_argument('--batch-dir',type=Path);p.add_argument('--plan',type=Path);p.add_argument('--commit');p.add_argument('--previous',type=Path)
    p.add_argument('--max-jobs',type=int,default=3);p.add_argument('--poll-seconds',type=float,default=10);p.add_argument('--threshold',type=int,default=25)
    p.add_argument('--set-owner');p.add_argument('--expected-owner');p.add_argument('--expected-generation',type=int)
    p.add_argument('--handoff',type=Path);p.add_argument('--spec',type=Path);p.add_argument('--job-id');p.add_argument('--pid',type=int);p.add_argument('--proc-start');p.add_argument('--exit-record');p.add_argument('--publication-guard')
    args=p.parse_args();actor={'owner':args.controller_id,'generation':args.generation}
    from corpus_runtime import Runtime
    db=args.state_root/'runtime.sqlite'
    if args.action=='status':
        result={'production':corpus_batch.status(args.queue,args.state_root/'batches',args.threshold),'jobs':Runtime(db,readonly=True).status(),'controller':load(args.state_root/'owner.json') if (args.state_root/'owner.json').exists() else None,'pending_publication':load(args.state_root/'pending-publication.json') if (args.state_root/'pending-publication.json').exists() else None}
    elif args.action=='owner':
        if not args.set_owner:result=load(args.state_root/'owner.json') if (args.state_root/'owner.json').exists() else {'owner':'current-session','generation':0}
        else:
            if args.controller_id!=args.set_owner:raise ValueError('new actor owner must equal --set-owner')
            if args.expected_generation is None:raise ValueError('--expected-generation required')
            if args.generation!=args.expected_generation+1:raise ValueError('new actor generation must equal previous+1')
            result=transfer_owner(args.state_root,args.expected_owner,args.expected_generation,args.set_owner)
    else:
        require_owner(args.state_root,actor)
        if args.action=='import-handoff':
            if not args.handoff:p.error('--handoff required')
            result=Runtime(db,args.controller_id,args.generation).import_reference(args.handoff)
        elif args.action in ('claim','revise','adopt'):
            if not args.spec:p.error('--spec required')
            spec=load(args.spec)
            with controller_guard(args.state_root,actor):
                rt=Runtime(db,args.controller_id,args.generation)
                keys=spec['work_keys'];check_claim(args.queue,args.state_root,['--job-id',spec['job_id']]+(['--previous-job-id',spec['previous_job_id']] if spec.get('previous_job_id') else [])+[v for k in keys for v in ('--work-key',k)])
                result=rt.register(spec)
                if args.action=='adopt':
                    if args.pid is None:p.error('--pid required')
                    result=rt.adopt(spec['job_id'],args.pid,args.proc_start,args.exit_record)
        elif args.action in ('run','resume','collect'):
            rt=Runtime(db,args.controller_id,args.generation)
            if args.action!='collect' and not args.job_id:p.error('--job-id required')
            result=getattr(rt,'start' if args.action=='run' else args.action)(args.job_id)
        elif args.action=='admit':
            if not args.decision:p.error('--decision required')
            with controller_guard(args.state_root,actor):
                holdpath=args.state_root/'source-holds.json'
                if holdpath.exists() and str(load(args.decision)['problem_id']) in load(holdpath):raise ValueError('source hold remains; explicit new source-based resolution required')
                result=admit(args.queue,args.decision)
        elif args.action=='batch':
            with controller_guard(args.state_root,actor):
                if load(args.queue)['base']['local_count']>load(args.queue)['base']['remote_main_count'] and not load(args.queue).get('active_batch'):corpus_batch.recover_active_batch(args.queue,args.state_root/'batches')
                result=corpus_batch.prepare(args.queue,args.state_root/'batches',args.threshold,B)
            if result['status']=='prepared_frozen_batch':result=corpus_batch.merge(Path(result['batch_dir']),actor=actor)
        elif args.action in ('publish','verify-public'):
            if not args.batch_dir:p.error('--batch-dir required')
            if args.publication_guard:
                assert_publication_guard(args.state_root,args.publication_guard);guard=contextlib.nullcontext()
            else:guard=publication_guard(args.state_root)
            with guard:
                with controller_guard(args.state_root,actor):pass
                if args.action=='publish':result=corpus_batch.publish(args.batch_dir,args.plan,actor=actor)
                else:result=corpus_batch.verify_public(args.batch_dir,args.plan,args.commit,args.previous,actor=actor)
        else:
            if not 1<=args.max_jobs<=8:raise ValueError('worker slots must be1..8; initial approved capacity3')
            rt=Runtime(db,args.controller_id,args.generation)
            while True:
                with controller_guard(args.state_root,actor):
                    rows=rt.collect();q=load(args.queue)
                    if q['base']['remote_main_count']>=30000: return 0
                    backlog=sum(sum(u['disposition']=='ready_for_review' for u in load(row['job_spec']['result_path'])['units']) for row in rows if row['result_status'] and row.get('job_spec') and Path(row['job_spec']['result_path']).is_file())
                    admitted={str(x['problem_id']) for x in q['queued_new_root_admitted']};merged={str(x['problem_id']) for x in load(Path(q['base']['package'])/'manifest.json')['items']}
                    pending=set()
                    for row in rows:
                        if row.get('result_status') and row.get('job_spec'):
                            pending.update(u['problem_id'] for u in load(row['job_spec']['result_path'])['units'] if u['disposition']=='ready_for_review')
                    rt.schedule(len(pending-admitted-merged));rows=rt.status()
                    capacity=args.max_jobs-sum(r['state'] in ('running','starting','orphan_running') or r['child_live'] for r in rows)
                    for row in rows:
                        if capacity<=0:break
                        if row['state'] in ('claimed','queued'):
                            require_owner(args.state_root,actor);rt.start(row['job_id'],args.max_jobs);capacity-=1
                    frozen=None
                    if q['base']['local_count']>q['base']['remote_main_count'] and not q.get('active_batch'):
                        corpus_batch.recover_active_batch(args.queue,args.state_root/'batches');q=load(args.queue)
                    active=q.get('active_batch')
                    resume_frozen=bool(active and active.get('frozen_base') and q['base']['local_count']==active['frozen_base']['local_count'] and not (Path(active['batch_dir'])/'merge/batch-result.json').exists())
                    if resume_frozen or corpus_batch.status(args.queue,args.state_root/'batches',args.threshold)['status']=='batch_ready':frozen=corpus_batch.prepare(args.queue,args.state_root/'batches',args.threshold,B)
                if frozen and frozen['status']=='prepared_frozen_batch':corpus_batch.merge(Path(frozen['batch_dir']),actor=actor)
                time.sleep(max(1,args.poll_seconds))
    print(json.dumps(result,ensure_ascii=False,indent=2));return 0

if __name__=='__main__':
    try:raise SystemExit(main())
    except (ValueError,RuntimeError,BlockingIOError) as e:
        print(json.dumps({'status':'action_required','error':str(e)},ensure_ascii=False),file=sys.stderr);raise SystemExit(2)
