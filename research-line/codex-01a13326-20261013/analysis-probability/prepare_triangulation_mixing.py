from pathlib import Path
import json,sys,os
R=Path('/disks/sata1/yupeng/human-proof-corpus/operations/codex-work-01a13326');P=R/'research-line/codex-01a13326-20261013';lane=P/'analysis-probability'
sys.path.insert(0,str(lane));import convert_drops_html as c
sys.path.insert(0,str(R/'corpus-work/scripts'));import prepared_delivery as delivery
os.environ['PATH']='/disks/sata1/yupeng/human-proof-corpus/runtime/texlive/2025/bin/x86_64-linux:'+os.environ['PATH']
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
specs=[
(12,'triangulation-flip-chain-functional-inequalities','S1.Thmtheorem1','Near-quadratic relaxation and log-Sobolev times for triangulation flip chains','H3','The authors develop transport-flow estimates controlling average and maximum congestion, analyze the triangulation/binary-tree rotation decomposition and Catalan tree heights, and prove near-quadratic inverse spectral gap and log-Sobolev constant. Complete full-version proofs, average-congestion analysis and appendices are retained; the mixing-time corollary is not a separate collected claim.')]


if len(sys.argv)>1:specs=[x for x in specs if x[1] in sys.argv[1:]]
for n,suffix,claim,title,level,reason in specs:
 existing=lane/'drafts'/('CP01A13326-AP-'+suffix)/'task.json'
 if existing.exists():
  print('Existing canonical revision preserved:',existing,flush=True)
  continue
 d=lane/'sources'/'arxiv2605-02067v2';source=d/'official-source.tex'
 parser=c.Parser();parser.feed((lane/'sources/icalp2026-12/published.html').read_text())
 meta=list(c.nodes(parser.root,'meta'))
 authors=[]
 for x in meta:
  if x.a.get('name')=='DC.Creator.PersonalName':
   parts=x.a['content'].split(', ',1);authors.append(' '.join(parts[::-1]))
 assert any(x.a.get('name')=='DC.Rights' and x.a.get('content')=='https://creativecommons.org/licenses/by/4.0/legalcode' for x in meta)
 sid='arxiv:2605.02067v2';url='https://arxiv.org/abs/2605.02067v2'
 save(d/'rights-facts.json',{'name':'CC BY 4.0','evidence':'arXiv version metadata metadata.html abs-license links http://creativecommons.org/licenses/by/4.0/; original full HTML retained at ../icalp2026-12/full-version.html','source_url':url,'original_paths':['published.html','published.pdf'],'conversion':'Full-version arXiv LaTeXML prose and math alttext, complete author sections and appendices retained. Original unmodified arXiv HTML is preserved; rendering copy adds only an HTML base URL.'})
 preamble=r'''\documentclass[10pt,a4paper]{article}
\usepackage{fontspec,amsmath,amssymb,amsthm,mathtools,graphicx,bm,bbm,stmaryrd,nicefrac,mathrsfs,braket}
\usepackage[margin=22mm]{geometry}
\usepackage[bookmarks=false]{hyperref}
\setlength{\emergencystretch}{3em}\DeclareMathOperator{\E}{\mathbb{E}}\DeclareMathOperator{\Gap}{\mathtt{gap}}\DeclareMathOperator{\MLS}{\mathtt{mls}}\DeclareMathOperator{\EC}{\mathtt{ec}}\DeclareMathOperator{\LS}{\mathtt{ls}}
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
 note='Editable TeX converted from the CC BY arXiv v2 full HTML prose and math alttext. Original full-version HTML/PDF and license metadata retained; all appendix proofs included. Only the specified claim counts; all author context and available source-local supporting proofs are included.'
 if n==3:note+=' Theorems 5, 6, 7 and quantum-input extensions whose proofs are deferred to a full version are retained only as author context and are not collected proof claims.'
 if n==19:note+=' The conference article includes a complete proof of Theorem 3.1. Introductory product-sample complexity assertions whose proofs are deferred to the full version are retained as author context and are not separate collected proof claims.'
 task={'schema_version':2,'selected_by':'Codex analysis-probability material worker','task_id':'CP01A13326-AP-'+suffix,'problem_id':None,'revision':'r001','source_id':sid,'source_version':'arXiv 2605.02067v2 full version 2026-04-28; CC BY 4.0 metadata retrieved 2026-10-13','claim_key':sid+':'+claim,'title':title,'authors':authors,'route':'Markov-chain mixing and transport flows','source_url':url,'license':{'name':'CC BY 4.0','evidence_path':str((d/'rights-facts.json').relative_to(P)),'version_url':url},'statement_spans':statement,'proof_spans':proof,'context_spans':[],'standard_prerequisites':[],'core_obligations':[reason],'proof_roadmap':[],'difficulty_level':level,'difficulty_reason':reason,'dedup':{'status':'focused_semantic_uniqueness_supported','scope':'Refreshed all active operations projects using both lane/task and lane/drafts/task layouts, plus DOI/source-title and claim comparisons. No ICALP2026.12, arXiv2605.02067 or matching source title was found. Only main functional-inequality theorem counts; its spectral and log-Sobolev parts remain a single author theorem, with mixing-time Corollary1.2 not separately counted.','compared':['CP01A13326-AP-parity-product-distribution-direct-sum'] if n==19 else []},'review_paths':[],'assembly':{'preamble_spans':[{'path':str((d/'official-preamble.tex').relative_to(P)),'start_line':1,'end_line':5,'label':'Official HTML math-alttext wrapper'}],'body_spans':[dict(proof[0],role='proof'),dict(statement[0],role='statement'),dict(proof[1],role='proof')],'asset_paths':[{'path':str((d/'published.pdf').relative_to(P)),'target':'items/original-'+d.name+'.pdf'},{'path':str((d/'published.html').relative_to(P)),'target':'items/original-'+d.name+'.html'}],'bibliography_paths':[],'engine':'xelatex','allow_shell_escape':False,'bibliography_backend':'none','bibliography_style':'plainnat','editorial_notes':[note]},'status':'ready_for_assembly','ready_blockers':[]}
 ledger=d/'svg-asset-ledger.json'
 if ledger.exists():
  records=json.loads(ledger.read_text())['objects']
  for i,x in enumerate(records,1):
   task['assembly']['asset_paths'].extend([{'path':x['svg_path'],'target':'items/'+d.name+'-original-svg-'+str(i).zfill(2)+'.svg'},{'path':x['pdf_path'],'target':x['target']}])
  task['assembly']['asset_paths'].append({'path':str(ledger.relative_to(P)),'target':'items/'+d.name+'-svg-asset-ledger.json'})
 image_ledger=d/'html-image-ledger.json'
 if image_ledger.exists():
  image_records=json.loads(image_ledger.read_text())['images']
  task['assembly']['asset_paths'].extend({'path':x['image_path'],'target':x['target']} for x in image_records)
  task['assembly']['asset_paths'].append({'path':str(image_ledger.relative_to(P)),'target':'items/'+d.name+'-html-image-ledger.json'})
 task['assembly']['asset_paths'].extend([{'path':str((d/'metadata.html').relative_to(P)),'target':'items/original-arxiv2605-02067v2-metadata.html'},{'path':str((lane/'sources/icalp2026-12/full-version.html').relative_to(P)),'target':'items/original-arxiv2605-02067v2-unmodified.html'}])
 td=lane/'drafts'/task['task_id'];td.mkdir(exist_ok=True);tf=td/'task.json';save(tf,task)
 originals=json.loads((lane/'ORIGINAL_SOURCES.json').read_text())
 if not any(x['source_id']==sid for x in originals):
  originals.append({'source_id':sid,'paths':[str((d/'published.html').relative_to(P)),str((d/'published.pdf').relative_to(P))]});save(lane/'ORIGINAL_SOURCES.json',originals)
 if ledger.exists():
  record=next(x for x in originals if x['source_id']==sid)
  for x in records:
   if x['svg_path'] not in record['paths']:record['paths'].append(x['svg_path'])
  save(lane/'ORIGINAL_SOURCES.json',originals)
 if image_ledger.exists():
  record=next(x for x in originals if x['source_id']==sid)
  for x in image_records:
   if x['image_path'] not in record['paths']:record['paths'].append(x['image_path'])
  save(lane/'ORIGINAL_SOURCES.json',originals)
 print('ASSEMBLING',task['task_id'],flush=True)
 try:print(json.dumps(delivery.assemble(tf,P,lane/'jobs',material_only=True)),flush=True)
 except Exception as error:print('ASSEMBLY_ERROR',task['task_id'],str(error),flush=True)

