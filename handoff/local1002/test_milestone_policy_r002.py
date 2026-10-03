import unittest,json,hashlib,copy
from pathlib import Path
from milestone_policy import decide

def h(b):return hashlib.sha256(b).hexdigest()
def enc(d):return json.dumps(d,sort_keys=True,separators=(',',':')).encode()
def report(ids,count):return {'mode':'editable-delivery','editable_qualified_count':len(ids),'package_item_count':count,'errors':[],'items':{i:{'status':'qualified_editable','errors':[]} for i in ids}}
class MilestonePolicyTests(unittest.TestCase):
 def setUp(self):
  local=Path(__file__).resolve().parent;q=json.loads((local/'reconstruction.plan.json').read_bytes());self.new=set(q['new_ids']);self.old=set(json.loads((local/'fixed975-identity-ids.json').read_bytes()));self.i=sorted(self.old,key=int)[0]
  content={'row':{'problem_id':self.i},'body_evidence':{'source':'same'},'files':{'package:item':{'sha256':'a'*64}},'runtime_files':{'validator':{'sha256':'b'*64}},'runtime':{'validator':'b'*64}}
  identity={'content':content,'identity_sha256':h(enc(content))};raw=enc(report([self.i],975));self.prior={'item_id':self.i,'identity':copy.deepcopy(identity),'report_sha256':h(raw)};self.raw=raw;self.current=copy.deepcopy(identity);self.proj={'index':['exact row'],'SQLite':{'fulltext':'same','source':'same'}}
  self.session={'prior_count':975,'current_count':1002,'base_ids':self.old,'new_ids':self.new,'anchor':{'kind':'root_authorized_qualified_local_base_pending_remote_commit','count':975,'expected_tree':'db9c995b48c0963d0c648cd0fd25d803c9012af8','reports':{i:h(enc(report([i],975))) for i in self.old},'qualified_receipt_pinned':True,'sanitized_export_scope_cleared':True},'fresh_new_reports':{i:{'exit_code':0,'report_bytes':enc(report([i],1002))} for i in self.new},'aggregate':{'exit_code':0,'report_bytes':enc(report(self.old|self.new,1002))}}
 def call(self):return decide(self.current,self.prior,self.raw,self.proj,self.proj,self.session)
 def test_true975_to1002_exact_material_retains_history_with_fresh27_and_aggregate(self):
  d=self.call();self.assertEqual(d['action'],'retain_historical_local_item_checks');self.assertEqual((d['prior_count'],d['current_count'],d['fresh_new_item_count']),(975,1002,27));self.assertFalse(d['fresh_cli_execution']);self.assertTrue(d['publication_requires_verified_base_commit'])
 def test_changed_material_refuses(self):
  self.current['content']['files']['package:item']['sha256']='c'*64;self.current['identity_sha256']=h(enc(self.current['content']));self.assertEqual(self.call()['action'],'fresh_required')
 def test_changed_runtime_refuses(self):
  self.current['content']['runtime_files']['validator']['sha256']='c'*64;self.current['identity_sha256']=h(enc(self.current['content']));self.assertEqual(self.call()['action'],'fresh_required')
 def test_missing_prior_report_refuses(self):
  self.raw=b'';self.assertEqual(self.call()['action'],'fresh_required')
 def test_missing_one_new_actual_call_refuses(self):
  self.session['fresh_new_reports'].pop(next(iter(self.new)));self.assertEqual(self.call()['action'],'fresh_required')
 def test_missing_fresh_full_aggregate_refuses(self):
  self.session['aggregate']['report_bytes']=b'';self.assertEqual(self.call()['action'],'fresh_required')
 def test_missing_base_execution_report_binding_refuses(self):
  self.session['anchor']['reports'].pop(next(i for i in self.old if i!=self.i));self.assertEqual(self.call()['action'],'fresh_required')
 def test_changed_SQL_projection_refuses(self):
  self.assertEqual(decide(self.current,self.prior,self.raw,self.proj,{'SQLite':'changed'},self.session)['action'],'fresh_required')
 def test_superseded_unsanitized_base_refuses(self):
  self.session['anchor']['sanitized_export_scope_cleared']=False;self.assertEqual(self.call()['action'],'fresh_required')
 def test_false_milestone_counts_refuse(self):
  self.session['current_count']=1001;self.assertEqual(self.call()['action'],'fresh_required')
if __name__=='__main__':unittest.main()
