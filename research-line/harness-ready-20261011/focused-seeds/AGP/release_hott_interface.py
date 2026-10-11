import pathlib,json
P=pathlib.Path(r'C:/Users/20600/Documents/Codex/corpus-repair-20261010/research-line/harness-ready-20261011');O=P/'focused-seeds/AGP';load=lambda p:json.loads(pathlib.Path(p).read_text(encoding='utf8'))
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
name='AGP-hott-connected-truncated-factorization';p=O/name/'task.json';t=load(p);t['status']='ready_for_assembly';t['engineering_blockers']=[];save(p,t)
pending=load(O/'PENDING_TASKS.json');row=next(x for x in pending if x['task_id']==name);row['status']='ready_for_assembly';ready=load(O/'READY_TASKS.json');ready.append(row);save(O/'READY_TASKS.json',ready);save(O/'PENDING_TASKS.json',[x for x in pending if x['task_id']!=name]);print('Ready',len(ready))
