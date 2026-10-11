import pathlib,json,re
p=pathlib.Path(r'C:/Users/20600/Documents/Codex/corpus-repair-20261010/research-line/harness-ready-20261011'); b='focused-seeds/AGP/sources/hott-book-578b85cc/extracted/book-578b85cc8d586b1677ec4335148adeb443057d24/'
labelpath=b+'main.labelnumbers.first-edition'; labels={}
for i,l in enumerate((p/labelpath).read_text(encoding='utf-8').splitlines(),1):
 m=re.match(r'\\newlabel\{([^}]+)\}\{([^}]+)\}',l)
 if m and not m[1].startswith('cref@'):labels[m[1]]=(i,m[2])
for f in (p/'focused-seeds/ACL').glob('ACL-logic-hott-*/task.json'):
 t=json.loads(f.read_text(encoding='utf-8'));text='\n'.join('\n'.join((p/s['path']).read_text(encoding='utf-8-sig').splitlines()[s['start_line']-1:s['end_line']]) for s in t['assembly']['body_spans']);text='\n'.join(x.split('%')[0] for x in text.splitlines()); owned=set(re.findall(r'\\label\{([^}]+)\}',text));refs={v.strip() for m in re.finditer(r'\\(?:c|C|eq)?ref\{([^}]+)\}',text) for v in m[1].split(',')}-owned
 t['assembly']['external_references']=[]
 for r in sorted(refs):
  if r not in labels:print('missing',t['task_id'],r);continue
  i,n=labels[r];t['assembly']['external_references'].append(dict(label=r,kind='reference',number=n,source_span=dict(path=labelpath,start_line=i,end_line=i,label='original fixed-book reference'),non_load_bearing=True,reason='Original book navigation or standard prerequisite reference; target construction and its local proof chain are retained in body spans.'))
 if 'cumulative-hierarchy' in t['task_id']:t['assembly']['editorial_notes'].append('The author labels the retained proof Sketch of proof. All nine author cases are included, with bisimulation and monic-presentation support; no elaboration has been written by the selector.')
 f.write_text(json.dumps(t,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(t['task_id'],len(refs))