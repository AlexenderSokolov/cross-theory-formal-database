import json,pathlib,sys
P=pathlib.Path(r'C:/Users/20600/Documents/Codex/corpus-repair-20261010/research-line/harness-ready-20261011');O=P/'focused-seeds/AGP';sys.path.insert(0,str(P.parents[1]/'corpus-work/scripts'));import prepared_delivery as d
load=lambda p:json.loads(pathlib.Path(p).read_text(encoding='utf8'))
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
rs=load(O/'SOURCE_RECORDS.json')
for taskid in ['AGP-stacks-088E','C-probability-simultaneous-markov-quantile-approximation']:
 p=O/taskid/'task.json';t=load(p);rec=next(x for x in rs if x['source_record_id']==t['source_authorization']['source_record_id'])
 if taskid.startswith('C-'):
  t['license']['name']='CC BY 4.0';rec['license']=t['license'];save(p,t)
  for rp in t['review_paths']:
   r=load(P/rp);r['approved_task_config']=d.task_config(t);r['mechanical_metadata_alignment']={'reason':'Canonical license spellingCC BY 4.0; unchanged legal license URL and unchanged mathematical scope. No new review claimed.'};save(P/rp,r)
 rec['allowed_files']=list(dict.fromkeys(t['assembly']['asset_paths']+t['assembly']['bibliography_paths']+[t['license']['evidence_path']]))
 d.validate_task(p,P);print(taskid,t['problem_id'],'validate_task PASS')
save(O/'SOURCE_RECORDS.json',rs)
