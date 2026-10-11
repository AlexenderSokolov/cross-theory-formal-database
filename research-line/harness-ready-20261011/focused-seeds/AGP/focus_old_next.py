exec(open(__file__.replace('focus_old_next.py','inspect_metadata.py'),encoding='utf-8-sig').read().split('m=load')[0])
ids=['S001-artin-lemma-approximate','S001-artin-lemma-limit-preserving','S001-lemma-coequalizer','S001-theorem-complexes-algebraic','S001-lemma-polarized-diagonal-separated-fp','S001-theorem-chow-finite-type','S001-lemma-algebraization-principal-bis','S001-lemma-cd-1-canonical','S001-proposition-effective','S001-theorem-remarkable-equivalence']
rows=[json.loads(x) for x in (P.parent/'index.jsonl').read_text(encoding='utf-8-sig').splitlines()]
for x in rows:
 if x['problem_id'] in ids:
  print('\n###',x['problem_id'],x['source_file']);s=(R/x['item_path']).read_text(encoding='utf8');end=s.find('\\begin{proof}');print(s[:end][:2000]);print('REASON',x['difficulty_reason'][:1700]);print('REVIEWS',x['review_evidence'],'FLAGS',x['review_flags'])
