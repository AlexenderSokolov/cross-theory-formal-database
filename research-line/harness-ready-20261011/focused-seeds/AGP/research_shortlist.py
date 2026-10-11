exec(open(__file__.replace('research_shortlist.py','inspect_metadata.py'),encoding='utf-8-sig').read().split('m=load')[0])
rows=[json.loads(x) for x in (P.parent/'index.jsonl').read_text(encoding='utf-8-sig').splitlines()]
o=[json.loads(x) for x in (P.parent/'main-overlap.jsonl').read_text(encoding='utf-8-sig').splitlines()];print('overlap shape',list(o[0]))
exclude={x.get('research_problem_id',x.get('research_id')) for x in o}
for x in rows:
 if x['problem_id'] not in exclude:print(x['problem_id'], x['source_file'], x.get('primary_label'),len(x.get('review_evidence',[])))
