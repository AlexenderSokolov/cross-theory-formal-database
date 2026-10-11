import pathlib,json,sys
p=pathlib.Path(r'C:/Users/20600/Documents/Codex/corpus-repair-20261010/research-line/harness-ready-20261011');r=p.parent.parent
ids=['ACL-analysis-hartree-low-regularity-asymptotic-stability','ACL-analysis-hypoelliptic-chain-weak-harnack','ACL-analysis-lattice-modified-wave-operator-completeness','ACL-analysis-schrodinger-determinant-lq-optimal-potential']
sys.path.insert(0,str(r/'corpus-work/scripts'));import prepared_delivery as pd
w={v['task_id']:v for v in map(json.loads,(p/'PREPARATION_WORKLIST.jsonl').read_text(encoding='utf-8-sig').splitlines())}
for tid in ids:
 job=pathlib.Path(w[tid]['assembly_job']);print('START',tid,flush=True)
 try:
  pd.assemble(p/w[tid]['task_path'],p,job.parent.parent,compile_now=False,material_only=True,refresh=True)
  result=pd.compile_job(job,resume=True);print('RESULT',tid,result,flush=True)
 except Exception as e: print('ERROR',tid,str(e),flush=True)