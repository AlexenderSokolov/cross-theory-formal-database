"""Regenerate checkout-local compile artifacts/receipts without changing the package.

Requires installed XeLaTeX, packages/fonts and pypdf; never downloads or installs.
"""
import argparse
import datetime
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

import editable_delivery as gate


def compile_item(package,row,build_root,engine,timeout):
    ident=row['problem_id']
    receipt=dict(problem_id=ident,ok=False,passes=0,shell_escape=False,engine=engine,
                 compiled_at=datetime.datetime.now(datetime.timezone.utc).isoformat())
    try:
        tex=gate.local(package,row['item_path']);data=tex.read_bytes();receipt['input_sha256']=gate.digest(data)
        if receipt['input_sha256']!=row['tex_sha256']:raise ValueError('input hash differs from published manifest')
        if re.search(r'\\(?:input|include)\b',gate.active_tex(data.decode('utf-8'))):raise ValueError('editable inputs must already be flattened')
        dependencies={}
        for asset in row.get('asset_dependencies',[]):
            path=gate.local(package,asset['path']);h=gate.digest(path.read_bytes())
            if h!=asset['sha256']:raise ValueError('declared asset hash mismatch: '+asset['path'])
            dependencies[asset['path']]=h
        receipt['dependency_sha256']=dependencies
        for name in re.findall(r'\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}',gate.active_tex(data.decode('utf-8'))):
            path=(tex.parent/name).resolve()
            if not path.is_relative_to(package) or str(path.relative_to(package)) not in dependencies:
                raise ValueError('undeclared figure dependency: '+name)
        out=(build_root/ident).resolve()
        if not out.is_relative_to(build_root.resolve()):raise ValueError('build path escapes external root')
        out.mkdir(parents=True,exist_ok=True);compiler_log=out/'compiler.log'
        if any(not p.resolve().is_relative_to(build_root.resolve()) for p in out.rglob('*')):
            raise ValueError('existing build artifact escapes external root')
        env=os.environ.copy();env['openin_any']='r';env['openout_any']='p'
        for name,folder in [('HOME','.home'),('XDG_CACHE_HOME','.cache'),('TEXMFVAR','.texmf-var'),('TEXMFCONFIG','.texmf-config')]:
            cache=(build_root/folder).resolve()
            if not cache.is_relative_to(build_root):raise ValueError('compiler cache path escapes external root')
            cache.mkdir(parents=True,exist_ok=True);env[name]=str(cache)
        with compiler_log.open('w',encoding='utf-8') as stream:
            for _ in range(4):
                result=subprocess.run([engine,'-no-shell-escape','-interaction=nonstopmode','-halt-on-error','-file-line-error','-recorder',
                                       '-output-directory='+str(out),tex.name],cwd=tex.parent,env=env,stdout=stream,stderr=subprocess.STDOUT,timeout=timeout)
                if result.returncode:raise ValueError('engine exit '+str(result.returncode))
                receipt['passes']+=1
                final_log=gate.local(build_root,str((out/(tex.stem+'.log')).relative_to(build_root)))
                log=final_log.read_text(encoding='utf-8',errors='replace')
                receipt['rerun_requests']=re.findall(r'^.*(?:Label\(s\) may have changed|Rerun to get (?:cross-references|outlines|bookmarks) right|Rerun to get /PageLabels entry|Package rerunfilecheck Warning:.*has changed).*$',log,re.I|re.M)
                if receipt['passes']>=2 and not receipt['rerun_requests']:break
        if receipt['rerun_requests']:raise ValueError('references/bookmarks did not stabilize after four successful passes')
        final_log=gate.local(build_root,str((out/(tex.stem+'.log')).relative_to(build_root)))
        log=final_log.read_text(encoding='utf-8',errors='replace')
        receipt['unresolved_references']=re.findall(r'.*(?:undefined references|undefined citations|Reference .+ undefined|Citation .+ undefined).*',log,re.I)
        receipt['missing_characters']=re.findall(r'.*Missing character:.*',log)
        receipt['multiply_defined_labels']=re.findall(r'.*(?:Label .+ multiply defined|multiply-defined labels).*',log,re.I)
        if receipt['multiply_defined_labels']:raise ValueError('multiply-defined labels in final TeX log')
        if receipt['unresolved_references'] or receipt['missing_characters']:raise ValueError('unresolved references/citations or missing glyphs')
        fls=gate.local(build_root,str((out/(tex.stem+'.fls')).relative_to(build_root)))
        for line in fls.read_text(encoding='utf-8').splitlines():
            if not line.startswith('INPUT '):continue
            path=Path(line[6:]);path=(path if path.is_absolute() else tex.parent/path).resolve()
            if path==tex or not path.is_relative_to(package):continue
            if not path.is_file() or str(path.relative_to(package)) not in dependencies:raise ValueError('undeclared local recorder input: '+str(path))
        if tex.read_bytes()!=data:raise ValueError('input changed during compile')
        for name,h in dependencies.items():
            if gate.digest(gate.local(package,name).read_bytes())!=h:raise ValueError('asset changed during compile: '+name)
        pdf=gate.local(build_root,str((out/(tex.stem+'.pdf')).relative_to(build_root)))
        if not pdf.read_bytes().startswith(b'%PDF-'):raise ValueError('fresh PDF signature missing')
        from pypdf import PdfReader
        receipt.update(ok=True,pdf_path=str(pdf.relative_to(build_root)),pdf_sha256=gate.digest(pdf.read_bytes()),
                       pages=len(PdfReader(pdf).pages),compiler_log_path=str(compiler_log.relative_to(build_root)),
                       compiler_log_sha256=gate.digest(compiler_log.read_bytes()))
    except (OSError,ValueError,KeyError,TypeError,ImportError,subprocess.TimeoutExpired) as exc:
        receipt['error']=str(exc)
    return receipt


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package',type=Path,required=True);parser.add_argument('--build-root',type=Path,required=True)
    parser.add_argument('--receipt-root',type=Path,required=True);parser.add_argument('--item');parser.add_argument('--engine',default='xelatex')
    parser.add_argument('--timeout',type=int,default=180);args=parser.parse_args()
    package=args.package.resolve();build=args.build_root.resolve();receipts=args.receipt_root.resolve()
    if build.is_relative_to(package) or receipts.is_relative_to(package):parser.error('build and receipt roots must be outside the read-only package')
    engine=shutil.which(args.engine)
    if not engine:parser.error('installed TeX engine missing; no software will be installed')
    manifest=gate.read_json(gate.local(package,'manifest.json'));rows=manifest.get('items')
    if not isinstance(rows,list) or any(not gate.ID.fullmatch(str(r.get('problem_id',''))) for r in rows):parser.error('unsupported manifest/ID schema')
    if len({r['problem_id'] for r in rows})!=len(rows):parser.error('duplicate manifest IDs')
    selected=[r for r in rows if args.item is None or r['problem_id']==args.item]
    if not selected:parser.error('requested item absent from manifest')
    receipts.mkdir(parents=True,exist_ok=True);results=[]
    for row in selected:
        path=(receipts/(row['problem_id']+'.json')).resolve()
        if not path.is_relative_to(receipts):parser.error('receipt path escapes external root')
        result=compile_item(package,row,build,engine,args.timeout)
        path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');results.append(result)
    print(json.dumps(dict(receipt_set=str(receipts),items=results),ensure_ascii=False,indent=2))
    return int(any(not r['ok'] for r in results))


if __name__=='__main__':sys.exit(main())
