import pathlib,json,re
P=pathlib.Path(r'C:/Users/20600/Documents/Codex/corpus-repair-20261010/research-line/harness-ready-20261011');O=P/'focused-seeds/AGP'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,t):p.write_text(json.dumps(t,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def rebuild(t):t['assembly']['body_spans']=[dict(role=r,**s) for r in ['context','statement','proof'] for s in t[r+'_spans']]
def addspan(t,role,a,b,label='Additional original context/support'):
 s=dict(t['statement_spans'][0]);s.update(start_line=a,end_line=b,label=label);t[role+'_spans'].append(s)
f=O/'AGP-probability-leaf-growth-ghp/task.json';t=load(f)
t['context_spans'][1].update(start_line=451,end_line=472);t['context_spans'][3].update(start_line=572,end_line=592)
t['proof_spans'][0]['end_line']=570;t['proof_spans'][1]['end_line']=618
addspan(t,'context',154,243,'Original explanatory tree figure');addspan(t,'context',332,362,'Original building-scheme definitions')
asset=pathlib.Path(r'C:/Users/20600/Documents/Codex/corpus-repair-20261010/editable-corpus/assets/2413/curien-et-al_figures/fonctionc.pdf');import shutil
out=O/'sources/probability-continuation-20261011/fonctionc.pdf';shutil.copyfile(asset,out)
t['assembly']['asset_paths']=[{'path':out.relative_to(P).as_posix(),'target':'items/fonctionc.pdf'}]
rebuild(t);save(f,t)
# Preserve exact original references used only in retained navigation / declared foundational inputs.
for f in O.glob('AGP-probability-pinning-*/task.json'):
 t=load(f)
 if 'critical-curve' in t['task_id']:addspan(t,'context',197,206,'Original beta-zero criterion')
 if 'large-beta' in t['task_id']:addspan(t,'proof',1549,1591,'Cited standard renewal facts retained verbatim')
 if 'annealed-exponent' in t['task_id']:addspan(t,'proof',1781,1811,'Original Tauberian support lemma')
 rebuild(t);src=P/t['statement_spans'][0]['path'];ls=src.read_text(encoding='utf-8-sig').splitlines();full='\n'.join(ls)
 body='\n'.join('\n'.join(ls[s['start_line']-1:s['end_line']]) for s in t['assembly']['body_spans'])
 labels=set(re.findall(r'\\label\{([^}]+)\}',body));refs=set(re.findall(r'\\(?:eqref|ref)\{([^}]+)\}',body));needed=refs-labels
 sec=0;sub=0;theo=0;current=None;mapping={};envs={'prop':'proposition','theo':'theorem','lemm':'lemma','remark':'remark','conj':'theorem'}
 for i,line in enumerate(ls,1):
  if re.search(r'\\section\{',line):sec+=1;sub=0;theo=0;current=('section',str(sec))
  if re.search(r'\\subsection\{',line):sub+=1;current=('section',f'{sec}.{sub}')
  m=re.search(r'\\begin\{('+ '|'.join(envs)+r')\}',line)
  if m:theo+=1;current=(envs[m[1]],f'{sec}.{theo}')
  for lab in re.findall(r'\\label\{([^}]+)\}',line):mapping[lab]=(i,current)
 ext=[]
 for lab in sorted(needed):
  i,kn=mapping[lab];kind,num=kn
  ext.append({'label':lab,'kind':kind,'number':num,'source_span':dict(path=t['statement_spans'][0]['path'],start_line=i,end_line=i,label=lab),'non_load_bearing':True,'reason':'Original cross-reference in retained introductory navigation or a declared standard renewal input. The selected claim and every local core estimate used for it are retained in full; this pointer does not substitute for a selected proof.'})
 t['assembly']['external_references']=ext;save(f,t)
 print(t['task_id'],'external',[(e['label'],e['number']) for e in ext])
