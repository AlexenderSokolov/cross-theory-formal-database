import pathlib,json
p=pathlib.Path(r'C:/Users/20600/Documents/Codex/corpus-repair-20261010/research-line/harness-ready-20261011')
layout=p/'focused-seeds/ACL/sources/article-layout.tex'
layout.write_text(r'''% Mechanical standalone compatibility; mathematical author macros remain authoritative.
\usepackage{hyperref}
\providecommand{\ie}{i.e.}
\providecommand{\eg}{e.g.}
\providecommand{\resp}{resp.}
\providecommand{\No}[1]{\left\| #1 \right\|}
\makeatletter
\@ifundefined{cal}{\DeclareOldFontCommand{\cal}{\normalfont}{\mathcal}}{}
\makeatother
''',encoding='utf-8')
ids=['ACL-analysis-heat-disjoint-boundary-controllability','ACL-analysis-heat-intersecting-null-boundary-control','ACL-analysis-heat-boundary-collar-exact-desensitization','ACL-analysis-hartree-low-regularity-asymptotic-stability','ACL-analysis-hypoelliptic-chain-weak-harnack','ACL-analysis-lattice-modified-wave-operator-completeness','ACL-analysis-moyal-free-evolution-dispersive-decay','ACL-analysis-schrodinger-determinant-lq-optimal-potential']
for tid in ids:
 f=p/'focused-seeds/ACL'/tid/'task.json';t=json.loads(f.read_text(encoding='utf-8-sig'));s=dict(path=str(layout.relative_to(p)),start_line=1,end_line=9,label='mechanical article compatibility for original publication-class layout macros');t['assembly']['preamble_spans']=[s]+[x for x in t['assembly']['preamble_spans'] if x['path']!=s['path']];f.write_text(json.dumps(t,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(tid)
f=p/'focused-seeds/ACL/ACL-logic-hott-choice-well-ordering-universe-correct/task.json';t=json.loads(f.read_text(encoding='utf-8-sig'));s=dict(path='focused-seeds/AGP/sources/hott-book-578b85cc/extracted/book-578b85cc8d586b1677ec4335148adeb443057d24/hits.tex',start_line=1205,end_line=1208,label='original remark on quotients of non-sets, retained to resolve the referenced scope')
t['context_spans']=[s]+t['context_spans'];t['assembly']['body_spans']=[dict(s,role='context')]+t['assembly']['body_spans'];t['assembly']['editorial_notes'].append('The original fixed-edition label-number file does not list rmk:quotient-of-non-set. Its actual four-line author remark is included with the native label instead of assigning an unverified printed number.');f.write_text(json.dumps(t,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')