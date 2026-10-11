exec(open(__file__.replace('research_compact.py','inspect_metadata.py'),encoding='utf-8-sig').read().split('m=load')[0])
ids=['S001-proposition-tate-map','S001-proposition-poincare-duality','S001-proposition-relative-poincare-duality','S001-lemma-Garel','S001-lemma-Garel-upstairs','S001-lemma-compare-higher','S001-lemma-openness-smoothness','S001-theorem-quillen-spectral-sequence','S001-proposition-injective-pic','S001-lemma-non-effective-descent-projective']
rows=[json.loads(x) for x in (P.parent/'index.jsonl').read_text(encoding='utf-8-sig').splitlines()]
for x in rows:
 if x['problem_id'] in ids:
  print('\n###',x['problem_id'],x['source_file']);print(x['difficulty_reason'][:2100]);print('REVIEWS',x['review_evidence']);print('LOCATORS',x['statement_locator'][:100],x['proof_locator'][:100])
