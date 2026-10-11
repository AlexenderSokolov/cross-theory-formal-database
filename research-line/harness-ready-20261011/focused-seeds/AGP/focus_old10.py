exec(open(__file__.replace('focus_old10.py','inspect_metadata.py'),encoding='utf-8-sig').read().split('m=load')[0])
ids=['S001-chow-lemma-tricky','S001-criteria-theorem-bootstrap','S001-lemma-canonical-class-obstruction','S001-proposition-annihilator-complex','S001-lemma-S2-extensions','S001-proposition-siblings-isomorphic','S001-lemma-algebraic-quasi-projective','S001-lemma-there-is-a-scheme-integral-over-refined','S001-lemma-weak-chow','S001-theorem-DM','S001-theorem-quasi-DM']
rows=[json.loads(x) for x in (P.parent/'index.jsonl').read_text(encoding='utf-8-sig').splitlines()]
for x in rows:
 if x['problem_id'] in ids:
  print('\n###',x['problem_id'],x['source_file']);s=(R/x['item_path']).read_text(encoding='utf8');end=s.find('\\begin{proof}');print(s[:end][:2600]);print('REASON',x['difficulty_reason'][:1600]);print('REVIEWS',x['review_evidence'],'FLAGS',x['review_flags'])
