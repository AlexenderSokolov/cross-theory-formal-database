import pathlib,re
root=pathlib.Path(r'D:/tmp/r2work/repo')
for f,labels in {'flat.tex':['example-two-generators','lemma-h-sheaf-colim-F','lemma-colim-F-Vect'],'groupoids.tex':['lemma-integral-over-invariants','lemma-invariants-base-change','lemma-points'],'more-groupoids.tex':['lemma-finite-flat-over-almost-dense-subscheme','lemma-find-affine-integral'],'injectives.tex':['lemma-derived-products']}.items():
 lines=(root/f).read_text(encoding='utf8').splitlines()
 for lab in labels:
  at=next(i for i,x in enumerate(lines) if '\\label{'+lab+'}' in x);a=at
  while a>=0 and '\\begin{' not in lines[a]:a-=1
  env=re.search(r'\\begin\{([^}]+)\}',lines[a]).group(1);b=next(i for i in range(at+1,len(lines)) if '\\end{'+env+'}' in lines[i]);pr=next((i for i in range(b+1,min(b+12,len(lines))) if '\\begin{proof}' in lines[i]),None)
  if pr is not None:b=next(i for i in range(pr+1,len(lines)) if '\\end{proof}' in lines[i])
  print(f,lab,a+1,b+1)
