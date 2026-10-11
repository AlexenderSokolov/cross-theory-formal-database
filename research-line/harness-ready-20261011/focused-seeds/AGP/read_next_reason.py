exec(open(__file__.replace('read_next_reason.py','inspect_metadata.py'),encoding='utf-8-sig').read().split('m=load')[0])
ids=['S001-spaces-pushouts-lemma-two-compactifications','S001-proposition-tate-map','S001-lemma-Garel-upstairs']
rows=[json.loads(x) for x in (P.parent/'index.jsonl').read_text(encoding='utf-8-sig').splitlines()]
for x in rows:
 if x['problem_id'] in ids: print('\n###',x['problem_id']);print(x['difficulty_reason'])
