from pathlib import Path
from html.parser import HTMLParser
import re,json,pymupdf
P=Path('/disks/sata1/yupeng/human-proof-corpus/operations/codex-work-01a13349/research-line/codex-01a13349-20261013');D=P/'hyperlogic-complexity/sources/scout-round4'
class N:
 def __init__(self,tag='',attrs=(),parent=None):self.tag=tag;self.a=dict(attrs);self.ch=[];self.parent=parent
 def walk(self):
  yield self
  for c in self.ch:
   if isinstance(c,N):yield from c.walk()
class Parser(HTMLParser):
 def __init__(self):super().__init__(convert_charrefs=True);self.root=N('root');self.stack=[self.root]
 def handle_starttag(self,t,a):
  n=N(t,a,self.stack[-1]);self.stack[-1].ch.append(n)
  if t not in ['meta','link','img','br','hr','input','base','source','wbr','area','embed','param','col']:self.stack.append(n)
 def handle_startendtag(self,t,a):self.stack[-1].ch.append(N(t,a,self.stack[-1]))
 def handle_endtag(self,t):
  for i in range(len(self.stack)-1,0,-1):
   if self.stack[i].tag==t:self.stack=self.stack[:i];break
 def handle_data(self,s):self.stack[-1].ch.append(s)
def text(n):return n if isinstance(n,str) else ''.join(text(c) for c in n.ch)
def cls(n,c):return c in n.a.get('class','').split()
def esc(s):
 s=re.sub(r'\s+',' ',s)
 return ''.join({'\\':r'\textbackslash{}','{':r'\{','}':r'\}','$':r'\$','%':r'\%','&':r'\&','#':r'\#','_':r'\_','^':r'\textasciicircum{}','~':r'\textasciitilde{}'}.get(c,c) for c in s)
p=Parser();p.feed((D/'csl30-fulltext.html').read_text());nodes=list(p.root.walk());article=next(n for n in nodes if n.tag=='article' and cls(n,'ltx_document'))
# The sole arrow diagram is preserved as an exact vector crop from original published PDF, page18 equation7.1.
orig=pymupdf.open(D/'csl30.pdf');clip=pymupdf.Rect(105,536,510,583);crop=pymupdf.open();page=crop.new_page(width=clip.width,height=clip.height);page.show_pdf_page(page.rect,orig,17,clip=clip);crop.save(D/'original-diagram-S7.E1-page18.pdf')
RULES=r'''\displaystyle
\begin{aligned}
e&=e\oplus_r e\\
e_1\oplus_r e_2&=e_2\oplus_{1-r}e_1\\
(e_1\oplus_r e_2)\oplus_s e_3&=e_1\oplus_{rs}(e_2\oplus_{\frac{s(1-r)}{1-rs}}e_3)\\
a(e_1\oplus_r e_2)&=ae_1\oplus_r ae_2
\end{aligned}
\quad
\begin{gathered}
\mu v\,g=\mu u\,g[u/v]\\
\mu v\,g=g[\mu v\,g/v]\\
\frac{f=g[f/v]}{f=\mu v\,g}
\end{gathered}
\quad
\begin{gathered}
\frac{e_1=e_2}{ae_1=ae_2}\\[3pt]
\frac{e_1=f_1\quad e_2=f_2}{e_1\oplus_r e_2=f_1\oplus_r f_2}\\[3pt]
\frac{e_1=f_1\ \dots\ e_n=f_n}{k[\vec e/\vec v]=k[\vec f/\vec v]}
\end{gathered}
'''
# The generated alttext flattens four inference bars in S3.Ex10.m1. The above is a literal editable transcription of publisher Figure1/page7, not a new rule.
anchors=[];math_used=[]
def anchor(n):
 id=n.a.get('id')
 if not id:return ''
 anchors.append(id);return '%\n% SOURCE HTML #'+id+'\n'+r'\hypertarget{html:'+id+'}{}'
def inside(n):return ''.join(render(c) for c in n.ch)
def render(n):
 if isinstance(n,str):return esc(n)
 if n.tag in ['script','style','annotation','annotation-xml']:return ''
 if cls(n,'ltx_note'):
  content=next((x for x in n.walk() if cls(x,'ltx_note_content')),None)
  if content:
   children=[x for x in content.ch if not(isinstance(x,N) and (cls(x,'ltx_note_mark') or cls(x,'ltx_tag_note')))]
   return anchor(n)+r'\footnote{'+''.join(render(x) for x in children)+'}'
 if n.a.get('id')=='S7.E1':return anchor(n)+r'\begin{center}\includegraphics[width=.8\linewidth]{original-diagram-S7.E1-page18.pdf}\end{center}'+'\n'
 if n.tag=='object':
  id=n.a.get('id');assert n.a.get('type')=='image/svg+xml' and (D/'publisher-figures'/(id+'.pdf')).is_file(),n.a
  return anchor(n)+r'\begin{center}\includegraphics[width='+n.a['width']+r'pt]{'+id+r'.pdf}\end{center}'+'\n'
 if n.tag=='svg':raise ValueError('unexpected mathematical SVG '+str(n.a.get('id')))
 if n.tag=='math':
  code=n.a.get('alttext');assert code is not None,n.a
  math_used.append(n.a.get('id'));code=RULES if n.a.get('id')=='S3.Ex10.m1' else code
  code=re.sub(r'(?<!\\)%[^\n]*\n','',code)
  code=re.sub(r'\\cal\s+([A-Za-z])',lambda m:r'\mathcal{'+m.group(1)+'}',code)
  if n.a.get('id')=='S5.Thmtheorem1.p1.m8':
   code=r'\begin{aligned}\operatorname{conv}(U)&=\{r\vec{p}+(1-r)\vec{q}\\&\mid\vec{p},\vec{q}\in U\text{ and }r\in[0,1]\}\end{aligned}'
  return anchor(n)+(r'\['+code+r'\]' if n.a.get('display')=='block' or n.a.get('id')=='S5.Thmtheorem1.p1.m8' else r'\({'+code+r'}\)')
 if n.tag in ['h1','h2','h3','h4','h5','h6']:
  s=inside(n)
  # Hyperlink destinations are not safe inside amsart moving section titles.
  # Preserve every original HTML anchor immediately before its same visible title.
  if cls(n,'ltx_title_section') or cls(n,'ltx_title_subsection'):
   ap=r'%\n% SOURCE HTML #[^\n]+\n\\hypertarget\{html:[^}]+\}\{\}'
   targets=''.join(re.findall(ap,s));s=re.sub(ap,'',s)
   command=r'\section*{' if cls(n,'ltx_title_section') else r'\subsection*{'
   return anchor(n)+targets+command+s.strip()+'}\n'
  return anchor(n)+r'\par\noindent\textbf{'+s.strip()+r'}\quad '
 if n.tag=='p':return anchor(n)+inside(n)+'\n'+r'\par\medskip'+'\n'
 if n.tag=='figure':return anchor(n)+'\n'+r'\begin{center}'+'\n'+inside(n)+'\n'+r'\end{center}'+'\n'
 if n.tag=='figcaption':return '\n'+r'\par\smallskip '+inside(n)+'\n'+r'\par\medskip'+'\n'
 if n.tag in ['ul','ol']:return anchor(n)+'\n'+r'\begin{list}{}{\leftmargin=2em}'+'\n'+inside(n)+'\n'+r'\end{list}'+'\n'
 if n.tag=='li':return anchor(n)+'\n'+r'\item[] '+inside(n)+'\n'
 if n.tag=='br':return r'\newline{}'
 if n.tag=='img':
  # No mathematical raster images occur in the selected manuscript sections. Source frontmatter logos remain available in original HTML/PDF.
  raise ValueError('unexpected manuscript image '+str(n.a))
 if n.tag=='a':
  s=inside(n);url=n.a.get('href','')
  if url.startswith('#'):return r'\hyperlink{html:'+url[1:]+'}{'+s+'}'
  if url.startswith(('http:','https:')):return r'\href{'+url.replace('%',r'\%').replace('#',r'\#')+'}{'+s+'}'
  return s
 if n.tag in ['em','i'] or cls(n,'ltx_font_italic'):return anchor(n)+r'\emph{'+inside(n)+'}'
 if n.tag in ['b','strong'] or cls(n,'ltx_font_bold'):return anchor(n)+r'\textbf{'+inside(n)+'}'
 if cls(n,'ltx_font_typewriter'):
  raw=text(n)
  return anchor(n)+(r'\nolinkurl{'+raw+'}' if raw.startswith(('doi:','http:','https:','www.')) else r'\texttt{'+inside(n)+'}')
 if n.tag in ['sup','sub']:return anchor(n)+(r'\textsuperscript{' if n.tag=='sup' else r'\textsubscript{')+inside(n)+'}'
 return anchor(n)+inside(n)
chosen=[]
abstract=next((n for n in article.walk() if cls(n,'ltx_abstract')),None)
if abstract:chosen.append(abstract)
chosen += [n for n in article.walk() if cls(n,'ltx_classification') and any(isinstance(c,N) and c.tag=='h6' and text(c).strip().startswith(('Funding:','Acknowledg')) for c in n.ch)]
chosen += [n for n in article.ch if isinstance(n,N) and (n.tag=='section' or cls(n,'ltx_bibliography'))]
assert any(n.a.get('id')=='S7' for n in chosen)
s='\n'.join(render(n) for n in chosen)
s=s.replace('}\\n','}\n')
s=s.replace('% SOURCE HTML #S1\n',r'\par\noindent\textbf{Funding (original publisher PDF page1 and article metadata):} Lawrence S. Moss: Lawrence S. Moss was supported by grant \#586136 from the Simons Foundation. Alexandra Silva: ERC grant Autoprobe (no. 101002697). This work was done in part while the author was visiting the Simons Institute for the Theory of Computing.\par\medskip'+'\n% SOURCE HTML #S1\n',1)
s=re.sub(r'(?<![\w{/])www\.[A-Za-z0-9./_-]+',lambda m:r'\nolinkurl{'+m.group(0)+'}',s)
assert not any(ord(c)<32 and c not in '\n\t\r' for c in s), 'unexpected control byte in converter output'
(D/'rendercopy-csl30.tex').write_text(s+'\n')
(D/'csl30-formula-anchors.json').write_text(json.dumps(dict(source='CSL2025.30 official CC BY4 full LaTeXML HTML',html='csl30-fulltext.html',math_ids=math_used,structural_override=dict(id='S3.Ex10.m1',basis='Original PDF page7 Figure1 inference bars, editable literal transcription'),diagram=dict(id='S7.E1',basis='Original PDF page18 vector crop, full equation7.1 labels retained')),indent=2)+'\n')
print('chosen',[(n.tag,n.a.get('id'),n.a.get('class')) for n in chosen]);print('math rendered',len(math_used),'anchors',len(anchors),'renderlines',len(s.splitlines()))
