from pathlib import Path
import json,sys,os,copy
R=Path('/disks/sata1/yupeng/human-proof-corpus/operations/codex-work-01a13326')
P=R/'research-line/codex-01a13326-20261013';lane=P/'analysis-probability'
sys.path.insert(0,str(R/'corpus-work/scripts'));import prepared_delivery as delivery
os.environ['PATH']='/disks/sata1/yupeng/human-proof-corpus/runtime/texlive/2025/bin/x86_64-linux:'+os.environ['PATH']
needle='Standard finite probability and the cited sampler/extractor or multicalibration results'
suffixes=[
'multiparty-set-intersection-minentropy','chained-index-minentropy-lower-bound',
'biased-linearity-query-threshold','random-regular-graph-matrix-norm',
'recursive-uniform-prg-short-seed','cg-extractor-seed-length-lower-bound','avoidance-blackbox-reduction-barrier',
'awpe-gapp-counting-martingale','kolmogorov-counting-measure-zero','circuit-size-counting-dimension',
'stream-decoding-length-lower-bound','few-path-quantum-logspace-counting',
'nonadaptive-noncollapsing-adversary',
'weak-parity-nekomata-bootstrap','prime-mod-quantum-fanout-equivalence',
'odd-arity-holant-dichotomy']
results=[]
for suffix in suffixes:
 name='CP01A13326-AP-'+suffix;td=lane/'drafts'/name;tf=td/'task.json';task=delivery.load(tf)
 assert any(x.get('name')==needle for x in task.get('standard_prerequisites',[])),name
 old=task['revision'];old_alias=td/('task-'+old+'.json')
 if not old_alias.exists():delivery.save(old_alias,task)
 revisions=[int(old[1:])]+[int(p.name[1:]) for p in (lane/'jobs'/name).iterdir() if p.is_dir() and p.name.startswith('r') and p.name[1:].isdigit()]
 new='r'+str(max(revisions)+1).zfill(3)
 task['revision']=new;task['standard_prerequisites']=[]
 delivery.save(td/('task-'+new+'.json'),task);delivery.save(tf,task)
 print('REPAIR',name,old,'->',new,flush=True)
 row={'task_id':name,'old_revision':old,'new_revision':new,'task_path':str(tf.relative_to(P)),'source_id':task['source_id']}
 try:
  result=delivery.assemble(tf,P,lane/'jobs',material_only=True)
  row.update({k:result[k] for k in ['status','job','pages','pdf','receipt']})
  newtex=next((Path(result['job'])/('package-root-'+new)/'items').glob('*author_proof.tex'))
  assert needle not in newtex.read_text(), 'Generic prerequisite text remained in new TeX'
  print(json.dumps(row),flush=True)
 except Exception as error:
  row.update({'status':'repair_compile_failed','error':str(error)})
  print(json.dumps(row),flush=True)
 results.append(row)
 delivery.save(lane/'PREREQUISITES_REPAIR_RESULTS.json',results)

