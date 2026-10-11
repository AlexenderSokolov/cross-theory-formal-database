exec(open(__file__.replace('read_research.py','inspect_metadata.py'),encoding='utf-8-sig').read().split('m=load')[0])
ids=['S001-theorem-keel-mori','S001-lemma-brown-bis','S001-lemma-smash-nilpotence','S001-theorem-multiplicity-with-koszul','S001-more-groupoids-lemma-slice','S001-lemma-compare-higher','S001-lemma-openness-smoothness','S001-lemma-characteristic-p-case']
rows=[json.loads(x) for x in (P.parent/'index.jsonl').read_text(encoding='utf-8-sig').splitlines()]
for x in rows:
 if x['problem_id'] in ids:
  print('\n###',x['problem_id']);print(x['difficulty_reason']);print('REVIEWS',x['review_evidence']);print('LOCATORS',x['statement_locator'][:200],x['proof_locator'][:200])
