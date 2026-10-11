import pathlib,re,json
root=pathlib.Path(r'D:/tmp/r2work/repo')
queries={'chow.tex':['definition-periodic-complex','definition-periodic-length','definition-periodic-determinant'],'defos.tex':['lemma-canonical-class','lemma-induced-map'],'equiv.tex':['definition-siblings','lemma-good-map'],'stacks-morphisms.tex':['lemma-DM-residual-gerbe','lemma-slice'],'decent-spaces.tex':['lemma-bounded-fibres']}
for file,labels in queries.items():
 lines=(root/file).read_text(encoding='utf8').splitlines()
 for label in labels:
  at=next(i for i,x in enumerate(lines) if '\\label{'+label+'}' in x);a=at
  while a>=0 and not re.search(r'\\begin\{|\\section\{',lines[a]):a-=1
  env=re.search(r'\\begin\{([^}]+)\}',lines[a]);end=next((i for i in range(at+1,len(lines)) if '\\end{'+env.group(1)+'}' in lines[i]),at+1) if env else at+1
  pr=next((i for i in range(end+1,min(end+12,len(lines))) if '\\begin{proof}' in lines[i]),None)
  if pr is not None:end=next(i for i in range(pr+1,len(lines)) if '\\end{proof}' in lines[i])
  print(file,label,a+1,end+1)
for file,label in [('chow','lemma-tricky'),('defos','lemma-canonical-class-obstruction'),('equiv','proposition-siblings-isomorphic'),('groupoids','lemma-algebraic-quasi-projective'),('decent-spaces','lemma-there-is-a-scheme-integral-over-refined'),('spaces-cohomology','lemma-weak-chow'),('stacks-morphisms','theorem-DM')]:
 text=(root/'tags/tags').read_text(encoding='utf8');match=re.search(r'^([^,\n]+),'+re.escape(file+'-'+label)+'$',text,re.M);print('TAG',file,label,match.group(1) if match else None)
