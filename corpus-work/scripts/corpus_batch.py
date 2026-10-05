"""Frozen production batches; existing gates and root decisions remain authoritative."""
from __future__ import annotations
import argparse, json, os, subprocess, sys, fcntl
from contextlib import contextmanager
from pathlib import Path
import merge_editable_batch as merger
from corpus_delivery_tools import load, dump, check_report

DEFAULT_ROOT = Path('/disks/sata1/yupeng/human-proof-corpus')

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
    available=local-remote+len(rows)
    return dict(status='batch_ready' if available>=threshold and rows else 'waiting_for_admissions',
                local_count=local,remote_count=remote,queued_new_count=len(rows),
                available_release_increment=available,threshold=threshold,
                remaining=max(0,threshold-available),expected_count=local+len(rows),incoming_ids=ids)

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
    if summary['status']!='batch_ready': return summary
    q=load(Path(queue)); project=Path(project).resolve(); state=safe(state_root,project)
    name='batch-'+str(summary['local_count'])+'-'+ '-'.join(summary['incoming_ids'])
    folder=state/name
    if folder.exists():
        frozen=load(folder/'batch.json')
        if frozen['incoming_ids']!=summary['incoming_ids'] or frozen['local_count']!=summary['local_count']:
            raise ValueError('frozen batch identity conflict')
        return frozen
    base=entry(q['base'],project)
    incoming=[entry(row,project,True) for row in q['queued_new_root_admitted']]
    decisions=[]
    for row in q['queued_new_root_admitted']:
        decisions.append({k:row[k] for k in ('problem_id','accepted_H','difficulty_reason','material_basis','semantic_basis')})
    spec=dict(schema_version=1,base=base,incoming=incoming,master_helpers=str(project/'repo/editable-corpus'))
    review=dict(schema_version=1,status='material_review_complete',holds=[],duplicates=[],
                base_manifest_sha256=base['manifest_sha256'],incoming_manifest_sha256=[x['manifest_sha256'] for x in incoming],
                incoming_ids=summary['incoming_ids'],basis=json.dumps(decisions,ensure_ascii=False),
                compile_reuse_basis='Frozen root-admitted queue rows and their final READY, accepted item reports and unchanged declared compile receipts are reused; no new per-item gate or compilation.')
    folder.mkdir(parents=True,exist_ok=False)
    dump(folder/'spec.json',spec);dump(folder/'material-review.json',review)
    frozen=dict(summary,status='prepared_frozen_batch',batch_id=name,batch_dir=str(folder),
                spec=str(folder/'spec.json'),review=str(folder/'material-review.json'),output=str(folder/'merge'),queue=str(Path(queue).resolve()))
    dump(folder/'batch.json',frozen);return frozen

def merge(batch_dir):
    folder=Path(batch_dir);frozen=load(folder/'batch.json');output=Path(frozen['output'])
    receipt=output/'batch-result.json'
    if receipt.exists():
        result=load(receipt)
        if result.get('status')=='actual_editable_batch_gate_passed_not_remote' and result.get('items')==frozen['expected_count']:
            update_queue(folder,result)
            return result
        raise ValueError('previous failed/partial batch retained; choose reviewed new revision')
    if output.exists(): raise ValueError('partial output retained; no implicit restart')
    result=merger.merge_batch(Path(frozen['spec']),Path(frozen['review']),None,output)
    update_queue(folder,result)
    return result

@contextmanager
def controller_lock(project=DEFAULT_ROOT):
    path=Path(project)/'operations/corpusctl/controller.lock'
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('a') as stream:
        fcntl.flock(stream,fcntl.LOCK_EX)
        try: yield
        finally: fcntl.flock(stream,fcntl.LOCK_UN)

def update_queue(batch_dir, result, remote=False):
    frozen=load(Path(batch_dir)/'batch.json');path=Path(frozen['queue']);q=load(path)
    old=q['base'];target=frozen['expected_count']
    if remote:
        if int(old['local_count'])<target: raise ValueError('public result ahead of local queue')
        if int(old['remote_main_count'])>target: return q
        old['remote_main_count']=target
        q['remote_main_count']=target
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
    q['remaining_new_root_admissions_for_first_release']=max(0,int(q.get('first_release_target',target))-q['new_root_admitted_total_before_merge'])
    temporary=path.with_name(path.name+'.batch.tmp');dump(temporary,q);os.replace(temporary,path)
    return q

def publish_plan(batch_dir, project=DEFAULT_ROOT):
    """Convert already admitted/merged material to the existing release helper contract."""
    from prepare_editable_release import HELPERS, TRANSPORT_NAMES, public_path
    folder=Path(batch_dir);frozen=load(folder/'batch.json');result=load(Path(frozen['output'])/'batch-result.json')
    package=Path(result['package']);build=Path(result['build_root']);receipts=Path(result['receipt_root']);master=Path(project)/'repo/editable-corpus'
    review_path=folder/'public-review.json';plan_path=folder/'publish-plan.json'
    if plan_path.exists(): return plan_path
    files=[];filemap={}
    for name in selected_paths(package):
        filemap[name]=merger.core.sha(package/name)
        if Path(name).parts[0] in ('database-parts','validation-artifact-parts','validation-artifact-deltas') or name in TRANSPORT_NAMES or name in ('validation-chain.json','restore_validation_chain.py'):
            continue
        files.append(dict(root='package',path=name,sha256=filemap[name]))
    for name in HELPERS:
        if not (package/name).exists(): files.append(dict(root='master_helpers',path=name,sha256=merger.core.sha(master/name)))
    for root,kind in ((build,'build'),(receipts,'receipts')):
        for path in sorted(root.rglob('*')):
            if not path.is_file(): continue
            name=path.relative_to(root).as_posix()
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
        '--public-filelist',str(review_path),'--public-filelist-sha256',merger.core.sha(review_path),'--output',str(out)]
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
    filelist=folder/'release/PUBLIC_FILELIST.json';transport=folder/'public';package=transport/'package';artifacts=transport/'artifacts';report=transport/'aggregate.json'
    commands=[dict(argv=['bash',str(Path(project)/'repo/corpus-work/run_public_transport.sh'),
        '--commit',commit,'--filelist',str(filelist),'--filelist-sha256',merger.core.sha(filelist),
        '--cache',old['cache'],'--old-filelist',old['filelist'],'--old-filelist-sha256',merger.core.sha(Path(old['filelist'])),
        '--old-public-proof',old['public_proof'],'--old-public-proof-sha256',merger.core.sha(Path(old['public_proof'])),
        '--old-commit',old['commit'],'--output',str(transport)])]
    commands.extend(dict(argv=[py,'-B',str(package/name),*args]) for name,args in [
        ('restore_database.py',[]),('test_restore_database.py',[]),('test_database.py',[]),('restore_validation_artifacts.py',['--destination',str(artifacts)])])
    commands.append(dict(argv=[py,'-B',str(Path(project)/'repo/corpus-work/scripts/validate_corpus.py'),
        '--mode','editable-delivery','--package',str(package),'--evidence',str(package/'delivery-evidence.json'),
        '--build-root',str(artifacts/'build'),'--receipt-root',str(artifacts/'receipts'),'--report',str(report)]))
    dump(plan_path,dict(stage='verify-public',batch_id=frozen['batch_id'],expected_count=frozen['expected_count'],commit=commit,
                       commands=commands,transport_receipt=str(transport/'TRANSPORT_RECEIPT.json'),transport_root=str(transport),
                       aggregate_report=str(report),restored_receipt_root=str(artifacts/'receipts')))
    return plan_path

def transition(batch_dir, stage, plan_path):
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
    for n,command in enumerate(commands):
        argv=command.get('argv')
        if not isinstance(argv,list) or not argv or any(not isinstance(x,str) for x in argv): raise ValueError('argv list required; shell commands forbidden')
        # Caller supplies reviewed exact helper commands, never shell command strings.
        receipt=stage_dir/(str(n)+'.json')
        if receipt.exists():
            old=load(receipt)
            if old['argv']!=argv: raise ValueError('stage command changed')
            if old['exit_code']==0: continue
            raise ValueError('failed stage retained; new reviewed revision required')
        started=stage_dir/(str(n)+'.started.json')
        if started.exists(): raise ValueError('interrupted stage needs reconciliation; do not repeat output mutation')
        dump(started,dict(argv=argv,status='started_not_completed'))
        with (stage_dir/(str(n)+'.log')).open('w') as log:
            run=subprocess.run(argv,shell=False,stdout=log,stderr=subprocess.STDOUT,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
        dump(receipt,dict(argv=argv,exit_code=run.returncode))
        if run.returncode: raise ValueError('release stage failed; see '+str(receipt))
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
            log=stage_dir/(str(index)+'.log')
            actual_commands.append(dict(argv=record['argv'],returncode=record['exit_code'],
                                        log=str(log.resolve()),log_sha256=merger.core.sha(log)))
        if len(actual_commands)!=5: raise ValueError('public plan requires five actual restoration commands')
        result=dict(status='public_exact_commit_full'+str(frozen['expected_count'])+'_restored_verified',
                    commit=commit,verified_corpus_commit=commit,verified_count=frozen['expected_count'],
                    remote_main_delivered_count=frozen['expected_count'],public_files_verified=len(files),
                    public_filelist_sha256=merger.core.sha(public_filelist),
                    manifest_sha256=merger.core.sha(package/'manifest.json'),sql=sql,commands=actual_commands,
                    actual_gate=gate,remote_count_update_required=True,
                    cache=str(package),filelist=str(public_filelist),public_proof=str(done.resolve()))
    else:
        if 'preparation_report' in plan:
            prepared=load(Path(plan['preparation_report']))
            if prepared.get('status')!='prepared_editable_release_not_restored_or_remote_verified':
                raise ValueError('release preparation helper did not complete')
            if prepared.get('items')!=frozen['expected_count'] or prepared.get('sql',{}).get('problem_count')!=frozen['expected_count']:
                raise ValueError('prepared release count mismatch')
            if prepared.get('input_aggregate',{}).get('actual_qualified_count')!=frozen['expected_count']:
                raise ValueError('preparation does not reuse complete input aggregate')
            result=dict(status='release_prepared_root_publish_pending',verified_count=frozen['expected_count'],
                        reused_merge_aggregate=True,additional_local_restore_performed=False,remote_delivered_increment=0)
        else:
            local=load(Path(plan['local_verification_receipt']))
            if local.get('status')!='actual_local_release_SQL_artifacts_tests_fullgate_passed_not_remote':
                raise ValueError('release preparation is not actual local restoration')
            if local.get('sql',{}).get('problem_count')!=frozen['expected_count']: raise ValueError('release restored count mismatch')
            result=dict(status='release_prepared_local_restored_root_publish_pending',verified_count=frozen['expected_count'],remote_delivered_increment=0)
    dump(done,result);return result

def publish(batch_dir, plan_path=None): return transition(batch_dir,'publish',plan_path or publish_plan(batch_dir))
def verify_public(batch_dir, plan_path=None, commit=None, previous=None):
    result=transition(batch_dir,'verify-public',plan_path or public_plan(batch_dir,commit,previous))
    update_queue(batch_dir,result,remote=True)
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['status','prepare','merge','publish','verify-public'])
    p.add_argument('--queue',type=Path);p.add_argument('--state-root',type=Path);p.add_argument('--batch-dir',type=Path);p.add_argument('--plan',type=Path);p.add_argument('--threshold',type=int,default=25);p.add_argument('--commit');p.add_argument('--previous',type=Path)
    a=p.parse_args()
    if a.action in ('status','prepare'):
        if not a.queue or not a.state_root: p.error('--queue and --state-root required')
        result=status(a.queue,a.state_root,a.threshold) if a.action=='status' else prepare(a.queue,a.state_root,a.threshold)
    elif a.action=='merge': result=merge(a.batch_dir)
    elif a.action=='publish': result=publish(a.batch_dir,a.plan)
    else: result=verify_public(a.batch_dir,a.plan,a.commit,a.previous)
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':
    with controller_lock(): main()
