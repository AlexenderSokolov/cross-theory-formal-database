from html.parser import HTMLParser
from pathlib import Path
import re,json,sys
GRAPHICS = {}
class N:
 def __init__(self,t,a=()):self.t=t;self.a=dict(a);self.c=[]
class Parser(HTMLParser):
 def __init__(self):super().__init__(convert_charrefs=True);self.root=N('root');self.stack=[self.root]
 def handle_starttag(self,t,a):
  n=N(t,a);self.stack[-1].c.append(n)
  if t not in {'meta','link','img','br','hr','input','base','wbr','source'}:self.stack.append(n)
 def handle_startendtag(self,t,a):self.handle_starttag(t,a);self.handle_endtag(t)
 def handle_endtag(self,t):
  for i in range(len(self.stack)-1,0,-1):
   if self.stack[i].t==t:self.stack=self.stack[:i];break
 def handle_data(self,d):self.stack[-1].c.append(d)
def esc(s):
 return ''.join({'\\':r'\textbackslash{}','&':r'\&','%':r'\%','$':r'\$','#':r'\#','_':r'\_','{':r'\{','}':r'\}','~':r'\textasciitilde{}','^':r'\textasciicircum{}'}.get(c,c) for c in s).replace('\u2062','').replace('\u200b','').replace('\u2009',r'\thinspace{}').replace('\u220e',r'\ensuremath{\blacksquare}').replace('\u2023',r'\ensuremath{\blacktriangleright}')
def nodes(n,t=None):
 if isinstance(n,str):return
 if t is None or n.t==t:yield n
 for c in n.c:yield from nodes(c,t)
def plain(n):
 if isinstance(n,str):yield n
 else:
  for c in n.c:yield from plain(c)
def render(n,eq=False):
 if isinstance(n,str):return esc(n)
 cl=n.a.get('class','');tag=n.t
 if tag in ['script','style','svg']:return ''
 if tag=='object' and n.a.get('type')=='image/svg+xml':
  target=GRAPHICS.get(n.a.get('data'))
  if target is None:raise ValueError('SVG object has no prepared asset: '+n.a.get('data',''))
  # Handle the object as one image; never recurse into its fallback img.
  return '\n\\par\\noindent\\includegraphics[width=\\linewidth,height=0.78\\textheight,keepaspectratio]{'+target+'}\\par\n'
 if tag=='img' and n.a.get('src') in GRAPHICS:
  return '\n\\par\\noindent\\includegraphics[width=\\linewidth,height=0.78\\textheight,keepaspectratio]{'+GRAPHICS[n.a['src']]+'}\\par\n'
 if tag=='math':
  a=n.a.get('alttext','');a=re.sub(r'%\\?\n', '', a); refs=[''.join(x for x in plain(c)).strip() for c in nodes(n,'a')]; ri=iter(refs)
  a=re.sub(r'\\hyperref@@ii\[[^]]*\]\{[^}]*\}|\\lx@cref\{[^}]*\}\{[^}]*\}',lambda m:next(ri,'source reference'),a)
  a=re.sub(r'\\eqref\{[^}]*\}',lambda m:'('+next(ri,'source reference')+')',a)
  a=a.replace(r'\leavevmode', '').replace(r'\hfill','').replace(r'\mathrm{\Delta}',r'\Delta')
  embedded=list(nodes(n,'img'))
  if embedded and r'\includegraphics' in a:
   if len(embedded)!=1:raise ValueError('Ambiguous embedded math images: '+n.a.get('id',''))
   original=embedded[0];target=GRAPHICS.get(original.a.get('src'))
   if target is None:raise ValueError('Embedded math image has no asset: '+original.a.get('src',''))
   height=float(original.a.get('height','9'))*0.75
   image_tex=r'\hbox{\includegraphics[height='+str(height)+'bp]{'+target+'}}'
   a,count=re.subn(r'(?:\\immediate\s*)*\\hbox\{\{\\includegraphics\{\}\{\}\{[^}]+\}\}\}',lambda m:image_tex+'\n'*m.group(0).count('\n'),a)
   if count!=1:raise ValueError('Embedded math graphic encoding not recognized: '+n.a.get('id',''))
  # LaTeXML encodes this dotted union with an unusable zero accent code.
  a=re.sub(r'\\mathaccent\s+0\{\\cdot\}\\cup',lambda m:r'\dot{\cup}'+'\n'*m.group(0).count('\n'),a)
  return a if eq else ('$'+a+'$' if n.a.get('display')!='block' else '\n\\['+a+'\\]\n')
 if 'ltx_note_mark' in cl or 'ltx_tag_note' in cl:return ''
 if 'ltx_note_outer' in cl:return ''.join(render(c) for c in n.c)
 if 'ltx_note_content' in cl:return r'\footnote{'+''.join(render(c) for c in n.c)+'}'
 if tag=='table' and 'ltx_eqn' in cl:
  rows=[]
  for row in nodes(n,'tr'):
   cells=[]
   for cell in row.c:
    if isinstance(cell,N) and cell.t=='td' and 'ltx_eqn_eqno' not in cell.a.get('class',''):
     text=''.join(render(c,True) for c in cell.c).strip()
     if text:cells.append(text)
   if cells:rows.append(' '.join(cells))
  return '\n\\[\\begin{gathered}\n'+(' \\\\\n'.join(rows))+'\n\\end{gathered}\\]\n'
 body=''.join(render(c,eq) for c in n.c)
 if tag in ['h1','h2','h3','h4','h5','h6']:return '\n\\par\\medskip\\noindent\\textbf{'+body+'}\\par\n'
 if tag=='p':return '\n'+body+'\\par\n'
 if tag in ['ul','ol']:return '\n\\begin{'+('enumerate' if tag=='ol' else 'itemize')+'}\n'+body+'\n\\end{'+('enumerate' if tag=='ol' else 'itemize')+'}\n'
 if tag=='li':return '\n\\item[] '+body+'\n'
 if tag=='br':return '\n'
 if tag=='tr':return body+r'\par'+ '\n'
 if tag in ['td','th']:return body+' '
 if tag=='table':return '\n'+body+'\n'
 if tag=='img':return ''
 if 'ltx_font_italic' in cl and tag in ['span','em']:return (r'{\itshape '+body+'}') if (r'\par' in body or re.search(r'\n\s*\n',body)) else (r'\emph{'+body+'}')
 if 'ltx_font_bold' in cl and tag in ['span','strong']:return (r'{\bfseries '+body+'}') if (r'\par' in body or re.search(r'\n\s*\n',body)) else (r'\textbf{'+body+'}')
 if 'ltx_theorem' in cl and 'ltx_theorem_' in cl:return '\n% SOURCE-ID '+n.a.get('id','')+'\n'+body+'\n% END-SOURCE-ID '+n.a.get('id','')+'\n'
 return body
if __name__=='__main__':
 p=Path(sys.argv[1]);ledger=p/'svg-asset-ledger.json'
 if ledger.exists():GRAPHICS.update({x['html_data']:Path(x['target']).name for x in json.loads(ledger.read_text())['objects']})
 images=p/'html-image-ledger.json'
 if images.exists():GRAPHICS.update({x['html_src']:Path(x['target']).name for x in json.loads(images.read_text())['images']})
 parser=Parser();parser.feed((p/'published.html').read_text());article=next(nodes(parser.root,'article'))
 parts=[render(n) for n in article.c if isinstance(n,N) and n.t=='section'];out='\n'.join(parts);(p/'official-source.tex').write_text(out)
 lines=out.splitlines();m={}
 for i,l in enumerate(lines):
  if l.startswith('% SOURCE-ID '):m[l[12:]]=[i+1,0]
  if l.startswith('% END-SOURCE-ID '):
   k=l[16:]
   if k in m:m[k][1]=i+1
 (p/'official-source-map.json').write_text(json.dumps(m,indent=2));print(len(lines),m)
