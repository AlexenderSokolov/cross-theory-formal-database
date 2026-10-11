import pathlib,json,re
P=pathlib.Path(r'C:/Users/20600/Documents/Codex/corpus-repair-20261010/research-line/harness-ready-20261011');O=P/'focused-seeds/AGP';load=lambda p:json.loads(pathlib.Path(p).read_text(encoding='utf8'))
for row in load(O/'READY_TASKS.json'):
 if row['task_id'] not in ['AGP-stacks-'+x for x in ['07XB','0GI5','0AGG','0CQ8','0DPT','0EJI','0DLN']]:continue
 t=load(P/row['task_path']);stack=[];errors=[]
 for s in t['assembly']['body_spans']:
  lines=(P/s['path']).read_text(encoding='utf8').splitlines()
  for ln in range(s['start_line'],s['end_line']+1):
   text=lines[ln-1].split('%')[0]
   for kind,env in re.findall(r'\\(begin|end)\{([^}]+)\}',text):
    if kind=='begin':stack.append((env,ln))
    elif not stack or stack[-1][0]!=env:errors.append((kind,env,ln,stack[-1] if stack else None))
    else:stack.pop()
 if stack or errors:print(t['task_id'],'unclosed',stack,'mismatch',errors[:8])
