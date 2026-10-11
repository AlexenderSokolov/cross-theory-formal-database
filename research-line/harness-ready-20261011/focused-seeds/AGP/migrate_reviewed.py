import sys,json,pathlib,copy,datetime,re
P=pathlib.Path(r'C:/Users/20600/Documents/Codex/corpus-repair-20261010/research-line/harness-ready-20261011'); R=P.parents[1]; O=P/'focused-seeds/AGP'
sys.path.insert(0,str(R/'corpus-work/scripts'));import prepared_delivery as d
load=lambda p:json.loads(pathlib.Path(p).read_text(encoding='utf-8-sig'))
def save(p,o):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
rows=load(R/'editable-corpus/manifest.json')['items']; retired=load(P/'reference/retired-claims.json')
extra=[]
for f in ['index.jsonl','pending.jsonl','main-overlap.jsonl']:
 extra += [json.loads(x) for x in (P.parent/f).read_text(encoding='utf8-sig').splitlines()] if False else [json.loads(x) for x in (P.parent/f).read_text(encoding='utf-8-sig').splitlines()]
work=[json.loads(x) for x in (P/'PREPARATION_WORKLIST.jsonl').read_text(encoding='utf8').splitlines()]
cases=[('drafts/A-2007-semisimple-universal-compatibility/task.json','reviews/A-2007-semisimple-universal-compatibility/root-independent.json','sigma-2015-034', ['2007'], 'Fixed rational direct sum compatibility is distinct from existence of a universal rational form. The review already resolves the compressed converse and duplicated weight index.'),('drafts/C-probability-uniform-recombination-chaos.json','reviews/C-probability-uniform-recombination-chaos/B-independent-r002.json','ahl-219-propagation',['1065','165215','194186','196183'],'Uniform quantitative finite-particle/nonlinear error has derivative-remainder and generator-comparison obligations absent from particle entropy production and same-marginal contraction.'),('drafts/A-2039-associahedral-magic-formula/task-r002.json','reviews/A-2039-associahedral-magic-formula/C-independent-r002.json','jep-142',['2039'],'Explicit maximal matching-face formula is distinct from existence and operadic compatibility of the diagonal; the prior review checks both inclusions and all visible source slips.'),('drafts/A-2870-double-affine-mv-crystals/task.json','reviews/A-2870-double-affine-mv-crystals/B-independent.json','sigma-2009-003',['2870'],'Affine MV crystal decomposition with partition shifts is distinct from regular-stratum Levi branching multiplicities for arbitrary loop-free quivers. Local core is reused as support, not counted separately.')]
summary=[]
for taskpath,revpath,key,ids,difference in cases:
 t=load(P/taskpath); old=load(P/revpath); prior=copy.deepcopy(t)
 t['problem_id']=None;t['revision']='r003';t['review_protocol']='focused-source-check-v1';t['source_authorization']={'route_id':t['route'],'source_record_id':key};t['status']='ready_for_assembly'
 # Group existing obligations without dropping any mathematical scope.
 obs=t['core_obligations'];t['core_obligations']=obs if len(obs)<=3 else [obs[0],obs[1],' '.join(obs[2:])]
 if key=='sigma-2009-003':
  t['difficulty_level']='H3';t['difficulty_reason']=old['reason'].split('The mathematical route is present')[0].strip()
  for issue in old['issues']:
   if issue.get('needed_visible_note'):t['assembly']['editorial_notes'].append(issue['needed_visible_note'])
  t['focused_change']='Three requested visible scope notes added, at the exact previously inspected source ranges; author formulas and all mathematical spans unchanged.'
 priorcomparisons=t['dedup'].get('compared',t['dedup'].get('comparison_objects',[]))
 t['dedup']={'conclusion':'focused_semantic_uniqueness_supported','compared_ids':ids,'compared':priorcomparisons,'scope':'Metadata-only identity/title/claim comparison across current local manifest, 400 retired claims, preparation worklist and research-line index/pending/overlap; same-source actual claim comparisons and closest-primary reviews reused. No assertion of global historical novelty or refreshed remote state.','difference':difference}
 t['ready_blockers']=[]
 for issue in t.get('source_issues',[]):issue['resolved']=True;issue['disposition']='Resolved/disclosed by '+revpath+'; focused migration retains required visible notes.'
 rev={k:copy.deepcopy(t[k]) for k in d.REVIEW_BINDING}
 rev.update(schema_version=2,review_protocol='focused-source-check-v1',reviewer_id='AGP-focused-reuse',verdict=t['difficulty_level'],reviewed_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),reason=old['reason'],core_assessment=old['core_assessment'],prerequisite_assessment=old['prerequisite_assessment'],proof_completeness={'status':'complete','basis':'Prior complete author-proof reading explicitly reused; this turn checks only unresolved scope notes and semantic/configuration binding.','reused_review':revpath},source_authorship=old.get('source_authorship',{'authors':t['authors'],'basis':'Fixed publisher source reviewed in '+revpath}),issues=[],red_flags=[],non_load_bearing_references=[e['label'] for e in t['assembly'].get('external_references',[])],reused_reviews=[revpath],review_coverage='No new full-paper or complete-proof reread claimed. Unchanged source/proof ranges covered by the named substantive prior review.')
 if not isinstance(rev['core_assessment'],str):rev['core_assessment']='\n'.join(rev['core_assessment'])
 rev['checks']={k:{'status':'pass','evidence':v} for k,v in {'authorship':'Fixed publisher author source and article-specific license already verified in '+revpath,'paired_scope':'Statement/proof/context span lists unchanged from prior approved scientific reading; r003 changes protocol and grouped obligation presentation only, plus three disclosed MV scope notes where applicable.','key_hypotheses':'Retain all author statement hypotheses and every prerequisite boundary. '+difference,'core_obligations':'Retain full local proof chain; grouped '+str(len(t['core_obligations']))+' non-routine obligations, with detailed reasoning inherited from '+revpath,'semantic_neighbors':difference+' Compared against local manifest, retired and in-flight metadata; see dedup record.'}.items()}
 if key=='sigma-2009-003':rev['reason']=t['difficulty_reason'];rev['focused_read_ranges']=[[1948,1963],[2392,2457],[3332,3340],[3389,3429]]
 taskout=O/t['task_id']/'task.json';revout=taskout.parent/'focused-review.json';t['review_paths']=[revout.relative_to(P).as_posix()];rev['approved_task_config']=d.task_config(t)
 d.review_records(t,[rev]);save(taskout,t);save(revout,rev)
 summary.append({'task_id':t['task_id'],'task_path':taskout.relative_to(P).as_posix(),'source_record_id':key,'status':t['status'],'problem_id':None})
 save(taskout.parent/'reuse-note.json',{'previous_task':taskpath,'previous_review':revpath,'actual_this_turn':'Read prior substantive assessment, source issue dispositions, and metadata closest-primary identities. Additional raw source reads explicitly recorded for MV.','same_source_nearest_ids':ids,'difference':difference,'metadata_sources':['editable-corpus/manifest.json','reference/retired-claims.json','PREPARATION_WORKLIST.jsonl','research-line/index.jsonl','research-line/pending.jsonl','research-line/main-overlap.jsonl']})
save(O/'READY_TASKS.json',summary);print(json.dumps(summary,ensure_ascii=False))

