from pathlib import Path
import json,hashlib,subprocess,os
root=Path('/disks/sata1/yupeng/human-proof-corpus');runtime=root/'runtime';reports=root/'reports'
packages=[]
for block in (runtime/'texlive/2025/tlpkg/texlive.tlpdb').read_text().split('\n\n'):
 fields={}
 for line in block.splitlines():
  if line.startswith(('name ','revision ','catalogue-version ','category ')):
   key,value=line.split(' ',1);fields[key]=value
 if 'name' in fields: packages.append(fields)
(reports/'env-texlive-packages.tsv').write_text('name\trevision\tversion\tcategory\n'+''.join('\t'.join(p.get(k,'') for k in ['name','revision','catalogue-version','category'])+'\n' for p in packages))
env=os.environ.copy();env['FONTCONFIG_FILE']=str(runtime/'etc/fonts.xml');env['XDG_CACHE_HOME']=str(runtime/'setup-home/.cache')
font_queries=['Latin Modern Roman','Latin Modern Roman Caps','NimbusRoman-Regular','DejaVu Serif','Noto Serif','Noto Serif CJK SC','Noto Sans Math','DejaVu Math TeX Gyre']
fonts=[]
for query in font_queries:
 text=subprocess.run(['/usr/bin/fc-match','--format','%{file}|%{postscriptname}|%{family}|%{style}\n',query],capture_output=True,text=True,env=env,check=True).stdout.strip()
 path,postscript,family,style=text.split('|',3);p=Path(path)
 fonts.append({'requested':query,'path':path,'postscript_name':postscript,'family':family,'style':style,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(reports/'env-font-manifest.json').write_text(json.dumps(fonts,indent=2,ensure_ascii=False)+'\n')
versions={}
for name,args in {'bubblewrap':['/usr/bin/bwrap','--version'],'poppler_pdfinfo':['/usr/bin/pdfinfo','-v'],'glibc':['/usr/bin/ldd','--version']}.items():
 result=subprocess.run(args,capture_output=True,text=True,check=False);versions[name]=(result.stdout+result.stderr).splitlines()[0]
versions['python_stdlib_prefix']='/disks/sata1/yupeng/anaconda3/lib/python3.13'
versions['tex_repository']='https://ftp.math.utah.edu/pub/tex/historic/systems/texlive/2025/tlnet-final'
versions['python_dependencies']=json.loads(subprocess.run([str(runtime/'python/bin/python'),'-m','pip','list','--format=json'],capture_output=True,text=True,check=True).stdout)
versions['installed_tex_packages']=len(packages)
(reports/'env-runtime-manifest.json').write_text(json.dumps(versions,indent=2,ensure_ascii=False)+'\n')
print('captured_installed_tex_packages',len(packages));print(json.dumps(fonts,indent=2))
