exec(open(__file__.replace('next_candidates.py','inspect_metadata.py'),encoding='utf-8-sig').read().split('m=load')[0])
ids=['S001-lemma-algebraization-principal-bis','S001-lemma-algebraize-local-cohomology-general','S001-lemma-blowup','S001-lemma-cd-1-canonical','S001-lemma-resolve-general','S001-theorem-normalized-base-change-with-reduced-fibre','S001-lemma-finite-etale-on-proper-over-henselian-pair']
rows=[json.loads(x) for x in (P.parent/'index.jsonl').read_text(encoding='utf-8-sig').splitlines()]
for x in rows:
 if x['problem_id'] in ids:
  print('\n###',x['problem_id'],x['source_file']);print(x['difficulty_reason'][:2200]);print('REVIEWS',x['review_evidence'])
