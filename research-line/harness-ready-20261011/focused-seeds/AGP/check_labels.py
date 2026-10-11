import pathlib,json,re
P=pathlib.Path(r'C:/Users/20600/Documents/Codex/corpus-repair-20261010/research-line/harness-ready-20261011');O=P/'focused-seeds/AGP';load=lambda p:json.loads(pathlib.Path(p).read_text(encoding='utf8'))
for row in load(O/'READY_TASKS.json'):
 t=load(P/row['task_path']);labels={}
 for s in t['assembly']['body_spans']:
  lines=(P/s['path']).read_text(encoding='utf-8-sig').splitlines()
  for i in range(s['start_line'],s['end_line']+1):
   for lab in re.findall(r'\\label\{([^}]+)\}',lines[i-1].split('%')[0]):labels.setdefault(lab,[]).append((s['path'],i))
 duplicates={k:v for k,v in labels.items() if len(v)>1}
 if duplicates:print(t['task_id'],duplicates)
