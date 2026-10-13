from pathlib import Path
import sys,os,json,argparse
P=Path(__file__).resolve().parent.parent;R=P.parent.parent
os.environ['PATH']='/disks/sata1/yupeng/human-proof-corpus/runtime/texlive/2025/bin/x86_64-linux:'+os.environ['PATH']
sys.path.insert(0,str(R/'corpus-work/scripts'));import prepared_delivery as d
ap=argparse.ArgumentParser();ap.add_argument('tasks',nargs='*');args=ap.parse_args()
paths=[P/x for x in args.tasks] if args.tasks else [p for lane in ['communication-complexity','geometry-algorithms','number-theory'] for p in (P/lane).glob('*/task.json')]
for tf in sorted(paths):
 try:
  t=d.load(tf)
  if not t['task_id'].startswith('CP01A1332F-') or t.get('status') not in ('ready_for_assembly','prepared_unpublished'):continue
  job=P/'jobs'/t['task_id']/t['revision'];sf=job/'job-state.json'
  if not sf.is_file():d.assemble(tf,P,P/'jobs',compile_now=False,material_only=True)
  state=d.load(sf)
  if state['status']=='compiled_pending_qa':continue
  if state['status']=='needs_codex' and not args.tasks:continue
  if state['status']=='needs_codex':
   d.assemble(tf,P,P/'jobs',compile_now=False,material_only=True,refresh=True)
   d.compile_job(job,resume=True)
  elif state['status']=='assembled':d.compile_job(job)
  state=d.load(sf)
  print(json.dumps({'task_id':t['task_id'],'status':state['status']},ensure_ascii=False),flush=True)
 except Exception as e:print(json.dumps({'task_path':str(tf.relative_to(P)),'failed':str(e)},ensure_ascii=False),flush=True)
