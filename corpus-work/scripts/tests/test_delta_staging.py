"""D01/T04/G01 real-byte fixtures. Trusted unchanged preflight/proof boundary mocked.
No source admission, corpus counts, baseline audit or external publication.
"""
from contextlib import closing
import gzip,hashlib,importlib.util,io,json,os,shutil,sqlite3,stat,subprocess,sys,tempfile,threading,unittest,zipfile
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from unittest.mock import patch
HERE=Path(__file__).resolve().parent; SUPPORT=HERE/'delta-test-support'
sys.path.insert(0,str(SUPPORT))
import prepare_editable_release as release
import prepare_public_transport as transport
import restore_validation_chain as chain
import resume_validation_chain as resume
import stage_corpus_release as stage

def master_helper_source(name):
 # The corpus-work/scripts schema1 file is a CLI adapter. Fixture restoration
 # must use the actual editable-corpus master, never Python import precedence.
 if (SUPPORT/name).is_file():
  source=SUPPORT/name
 elif name=='resume_validation_chain.py' and (HERE/name).is_file():
  source=HERE/name  # New wrapper under test may not yet be deployed to master.
 else:
  candidates=[]
  for ancestor in (HERE,*HERE.parents):
   candidates.extend((ancestor/'editable-corpus',ancestor/'repo/editable-corpus'))
  candidates.extend(Path(value) for value in sys.path if value and Path(value).name=='editable-corpus')
  source=next((root/name for root in candidates if (root/name).is_file()),None)
  if source is None and name!='restore_validation_artifacts.py' and (HERE/name).is_file():source=HERE/name
 if name=='restore_validation_artifacts.py':
  if source is None:raise ValueError('fixture requires exact editable-corpus schema1 master helper')
  spec=importlib.util.spec_from_file_location('_fixture_exact_schema1_master',source)
  module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
  if not callable(getattr(module,'restore',None)):
   raise ValueError('fixture selected schema1 CLI adapter instead of master: '+str(source))
 return source

def dump(p,v):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v)+'\n',encoding='utf8')
def data(ident):
 d={f'build/{ident}/item{ext}':(ident+ext).encode() for ext in ('.pdf','.log','.fls','.aux')}
 d[f'build/{ident}/compiler.log']=b'compiler';d[f'receipts/{ident}.json']=json.dumps({'fixture':ident}).encode();return d
def entry(name,p):return dict(path=name,bytes=p.stat().st_size,sha256=release.sha(p))
def archive(root,files):
 root.mkdir();buffer=io.BytesIO();fmap={}
 with zipfile.ZipFile(buffer,'w') as z:
  for name,b in files.items():
   info=zipfile.ZipInfo(name);info.create_system=3;info.external_attr=(stat.S_IFREG|0o644)<<16;info.compress_type=zipfile.ZIP_DEFLATED
   z.writestr(info,b);fmap[name]=dict(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
  z.writestr('ARTIFACT_FILEMAP.json',json.dumps(fmap))
 zpath=root/'archive.zip';zpath.write_bytes(buffer.getvalue());parts=release.split_parts(zpath,root,'validation-artifact-parts','fresh-build.zip.part-')
 d=dict(schema_version=1,format='ordered zip parts with exact filemap',part_count=len(parts),parts=parts,archive_sha256=release.sha(zpath),archive_bytes=zpath.stat().st_size,file_count=len(fmap),receipt_set_relative='receipts',build_root_relative='build')
 dump(root/'validation-artifact-delivery.json',d);return d

class Tests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.r=Path(self.temp.name);r=self.r
  self.base=r/'old';self.old=archive(self.base,data('001'));dump(self.base/'manifest.json',{'items':[{'problem_id':'001'}]})
  self.oldlist=r/'oldlist.json';names=['manifest.json','validation-artifact-delivery.json',*[p['path'] for p in self.old['parts']]]
  dump(self.oldlist,dict(schema_version=1,files=[entry(n,self.base/n) for n in names]))
  self.proof=r/'proof.json';dump(self.proof,dict(commands=[{},{},{},dict(argv=[sys.executable,'-B',str(self.base/'restore_validation_artifacts.py')])]))
  self.previous=r/'previous.json';dump(self.previous,dict(cache=str(self.base),filelist=str(self.oldlist),public_proof=str(self.proof),commit='1'*40))
  self.master=r/'master';self.master.mkdir()
  for n in release.HELPERS:
   src=master_helper_source(n)
   if src is not None:shutil.copyfile(src,self.master/n)
   else:(self.master/n).write_text('# fixture')
  self.pkg=r/'merged';self.pkg.mkdir();self.manifest={'items':[{'problem_id':'001'},{'problem_id':'002'}]};dump(self.pkg/'manifest.json',self.manifest)
  with closing(sqlite3.connect(self.pkg/'corpus.sqlite')) as db:db.execute('CREATE TABLE full_text(problem_id TEXT,tex_content TEXT)');db.executemany('INSERT INTO full_text VALUES (?,?)',[('001','old proof'),('002','new proof')]);db.commit()
  self.build=r/'build';self.receipts=r/'receipts';self.build.mkdir();self.receipts.mkdir();self.art={};files=[]
  for n,b in data('002').items():
   kind,rel=n.split('/',1);p=(self.build if kind=='build' else self.receipts)/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b);self.art[n]=p;files.append(dict(root=kind,path=rel,sha256=release.sha(p)))
  self.public={'manifest.json':self.pkg/'manifest.json',**{n:self.master/n for n in release.HELPERS}}
  self.review=dict(files=files,master_helper_sha256={n:release.sha(self.master/n) for n in release.HELPERS});self.reviewpath=r/'review.json';dump(self.reviewpath,self.review)
  self.aggregate=r/'aggregate.json';dump(self.aggregate,{'fixture':True});self.out=r/'release'
 def tearDown(self):self.temp.cleanup()
 def prepare(self,ids=None):
  trusted=(self.pkg,self.build,self.receipts,self.master,self.manifest,self.review,self.public,self.art,{'sqlite_sha256':release.sha(self.pkg/'corpus.sqlite')},{'fixture':True})
  with patch.object(release,'preflight',return_value=trusted),patch.object(transport,'verified_previous',return_value={}):
   return release.prepare(self.pkg,self.build,self.receipts,self.aggregate,release.sha(self.aggregate),self.reviewpath,release.sha(self.reviewpath),self.out,self.previous,ids or ['002'])
 def args(self,prep,out):
  p=Path(prep['package']);return (p/'validation-chain.json',prep['validation_chain_sha256'],{k:p/v for k,v in prep['artifact_archive_roots'].items()},p/'restore_validation_artifacts.py',prep['schema1_restore_helper_sha256'],out)
 def test_D01_full_delta_existing_chain_transport_old_download_zero(self):
  prep=self.prepare();p=Path(prep['package']);self.assertEqual(prep['delta_artifact_files'],6);self.assertEqual(prep['artifact_files'],12)
  restored=chain.restore(*self.args(prep,self.r/'fresh'));self.assertEqual(restored['artifact_files'],12)
  for n,b in {**data('001'),**data('002')}.items():self.assertEqual((self.r/'fresh'/n).read_bytes(),b)
  for part in self.old['parts']:self.assertEqual((p/part['path']).read_bytes(),(self.base/part['path']).read_bytes())
  d=json.loads((p/'database-delivery.json').read_text());self.assertEqual(gzip.decompress(b''.join((p/x['path']).read_bytes() for x in d['parts'])),(self.pkg/'corpus.sqlite').read_bytes())
  requests=[]
  class Handler(BaseHTTPRequestHandler):
   def do_GET(h):
    n=h.path.split('/editable-corpus/',1)[1];requests.append(n);h.send_response(200);h.end_headers();h.wfile.write((p/n).read_bytes())
   def log_message(*a):pass
  server=ThreadingHTTPServer(('127.0.0.1',0),Handler);t=threading.Thread(target=server.serve_forever,daemon=True);t.start()
  proof=self.r/'fixture-proof.json';dump(proof,dict(status='test_local_fixture_previous_bytes_only_not_public',cache_root=str(self.base),public_files_verified=len(json.loads(self.oldlist.read_text())['files']),verified_corpus_commit='1'*40,public_filelist_sha256=release.sha(self.oldlist)))
  try:transport.prepare('2'*40,self.out/'PUBLIC_FILELIST.json',prep['public_filelist_sha256'],self.base,self.oldlist,release.sha(self.oldlist),proof,release.sha(proof),'1'*40,self.r/'transport','http://127.0.0.1:'+str(server.server_port),1,0)
  finally:server.shutdown();server.server_close();t.join()
  self.assertFalse(any(n.startswith('validation-artifact-parts/') for n in requests));self.assertNotIn('validation-artifact-delivery.json',requests)
  with patch.object(release,'preflight',side_effect=AssertionError('must not repeat preflight')):self.assertEqual(self.prepare(),prep)
 def test_D01_second_delta_preserves_previous_chain_inode_bytes(self):
  first=self.prepare();first_package=Path(first['package']);old_chain=(first_package/'validation-chain.json').read_bytes()
  next_previous=self.r/'next-previous.json';next_proof=self.r/'next-proof.json'
  argv=[sys.executable,'-B',str(first_package/'resume_validation_chain.py')]
  for ident,relative in first['artifact_archive_roots'].items():argv.extend(['--archive-root',ident+'='+str(first_package/relative)])
  dump(next_proof,dict(commands=[{},{},{},dict(argv=argv)]))
  dump(next_previous,dict(cache=str(first_package),filelist=str(self.out/'PUBLIC_FILELIST.json'),public_proof=str(next_proof),commit='2'*40))
  next_pkg=self.r/'merged-next';shutil.copytree(self.pkg,next_pkg);self.pkg=next_pkg;self.previous=next_previous;self.out=self.r/'release-next'
  self.manifest={'items':[{'problem_id':x} for x in ('001','002','003')]};dump(self.pkg/'manifest.json',self.manifest)
  self.public={'manifest.json':self.pkg/'manifest.json',**{n:self.master/n for n in release.HELPERS}};self.art={};entries=[]
  for name,b in data('003').items():
   kind,relative=name.split('/',1);p=(self.build if kind=='build' else self.receipts)/relative;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b);self.art[name]=p;entries.append(dict(root=kind,path=relative,sha256=release.sha(p)))
  self.review['files']=entries;dump(self.reviewpath,self.review)
  second=self.prepare(['003']);self.assertEqual((first_package/'validation-chain.json').read_bytes(),old_chain)
  restored=chain.restore(*self.args(second,self.r/'second-restored'));self.assertEqual(restored['artifact_files'],18)
  self.assertEqual(len(second['artifact_archive_roots']),3)
 def test_T04_partial_second_archive_reuses_completed_first(self):
  prep=self.prepare();out=self.r/'resume';loader=resume.schema1_module;calls=[]
  def faulty(plan):
   module=loader(plan);original=module.restore
   def run(root,dest):
    calls.append(str(root))
    if len(calls)==2:
     partial=dest/'build/002/item.pdf';partial.parent.mkdir(parents=True);partial.write_bytes(b'partial');raise OSError('fixture interrupted archive2')
    return original(root,dest)
   module.restore=run;return module
  with patch.object(resume,'schema1_module',side_effect=faulty):
   with self.assertRaises(OSError):resume.restore(*self.args(prep,out))
  first=next((out/'stages').glob('00000-*-attempt-001'));stamp=(first/'build/001/item.pdf').stat().st_mtime_ns
  result=resume.restore(*self.args(prep,out));self.assertEqual(result['reused_completed_archives'],1);self.assertEqual((first/'build/001/item.pdf').stat().st_mtime_ns,stamp)
  self.assertEqual(len(list((out/'stages').glob('00001-*-attempt-*'))),2);self.assertEqual(result['artifact_files'],12);self.assertEqual(result['remote_count_increment'],0)
 def test_D01_preflight_incoming_only_never_reads_old_compile_roots(self):
  manifest={'items':[]};evidence={'items':{}};entries=[]
  for ident in ('001','002'):
   item=dict(problem_id=ident,item_path=f'items/{ident}.tex',license_path=f'sources/{ident}/LICENSE',compile_receipt=f'receipts/{ident}.json',primary={},contexts=[],tex_sha256='a'*64)
   manifest['items'].append(item);evidence['items'][ident]=dict(sources=[],bodies=[])
   for name in (item['item_path'],item['license_path'],item['compile_receipt'],f'sources/{ident}/provenance.json'):
    target=self.pkg/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_text('fixture')
  receipt=dict(ok=True,passes=2,shell_escape=False,input_sha256='a'*64,pdf_path='002/item.pdf',compiler_log_path='002/compiler.log',pdf_sha256=release.sha(self.build/'002/item.pdf'),compiler_log_sha256=release.sha(self.build/'002/compiler.log'))
  dump(self.receipts/'002.json',receipt)
  dump(self.pkg/'manifest.json',manifest)
  for name in ('INDEX.md','delivery-evidence.json'):(self.pkg/name).write_text('fixture')
  for path in sorted(self.pkg.rglob('*')):
   if path.is_file() and path.name!='corpus.sqlite':entries.append(dict(root='package',path=path.relative_to(self.pkg).as_posix(),sha256=release.sha(path)))
  entries.extend(dict(root='master_helpers',path=n,sha256=release.sha(self.master/n)) for n in release.HELPERS)
  for name,path in self.art.items():
   kind,relative=name.split('/',1);entries.append(dict(root=kind,path=relative,sha256=release.sha(path)))
  aggregate={'items':{'001':{},'002':{}},'package_item_count':2};dump(self.aggregate,aggregate)
  review=dict(schema_version=1,status='public_filelist_review_complete',package_manifest_sha256=release.sha(self.pkg/'manifest.json'),aggregate_report_sha256=release.sha(self.aggregate),reviewed_package_filemap={},master_helper_sha256={n:release.sha(self.master/n) for n in release.HELPERS},files=entries)
  dump(self.reviewpath,review)
  history={'old_items':{'001':manifest['items'][0]}}
  with patch.object(release.merge,'load_package',return_value=(manifest,evidence)),patch.object(release.merge,'verify_filemap'),patch.object(release.merge,'index_rows'),patch.object(release.delivery,'check_report',return_value={}),patch.object(release,'check_sql',return_value={}):
   result=release.preflight(self.pkg,self.build,self.receipts,self.aggregate,release.sha(self.aggregate),self.reviewpath,release.sha(self.reviewpath),self.r/'preflight-output',self.master,history,['002'])
   self.assertEqual(set(result[7]),set(self.art))
   self.assertFalse((self.build/'001').exists());self.assertFalse((self.receipts/'001.json').exists())
   history['old_items']['001']={**manifest['items'][0],'item_path':'changed.tex'}
   with self.assertRaisesRegex(ValueError,'non-incoming manifest changed'):
    release.preflight(self.pkg,self.build,self.receipts,self.aggregate,release.sha(self.aggregate),self.reviewpath,release.sha(self.reviewpath),self.r/'preflight-output',self.master,history,['002'])
 def test_G01_atomic_staging_and_unrelated_index_rejection(self):
  prep=self.prepare();project=self.r/'project';repo=project/'repo';repo.mkdir(parents=True);subprocess.run(['git','init','-q',str(repo)],check=True)
  for k,v in [('user.email','fixture@example.invalid'),('user.name','Fixture'),('core.autocrlf','false')]:subprocess.run(['git','-C',str(repo),'config',k,v],check=True)
  for row in json.loads(self.oldlist.read_text())['files']:
   target=repo/'editable-corpus'/row['path'];target.parent.mkdir(parents=True,exist_ok=True);os.link(self.base/row['path'],target)
  dump(repo/'handoff/yupeng/PRODUCTION_QUEUE.json',{'fixture':True});subprocess.run(['git','-C',str(repo),'add','--','editable-corpus','handoff'],check=True);subprocess.run(['git','-C',str(repo),'commit','-qm','fixture'],check=True)
  batch=self.r/'batch';batch.mkdir();shutil.copytree(self.out,batch/'release-attempt-001');dump(batch/'publish/result.json',dict(release_root=str(batch/'release-attempt-001')))
  dump(batch/'batch.json',dict(expected_count=2));dump(batch/'merge/batch-result.json',{'fixture':True});dump(batch/'material-review.json',{'fixture':True})
  part=repo/'editable-corpus'/self.old['parts'][0]['path'];stamp=part.stat().st_mtime_ns;result=stage._stage_files(batch,project)
  self.assertGreaterEqual(result['unchanged_public_files_skipped'],2);self.assertEqual(part.stat().st_mtime_ns,stamp);self.assertEqual(json.loads((self.base/'manifest.json').read_text())['items'],[{'problem_id':'001'}]);self.assertIn('restore_validation_chain.py',(repo/'editable-corpus/RECOVERY_CURRENT.md').read_text(encoding='utf8'))
  (repo/'unrelated.txt').write_text('preserve');subprocess.run(['git','-C',str(repo),'add','--','unrelated.txt'],check=True)
  with self.assertRaisesRegex(ValueError,'unrelated staged'):stage._stage_files(batch,project)
if __name__=='__main__':unittest.main()
