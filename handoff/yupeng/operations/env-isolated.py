#!/usr/bin/env python3
"""Run trusted corpus engineering Python in a credential-free, offline bwrap sandbox."""
from pathlib import Path
import json, os, re, shutil, subprocess, sys, tempfile
ROOT=Path('/disks/sata1/yupeng/human-proof-corpus').resolve()
RUNTIME=ROOT/'runtime'
BASE=Path('/disks/sata1/yupeng/anaconda3')
if len(sys.argv)<2:
 raise SystemExit('usage: env-isolated.sh TRUSTED_SCRIPT [helper arguments...]')
script=Path(sys.argv[1]).resolve(); args=sys.argv[2:]
if not (script.is_relative_to(ROOT/'repo/corpus-work/scripts') or (script.parent==ROOT/'operations' and script.name.startswith('env-'))) or not script.is_file():
 raise SystemExit('trusted helper must be a corpus-work/scripts file in this checkout')
def option(name):
 for index,arg in enumerate(args):
  if arg==name and index+1<len(args): return Path(args[index+1]).resolve()
  if arg.startswith(name+'='): return Path(arg.split('=',1)[1]).resolve()
 return None
package=option('--package'); build=option('--build-root'); receipts=option('--receipt-root')
if package is None or build is None or receipts is None:
 raise SystemExit('--package, --build-root and --receipt-root must be explicit absolute paths')
for path in [package,build,receipts]:
 if not path.is_relative_to(ROOT) or path==ROOT: raise SystemExit('all corpus paths must stay within this project')
if build.is_relative_to(package) or receipts.is_relative_to(package):
 raise SystemExit('outputs must be outside the read-only package')
if not package.is_dir(): raise SystemExit('package directory missing')
writable={build,receipts}
for flag in ['--report','--json-report','--report-file']:
 report=option(flag)
 if report:
  if not report.is_relative_to(ROOT/'reports'): raise SystemExit('report must be in project reports')
  writable.add(report.parent)
for path in writable: path.mkdir(parents=True,exist_ok=True)
for name in ['.home','.cache','.texmf-var','.texmf-config','.tmp']:
 (build/name).mkdir(parents=True,exist_ok=True)
command=['/usr/bin/bwrap','--unshare-all','--die-with-parent','--new-session',
 '--ro-bind','/usr','/usr','--ro-bind','/bin','/bin','--ro-bind','/lib','/lib','--ro-bind','/lib64','/lib64',
 '--proc','/proc','--dev','/dev','--tmpfs','/tmp','--ro-bind',str(ROOT),str(ROOT),
 '--ro-bind',str(BASE/'lib/python3.13'),str(BASE/'lib/python3.13'),
 '--tmpfs',str(BASE/'lib/python3.13/site-packages')]
for lib in json.loads((ROOT/'reports/env-python-base-libraries.json').read_text()):
 if Path(lib).is_file(): command.extend(['--ro-bind',lib,lib])
for path in ['/etc/fonts','/etc/ld.so.cache']:
 if Path(path).exists(): command.extend(['--ro-bind',path,path])
# Expose official font binaries at historical TeX lookup paths, without modifying the host font directory.
if (RUNTIME/'fonts/NotoSansMath-Regular.ttf').is_file():
 command.extend(['--ro-bind',str(RUNTIME/'fonts'),'/usr/share/fonts/truetype/noto'])
for path in sorted(writable,key=lambda p:len(str(p))): command.extend(['--bind',str(path),str(path)])
# Compilation must expose only the current entry and its declared same-folder assets.
# Exact files are hard-linked into a read-only runtime view; package metadata/sources stay readable.
if script.name=='compile_editable_delivery.py':
 selected_id=None
 for index,arg in enumerate(args):
  if arg=='--item' and index+1<len(args): selected_id=args[index+1]
  elif arg.startswith('--item='): selected_id=arg.split('=',1)[1]
 if selected_id is None: raise SystemExit('isolated compilation requires explicit --item')
 rows=json.loads((package/'manifest.json').read_text()).get('items',[])
 selected=[r for r in rows if r.get('problem_id')==selected_id]
 if len(selected)!=1: raise SystemExit('selected item must occur exactly once in the manifest')
 row=selected[0];entry=(package/row['item_path']).resolve()
 if not entry.is_relative_to(package) or not entry.is_file(): raise SystemExit('entry escapes or is absent from package')
 view_root=RUNTIME/'item-input-views';view_root.mkdir(parents=True,exist_ok=True)
 view=Path(tempfile.mkdtemp(prefix=selected_id+'-',dir=view_root))
 inputs=[entry]
 for asset in row.get('asset_dependencies',[]):
  source=(package/asset['path']).resolve()
  if not source.is_relative_to(package) or not source.is_file(): raise SystemExit('asset escapes or is absent from package')
  if source.is_relative_to(entry.parent): inputs.append(source)
 for source in sorted(set(inputs)):
  target=view/source.relative_to(entry.parent);target.parent.mkdir(parents=True,exist_ok=True)
  os.link(source,target)
 command.extend(['--ro-bind',str(view),str(entry.parent)])

env={
 'PATH':str(RUNTIME/'texlive/2025/bin/x86_64-linux')+':'+str(RUNTIME/'python/bin')+':/usr/bin:/bin',
 'HOME':str(build/'.home'),'XDG_CACHE_HOME':str(build/'.cache'),
 'TEXMFVAR':str(build/'.texmf-var'),'TEXMFCONFIG':str(build/'.texmf-config'),
 'TMPDIR':str(build/'.tmp'),'FONTCONFIG_FILE':str(RUNTIME/'etc/fonts.xml'),
 'LANG':'C.UTF-8','LC_ALL':'C.UTF-8','openin_any':'r','openout_any':'p',
 'PYTHONDONTWRITEBYTECODE':'1',
}
manifest=package/'manifest.json'
if manifest.is_file():
 rows=json.loads(manifest.read_text()).get('items',[])
 item=None
 for index,arg in enumerate(args):
  if arg=='--item' and index+1<len(args): item=args[index+1]
  elif arg.startswith('--item='): item=arg.split('=',1)[1]
 dirs=set()
 for row in rows:
  if item is not None and row.get('problem_id')!=item: continue
  for asset in row.get('asset_dependencies',[]):
   path=(package/asset['path']).resolve()
   if not path.is_relative_to(package): raise SystemExit('runtime asset escapes package')
   if path.suffix in ['.sty','.cls','.def','.fd']: dirs.add(str(path.parent))
 if dirs: env['TEXINPUTS']=':'.join(sorted(dirs))+':'
for name,value in env.items(): command.extend(['--setenv',name,value])
command.extend(['--chdir',str(package),str(RUNTIME/'python/bin/python'),str(script),*args])
raise SystemExit(subprocess.run(command,check=False,env={}).returncode)
