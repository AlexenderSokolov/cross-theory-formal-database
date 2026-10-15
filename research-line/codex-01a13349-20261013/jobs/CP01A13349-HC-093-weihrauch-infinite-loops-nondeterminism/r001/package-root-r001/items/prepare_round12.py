from pathlib import Path
import re,subprocess,os,shutil
D=Path(__file__).resolve().parent
basic='\\documentclass[11pt,a4paper]{amsart}\n\\usepackage[a4paper,landscape,margin=20mm]{geometry}\n\\usepackage{amsmath,amssymb,amsthm,graphicx,xcolor}\n\\usepackage[no-math]{fontspec}\n\\setmainfont{lmroman10-regular.otf}[BoldFont=lmroman10-bold.otf,ItalicFont=lmroman10-italic.otf,BoldItalicFont=lmroman10-bolditalic.otf,SmallCapsFont=lmromancaps10-regular.otf]\n\\usepackage[inline,shortlabels]{enumitem}\n'
for id,file,bib in [('2501.17734v4','limits.tex','limits'),('2504.18227v4','main.tex','biblio')]:
 Q=D/id;s=(Q/file).read_text();O=D/(id+'-prepared');O.mkdir(exist_ok=True)
 def flat(text,base):
  out=[]
  for line in text.splitlines():
   active=re.split(r'(?<!\\)%',line,maxsplit=1)[0];m=re.search(r'\\input\{([^}]+)\}',active)
   if m:
    f=base/m[1];f=f if f.suffix else f.with_suffix('.tex');out+=['% ORIGINAL INPUT '+str(f.relative_to(Q)),flat(f.read_text(),f.parent),('\\fi % close original sec9 true conditional at input boundary' if f.name=='sec9-ogs-compo.tex' else ''),'% END ORIGINAL INPUT '+str(f.relative_to(Q))]
   else:out.append(line)
  return '\n'.join(out)
 lmcs=(Q/'lmcs.cls').read_text();env=lmcs[lmcs.index(r'\theoremstyle{plain}',lmcs.index('%%% Theorem environments')):lmcs.index('% end-of-proof sign')]
 if id.startswith('2501'):
  pre=s[s.index(r'\usepackage{hyperref}'):s.index(r'\title{')]
  pre+=s[s.index(r'\begin{document}')+len(r'\begin{document}'):s.index(r'\keywords{}')]
 else:
  flags=s[:s.index(r'\documentclass')]
  pre=flags+flat(s[s.index(r'\usepackage{hyperref}'):s.index(r'\begin{document}')],Q)
 (O/'wrapper.tex').write_text(basic+env+'\n'+pre+'\n'+r'\AtBeginDocument{\def\shorttitle{'+('Loops and nondeterminism' if id.startswith('2501') else 'Games, processes and functions')+'}}\n')
 ab=re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}',s,re.S)[1]
 start=re.search(r'^\\maketitle\s*$',s,re.M).end()
 end=s.index(r'\end{document}')
 body=s[start:end]
 # Preserve active source sections and original appendix order; bibliography handled as original bbl at its original location.
 body=re.sub(r'^\\bibliographystyle\{[^}]+\}\s*\n\\bibliography\{[^}]+\}',r'% ORIGINAL BIBLIOGRAPHY POSITION',body,flags=re.M)
 body=r'\paragraph{Original abstract.} '+ab+'\n'+flat(body,Q)
 (O/'rendercopy-body.tex').write_text(body+'\n')
 (O/'references.aux').write_text('\\relax\n\\citation{*}\n\\bibstyle{alphaurl}\n\\bibdata{'+str(Q/bib)+'}\n')
 envp=dict(os.environ);envp['PATH']='/disks/sata1/yupeng/human-proof-corpus/runtime/texlive/2025/bin/x86_64-linux:'+envp['PATH'];envp['BSTINPUTS']=str(Q)+':'+str(D.parent/'scout-round11/2503.11590v4')+':'
 r=subprocess.run(['bibtex','references'],cwd=O,env=envp,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True);(O/'bibtex.stdout').write_text(r.stdout)
 print(id,'body',len(body.splitlines()),'wrapper',len((O/'wrapper.tex').read_text().splitlines()),'bib',r.returncode,r.stdout[-350:])
 if id.startswith('2504'):
  vendor=D.parent/'scout-round4/2411.15979v1/vendor/mathpartir';shutil.copyfile(vendor/'mathpartir.sty',O/'mathpartir.sty')
 (O/'probe.tex').write_text((O/'wrapper.tex').read_text()+r'\begin{document}'+'\n'+body.replace('% ORIGINAL BIBLIOGRAPHY POSITION',(O/'references.bbl').read_text())+'\n'+r'\end{document}'+'\n')
 r=subprocess.run(['xelatex','-no-shell-escape','-interaction=nonstopmode','-halt-on-error','-file-line-error','probe.tex'],cwd=O,env=envp,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True);(O/'xelatex-1.stdout').write_text(r.stdout);print(id,'tex',r.returncode,r.stdout[-1200:])
