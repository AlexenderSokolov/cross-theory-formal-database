import importlib.util,json,tempfile,unittest
from pathlib import Path
P=Path(__file__).parents[1]
def module():
 s=importlib.util.spec_from_file_location('admit_batch',P/'scripts/admit_batch.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
class BatchTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name);self.c=self.root/'corpus';self.c.mkdir();(self.c/'item_status.json').write_text(json.dumps({'schema_version':1,'items':{}}))
 def tearDown(self):self.temp.cleanup()
 def test_thread_bound(self):
  with self.assertRaisesRegex(ValueError,'workers'):module().admit_batch(self.root,[],workers=5)
 def test_duplicate_staged_identity_is_imported_once(self):
  m=module();meta={'dedup_key':'paper:one','id':'241'}
  unique,duplicates=m.unique_specs([('a',meta),('b',meta)])
  self.assertEqual(len(unique),1);self.assertEqual(duplicates,['b'])
 def test_conflicting_duplicate_id_rejected(self):
  with self.assertRaisesRegex(ValueError,'conflicting'):module().unique_specs([('a',{'dedup_key':'x','id':'241'}),('b',{'dedup_key':'x','id':'242'})])
 def test_precompiled_receipt_invalidated_by_source_change(self):
  m=module();(self.c/'raw').mkdir();(self.c/'tex').mkdir();(self.c/'out').mkdir()
  (self.c/'raw/a.txt').write_text('a');(self.c/'tex/241_x.tex').write_text('x');(self.c/'out/a.pdf').write_bytes(b'%PDF-test')
  meta={'tex_path':'tex/241_x.tex','source_path':'raw/a.txt'}
  receipt={'ok':True,'passes':2,'input_sha256':m.sha(self.c/meta['tex_path']),'dependency_sha256':m.dependencies(self.c,meta),'pdf':'out/a.pdf','pdf_sha256':m.sha(self.c/'out/a.pdf')}
  self.assertTrue(m.receipt_current(self.c,meta,receipt));(self.c/'raw/a.txt').write_text('changed');self.assertFalse(m.receipt_current(self.c,meta,receipt))
 def test_next_hundred_boundary(self):
  self.assertEqual(module().next_boundary(308),400);self.assertEqual(module().next_boundary(300),400)
 def staged(self,key,item):
  import hashlib
  raw=self.c/'raw';raw.mkdir(exist_ok=True);source=raw/(key+'.tex');source.write_text('\\begin{theorem}Identity.\\end{theorem}\n\\begin{proof}Reflexivity establishes the identity.\\end{proof}')
  license=raw/'LICENSE';license.write_text('Fixture license')
  stage=self.root/key;stage.mkdir();tex=stage/(key+'.tex');tex.write_text('\\documentclass{article}\\usepackage{amsthm}\\newtheorem{theorem}{Theorem}\\begin{document}'+source.read_text()+'\\end{document}')
  excerpt=stage/(key+'.excerpt.tex');excerpt.write_text(source.read_text())
  meta={'id':item,'dedup_key':'fixture:'+key,'title':key,'author':'Fixture','difficulty_level':'H2','difficulty_reason':'Fixture reviewed reason','source_url':'https://example.com/'+key,'source_version':'fixture-version','retrieved_at':'2026-09-30','source_path':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'tex_path':str(tex),'excerpt_path':str(excerpt),'excerpt_sha256':hashlib.sha256(excerpt.read_bytes()).hexdigest(),'license_path':str(license),'license':'Fixture license','evidence_mode':'native_tex','source_locator':{'start_line':1,'end_line':2},'proof_complete':True,'proof_review':{'reviewed':True,'context_checked':True,'method':'fixture review','note':'Complete fixture source'}}
  p=stage/(key+'.metadata.json');p.write_text(json.dumps(meta));return p
 def test_failed_compiles_remain_quarantined_and_global_writes_serial(self):
  import threading
  from unittest.mock import patch
  m=module();paths=[self.staged('one','241'),self.staged('two','242')];threads=[];original=m.write_json
  def checked(path,data):threads.append(threading.get_ident());return original(path,data)
  with patch.object(m,'write_json',side_effect=checked):result=m.admit_batch(self.root,paths,engine='definitely-no-such-engine',workers=4)
  self.assertEqual(result['final_qualified'],0);self.assertTrue(all(not x['qualified'] for x in result['items']))
  self.assertEqual(set(threads),{threading.get_ident()});self.assertNotIn('| 241 |',(self.c/'INDEX.md').read_text())
  receipts=json.loads((self.c/'.work/compile_report.json').read_text());self.assertEqual(set(receipts),{'241','242'})
 def test_colliding_ids_leave_manifest_and_registry_unchanged(self):
  paths=[self.staged('one','241'),self.staged('two','241')]
  with self.assertRaisesRegex(ValueError,'collision'):module().admit_batch(self.root,paths,engine='definitely-no-such-engine')
  self.assertEqual(json.loads((self.c/'item_status.json').read_text())['items'],{});self.assertFalse((self.c/'.work/id_registry.json').exists())
 @unittest.skipUnless((P/'.tex-cache/formats/xelatex.fmt').is_file(),'fixture requires installed XeTeX format')
 def test_real_parallel_success_failure_boundary_and_resume(self):
  import shutil
  cache=self.root/'.tex-cache';(cache/'formats').mkdir(parents=True);shutil.copyfile(P/'.tex-cache/formats/xelatex.fmt',cache/'formats/xelatex.fmt')
  if (P/'.tex-cache/lm/lm').exists():shutil.copytree(P/'.tex-cache/lm/lm',cache/'lm/lm')
  paths=[self.staged('live'+str(i),str(241+i)) for i in range(4)]
  broken=json.loads(paths[3].read_text());Path(broken['tex_path']).write_text('\\documentclass{article}\\begin{document}\\UndefinedFixtureCommand\\end{document}')
  m=module();first=m.admit_batch(self.root,paths,workers=4,target_count=2)
  self.assertEqual(first['final_qualified'],2);self.assertTrue(first['strict_gate_ok'])
  statuses={r['id']:r for r in first['items']};self.assertTrue(statuses['243']['ready']);self.assertFalse(statuses['244']['qualified'])
  second=m.admit_batch(self.root,paths[:3],workers=4,target_count=3)
  self.assertEqual(second['final_qualified'],3);self.assertTrue(second['strict_gate_ok'])
  statuses={r['id']:r for r in second['items']};self.assertIn('skipped',statuses['241']);self.assertTrue(statuses['243']['receipt_reused'])

 @unittest.skipUnless((P/'.tex-cache/formats/xelatex.fmt').is_file(),'fixture requires installed XeTeX format')
 def test_real_batch_uses_session_intermediates_and_final_fresh_gate(self):
  import shutil
  from unittest.mock import patch
  m=module()
  import validate_corpus as validator
  cache=self.root/'.tex-cache';(cache/'formats').mkdir(parents=True)
  shutil.copyfile(P/'.tex-cache/formats/xelatex.fmt',cache/'formats/xelatex.fmt')
  if (P/'.tex-cache/lm/lm').exists():shutil.copytree(P/'.tex-cache/lm/lm',cache/'lm/lm')
  paths=[self.staged('session'+str(i),str(241+i)) for i in range(2)]
  events=[];ordinary=m.validate
  def fresh(*args,**kwargs):
   events.append(('fresh',validator._validation_cache.get() is None))
   return ordinary(*args,**kwargs)
  def scoped(*args,**kwargs):
   events.append(('session',validator._validation_cache.get() is not None))
   return validator.validate_in_session(*args,**kwargs)
  with patch.object(m,'validate',side_effect=fresh),patch.object(m,'validate_in_session',side_effect=scoped,create=True):
   result=m.admit_batch(self.root,paths,workers=2,target_count=2)
  self.assertEqual(result['final_qualified'],2);self.assertTrue(result['strict_gate_ok'])
  self.assertEqual(events[0],('fresh',True));self.assertEqual(events[-1],('fresh',True))
  self.assertEqual(events[1:-1],[('session',True)]*3)
  self.assertIsNone(validator._validation_cache.get())

 @unittest.skipUnless((P/'.tex-cache/formats/xelatex.fmt').is_file(),'fixture requires installed XeTeX format')
 def test_invalid_index_title_rejected_before_activation_valid_candidate_admitted(self):
  import shutil
  from unittest.mock import patch
  cache=self.root/'.tex-cache';(cache/'formats').mkdir(parents=True)
  shutil.copyfile(P/'.tex-cache/formats/xelatex.fmt',cache/'formats/xelatex.fmt')
  if (P/'.tex-cache/lm/lm').exists():shutil.copytree(P/'.tex-cache/lm/lm',cache/'lm/lm')
  m=module();paths=[self.staged('badpipe','241'),self.staged('badnewline','242'),self.staged('valid','243')]
  for path,title in zip(paths,['Absolute |p| condition','Title\ncontinued']):
   meta=json.loads(path.read_text());meta['title']=title;path.write_text(json.dumps(meta))
  statuses=[];original=m.write_json
  def track(path,data):
   if path.name=='item_status.json':statuses.append({i:x['status'] for i,x in data['items'].items()})
   return original(path,data)
  with patch.object(m,'write_json',side_effect=track):result=m.admit_batch(self.root,paths,workers=2,target_count=3)
  self.assertEqual(result['final_qualified'],1);self.assertTrue(result['strict_gate_ok'])
  items={x['id']:x for x in result['items']}
  for i in ['241','242']:
   self.assertFalse(items[i]['qualified']);self.assertIn('INDEX fields',items[i]['reason'])
   self.assertTrue(all(x.get(i)!='active' for x in statuses))
   self.assertFalse((self.c/'metadata'/f'{i}.json').exists())
  self.assertTrue(items['243']['qualified'])
  self.assertNotIn('| 241 |',(self.c/'INDEX.md').read_text());self.assertIn('| 243 |',(self.c/'INDEX.md').read_text())
