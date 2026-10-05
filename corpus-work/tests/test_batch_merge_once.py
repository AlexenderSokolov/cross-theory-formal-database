"""Five bounded engineering scenarios; fixtures are never mathematical items."""
from pathlib import Path
import json,os,shutil,sqlite3,sys,unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import merge_editable_batch as batch
import merge_editable_packages as core
ROOT=Path('/disks/sata1/yupeng/human-proof-corpus');OWN=ROOT/'candidates/batch-merge-once-r001';MASTER=ROOT/'repo/editable-corpus';TRIAL=Path(os.environ['BATCH_ONCE_TEST_ROOT'])

def dump(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
def load(p):return json.loads(p.read_text())

class BatchOnceContract(unittest.TestCase):
 def setUp(self):
  self.directory=TRIAL/self._testMethodName;self.directory.mkdir()
 def make(self,label,ident):
  top=self.directory/label;top.mkdir();pkg=top/'package';pkg.mkdir();(pkg/'items').mkdir();(pkg/'receipts').mkdir();(pkg/'sources').mkdir()
  statement='Engineering fixture data only; no mathematical statement or admission.'
  proof='Engineering protocol payload only; no mathematical proof or human theorem.'
  text='\\documentclass{article}\n\\begin{document}\n'+statement+'\n'+proof+'\n\\end{document}\n'
  item=pkg/'items'/f'{ident}.tex';item.write_text(text);source=pkg/'sources'/f'{ident}.tex';source.write_text(text);(pkg/'license.txt').write_text('ENGINEERING FIXTURE ONLY')
  for name in batch.HELPERS:shutil.copy2(MASTER/name,pkg/name)
  build=top/'build';(build/ident).mkdir(parents=True);receipts=top/'receipts';receipts.mkdir()
  (build/ident/'fixture.pdf').write_bytes(b'ENGINEERING ARTIFACT; NOT A REAL PDF');(build/ident/'compiler.log').write_text('ENGINEERING LOG ONLY')
  receipt={'problem_id':ident,'ok':True,'passes':2,'shell_escape':False,'input_sha256':core.sha(item),'dependency_sha256':{},'pdf_path':ident+'/fixture.pdf','pdf_sha256':core.sha(build/ident/'fixture.pdf'),'compiler_log_path':ident+'/compiler.log','compiler_log_sha256':core.sha(build/ident/'compiler.log'),'rerun_requests':[],'unresolved_references':[],'missing_characters':[],'multiply_defined_labels':[]}
  dump(receipts/(ident+'.json'),receipt);shutil.copy2(receipts/(ident+'.json'),pkg/'receipts'/(ident+'.json'))
  row={'problem_id':ident,'title':'ENGINEERING FIXTURE','difficulty_level':'H1','difficulty_reason':'ENGINEERING ONLY NO MATHEMATICAL COUNT','source_id':'fixture-'+ident,'author':'Fixture','work':'Fixture-'+ident,'source_url':'https://example.invalid/fixture-'+ident,'source_version':'TEST','retrieved_at':'2026-10-05','license':'FIXTURE','license_path':'license.txt','item_path':'items/'+ident+'.tex','tex_sha256':core.sha(item),'origin_class':'human_authored_native_tex','status':'verified_editable_tex','compile_receipt':'receipts/'+ident+'.json','asset_dependencies':[],'primary':{},'contexts':[]}
  check={'complete_statement':True,'complete_proof':True,'required_context_preserved':True,'above_ordinary_phd_quals':True,'source_authorship':'named-human-author','checked_at':'2026-10-05','method':'ENGINEERING FIXTURE TYPE CHECK ONLY','note':'These typed values exercise code, never corpus admission.'}
  body=lambda role,line: {'role':role,'tex_lines':[line,line],'tex_sha256':core.hashlib.sha256(text.splitlines()[line-1].encode()).hexdigest(),'source_index':0,'source_lines':[line,line],'method':'exact_tex'}
  m={'schema_version':1,'scope':'ENGINEERING FIXTURE ONLY','verified_count':1,'items':[row]};dump(pkg/'manifest.json',m)
  ev={'schema_version':1,'package_manifest_sha256':core.sha(pkg/'manifest.json'),'items':{ident:{'item_sha256':row['tex_sha256'],'independent_problem_unit':True,'claim_key':'fixture-claim-'+ident,'source_check':check,'sources':[{'root':'package','path':'sources/'+ident+'.tex','sha256':core.sha(source)}],'bodies':[body('primary_statement',3),body('primary_proof',4)]}}};dump(pkg/'delivery-evidence.json',ev)
  (pkg/'INDEX.md').write_text(f'| {ident} | ENGINEERING FIXTURE | H1 | [TeX](items/{ident}.tex) | [Source](https://example.invalid/fixture) |\n')
  report=top/'accepted-item.json';dump(report,{'schema_version':1,'mode':'editable-delivery','package_item_count':1,'editable_qualified_count':1,'items':{ident:{'status':'qualified_editable','errors':[]}},'errors':[],'receipt_set':str(receipts)})
  entry={'package':str(pkg),'manifest_sha256':core.sha(pkg/'manifest.json'),'build_root':str(build),'receipt_root':str(receipts),'paths':[p.relative_to(pkg).as_posix() for p in pkg.rglob('*') if p.is_file()],'artifact_paths':{'build':[ident+'/fixture.pdf',ident+'/compiler.log'],'receipts':[ident+'.json']},'accepted_report':{'path':str(report),'manifest_sha256':core.sha(pkg/'manifest.json')}}
  return entry
 def prepare(self,count=1):
  base=self.make('base','900000');incoming=[self.make('incoming-'+str(i),'900'+str(i+1).zfill(3)) for i in range(count)]
  spec={'base':base,'incoming':incoming,'master_helpers':str(MASTER)};self.bind(spec);return spec
 def bind(self,spec):
  review={'schema_version':1,'status':'material_review_complete','holds':[],'duplicates':[],'basis':'ENGINEERING FIXTURES ONLY','compile_reuse_basis':'TYPED CONTRACT FIXTURES, NO REAL COMPILE CLAIM','base_manifest_sha256':spec['base']['manifest_sha256'],'incoming_manifest_sha256':[e['manifest_sha256'] for e in spec['incoming']],'incoming_ids':[r['problem_id'] for e in spec['incoming'] for r in load(Path(e['package'])/'manifest.json')['items']]}
  self.specpath=self.directory/'spec.json';self.reviewpath=self.directory/'review.json';dump(self.specpath,spec);dump(self.reviewpath,review)
 def accepted_again(self,entry):
  pkg=Path(entry['package']);entry['manifest_sha256']=core.sha(pkg/'manifest.json');entry['accepted_report']['manifest_sha256']=entry['manifest_sha256'];e=load(pkg/'delivery-evidence.json');e['package_manifest_sha256']=entry['manifest_sha256'];dump(pkg/'delivery-evidence.json',e)
 def fake_final_gate(self,pkg,build,receipts,report,validator=None):
  ids=[r['problem_id'] for r in load(pkg/'manifest.json')['items']];dump(report,{'schema_version':1,'mode':'editable-delivery','package_item_count':len(ids),'editable_qualified_count':len(ids),'items':{i:{'status':'qualified_editable','errors':[]} for i in ids},'errors':[],'receipt_set':str(receipts)});return {'report':str(report),'actual_qualified_count':len(ids),'fixture_only':True}
 def merge(self,spec,name='output',gate=None):
  self.bind(spec)
  with patch.object(batch,'gate',side_effect=gate or self.fake_final_gate) as observed:
   result=batch.merge_batch(self.specpath,self.reviewpath,None,self.directory/name)
  return result,observed.call_count
 def rejected(self,spec,pattern,name='rejected'):
  self.bind(spec)
  with self.assertRaisesRegex(ValueError,pattern):batch.merge_batch(self.specpath,self.reviewpath,None,self.directory/name)
  self.assertFalse((self.directory/name).exists())
 def test_1_twentyfive_packets_one_base_copy_rebuild_gate(self):
  spec=self.prepare(25);base=Path(spec['base']['package']);original=(base/'manifest.json').read_bytes();actualcopy=core.copy_inputs;actualLoad=core.load_package
  with patch.object(core,'copy_inputs',wraps=actualcopy) as copied,patch.object(core,'load_package',wraps=actualLoad) as loaded:
   result,calls=self.merge(spec)
  self.assertEqual(result['items'],26);self.assertEqual(result['rebuild_calls'],1);self.assertEqual(result['gate_calls'],1);self.assertEqual(result['incoming_gate_reuse'],25);self.assertEqual(calls,1)
  self.assertEqual(sum(Path(c.args[0])==base for c in copied.call_args_list),1);self.assertEqual(sum(Path(c.args[0])==base for c in loaded.call_args_list),1);self.assertFalse(next(c for c in loaded.call_args_list if Path(c.args[0])==base).kwargs['validate_material'])
  out=self.directory/'output';self.assertFalse((out/'steps').exists());self.assertFalse((out/'reviews').exists());self.assertEqual((base/'manifest.json').read_bytes(),original)
  with sqlite3.connect(out/'package/corpus.sqlite') as db:
   self.assertEqual(db.execute('SELECT COUNT(*) FROM problems').fetchone()[0],26);self.assertEqual(db.execute('pragma integrity_check').fetchone()[0],'ok')
   for row in load(out/'package/manifest.json')['items']:self.assertEqual(db.execute('SELECT tex_content FROM problems WHERE problem_id=?',(row['problem_id'],)).fetchone()[0],(out/'package'/row['item_path']).read_text())
  dump(self.directory/'FIXTURE_METRICS.json',dict(result,engineering_only=True,mathematical_items_added=0))
 def test_2_reuse_success_coverage_failure_final_change_rejected(self):
  for kind in ['plural','missing','failed','wrong-id','stale-binding','changed-body','changed-source','changed-artifact']:
   with self.subTest(kind=kind):
    top=self.directory/kind;top.mkdir();before=self.directory;self.directory=top;spec=self.prepare();e=spec['incoming'][0];pkg=Path(e['package']);report=Path(e['accepted_report']['path'])
    if kind=='plural':e['accepted_reports']=[e.pop('accepted_report')];result,calls=self.merge(spec);self.assertEqual(result['incoming_gate_reuse'],1);self.assertEqual(calls,1)
    else:
     if kind=='missing':e.pop('accepted_report');message='accepted report descriptors'
     if kind=='failed':j=load(report);j['errors']=['deliberate failed fixture'];dump(report,j);message='deliberate failed'
     if kind=='wrong-id':j=load(report);j['items']={'999999':{'status':'qualified_editable','errors':[]}};dump(report,j);message='ID coverage'
     if kind=='stale-binding':j=load(pkg/'manifest.json');j['scope']='changed after acceptance';dump(pkg/'manifest.json',j);e['manifest_sha256']=core.sha(pkg/'manifest.json');v=load(pkg/'delivery-evidence.json');v['package_manifest_sha256']=e['manifest_sha256'];dump(pkg/'delivery-evidence.json',v);message='does not bind the final packet'
     if kind=='changed-body':(pkg/'items/900001.tex').write_text('changed fixture body');message='changed editable body'
     if kind=='changed-source':(pkg/'sources/900001.tex').write_text('changed fixture source');message='changed/invalid final packet evidence'
     if kind=='changed-artifact':(Path(e['build_root'])/'900001/fixture.pdf').write_bytes(b'changed artifact');message='changed accepted compile artifact'
     self.rejected(spec,message)
    self.directory=before
 def test_3_duplicate_ID_claim_alias_source_DOI_guards(self):
  for kind in ['id','claim','alias','source','doi']:
   with self.subTest(kind=kind):
    top=self.directory/kind;top.mkdir();before=self.directory;self.directory=top;spec=self.prepare();entry=spec['incoming'][0];pkg=Path(entry['package']);m=load(pkg/'manifest.json');ev=load(pkg/'delivery-evidence.json');row=m['items'][0]
    if kind=='id':
     spec['incoming']=[self.make('duplicate-id-input','900000')];self.rejected(spec,'duplicate stable ID');self.directory=before;continue
    if kind=='claim':ev['items']['900001']['claim_key']='fixture-claim-900000';message='duplicate claim'
    if kind=='alias':ev['items']['900001']['historical_claim_key_aliases']=[' FIXTURE-CLAIM-900000 '];message='duplicate claim'
    if kind=='source':row['source_id']='fixture-900000';message='source identity conflict'
    if kind=='doi':
     bm=load(Path(spec['base']['package'])/'manifest.json');bm['items'][0]['primary']['doi']='10.9999/fixture';dump(Path(spec['base']['package'])/'manifest.json',bm);spec['base']['manifest_sha256']=core.sha(Path(spec['base']['package'])/'manifest.json');be=load(Path(spec['base']['package'])/'delivery-evidence.json');be['package_manifest_sha256']=spec['base']['manifest_sha256'];dump(Path(spec['base']['package'])/'delivery-evidence.json',be);row['primary']['doi']='10.9999/fixture';message='same DOI'
    dump(pkg/'manifest.json',m);dump(pkg/'delivery-evidence.json',ev);self.accepted_again(entry);self.rejected(spec,message);self.directory=before
 def test_4_content_collision_unsafe_symlink_existing_output(self):
  for kind in ['collision','unsafe','symlink','existing']:
   with self.subTest(kind=kind):
    top=self.directory/kind;top.mkdir();before=self.directory;self.directory=top;spec=self.prepare();a=Path(spec['base']['package']);b=Path(spec['incoming'][0]['package'])
    if kind=='collision':(a/'shared-note.txt').write_text('one');(b/'shared-note.txt').write_text('two');spec['base']['paths'].append('shared-note.txt');spec['incoming'][0]['paths'].append('shared-note.txt');self.rejected(spec,'conflicting package file')
    if kind=='unsafe':spec['incoming'][0]['paths'].append('../escape');self.rejected(spec,'unsafe package-relative path')
    if kind=='symlink':(b/'linked').symlink_to(a/'license.txt');spec['incoming'][0]['paths'].append('linked');self.rejected(spec,'symlink')
    if kind=='existing':out=self.directory/'rejected';out.mkdir();(out/'keep').write_text('kept');self.bind(spec);self.assertRaisesRegex(ValueError,'output must be new',batch.merge_batch,self.specpath,self.reviewpath,None,out);self.assertEqual((out/'keep').read_text(),'kept')
    self.directory=before
 def test_5_rebuild_or_final_gate_failure_preserves_base_partial_output(self):
  for kind in ['rebuild','gate']:
   with self.subTest(kind=kind):
    top=self.directory/kind;top.mkdir();before=self.directory;self.directory=top;spec=self.prepare();base=Path(spec['base']['package']);snapshot=[(base/n).read_bytes() for n in ['manifest.json','INDEX.md','items/900000.tex']];self.bind(spec)
    if kind=='gate':
     with patch.object(batch,'gate',side_effect=ValueError('injected final gate failure')):self.assertRaisesRegex(ValueError,'injected final gate failure',batch.merge_batch,self.specpath,self.reviewpath,None,self.directory/'output')
    else:
     with patch.object(batch.importlib.util,'module_from_spec',return_value=type('Fail',(),{'rebuild':lambda self,*a: (_ for _ in ()).throw(ValueError('injected rebuild failure'))})()),patch.object(batch.importlib.util,'spec_from_file_location',return_value=type('Spec',(),{'loader':type('Loader',(),{'exec_module':lambda self,mod:None})()})()):self.assertRaisesRegex(ValueError,'injected rebuild failure',batch.merge_batch,self.specpath,self.reviewpath,None,self.directory/'output')
    self.assertEqual(snapshot,[(base/n).read_bytes() for n in ['manifest.json','INDEX.md','items/900000.tex']]);result=load(self.directory/'output/batch-result.json');self.assertEqual(result['status'],'failed_batch_partial_output_retained');self.assertTrue((self.directory/'output/package/manifest.json').exists());self.directory=before

if __name__=='__main__':unittest.main(verbosity=2)
