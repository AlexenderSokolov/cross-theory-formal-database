import pathlib,json,sys,re
P=pathlib.Path(r'C:/Users/20600/Documents/Codex/corpus-repair-20261010/research-line/harness-ready-20261011');O=P/'focused-seeds/AGP';sys.path.insert(0,str(P.parents[1]/'corpus-work/scripts'));import prepared_delivery as d
load=lambda p:json.loads(pathlib.Path(p).read_text(encoding='utf-8-sig'));results=[]
for x in load(O/'READY_TASKS.json'):
 t=load(P/x['task_path']);revs=[load(P/r) for r in t['review_paths']];d.review_records(t,revs)
 ss=t['statement_spans']+t['proof_spans']+t['context_spans']+t['assembly']['preamble_spans']+[r['source_span'] for r in t['assembly'].get('external_references',[])]
 for s in ss:
  d.normalized_span(s);f=d.relative_path(P,s['path'],existing=True);lines=f.read_text(encoding='utf-8-sig').splitlines();assert s['end_line']<=len(lines),(t['task_id'],s)
 for key in ['asset_paths','bibliography_paths']:
  for f in t['assembly'][key]:d.relative_path(P,f,existing=True)
 for role in ['statement','proof','context']:
  assert [d.normalized_span(s) for s in t[role+'_spans']]==[d.normalized_span(s) for s in t['assembly']['body_spans'] if s['role']==role],(t['task_id'],role)
 results.append({'task_id':t['task_id'],'review_binding':'pass','source_span_bounds':'pass','referenced_files':'pass','assembly_role_binding':'pass','compile_status':'not_run','problem_id':t['problem_id']})
(O/'MATERIAL_VALIDATION.json').write_text(json.dumps({'results':results,'scope':'Review/config binding, precise span bounds, file presence and assembly role agreement only; no compilation/page QA, no hashes and no source-byte comparison.'},ensure_ascii=False,indent=2),encoding='utf8')
print('Validated',len(results))
