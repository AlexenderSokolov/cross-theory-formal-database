import pathlib,json,re,collections
p=pathlib.Path(r'C:/Users/20600/Documents/Codex/corpus-repair-20261010/research-line/harness-ready-20261011')
for f in (p/'focused-seeds/ACL').glob('ACL-logic-hott-*/task.json'):
 t=json.loads(f.read_text(encoding='utf-8')); print(t['task_id'])
 for s in t['assembly']['body_spans']:
  ls=(p/s['path']).read_text(encoding='utf-8-sig').splitlines();txt='\n'.join(x.split('%')[0] for x in ls[s['start_line']-1:s['end_line']]); c=collections.Counter(re.findall(r'\\begin\{([^}]+)\}',txt));c.subtract(re.findall(r'\\end\{([^}]+)\}',txt)); bad={k:v for k,v in c.items() if v};
  if bad:print(s['start_line'],s['end_line'],bad,ls[s['start_line']-1],ls[s['end_line']-1])
  if s['role'] in ['statement','proof']:print('boundary',s['role'],ls[s['start_line']-1],ls[s['end_line']-1])