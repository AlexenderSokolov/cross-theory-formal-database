from pathlib import Path
p=Path(__file__).with_name('prepare_homotopy_continuation.py');s=p.read_text(encoding='utf-8-sig');prefix=s.split('cases=[')[0].replace("B/'homotopy.tex'","B/'hlevels.tex'");exec(prefix)
cases=[('AGP-hott-path-truncation','Path spaces of an n-plus-one truncation are n-truncated path spaces','thm:path-truncation',[(671,674)],[(676,722)],[(658,670)],['Define a two-variable code family on the truncated type using the truncated universe.','Construct encode/decode and verify both inverse homotopies by truncation and path induction.'],'The proof must generalize endpoints before it can use identity induction, and control truncation levels of the code universe and inverse homotopies. This supplies H2 synthetic homotopy material.','This is the general path-space/truncation comparison. Circle path spaces have a different integer code, and the long exact sequence uses this identity as background without proving or separately counting it.')]
tail='for tid,title,claim,st,pr,ctx,obs,reason,diff in cases:'+s.split('for tid,title,claim,st,pr,ctx,obs,reason,diff in cases:')[1];exec(tail)
# Supply the original layout macros and keep role lists in assembly order.
f=O/'AGP-hott-path-truncation/task.json';t=json.loads(f.read_text(encoding='utf-8-sig'));t['assembly']['preamble_spans']=json.loads((O/'AGP-hott-circle-pathspace/task.json').read_text(encoding='utf-8-sig'))['assembly']['preamble_spans'];t['research_record_reuse']={'research_id':'S046-thm:path-truncation','basis':'Existing unpublished book result migrated once; original source proof preserved.'}
for r in ['statement','proof','context']:t[r+'_spans']=[{k:v for k,v in x.items() if k!='role'} for x in t['assembly']['body_spans'] if x['role']==r]
f.write_text(json.dumps(t,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for tag,route in [('0334','algebra'),('0BML','algebra'),('02HT','algebra'),('0C7C','combinatorics')]:
 f=O/('AGP-stacks-'+tag)/'task.json';t=json.loads(f.read_text(encoding='utf-8-sig'));t['route']=route
 if tag=='0C7C':
  for x in t['proof_spans']+t['assembly']['body_spans']:
   if x['start_line']==683:x['start_line']=682
 f.write_text(json.dumps(t,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
