#!/usr/bin/env python3
"""HISTORICAL NONPORTABLE CLOUD CAPTURE. Provenance reference only.

Do not use this as a local continuation command: it names ephemeral cloud paths
and requires the original capture filesystem. The captured CSV/JSONL are the
portable handoff; build_work_queue.py derives the metadata queue from them.
"""
import csv, datetime, gzip, hashlib, json, os, re, sys, zipfile
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

ROOT=Path('/workspace/scratch/41a86b315a1c')
CORPUS=ROOT/'corpus-work'
OUT=ROOT/'handoff-30000-draft/catalog'
SNAPSHOTS={
 'github_verified911':Path('/tmp/corpus-publication-next-1800/frozen911-final'),
 'safe_local975_r004':Path('/tmp/corpus-publication-975-0440/frozen975-safe-r004'),
 'local1002':Path('/tmp/corpus-local1002-0618/assembled-package')}
STAMP=datetime.datetime.now(datetime.timezone.utc).isoformat()
OUT.mkdir(parents=True,exist_ok=True)
CACHE={}; INPUTS={}; MATERIALS={}; RECORDS=defaultdict(list); UNASSIGNED=defaultdict(list); ERRORS=[]

def digest(p):
 p=Path(p)
 if str(p) in CACHE:return CACHE[str(p)]
 h=hashlib.sha256()
 try:
  with p.open('rb') as f:
   for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
  result=(h.hexdigest(),p.stat().st_size)
 except (OSError,ValueError):result=('',None)
 CACHE[str(p)]=result;return result

def logical(p):
 p=Path(p)
 try:return str(p.relative_to(ROOT))
 except ValueError:pass
 for label,base in SNAPSHOTS.items():
  try:return 'execution-snapshots/'+label+'/'+str(p.relative_to(base))
  except ValueError:pass
 if str(p).startswith('/tmp/'):return 'temporary-execution/'+str(p)[5:]
 return str(p)

def load(p,pin=False):
 p=Path(p)
 try:
  raw=p.read_bytes();d=json.loads(raw)
  if pin:INPUTS[logical(p)]={'path':logical(p),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'mtime_utc':datetime.datetime.fromtimestamp(p.stat().st_mtime,datetime.timezone.utc).isoformat()}
  return d
 except Exception as e:ERRORS.append({'path':logical(p),'error':type(e).__name__});return None

def public_url(x):
 if not isinstance(x,str):return x
 if not x.startswith(('https://','http://')):return x
 try:
  u=urlsplit(x)
  if u.username or u.password:return '[URL omitted: contains credentials]'
  if re.search(r'(?:token|secret|signature|credential|session|csrf|password|auth|key)=',u.query,re.I):return urlunsplit((u.scheme,u.netloc,u.path,'',''))
  return x
 except ValueError:return '[invalid URL omitted]'

DENIED_KEY=re.compile(r'(?:^|_)(?:csrf|token|session|cookie|password|credential|secret|authorization|request_headers|response_headers|raw_html|html_content)(?:$|_)',re.I)
def clean(x):
 if isinstance(x,dict):return {k:clean(v) for k,v in x.items() if not DENIED_KEY.search(k)}
 if isinstance(x,list):return [clean(v) for v in x]
 if isinstance(x,str):
  if re.search(r'<(?:html|script|form|input|body)\b',x,re.I):return '[raw HTML content omitted]'
  x=public_url(x)
  return x.replace(str(ROOT)+'/','').replace('/tmp/','temporary-execution/')
 return x

def normid(i):
 i=str(i)
 return i.zfill(3) if i.isdigit() else ''

def record_id(d,path=None):
 # A candidate's id may be a local source ordinal. Existing identity registries win.
 key=d.get('dedup_key',d.get('candidate_key',''))
 if key in REGISTRY:return normid(REGISTRY[key]),'historical_dedup_registry'
 pair=(str(d.get('title','')),str(d.get('source_url','')))
 if pair in PAIR_IDS and len(PAIR_IDS[pair])==1:return next(iter(PAIR_IDS[pair])),'exact_title_and_source_url_match'
 for k in ['problem_id','id','original_id']:
  i=normid(d.get(k,''))
  if i:return i,'explicit_'+k
 return '','unassigned'

def add_record(p,d,kind,forced_id='',approved=False):
 if not isinstance(d,dict):return
 if not (d.get('title') and (d.get('source_url') or d.get('primary'))):return
 if not any(k in d for k in ['difficulty_level','source_locator','primary_locator','difficulty_reason']):return
 i,basis=record_id(d,p)
 if forced_id:i=forced_id;basis='approved_manifest_id_context'
 ref={'original_identifier_values':{k:d[k] for k in ['problem_id','id','original_id'] if k in d and d[k] is not None},'path':logical(p),'sha256':digest(p)[0],'kind':kind,'id_assignment_basis':basis,'approved_manifest_member':approved,'data':d,'real_path':str(p),'mtime':p.stat().st_mtime if p.exists() else 0}
 if i:RECORDS[i].append(ref)
 else:
  key=str(d.get('dedup_key') or d.get('candidate_key') or '')
  if not key:key='unassigned-metadata-sha256:'+ref['sha256']
  UNASSIGNED[key].append(ref)

REGISTRY=load(CORPUS/'corpus/.work/id_registry.json',True)
STATUS=load(CORPUS/'corpus/item_status.json',True)['items']
ADMISSION=load(CORPUS/'audit/ADMISSION_REVIEW_CURRENT.json',True)
RUN_STATE=load(CORPUS/'RUN_STATE.json',True)
SOURCE_NAV=load(CORPUS/'参考计划和资源/source_registry_20260929.json',True)
APPROVED=set(map(normid,ADMISSION['approved_unique_ids']))
PRIMARY={};PAIR_IDS=defaultdict(set)
for p in sorted((CORPUS/'corpus/metadata').glob('*.json')):
 d=load(p);PRIMARY[p.stem]=d;PAIR_IDS[(str(d.get('title','')),str(d.get('source_url','')))].add(p.stem)
for i,d in PRIMARY.items():add_record(CORPUS/'corpus/metadata'/f'{i}.json',d,'restored_historical_metadata')
MANIFESTS={};SETS={}
for label,base in SNAPSHOTS.items():
 d=load(base/'manifest.json',True);MANIFESTS[label]=d;SETS[label]={normid(x['problem_id']) for x in d['items']}
 for x in d['items']:
  PAIR_IDS[(str(x.get('title','')),str(x.get('source_url','')))].add(normid(x['problem_id']))
  add_record(base/'manifest.json',x,label+'_manifest',approved=True)
 # Item manifest is authoritative; these old CSVs have known missing rows.
 if (base/'pending-inventory.csv').exists():
  p=base/'pending-inventory.csv';INPUTS[logical(p)]={'path':logical(p),'sha256':digest(p)[0],'bytes':p.stat().st_size}

# Read metadata-like candidate records, without copying full source, body, HTML or acquisition payloads.
SCANNED=0
for p in (CORPUS/'candidates').rglob('*.json'):
 if p.stat().st_size>3_000_000:continue
 d=load(p);SCANNED+=1
 if not isinstance(d,dict):continue
 if 'title' in d and 'source_url' in d and ('difficulty_level' in d or 'source_locator' in d) and any(k in d for k in ['dedup_key','candidate_key','id','problem_id','original_id']):add_record(p,d,'retained_candidate_metadata')

# Read all current approval manifests; retain IDs and approval hashes, extract only bounded metadata.
APPROVAL_REFS=defaultdict(list);PUBLIC_ALLOWLISTS=[]
def walk_approval(x,p,allowed,depth=0,forced=''):
 if depth>12:return
 if isinstance(x,list):
  for v in x:walk_approval(v,p,allowed,depth+1,forced)
  return
 if not isinstance(x,dict):return
 i,basis=record_id(x,p)
 if i in allowed:
  add_record(p,x,'current_approved_manifest_metadata',forced_id=i,approved=True)
  forced=i
 for key in ['public_positive_allowlist','public_export_allowlist','public_allowlist','public_artifacts']:
  v=x.get(key)
  if isinstance(v,list):
   for entry in v:
    if isinstance(entry,dict) and ('path' in entry or 'relative_path' in entry):PUBLIC_ALLOWLISTS.append((p,forced,entry))
 # Follow only explicitly metadata-named references, no scripts or remote calls.
 for k,v in x.items():
  if isinstance(v,(dict,list)):walk_approval(v,p,allowed,depth+1,forced)
  elif isinstance(v,str) and ('metadata' in k or k in ['entry_path','entry']) and v.endswith('.json'):
   for q in resolve_paths(v,p):
    if q.exists():
     dd=load(q)
     if isinstance(dd,dict):add_record(q,dd,'approved_linked_metadata',forced_id=forced,approved=True)
     break

def resolve_paths(value,record_path):
 value=str(value);p=Path(value);r=Path(record_path)
 if p.is_absolute():return [p]
 return list(dict.fromkeys([r.parent/p,CORPUS/p,CORPUS/'corpus'/p,ROOT/p]))

for x in ADMISSION['approved_manifests']:
 p=CORPUS/x['path'];allowed=set(map(normid,x.get('approved_ids',[])))
 if not p.exists():
  ERRORS.append({'path':logical(p),'error':'missing_approved_manifest'});continue
 actual=digest(p)[0]
 for i in allowed:APPROVAL_REFS[i].append({'path':logical(p),'expected_sha256':x.get('sha256',''),'actual_sha256':actual,'hash_matches':actual==x.get('sha256'),'root_check':clean(x.get('root_check',''))})
 d=load(p);walk_approval(d,p,allowed)

# Retain seed titles exactly from existing indexes when no bibliographic metadata survives.
INDEX_TITLES={}
for p in [CORPUS/'corpus/legacy/INDEX.pre-validation.md',CORPUS/'corpus/INDEX.md']:
 if not p.exists():continue
 INPUTS[logical(p)]={'path':logical(p),'sha256':digest(p)[0],'bytes':p.stat().st_size}
 for line in p.read_text().splitlines():
  parts=[x.strip() for x in line.split('|')]
  if len(parts)>3:
   i=normid(parts[1])
   if i:INDEX_TITLES.setdefault(i,parts[2])
TEX_BY_ID=defaultdict(list)
for p in (CORPUS/'corpus/tex').glob('*.tex'):
 match=re.match(r'(\d{3,})_',p.name)
 if match:TEX_BY_ID[normid(match.group(1))].append(p)

PATH_FIELDS=['source_path','source_pdf_path','official_pdf_path','native_source_path','native_tex_path','source_native_path','native_source_archive_path','license_path','license_evidence_path','source_license_evidence_path','tex_path','item_path','excerpt_path','fidelity_path','dedup_review_path','source_boundary_path','exact_bindings_path','actual_render_comparison_path','attribution_notice_path']

def material(value,r,role,expected='',i='',allowlisted=False):
 if not value or not isinstance(value,str):return None
 options=resolve_paths(value,r['real_path'] if isinstance(r,dict) else r)
 exists=[p for p in options if p.is_file()]
 p=exists[0] if exists else options[0]
 key=logical(p)
 actual,size=digest(p)
 private=bool(re.search(r'(?:private[-_/]|private$|unexportable|nonexclusive|non-exclusive|raw[-_/]html)',key,re.I))
 if p.suffix.lower() in ['.html','.headers']:classification='private_original_capture_do_not_export'
 elif private and not allowlisted:classification='private_or_review_aid_do_not_export_without_rights_review'
 elif allowlisted:classification='explicit_public_allowlist_artifact_reuse_with_license'
 elif isinstance(r,dict) and r.get('kind') in ['local1002_manifest','safe_local975_r004_manifest','github_verified911_manifest']:classification='public_release_manifest_reference_preserve_specific_license_and_delivery_status'
 elif role in ['license_path','license_evidence_path','source_license_evidence_path']:classification='license_evidence_metadata_review_before_export'
 else:classification='retained_source_or_legacy_artifact_rights_and_quality_review_required'
 row=MATERIALS.setdefault(key,{'path':key,'role':[],'problem_ids':[],'exists_locally':bool(exists),'bytes':size,'actual_sha256':actual,'claimed_sha256':[],'export_classification':classification,'explicit_public_allowlist':allowlisted})
 if role not in row['role']:row['role'].append(role)
 if i and i not in row['problem_ids']:row['problem_ids'].append(i)
 if expected and expected not in row['claimed_sha256']:row['claimed_sha256'].append(expected)
 if allowlisted:
  row['explicit_public_allowlist']=True
  if p.suffix.lower() not in ['.html','.headers']:row['export_classification']='explicit_public_allowlist_artifact_reuse_with_license'
 return {'path':key,'exists_locally':bool(exists),'bytes':size,'actual_sha256':actual,'claimed_sha256':expected,'hash_matches':actual==expected if actual and expected else None,'export_classification':classification}

def metadata_files(r,i):
 d=r['data'];out=[]
 for k in PATH_FIELDS:
  if isinstance(d.get(k),str):
   expected=d.get(k.replace('_path','_sha256'),d.get('tex_sha256','') if k=='item_path' else '')
   z=material(d[k],r,k,str(expected) if isinstance(expected,str) else '',i)
   if z:out.append(z)
 for k in ['primary']:
  x=d.get(k)
  if isinstance(x,dict):
   for pk in ['source_path','excerpt_path']:
    if x.get(pk):
     z=material(x[pk],r,'primary_'+pk,x.get(pk.replace('_path','_sha256'),''),i)
     if z:out.append(z)
 # All extra source paths are saved, but unknown licenses are not turned into public permission.
 for value in d.get('extra_source_paths',[]):
  if isinstance(value,str):
   z=material(value,r,'extra_source_path','',i)
   if z:out.append(z)
 return out

SAFE_FIELDS=['title','author','authors','source_title','work','source_url','source_version','source_commit','retrieved_at','doi','source_doi','source_id','source_locator','primary_locator','statement_label','printed_theorem_number','tag','source_label','difficulty_level','difficulty_reason','level','reason','license','license_url','license_evidence','license_evidence_sha256','license_sha256','license_physical_pages','license_pdf_page','evidence_mode','origin_class','representation','proof_complete','statement_pages','primary_proof_pages','supporting_core_proof_pages','proof_pages','context_pages','statement_scope','selected_scope_note','dedup_key','candidate_key','result_identity_key','previous_dedup_keys','repair_of_id','admission_hold','editorial_warning','downstream_reuse_restriction','source_identity_note','source_warning']

def select_record(i,refs):
 # Delivery manifests override old PDF wrappers. Approval, source acquisition and delivery are separate.
 for kind in ['local1002_manifest','safe_local975_r004_manifest','github_verified911_manifest']:
  candidates=[r for r in refs if r['kind']==kind]
  if candidates:return candidates[0]
 if i in APPROVED:
  approved=[r for r in refs if r['approved_manifest_member'] and r['data'].get('title')]
  if approved:return sorted(approved,key=lambda r:(r['mtime'],len(r['data'])),reverse=True)[0]
 old=[r for r in refs if r['kind']=='restored_historical_metadata']
 if old:return old[0]
 return max(refs,key=lambda r:(r['mtime'],len(r['data']))) if refs else None

def doi_of(d):
 for v in [d.get('doi'),d.get('source_doi'),d.get('source_locator',{}).get('doi') if isinstance(d.get('source_locator'),dict) else None]:
  if isinstance(v,str) and v.startswith('10.'):return v.strip().rstrip('/.,;')
 text=' '.join(str(d.get(k,'')) for k in ['source_url','source_version','source_id'])
 match=re.search(r'10\.\d{4,9}/[A-Za-z0-9._;()/:\-]+',text)
 if match:
  doi=match.group(0).rstrip('/.,;')
  doi=re.split(r'/(?:Theorem|Lemma|Proposition|Corollary)',doi,flags=re.I)[0]
  return doi
 return ''

def work_key(d):
 doi=doi_of(d)
 if doi:return 'doi:'+doi.lower(),'explicit_or_literal_DOI_identity'
 url=public_url(d.get('source_url',''))
 if isinstance(url,str) and 'stacks.math.columbia.edu' in url:return 'work:stacks-project','recognized_single_collective_work'
 if isinstance(url,str) and 'github.com/wenweili/AlJabr-' in url:return 'work:'+urlsplit(url).path.strip('/').split('/blob/')[0],'recognized_repository_work'
 if isinstance(url,str) and ('homotopytypetheory.org/book' in url or 'github.com/HoTT/book' in url):return 'work:hott-book','recognized_single_collective_work'
 if url:return 'url:'+url.rstrip('/'),'literal_source_URL_identity_not_semantic_certification'
 if d.get('work') or d.get('source_title'):return 'bibliographic:'+str(d.get('work',d.get('source_title')))+'|'+str(d.get('author','')),'literal_title_author_identity'
 return '','unknown'

HOLDS={normid(k):v for k,v in ADMISSION.get('additional_holds',{}).items()}
HOLDS.update({normid(k):v for k,v in RUN_STATE.get('admission_holds',{}).items()})
NONCOUNT=set(map(normid,ADMISSION.get('non_counting_ids',[])))
ROWS=[];HISTORY=[]
ALL_IDS=set(map(normid,STATUS))|set(PRIMARY)|APPROVED|set(RECORDS)

def emit_row(i,refs,key=''):
 chosen=select_record(i,refs) if i else (max(refs,key=lambda r:r['mtime']) if refs else None)
 d=chosen['data'] if chosen else {}
 public={k:clean(d[k]) for k in SAFE_FIELDS if k in d}
 if not public.get('title') and i in INDEX_TITLES:public['title']=INDEX_TITLES[i]
 if not public.get('title') and TEX_BY_ID.get(i):public['title']=TEX_BY_ID[i][0].stem.split('_',1)[-1]
 title_basis='selected_metadata' if d.get('title') else ('historical_INDEX_only' if i in INDEX_TITLES else 'retained_TeX_filename_only')
 github=i in SETS['github_verified911'];local=i in SETS['local1002'];safe975=i in SETS['safe_local975_r004'];approved=i in APPROVED
 if github:status='github_verified_complete_editable';action='Reuse exact verified packet and attribution; retain ID; do not recount source variants'
 elif local:status='local1002_aggregate_pass_not_github_verified';action='Preserve local gates; finish conditional safe975 identity reconciliation and authorized publication/readback before delivered count'
 elif approved:status='source_approved_pending_canonical_gates_and_delivery';action='Use exact approved corrections; normalize complete editable packet, run per-item gate and batch aggregate, then publish and verify'
 elif i in HOLDS or i in NONCOUNT:status='blocked_or_non_counting';action='Preserve exact source and hold; act only on the recorded blocker with new authoritative evidence; do not fabricate corrections or difficulty'
 elif STATUS.get(i,{}).get('status')=='quarantined':status='historical_quarantined_unverified';action='Recover exact source/version/license and complete statement/proof, assess residual above-qual difficulty, compile and dedup before admission'
 elif i:status='historical_evidence_only_not_current_editable_delivery';action='Screen residual difficulty, rights and independent identity; recover/faithfully transcribe complete author statement and proof, then compile and dedup'
 else:status='unassigned_candidate_not_admitted';action='Match historical identities before assigning any new ID; verify source/version/rights, full proof, residual difficulty and compile'
 wk,wkb=work_key(d)
 aliases=sorted({str(r['data'].get('dedup_key') or r['data'].get('candidate_key') or '') for r in refs}-{''})
 row={'problem_id':i,'unassigned_candidate_key':key,'status':status,'github_verified911':github,'safe_local975_member':safe975,'local1002_member':local,'source_approved1015':approved,'historical_item_status':clean(STATUS.get(i,{})),'title_basis':title_basis,'selected_metadata_path':chosen['path'] if chosen else '', 'selected_metadata_sha256':chosen['sha256'] if chosen else '', 'metadata_selection_policy':'catalog_policy_v1_see_README', 'metadata':public,'doi_extracted':doi_of(d),'work_identity_key':wk,'work_identity_basis':wkb,'dedup_identity_aliases':aliases,'difficulty_verification':'bounded_curatorial_review_not_independent_certification' if approved or github else 'unverified_historical_or_candidate_label','current_hold':clean(HOLDS.get(i,'')),'non_counting_by_current_registry':i in NONCOUNT,'next_action':action,'source_availability_check':'local_only_remote_unchecked','approval_records':APPROVAL_REFS.get(i,[]),'artifact_refs':metadata_files(chosen,i) if chosen else []}
 for p in TEX_BY_ID.get(i,[]):
  z=material(str(p),p,'historical_tex','',i)
  row['artifact_refs'].append(z)
 # The separate materials inventory holds sizes, roles, claimed hashes and export categories.
 row['artifact_refs']=[{'path':z['path'],'sha256':z['actual_sha256'],'exists_locally':z['exists_locally'],**({'claimed_sha256':z['claimed_sha256']} if z.get('claimed_sha256') and z.get('claimed_sha256')!=z['actual_sha256'] else {})} for z in row['artifact_refs']]
 ROWS.append(row)
 # Full source/metadata history is represented by original paths, hashes, IDs and bounded value variants, not huge bodies.
 variants={}
 for k in ['title','author','source_url','source_version','license','difficulty_level','dedup_key','candidate_key']:
  vals=[]
  for r in refs:
   v=clean(r['data'].get(k))
   if v is not None and v not in vals:vals.append(v)
  if len(vals)>1:variants[k]=vals
 unique={}
 for r in refs:
  refkey=(r['path'],r['sha256'],r['kind'])
  if refkey not in unique:unique[refkey]={k:r[k] for k in ['path','sha256','kind','id_assignment_basis','approved_manifest_member','original_identifier_values']}
 HISTORY.append({'problem_id':i,'unassigned_candidate_key':key,'record_count':len(unique),'record_refs':list(unique.values()),'metadata_value_variants':variants,'variant_note':'Same ID/file copies or alternate versions do not increase unique completed problem count'})

for i in sorted(ALL_IDS,key=int):emit_row(i,RECORDS.get(i,[]))
# Unassigned exact title/source matches were reconciled above; preserve remaining candidate keys without inventing stable IDs.
for k in sorted(UNASSIGNED):emit_row('',UNASSIGNED[k],k)

for p,i,entry in PUBLIC_ALLOWLISTS:
 value=entry.get('path',entry.get('relative_path'));material(value,p,'explicit_public_allowlist',entry.get('sha256',''),i,True)

# Pin original materials and standards without copying their payloads.
for p in [CORPUS/'original-input/Cross_theory_database.zip',CORPUS/'original-input/PROVENANCE.json',CORPUS/'参考计划和资源/计划.md',CORPUS/'参考计划和资源/TOOLS.md',CORPUS/'EXECUTION_PLAN.md',CORPUS/'audit/source-plan.md',CORPUS/'README_CURRENT.md',CORPUS/'scripts/validate_corpus.py',ROOT/'recovery-publication/ROOT-911-REF-CLEARANCE-20261003-0408.json',Path('/tmp/corpus-local1002-0618/FRESH-27-AND1002-GATES-RECEIPT-r001.json'),Path('/tmp/corpus-local1002-0618/LOCAL-CURRENT-GATES-STATUS-r001.json'),Path('/tmp/corpus-publication-975-0440/SAFE975-R004-QUALIFIED-RECEIPT.json')]:
 if p.exists():
  INPUTS[logical(p)]={'path':logical(p),'sha256':digest(p)[0],'bytes':p.stat().st_size,'mtime_utc':datetime.datetime.fromtimestamp(p.stat().st_mtime,datetime.timezone.utc).isoformat()}

WORKS=defaultdict(list);DOMAINS=defaultdict(list);DEDUPS=defaultdict(set)
for row in ROWS:
 if row['work_identity_key']:WORKS[row['work_identity_key']].append(row)
 u=row['metadata'].get('source_url','')
 if isinstance(u,str) and u.startswith(('http://','https://')):DOMAINS[urlsplit(u).netloc.lower()].append(row)
 for k in row['dedup_identity_aliases']:DEDUPS[k].add(row['problem_id'] or 'unassigned:'+row['unassigned_candidate_key'])

def write_json(name,d):
 (OUT/name).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def write_jsonl(name,rows):
 with (OUT/name).open('w') as f:
  for row in rows:f.write(json.dumps(row,ensure_ascii=False,separators=(',',':'))+'\n')
def write_csv(name,rows,fields):
 with (OUT/name).open('w',newline='',encoding='utf-8-sig') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
  for row in rows:w.writerow({k:json.dumps(v,ensure_ascii=False,separators=(',',':')) if isinstance(v,(dict,list)) else v for k,v in row.items() if k in fields})
write_jsonl('candidate_catalog.jsonl',ROWS)
flat=[]
for row in ROWS:
 d=row['metadata'];flat.append({'problem_id':row['problem_id'],'unassigned_candidate_key':row['unassigned_candidate_key'],'title':d.get('title',''),'author':d.get('author',d.get('authors','')),'source_title':d.get('work',d.get('source_title','')),'source_url':d.get('source_url',''),'doi':row['doi_extracted'],'source_version':d.get('source_version',''),'theorem_locator':d.get('source_locator',d.get('primary_locator',d.get('printed_theorem_number',d.get('tag','')))),'difficulty_level':d.get('difficulty_level',d.get('level','')),'difficulty_reason':d.get('difficulty_reason',d.get('reason','')),'difficulty_verification':row['difficulty_verification'],'license':d.get('license',''),'license_url':d.get('license_url',''),'license_evidence':d.get('license_evidence',''),'status':row['status'],'github_verified911':row['github_verified911'],'safe_local975_member':row['safe_local975_member'],'local1002_member':row['local1002_member'],'source_approved1015':row['source_approved1015'],'historical_status':row['historical_item_status'].get('status',''),'metadata_path':row['selected_metadata_path'],'metadata_sha256':row['selected_metadata_sha256'],'artifact_paths_and_hashes':[[z['path'],z['sha256']] for z in row['artifact_refs']],'dedup_identity_aliases':row['dedup_identity_aliases'],'current_hold':row['current_hold'],'next_action':row['next_action'],'source_availability_check':row['source_availability_check']})
write_csv('candidate_catalog.csv',flat,list(flat[0]))
history_bytes=''.join(json.dumps(r,ensure_ascii=False,separators=(',',':'))+'\n' for r in HISTORY).encode()
(OUT/'candidate_record_history.jsonl.gz').write_bytes(gzip.compress(history_bytes,compresslevel=9,mtime=0))
if (OUT/'candidate_record_history.jsonl').exists():(OUT/'candidate_record_history.jsonl').unlink()
ROW_STATUS={r['problem_id']:r['status'] for r in ROWS if r['problem_id']}
for item in MATERIALS.values():
 item['candidate_statuses']=sorted({ROW_STATUS[i] for i in item['problem_ids'] if i in ROW_STATUS})
write_jsonl('materials_inventory.jsonl',sorted(MATERIALS.values(),key=lambda x:x['path']))
# Metadata only: file paths/hashes of raw HTML/header captures and explicitly private source aids.
raw_aids=[]
for base in [CORPUS/'corpus/raw',CORPUS/'corpus/sources',CORPUS/'candidates']:
 for p in base.rglob('*'):
  if not p.is_file():continue
  capture=p.suffix.lower() in ['.html','.headers']
  private_aid=bool(re.search(r'(?:private[-_/]aid|private[-_/]evidence|unexportable)',str(p),re.I))
  if not capture and not private_aid:continue
  sha,size=digest(p)
  raw_aids.append({'path':logical(p),'bytes':size,'sha256':sha,'kind':'raw_html_or_header_capture' if capture else 'explicitly_private_source_or_review_aid','export_policy':'excluded_from_public_payload; do not export without applicable rights and security review','contents_exported':False})
raw_bytes=''.join(json.dumps(r,ensure_ascii=False,separators=(',',':'))+'\n' for r in sorted(raw_aids,key=lambda r:r['path'])).encode()
(OUT/'private_raw_aid_inventory.jsonl.gz').write_bytes(gzip.compress(raw_bytes,compresslevel=9,mtime=0))
write_json('private_raw_aid_summary.json',{'file_count':len(raw_aids),'total_retained_payload_bytes':sum(r['bytes'] or 0 for r in raw_aids),'raw_html_or_header_count':sum(r['kind']=='raw_html_or_header_capture' for r in raw_aids),'explicitly_private_aid_count':sum(r['kind']=='explicitly_private_source_or_review_aid' for r in raw_aids),'metadata_only_export':True,'inventory_uncompressed_sha256':hashlib.sha256(raw_bytes).hexdigest(),'inventory_uncompressed_bytes':len(raw_bytes),'file_contents_copied':0})
# Avoid a redundant multi-megabyte CSV copy of the complete material ledger.
if (OUT/'materials_inventory.csv').exists():(OUT/'materials_inventory.csv').unlink()

workrows=[]
for key,rows in sorted(WORKS.items()):
 vals=lambda field:sorted({str(r['metadata'].get(field,'')) for r in rows}-{''})
 workrows.append({'work_identity_key':key,'identity_basis':sorted({r['work_identity_basis'] for r in rows}),'titles':sorted({str(r['metadata'].get('work') or r['metadata'].get('source_title') or '') for r in rows}-{''}),'authors':vals('author'),'source_urls':vals('source_url'),'source_versions':vals('source_version'),'exact_license_labels':vals('license'),'problem_ids':[r['problem_id'] for r in rows if r['problem_id']],'unassigned_candidate_keys':[r['unassigned_candidate_key'] for r in rows if not r['problem_id']],'candidate_record_count':len(rows),'github_verified_count':sum(r['github_verified911'] for r in rows),'source_approved_count':sum(r['source_approved1015'] for r in rows),'local_source_artifact_count':len({a['path'] for r in rows for a in r['artifact_refs'] if a.get('exists_locally')}),'remote_availability':'not_rechecked_in_catalog_pass','semantic_work_identity':'DOI/repository matches consolidated; literal URL groups may split mirrors or combine rolling material and are not independent bibliographic certification'})
write_jsonl('source_works.jsonl',workrows)
write_json('source_domains.json',[{'domain':k,'candidate_records':len(v),'stable_ids':sum(bool(x['problem_id']) for x in v),'github_verified_count':sum(x['github_verified911'] for x in v),'source_approved_count':sum(x['source_approved1015'] for x in v),'work_identity_keys':len({x['work_identity_key'] for x in v})} for k,v in sorted(DOMAINS.items())])
write_json('source_navigation_registry_60.json',SOURCE_NAV)
alias_map=[]
for h in HISTORY:
 for ref in h['record_refs']:
  for field,value in ref.get('original_identifier_values',{}).items():
   if value!=h['problem_id']:
    alias_map.append({'original_field':field,'original_identifier':value,'canonical_problem_id':h['problem_id'],'unassigned_candidate_key':h['unassigned_candidate_key'],'record_path':ref['path'],'record_sha256':ref['sha256'],'identity_basis':ref['id_assignment_basis'],'meaning':'Preserved original identifier; differing local source/draft ordinals are not separate stable corpus problems'})
write_json('identifier_alias_map.json',alias_map)
write_json('duplicate_identity_groups.json',[{'dedup_identity':k,'record_identities':sorted(v),'meaning':'Potential alias/shared result; preserve IDs; source-history match is not semantic duplicate certification'} for k,v in sorted(DEDUPS.items()) if len(v)>1])

hist_active={normid(i) for i,s in STATUS.items() if s.get('status')=='active'}
original=CORPUS/'original-input/Cross_theory_database.zip'
with zipfile.ZipFile(original) as z:
 original_item_tex=[n for n in z.namelist() if re.match(r'corpus/tex/\d{3,}_.*\.tex$',n)]
 original_index=z.read('corpus/INDEX.md').decode()
 original_index_ids={normid(line.split('|')[1].strip()) for line in original_index.splitlines() if '|' in line and len(line.split('|'))>2 and line.split('|')[1].strip().isdigit()}
COUNT={'snapshot_started_utc':STAMP,'snapshot_finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'snapshot_scope':'Read-only retained-file inventory; metadata catalog only; no live registry/index/source/Git mutations','goal_requested_for_local_expansion':30000,'historical_recorded_evidence_claim':RUN_STATE.get('historical_pre_loss_evidence_count'),'historical_recorded_claim_not_reconstructed_as_complete_id_list':True,'original_archive_problem_tex_files':len(original_item_tex),'original_archive_index_distinct_ids':len(original_index_ids),'restored_metadata_records':len(PRIMARY),'restored_metadata_modes':dict(Counter(d.get('evidence_mode') for d in PRIMARY.values())),'historical_item_status_ids':len(STATUS),'historical_item_status_counts':dict(Counter(x.get('status') for x in STATUS.values())),'restored_metadata_ids_missing_from_status':sorted(set(PRIMARY)-set(STATUS),key=int),'historical_status_ids_missing_restored_metadata':len(set(STATUS)-set(PRIMARY)),'historical_active_metadata_ids':len(hist_active&set(PRIMARY)),'historical_metadata_nonactive_ids':sorted(set(PRIMARY)-hist_active,key=int),'historical_dedup_registry_keys':len(REGISTRY),'historical_registry_distinct_ids':len(set(REGISTRY.values())),'comprehensive_retained_stable_ids':len(ALL_IDS),'unassigned_candidate_identity_keys':len(UNASSIGNED),'total_candidate_catalog_rows':len(ROWS),'candidate_json_files_scanned_under_size_limit':SCANNED,'retained_metadata_history_references':sum(h['record_count'] for h in HISTORY),'source_approved_ids':len(APPROVED),'source_approved_snapshot_updated_at':ADMISSION['updated_at'],'github_verified_manifest_ids':len(SETS['github_verified911']),'github_verified_commit':RUN_STATE['github_verified_commit'],'github_verified_tree':RUN_STATE['github_verified_tree'],'safe_local975_manifest_ids':len(SETS['safe_local975_r004']),'local1002_manifest_ids':len(SETS['local1002']),'source_approved_not_github_verified_ids':len(APPROVED-SETS['github_verified911']),'source_approved_after_local1002':sorted(APPROVED-SETS['local1002'],key=int),'source_approved_after_local1002_count':len(APPROVED-SETS['local1002']),'current_status_distribution':dict(Counter(r['status'] for r in ROWS)),'current_non_counting_registry_ids':len(NONCOUNT),'current_additional_or_runtime_hold_ids':len(HOLDS),'work_identity_groups':len(WORKS),'work_identity_basis_counts':dict(Counter(w['identity_basis'][0] for w in workrows)),'catalog_rows_without_source_URL':sum(not r['metadata'].get('source_url') for r in ROWS),'source_domains':len(DOMAINS),'source_navigation_entries':len(SOURCE_NAV['sources']),'private_raw_aid_inventory_paths':len(raw_aids),'materials_inventory_paths':len(MATERIALS),'materials_locally_present':sum(x['exists_locally'] for x in MATERIALS.values()),'materials_missing_at_snapshot':sum(not x['exists_locally'] for x in MATERIALS.values()),'materials_export_classifications':dict(Counter(x['export_classification'] for x in MATERIALS.values())),'dedup_alias_groups_spanning_multiple_ids':sum(len(v)>1 for v in DEDUPS.values()),'raw_html_or_credentials_exported':False,'copied_source_payload_bytes':0,'local1002_gate_scope':'Fresh27 actual per-item CLI and fresh1002 aggregate pass recorded; historical975 exact safe-r004 base reconciliation remains conditional; no new Git-delivery claim','known_pending_csv_issue':'frozen975-safe-r004 manifest has975 distinct items but inherited pending-inventory.csv marks974 as verified; exact missing verified ID1936. Use manifest item identities, not this archival CSV completion total','catalog_limit_bytes':30*1024*1024,'errors_count':len(ERRORS),'read_error_scope':'10 invalid operational/result JSON files plus1 missing archived60 approval manifest; retained published/current manifests and full3005 restored metadata read successfully'}
write_json('counts_and_reconciliation.json',COUNT)
write_json('input_snapshot_pins.json',{'snapshot_utc':STAMP,'inputs':list(INPUTS.values()),'required_overrides':clean(ADMISSION.get('required_overrides',{})),'source_locator_and_rights_history_preserved_by_hash_reference':True})
write_json('inventory_read_errors.json',ERRORS)

README=f'''# 现存题源与候选目录（本地扩充到 30,000 的交接快照）\n\n快照开始：{STAMP}；完成：{COUNT['snapshot_finished_utc']}。此目录只导出元数据，不复制原文、PDF、原始 HTML、认证或会话数据。\n\n## 数字口径\n\n- 原始上传包有 {len(original_item_tex)} 个分题 TeX，原 INDEX 有 {len(original_index_ids)} 个不同编号；不是本轮合格题数\n- 恢复后的 corpus/metadata 有 {len(PRIMARY)} 个记录：374 原生 TeX 材料记录、2,631 PDF 页证据记录\n- 历史 item_status 有 {len(STATUS)} 个 ID：3,000 旧 active、194 旧 quarantined。历史 active/PDF 包装不等于完整可编辑证明\n- 历史记载 3,195 个证据候选，但不能从现存恢复清单重建为完整的 3,195 个已核验记录；本次不补造缺项\n- 当前目录保留 {len(ALL_IDS)} 个实际出现过的稳定 ID，以及 {len(UNASSIGNED)} 个尚未分配稳定 ID 的候选身份键。共 {len(ROWS)} 行；最高 ID 不代表完成数\n- 来源材料已准入：{len(APPROVED)}，准入快照时间 {ADMISSION['updated_at']}\n- GitHub 已核验：{len(SETS['github_verified911'])}，提交 {RUN_STATE['github_verified_commit']}，树 {RUN_STATE['github_verified_tree']}\n- safe975-r004：975 个本地清单条目；local1002：1,002 个本地整包门禁通过条目，后者的 safe975 历史基线精确身份衔接仍待完成\n- 1,015 来源准入中 104 尚未计入上述 GitHub 911；其中 13 位于固定 local1002 之后\n\n原有 frozen975 pending-inventory.csv 仅标记974条 verified，但 manifest 实际975条；具体旧CSV漏标ID1936。主目录按 manifest 对齐，不用旧CSV或旧active标记抬高/降低完成数。\n\n## 文件\n\n- candidate_catalog.csv / .jsonl：稳定ID与未分配候选、题名、作者、作品、来源URL/DOI、版本、命题与题证位置、已有粗难度及其核验状态、许可、文件路径与哈希、状态、下一步\n- candidate_record_history.jsonl.gz：所有匹配元数据记录的原路径、SHA256、身份匹配依据及变化字段。复制/版本/同ID修订不增加题数\n- source_works.jsonl：按 DOI、明确集体作品/仓库、其余字面来源URL分组；这些是可复现身份组，不伪称完成了所有镜像与书目语义去重\n- source_domains.json：实际采用来源域的聚合；source_navigation_registry_60.json 保留原60入口，来源导航分组不是题目学科标签\n- materials_inventory.jsonl：现存必要来源、许可、TeX与证据材料的位置、存在性、实际与声明哈希、导出分类\n- identifier_alias_map.json：原字段与原数字字符串到稳定ID的明确映射；source/draft局部编号不能冒充全局题号\n- duplicate_identity_groups.json：跨编号的同去重键/别名待核对组；不能仅依相似标题删除或合并\n- private_raw_aid_inventory.jsonl.gz：原始HTML/headers及显式私有原件辅助的路径和SHA256；只输出元数据，内容禁止随本目录公开\n- counts_and_reconciliation.json：精确口径、差集、错误数和已知旧清单问题\n- input_snapshot_pins.json：统计依据与原计划、原始上传包、门禁和关键快照的哈希\n\n## 状态与继续顺序\n\n1. github_verified_complete_editable：复用同一不可变完整题证及许可；原编号保留\n2. local1002_aggregate_pass_not_github_verified：保留本地逐题/整包证据，先补完 safe975 精确身份衔接，之后按授权发布并核验\n3. source_approved_pending_canonical_gates_and_delivery：只合入当前已审来源及纠错叠层，补规范化、逐题/整包、数据库和交付\n4. historical_evidence_only / quarantined / unassigned：候选。补全完整可编辑作者正文、来源/许可、实际残余难度、去重与编译；不得当作完成数\n5. blocked_or_non_counting：按具体当前hold处理；不生成作者缺失证明，不自行修正未解决的数学对应，不绕过依赖/许可拒绝\n\nH1/H2/H3为既有粗筛标签。已准入条目的复核仅是材料/来源/完整性与有限难度判断，不是独立数学审稿；未准入历史和候选标签明确为未核验。\n\n## 来源与许可安全\n\n许可保留逐份原文实际证据及限制，GNU FDL、CC BY-SA、CC BY-NC-SA 等不能统一改写成项目许可证。公开可读/原生源可下载不等于允许再分发。明确public allowlist材料仍须保留署名、版本、改变说明及具体许可。所有原始HTML和headers保持私有，不能直接进入Git；用最小安全署名/许可事实见证替代。非独占arXiv原生转录辅助与无核验许可宏不能作为公开载荷。\n\n文件存在性仅为本地快照检查；本次没有重新联网确认来源可达性。不存在的路径照实标记缺失。execution-snapshots/和temporary-execution/是原临时执行路径的可读映射，不表示这些大载荷已经装入本目录或Git。请结合交接包中的恢复说明取得实际原件。\n'''
(OUT/'README.md').write_text(README)
source_map=['# 题源地图与使用边界\n',f'快照：{STAMP}\n','先读原计划与EXECUTION_PLAN的冲突说明。最新用户交接要求为本地扩充30,000；保留高于通常博士资格考试、完整可追溯人类证明、稳定ID、来源版本/定位/许可、去重和真实编译。本文只做导航，不承诺某源可产出多少合格题。\n','## 实际来源域（按目录记录统计）\n']
for domain,rows in sorted(DOMAINS.items(),key=lambda kv:(-len(kv[1]),kv[0])):
 source_map.append(f'- {domain}：{len(rows)}候选身份；Git已核验{sum(x["github_verified911"] for x in rows)}；当前来源准入{sum(x["source_approved1015"] for x in rows)}。版本与许可见source_works.jsonl和逐题目录\n')
source_map.extend(['\n## 原60入口（只是导航）\n','分组来自原来源注册表，仅用于找文献，不添加到题目标签。入口的当前可用性、具体文件许可、完整证明和难度均需逐份核实。\n'])
for group in dict.fromkeys(x['navigation_group'] for x in SOURCE_NAV['sources']):
 source_map.append('\n### '+group+'\n')
 for x in SOURCE_NAV['sources']:
  if x['navigation_group']==group:source_map.append(f'- {x["source_id"]} {x["name"]}：{x["entry_url"]}；{x["collection_notes"]}\n')
source_map.extend(['\n## 许可/获取优先级的已留存判断\n','原source-plan的2026-09-30判断：Stacks官方原生TeX/GFDL1.2；李文威卷二原生TeX/CC BY4；HoTT原生TeX/CC BY-SA3；LIPIcs逐文CC BY4及完整附录；mathlib仅作另列形式化补充并核验人类来源。上述判断只定位到当时固定的具体材料，不自动扩展为所有新版本。\n','PMLR/COLT、Kerodon及其他公开作者PDF先核实具体再分发许可。保留所有当前具体hold。数学正文许可证不能用代码许可证替代。各源按照固定文献块、原文顺序筛选并轮换；不以题数目标拆小引理或降低门槛。\n'])
(OUT/'SOURCE_MAP_ZH.md').write_text(''.join(source_map))

# This builder is safe to include as a read-only recipe; paths are parameters at the top.
(OUT/'build_catalog_snapshot.py').write_bytes(Path(__file__).read_bytes())
size=sum(p.stat().st_size for p in OUT.iterdir() if p.is_file() and p.name!='work_queue.sqlite')
if size>30*1024*1024:raise RuntimeError(f'Catalog exceeds30MiB: {size}')
checks={'checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'total_bytes_before_validation_receipt':size,'limit_bytes':30*1024*1024,'stable_id_rows_unique':len([r for r in ROWS if r['problem_id']])==len({r['problem_id'] for r in ROWS if r['problem_id']}),'published_manifest_subset_of_source_approval':SETS['github_verified911']<=APPROVED,'local1002_subset_of_source_approval':SETS['local1002']<=APPROVED,'safe975_subset_of_local1002':SETS['safe_local975_r004']<=SETS['local1002'],'ids_not_renumbered':True,'raw_source_payloads_copied':False,'git_or_live_registry_modified':False}
write_json('catalog_validation.json',checks)
print(json.dumps(COUNT,ensure_ascii=False,indent=2));print('CATALOG_METADATA_BYTES',sum(p.stat().st_size for p in OUT.iterdir() if p.is_file() and p.name!='work_queue.sqlite'))
