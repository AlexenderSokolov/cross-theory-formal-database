# Mechanical conversion example actually used for FSCD2025.20.
# Copy into your own lane and edit S, BASE and SECTIONS. Do not run this copy
# against another lane. Inspect source-specific TeX macros, tables, images,
# footnotes and proof boundaries; this script does not decide mathematical scope.
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString
import urllib.request, re
S = Path(__file__).parent / 'fscd-2025-23'
BASE = 'https://drops.dagstuhl.de/storage/00lipics/lipics-vol337-fscd2025/html/LIPIcs.FSCD.2025.23/'
SECTIONS = ['Sx1','S1','S2','S3','S4','S5','S6','A1']
s = BeautifulSoup((S/'source.html').read_text(), 'html.parser')
names = {}
for i,o in enumerate(s.find_all('object'),1):
    name='graphic-%02d'%i; names[o['data']]=name
    urllib.request.urlretrieve(BASE+o['data'],S/(name+'.svg'))
# FSCD20-only native-ref resolution, checked against the publisher MathML text.
# Replace this dictionary in a new source, never reuse its numbers blindly.
refs={}

def mathtex(n):
    a=re.sub(r'%\s*\n','',n.get('alttext',''))
    def replace(m):
        assert m.group(1) in refs, m.group(1)
        return refs[m.group(1)]
    return re.sub(r'\\ref\{([^}]+)\}',replace,a)
def esc(t):
    return ''.join({'&':r'\&','%':r'\%','$':r'\$','#':r'\#','_':r'\_','{':r'\{','}':r'\}','~':r'\textasciitilde{}','^':r'\textasciicircum{}','\\':r'\textbackslash{}','‣':r'\ensuremath{\blacktriangleright}'}.get(c,c) for c in re.sub(r'\s+',' ',t))
def render(n):
    if isinstance(n,NavigableString): return esc(str(n))
    if n.name=='math':
        objects=n.find_all('object')
        if objects:
            return ''.join(r'\includegraphics[width='+str(min(float(o.get('width',200)),450))+r'pt]{'+names[o['data']]+'.pdf}' for o in objects)
        return ('\\['+mathtex(n)+'\\]' if n.get('display')=='block' else '$'+mathtex(n)+'$')
    if n.name=='object':
        return '\n\\begin{center}\\includegraphics[width=0.95\\linewidth,height=0.45\\textheight,keepaspectratio]{'+names[n['data']]+'.pdf}\\end{center}\n'
    if n.name in ['script','style','svg','img']: return ''
    text=''.join(render(c) for c in n.children)
    if n.name in ['h2','h3','h4','h5','h6']: text='\n\\par\\medskip\\noindent\\textbf{'+text.strip()+'}\\par\n'
    elif n.name=='li': text='\n\\par\\noindent '+text+'\n'
    elif n.name in ['p','figcaption']: text='\n'+text.strip()+'\\par\n'
    if n.get('id') and n.name in ['section','div','figure']: text='\n% BEGIN '+n['id']+'\n'+text+'\n% END '+n['id']+'\n'
    return text
body='\n'.join(render(s.find(id=x)) for x in SECTIONS)
(S/'author-extract.tex').write_text(body)
(S/'bibliography.tex').write_text(render(s.find(id='bib')))
for i,l in enumerate(body.splitlines(),1):
    if l.startswith('% BEGIN ') or l.startswith('% END '): print(i,l)
# Original SVG -> PDF: run separately using the existing runtime Python with fitz:
# import fitz
# for f in S.glob('graphic-*.svg'):
#     d=fitz.open(f); f.with_suffix('.pdf').write_bytes(d.convert_to_pdf())
