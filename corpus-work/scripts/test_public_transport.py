"""Explicit local HTTP fixtures for thin transport; no public restoration claim."""
from pathlib import Path
import argparse, hashlib, http.server, json, shutil, socketserver, subprocess, threading

ROOT=Path('/disks/sata1/yupeng/human-proof-corpus');OWN=ROOT/'candidates/reusable-public-recovery-r001';PYTHON=ROOT/'runtime/python/bin/python';TOOL=OWN/'prepare_public_transport.py'
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--trial-dir',type=Path,required=True);args=parser.parse_args();TRIAL=args.trial_dir.absolute()
if TRIAL.exists() or TRIAL.is_symlink() or not TRIAL.resolve().is_relative_to(OWN):parser.error('fresh trial directory inside owned candidate required')
TRIAL.mkdir(parents=True);REPORTS=TRIAL/'reports';REPORTS.mkdir();SERVER=TRIAL/'explicit-local-http-fixture';SERVER.mkdir()
OLD='1'*40;CURRENT='2'*40;REPOSITORY='AlexenderSokolov/cross-theory-formal-database';PREFIX='editable-corpus';REMOTE=SERVER/REPOSITORY/CURRENT/PREFIX;REMOTE.mkdir(parents=True)
OLD_BYTES=b'unchanged synthetic fixture bytes\n';NEW_BYTES=b'new synthetic fixture bytes\n';(REMOTE/'items').mkdir();(REMOTE/'items/new.bin').write_bytes(NEW_BYTES)
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def row(name,content):return {'path':name,'bytes':len(content),'sha256':hashlib.sha256(content).hexdigest()}
def dump(path,value):path.write_text(json.dumps(value,indent=2)+'\n')
def load(path):return json.loads(path.read_text())
class Handler(http.server.SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory=str(SERVER),**kw)
 def log_message(self,*a):pass
 def do_GET(self):
  if self.path.endswith('/items/redirect.bin'):
   self.send_response(302);self.send_header('Location','/'+REPOSITORY+'/'+CURRENT+'/'+PREFIX+'/items/new.bin');self.end_headers()
  else:super().do_GET()
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();BASE='http://127.0.0.1:'+str(server.server_port);RESULTS=[]
def case(name,mode='normal'):
 p=TRIAL/name;p.mkdir();cache=p/'cache';cache.mkdir();(cache/'items').mkdir()
 if mode=='directory':(cache/'items/old.bin').mkdir()
 elif mode=='symlink':(cache/'items/old.bin').symlink_to(REMOTE/'items/new.bin')
 else:(cache/'items/old.bin').write_bytes(OLD_BYTES if mode!='tamper' else b'changed test cache\n')
 dump(p/'old-filelist.json',{'schema_version':1,'files':[row('items/old.bin',OLD_BYTES)]});dump(p/'current-filelist.json',{'schema_version':1,'files':[row('items/old.bin',OLD_BYTES),row('items/new.bin',NEW_BYTES)]})
 dump(p/'old-public-proof.json',{'status':'test_local_fixture_previous_bytes_only_not_public','verified_corpus_commit':OLD,'public_filelist_sha256':digest(p/'old-filelist.json'),'public_files_verified':1,'cache_root':str(cache)})
 return p
def argv(p,extra=None,test=True):
 result=[str(PYTHON),'-B',str(TOOL),'--commit',CURRENT,'--filelist',str(p/'current-filelist.json'),'--filelist-sha256',digest(p/'current-filelist.json'),'--cache',str(p/'cache'),'--old-filelist',str(p/'old-filelist.json'),'--old-filelist-sha256',digest(p/'old-filelist.json'),'--old-public-proof',str(p/'old-public-proof.json'),'--old-public-proof-sha256',digest(p/'old-public-proof.json'),'--old-commit',OLD,'--output',str(p/'output')]
 if test:result+=['--test-local-http',BASE]
 if extra:
  for flag,value in extra.items():result[result.index(flag)+1]=value
 return result
def run(name,p,expected=None,extra=None,test=True):
 cmd=argv(p,extra,test);q=subprocess.run(cmd,capture_output=True,text=True);(REPORTS/(name+'.stdout')).write_text(q.stdout);(REPORTS/(name+'.stderr')).write_text(q.stderr)
 ok=q.returncode==0 if expected is None else q.returncode!=0 and expected in q.stderr;RESULTS.append({'name':name,'argv':cmd,'exit_code':q.returncode,'expected_met':ok});dump(REPORTS/'ACTUAL_COMMANDS.json',RESULTS);print(name,q.returncode,ok,flush=True);assert ok,q.stdout+q.stderr
try:
 p=case('positive');oldhash=digest(p/'cache/items/old.bin');run('positive',p);receipt=load(p/'output/TRANSPORT_RECEIPT.json');assert receipt['status']=='prepared_test_local_transport_fixture_not_public' and receipt['reused_files']==receipt['downloaded_files']==1 and receipt['files_completed']==2 and receipt['reused_bytes']==len(OLD_BYTES) and receipt['downloaded_bytes']==len(NEW_BYTES)
 assert (p/'output/package/items/old.bin').read_bytes()==OLD_BYTES and (p/'output/package/items/new.bin').read_bytes()==NEW_BYTES and digest(p/'cache/items/old.bin')==oldhash
 assert (p/'output/package/items/old.bin').stat().st_ino!=(p/'cache/items/old.bin').stat().st_ino
 ledger=[json.loads(l) for l in (p/'output/TRANSFER_LEDGER.jsonl').read_text().splitlines()];assert len(ledger)==2 and {x['action'] for x in ledger}=={'reuse_copy2_old_public_proven_bytes','download_test_local_http_fixture'}
 p=case('cache-tamper','tamper');run('cache-tamper',p,'proven old cache bytes changed');assert not (p/'output').exists()
 p=case('wrong-current-pin');run('wrong-current-pin',p,'external pin mismatch',{'--filelist-sha256':'0'*64});assert not (p/'output').exists()
 p=case('wrong-old-proof-pin');run('wrong-old-proof-pin',p,'external pin mismatch',{'--old-public-proof-sha256':'0'*64});assert not (p/'output').exists()
 p=case('old-commit-mismatch');run('old-commit-mismatch',p,'old public proof commit/filelist mismatch',{'--old-commit':'3'*40});assert not (p/'output').exists()
 p=case('existing-output');(p/'output').mkdir();(p/'output/keep.txt').write_text('retain existing output\n');keep=digest(p/'output/keep.txt');run('existing-output',p,'fresh output required');assert digest(p/'output/keep.txt')==keep and len(list((p/'output').iterdir()))==1
 p=case('missing-remote');j=load(p/'current-filelist.json');j['files'].append(row('zz-missing.bin',b'absent\n'));dump(p/'current-filelist.json',j);run('missing-remote',p,'HTTP Error 404');r=load(p/'output/TRANSPORT_RECEIPT.json');assert r['status']=='failed_transport_partial_output_retained_not_qualified' and r['files_completed']==2 and (p/'output/package/items/new.bin').read_bytes()==NEW_BYTES
 p=case('cached-directory','directory');run('cached-directory',p,'ordinary file required');assert not (p/'output').exists()
 p=case('cached-symlink','symlink');run('cached-symlink',p,'symlink path rejected');assert not (p/'output').exists()
 p=case('duplicate-path');j=load(p/'current-filelist.json');j['files'].append(j['files'][0]);dump(p/'current-filelist.json',j);run('duplicate-path',p,'duplicate filelist path');assert not (p/'output').exists()
 p=case('noncanonical-path');j=load(p/'current-filelist.json');j['files'][1]['path']='items/../outside.bin';dump(p/'current-filelist.json',j);run('noncanonical-path',p,'noncanonical filelist path');assert not (p/'output').exists()
 p=case('noncanonical-test-URL');run('noncanonical-test-URL',p,'explicit canonical loopback',{'--test-local-http':'http://localhost:'+str(server.server_port)});assert not (p/'output').exists()
 p=case('redirected-URL');j=load(p/'current-filelist.json');j['files'][1]['path']='items/redirect.bin';dump(p/'current-filelist.json',j);run('redirected-URL',p,'exact commit URL redirect rejected');assert load(p/'output/TRANSPORT_RECEIPT.json')['status']=='failed_transport_partial_output_retained_not_qualified'
 p=case('fixture-proof-rejected-in-production');run('fixture-proof-rejected-in-production',p,'actual exact public full-restoration proof required',test=False);assert not (p/'output').exists()
 summary={'status':'explicit_local_HTTP_transport_tests_passed_not_public','tool_sha256':digest(TOOL),'tests_sha256':digest(Path(__file__)),'positive_files_reused':1,'positive_files_downloaded':1,'copy2_not_hardlinked':True,'negative_cases':len(RESULTS)-1,'all_expected_met':all(x['expected_met'] for x in RESULTS),'partial_download_failures_retained':True,'existing_cache_original_positive_unchanged':True,'actual_public_recovery_performed':False,'actual_SQL_artifact_gate_performed':False,'remote_count_increment':0};dump(REPORTS/'TEST_RESULTS.json',summary);print('TRANSPORT_TEST_PASS',digest(REPORTS/'TEST_RESULTS.json'),flush=True)
finally:server.shutdown();server.server_close();thread.join()
