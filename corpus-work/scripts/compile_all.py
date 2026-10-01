"""Fresh two-pass local compilation with hash-bound evidence receipts."""
import argparse, datetime, json, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path
from validate_corpus import dependencies, local, read_json, sha, write_json

def compile_one(corpus,item,meta,engine,timeout):
 receipt={'ok':False,'passes':0,'err':'','compiled_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 try:
  tex=local(corpus,meta['tex_path']);receipt['input_sha256']=sha(tex);receipt['dependency_sha256']=dependencies(corpus,meta)
  executable=shutil.which(engine)
  if not executable:raise ValueError('engine missing: '+engine)
  receipt['engine']=executable
  output=Path(tempfile.mkdtemp(prefix=item+'-',dir=corpus/'.work/build'));receipt['build_dir']=str(output.relative_to(corpus))
  log=output/'compiler.log';receipt['log']=str(log.relative_to(corpus))
  env=os.environ.copy()
  cache=corpus.parent/'.tex-cache'
  if (cache/'formats/xelatex.fmt').is_file():env.setdefault('TEXFORMATS',str(cache/'formats')+'//:')
  if (cache/'lm/lm').is_dir():env.setdefault('TEXMF','{'+str(cache/'lm/lm')+',/usr/share/texlive/texmf-dist}')
  (cache/'home').mkdir(parents=True,exist_ok=True);(cache/'xdg').mkdir(parents=True,exist_ok=True)
  env['HOME']=str(cache/'home');env['XDG_CACHE_HOME']=str(cache/'xdg')
  env['openin_any']='r';env['openout_any']='p';env['TEXMFOUTPUT']=str(output)
  with log.open('w',encoding='utf-8') as stream:
   for _ in range(2):
    p=subprocess.run([executable,'-no-shell-escape','-interaction=nonstopmode','-halt-on-error','-file-line-error','-recorder','-output-directory='+str(output),str(tex)],cwd=corpus/'tex',stdout=stream,stderr=subprocess.STDOUT,timeout=timeout,env=env)
    if p.returncode:raise ValueError('engine exit '+str(p.returncode))
    receipt['passes']+=1
  pdf=output/(tex.stem+'.pdf')
  if not pdf.is_file() or not pdf.read_bytes().startswith(b'%PDF-'):raise ValueError('fresh PDF missing/invalid')
  final_log=output/(tex.stem+'.log')
  if not final_log.is_file():raise ValueError('final-pass TeX log missing')
  text=final_log.read_text(encoding='utf-8',errors='replace')
  if re.search(r'(?:undefined references|undefined citations|Reference .+ undefined|Citation .+ undefined)',text,re.I):raise ValueError('unresolved references/citations')
  # FLS records reveal hidden transitive local resources ignored by lexical scan.
  fls=output/(tex.stem+'.fls')
  if not fls.is_file():raise ValueError('recorder file missing')
  deps=receipt['dependency_sha256']
  for line in fls.read_text(encoding='utf-8',errors='replace').splitlines():
   if not line.startswith('INPUT '):continue
   raw=Path(line[6:]);p=(raw if raw.is_absolute() else corpus/'tex'/raw).resolve()
   if p.is_file() and p.is_relative_to(corpus) and not p.is_relative_to(output) and p!=tex:deps[str(p.relative_to(corpus))]=sha(p)
  # Dynamic resource discovery must agree with validation's explicit dependencies.
  if deps!=dependencies(corpus,meta):raise ValueError('untracked local dependency in recorder; declare literal input/include path')
  if sha(tex)!=receipt['input_sha256']:raise ValueError('input changed during compilation')
  receipt.update(ok=True,pdf=str(pdf.relative_to(corpus)),pdf_sha256=sha(pdf))
 except (OSError,ValueError,KeyError,TypeError,subprocess.TimeoutExpired) as e:receipt['err']=str(e)
 return receipt

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--item');p.add_argument('--engine',default=os.environ.get('XELATEX','xelatex'));p.add_argument('--timeout',type=int,default=180);args=p.parse_args()
 corpus=(args.root/'corpus').resolve();(corpus/'.work/build').mkdir(parents=True,exist_ok=True)
 try:records=read_json(corpus/'item_status.json')['items']
 except (OSError,ValueError,KeyError) as e:print('manifest:',e,file=sys.stderr);return 1
 path=corpus/'.work/compile_report.json'
 try:report=read_json(path)
 except (OSError,ValueError):report={}
 if not isinstance(report,dict):report={}
 selected=[args.item] if args.item else [n for n,r in records.items() if r.get('status')=='active']
 if args.item and (args.item not in records or not records[args.item].get('metadata')):print('requested item missing metadata',file=sys.stderr);return 1
 failed=False
 for n in selected:
  try:meta=read_json(local(corpus,records[n]['metadata']));receipt=compile_one(corpus,n,meta,args.engine,args.timeout)
  except (OSError,ValueError,KeyError,TypeError) as e:receipt={'ok':False,'passes':0,'err':'metadata: '+str(e)}
  report[n]=receipt;write_json(path,report);failed|=not receipt['ok'];print(('PASS' if receipt['ok'] else 'FAIL'),n,receipt.get('err',''))
 return int(failed)
if __name__=='__main__':sys.exit(main())
