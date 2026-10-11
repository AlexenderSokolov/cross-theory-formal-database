import pathlib,re
root=pathlib.Path(r'D:/tmp/r2work/repo')
for f,labels in {'spaces-pushouts.tex':['lemma-colimit-check-etale-locally','lemma-descend-etale-proper-surjective'],'stacks-more-morphisms.tex':['lemma-make-section'],'moduli.tex':['lemma-polarized-diagonal-separated-fp']}.items():
 lines=(root/f).read_text(encoding='utf8').splitlines()
 for label in labels:
  at=next(i for i,x in enumerate(lines) if '\\label{'+label+'}' in x);a=at
  while a>=0 and '\\begin{' not in lines[a]:a-=1
  b=next(i for i in range(at+1,len(lines)) if '\\end{proof}' in lines[i]);print(f,label,a+1,b+1)
