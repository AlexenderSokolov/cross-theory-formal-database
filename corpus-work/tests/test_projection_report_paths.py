"""Retained real-package regression for projection-report namespaces only."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,sqlite3,sys,traceback,copy
ROOT=Path('/disks/sata1/yupeng/human-proof-corpus')
OWN=ROOT/'candidates/native-engineering-r001/projection-report-path-r001'
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--trial-dir',type=Path,required=True)
parser.add_argument('--checks',choices=['merge-only','all'],default='all')
args=parser.parse_args()
TRIAL=args.trial_dir.absolute()
if TRIAL.exists() or not TRIAL.resolve().is_relative_to(OWN):
 parser.error('trial must be fresh inside owned candidate')
TRIAL.mkdir();REPORTS=TRIAL/'reports';REPORTS.mkdir()
PY=ROOT/'runtime/python/bin/python';SCRIPTS=ROOT/'repo/corpus-work/scripts';MASTER=ROOT/'repo/editable-corpus'
TOOL=Path(__file__).resolve().parents[1]/'scripts/sync_editable_projections.py'
sys.dont_write_bytecode=True;sys.path.insert(0,str(SCRIPTS))
from merge_editable_packages import load_package,validate_union,copy_inputs,verify_filemap
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def inventory(p):return {f.relative_to(p).as_posix():sha(f) for f in p.rglob('*') if f.is_file()}
def dump(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
PINS=TRIAL/'helper-pins.json'
dump(PINS,{'schema_version':1,'master_helper_sha256':{n:sha(MASTER/n) for n in ['schema.sql','rebuild_database.py','restore_database.py','test_database.py','test_restore_database.py']},'programme_sha256':{n:sha(SCRIPTS/n) for n in ['corpus_delivery_tools.py','merge_editable_packages.py','editable_delivery.py']}})
RESULTS=[];COMMANDS=[]
def fixture(ident,legacy=True):
 w='worker-02-1475' if ident=='1475' else 'worker-04-1479'
 origin=ROOT/'candidates/server-workers/parallel12-r001'/w/'next-native-close-r006'
 p=TRIAL/'inputs'/ident
 shutil.copytree(origin/'restored-r006/package',p)
 if legacy:shutil.copy2(origin/'package/PROJECTION_PREPARATION.json',p/'PROJECTION_PREPARATION.json')
 return p
INPUTS={i:fixture(i) for i in ['1475','1479']}
BEFORE={i:inventory(p) for i,p in INPUTS.items()}
OUT={}
def sync(p,out,name,expected_error=None,pin=None):
 cmd=[str(PY),'-B',str(TOOL),'--package',str(p),'--manifest-sha256',pin or sha(p/'manifest.json'),'--master-helpers',str(MASTER),'--helper-pins',str(PINS),'--helper-pins-sha256',sha(PINS),'--output',str(out)]
 z=subprocess.run(cmd,capture_output=True,text=True)
 (REPORTS/(name+'.stdout')).write_text(z.stdout);(REPORTS/(name+'.stderr')).write_text(z.stderr)
 COMMANDS.append({'name':name,'command':cmd,'exit_code':z.returncode})
 dump(REPORTS/'ACTUAL_COMMANDS.json',COMMANDS)
 if expected_error:
  assert z.returncode!=0 and expected_error in z.stderr,(z.stdout,z.stderr);assert not out.exists();return
 assert z.returncode==0,(z.stdout,z.stderr)
 return json.loads(z.stdout)
for i,p in INPUTS.items():
 out=TRIAL/('output-'+i);result=sync(p,out,'sync-'+i);OUT[i]=(out,result)
def run_case(name,fn):
 try:
  detail=fn();RESULTS.append({'name':name,'passed':True,'detail':detail})
 except Exception as exc:
  (REPORTS/(name+'.traceback')).write_text(traceback.format_exc())
  RESULTS.append({'name':name,'passed':False,'error':str(exc),'exception':type(exc).__name__})
 dump(REPORTS/'RESULTS.json',RESULTS)
 print(name,RESULTS[-1]['passed'],flush=True)
def actual_two_packet_merge():
 packages=[load_package(OUT[i][0]) for i in ['1475','1479']]
 assert validate_union(packages)=={'1475','1479'}
 dest=TRIAL/'real-two-packet-preflight-copy';dest.mkdir()
 maps={}
 for ident in ['1475','1479']:
  p=OUT[ident][0];maps[ident]=inventory(p);verify_filemap(p,maps[ident]);copy_inputs(p,dest,maps[ident])
 for ident in ['1475','1479']:
  p=OUT[ident][0]
  assert sha(dest/'items'/(ident+'_alco_'+('175' if ident=='1475' else '182')+'.tex'))==sha(p/'items'/(ident+'_alco_'+('175' if ident=='1475' else '182')+'.tex'))
 dump(REPORTS/'REAL_TWO_PACKET_MERGE_PREFLIGHT.json',{'actual_validate_union':True,'actual_verify_filemap_and_copy_inputs':True,'IDs':['1475','1479'],'all_files_copied_without_conflict':True,'filemaps':maps,'destination':str(dest),'count_promoted':False})
 return {'guard_program_sha256':sha(SCRIPTS/'merge_editable_packages.py'),'copied_files':len(inventory(dest))}
run_case('two-single-real-merge-preflight',actual_two_packet_merge)
if args.checks=='all':
 def single_names_and_legacy():
  detail={}
  for ident in ['1475','1479']:
   p,result=OUT[ident];relative='sources/'+ident+'/PROJECTION_PREPARATION.json'
   assert result['report_path']==relative and (p/relative).is_file()
   assert not (p/'PROJECTION_PREPARATION.json').exists()
   old=INPUTS[ident]/'PROJECTION_PREPARATION.json';history=p/'sources'/ident/'projection-preparation-history'/(sha(old)+'.json')
   assert sha(history)==sha(old)
   assert inventory(INPUTS[ident])==BEFORE[ident]
   detail[ident]={'report':relative,'legacy_path':str(history.relative_to(p)),'legacy_byte_SHA':sha(old),'complete_input_inventory_unchanged':True}
  dump(REPORTS/'LEGACY_AND_INPUT_IDENTITY.json',detail)
  return detail
 run_case('single-namespace-legacy-bytes-input-unchanged',single_names_and_legacy)
 def nested_report_history():
  src=OUT['1475'][0];before=inventory(src);oldreport=src/'sources/1475/PROJECTION_PREPARATION.json';oldhash=sha(oldreport)
  out=TRIAL/'resynced-1475';result=sync(src,out,'resync-canonical-report')
  assert result['report_path']=='sources/1475/PROJECTION_PREPARATION.json'
  assert sha(out/'sources/1475/projection-preparation-history'/(oldhash+'.json'))==oldhash
  assert inventory(src)==before
  return {'prior_canonical_report_byte_SHA':oldhash,'input_inventory_unchanged':True}
 run_case('canonical-report-preserved-on-resync',nested_report_history)
 def multi_names():
  base=TRIAL/'multi-input-A';base.mkdir()
  for i in ['1475','1479']:
   origin=INPUTS[i];fmap={n:h for n,h in inventory(origin).items() if n!='PROJECTION_PREPARATION.json'}
   copy_inputs(origin,base,fmap)
  manifests=[json.loads((INPUTS[i]/'manifest.json').read_text()) for i in ['1475','1479']]
  evidence=[json.loads((INPUTS[i]/'delivery-evidence.json').read_text()) for i in ['1475','1479']]
  m={'schema_version':1,'verified_count':2,'scope':'Report namespace regression batch A, no admission','items':[x for z in manifests for x in z['items']]}
  dump(base/'manifest.json',m)
  e={'schema_version':1,'package_manifest_sha256':sha(base/'manifest.json'),'items':{k:v for z in evidence for k,v in z['items'].items()}}
  dump(base/'delivery-evidence.json',e)
  # A retained legacy preparation receipt belongs to the earlier input; it is metadata only.
  shutil.copy2(INPUTS['1475']/'PROJECTION_PREPARATION.json',base/'PROJECTION_PREPARATION.json')
  other=TRIAL/'multi-input-B';shutil.copytree(base,other)
  m2=copy.deepcopy(m);m2['scope']='Report namespace regression batch B, no admission';dump(other/'manifest.json',m2)
  e2=copy.deepcopy(e);e2['package_manifest_sha256']=sha(other/'manifest.json');dump(other/'delivery-evidence.json',e2)
  resultpaths=[]
  for label,inp in [('A',base),('B',other)]:
   before=inventory(inp);out=TRIAL/('multi-output-'+label);result=sync(inp,out,'multi-'+label)
   expected='reports/projection-preparation-'+sha(inp/'manifest.json')+'.json'
   assert result['report_path']==expected and (out/expected).is_file()
   assert not (out/'PROJECTION_PREPARATION.json').exists()
   old=inp/'PROJECTION_PREPARATION.json';history=out/'reports/projection-preparation-history'/(sha(old)+'.json')
   assert sha(history)==sha(old) and inventory(inp)==before
   with sqlite3.connect(out/'corpus.sqlite') as db:assert db.execute('select count(*) from problems').fetchone()[0]==2 and db.execute('pragma integrity_check').fetchone()[0]=='ok'
   resultpaths.append(expected)
  assert resultpaths[0]!=resultpaths[1]
  dump(REPORTS/'MULTI_MANIFEST_NAMES.json',{'paths':resultpaths,'complete_manifest_hash_in_each_name':True,'both_two_item_full_SQL_projections':True,'original_inputs_unchanged':True,'duplicate_ID_admission_not_claimed':True})
  return resultpaths
 run_case('multi-full-manifest-unique-report-names',multi_names)
 def existing_collision_guard():
  a=TRIAL/'collision-A';bb=TRIAL/'collision-B'
  shutil.copytree(OUT['1475'][0],a);shutil.copytree(OUT['1479'][0],bb)
  (a/'unrelated-collision.json').write_text('first preserved input\n');(bb/'unrelated-collision.json').write_text('different preserved input\n')
  validate_union([load_package(a),load_package(bb)])
  dest=TRIAL/'still-rejected-conflict';dest.mkdir();copy_inputs(a,dest,inventory(a))
  try:copy_inputs(bb,dest,inventory(bb))
  except ValueError as exc:assert 'conflicting package file: unrelated-collision.json' in str(exc);return {'existing_nonreport_collision_guard':'still rejected'}
  raise AssertionError('real merge guard accepted conflicting non-report bytes')
 run_case('existing-file-collision-guard-not-relaxed',existing_collision_guard)
 def wrong_pin():
  sync(INPUTS['1475'],TRIAL/'bad-pin-output','wrong-pin','external reviewed manifest pin mismatch','0'*64)
  return 'wrong manifest pin rejected before output'
 run_case('existing-manifest-pin-guard',wrong_pin)
 def body_guard():
  p=TRIAL/'bad-body-input';shutil.copytree(INPUTS['1475'],p)
  e=json.loads((p/'delivery-evidence.json').read_text());e['items']['1475']['bodies'][0]['tex_sha256']='0'*64;dump(p/'delivery-evidence.json',e)
  sync(p,TRIAL/'bad-body-output','bad-body','source/body/comparison declaration invalid')
  return 'wrong original body hash rejected'
 run_case('existing-body-hash-guard',body_guard)
 def receipt_guard():
  p=TRIAL/'bad-receipt-input';shutil.copytree(INPUTS['1475'],p)
  q=json.loads((p/'receipts/1475.json').read_text());q['ok']=False;dump(p/'receipts/1475.json',q)
  sync(p,TRIAL/'bad-receipt-output','bad-receipt','failing or inconsistent actual compile receipt')
  return 'failed compile receipt still rejected'
 run_case('existing-actual-receipt-guard',receipt_guard)
 def source_and_ID_guards():
  a=load_package(OUT['1475'][0]);b=load_package(OUT['1479'][0])
  try:validate_union([a,a])
  except ValueError as exc:assert 'duplicate stable ID' in str(exc)
  else:raise AssertionError('duplicate ID accepted')
  bad=copy.deepcopy(b)
  for k in ['source_id','work','source_url','source_version','retrieved_at','license','license_path']:bad[0]['items'][0][k]=a[0]['items'][0][k]
  bad[0]['items'][0]['author']='Deliberately conflicting metadata regression only'
  try:validate_union([a,bad])
  except ValueError as exc:assert 'source identity conflict' in str(exc)
  else:raise AssertionError('conflicting source metadata accepted')
  return 'real duplicate stable-ID and source-conflict guards reject'
 run_case('existing-source-and-ID-guards',source_and_ID_guards)
assert all(inventory(p)==BEFORE[i] for i,p in INPUTS.items())
summary={'status':'targeted_report_namespace_checks_passed' if all(z['passed'] for z in RESULTS) else 'targeted_report_namespace_checks_failed','tool_sha256':sha(TOOL),'test_sha256':sha(Path(__file__)),'trial':str(TRIAL),'checks':RESULTS,'input_inventory_exact_unchanged':True,'old_real_fixtures_byte_identities':BEFORE,'master_helper_pin_record_sha256':sha(PINS),'actual_commands':str(REPORTS/'ACTUAL_COMMANDS.json'),'no_main_Git_math_receipt_runtime_or_count_mutation':True}
dump(REPORTS/'SUMMARY.json',summary)
raise SystemExit(0 if all(z['passed'] for z in RESULTS) else 1)
