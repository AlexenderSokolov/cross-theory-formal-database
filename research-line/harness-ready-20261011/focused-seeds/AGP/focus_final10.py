exec(open(__file__.replace('focus_final10.py','inspect_metadata.py'),encoding='utf-8-sig').read().split('m=load')[0])
ids=['S001-lemma-algebraize-local-cohomology-general','S001-lemma-factor-hom','S001-lemma-K-injective-embedding-filtration','S001-lemma-check-flat-comparison-on-etale-covering','S001-lemma-cohomology-on-subcategory','S001-lemma-lqc-colimits','S001-lemma-curves-diagonal-separated-fp','S001-groupoids-lemma-etale','S001-lemma-find-affine-codimension-1','S001-lemma-vector-bundle-II']
for x in [json.loads(z) for z in (P.parent/'index.jsonl').read_text(encoding='utf-8-sig').splitlines()]:
 if x['problem_id'] in ids:
  print('\n###',x['problem_id'],x['source_file']);s=(R/x['item_path']).read_text(encoding='utf8');end=s.find('\\begin{proof}');print(s[:end][:2500]);print('REASON',x['difficulty_reason'][:1100]);print('REVIEWS',x['review_evidence'],'FLAGS',x['review_flags'])
