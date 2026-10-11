exec(open(__file__.replace('focus_next8.py','inspect_metadata.py'),encoding='utf-8-sig').read().split('m=load')[0])
ids=['S001-theorem-quillen-spectral-sequence','S001-lemma-kunneth-single-sheaf','S001-spaces-over-fields-lemma-numerical-polynomial-from-euler','S001-spaces-divisors-lemma-ample-on-fibre','S001-stacks-limits-lemma-finite-type-closed-in-finite-presentation','S001-stacks-sheaves-proposition-QC-compare','S001-theorem-cohomology-hypercoverings','S001-lemma-hypercovering-descent-bounded-abelian','S001-lemma-local-structure-constructible-complex','S001-lemma-finite-etale-on-proper-over-henselian-pair']
rows=[json.loads(x) for x in (P.parent/'index.jsonl').read_text(encoding='utf-8-sig').splitlines()]
for x in rows:
 if x['problem_id'] in ids:
  print('\n###',x['problem_id'],x['source_file']);s=(R/x['item_path']).read_text(encoding='utf8');end=s.find('\\begin{proof}');print(s[:end][:2100]);print('REASON',x['difficulty_reason'][:1700]);print('REVIEWS',x['review_evidence'],'FLAGS',x['review_flags'])
