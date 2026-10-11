exec(open(__file__.replace('new7_neighbors.py','inspect_metadata.py'),encoding='utf-8-sig').read().split('m=load')[0])
keys=['periodic','canonical-class-obstruction','annihilat','siblings','quasi-projectiv','scheme integral','Chow','Deligne','DM residual']
rows=load(R/'editable-corpus/manifest.json')['items']
for x in rows:
 st=' '.join(str(x.get(k,'')) for k in ['title','claim_key']).lower()
 if any(k.lower() in st for k in keys):
  if len(st)<1500:print(x['problem_id'],x.get('title'),x.get('claim_key'))
