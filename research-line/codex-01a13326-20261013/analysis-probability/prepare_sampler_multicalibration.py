from pathlib import Path
import json,sys,os
R=Path('/disks/sata1/yupeng/human-proof-corpus/operations/codex-work-01a13326');P=R/'research-line/codex-01a13326-20261013';lane=P/'analysis-probability'
sys.path.insert(0,str(lane));import convert_drops_html as c
sys.path.insert(0,str(R/'corpus-work/scripts'));import prepared_delivery as delivery
os.environ['PATH']='/disks/sata1/yupeng/human-proof-corpus/runtime/texlive/2025/bin/x86_64-linux:'+os.environ['PATH']
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
specs=[
(6,'near-optimal-strong-averaging-sampler','Thmmtheorem1','Near-optimal randomness-efficient strong averaging samplers','H3','The author construction combines a small-domain reduction, strong sampler composition and almost-wise independence to achieve near-optimal sample complexity while retaining an additive logarithmic seed term. The complete reduction lemma, parameterized construction and appendix moment argument are retained.'),
(6,'near-optimal-matrix-sampler','Thmmtheorem3','Near-optimal matrix samplers using composition and matrix moment bounds','H3','The construction controls spectral-norm deviation for matrix-valued functions using noncommutative moment bounds, matrix sampler composition and subsampling. The full scalar support and matrix-specific Hermitian reduction and moment proofs are retained. It is distinct from the scalar strong-averaging sampler result.'),
(19,'multicalibrated-distribution-partition','S3.Thmtheorem1','Multicalibrated partitions with indistinguishable conditional distribution surrogates','H2','The author proof constructs paired distribution surrogates from a multicalibrated partition and transfers indistinguishability through conditional mixtures while preserving partition probabilities and explicit oracle-circuit complexity. The complete Section 3 argument and its definitions are retained; the standard cited multicalibration theorem remains a prerequisite.')]
for n,suffix,claim,title,level,reason in specs:
 d=lane/'sources'/('ccc2025-'+str(n));source=d/'official-source.tex'
 parser=c.Parser();parser.feed((d/'published.html').read_text())
 meta=list(c.nodes(parser.root,'meta'))
 authors=[]
 for x in meta:
  if x.a.get('name')=='DC.Creator.PersonalName':
   parts=x.a['content'].split(', ',1);authors.append(' '.join(parts[::-1]))
 assert any(x.a.get('name')=='DC.Rights' and x.a.get('content')=='https://creativecommons.org/licenses/by/4.0/legalcode' for x in meta)
 sid='doi:10.4230/LIPIcs.CCC.2025.'+str(n);url='https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.CCC.2025.'+str(n)
 save(d/'rights-facts.json',{'name':'CC BY 4.0','evidence':'Official HTML DC.Rights specifies https://creativecommons.org/licenses/by/4.0/legalcode','source_url':url,'original_paths':['published.html','published.pdf'],'conversion':'Official LaTeXML prose and math alttext, all author sections and appendices retained; native SVG object boundary explicitly checked.'})
 preamble=r'''\documentclass[10pt,a4paper]{article}
\usepackage{fontspec,amsmath,amssymb,amsthm,mathtools,graphicx,bm,bbm,stmaryrd}
\usepackage[margin=22mm]{geometry}
\usepackage[bookmarks=false]{hyperref}
\setlength{\emergencystretch}{3em}
'''
 (d/'official-preamble.tex').write_text(preamble)
 lines=source.read_text().splitlines()
 starts=[i+1 for i,l in enumerate(lines) if l=='% SOURCE-ID '+claim]
 assert starts
 start=starts[0];end=next(i+1 for i,l in enumerate(lines) if i+1>=start and l=='% END-SOURCE-ID '+claim)
 path=str(source.relative_to(P))
 def span(a,b,label):return {'path':path,'start_line':a,'end_line':b,'label':label}
 statement=[span(start,end,claim)]
 proof=[span(1,start-1,'Complete author preliminaries and supporting definitions'),span(end+1,len(lines),'Complete remaining author arguments, supporting lemmas, bibliography and appendices')]
 note='Editable TeX converted from the official CC BY HTML prose and math alttext. Original official PDF/HTML retained. Only the specified claim counts; all author context and available source-local supporting proofs are included.'
 if n==19:note+=' The conference article includes a complete proof of Theorem 3.1. Introductory product-sample complexity assertions whose proofs are deferred to the full version are retained as author context and are not separate collected proof claims.'
 task={'schema_version':2,'selected_by':'Codex analysis-probability material worker','task_id':'CP01A13326-AP-'+suffix,'problem_id':None,'revision':'r001','source_id':sid,'source_version':'CCC2025.'+str(n)+' official CC BY HTML/PDF publication retrieved 2026-10-13','claim_key':sid+':'+claim,'title':title,'authors':authors,'route':'probabilistic constructions and pseudorandomness','source_url':url,'license':{'name':'CC BY 4.0','evidence_path':str((d/'rights-facts.json').relative_to(P)),'version_url':url},'statement_spans':statement,'proof_spans':proof,'context_spans':[],'standard_prerequisites':[{'name':'Standard finite probability and the cited sampler/extractor or multicalibration results','use':'Definitions and all source-local support proofs are retained; cited established results are used as the authors state.'}],'core_obligations':[reason],'proof_roadmap':[],'difficulty_level':level,'difficulty_reason':reason,'dedup':{'status':'focused_semantic_uniqueness_supported','scope':'Targeted current and parallel operations task/source/title inspection found no matching collected source/claim. Scalar and matrix sampler constructions have different target function classes and core proof machinery. The multicalibrated surrogate theorem is separate from parity decision-tree direct sums.','compared':['CP01A13326-AP-parity-product-distribution-direct-sum'] if n==19 else []},'review_paths':[],'assembly':{'preamble_spans':[{'path':str((d/'official-preamble.tex').relative_to(P)),'start_line':1,'end_line':5,'label':'Official HTML math-alttext wrapper'}],'body_spans':[dict(proof[0],role='proof'),dict(statement[0],role='statement'),dict(proof[1],role='proof')],'asset_paths':[{'path':str((d/'published.pdf').relative_to(P)),'target':'items/original-'+d.name+'.pdf'},{'path':str((d/'published.html').relative_to(P)),'target':'items/original-'+d.name+'.html'}],'bibliography_paths':[],'engine':'xelatex','allow_shell_escape':False,'bibliography_backend':'none','bibliography_style':'plainnat','editorial_notes':[note]},'status':'ready_for_assembly','ready_blockers':[]}
 td=lane/'drafts'/task['task_id'];td.mkdir(exist_ok=True);tf=td/'task.json';save(tf,task)
 originals=json.loads((lane/'ORIGINAL_SOURCES.json').read_text())
 if not any(x['source_id']==sid for x in originals):
  originals.append({'source_id':sid,'paths':[str((d/'published.html').relative_to(P)),str((d/'published.pdf').relative_to(P))]});save(lane/'ORIGINAL_SOURCES.json',originals)
 print('ASSEMBLING',task['task_id'],flush=True)
 try:print(json.dumps(delivery.assemble(tf,P,lane/'jobs',material_only=True)),flush=True)
 except Exception as error:print('ASSEMBLY_ERROR',task['task_id'],str(error),flush=True)

