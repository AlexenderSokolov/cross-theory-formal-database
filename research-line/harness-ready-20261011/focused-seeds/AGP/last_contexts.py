import pathlib,re
root=pathlib.Path(r'D:/tmp/r2work/repo')
for file,label in [('chow.tex','remark-more-elementary'),('stacks-morphisms.tex','definition-DM')]:
 lines=(root/file).read_text(encoding='utf8').splitlines();matches=[i for i,x in enumerate(lines) if '\\label{'+label+'}' in x]
 if not matches:continue
 at=matches[0];a=at
 while a>=0 and not re.search(r'\\begin\{|\\section\{',lines[a]):a-=1
 env=re.search(r'\\begin\{([^}]+)\}',lines[a]);b=next(i for i in range(at+1,len(lines)) if '\\end{'+env.group(1)+'}' in lines[i]);print(file,label,a+1,b+1)
