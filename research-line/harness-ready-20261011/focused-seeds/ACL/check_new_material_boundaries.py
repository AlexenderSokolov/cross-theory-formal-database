import pathlib,json,re,collections
p=pathlib.Path(r'C:/Users/20600/Documents/Codex/corpus-repair-20261010/research-line/harness-ready-20261011')
for f in (p/'focused-seeds/ACL').glob('*/task.json'):
 t=json.loads(f.read_text(encoding='utf-8-sig'))
 if t.get('selected_by')!='ACL-material-production':continue
 txt='\n'.join('\n'.join((p/s['path']).read_text(encoding='utf-8-sig').splitlines()[s['start_line']-1:s['end_line']]) for s in t['assembly']['body_spans']);txt='\n'.join(x.split('%')[0] for x in txt.splitlines()); c=collections.Counter(re.findall(r'\\begin\{([^}]+)\}',txt));c.subtract(re.findall(r'\\end\{([^}]+)\}',txt));bad={k:v for k,v in c.items() if v}
 if bad:print(t['task_id'],bad)