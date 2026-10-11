import pathlib,re
root=pathlib.Path(r'D:/tmp/r2work/repo')
queries={'hypercovering.tex':['definition-covering-SR','definition-hypercovering','lemma-h0-cech','lemma-cech-spectral-sequence','lemma-covering','lemma-acyclic-hypercover-sheaves'],'spaces-simplicial.tex':['lemma-augmentation-spectral-sequence','lemma-localize-injective','lemma-hypercovering-cech-complex','lemma-hypercovering-descent-sheaves'],'cotangent.tex':['lemma-O-homology-B-homology','lemma-apply-O-B-comparison'],'proetale.tex':['lemma-derived-complete-zero','lemma-derived-complete-limit','lemma-describe-constructible-complexes']}
for f,labels in queries.items():
 lines=(root/f).read_text(encoding='utf8').splitlines()
 for label in labels:
  at=next(i for i,x in enumerate(lines) if '\\label{'+label+'}' in x);a=at
  while a>=0 and '\\begin{' not in lines[a]:a-=1
  env=re.search(r'\\begin\{([^}]+)\}',lines[a]).group(1);b=next(i for i in range(at+1,len(lines)) if '\\end{'+env+'}' in lines[i]);pr=next((i for i in range(b+1,min(b+12,len(lines))) if '\\begin{proof}' in lines[i]),None)
  if pr is not None:b=next(i for i in range(pr+1,len(lines)) if '\\end{proof}' in lines[i])
  print(f,label,a+1,b+1)
