import pathlib,json,sys,re
P=pathlib.Path(r'C:/Users/20600/Documents/Codex/corpus-repair-20261010/research-line/harness-ready-20261011');O=P/'focused-seeds/AGP';sys.path.insert(0,str(P.parents[1]/'corpus-work/scripts'));import prepared_delivery as d
load=lambda p:json.loads(pathlib.Path(p).read_text(encoding='utf8'))
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
p=O/'AGP-stacks-0EJI/task.json';t=load(p)
for s in t['context_spans']+t['assembly']['body_spans']:
 if s['start_line']==4982 and s['end_line']==5277:s['end_line']=5294
body='\n'.join('\n'.join((P/s['path']).read_text(encoding='utf8').splitlines()[s['start_line']-1:s['end_line']]) for s in t['assembly']['body_spans']);labels=set(re.findall(r'\\label\{([^}]+)\}',body));known=labels|{x['label'] for x in t['assembly']['external_references']};tags={}
for i,s in enumerate((O/'sources/stacks-snapshot-20261011/tags.txt').read_text(encoding='utf8').splitlines(),1):
 if ',' in s:
  tag,label=s.split(',',1);tags[label]=(tag,i)
for lab in set(re.findall(r'\\(?:ref|eqref)\{([^}]+)\}',body))-known:
 key=lab if lab in tags else 'algebraization-'+lab;tag,ln=tags[key];kind=next((k for k in ['definition','theorem','proposition','lemma','equation','section'] if k+'-' in lab),'section');t['assembly']['external_references'].append(dict(label=lab,kind=kind,number=tag,source_span=dict(path='focused-seeds/AGP/sources/stacks-snapshot-20261011/tags.txt',start_line=ln,end_line=ln,label=key),non_load_bearing=True,reason='Classical finite-module completion or quasi-affine sheaf fact in the completed context proof; not the canonical-extension construction.'))
save(p,t);rp=O/'AGP-stacks-0EJI/focused-review.json';r=load(rp);r['context_spans']=t['context_spans'];r['non_load_bearing_references']=[x['label'] for x in t['assembly']['external_references']];r['approved_task_config']=d.task_config(t);save(rp,r)
