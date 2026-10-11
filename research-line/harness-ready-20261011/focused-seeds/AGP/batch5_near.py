exec(open(__file__.replace('batch5_near.py','inspect_metadata.py'),encoding='utf-8-sig').read().split('m=load')[0])
for x in load(R/'editable-corpus/manifest.json')['items']:
 if any(z in x.get('source_id','') for z in ['quot.tex','moduli.tex','artin.tex','spaces-pushouts.tex','algebraization.tex','stacks-more-morphisms.tex']):print(x['problem_id'],x.get('title'),x.get('primary',{}).get('tag_url'))
