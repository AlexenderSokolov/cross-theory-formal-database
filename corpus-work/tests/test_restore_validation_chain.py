"""Bounded transport tests; every generated test directory is retained."""
from pathlib import Path
import hashlib,json,os,stat,unittest,uuid,zipfile,io,warnings
import restore_validation_chain as chain
W=Path(__file__).resolve().parent
HELPER=Path(os.environ.get('CORPUS_SCHEMA1_HELPER',str(W.parents[1]/'repo/editable-corpus/restore_validation_artifacts.py')))
RUN=W/'test-runs'/('run-'+uuid.uuid4().hex);RUN.mkdir(parents=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def digest(b):return hashlib.sha256(b).hexdigest()
def dump(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def identity(a,b):return {'archive_id':a,'sha256':digest(b),'bytes':len(b)}
def files(ident,text='old'):
 return {f'build/{ident}/proof.pdf':('PDF-'+text).encode(),f'build/{ident}/proof.log':('LOG-'+text).encode(),f'build/{ident}/proof.fls':('FLS-'+text).encode(),f'build/{ident}/proof.aux':('AUX-'+text).encode(),f'build/{ident}/proof.out':('OUT-'+text).encode(),f'build/{ident}/compiler.log':('COMPILER-'+text).encode(),f'receipts/{ident}.json':json.dumps({'problem_id':ident,'synthetic_transport_fixture':True,'version':text}).encode()}
def archive(root,contents,duplicates=False,symlink_entry=False,duplicate_map=False):
 root.mkdir();fmap={p:{'sha256':digest(b),'bytes':len(b)} for p,b in contents.items()};bio=io.BytesIO()
 with warnings.catch_warnings():
  warnings.simplefilter('ignore',UserWarning)
  with zipfile.ZipFile(bio,'w',zipfile.ZIP_DEFLATED) as z:
   for p,b in contents.items():
    zi=zipfile.ZipInfo(p);zi.create_system=3;zi.external_attr=((stat.S_IFLNK if symlink_entry else stat.S_IFREG)|0o644)<<16;zi.compress_type=zipfile.ZIP_DEFLATED;z.writestr(zi,b)
   if duplicates:z.writestr(next(iter(contents)),next(iter(contents.values())))
   js=json.dumps(fmap,indent=2)
   if duplicate_map:
    key=next(iter(fmap));row=json.dumps(fmap[key]);js='{'+json.dumps(key)+':'+row+','+json.dumps(key)+':'+row+'}'
   z.writestr('ARTIFACT_FILEMAP.json',js+'\n')
 raw=bio.getvalue();parts=[];size=max(1,len(raw)//2);sub=root/'validation-artifact-parts';sub.mkdir()
 for i,st in enumerate(range(0,len(raw),size)):
  rel=f'validation-artifact-parts/archive.part-{i:05}';part=raw[st:st+size];(root/rel).write_bytes(part);parts.append({'index':i,'path':rel,'bytes':len(part),'sha256':digest(part)})
 d={'schema_version':1,'format':'ordered zip parts with exact filemap','part_count':len(parts),'parts':parts,'archive_sha256':digest(raw),'archive_bytes':len(raw),'file_count':len(fmap),'restore_command':'python3 restore_validation_artifacts.py --destination /absolute/new/external/artifacts','receipt_set_relative':'receipts','build_root_relative':'build'};dump(root/'validation-artifact-delivery.json',d);return d
class ChainTests(unittest.TestCase):
 def setUp(self):
  self.w=RUN/self._testMethodName;self.w.mkdir();self.a=files('101');self.b=files('102','new');self.roots={'base':self.w/'base','delta':self.w/'delta'};self.da=archive(self.roots['base'],self.a);self.db=archive(self.roots['delta'],self.b);self.doc=self.document();self.p=self.w/'chain.json';self.out=self.w/'output'
 def document(self):
  final={p:identity('base',b) for p,b in self.a.items()};final.update({p:identity('delta',b) for p,b in self.b.items()});return {'schema_version':2,'format':'ordered schema1 validation archives with explicit final filemap','archives':[{'index':0,'id':'base','delivery_sha256':sha(self.roots['base']/'validation-artifact-delivery.json'),'delivery':self.da},{'index':1,'id':'delta','delivery_sha256':sha(self.roots['delta']/'validation-artifact-delivery.json'),'delivery':self.db}],'final_file_count':len(final),'final_filemap':final}
 def refresh(self):
  for r in self.doc['archives']:
   r['delivery_sha256']=sha(self.roots[r['id']]/'validation-artifact-delivery.json');r['delivery']=json.loads((self.roots[r['id']]/'validation-artifact-delivery.json').read_text())
 def snapshot(self):
  return {str(p):sha(p) for r in self.roots.values() for p in r.rglob('*') if p.is_file() and not p.is_symlink()}
 def run_restore(self):
  dump(self.p,self.doc);return chain.restore(self.p,sha(self.p),self.roots,HELPER,sha(HELPER),self.out)
 def rejected(self):
  before=self.snapshot()
  with self.assertRaises((ValueError,FileNotFoundError,zipfile.BadZipFile)):self.run_restore()
  self.assertFalse(self.out.exists());self.assertFalse(self.out.is_symlink());self.assertEqual(before,self.snapshot())
 def test_additive_roundtrip_real_schema1_helper(self):
  before=self.snapshot();r=self.run_restore();self.assertEqual(r['artifact_files'],14)
  for p,b in {**self.a,**self.b}.items():self.assertEqual((self.out/p).read_bytes(),b)
  self.assertTrue((self.out/'stages/00000-base/RESTORE_RECEIPT.json').is_file());self.assertEqual(before,self.snapshot())
 def changed_delta(self):
  new=self.w/'changed';self.b=files('101','updated');self.db=archive(new,self.b);self.roots['delta']=new;self.doc=self.document()
  for p,b in self.b.items():self.doc['final_filemap'][p]['overrides']=[identity('base',self.a[p])]
 def test_explicit_changed_ID_override_preserves_stage(self):
  self.changed_delta();r=self.run_restore();self.assertEqual(r['artifact_files'],7)
  for p,b in self.b.items():self.assertEqual((self.out/p).read_bytes(),b);self.assertEqual((self.out/'stages/00000-base'/p).read_bytes(),self.a[p])
 def test_missing_override_rejected(self):
  self.changed_delta();del self.doc['final_filemap'][next(iter(self.b))]['overrides'];self.rejected()
 def test_wrong_override_pin_rejected(self):
  self.changed_delta();self.doc['final_filemap'][next(iter(self.b))]['overrides'][0]['sha256']='0'*64;self.rejected()
 def test_missing_part_rejected(self):
  self.da['parts'][0]['path']='validation-artifact-parts/missing';dump(self.roots['base']/'validation-artifact-delivery.json',self.da);self.refresh();self.rejected()
 def test_wrong_parts_order_rejected(self):
  self.da['parts'].reverse();dump(self.roots['base']/'validation-artifact-delivery.json',self.da);self.refresh();self.rejected()
 def test_tampered_part_rejected(self):
  p=self.roots['base']/self.da['parts'][0]['path'];p.write_bytes(p.read_bytes()+b'x');self.rejected()
 def test_wrong_archive_order_rejected(self):
  self.doc['archives'].reverse();self.rejected()
 def test_duplicate_ZIP_path_rejected(self):
  new=self.w/'dupe';self.da=archive(new,self.a,duplicates=True);self.roots['base']=new;self.doc=self.document();self.rejected()
 def test_duplicate_ZIP_filemap_key_rejected(self):
  new=self.w/'dupe-map';self.da=archive(new,self.a,duplicate_map=True);self.roots['base']=new;self.doc=self.document();self.rejected()
 def test_duplicate_final_filemap_JSON_key_rejected(self):
  dump(self.p,self.doc);text=self.p.read_text();key=next(iter(self.a));needle=json.dumps(key)+':';pin=json.dumps(identity('base',self.a[key]));text=text.replace(needle,needle+pin+','+needle,1);self.p.write_text(text);before=self.snapshot()
  with self.assertRaises(ValueError):chain.restore(self.p,sha(self.p),self.roots,HELPER,sha(HELPER),self.out)
  self.assertFalse(self.out.exists());self.assertEqual(before,self.snapshot())
 def test_escape_part_rejected(self):
  self.da['parts'][0]['path']='../escape';dump(self.roots['base']/'validation-artifact-delivery.json',self.da);self.refresh();self.rejected()
 def test_escape_ZIP_path_rejected(self):
  new=self.w/'escape-zip';self.da=archive(new,{'../escape':b'bad'});self.roots['base']=new;self.doc=self.document();self.rejected()
 def test_existing_output_preserved(self):
  self.out.mkdir();s=self.out/'sentinel';s.write_text('preserve');dump(self.p,self.doc)
  with self.assertRaises(ValueError):chain.restore(self.p,sha(self.p),self.roots,HELPER,sha(HELPER),self.out)
  self.assertEqual(s.read_text(),'preserve');self.assertEqual(list(self.out.iterdir()),[s])
 def test_dangling_output_symlink_preserved(self):
  self.out.symlink_to(self.w/'never-created',target_is_directory=True);dump(self.p,self.doc)
  with self.assertRaises(ValueError):chain.restore(self.p,sha(self.p),self.roots,HELPER,sha(HELPER),self.out)
  self.assertTrue(self.out.is_symlink());self.assertFalse((self.w/'never-created').exists())
 def test_unknown_helper_mismatching_external_pin_rejected(self):
  bad=self.w/'bad-helper.py';bad.write_text('raise RuntimeError("must never execute")\n');dump(self.p,self.doc)
  with self.assertRaises(ValueError):chain.restore(self.p,sha(self.p),self.roots,bad,sha(HELPER),self.out)
  self.assertFalse(self.out.exists())
 def test_symlink_part_rejected(self):
  new=self.w/'linked';self.da=archive(new,self.a);self.roots['base']=new;self.doc=self.document();part=new/self.da['parts'][0]['path'];target=self.w/'target.part';target.write_bytes(part.read_bytes());link=new/'validation-artifact-parts/link';link.symlink_to(target);self.da['parts'][0]['path']='validation-artifact-parts/link';dump(new/'validation-artifact-delivery.json',self.da);self.refresh();self.rejected()
 def test_symlink_ZIP_entry_rejected(self):
  new=self.w/'symlink-zip';self.da=archive(new,self.a,symlink_entry=True);self.roots['base']=new;self.doc=self.document();self.rejected()
 def test_undeclared_stage_only_path_rejected(self):
  del self.doc['final_filemap'][next(iter(self.a))];self.doc['final_file_count']-=1;self.rejected()
 def test_explicit_stage_only_path_preserved(self):
  new=self.w/'renamed';self.b={p.replace('/proof.','/proof_v2.'):b for p,b in files('101','renamed').items()};self.db=archive(new,self.b);self.roots['delta']=new;self.doc=self.document();self.doc['final_filemap']={p:identity('delta',b) for p,b in self.b.items()};self.doc['final_file_count']=len(self.b);oldpaths=set(self.a)-set(self.b);self.doc['stage_only_paths']={p:[identity('base',self.a[p])] for p in oldpaths}
  for p in set(self.a)&set(self.b):self.doc['final_filemap'][p]['overrides']=[identity('base',self.a[p])]
  r=self.run_restore();self.assertEqual(r['artifact_files'],7)
  for p in oldpaths:self.assertFalse((self.out/p).exists());self.assertEqual((self.out/'stages/00000-base'/p).read_bytes(),self.a[p])
 def test_caller_pinned_semantic_preserving_helper_revision_supported(self):
  changed=self.w/'trusted-comment-revision.py';changed.write_bytes(HELPER.read_bytes()+b'\n# caller-approved equivalent helper fixture revision\n');dump(self.p,self.doc);r=chain.restore(self.p,sha(self.p),self.roots,changed,sha(changed),self.out);self.assertEqual(r['artifact_files'],14)
if __name__=='__main__':
 print('Retained test run:',RUN);unittest.main(verbosity=2)