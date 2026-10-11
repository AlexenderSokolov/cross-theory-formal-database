import pathlib,json
P=pathlib.Path(r'C:/Users/20600/Documents/Codex/corpus-repair-20261010/research-line/harness-ready-20261011');O=P/'focused-seeds/AGP';load=lambda p:json.loads(pathlib.Path(p).read_text(encoding='utf-8-sig'))
def save(p,x):pathlib.Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
e=load(O/'sources/stacks-snapshot-20261011/LICENSE_OBSERVATION.json');e['status']='supported';e['source_family']='Stacks Project';save(O/'sources/stacks-snapshot-20261011/LICENSE_OBSERVATION.json',e)
ready=load(O/'READY_TASKS.json');rs=load(O/'SOURCE_RECORDS.json')
for row in ready:
 t=load(P/row['task_path']);row['problem_id']=t['problem_id']
 rec=next(r for r in rs if r['source_record_id']==t['source_authorization']['source_record_id']);rec['allowed_files']=list(dict.fromkeys(t['assembly']['asset_paths']+t['assembly']['bibliography_paths']+[t['license']['evidence_path']]))
 ss=t['statement_spans']+t['proof_spans']+t['context_spans']+t['assembly']['preamble_spans']+[x['source_span'] for x in t['assembly'].get('external_references',[])]
 # Authorize actual selected spans, not the entire cached chapter.
 merged={}
 for s in ss:merged.setdefault(s['path'],[]).append((s['start_line'],s['end_line']))
 allowed=[]
 for path,intervals in merged.items():
  reduced=[]
  for a,b in sorted(intervals):
   if reduced and a<=reduced[-1][1]+1:reduced[-1][1]=max(reduced[-1][1],b)
   else:reduced.append([a,b])
  allowed += [dict(path=path,start_line=a,end_line=b) for a,b in reduced]
 rec['allowed_scope']=allowed
save(O/'READY_TASKS.json',ready);save(O/'SOURCE_RECORDS.json',rs)
source=load(O/'sources/stacks-snapshot-20261011/SOURCE_RECORD.json');source['copied_chapters']=sorted({p.name for p in (O/'sources/stacks-snapshot-20261011').glob('*.tex') if p.name not in ['preamble.tex','wrapper.tex']});source['selected_tags']=[load(P/x['task_path'])['claim_key'].split(':')[-1] for x in ready if x['task_id'].startswith('AGP-stacks')];save(O/'sources/stacks-snapshot-20261011/SOURCE_RECORD.json',source)
holds=[{'research_id':'S001-lemma-characteristic-p-case','status':'needs_targeted_source_resolution','source_file':'D:/tmp/r2work/repo/more-algebra.tex','statement_lines':[34817,34830],'proof_lines':[34832,34974],'counted':False,'reason':'The author statement requires a finite Galois totally ramified K_1/K. The final nonempty-J branch constructs only a separable totally ramified p-power extension at34926–34930 and ends at34974 without establishing Galoisness. Taking a Galois closure does not automatically preserve total ramification. This is a specific unresolved proof-to-hypothesis issue, not a counterexample or a verdict against the entire Epp theorem.','additional_source_slips':'The first Artin–Schreier telescoping substitution has a sign inconsistency for odd p; the original J definition uses lambda_i in place of lambda_j. No new proof or repaired statement is entered.'},{'task_id':'A-1912-parity-perverse-tilting','status':'needs_targeted_source_resolution','counted':False,'reason':'Still requires article-page/transcription and rank-one parity input scope check; no new generic full-paper review scheduled.'}]
save(O/'HOLDS_AND_PENDING.json',holds)
print('Ready',len(ready),'source records',len(rs),'pending',len(holds))
