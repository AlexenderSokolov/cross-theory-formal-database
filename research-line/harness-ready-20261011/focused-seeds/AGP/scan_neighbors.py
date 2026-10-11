exec(open(__file__.replace('scan_neighbors.py','inspect_metadata.py'),encoding='utf-8-sig').read().split('m=load')[0])
sets={'manifest':load(R/'editable-corpus/manifest.json')['items'],'public': [json.loads(x) for x in (P/'reference/public-items.jsonl').read_text(encoding='utf8').splitlines()], 'retired':load(P/'reference/retired-claims.json')}
for name,rows in sets.items():
 for x in rows:
  text=json.dumps({k:v for k,v in x.items() if k in ['title','source_id','claim_key','source','source_title']}).lower()
  if any(k in text for k in ['2015.034','ahl.219','real-universal','real universal','recombination','jep.142','2009.003']):
   print(name,json.dumps({k:v for k,v in x.items() if k in ['problem_id','title','source_id','claim_key','primary','source','status']},ensure_ascii=False))
