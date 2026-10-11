import pathlib,json,sys
p=pathlib.Path(r'C:/Users/20600/Documents/Codex/corpus-repair-20261010/research-line/harness-ready-20261011');r=p.parent.parent
f=p/'focused-seeds/ACL/ACL-analysis-hartree-low-regularity-asymptotic-stability/task.json';t=json.loads(f.read_text(encoding='utf-8'));old='focused-seeds/ACL/sources/analysis-cache-820/source.tex';new='focused-seeds/ACL/sources/analysis-cache-820/source-layout.tex';txt=(p/old).read_text(encoding='utf-8');needle=r'\label{HSS}';k=txt.index(needle,txt.index(needle)+1);txt=txt[:k]+txt[k:].replace(needle,r'\label{HSS-second}',1);(p/new).write_text(txt,encoding='utf-8');
for field in ['statement_spans','proof_spans','context_spans']:
 for q in t[field]:
  if q['path']==old:q['path']=new
for field in ['preamble_spans','body_spans']:
 for q in t['assembly'][field]:
  if q['path']==old:q['path']=new
t['assembly']['editorial_notes'].append('Mechanical TeX-only repair: original source labels both equations at lines 466 and 470 HSS and never refers to that key. The second unused label is renamed HSS-second in source-layout.tex; source.tex remains unchanged and mathematical text is identical.');f.write_text(json.dumps(t,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
d=p/'focused-seeds/ACL/ACL-analysis-schrodinger-determinant-lq-optimal-potential';layout=d/'layout.tex';txt=layout.read_text(encoding='utf-8')+'\\providecommand{\\Subsubsection}{\\subsubsection}\n';layout.write_text(txt,encoding='utf-8');f=d/'task.json';t=json.loads(f.read_text(encoding='utf-8'));next(x for x in t['assembly']['preamble_spans'] if x['path']==str(layout.relative_to(p)))['end_line']=len(txt.splitlines());f.write_text(json.dumps(t,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sys.path.insert(0,str(r/'corpus-work/scripts'));import prepared_delivery as pd
for tid in ['ACL-analysis-hartree-low-regularity-asymptotic-stability','ACL-analysis-schrodinger-determinant-lq-optimal-potential']:
 job=r/'materials'/tid/'r001'
 try:
  pd.assemble(p/'focused-seeds/ACL'/tid/'task.json',p,r/'materials',compile_now=False,material_only=True,refresh=True);q=pd.compile_job(job,resume=True);print(tid,q['status'],q['pages'],flush=True)
 except Exception as e:print(tid,'ERROR',str(e),flush=True)