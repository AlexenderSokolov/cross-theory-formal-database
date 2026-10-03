#!/usr/bin/env python3
"""Check explicit package/class/TikZ/PGF/PGFPlots/TCB library names; never replaces real compilation."""
from pathlib import Path
import argparse,json,re,subprocess,sys
ROOT=Path('/disks/sata1/yupeng/human-proof-corpus');sys.path.insert(0,str(ROOT/'repo/corpus-work/scripts'));import editable_delivery as gate
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--package',type=Path,action='append',required=True);p.add_argument('--report',type=Path,required=True);a=p.parse_args()
texbin=ROOT/'runtime/texlive/2025/bin/x86_64-linux';requests={};dynamic=[];count=0
for package in a.package:
 package=package.resolve()
 for row in json.loads((package/'manifest.json').read_text())['items']:
  count+=1;ident=row['problem_id'];text=gate.active_tex((package/row['item_path']).read_text())
  declared={Path(asset['path']).name for asset in row.get('asset_dependencies',[])}
  def request(choices):
   if any(name in declared for name in choices):return
   requests.setdefault(tuple(choices),set()).add(ident)
  for names in re.findall(r'\\(?:usepackage|RequirePackage)(?:\[[^]]*\])?\{([^}]+)\}',text):
   for name in names.split(','):request([name.strip()+'.sty'])
  for name in re.findall(r'\\documentclass(?:\[[^]]*\])?\{([^}]+)\}',text):request([name+'.cls'])
  for command,braced,bracketed in re.findall(r'\\(usetikzlibrary|usepgfplotslibrary|usepgflibrary|tcbuselibrary)\s*(?:\{([^}]+)\}|\[([^]]+)\])',text):
   for name in (braced or bracketed).split(','):
    name=name.strip()
    if not re.fullmatch(r'[A-Za-z0-9_.+-]+',name):dynamic.append({'item':ident,'command':command,'expression':name});continue
    if command=='usetikzlibrary':request(['tikzlibrary'+name+'.code.tex','pgflibrary'+name+'.code.tex'])
    elif command=='usepgfplotslibrary':request(['tikzlibrarypgfplots.'+name+'.code.tex'])
    elif command=='usepgflibrary':request(['pgflibrary'+name+'.code.tex'])
    else:request(['tcblibrary'+name+'.code.tex'])
tlpdb=max((ROOT/'runtime/texlive/2025/tlpkg').glob('texlive.tlpdb.main.*'),key=lambda p:p.stat().st_size);lookup={};pkg=None
for line in tlpdb.read_text().splitlines():
 if line.startswith('name '):pkg=line[5:]
 elif line.startswith(' ') and line.strip().startswith(('RELOC/tex/','texmf-dist/tex/','tex/')):lookup.setdefault(Path(line.strip().split()[0]).name,set()).add(pkg)
missing=[];found=[]
for choices,ids in sorted(requests.items()):
 match=None
 for filename in choices:
  result=subprocess.run([str(texbin/'kpsewhich'),filename],capture_output=True,text=True,env={'HOME':str(ROOT/'runtime/setup-home'),'PATH':str(texbin)+':/usr/bin:/bin'})
  if not result.returncode and result.stdout.strip():match={'logical_file':filename,'actual_path':result.stdout.strip()};break
 if match:found.append({'choices':choices,'items':sorted(ids),**match})
 else:missing.append({'choices':choices,'items':sorted(ids),'official_package_candidates':sorted({pkg for name in choices for pkg in lookup.get(name,[])})})
report={'manifest_entries_inspected':count,'explicit_requirements':len(requests),'missing':missing,'unexpanded_dynamic_expressions':dynamic,'found':found,'boundary':'Static engineering precheck; every selected item still requires real compile and editable-delivery validation.'}
a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='found'},indent=2));raise SystemExit(bool(missing))
