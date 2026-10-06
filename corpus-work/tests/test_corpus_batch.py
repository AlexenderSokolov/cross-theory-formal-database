"""Engineering adapter tests; synthetic data never counts as mathematical admission."""
import json, tempfile, unittest, sys
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import corpus_batch as c

def write(path,value):
 path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value))
class BatchTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name);self.queue=self.root/'queue.json'
 def queue_data(self,n=11):
  return {'base':{'local_count':1048,'remote_main_count':1040},'queued_new_root_admitted':[{'problem_id':str(2000+i),'state':'root_admitted_waiting_batch','final_revision_frozen':True,'accepted_H':'H2','difficulty_reason':'source decision','material_basis':'complete','semantic_basis':'distinct'} for i in range(n)]}
 def test_real_shape_waits_six_without_output(self):
  write(self.queue,self.queue_data());state=self.root/'state'
  result=c.prepare(self.queue,state,project=self.root)
  self.assertEqual(result['remaining'],6);self.assertEqual(result['expected_count'],1059);self.assertFalse(state.exists())
 def test_unfrozen_and_duplicate_refused(self):
  q=self.queue_data();q['queued_new_root_admitted'][0]['final_revision_frozen']=False;write(self.queue,q)
  with self.assertRaises(ValueError): c.status(self.queue)
  q=self.queue_data();q['queued_new_root_admitted'][1]['problem_id']='2000';write(self.queue,q)
  with self.assertRaises(ValueError): c.status(self.queue)
 def test_freeze_threshold_and_resume_no_reprepare(self):
  q=self.queue_data(17);write(self.queue,q)
  def fake(row,project,incoming=False):
   return {'manifest_sha256':'a'*64,'package':'fixture'}
  with patch.object(c,'entry',side_effect=fake) as entry:
   result=c.prepare(self.queue,self.root/'state',project=self.root)
   calls=entry.call_count
   repeated=c.prepare(self.queue,self.root/'state',project=self.root)
   self.assertEqual(entry.call_count,calls);self.assertEqual(result,repeated)
  self.assertEqual(result['expected_count'],1065)
  spec=json.loads(Path(result['spec']).read_text());self.assertEqual(len(spec['incoming']),17)
 def batch(self):
  folder=self.root/'batch';folder.mkdir();write(folder/'batch.json',{'batch_id':'fixture','expected_count':2,'output':str(folder/'merge'),'spec':str(folder/'spec.json'),'review':str(folder/'review.json')})
  return folder
 def test_merge_once_and_failure_not_restarted(self):
  folder=self.batch();output=folder/'merge'
  def run(*args):
   output.mkdir();result={'status':'actual_editable_batch_gate_passed_not_remote','items':2};write(output/'batch-result.json',result);return result
  with patch.object(c.merger,'merge_batch',side_effect=run) as merge, patch.object(c,'update_queue') as update:
   c.merge(folder);c.merge(folder);self.assertEqual(merge.call_count,1)
  write(output/'batch-result.json',{'status':'failed_batch_partial_output_retained'})
  with patch.object(c.merger,'merge_batch') as merge:
   with self.assertRaises(ValueError): c.merge(folder)
   merge.assert_not_called()
 def test_interrupted_stage_not_replayed(self):
  folder=self.batch();write(folder/'merge/batch-result.json',{'status':'actual_editable_batch_gate_passed_not_remote'})
  plan={'stage':'publish','expected_count':2,'batch_id':'fixture','commands':[{'argv':['fixture-helper']}]};write(self.root/'plan.json',plan)
  write(folder/'publish/0.started.json',{'status':'started_not_completed'})
  with patch.object(c.subprocess,'run') as run:
   with self.assertRaises(ValueError): c.publish(folder,self.root/'plan.json')
   run.assert_not_called()
 def test_bundle_receipt_cannot_claim_publish(self):
  folder=self.batch();write(folder/'merge/batch-result.json',{'status':'actual_editable_batch_gate_passed_not_remote'})
  write(self.root/'local.json',{'status':'bundle_prepared'})
  plan={'stage':'publish','expected_count':2,'batch_id':'fixture','commands':[{'argv':['fixture-helper']}],'local_verification_receipt':str(self.root/'local.json')};write(self.root/'plan.json',plan)
  write(folder/'publish/0.json',{'argv':['fixture-helper'],'exit_code':0})
  with self.assertRaises(ValueError): c.publish(folder,self.root/'plan.json')
 def test_queue_transaction_preserves_later_admissions(self):
  folder=self.batch();frozen=json.loads((folder/'batch.json').read_text());q=self.queue_data(2)
  q['base'].update(package='base',build_root='build',receipt_root='receipts')
  write(self.queue,q);frozen.update(queue=str(self.queue),incoming_ids=['2000'],local_count=1048,expected_count=1049);write(folder/'batch.json',frozen)
  result={'package':'merged','build_root':'merged-build','receipt_root':'merged-rec','actual_aggregate':{'report':'aggregate'}}
  c.update_queue(folder,result);actual=json.loads(self.queue.read_text())
  self.assertEqual(actual['base']['local_count'],1049);self.assertEqual(actual['base']['remote_main_count'],1040)
  self.assertEqual([r['problem_id'] for r in actual['queued_new_root_admitted']],['2001'])
  c.update_queue(folder,result);self.assertEqual(json.loads(self.queue.read_text())['queued_new_count'],1)
  c.update_queue(folder,{},remote=True);self.assertEqual(json.loads(self.queue.read_text())['base']['remote_main_count'],1049)
 def test_path_escape_refused(self):
  with self.assertRaises(ValueError): c.safe(self.root.parent/'outside',self.root)
 def test_public_result_is_next_checkpoint_previous_proof(self):
  import prepare_public_transport as transport
  folder=self.batch();write(folder/'merge/batch-result.json',{'status':'actual_editable_batch_gate_passed_not_remote'})
  root=folder/'public';package=root/'package';receipts=root/'artifacts/receipts'
  manifest=package/'manifest.json';write(manifest,{'items':[]})
  filelist=root/'PUBLIC_FILELIST.json';manifest_pin=c.merger.core.sha(manifest)
  entries={'manifest.json':{'path':'manifest.json','bytes':manifest.stat().st_size,'sha256':manifest_pin}}
  write(filelist,{'files':list(entries.values())})
  commit='a'*40
  write(root/'TRANSPORT_RECEIPT.json',{'current_commit':commit,'status':'prepared_exact_public_transport_requires_actual_restore_and_full_gate'})
  gatefile=root/'aggregate.json'
  write(gatefile,{'mode':'editable-delivery','editable_qualified_count':2,'package_item_count':2,'errors':[],'items':{'1':{'errors':[]},'2':{'errors':[]}},'receipt_set':str(receipts.resolve())})
  commands=[{'argv':['download']}]
  for script in ('restore_database.py','test_restore_database.py','test_database.py','restore_validation_artifacts.py'):
   commands.append({'argv':['python','-B',str(package/script)]})
  commands.append({'argv':['python','-B','validator','--mode','editable-delivery','--package',str(package),'--evidence',str(package/'delivery-evidence.json'),'--receipt-root',str(receipts)]})
  plan={'stage':'verify-public','batch_id':'fixture','expected_count':2,'commands':commands,'commit':commit,'transport_receipt':str(root/'TRANSPORT_RECEIPT.json'),'transport_root':str(root),'aggregate_report':str(gatefile),'restored_receipt_root':str(receipts)}
  write(self.root/'plan.json',plan)
  for n,command in enumerate(commands):
   write(folder/f'verify-public/{n}.json',{'argv':command['argv'],'exit_code':0})
   (folder/f'verify-public/{n}.log').write_text('actual fixture completed')
  sql={'problem_count':2,'integrity':'ok','foreign_key_errors':[],'full_problem_and_source_projection':True,'sqlite_sha256':'b'*64}
  gate={'report':str(gatefile),'sha256':c.merger.core.sha(gatefile),'actual_qualified_count':2}
  with patch.object(c,'check_report',return_value=gate),patch('prepare_editable_release.check_sql',return_value=sql),patch.object(c.subprocess,'run') as run:
   result=c.transition(folder,'verify-public',self.root/'plan.json');run.assert_not_called()
  proof=folder/'verify-public/result.json'
  checked=transport.verified_previous(proof,c.merger.core.sha(proof),commit,c.merger.core.sha(filelist),entries,package)
  self.assertEqual(checked['remote_main_delivered_count'],2)
  self.assertEqual(result['cache'],str(package))
  self.assertEqual(result['public_proof'],str(proof.resolve()))
  with self.assertRaises(ValueError):transport.verified_previous(proof,c.merger.core.sha(proof),'c'*40,c.merger.core.sha(filelist),entries,package)
 def test_publish_reuses_input_aggregate_without_second_restore(self):
  folder=self.batch();write(folder/'merge/batch-result.json',{'status':'actual_editable_batch_gate_passed_not_remote'})
  prepared=self.root/'prepared.json'
  write(prepared,{'status':'prepared_editable_release_not_restored_or_remote_verified','items':2,'sql':{'problem_count':2},'input_aggregate':{'actual_qualified_count':2}})
  plan={'stage':'publish','batch_id':'fixture','expected_count':2,'commands':[{'argv':['prepare-only']}],'preparation_report':str(prepared)}
  write(self.root/'plan.json',plan);write(folder/'publish/0.json',{'argv':['prepare-only'],'exit_code':0})
  with patch.object(c.subprocess,'run') as run:
   result=c.transition(folder,'publish',self.root/'plan.json');run.assert_not_called()
  self.assertTrue(result['reused_merge_aggregate']);self.assertFalse(result['additional_local_restore_performed'])
if __name__=='__main__': unittest.main()
