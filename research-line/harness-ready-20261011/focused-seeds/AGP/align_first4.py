import json,pathlib,sys,datetime
P=pathlib.Path(r'C:/Users/20600/Documents/Codex/corpus-repair-20261010/research-line/harness-ready-20261011');O=P/'focused-seeds/AGP';sys.path.insert(0,str(P.parents[1]/'corpus-work/scripts'));import prepared_delivery as d
load=lambda p:json.loads(pathlib.Path(p).read_text(encoding='utf-8-sig'))
def save(p,x):pathlib.Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
records=load(O/'SOURCE_RECORDS.json')
for name in ['A-2007-semisimple-universal-compatibility','A-2039-associahedral-magic-formula','A-2870-double-affine-mv-crystals','C-probability-uniform-recombination-chaos']:
 tp=O/name/'task.json';t=load(tp);oldpath=t['license']['evidence_path'];e=load(P/oldpath)
 p=tp.parent/'license-acceptance.json';save(p,{'status':'supported','source_id':t['source_id'],'source_version':t['source_version'],'license':'CC BY 4.0','version_url':t['license']['version_url'],'evidence_basis':'Metadata acceptance of existing article-specific publisher license observation; no new network/license verification claimed.','inherited_evidence_path':oldpath,'inherited_observation':e})
 t['license']['name']='CC BY 4.0';t['license']['evidence_path']=p.relative_to(P).as_posix();save(tp,t)
 for rp in t['review_paths']:
  r=load(P/rp);r['approved_task_config']=d.task_config(t);r['mechanical_metadata_alignment']={'reason':'Existing publisher license observation accepted in explicit supported schema; canonical spacing of license name. Root-assigned real ID retained. No mathematical source/scope change and no new review claimed.','source_evidence':oldpath};save(P/rp,r)
 for rec in records:
  if rec['source_record_id']==t['source_authorization']['source_record_id']:
   rec['license']=t['license'];rec['allowed_files']=list(dict.fromkeys(t['assembly']['asset_paths']+t['assembly']['bibliography_paths']+[t['license']['evidence_path']]))
 try:d.validate_task(tp,P);print(name,'PASS')
 except Exception as ex:print(name,type(ex).__name__,str(ex))
save(O/'SOURCE_RECORDS.json',records)
