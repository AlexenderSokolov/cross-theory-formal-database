"""Root-authorized LOCAL975→1002 policy adapter; never a validation gate.
The original evidence_ledger.py and its obsolete 500-boundary rule remain intact.
This explicitly permits exact historical item-check retention at the true milestone
only with fresh27 actual calls, a fresh full1002 aggregate, complete unchanged
material/build/runtime and INDEX/SQL projections, and a cleared local base.
Remote publication still requires the verified actual975 commit and root lock.
"""
import hashlib,json,re

def canonical(v):return json.dumps(v,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()
def digest(b):return hashlib.sha256(b).hexdigest()
def unique(pairs):
 out={}
 for k,v in pairs:
  if k in out:raise ValueError('duplicate JSON key')
  out[k]=v
 return out

def success(raw,ids,total=None):
 try:r=json.loads(raw,object_pairs_hook=unique)
 except (ValueError,UnicodeError,TypeError):return False
 return (isinstance(r,dict) and r.get('mode')=='editable-delivery' and r.get('errors')==[] and type(r.get('editable_qualified_count')) is int and r['editable_qualified_count']==len(ids) and (total is None or r.get('package_item_count')==total) and isinstance(r.get('items'),dict) and set(r['items'])==set(ids) and all(isinstance(x,dict) and x.get('status')=='qualified_editable' and x.get('errors')==[] for x in r['items'].values()))

def decide(current,prior,prior_report_bytes,prior_projection,current_projection,session):
 def refuse(reason):return {'action':'fresh_required','reason':reason,'fresh_cli_execution':False}
 try:
  old=session['base_ids'];new=session['new_ids'];anchor=session['anchor'];item=prior['item_id']
  if (session['prior_count'],session['current_count'])!=(975,1002) or len(old)!=975 or len(new)!=27 or set(old)&set(new):return refuse('real975→1002 counts or exact ID partition invalid')
  if anchor.get('kind')!='root_authorized_qualified_local_base_pending_remote_commit' or anchor.get('count')!=975 or not anchor.get('qualified_receipt_pinned') or anchor.get('sanitized_export_scope_cleared') is not True or not re.fullmatch('[0-9a-f]{40}',anchor.get('expected_tree','')):return refuse('qualified sanitized local975 base anchor missing or superseded')
  if set(anchor.get('reports',{}))!=set(old) or item not in old or anchor.get('reports',{}).get(item)!=prior.get('report_sha256'):return refuse('historical report absent from exact base execution anchor')
  if not prior_report_bytes or digest(prior_report_bytes)!=prior.get('report_sha256') or not success(prior_report_bytes,{item}):return refuse('missing/tampered/unsuccessful prior actual individual report')
  past=prior.get('identity',{})
  if current.get('identity_sha256')!=digest(canonical(current.get('content'))) or past.get('identity_sha256')!=digest(canonical(past.get('content'))):return refuse('material identity malformed')
  if current.get('identity_sha256')!=past.get('identity_sha256') or current.get('content')!=past.get('content'):return refuse('material/build/row/evidence/runtime identity changed')
  if current_projection!=prior_projection:return refuse('selected INDEX/SQLite/full-text projection changed')
  calls=session.get('fresh_new_reports',{})
  if set(calls)!=set(new) or any(x.get('exit_code')!=0 or not success(x.get('report_bytes'),{i},1002) for i,x in calls.items()):return refuse('missing/failed fresh actual27 individual calls')
  agg=session.get('aggregate',{})
  if agg.get('exit_code')!=0 or not success(agg.get('report_bytes'),set(old)|set(new),1002):return refuse('missing/failed fresh whole1002 aggregate')
 except (KeyError,TypeError,ValueError,AttributeError):return refuse('malformed required exact-retention evidence')
 return {'action':'retain_historical_local_item_checks','reason':'Root explicit milestone policy; exact historical975 selected identities/projections with fresh actual27 and freshfull1002 aggregate','prior_count':975,'current_count':1002,'fresh_new_item_count':27,'fresh_cli_execution':False,'fresh_full_aggregate_count':1002,'publication_requires_verified_base_commit':True,'scope':'Retained historical item-material/source/build/runtime checks only; this is local preparation, not fresh975 execution or remote publication.'}
