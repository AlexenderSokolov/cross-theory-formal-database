import argparse
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
import types
import sys
import io
import time
from contextlib import contextmanager,redirect_stdout
from unittest.mock import patch
import publish_corpus_bundle as relay
import controller_publish_pipeline as pipeline

class RecoveryTests(unittest.TestCase):
    def test_push_response_lost_after_actual_local_push(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);src=root/'src';remote=root/'remote.git'
            def git(*argv):return relay.run(['git',*map(str,argv)],cwd=src if src.exists() else root)
            git('init',src);git('config','user.name','Fixture');git('config','user.email','fixture@example.invalid')
            git('checkout','-b','corpus-progress-20261001')
            (src/'proof.txt').write_text('synthetic fixture');git('add','proof.txt');git('commit','-m','base')
            base=git('rev-parse','HEAD');git('init','--bare',remote);git('push',remote,'HEAD:corpus-progress-20261001')
            (src/'proof.txt').write_text('synthetic revision');git('commit','-am','next')
            target=git('rev-parse','HEAD');bundle=root/'next.bundle';git('bundle','create',bundle,base+'..HEAD')
            original=relay.run;pushes=[]
            def lost(argv,cwd=None):
                result=original(argv,cwd)
                if 'push' in argv:
                    pushes.append(argv);raise subprocess.CalledProcessError(255,argv,stderr='response lost')
                return result
            with patch.object(relay,'run',lost):
                receipt=relay.publish(bundle,root/'relay.git','corpus-progress-20261001',base,str(remote))
            self.assertEqual(receipt['commit'],target);self.assertTrue(receipt['push_response_recovered'])
            self.assertEqual(len(pushes),1);self.assertEqual(receipt['remote_count_increment'],0)
            self.assertEqual(relay.publish(bundle,root/'relay.git','corpus-progress-20261001',base,str(remote),target)['status'],'already_pushed_requires_public_restore')
            (src/'later.txt').write_text('synthetic concurrent advance');git('add','later.txt');git('commit','-m','concurrent');git('push',remote,'HEAD:corpus-progress-20261001')
            with self.assertRaisesRegex(ValueError,'remote advanced'):
                relay.publish(bundle,root/'relay.git','corpus-progress-20261001',base,str(remote),target)
            self.assertNotEqual(git('ls-remote',remote,'refs/heads/corpus-progress-20261001').split()[0],target)

    def args(self,root):
        return argparse.Namespace(cache=str(root),batch='/fixture/batch',generation=1,
            owner='local-controller-01a10a85',host='fixture',
            relay=str(root/'relay.git'),attempts=2,retry_seconds=0)

    def test_stage_retry_and_success_resume(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);p=pipeline.Pipeline(self.args(root));calls=[]
            def response():
                calls.append(1)
                if len(calls)==1:raise RuntimeError('SSH response lost')
                return {'status':'server_receipt_recovered'}
            self.assertEqual(p.step('commit',response)['status'],'server_receipt_recovered')
            self.assertEqual(p.step('commit',lambda:self.fail('completed step repeated'))['status'],'server_receipt_recovered')
            self.assertEqual(len(calls),2)
            with pipeline.local_lock(root):
                with self.assertRaises(OSError):
                    with pipeline.local_lock(root):pass

    def test_interrupted_scp_retries_only_missing_bundle(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);p=pipeline.Pipeline(self.args(root));calls=[]
            def download(argv,input=None):
                calls.append(argv);Path(argv[-1]).write_bytes(b'x' if len(calls)==1 else b'xyz')
                if len(calls)==1:raise RuntimeError('interrupted SCP')
            with patch.object(p,'command',download):
                result=p.step('scp',lambda:p.transfer({'bundle':'/fixture/a.bundle','bytes':3}))
                p.transfer({'bundle':'/fixture/a.bundle','bytes':3})
            self.assertEqual(result['bytes'],3);self.assertEqual(len(calls),2)

    def test_full_synthetic_chain_skips_completed_stages(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);p=pipeline.Pipeline(self.args(root));commit='b'*40;calls=[]
            def ctl(stage,*flags):
                calls.append(stage)
                if stage=='verify-public':return {'verified_corpus_commit':commit,'remote_main_delivered_count':1090}
                return {'status':'prepared'}
            pub={'stage':'commit_ready','target_commit':commit,'expected_count':1090,'previous_public_result':'/fixture/previous','branch':'fixture','remote':'fixture','expected_remote_base':'a'*40}
            def server(stage,**kwargs):
                if stage=='inspect':return pub
                calls.append(stage);return {'commit':commit,'bundle':'/fixture/b.bundle','bytes':3}
            class FakeGuard:
                token='1/fixture';previous_external=None
                def __init__(self,*a):pass
                def __enter__(self):return self
                def __exit__(self,*a):pass
                def check(self):pass
                def external(self,record):pass
            with patch.object(pipeline,'PublicationGuard',FakeGuard),patch.object(p,'check_owner'),patch.object(p,'ctl',ctl),patch.object(p,'server',server),patch.object(p,'transfer',return_value={'bundle':'fixture'}),patch.object(pipeline,'publish',return_value={'commit':commit}):
                self.assertEqual(p.run()['remote_main_delivered_count'],1090)
                first=list(calls);p.run();self.assertEqual(calls,first)
            self.assertEqual(json.loads((p.root/'result.json').read_text())['verified_corpus_commit'],commit)

    def test_old_owner_rejected_before_any_mutation(self):
        with tempfile.TemporaryDirectory() as folder:
            p=pipeline.Pipeline(self.args(Path(folder)))
            with patch.object(p,'ssh',return_value=json.dumps({'controller':{'owner':'new-controller','generation':2}})),patch.object(p,'ctl') as mutate:
                with self.assertRaises(ValueError):p.run()
                mutate.assert_not_called()
        compile(pipeline.REMOTE,'fixed-server-publication','exec')
        compile(pipeline.GUARD,'publication-guard','exec')

    def test_unknown_prior_writer_cannot_be_retried_from_remote_base(self):
        with tempfile.TemporaryDirectory() as folder:
            p=pipeline.Pipeline(self.args(Path(folder)))
            p.guard=types.SimpleNamespace(previous_external={'state':'unknown','process_identity':{'pid':9}})
            with patch.object(pipeline,'git_run') as remote:
                with self.assertRaisesRegex(ValueError,'terminal evidence'):p.reconcile_external({})
                remote.assert_not_called()

    def test_guard_loss_stops_write_and_terminal_evidence_reconciles_unknown(self):
        with tempfile.TemporaryDirectory() as folder:
            p=pipeline.Pipeline(self.args(Path(folder)));external=[]
            def lost():raise relay.GuardLost('synthetic connection loss')
            p.guard=types.SimpleNamespace(check=lost,external=external.append,previous_external=None)
            pub={'target_commit':'b'*40,'expected_remote_base':'a'*40,'branch':'fixture','remote':'fixture'}
            with patch.object(pipeline,'publish',side_effect=relay.GuardLost('writer killed remote=target')):
                with self.assertRaises(relay.GuardLost):p.push('fixture.bundle',pub)
            record=json.loads((p.root/'external-write.json').read_text())
            self.assertEqual(record['state'],'unknown');self.assertTrue(record['writer_terminal'])
            p.guard.previous_external=external[-1]
            with patch.object(pipeline,'git_run',return_value='b'*40+' refs/heads/fixture'):
                p.reconcile_external(pub)
            self.assertEqual(external[-1]['state'],'terminal');self.assertEqual(external[-1]['remote_commit'],'b'*40)

    def test_live_external_process_is_terminated_when_guard_disappears(self):
        checks=[]
        def guard():
            checks.append(1)
            if len(checks)>1:raise relay.GuardLost('synthetic guard loss')
        started=time.monotonic()
        with self.assertRaises(relay.GuardLost):
            relay.run([sys.executable,'-c','import time; time.sleep(20)'],guard=guard)
        self.assertLess(time.monotonic()-started,4)

    def test_commit_response_lost_and_bundle_uses_fixed_target_after_HEAD_moves(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);repo=root/'repo';repo.mkdir();batch=root/'operations/corpusctl/batches/fixture-1-2';batch.mkdir(parents=True)
            def git(*argv):return relay.run(['git','-C',str(repo),*map(str,argv)])
            git('init');git('config','user.name','Fixture');git('config','user.email','fixture@example.invalid');git('checkout','-b','fixture')
            (repo/'proof.txt').write_text('synthetic base');git('add','proof.txt');git('commit','-m','base');base=git('rev-parse','HEAD')
            (repo/'proof.txt').write_text('synthetic revision');git('add','proof.txt');tree=git('write-tree')
            actor={'owner':'fixture','generation':1}
            pub=dict(schema_version=2,record_type='publication',batch_id=batch.name,actor=actor,started_by=actor,actor_history=[],stage='git_staged',expected_count=2,incoming_ids=['001'],remote='fixture',branch='fixture',expected_remote_base=base,server_parent=base,expected_tree=tree,target_commit=None,bundle_path=None,previous_public_result='/fixture/previous',receipt_paths={})
            pipeline.save(batch/'publication.json',pub);pipeline.save(batch/'controller-publish/stage.json',{'paths':['proof.txt']})
            protocol=types.ModuleType('corpus_control_protocol')
            @contextmanager
            def controller_guard(*a):yield
            protocol.controller_guard=controller_guard;protocol.load_json=lambda p:json.loads(Path(p).read_text());protocol.save_json=pipeline.save;protocol.assert_publication_guard=lambda *a:None
            runtime=types.ModuleType('corpus_runtime');runtime.identity=lambda pid:{'pid':pid,'start_time':'fixture','cwd':str(root)}
            def remote(stage):
                cfg={'root':str(root),'batch':str(batch),'stage':stage,'actor':actor,'guard_token':'fixture'}
                native_popen=subprocess.Popen
                def fixture_popen(argv,**kwargs):
                    # POSIX exec/gated process groups are checked on Linux. This
                    # Windows fixture preserves real Git, without emulating exec.
                    if os.name=='nt' and len(argv)>4 and argv[2]=='-c':argv=json.loads(argv[-1])
                    return native_popen(argv,**kwargs)
                with patch.dict(sys.modules,{'corpus_control_protocol':protocol,'corpus_runtime':runtime}),patch.object(sys,'argv',['fixed',json.dumps(cfg)]),patch.object(subprocess,'Popen',fixture_popen),redirect_stdout(io.StringIO()) as output:
                    namespace={};exec(pipeline.PROCESS_SUPPORT,namespace)
                    # Windows Git fixture tests the commit identity; actual Linux
                    # process-group survival is exercised separately, without mocks.
                    namespace['writer_group_members']=lambda pgid:[]
                    try:exec(compile(pipeline.REMOTE_BODY,'remote','exec'),namespace)
                    except SystemExit as done:
                        if done.code!=0:raise
                return json.loads(output.getvalue().splitlines()[-1])
            original_save=pipeline.save
            def lost(path,value):
                if Path(path)==batch/'publication.json' and value.get('target_commit'):
                    raise RuntimeError('commit response lost before receipt')
                return original_save(path,value)
            with patch.object(protocol,'save_json',lost):
                with self.assertRaisesRegex(RuntimeError,'response lost'):remote('commit')
            target=git('rev-parse','HEAD');self.assertEqual(json.loads((batch/'publication.json').read_text())['target_commit'],None)
            self.assertEqual(remote('commit')['commit'],target)
            saved=json.loads((batch/'publication.json').read_text());self.assertEqual(saved['stage'],'commit_ready');self.assertEqual(saved['expected_tree'],tree)
            (repo/'later.txt').write_text('unrelated later change');git('add','later.txt');git('commit','-m','later')
            bundle=remote('bundle');self.assertEqual(bundle['commit'],target)
            self.assertEqual(git('bundle','list-heads',bundle['bundle']).split()[0],target)
            # Delete no files: simulate a lost commit receipt by retaining it under another name.
            (batch/'controller-publish/commit.json').rename(batch/'controller-publish/commit-lost.json')
            self.assertEqual(remote('commit')['commit'],target)
            proof={'verified_corpus_commit':target,'remote_main_delivered_count':2}
            pipeline.save(batch/'verify-public/result.json',proof)
            saved=json.loads((batch/'publication.json').read_text());saved.update(stage='reconciled');saved['receipt_paths']['public_result']=str(batch/'verify-public/result.json');pipeline.save(batch/'publication.json',saved)
            queue_path=repo/'handoff/yupeng/PRODUCTION_QUEUE.json'
            pipeline.save(queue_path,{'base':{'remote_main_count':1},'active_batch':{'batch_id':batch.name}})
            self.assertTrue(remote('public-result')['queue_reconciliation_needed'])
            pipeline.save(queue_path,{'base':{'remote_main_count':2},'active_batch':{'batch_id':'successor'}})
            self.assertFalse(remote('public-result')['queue_reconciliation_needed'])

    def test_reconciled_proof_repairs_only_uncommitted_queue_then_old_done_returns(self):
        with tempfile.TemporaryDirectory() as folder:
            p=pipeline.Pipeline(self.args(Path(folder)));proof={'verified_corpus_commit':'b'*40,'remote_main_delivered_count':1090}
            pub={'stage':'reconciled','target_commit':'b'*40,'expected_count':1090,'previous_public_result':'/fixture/previous'}
            class FakeGuard:
                def __init__(self,*a):pass
                def __enter__(self):return self
                def __exit__(self,*a):pass
                def check(self):pass
            needed=[True]
            def server(stage):
                if stage=='inspect':return pub
                self.assertEqual(stage,'public-result')
                return {'public_result':proof,'queue_reconciliation_needed':needed[0]}
            with patch.object(pipeline,'PublicationGuard',FakeGuard),patch.object(p,'check_owner'),patch.object(p,'server',server),patch.object(p,'ctl',return_value=proof) as ctl,patch.object(p,'step') as replay:
                self.assertEqual(p.run(),proof);ctl.assert_called_once_with('verify-public','--commit','b'*40,'--previous','/fixture/previous');replay.assert_not_called()
                needed[0]=False;ctl.reset_mock();self.assertEqual(p.run(),proof);ctl.assert_not_called();replay.assert_not_called()

if __name__=='__main__':unittest.main()
