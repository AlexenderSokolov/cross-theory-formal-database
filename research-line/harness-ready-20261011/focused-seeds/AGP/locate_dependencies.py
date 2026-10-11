import pathlib,re
root=pathlib.Path(r'D:/tmp/r2work/repo')
for file,labels in {'artin.tex':['lemma-base-change-versal','lemma-rs','section-axioms-functors'],'cotangent.tex':['remark-resolution','example-resolution-length-two','lemma-relation-with-naive-cotangent-complex','remark-explicit-comparison-map','remark-surjection','remark-elucidate-degree-two'],'weil.tex':['lemma-divide-difference-points','lemma-kernel-to-closure']}.items():
 lines=(root/file).read_text(encoding='utf8').splitlines()
 for label in labels:
  at=next(i for i,x in enumerate(lines) if '\\label{'+label+'}' in x);a=at
  while a>=0 and not re.search(r'\\begin\{|\\section\{',lines[a]):a-=1
  end=next((i for i in range(at+1,len(lines)) if re.search(r'\\end\{(?:proof|remark)\}',lines[i])),at+1)
  print(file,label,a+1,end+1)
