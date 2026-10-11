import pathlib,json
P=pathlib.Path(r'C:/Users/20600/Documents/Codex/corpus-repair-20261010/research-line/harness-ready-20261011');O=P/'focused-seeds/AGP';load=lambda p:json.loads(pathlib.Path(p).read_text(encoding='utf8'))
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
name='AGP-hott-connected-truncated-factorization';p=O/name/'task.json';t=load(p);t['status']='needs_codex';t['engineering_blockers']=['The source reference to an elementary homotopy-fibre exercise needs native external_references.kind=exercise support; do not relabel it as a theorem.'];save(p,t)
ready=load(O/'READY_TASKS.json');row=next(x for x in ready if x['task_id']==name);row['status']='needs_codex';pending=load(O/'PENDING_TASKS.json');pending.append(row);save(O/'PENDING_TASKS.json',pending);save(O/'READY_TASKS.json',[x for x in ready if x['task_id']!=name])
print('Ready',len(ready)-1,'HoTT mathematical preparations3, interface-ready2 pending1')
