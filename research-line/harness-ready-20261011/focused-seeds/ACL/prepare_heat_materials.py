import json,pathlib,copy
p=pathlib.Path(r'C:/Users/20600/Documents/Codex/corpus-repair-20261010/research-line/harness-ready-20261011')
base=json.loads((p/'focused-seeds/ACL/ACL-analysis-heat-shape-exact-obstruction/task.json').read_text(encoding='utf-8-sig'))
src='focused-seeds/ACL/sources/heat-shape-desensitizing-jep209/source0.tex'
def sp(a,b,label,role=None):
 d=dict(path=src,start_line=a,end_line=b,label=label)
 if role:d['role']=role
 return d
cases=[
('disjoint-boundary-controllability','Independent boundary trace controllability for a disjoint heat cascade','Prop-Approx-Cont-Case1',(330,360),(616,725),[(311,326)],'Use unique continuation outside the observation set and weak boundary trace duality to annihilate the first boundary datum, then an energy identity to propagate vanishing through the second component. The disjoint coupling and observation geometry rules out the immediate local coupling argument.','Public 2109 is finite-dimensional nonlinear shape desensitization (Thm-Case1-Exact-FD); this independently controls arbitrary pairs of boundary fluxes and retains the original unique-continuation argument. It is not the direct zero-flux desensitization corollary.'),
('intersecting-null-boundary-control','Simultaneous null control and approximate boundary traces for an intersecting heat cascade','Prop-Approx-Cont-Case2',(414,460),(1189,1459),[(311,315),(403,409),(330,360),(616,725),(462,481)],'Construct the completed observability space and a coercive strictly convex dual functional; establish coercivity by normalized weak limits and unique continuation. This enforces terminal null control together with independently prescribed boundary traces, beyond approximate density alone.','Disjoint boundary trace control cannot prescribe an exact terminal state. Public 2109 controls a nonlinear finite-dimensional shape derivative in a disjoint geometry; neither that target nor the prior obstruction is this mixed exact/approximate controllability theorem.'),
('boundary-collar-exact-desensitization','Exact heat-shape desensitization when the control contains the observation boundary','Thm-insensitizing-Boundary',(554,562),(1589,1653),[],'Design nested cutoffs in the coupled forward/backward equations and their commutator corrections so that the adjoint vanishes outside the observation region while the resulting control remains supported in the boundary collar. This is a constructive PDE localization argument, not a direct implication of approximate controllability.','Public 2109 is finite-dimensional exactness plus global approximation in disjoint geometry. The present target is all-direction exactness in a boundary-collar geometry, obtained by a separate cutoff/commutator construction; the interior-observation easy case is not counted.')]
for slug,title,label,statement,proof,extra,reason,neighbor in cases:
 t={k:copy.deepcopy(base[k]) for k in ['schema_version','source_id','source_version','authors','source_url','license']}
 t.update(task_id='ACL-analysis-heat-'+slug,problem_id=None,revision='r001',selected_by='ACL-material-production',route='analysis',claim_key='doi:10.5802/jep.209:'+label,title=title,status='ready_for_assembly',difficulty_level='H2',difficulty_reason=reason)
 t['statement_spans']=[sp(*statement,label)]
 t['proof_spans']=[sp(*proof,'complete author proof')]
 t['context_spans']=copy.deepcopy(base['context_spans'][:4])+[sp(a,b,'original framework and supplied support') for a,b in extra]
 t['standard_prerequisites']=[dict(name='Classical heat equation and functional analysis',statement='Weak and transposition solutions, Sobolev trace maps and parabolic regularity, Holmgren unique continuation, Hilbert-space range/kernel duality, standard heat observability and convex minimization. The displayed Hadamard derivative formula is a standard supplied input. Target-specific constructions remain in the original proof.')]
 t['core_obligations']=[reason]
 t['dedup']=dict(conclusion='focused_semantic_uniqueness_supported',compared=[dict(problem_id='2109',difference=neighbor)],scope='Compared same-source public manifest item, existing heat obstruction card and the three new heat targets; no direct desensitization corollaries counted.')
 t['assembly']=copy.deepcopy(base['assembly']); t['assembly']['body_spans']=[]
 spans=t['context_spans']+t['statement_spans']+t['proof_spans']
 for s in sorted(spans,key=lambda x:x['start_line']):
  q=copy.deepcopy(s);q['role']='statement' if s in t['statement_spans'] else 'proof' if s in t['proof_spans'] else 'context';t['assembly']['body_spans'].append(q)
 t['assembly']['external_references']=[]
 t['assembly']['editorial_notes']=['Original author statement and full paired proof retained; source license and version reused. No mathematical modifications or added assumptions.',neighbor]
 d=p/'focused-seeds/ACL'/t['task_id'];d.mkdir(exist_ok=True)
 (d/'task.json').write_text(json.dumps(t,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(t['task_id'])