exec(open(__file__.replace('source_records.py','inspect_metadata.py'),encoding='utf-8-sig').read().split('m=load')[0])
O=P/'focused-seeds/AGP'; out=[]
for row in load(O/'READY_TASKS.json'):
 t=load(P/row['task_path']); spans=t['statement_spans']+t['proof_spans']+t['context_spans']+t['assembly']['preamble_spans']+[x['source_span'] for x in t['assembly'].get('external_references',[])]
 merged={}
 for s in spans:
  k=s['path'];a,b=merged.get(k,(s['start_line'],s['end_line']));merged[k]=(min(a,s['start_line']),max(b,s['end_line']))
 out.append(dict(source_record_id=row['source_record_id'],route_id=t['route'],source_id=t['source_id'],source_version=t['source_version'],source_url=t['source_url'],license=t['license'],allowed_scope=[dict(path=k,start_line=a,end_line=b) for k,(a,b) in merged.items()],exclusions=[],counting_exclusions=t['dedup']['compared_ids'],prerequisite_boundary=t['standard_prerequisites'],native_assets=t['assembly']['asset_paths'],bibliography_paths=t['assembly']['bibliography_paths'],scope_note='Authorization envelope for these reused proof tasks; not a statement that every line between endpoints is a separately reviewed or countable claim.'))
(O/'SOURCE_RECORDS.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');print(len(out))
