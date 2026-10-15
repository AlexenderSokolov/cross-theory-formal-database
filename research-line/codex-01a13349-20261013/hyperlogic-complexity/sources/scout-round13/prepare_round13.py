from pathlib import Path
import re,os,subprocess,shutil
D=Path(__file__).resolve().parent
basic='\\documentclass[11pt,a4paper]{amsart}\n\\usepackage[a4paper,landscape,margin=20mm]{geometry}\n\\usepackage{amsmath,amssymb,amsthm,graphicx,xcolor,tikz}\n\\usepackage[no-math]{fontspec}\n\\setmainfont{lmroman10-regular.otf}[BoldFont=lmroman10-bold.otf,ItalicFont=lmroman10-italic.otf,BoldItalicFont=lmroman10-bolditalic.otf,SmallCapsFont=lmromancaps10-regular.otf]\n\\usepackage[inline,shortlabels]{enumitem}\n'
for id,bib in [('2501.05385v5','mskrzypczak'),('2503.08530v4','biblio')]:
 Q=D/id;main=(Q/'main.tex').read_text();O=D/(id+'-prepared');O.mkdir(exist_ok=True)
 def flat(s,base):
  out=[]
  for line in s.splitlines():
   active=re.split(r'(?<!\\)%',line,maxsplit=1)[0];m=re.search(r'\\input\s*(?:\{([^}]+)\}|([^\s%]+))',active)
   if m:
    f=base/(m[1] or m[2]);f=f if f.suffix else f.with_suffix('.tex')
    out+=['% ORIGINAL INPUT '+str(f.relative_to(Q)),flat(f.read_text(),f.parent),'% END ORIGINAL INPUT '+str(f.relative_to(Q))]
   else:out.append(line)
  return '\n'.join(out)
 lmcs=(Q/'lmcs.cls').read_text();env=lmcs[lmcs.index(r'\theoremstyle{plain}',lmcs.index('%%% Theorem environments')):lmcs.index('% end-of-proof sign')]
 start=main.index(r'\numberwithin') if id.startswith('2501') else main.index(r'\usepackage[utf8]')
 pre=flat(main[start:main.index(r'\begin{document}')],Q)
 (O/'wrapper.tex').write_text(basic+env+'\n'+pre+'\n'+r'\AtBeginDocument{\def\shorttitle{'+('MSO ordinal-rank dichotomy' if id.startswith('2501') else 'Probabilistic choreography projection')+'}}\n')
 ab=re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}',main,re.S)[1];body=main[re.search(r'^\\maketitle\s*$',main,re.M).end():main.index(r'\bibliographystyle')]
 credits=''
 if id.startswith('2501'):credits=r'\paragraph{Original publication credits.} All authors are supported by the National Science Centre, Poland (grant no.\@ 2021/\allowbreak41/\allowbreak B/\allowbreak ST6/\allowbreak03914). This is a journal version of a paper that originally appeared at STACS 2025.'+'\n'
 body=credits+r'\paragraph{Original abstract.} '+ab+'\n'+flat(body,Q);(O/'rendercopy-body.tex').write_text(body+'\n')
 keys=[]
 for m in re.finditer(r'\\cite\w*(?:\[[^\]]*\]){0,2}\{([^}]+)\}',body):
  keys.extend(k.strip() for k in m[1].split(','))
 keys=sorted(set(keys))
 (O/'references.aux').write_text('\\relax\n'+''.join('\\citation{'+k+'}\n' for k in keys)+'\\bibstyle{alphaurl}\n\\bibdata{'+str(Q/bib)+'}\n')
 envp=dict(os.environ);envp['PATH']='/disks/sata1/yupeng/human-proof-corpus/runtime/texlive/2025/bin/x86_64-linux:'+envp['PATH'];envp['BSTINPUTS']=str(Q)+':'+str(D.parent/'scout-round11/2503.11590v4')+':'
 r=subprocess.run(['bibtex','references'],cwd=O,env=envp,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True);(O/'bibtex.stdout').write_text(r.stdout);print(id,'bib',r.returncode,'keys',len(keys),r.stdout[-300:])
 if id.startswith('2503'):shutil.copyfile(Q/'sml-highlight.sty',O/'sml-highlight.sty')
 (O/'probe.tex').write_text((O/'wrapper.tex').read_text()+r'\graphicspath{{../'+id+r'/}}'+'\n'+r'\begin{document}'+'\n'+body+'\n'+(O/'references.bbl').read_text()+'\n'+r'\end{document}'+'\n')
 r=subprocess.run(['xelatex','-no-shell-escape','-interaction=nonstopmode','-halt-on-error','-file-line-error','probe.tex'],cwd=O,env=envp,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True);(O/'xelatex-1.stdout').write_text(r.stdout);print(id,'body',len(body.splitlines()),'tex',r.returncode,r.stdout[-900:])
