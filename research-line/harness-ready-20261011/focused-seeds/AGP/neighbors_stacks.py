exec(open(__file__.replace('neighbors_stacks.py','inspect_metadata.py'),encoding='utf-8-sig').read().split('m=load')[0])
rows=load(R/'editable-corpus/manifest.json')['items']
for x in rows:
 s=x.get('source_id','');title=x.get('title','');
 if any(z in s for z in ['intersection.tex','weil.tex','more-groupoids.tex','cotangent.tex','artin.tex','examples.tex']):print(x['problem_id'],title,str(x.get('primary',{}))[:210])
