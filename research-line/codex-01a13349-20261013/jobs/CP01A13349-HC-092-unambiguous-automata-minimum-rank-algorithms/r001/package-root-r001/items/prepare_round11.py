from pathlib import Path
import re,subprocess,os
D=Path(__file__).resolve().parent
for id,bib in [('2503.11590v4','bibliography'),('2511.09703v5','sample')]:
 Q=D/id;main=(Q/'main.tex').read_text();O=D/(id+'-prepared');O.mkdir(exist_ok=True)
 def flatten(s,base):
  out=[]
  for line in s.splitlines():
   active=re.split(r'(?<!\\)%',line,1)[0]
   m=re.search(r'\\input\{([^}]+)\}',active)
   if m:
    f=base/m[1];f=f if f.suffix else f.with_suffix('.tex')
    out+=['% ORIGINAL INPUT '+str(f.relative_to(Q)),flatten(f.read_text(),f.parent),'% END ORIGINAL INPUT '+str(f.relative_to(Q))]
   else:out.append(line)
  return '\n'.join(out)
 start=main.index('%% read in additional') if id.startswith('2503') else main.index('\\usepackage[utf8]')
 pre=main[start:main.index('\\begin{document}')]
 if id.startswith('2503'):pre=pre.replace(r'\usepackage{macros}',(Q/'macros.sty').read_text())
 basic='\\documentclass[11pt,a4paper]{amsart}\n\\usepackage[margin=20mm]{geometry}\n\\usepackage{amsmath,amssymb,amsthm,graphicx,xcolor}\n\\usepackage[no-math]{fontspec}\n\\setmainfont{lmroman10-regular.otf}[BoldFont=lmroman10-bold.otf,ItalicFont=lmroman10-italic.otf,BoldItalicFont=lmroman10-bolditalic.otf,SmallCapsFont=lmromancaps10-regular.otf]\n\\usepackage[inline]{enumitem}\n'
 env='\n'.join((Q/'lmcs.cls').read_text().splitlines()[704:773])
 (O/'wrapper.tex').write_text(basic+pre+'\n'+env+'\n'+r'\AtBeginDocument{\def\shorttitle{'+('Conservative Petri net structural liveness' if id.startswith('2503') else 'The rank of unambiguous finite automata')+'}}\n')
 ab=re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}',main,re.S)[1]
 k=main.index(r'\thanks{')+len(r'\thanks{');depth=1;j=k
 while depth:
  if main[j]=='{' and (j==0 or main[j-1]!='\\'):depth+=1
  if main[j]=='}' and main[j-1]!='\\':depth-=1
  j+=1
 credits=main[k:j-1]
 body=r'\paragraph{Original publication credits.} '+credits+'\n'+r'\paragraph{Original abstract.} '+ab+'\n'+flatten(main[re.search(r'^\\maketitle\s*$',main,re.M).end():main.index(r'\bibliographystyle')],Q)
 (O/'rendercopy-body.tex').write_text(body+'\n')
 (O/'references.aux').write_text('\\relax\n\\citation{*}\n\\bibstyle{alphaurl}\n\\bibdata{'+str(Q/bib)+'}\n')
 envp=dict(os.environ);envp['PATH']='/disks/sata1/yupeng/human-proof-corpus/runtime/texlive/2025/bin/x86_64-linux:'+envp['PATH'];envp['BSTINPUTS']=str(Q)+':'+str(D/'2503.11590v4')+':';envp['BIBINPUTS']=str(Q)+':'
 r=subprocess.run(['bibtex','references'],cwd=O,env=envp,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True);(O/'bibtex.stdout').write_text(r.stdout);print(id,'body',len(body.splitlines()),'wrapper',len((O/'wrapper.tex').read_text().splitlines()),'bibtex',r.returncode,r.stdout[-400:])
