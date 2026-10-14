from pathlib import Path
import sys,re,urllib.request
sys.path.append('/disks/sata1/yupeng/anaconda3/lib/python3.13/site-packages')
from bs4 import BeautifulSoup,NavigableString
import fitz
S=Path(__file__).resolve().parent
BASE='https://drops.dagstuhl.de/storage/00lipics/lipics-vol363-csl2026/html/LIPIcs.CSL.2026.28/'
h=BeautifulSoup((S/'source.html').read_text(),'html.parser')
names={}
for i,o in enumerate(h.find_all('object'),1):
 url=o['data'];name='graphic-%02d'%i;names[url]=name
 if not (S/(name+'.svg')).exists():
  with urllib.request.urlopen(BASE+url,timeout=30) as r:(S/(name+'.svg')).write_bytes(r.read())
 d=fitz.open(S/(name+'.svg'));(S/(name+'.pdf')).write_bytes(d.convert_to_pdf());d.close()
 print('retained graphic',i,url,flush=True)
def esc(t):
 t=re.sub(r'\s+',' ',t)
 t=t.replace('–','--').replace('—','---')
 return ''.join({'&':r'\&','%':r'\%','$':r'\$','#':r'\#','_':r'\_','{':r'\{','}':r'\}','~':r'\textasciitilde{}','^':r'\textasciicircum{}','\\':r'\textbackslash{}','‣':r'\ensuremath{\blacktriangleright}'}.get(c,c) for c in t)
def mt(n):
 a=re.sub(r'%\s*\n','',n.get('alttext',''))
 a=a.replace(r'\immediate','')
 for url,name in names.items():a=a.replace(url,name+'.pdf')
 return a
def render(n):
 if isinstance(n,NavigableString):return esc(str(n))
 if n.name in ['script','style','svg']:return ''
 if n.name=='math':return ('\\['+mt(n)+'\\]' if n.get('display')=='block' else '$'+mt(n)+'$')
 if n.name=='object':
  return '\n'+r'\begin{center}\includegraphics[width=0.95\linewidth,height=0.4\textheight,keepaspectratio]{'+names[n['data']]+r'.pdf}\end{center}'+'\n'
 if n.name=='img':
  if n.get('src')=='x1.png':return r'\includegraphics[height=1.2em]{source-x1.png}'
  return ''
 if 'ltx_note' in n.get('class',[]):
  content=n.find(class_='ltx_note_content')
  return r'\footnote{'+(''.join(render(c) for c in content.children) if content else ''.join(render(c) for c in n.children))+'}'
 t=''.join(render(c) for c in n.children)
 if n.name in ['h2','h3','h4','h5','h6']:t='\n'+r'\par\medskip\noindent\textbf{'+t.strip()+r'}\par'+'\n'
 elif n.name=='li':t='\n'+r'\par\noindent '+t+'\n'
 elif n.name in ['p','figcaption']:t='\n'+t.strip()+r'\par'+'\n'
 if n.get('id') and n.name in ['section','div','figure']:t='\n% BEGIN '+n['id']+'\n'+t+'\n% END '+n['id']+'\n'
 return t
# x1 is the author's small inline symbol, retained rather than dropped.
if h.find('img',src='x1.png'):
 with urllib.request.urlopen(BASE+'x1.png',timeout=30) as r:(S/'source-x1.png').write_bytes(r.read())
body='\n'.join(render(h.find(id=i)) for i in ['S1','S2','S3','S4','S5','S6','A1'])
(S/'author-editable.tex').write_text(body)
bib=[r'\begin{thebibliography}{99}']
for li in h.select('.ltx_bibitem'):
 tag=li.find(class_='ltx_tag_bibitem')
 number=tag.get_text(' ',strip=True) if tag else ''
 if tag:tag.decompose()
 bib.append(r'\bibitem{'+li['id'].replace('.','-')+'} '+render(li))
bib.append(r'\end{thebibliography}')
(S/'bibliography.tex').write_text('\n'.join(bib)+'\n')
print('Body',len(body.splitlines()),'math',len(h.find_all('math')),'graphics',len(names),'bibitems',len(h.select('.ltx_bibitem')),flush=True)
