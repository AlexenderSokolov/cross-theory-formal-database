"""Frozen production batches; existing gates and root decisions remain authoritative."""
from __future__ import annotations
import argparse, copy, json, os, subprocess, sys, fcntl, tempfile
from datetime import datetime, timezone
from contextlib import contextmanager, nullcontext
from pathlib import Path
import merge_editable_batch as merger
from corpus_delivery_tools import load, dump, check_report

DEFAULT_ROOT = Path('/disks/sata1/yupeng/human-proof-corpus')

def atomic_save(path, data):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.NamedTemporaryFile(mode='w',encoding='utf-8',dir=path.parent,delete=False) as stream:
        json.dump(data,stream,ensure_ascii=False,indent=2);stream.write('\n');temporary=stream.name
    os.replace(temporary,path)

def mutation_guard(state, actor):
    if not (Path(state)/'owner.json').exists():
        # Internal isolated fixtures do not attach a production controller.
        return nullcontext()
    from corpus_control_protocol import controller_guard
    return controller_guard(state,(actor or {}).get('owner'),(actor or {}).get('generation'))

def safe(path, root):
    p=Path(path).absolute(); root=Path(root).resolve()
    if not p.resolve().is_relative_to(root) or p.is_symlink():
        raise ValueError('path outside production root or symlink: '+str(p))
    return p

def status(queue, state_root=None, threshold=25):
    q=load(Path(queue)); b=q['base']; rows=q['queued_new_root_admitted']
    if threshold < 1: raise ValueError('positive threshold required')
    ids=[str(r['problem_id']) for r in rows]
    if len(set(ids))!=len(ids): raise ValueError('duplicate queued ID')
    if any(r.get('state')!='root_admitted_waiting_batch' or r.get('final_revision_frozen') is not True for r in rows):
        raise ValueError('queue contains unadmitted/unfrozen row')
    local=int(b['local_count']); remote=int(b['remote_main_count'])
    if remote>local: raise ValueError('remote exceeds local base')
    size=min(int(q.get('batch_size',threshold)),max(0,30000-remote))
    active=q.get('active_batch');blocked=bool(active) or local>remote
    available=len(rows)
    expected=active['expected_count'] if active and 'expected_count' in active else remote+size
    return dict(status='goal_reached' if remote==30000 and not active else ('pending_publication' if blocked else ('batch_ready' if available>=size and rows else 'waiting_for_admissions')),
                local_count=local,remote_count=remote,queued_new_count=len(rows),
                available_release_increment=available,threshold=threshold,
                remaining=max(0,size-available),expected_count=expected,incoming_ids=ids[:size],
                pending_remote_already_merged_local=local-remote,pending_publication=active,
                batch_size=size,next_public_target=remote+size)

def selected_paths(root):
    # Paths only. No directory digest/filemap; existing merger checks declared bytes.
    from prepare_editable_release import public_path
    names=[]
    for p in sorted(root.rglob('*')):
        if p.is_symlink(): raise ValueError('symlink in final package')
        if not p.is_file(): continue
        rel=p.relative_to(root).as_posix()
        if '__pycache__' in p.parts or rel.endswith('.sqlite.tmp'): continue
        public_path(rel)
        names.append(rel)
    return names

def entry(row, project, incoming=False):
    p=safe(row['package'],project); b=safe(row['build_root'],project); r=safe(row['receipt_root'],project)
    m=load(p/'manifest.json'); e=load(p/'delivery-evidence.json')
    identity=e.get('package_manifest_sha256')
    if not identity: identity=merger.core.sha(p/'manifest.json')  # Existing interface binding only.
    result=dict(package=str(p),build_root=str(b),receipt_root=str(r),manifest_sha256=identity,
                paths=selected_paths(p),artifact_paths={'build':[],'receipts':[]})
    for item in m['items']:
        ident=item['problem_id']; receipt=load(r/(ident+'.json'))
        result['artifact_paths']['receipts'].append(ident+'.json')
        # Keep declared PDF/log and ordinary auxiliary outputs; exclude runtime caches.
        for f in sorted((b/ident).iterdir()):
            if f.is_file() and (f.suffix in ('.pdf','.log','.fls','.aux','.out') or f.name=='compiler.log'):
                result['artifact_paths']['build'].append(f.relative_to(b).as_posix())
        for key in ('pdf_path','compiler_log_path'):
            if receipt[key] not in result['artifact_paths']['build']: raise ValueError('missing declared build artifact')
    if incoming:
        ready=load(safe(row['owner_final_ready'],project))
        # Root row is admission; READY may correctly retain its prior pending wording.
        ids={i['problem_id'] for i in m['items']}
        if ids!={str(row['problem_id'])}: raise ValueError('queue row packet ID mismatch')
        for field in ('package','build_root','receipt_root'):
            if field in ready and Path(ready[field]).resolve()!=Path(result[field]).resolve():
                raise ValueError('READY final root mismatch: '+field)
        if ready.get('manifest_sha256') and ready['manifest_sha256']!=identity:
            raise ValueError('READY final manifest mismatch')
        report=safe(row['accepted_report'],project)
        result['accepted_report']={'path':str(report),'manifest_sha256':identity}
        merger.accepted_reports(result,(m,e))
    return result

def prepare(queue, state_root, threshold=25, project=DEFAULT_ROOT):
    summary=status(queue,state_root,threshold)
    q=load(Path(queue)); project=Path(project).resolve(); state=safe(state_root,project)
    active=q.get('active_batch')
    if not active:
        if summary['status']!='batch_ready': return summary
        name='batch-'+str(summary['local_count'])+'-'+str(summary['expected_count'])+'-r'+str(q.get('batch_revision',1)).zfill(3)
        folder=state/name
        active=dict(batch_id=name,batch_dir=str(folder),frozen_base=copy.deepcopy(q['base']),
                    expected_count=summary['expected_count'],incoming_ids=summary['incoming_ids'],created_at=datetime.now(timezone.utc).isoformat())
        q['active_batch']=active;q.setdefault('last_publication',None)
        atomic_save(queue,q)  # Frozen intent precedes output/spec mutation.
    else:
        folder=safe(active['batch_dir'],project);name=active['batch_id']
        if folder.parent.resolve()!=state.resolve():raise ValueError('active batch outside fixed state root')
        if int(q['base']['local_count'])!=int(active['frozen_base']['local_count']):return summary
        if (folder/'merge/batch-result.json').exists():return summary
    if (folder/'batch.json').exists():
        frozen=load(folder/'batch.json')
        if frozen['incoming_ids']!=active['incoming_ids'] or frozen['local_count']!=active['frozen_base']['local_count']:
            raise ValueError('frozen batch identity conflict')
        return frozen
    wanted=active['incoming_ids'];by_id={row['problem_id']:row for row in q['queued_new_root_admitted']}
    if any(ident not in by_id for ident in wanted):raise ValueError('frozen admission missing; preserve active batch')
    rows=[by_id[ident] for ident in wanted]
    base=entry(active['frozen_base'],project)
    incoming=[entry(row,project,True) for row in rows]
    decisions=[]
    for row in rows:
        decisions.append({k:row[k] for k in ('problem_id','accepted_H','difficulty_reason','material_basis','semantic_basis')})
    spec=dict(schema_version=1,base=base,incoming=incoming,master_helpers=str(project/'repo/editable-corpus'))
    review=dict(schema_version=1,status='material_review_complete',holds=[],duplicates=[],
                base_manifest_sha256=base['manifest_sha256'],incoming_manifest_sha256=[x['manifest_sha256'] for x in incoming],
                incoming_ids=wanted,basis=json.dumps(decisions,ensure_ascii=False),
                compile_reuse_basis='Frozen root-admitted queue rows and their final READY, accepted item reports and unchanged declared compile receipts are reused; no new per-item gate or compilation.')
    folder.mkdir(parents=True,exist_ok=True)
    atomic_save(folder/'spec.json',spec);atomic_save(folder/'material-review.json',review)
    frozen=dict(summary,status='prepared_frozen_batch',batch_id=name,batch_dir=str(folder),
                local_count=active['frozen_base']['local_count'],remote_count=active['frozen_base']['remote_main_count'],
                expected_count=active['expected_count'],incoming_ids=wanted,frozen_base=active['frozen_base'],
                spec=str(folder/'spec.json'),review=str(folder/'material-review.json'),output=str(folder/'merge'),queue=str(Path(queue).resolve()))
    atomic_save(folder/'batch.json',frozen);return frozen

def merge(batch_dir,actor=None):
    folder=Path(batch_dir)
    with mutation_guard(folder.parent.parent,actor):pass
    with (folder/'merge.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        with mutation_guard(folder.parent.parent,actor):pass
        return _merge(batch_dir,actor)

def _merge(batch_dir,actor=None):
    folder=Path(batch_dir);frozen=load(folder/'batch.json');output=Path(frozen['output'])
    receipt=output/'batch-result.json'
    if receipt.exists():
        result=load(receipt)
        if result.get('status')=='actual_editable_batch_gate_passed_not_remote' and result.get('items')==frozen['expected_count']:
            update_queue(folder,result,actor=actor)
            return result
        raise ValueError('previous failed/partial batch retained; choose reviewed new revision')
    q=load(Path(frozen['queue']));active=q.get('active_batch')
    if not active or active['batch_id']!=frozen['batch_id']:raise ValueError('different or absent active batch')
    if q['base']['local_count']!=frozen['local_count']:raise ValueError('queue base changed before merge')
    if output.exists(): raise ValueError('partial output retained; no implicit restart')
    result=merger.merge_batch(Path(frozen['spec']),Path(frozen['review']),None,output)
    update_queue(folder,result,actor=actor)
    return result

@contextmanager
def controller_lock(project=DEFAULT_ROOT):
    path=Path(project)/'operations/corpusctl/controller.lock'
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('a') as stream:
        fcntl.flock(stream,fcntl.LOCK_EX)
        try: yield
        finally: fcntl.flock(stream,fcntl.LOCK_UN)

def recover_active_batch(queue,state_root):
    q=load(Path(queue))
    if q.get('active_batch'):return q['active_batch']
    if int(q['base']['local_count'])==int(q['base']['remote_main_count']):return None
    matches=[]
    for path in Path(state_root).glob('*/batch.json'):
        frozen=load(path);receipt=Path(frozen['output'])/'batch-result.json'
        if not receipt.exists():continue
        result=load(receipt)
        if result.get('status')=='actual_editable_batch_gate_passed_not_remote' and result.get('items')==q['base']['local_count'] and Path(result['package']).resolve()==Path(q['base']['package']).resolve() and frozen['remote_count']==q['base']['remote_main_count']:
            base=frozen.get('frozen_base') or load(Path(frozen['spec']))['base']
            if 'local_count' not in base:base=dict(base,local_count=frozen['local_count'],remote_main_count=frozen['remote_count'],accepted_report=q['base']['accepted_report'])
            matches.append(dict(batch_id=frozen['batch_id'],batch_dir=str(path.parent),frozen_base=base,expected_count=frozen['expected_count'],incoming_ids=frozen['incoming_ids'],created_at=datetime.now(timezone.utc).isoformat()))
    if len(matches)!=1:raise ValueError('pending merge must have unique actual receipt; needs_recovery')
    q['active_batch']=matches[0];atomic_save(queue,q);return matches[0]

def update_queue(batch_dir, result, remote=False,actor=None):
    with mutation_guard(Path(batch_dir).parent.parent,actor):
        return _update_queue(batch_dir,result,remote)

def _update_queue(batch_dir, result, remote=False):
    frozen=load(Path(batch_dir)/'batch.json');path=Path(frozen['queue']);q=load(path)
    old=q['base'];target=frozen['expected_count']
    active=q.get('active_batch');last=q.get('last_publication')
    if int(old['local_count'])>target or int(old['remote_main_count'])>target:raise ValueError('stale batch callback; preserve newer queue')
    if not active:
        if last and last['batch_id']==frozen['batch_id'] and last['count']==target:
            if remote and last['commit']!=result.get('verified_corpus_commit',result.get('commit')):raise ValueError('different public commit for completed batch')
            return q
        raise ValueError('different or absent active batch; reconcile actual receipt first')
    if active['batch_id']!=frozen['batch_id'] or active['incoming_ids']!=frozen['incoming_ids']:raise ValueError('different active batch; preserve pointer')
    if remote:
        if int(old['local_count'])!=target: raise ValueError('public result differs from local queue')
        if result.get('remote_main_delivered_count',result.get('verified_count'))!=target:raise ValueError('public result count mismatch')
        old['remote_main_count']=target
        q['remote_main_count']=target
        q['last_publication']=dict(batch_id=frozen['batch_id'],commit=result.get('verified_corpus_commit',result.get('commit')),count=target,result_path=str(Path(batch_dir)/'verify-public/result.json'))
        publication_path=Path(batch_dir)/'publication.json'
        if publication_path.exists():
            publication=load(publication_path)
            if publication['batch_id']!=frozen['batch_id'] or publication['target_commit']!=q['last_publication']['commit'] or publication['expected_count']!=target:
                raise ValueError('different publication identity at reconciliation')
            publication['receipt_paths']['public_result']=q['last_publication']['result_path']
            publication['stage']='reconciled'
            atomic_save(publication_path,publication)
        elif (Path(batch_dir).parent.parent/'owner.json').exists():raise ValueError('publication identity missing before queue reconciliation')
        q['active_batch']=None
    else:
        consumed=set(frozen['incoming_ids'])
        if int(old['local_count'])==target:
            if Path(old['package']).resolve()!=Path(result['package']).resolve(): raise ValueError('queue already advanced through different batch')
        elif int(old['local_count'])!=frozen['local_count']:
            raise ValueError('queue base changed; frozen batch cannot be applied')
        else:
            old.update(package=result['package'],build_root=result['build_root'],receipt_root=result['receipt_root'],
                       accepted_report=result['actual_aggregate']['report'],local_count=target)
        q['queued_new_root_admitted']=[row for row in q['queued_new_root_admitted'] if str(row['problem_id']) not in consumed]
        q['local_merged_count']=target
    q['queued_new_count']=len(q['queued_new_root_admitted'])
    q['pending_remote_already_merged_local']=int(old['local_count'])-int(old['remote_main_count'])
    q['new_root_admitted_total_before_merge']=int(old['local_count'])+q['queued_new_count']
    q['remaining_new_root_admissions_for_first_release']=max(0,min(q.get('batch_size',25),30000-int(old['remote_main_count']))-q['queued_new_count'])
    atomic_save(path,q)
    pending_path=Path(batch_dir).parent.parent/'pending-publication.json'
    pointer=dict(batch_dir=str(Path(batch_dir).resolve()),status='delivered' if remote else 'merged_pending_controller_publish',count=target)
    if remote: pointer['commit']=result.get('verified_corpus_commit',result.get('commit'))
    atomic_save(pending_path,pointer)
    return q

def publish_plan(batch_dir, project=DEFAULT_ROOT):
    """Convert already admitted/merged material to the existing release helper contract."""
    from prepare_editable_release import HELPERS, TRANSPORT_NAMES, public_path
    folder=Path(batch_dir);frozen=load(folder/'batch.json');result=load(Path(frozen['output'])/'batch-result.json')
    package=Path(result['package']);build=Path(result['build_root']);receipts=Path(result['receipt_root']);master=Path(project)/'repo/editable-corpus'
    review_path=folder/'public-review.json';plan_path=folder/'publish-plan.json'
    if plan_path.exists(): return plan_path
    publication=load(folder/'publication.json')
    previous=Path(publication['previous_public_result'])
    incoming_ids=set(frozen['incoming_ids'])
    files=[];filemap={}
    for name in selected_paths(package):
        filemap[name]=merger.core.sha(package/name)
        if Path(name).parts[0] in ('database-parts','validation-artifact-parts','validation-artifact-deltas') or name in TRANSPORT_NAMES or name in HELPERS or name in ('validation-chain.json','RECOVERY_CURRENT.md'):
            continue
        files.append(dict(root='package',path=name,sha256=filemap[name]))
    for name in HELPERS:
        files.append(dict(root='master_helpers',path=name,sha256=merger.core.sha(master/name)))
    for root,kind in ((build,'build'),(receipts,'receipts')):
        for path in sorted(root.rglob('*')):
            if not path.is_file(): continue
            name=path.relative_to(root).as_posix()
            if (Path(name).parts[0] if kind=='build' else path.stem) not in incoming_ids:continue
            if kind=='build' and (len(Path(name).parts)!=2 or path.suffix not in ('.pdf','.log','.fls','.aux','.out')): continue
            if kind=='receipts' and len(Path(name).parts)!=1: continue
            public_path(name);files.append(dict(root=kind,path=name,sha256=merger.core.sha(path)))
    aggregate=Path(result['actual_aggregate']['report']);aggregate_identity=merger.core.sha(aggregate)
    review=dict(schema_version=1,status='public_filelist_review_complete',
                package_manifest_sha256=merger.core.sha(package/'manifest.json'),aggregate_report_sha256=aggregate_identity,
                reviewed_package_filemap=filemap,master_helper_sha256={n:merger.core.sha(master/n) for n in HELPERS},files=files,
                basis='Inherited frozen root-admitted queue decisions and existing public base; exact package material and compile artifacts only; no private caches or upstream scripts.')
    dump(review_path,review)
    out=folder/'release';argv=[str(Path(project)/'runtime/python/bin/python'),'-B',str(Path(project)/'repo/corpus-work/scripts/prepare_editable_release.py'),
        '--package',str(package),'--build-root',str(build),'--receipt-root',str(receipts),
        '--aggregate-report',str(aggregate),'--aggregate-report-sha256',aggregate_identity,
        '--public-filelist',str(review_path),'--public-filelist-sha256',merger.core.sha(review_path),'--output',str(out),
        '--previous-public',str(previous),'--incoming-ids',*frozen['incoming_ids']]
    dump(plan_path,dict(stage='publish',batch_id=frozen['batch_id'],expected_count=frozen['expected_count'],
                       commands=[dict(argv=argv)],preparation_report=str(out/'release-preparation.json')))
    return plan_path

def public_plan(batch_dir, commit, previous, project=DEFAULT_ROOT):
    """Previous recovery descriptors are fixed receipts, not manually authored commands."""
    folder=Path(batch_dir);frozen=load(folder/'batch.json');old=load(Path(previous));py=str(Path(project)/'runtime/python/bin/python')
    plan_path=folder/'verify-public-plan.json'
    if plan_path.exists():
        if load(plan_path).get('commit')!=commit: raise ValueError('public revision already frozen')
        return plan_path
    release_result=load(folder/'publish/result.json')
    release=Path(release_result.get('release_root',str(folder/'release')))
    prepared=load(release/'release-preparation.json')
    filelist=release/'PUBLIC_FILELIST.json';transport=folder/'public';package=transport/'package';artifacts=transport/'artifacts';report=transport/'aggregate.json'
    commands=[dict(argv=['bash',str(Path(project)/'repo/corpus-work/run_public_transport.sh'),
        '--commit',commit,'--filelist',str(filelist),'--filelist-sha256',merger.core.sha(filelist),
        '--cache',old['cache'],'--old-filelist',old['filelist'],'--old-filelist-sha256',merger.core.sha(Path(old['filelist'])),
        '--old-public-proof',old['public_proof'],'--old-public-proof-sha256',merger.core.sha(Path(old['public_proof'])),
        '--old-commit',old['commit'],'--output',str(transport)])]
    commands.extend(dict(argv=[py,'-B',str(package/name)]) for name in ('restore_database.py','test_restore_database.py','test_database.py'))
    if (release/'package/validation-chain.json').exists():
        artifact_args=['--chain',str(package/'validation-chain.json'),'--expected-chain-sha256',prepared['validation_chain_sha256'],
                       '--schema1-helper',str(package/'restore_validation_artifacts.py'),'--expected-helper-sha256',prepared['schema1_restore_helper_sha256'],'--output',str(artifacts)]
        for ident,rel in prepared['artifact_archive_roots'].items():artifact_args.extend(['--archive-root',ident+'='+str(package/rel)])
        commands.append(dict(argv=[py,'-B',str(package/'resume_validation_chain.py'),*artifact_args]))
    else:commands.append(dict(argv=[py,'-B',str(package/'restore_validation_artifacts.py'),'--destination',str(artifacts)]))
    commands.append(dict(argv=[py,'-B',str(Path(project)/'repo/corpus-work/scripts/validate_corpus.py'),
        '--mode','editable-delivery','--package',str(package),'--evidence',str(package/'delivery-evidence.json'),
        '--build-root',str(artifacts/'build'),'--receipt-root',str(artifacts/'receipts'),'--report',str(report)]))
    dump(plan_path,dict(stage='verify-public',batch_id=frozen['batch_id'],expected_count=frozen['expected_count'],commit=commit,
                       commands=commands,transport_receipt=str(transport/'TRANSPORT_RECEIPT.json'),transport_root=str(transport),
                       aggregate_report=str(report),restored_receipt_root=str(artifacts/'receipts'),
                       artifacts_result=str(artifacts/'CHAIN_RESTORE_RECEIPT.json'),validation_chain_sha256=prepared.get('validation_chain_sha256'),
                       artifact_archive_roots=prepared.get('artifact_archive_roots')))
    return plan_path

def run_stage_command(stage_dir,n,argv,probe=None,actor=None,state=None,execution_argv=None):
    """Preserve attempts; resume only a terminal, unchanged logical operation."""
    from corpus_runtime import identity, live
    stage_dir=Path(stage_dir);stage_dir.mkdir(parents=True,exist_ok=True)
    receipt=stage_dir/(str(n)+'.json');started=stage_dir/(str(n)+'.started.json')
    old=load(receipt) if receipt.exists() else None
    if old:
        if old['argv']!=argv:raise ValueError('stage command changed')
        if old['exit_code']==0:return old
    launch=load(started) if started.exists() else None
    if launch and launch['argv']!=argv:raise ValueError('stage command changed')
    if launch and live(launch):raise ValueError('stage process still live; do not relaunch')
    if (old or launch) and probe and probe():
        previous=old or launch
        completed=dict(argv=argv,executed_argv=previous.get('executed_argv',argv),exit_code=0,reconciled_output=True,
                       attempt=previous.get('attempt',0),log=previous.get('log',str(stage_dir/(str(n)+'.log'))))
        atomic_save(receipt,completed);return completed
    if launch and not old and not launch.get('pid'):
        raise ValueError('legacy stage process identity missing; needs_recovery before retry')
    attempt=(old.get('attempt',0)+1) if old else (int(launch.get('attempt',0))+1 if launch else 0)
    if old:
        history=stage_dir/(str(n)+'.attempt-'+str(old.get('attempt',0))+'.json')
        if not history.exists():atomic_save(history,old)
    if launch:
        history=stage_dir/(str(n)+'.started-attempt-'+str(launch.get('attempt',0))+'.json')
        if not history.exists():atomic_save(history,launch)
    log_path=stage_dir/(str(n)+'.log' if attempt==0 else str(n)+'.attempt-'+str(attempt)+'.log')
    with mutation_guard(state,actor) if state else nullcontext():
        with log_path.open('w') as log:
            process=subprocess.Popen(execution_argv or argv,shell=False,stdout=log,stderr=subprocess.STDOUT,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
        ident=identity(process.pid)
        atomic_save(started,dict(argv=argv,executed_argv=execution_argv or argv,attempt=attempt,log=str(log_path),status='started_not_completed',pid=process.pid,
                    proc_start=ident['start_time'] if ident else None,proc_cwd=ident['cwd'] if ident else None))
    code=process.wait()
    record=dict(argv=argv,executed_argv=execution_argv or argv,exit_code=code,attempt=attempt,log=str(log_path))
    atomic_save(receipt,record)
    if code:raise ValueError('release stage failed; see '+str(receipt))
    return record

def completed_step(plan,stage,n):
    """Inspect the existing helper output after a lost response, without rerunning it."""
    try:
        if stage=='publish':
            result=load(Path(plan['preparation_report']))
            return result.get('status')=='prepared_editable_release_not_restored_or_remote_verified' and result.get('items')==plan['expected_count']
        root=Path(plan['transport_root']);package=root/'package'
        if n==0:
            result=load(Path(plan['transport_receipt']))
            return result.get('current_commit')==plan['commit'] and result.get('status')=='prepared_exact_public_transport_requires_actual_restore_and_full_gate'
        if n==1:
            descriptor=load(package/'database-delivery.json');sql=package/'corpus.sqlite'
            return sql.exists() and sql.stat().st_size==descriptor['sqlite_bytes'] and merger.core.sha(sql)==descriptor['sqlite_sha256']
        if n==4:
            result=load(Path(plan['artifacts_result']))
            return result.get('status')=='actual_validation_chain_restore_complete_not_qualified_or_remote' and result.get('chain_sha256')==plan['validation_chain_sha256']
        if n==5:
            check_report(Path(plan['aggregate_report']),plan['expected_count'])
            return load(Path(plan['aggregate_report'])).get('receipt_set')==str(Path(plan['restored_receipt_root']).resolve())
    except (OSError,ValueError,KeyError):pass
    return False

def transition(batch_dir, stage, plan_path,actor=None):
    """Run a frozen root-supplied release/recovery command plan, resume completed steps.

    publish plans use run_prepare_release.sh (reviewed public list required).
    verify-public plans use run_public_transport.sh followed by fixed restore and
    final validator commands. Git/bundle transfer remains root-owned.
    """
    folder=Path(batch_dir);frozen=load(folder/'batch.json'); merged=load(Path(frozen['output'])/'batch-result.json')
    if merged.get('status')!='actual_editable_batch_gate_passed_not_remote': raise ValueError('batch has not passed')
    plan=load(Path(plan_path))
    if plan.get('stage')!=stage or plan.get('expected_count')!=frozen['expected_count']:
        raise ValueError('release plan batch/count mismatch')
    if plan.get('batch_id')!=frozen['batch_id']: raise ValueError('release plan batch ID mismatch')
    frozen_plan=folder/(stage+'-plan.json')
    if frozen_plan.exists():
        if load(frozen_plan)!=plan: raise ValueError('stage plan frozen; use new revision')
    else: dump(frozen_plan,plan)
    commands=plan.get('commands')
    if not isinstance(commands,list) or not commands: raise ValueError('explicit command plan required')
    stage_dir=folder/stage;stage_dir.mkdir(exist_ok=True)
    done=stage_dir/'result.json'
    if done.exists(): return load(done)
    preparation_report=Path(plan['preparation_report']) if stage=='publish' and 'preparation_report' in plan else None
    for n,command in enumerate(commands):
        argv=command.get('argv')
        if not isinstance(argv,list) or not argv or any(not isinstance(x,str) for x in argv): raise ValueError('argv list required; shell commands forbidden')
        # Caller supplies reviewed exact helper commands, never shell command strings.
        execution_argv=None;probe_plan=plan
        if stage=='publish' and preparation_report:
            prior=load(stage_dir/(str(n)+'.json')) if (stage_dir/(str(n)+'.json')).exists() else (load(stage_dir/(str(n)+'.started.json')) if (stage_dir/(str(n)+'.started.json')).exists() else None)
            actual=prior.get('executed_argv',argv) if prior else argv
            preparation_report=Path(actual[actual.index('--output')+1])/'release-preparation.json'
            probe_plan=dict(plan,preparation_report=str(preparation_report))
            if prior and prior.get('exit_code')!=0 and not completed_step(probe_plan,stage,n):
                if not prior.get('pid') or not __import__('corpus_runtime').live(prior):
                    attempt=int(prior.get('attempt',0))+1;new_output=folder/('release-attempt-'+str(attempt).zfill(3))
                    execution_argv=list(argv);execution_argv[execution_argv.index('--output')+1]=str(new_output)
                    preparation_report=new_output/'release-preparation.json'
        record=run_stage_command(stage_dir,n,argv,probe=lambda:completed_step(probe_plan,stage,n),actor=actor,state=folder.parent.parent,execution_argv=execution_argv)
        if stage=='publish' and preparation_report:
            actual=record.get('executed_argv',argv);preparation_report=Path(actual[actual.index('--output')+1])/'release-preparation.json'
    if stage=='verify-public':
        commit=plan.get('commit','')
        if len(commit)!=40 or any(c not in '0123456789abcdef' for c in commit): raise ValueError('exact public commit required')
        transport=load(Path(plan['transport_receipt']))
        if transport.get('current_commit')!=commit or transport.get('status')!='prepared_exact_public_transport_requires_actual_restore_and_full_gate':
            raise ValueError('transport does not bind requested commit')
        report=load(Path(plan['aggregate_report']))
        restored_receipts=Path(plan['restored_receipt_root']).resolve()
        if report.get('receipt_set')!=str(restored_receipts): raise ValueError('gate is not the restored public receipt set')
        transport_root=Path(plan['transport_root']).resolve()
        if not restored_receipts.is_relative_to(transport_root): raise ValueError('restored receipt root outside exact public transport')
        gate=check_report(Path(plan['aggregate_report']),frozen['expected_count'])
        from prepare_editable_release import check_sql
        package=transport_root/'package'
        sql=check_sql(package,load(package/'manifest.json'))
        public_filelist=transport_root/'PUBLIC_FILELIST.json'
        files=load(public_filelist)['files']
        actual_commands=[]
        # Five fixed restoration/test/gate commands, excluding the preceding download.
        for index in range(1,len(commands)):
            record=load(stage_dir/(str(index)+'.json'))
            log=Path(record.get('log',str(stage_dir/(str(index)+'.log'))))
            actual_commands.append(dict(argv=record['argv'],returncode=record['exit_code'],
                                        log=str(log.resolve()),log_sha256=merger.core.sha(log)))
        if len(actual_commands)!=5: raise ValueError('public plan requires five actual restoration commands')
        result=dict(status='public_exact_commit_full'+str(frozen['expected_count'])+'_restored_verified',
                    commit=commit,verified_corpus_commit=commit,verified_count=frozen['expected_count'],
                    remote_main_delivered_count=frozen['expected_count'],public_files_verified=len(files),
                    public_filelist_sha256=merger.core.sha(public_filelist),
                    manifest_sha256=merger.core.sha(package/'manifest.json'),sql=sql,commands=actual_commands,
                    actual_gate=gate,remote_count_update_required=True,
                    cache=str(package),filelist=str(public_filelist),public_proof=str(done.resolve()),
                    artifact_archive_roots=plan.get('artifact_archive_roots'),validation_chain_sha256=plan.get('validation_chain_sha256'))
    else:
        if 'preparation_report' in plan:
            prepared=load(preparation_report)
            if prepared.get('status')!='prepared_editable_release_not_restored_or_remote_verified':
                raise ValueError('release preparation helper did not complete')
            if prepared.get('items')!=frozen['expected_count'] or prepared.get('sql',{}).get('problem_count')!=frozen['expected_count']:
                raise ValueError('prepared release count mismatch')
            if prepared.get('input_aggregate',{}).get('actual_qualified_count')!=frozen['expected_count']:
                raise ValueError('preparation does not reuse complete input aggregate')
            result=dict(status='release_prepared_root_publish_pending',verified_count=frozen['expected_count'],
                        reused_merge_aggregate=True,additional_local_restore_performed=False,remote_delivered_increment=0,
                        release_root=str(preparation_report.parent),preparation_report=str(preparation_report))
        else:
            local=load(Path(plan['local_verification_receipt']))
            if local.get('status')!='actual_local_release_SQL_artifacts_tests_fullgate_passed_not_remote':
                raise ValueError('release preparation is not actual local restoration')
            if local.get('sql',{}).get('problem_count')!=frozen['expected_count']: raise ValueError('release restored count mismatch')
            result=dict(status='release_prepared_local_restored_root_publish_pending',verified_count=frozen['expected_count'],remote_delivered_increment=0)
    dump(done,result);return result

def publish(batch_dir, plan_path=None,actor=None): return transition(batch_dir,'publish',plan_path or publish_plan(batch_dir),actor=actor)
def verify_public(batch_dir, plan_path=None, commit=None, previous=None,actor=None):
    result=transition(batch_dir,'verify-public',plan_path or public_plan(batch_dir,commit,previous),actor=actor)
    update_queue(batch_dir,result,remote=True,actor=actor)
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['status','prepare','merge','publish','verify-public'])
    p.add_argument('--queue',type=Path);p.add_argument('--state-root',type=Path);p.add_argument('--batch-dir',type=Path);p.add_argument('--plan',type=Path);p.add_argument('--threshold',type=int,default=25);p.add_argument('--commit');p.add_argument('--previous',type=Path)
    p.add_argument('--controller-id');p.add_argument('--generation',type=int);p.add_argument('--publication-guard')
    a=p.parse_args();actor={'owner':a.controller_id,'generation':a.generation}
    state=a.state_root.parent if a.state_root else (a.batch_dir.parent.parent if a.batch_dir else DEFAULT_ROOT/'operations/corpusctl')
    if a.action=='status':
        if not a.queue or not a.state_root: p.error('--queue and --state-root required')
        result=status(a.queue,a.state_root,a.threshold)
    else:
        from corpus_control_protocol import controller_guard,publication_guard,assert_publication_guard
        if not a.controller_id or a.generation is None:p.error('explicit --controller-id and --generation required for mutation')
        if a.action=='prepare':
            if not a.queue or not a.state_root:p.error('--queue and --state-root required')
            with controller_guard(state,actor):result=prepare(a.queue,a.state_root,a.threshold)
        elif a.action=='merge':result=merge(a.batch_dir,actor=actor)
        else:
            if a.publication_guard:
                assert_publication_guard(state,a.publication_guard);guard=nullcontext()
            else:guard=publication_guard(state)
            with guard:
                with controller_guard(state,actor):pass
                result=publish(a.batch_dir,a.plan,actor=actor) if a.action=='publish' else verify_public(a.batch_dir,a.plan,a.commit,a.previous,actor=actor)
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':
    main()
