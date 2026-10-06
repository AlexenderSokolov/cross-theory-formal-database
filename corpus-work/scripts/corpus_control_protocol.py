"""Short shared controller transactions; publication-before-controller handoff."""
import contextlib, datetime, fcntl, json, os, re, tempfile
from pathlib import Path
_LOCKS={}
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def load_json(path):
 def unique(pairs):
  result={}
  for key,value in pairs:
   if key in result:raise ValueError('duplicate JSON key: '+key)
   result[key]=value
  return result
 return json.loads(Path(path).read_text(encoding='utf-8'),object_pairs_hook=unique)
def save_json(path,data):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
 with tempfile.NamedTemporaryFile('w',encoding='utf-8',dir=path.parent,prefix='.'+path.name,delete=False) as f:
  json.dump(data,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno());tmp=f.name
 os.replace(tmp,path)
def require_owner(state,owner,generation=None):
 if isinstance(owner,dict):owner,generation=owner.get('owner'),owner.get('generation')
 p=Path(state)/'owner.json'; current=load_json(p) if p.exists() else {'owner':'current-session','generation':0}
 if not owner or type(generation) is not int or (owner,generation)!=(current.get('owner'),current.get('generation',0)):
  raise ValueError('controller actor rejected: owner/generation differs')
 return current
@contextlib.contextmanager
def file_guard(path,wait=False):
 path=Path(path).absolute();key=str(path)
 if key in _LOCKS:
  _LOCKS[key][1]+=1
  try:yield _LOCKS[key][0]
  finally:_LOCKS[key][1]-=1
  return
 path.parent.mkdir(parents=True,exist_ok=True)
 with path.open('a') as f:
  fcntl.flock(f,fcntl.LOCK_EX if wait else fcntl.LOCK_EX|fcntl.LOCK_NB);_LOCKS[key]=[f,1]
  try:yield f
  finally:_LOCKS.pop(key,None);fcntl.flock(f,fcntl.LOCK_UN)
@contextlib.contextmanager
def controller_guard(state,owner,generation=None):
 with file_guard(Path(state)/'controller.lock',wait=True):
  require_owner(state,owner,generation);yield
@contextlib.contextmanager
def publication_guard(state):
 if str((Path(state)/'controller.lock').absolute()) in _LOCKS:raise ValueError('lock order requires publication before controller')
 with file_guard(Path(state)/'publication.lock'):yield

def transfer_owner(state,expected_owner,expected_generation,new_owner,publication_paths=()):
 state=Path(state)
 with publication_guard(state),file_guard(state/'controller.lock',wait=True):
  old=require_owner(state,expected_owner,expected_generation)
  paths=list(map(Path,publication_paths))
  for p in state.glob('batches/*/publication.json'):
   if p not in paths:paths.append(p)
  for p in [state/'publication-external.json']+[x.parent/'external-write.json' for x in paths]:
   if p.exists() and load_json(p).get('state',load_json(p).get('status')) in ('running','in_flight','unknown'):
    raise ValueError('needs_recovery: previous external write is live or unknown')
  actor={'owner':new_owner,'generation':old.get('generation',0)+1}
  for p in paths:
   if not p.exists():continue
   v=load_json(p)
   if v.get('stage')=='reconciled':continue
   history=v.setdefault('actor_history',[])
   if v.get('actor')!=actor:
    history.append(v['actor']);v['actor']=actor;save_json(p,v)
  record={'schema_version':2,'record_type':'owner',**actor,'previous_owner':old['owner'],'updated_at':now()}
  save_json(state/'owner.json',record);return record

def normalize_key(key):
 if not isinstance(key,str) or not key.strip():raise ValueError('work key required')
 key=key.strip()
 if key.isdecimal():return 'id:'+key
 if key.lower().startswith('id:'):
  value=key[3:]
  if not value.isdecimal():raise ValueError('invalid id work key')
  return 'id:'+value
 for prefix in ('https://doi.org/','http://doi.org/','http://dx.doi.org/','https://dx.doi.org/','doi:'):
  if key.lower().startswith(prefix):return 'doi:'+key[len(prefix):].lower()
 return key

CHECKPOINTS=('cached','source_review','normalized','compiled','page_qa','projected','item_passed')
SOURCE_REASONS={'source_ambiguity','missing_human_proof','source_version_conflict','rights_unresolved','difficulty_insufficient','semantic_duplicate_pending_review','source_access_denied'}
ENGINEERING_REASONS={'result_missing','result_invalid','compile_failure','projection_failure','tool_failure','unknown_execution_outcome','transport_failure','model_quota'}
READY_REFS=('package','ready','build_root','receipt_root','item_report','page_qa','source_map','rights','difficulty')
def validate_result(result,spec,unit_map,check_evidence=True):
 if set(result)!={'schema_version','record_type','job_id','attempt_id','block_id','finished_at','units'} or not isinstance(result.get('finished_at'),str) or not result['finished_at']:raise ValueError('result exact envelope fields required')
 try:
  if not re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})',result['finished_at']):raise ValueError('invalid date-time format')
  stamp=datetime.datetime.fromisoformat(result['finished_at'].replace('Z','+00:00'))
  if stamp.utcoffset()!=datetime.timedelta(0):raise ValueError('finished_at must use UTC')
 except (ValueError,TypeError):raise ValueError('finished_at must be a valid UTC date-time')
 if result.get('schema_version')!=2 or result.get('record_type')!='job_result':raise ValueError('result envelope invalid')
 for key in ('job_id','attempt_id','block_id'):
  if result.get(key)!=spec.get(key):raise ValueError('result '+key+' mismatch')
 units=result.get('units')
 if not isinstance(units,list) or len(units)!=len(spec['unit_ids']):raise ValueError('result unit count mismatch')
 seen=set()
 for u in units:
  required={'problem_id','work_key','revision','disposition','last_completed_stage','next_stage','next_action','reason_code','reason','evidence_refs'}
  if not required<=set(u) or set(u)-required-{'hold_evidence'}:raise ValueError('result exact unit fields required')
  pid=u.get('problem_id')
  if pid in seen or pid not in spec['unit_ids']:raise ValueError('result duplicate/extra unit')
  seen.add(pid)
  if normalize_key(u.get('work_key'))!=normalize_key(unit_map[pid]['work_key']):raise ValueError('result work key mismatch')
  if not isinstance(u.get('revision'),str) or not u['revision'] or not isinstance(u.get('next_action'),str) or not u['next_action'] or not isinstance(u.get('reason'),str):raise ValueError('result unit fields missing')
  stage=u.get('last_completed_stage');next_stage=u.get('next_stage');d=u.get('disposition');refs=u.get('evidence_refs')
  if stage is not None and stage not in CHECKPOINTS:raise ValueError('invalid completed checkpoint')
  if next_stage is not None and next_stage not in CHECKPOINTS:raise ValueError('invalid next checkpoint')
  if not isinstance(refs,dict) or set(refs)-set(READY_REFS)-{'logs'}:raise ValueError('evidence_refs required')
  if any(not isinstance(value,str) or not value for key,value in refs.items() if key!='logs'):raise ValueError('evidence paths must be strings')
  if 'logs' in refs and (not isinstance(refs['logs'],list) or any(not isinstance(v,str) or not v for v in refs['logs'])):raise ValueError('evidence logs must be path list')
  if d=='unfinished':
   if next_stage not in CHECKPOINTS:raise ValueError('unfinished next checkpoint required')
   if stage is not None and CHECKPOINTS.index(next_stage)<=CHECKPOINTS.index(stage):raise ValueError('unfinished cannot repeat completed stage')
  elif d in ('source_hold','engineering_hold'):
   allowed=SOURCE_REASONS if d=='source_hold' else ENGINEERING_REASONS
   if u.get('reason_code') not in allowed or not u.get('reason') or not isinstance(u.get('hold_evidence'),list) or not u['hold_evidence'] or any(not isinstance(v,str) or not v for v in u['hold_evidence']):raise ValueError('specific hold evidence required')
   if d=='source_hold' and next_stage is not None:raise ValueError('source hold cannot auto resume')
  elif d=='ready_for_review':
   if stage!='item_passed' or next_stage is not None or u.get('reason_code') is not None:raise ValueError('READY stage invalid')
   if set(refs)!=set(READY_REFS) or any(not refs.get(k) for k in READY_REFS):raise ValueError('READY evidence references missing')
   if check_evidence:
    for k in READY_REFS:
     if not Path(refs[k]).exists():raise ValueError('READY missing actual '+k)
    from merge_editable_batch import accepted_reports,core
    ready=load_json(refs['ready']);package=Path(refs['package']).resolve()
    declared=ready.get('package',ready.get('final_package'))
    if str(ready.get('problem_id'))!=pid or not declared or Path(declared).resolve()!=package or not re.search(r'(?:^|-)'+re.escape(u['revision'])+r'$',package.name):raise ValueError('READY revision/package mismatch')
    report_ref=ready.get('accepted_report',ready.get('item_report',ready.get('final_item_report')))
    if isinstance(report_ref,dict):report_ref=report_ref.get('path')
    if not isinstance(report_ref,str) or Path(report_ref).resolve()!=Path(refs['item_report']).resolve():raise ValueError('READY item report reference mismatch')
    compile_info=ready.get('compile') if isinstance(ready.get('compile'),dict) else {}
    for key in ('build_root','receipt_root'):
     declared_root=ready.get(key,compile_info.get(key))
     if declared_root is not None and Path(declared_root).resolve()!=Path(refs[key]).resolve():raise ValueError('READY compile root mismatch: '+key)
    manifest=load_json(package/'manifest.json');evidence=load_json(package/'delivery-evidence.json');identity=core.sha(package/'manifest.json')
    if evidence.get('package_manifest_sha256')!=identity:raise ValueError('delivery evidence manifest mismatch')
    declared_identity=ready.get('manifest_sha256',ready.get('package_manifest_sha256',compile_info.get('manifest_sha256')))
    if declared_identity is not None and declared_identity!=identity:raise ValueError('READY declared manifest mismatch')
    items=manifest.get('items',[])
    if len(items)!=1 or str(items[0].get('problem_id'))!=pid:raise ValueError('READY manifest scope mismatch')
    entry={'package':str(package),'build_root':str(Path(refs['build_root']).resolve()),'receipt_root':str(Path(refs['receipt_root']).resolve()),'manifest_sha256':identity,'accepted_report':{'path':str(Path(refs['item_report']).resolve()),'manifest_sha256':identity}}
    accepted_reports(entry,(manifest,evidence))
  else:raise ValueError('invalid disposition')
 if seen!=set(spec['unit_ids']):raise ValueError('result scope mismatch')
 return 'partial' if any(u['disposition']=='unfinished' for u in units) else 'complete'

def assert_publication_guard(state,token):
 from corpus_runtime import identity
 try:pid,start=token.split('/',1);pid=int(pid)
 except (ValueError,AttributeError):raise ValueError('publication guard token invalid')
 x=identity(pid)
 if not x or x['start_time']!=start or Path(x['cwd']).resolve()!=Path(state).resolve():raise ValueError('publication guard is not live/current')
 record=Path(state)/'publication-guard.json'
 if not record.exists() or load_json(record).get('token')!=token:raise ValueError('publication guard identity not registered')
 # A live process must actually hold the named flock, not merely possess a receipt.
 try:
  with (Path(state)/'publication.lock').open('a') as f:
   fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
 except BlockingIOError:return x
 raise ValueError('publication guard does not hold publication lock')
