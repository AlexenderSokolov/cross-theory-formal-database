from pathlib import Path
import sys,os,json,subprocess,re
lane=Path(__file__).resolve().parent;root=lane.parent;repo=root.parent.parent
sys.path.insert(0,str(repo/'corpus-work/scripts'))
import prepared_delivery as pd
os.environ['PATH']='/disks/sata1/yupeng/human-proof-corpus/runtime/texlive/2025/bin/x86_64-linux:'+os.environ['PATH']
def save(p,o):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n')
def compile_direct(job):
 state=json.loads((job/'job-state.json').read_text());package=job/state['package'];row=json.loads((package/'manifest.json').read_text())['items'][0];tex=package/row['item_path'];build=job/state['build_root']/row['problem_id'];build.mkdir(parents=True,exist_ok=True)
 receipt=dict(schema_version=2,policy=state['policy'],**pd.binding(state),ok=False,compile_run_id=state['task_id']+'/'+state['revision']+'/compile-001',engine='xelatex',driver='explicit_xelatex',latexmk_used=False,shell_escape=False,started_at=pd.utc_now(),bibliography_backend='bibtex',bibliography_runs=0,engine_runs=0,asset_paths=[a['path'] for a in row['asset_dependencies']])
 try:
  env=os.environ.copy();env['BIBINPUTS']=str(tex.parent)+os.pathsep
  for n in range(1,4):
   cmd=['xelatex','-no-shell-escape','-interaction=nonstopmode','-halt-on-error','-file-line-error','-recorder','-output-directory='+str(build),tex.name]
   result=subprocess.run(cmd,cwd=tex.parent,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True);(build/('xelatex-'+str(n)+'.stdout')).write_text(result.stdout)
   if result.returncode:raise RuntimeError(result.stdout[-1800:])
   receipt['engine_runs']+=1
   if n==1:
    result=subprocess.run(['bibtex',tex.stem],cwd=build,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True);(build/'bibtex.stdout').write_text(result.stdout)
    if result.returncode:raise RuntimeError(result.stdout[-1800:])
    receipt['bibliography_runs']+=1
  log=build/(tex.stem+'.log');txt=log.read_text(errors='replace')
  if 'Rerun to get' in txt or 'Label(s) may have changed' in txt:
   result=subprocess.run(cmd,cwd=tex.parent,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True);(build/'xelatex-4.stdout').write_text(result.stdout);receipt['engine_runs']+=1
   if result.returncode:raise RuntimeError(result.stdout[-1800:])
   txt=log.read_text(errors='replace')
  errs=[l for l in txt.splitlines() if re.search(r'undefined references|undefined citations|(?:Reference|Citation) .+ undefined|Missing character:|^!',l,re.I)]
  if errs:raise RuntimeError('\n'.join(errs[:12]))
  pdf=build/(tex.stem+'.pdf');info=subprocess.check_output(['pdfinfo',str(pdf)],text=True);(build/'pdfinfo.log').write_text(info);pages=int(re.search(r'^Pages:\s+(\d+)',info,re.M)[1])
  receipt.update(ok=True,completed_at=pd.utc_now(),pages=pages,passes=receipt['engine_runs'],pdf_path=str(pdf.relative_to(job)),compiler_log_path=str(log.relative_to(job)),rendered_pages=[],final_log_errors=[])
  state.update(status='compiled_pending_qa',compile_run_id=receipt['compile_run_id']);state.pop('error',None)
  print('COMPILED',state['task_id'],state['revision'],pages,flush=True)
 except Exception as e:
  state.update(status='needs_codex',error=str(e));receipt['error']=str(e);print('FAILED',state['task_id'],str(e),flush=True)
 finally:
  save(job/state['receipt_root']/(row['problem_id']+'.json'),receipt);save(package/row['compile_receipt'],receipt);save(job/'job-state.json',state)
paths=[Path(a).resolve() for a in sys.argv[1:]] if len(sys.argv)>1 else sorted(lane.glob('CP01A13326-CL-*/task.json'))
for path in paths:
 task=json.loads(path.read_text())
 if not any(a in task['source_id'] for a in ['2402.00133','2111.03639','2403.09184','2307.02968']):continue
 job=lane/'jobs'/task['task_id']/task['revision']
 if (job/'job-state.json').exists():print('PRESERVED',task['task_id'],json.loads((job/'job-state.json').read_text())['status'],flush=True);continue
 try:pd.assemble(path,root,lane/'jobs',material_only=True,compile_now=False)
 except Exception as e:print('ASSEMBLY-FAILED',task['task_id'],e,flush=True);continue
 compile_direct(job)
