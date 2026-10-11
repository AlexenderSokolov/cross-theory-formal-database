import pathlib,json,sys
p=pathlib.Path(r'C:/Users/20600/Documents/Codex/corpus-repair-20261010/research-line/harness-ready-20261011');r=p.parent.parent
ids=['ACL-analysis-hartree-low-regularity-asymptotic-stability','ACL-analysis-hypoelliptic-chain-weak-harnack','ACL-analysis-lattice-modified-wave-operator-completeness','ACL-analysis-schrodinger-determinant-lq-optimal-potential']
common=r'''\usepackage{xfrac}
\makeatletter
\@ifundefined{theo}{\newtheorem{theo}{Theorem}[section]}{}
\@ifundefined{lemm}{\newtheorem{lemm}[theo]{Lemma}}{}
\@ifundefined{prop}{\newtheorem{prop}[theo]{Proposition}}{}
\@ifundefined{coro}{\newtheorem{coro}[theo]{Corollary}}{}
\@ifundefined{rema}{\newtheorem{rema}[theo]{Remark}}{}
\makeatother
'''
for tid in ids:
 d=p/'focused-seeds/ACL'/tid;f=d/'task.json';t=json.loads(f.read_text(encoding='utf-8-sig'));txt=common if any(k in tid for k in ['hartree','lattice']) else '\\usepackage{xfrac}\n'
 if 'lattice' in tid:txt+=r'''\makeatletter
\@ifundefined{assu}{\newtheorem{assu}[theo]{Assumption}}{}
\@ifundefined{defi}{\newtheorem{defi}[theo]{Definition}}{}
\@ifundefined{enonce}{\newenvironment{enonce}[1]{\begin{assu}}{\end{assu}}}{}
\@ifundefined{proofc}{\newenvironment{proofc}{\begin{proof}}{\end{proof}}}{}
\makeatother
'''
 layout=d/'layout.tex';layout.write_text(txt,encoding='utf-8');s=dict(path=str(layout.relative_to(p)),start_line=1,end_line=len(txt.splitlines()),label='standalone adapter from existing same-source compiled item')
 t['assembly']['preamble_spans']=[s]+[v for v in t['assembly']['preamble_spans'] if v['path']!=s['path']];f.write_text(json.dumps(t,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sys.path.insert(0,str(r/'corpus-work/scripts'));import prepared_delivery as pd
w={v['task_id']:v for v in map(json.loads,(p/'PREPARATION_WORKLIST.jsonl').read_text(encoding='utf-8-sig').splitlines())}
for tid in ids:
 job=pathlib.Path(w[tid]['assembly_job']);print('START',tid,flush=True)
 try:
  pd.assemble(p/w[tid]['task_path'],p,job.parent.parent,compile_now=False,material_only=True,refresh=True)
  result=pd.compile_job(job,resume=True);print('RESULT',tid,result,flush=True)
 except Exception as e: print('ERROR',tid,str(e),flush=True)