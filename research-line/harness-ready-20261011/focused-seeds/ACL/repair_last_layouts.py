import pathlib,json
p=pathlib.Path(r'C:/Users/20600/Documents/Codex/corpus-repair-20261010/research-line/harness-ready-20261011')
def read(tid):
 f=p/'focused-seeds/ACL'/tid/'task.json';return f,json.loads(f.read_text(encoding='utf-8-sig'))
def save(f,t):f.write_text(json.dumps(t,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
layout=p/'focused-seeds/ACL/sources/nls-layout.tex';layout.write_text('\\usepackage{xfrac}\n\\providecommand{\\ie}{i.e.}\n\\providecommand{\\eg}{e.g.}\n\\providecommand{\\resp}{resp.}\n',encoding='utf-8')
f,t=read('ACL-analysis-nls-flat-torus-almost-global-stability');t['assembly']['preamble_spans']=[dict(path=str(layout.relative_to(p)),start_line=1,end_line=4,label='standalone publication-class fraction and prose abbreviations')]+t['assembly']['preamble_spans'];save(f,t)
f,t=read('ACL-combinatorics-ordinal-general-cantor-sum-ramsey-degrees');s=dict(path='sources/ordinal-big-ramsey-2305.07192v3/source0.tex',start_line=1900,end_line=1917,label='original cited Appendix table of finite coefficient counts');t['context_spans'].append(s);t['assembly']['body_spans'].append(dict(s,role='context'));save(f,t)
layout=p/'focused-seeds/ACL/sources/product-matching-layout.tex';layout.write_text('\\crefname{thm}{theorem}{theorems}\n\\Crefname{thm}{Theorem}{Theorems}\n',encoding='utf-8')
f,t=read('ACL-combinatorics-product-graph-perfect-matching-hitting-time');t['assembly']['preamble_spans'].append(dict(path=str(layout.relative_to(p)),start_line=1,end_line=2,label='cleveref name for original thm environment'));s=dict(path='sources/product-graph-matchings-2404.14020v4/source0.tex',start_line=1652,end_line=1688,label='original cited discussion section');t['context_spans'].append(s);t['assembly']['body_spans'].append(dict(s,role='context'));save(f,t)