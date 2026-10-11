exec(open(__file__.replace('batch3_shortlist.py','inspect_metadata.py'),encoding='utf-8-sig').read().split('m=load')[0])
ids=['S001-sites-cohomology-lemma-left-dual-derived','S001-etale-cohomology-theorem-fully-faithful','S001-stacks-sheaves-proposition-QC-compare','S001-coherent-theorem-grothendieck-existence','S001-spaces-more-morphisms-theorem-grothendieck-existence','S001-spaces-more-morphisms-theorem-stein-factorization-general','S001-spaces-properties-theorem-fully-faithful','S001-lemma-resolution-property-one-sheaf']
rows=[json.loads(x) for x in (P.parent/'index.jsonl').read_text(encoding='utf-8-sig').splitlines()]
for x in rows:
 if x['problem_id'] in ids:
  print('\n###',x['problem_id'],x['source_file']);print(x['difficulty_reason'][:2200]);print('REVIEWS',x['review_evidence']);print((R/x['item_path']).read_text(encoding='utf8')[:1100])
