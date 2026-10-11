exec(open(__file__.replace('batch6_near.py','inspect_metadata.py'),encoding='utf-8-sig').read().split('m=load')[0])
keys=['kunneth','künneth','hypercover','quillen','weakly contractible','ample on','finite etale cover','constructible complex','finite-type algebraic stack']
for x in load(R/'editable-corpus/manifest.json')['items']:
 s=(x.get('title','')+' '+str(x.get('claim_key',''))).lower()
 if any(k in s for k in keys):print(x['problem_id'],x.get('title'),x.get('claim_key'))
