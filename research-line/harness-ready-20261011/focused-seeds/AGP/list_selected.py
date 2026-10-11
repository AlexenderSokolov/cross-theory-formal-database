import pathlib,re,json
P=pathlib.Path(r'C:/Users/20600/Documents/Codex/corpus-repair-20261010/research-line/harness-ready-20261011');R=P.parents[1]
ids=['S001-lemma-smash-nilpotence','S001-more-groupoids-lemma-slice','S001-theorem-multiplicity-with-koszul','S001-lemma-compare-higher','S001-lemma-openness-smoothness','S001-lemma-non-effective-descent-projective','S001-proposition-tate-map','S001-theorem-keel-mori']
for id in ids:
 p=R/'research-line/archive/2026-10-10/initial_corpus/items'/f'{id}.tex';s=p.read_text(encoding='utf8');print(id, len(s.splitlines()),s[:500].replace('\n',' | '))
