import pathlib,re
root=pathlib.Path(r'D:/tmp/r2work/repo')
for file, labels in {'algebra.tex':['lemma-exact-on-fibres-open','lemma-complex-exact-mod','lemma-free-fibre-flat-free'],'spaces-pushouts.tex':['lemma-construct-elementary-distinguished-square','lemma-check-separated','lemma-separate-disjoint-locally-closed-by-blowing-up','lemma-blowup-iso-along','lemma-blowup-etale-along','lemma-replaced-by-strict-transform','lemma-compactification-dominates'],'discriminant.tex':['lemma-syntomic-quasi-finite','example-universal-quasi-finite-syntomic','lemma-locally-comes-from-universal','lemma-different-quasi-finite-complete-intersection']}.items():
 lines=(root/file).read_text(encoding='utf8').splitlines()
 for label in labels:
  at=next(i for i,x in enumerate(lines) if '\\label{'+label+'}' in x);a=at
  while a>=0 and not re.search(r'\\begin\{|\\section\{',lines[a]):a-=1
  end=next((i for i in range(at+1,len(lines)) if re.search(r'\\end\{(?:proof|remark|example)\}',lines[i])),at+1)
  print(file,label,a+1,end+1)
