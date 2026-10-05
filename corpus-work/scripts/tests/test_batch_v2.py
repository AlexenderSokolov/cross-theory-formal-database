import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).parent))
sys.path.append('/disks/sata1/yupeng/human-proof-corpus/repo/corpus-work/scripts')
import corpus_batch as batch

def write(p,value):
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value))

class BatchV2(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.state=self.root/'operations/corpusctl/batches';self.state.mkdir(parents=True)
        self.queue=self.root/'queue.json'
        self.base=dict(package=str(self.root/'base'),build_root=str(self.root/'build'),receipt_root=str(self.root/'receipts'),accepted_report=str(self.root/'aggregate'),local_count=1065,remote_main_count=1065)
        self.set_queue(8)
    def tearDown(self):self.tmp.cleanup()
    def set_queue(self,n,local=1065,remote=1065):
        b=dict(self.base,local_count=local,remote_main_count=remote)
        rows=[dict(problem_id=str(5000+i),state='root_admitted_waiting_batch',final_revision_frozen=True,accepted_H='H2',difficulty_reason='authored nonroutine core',material_basis='source',semantic_basis='distinct') for i in range(n)]
        write(self.queue,dict(base=b,queued_new_root_admitted=rows,active_batch=None,last_publication=None))
    def fake_entry(self,row,*args,**kwargs):
        return dict(manifest_sha256='a'*64,package=row.get('package','packet'),build_root='build',receipt_root='receipts',paths=[],artifact_paths={},accepted_report={})
    def freeze(self):
        with patch.object(batch,'entry',self.fake_entry):return batch.prepare(self.queue,self.state,project=self.root)
    def read(self):return json.loads(self.queue.read_text())
    def merged(self,frozen):
        result=dict(status='actual_editable_batch_gate_passed_not_remote',items=frozen['expected_count'],package=str(self.root/'merged'),build_root='b',receipt_root='r',actual_aggregate={'report':'report'})
        write(Path(frozen['output'])/'batch-result.json',result);return result
    def test_B01_waiting8_does_not_create_batch(self):
        r=self.freeze();self.assertEqual(r['status'],'waiting_for_admissions');self.assertEqual(r['remaining'],17)
        self.assertEqual(r['expected_count'],1090);self.assertEqual(list(self.state.iterdir()),[])
    def test_B02_pending_plus_one_no_merge(self):
        self.set_queue(1,1090,1065);q=self.read();q['active_batch']={'batch_id':'existing','batch_dir':str(self.state/'existing'),'frozen_base':self.base,'expected_count':1090,'incoming_ids':[str(8000+i) for i in range(25)]};write(self.queue,q)
        self.assertEqual(self.freeze()['status'],'pending_publication');self.assertEqual(len(self.read()['queued_new_root_admitted']),1)
    def test_B03_frozen_scope_survives_new_admission_and_intent_crash(self):
        self.set_queue(25)
        with patch.object(batch,'entry',side_effect=RuntimeError('crash after intent')):
            with self.assertRaisesRegex(RuntimeError,'crash'):batch.prepare(self.queue,self.state,project=self.root)
        q=self.read();self.assertIsNotNone(q['active_batch']);ids=q['active_batch']['incoming_ids']
        q['queued_new_root_admitted'].append(dict(q['queued_new_root_admitted'][0],problem_id='7000'));write(self.queue,q)
        frozen=self.freeze();self.assertEqual(frozen['incoming_ids'],ids);self.assertEqual(frozen['expected_count'],1090)
        self.assertEqual(self.freeze()['batch_id'],frozen['batch_id'])
    def test_B04_merge_receipt_reconcile_preserves_later_row(self):
        self.set_queue(25);f=self.freeze();r=self.merged(f)
        q=self.read();q['queued_new_root_admitted'].append(dict(q['queued_new_root_admitted'][0],problem_id='7000'));write(self.queue,q)
        with patch.object(batch.merger,'merge_batch',side_effect=AssertionError('rebuild repeated')):batch.merge(Path(f['batch_dir']));batch.merge(Path(f['batch_dir']))
        self.assertEqual(self.read()['base']['local_count'],1090);self.assertEqual([x['problem_id'] for x in self.read()['queued_new_root_admitted']],['7000'])
    def test_B05_missing_pointer_unique_receipt_recovery_and_ambiguity(self):
        self.set_queue(25);f=self.freeze();r=self.merged(f);batch.update_queue(f['batch_dir'],r)
        q=self.read();q['active_batch']=None;write(self.queue,q)
        recovered=batch.recover_active_batch(self.queue,self.state);self.assertEqual(recovered['batch_id'],f['batch_id'])
        q=self.read();q['active_batch']=None;write(self.queue,q)
        other=self.state/'conflict';other.mkdir();write(other/'batch.json',dict(json.loads((Path(f['batch_dir'])/'batch.json').read_text()),batch_id='conflict',batch_dir=str(other),output=str(other/'merge')));write(other/'merge/batch-result.json',r)
        with self.assertRaisesRegex(ValueError,'unique'):batch.recover_active_batch(self.queue,self.state)
    def test_B06_fifo25_and_B07_final10(self):
        self.set_queue(26);f=self.freeze();self.assertEqual(len(f['incoming_ids']),25);self.assertEqual(f['expected_count'],1090)
        self.assertEqual(f['incoming_ids'],[str(5000+i) for i in range(25)])
        self.set_queue(12,29990,29990);f=self.freeze();self.assertEqual(len(f['incoming_ids']),10);self.assertEqual(f['expected_count'],30000)
    def test_T05_public_result_reconcile_once_and_stale_reject(self):
        self.set_queue(25);f=self.freeze();r=self.merged(f);batch.update_queue(f['batch_dir'],r)
        public=dict(verified_corpus_commit='b'*40,remote_main_delivered_count=1090,verified_count=1090)
        batch.update_queue(f['batch_dir'],public,remote=True);first=self.read();batch.update_queue(f['batch_dir'],public,remote=True)
        self.assertEqual(self.read(),first);self.assertIsNone(first['active_batch']);self.assertEqual(first['last_publication']['commit'],'b'*40)
        batch.update_queue(f['batch_dir'],r);self.assertEqual(self.read(),first)
        q=self.read();q['base']['local_count']=1115;q['base']['remote_main_count']=1115;write(self.queue,q)
        with self.assertRaisesRegex(ValueError,'stale|different'):batch.update_queue(f['batch_dir'],public,remote=True)

    def test_public_reconciled_precedes_atomic_active_release(self):
        self.set_queue(25);f=self.freeze();r=self.merged(f);batch.update_queue(f['batch_dir'],r)
        pub=Path(f['batch_dir'])/'publication.json'
        write(pub,dict(batch_id=f['batch_id'],stage='pushed',target_commit='b'*40,expected_count=1090,receipt_paths={}))
        public=dict(verified_corpus_commit='b'*40,remote_main_delivered_count=1090,verified_count=1090)
        save=batch.atomic_save
        def lost_queue(path,data):
            if Path(path)==self.queue:raise RuntimeError('queue write lost')
            return save(path,data)
        with patch.object(batch,'atomic_save',lost_queue):
            with self.assertRaisesRegex(RuntimeError,'queue write'):batch.update_queue(f['batch_dir'],public,remote=True)
        self.assertEqual(json.loads(pub.read_text())['stage'],'reconciled')
        self.assertIsNotNone(self.read()['active_batch'])
        batch.update_queue(f['batch_dir'],public,remote=True)
        self.assertIsNone(self.read()['active_batch'])

if __name__=='__main__':unittest.main()
