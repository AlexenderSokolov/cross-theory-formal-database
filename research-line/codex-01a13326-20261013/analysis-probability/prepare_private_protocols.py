from pathlib import Path
import json,sys,os
R=Path('/disks/sata1/yupeng/human-proof-corpus/operations/codex-work-01a13326');P=R/'research-line/codex-01a13326-20261013';lane=P/'analysis-probability'
sys.path.insert(0,str(lane));import convert_drops_html as c
sys.path.insert(0,str(R/'corpus-work/scripts'));import prepared_delivery as delivery
os.environ['PATH']='/disks/sata1/yupeng/human-proof-corpus/runtime/texlive/2025/bin/x86_64-linux:'+os.environ['PATH']
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
specs=[
(79,'two-bit-private-helper-circuit-protocol','S1.Thmtheorem1','Exactly two random bits suffice for perfectly one-private helper-party computation','H3','The authors construct masked XOR and AND gadgets, compose them using a two-bit shared seed while proving full one-party simulation, and prove the matching randomness lower bound for AND. Complete helper model, gadgets and source-local simulation arguments are retained.'),
(79,'five-bit-private-and-no-helpers','S1.Thmtheorem3','A five-bit seed for perfectly one-private multiparty AND without helpers','H3','The authors replace helper parties by overlapping input-party roles using a cyclic sliding-window independence generator, construct the full AND protocol and prove joint-view privacy for every role. Complete protocol and author simulations are retained.'),
(79,'cyclic-window-independence-generators','S1.Thmtheorem6','Explicit linear cyclic sliding-window independence generators for every seed and output length','H2','The authors give an explicit binary consecutive-basis construction for all seed lengths k and output lengths m at least k and prove every cyclic window has full rank. The complete combinatorial construction and its proof are retained; the five-bit specialization is not counted separately.')]


if len(sys.argv)>1:specs=[x for x in specs if x[1] in sys.argv[1:]]
for n,suffix,claim,title,level,reason in specs:
 existing=lane/'drafts'/('CP01A13326-AP-'+suffix)/'task.json'
 if existing.exists():
  print('Existing canonical revision preserved:',existing,flush=True)
  continue
 d=lane/'sources'/('icalp2026-'+str(n));source=d/'official-source.tex'
 parser=c.Parser();parser.feed((d/'published.html').read_text())
 meta=list(c.nodes(parser.root,'meta'))
 authors=[]
 for x in meta:
  if x.a.get('name')=='DC.Creator.PersonalName':
   parts=x.a['content'].split(', ',1);authors.append(' '.join(parts[::-1]))
 assert any(x.a.get('name')=='DC.Rights' and x.a.get('content')=='https://creativecommons.org/licenses/by/4.0/legalcode' for x in meta)
 sid='doi:10.4230/LIPIcs.ICALP.2026.'+str(n);url='https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ICALP.2026.'+str(n)
 save(d/'rights-facts.json',{'name':'CC BY 4.0','evidence':'Official HTML DC.Rights specifies https://creativecommons.org/licenses/by/4.0/legalcode','source_url':url,'original_paths':['published.html','published.pdf'],'conversion':'Official LaTeXML prose and math alttext, all author sections and appendices retained; native SVG object boundary explicitly checked.'})
 preamble=r'''\documentclass[10pt,a4paper]{article}
\usepackage{fontspec,amsmath,amssymb,amsthm,mathtools,graphicx,bm,bbm,stmaryrd,nicefrac,mathrsfs,braket,xcolor}
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
 if n==79:note+=' Theorem1.5 is the five-bit specialization of general Theorem1.6 and is not an additional collected claim. Corollary1.2 is not counted separately.'
 if n==19:note+=' The conference article includes a complete proof of Theorem 3.1. Introductory product-sample complexity assertions whose proofs are deferred to the full version are retained as author context and are not separate collected proof claims.'
 task={'schema_version':2,'selected_by':'Codex analysis-probability material worker','task_id':'CP01A13326-AP-'+suffix,'problem_id':None,'revision':'r001','source_id':sid,'source_version':'ICALP2026.'+str(n)+' official CC BY HTML/PDF publication retrieved 2026-10-13','claim_key':sid+':'+claim,'title':title,'authors':authors,'route':'information-theoretic private protocols and cyclic generators','source_url':url,'license':{'name':'CC BY 4.0','evidence_path':str((d/'rights-facts.json').relative_to(P)),'version_url':url},'statement_spans':statement,'proof_spans':proof,'context_spans':[],'standard_prerequisites':[],'core_obligations':[reason],'proof_roadmap':[],'difficulty_level':level,'difficulty_reason':reason,'dedup':{'status':'focused_semantic_uniqueness_supported','scope':'Refreshed all active operations projects using both lane/task and lane/drafts/task layouts, plus DOI/source-title and claim comparisons. No ICALP2026.79 or matching paper title was found in active task layouts. The helper circuit protocol, no-helper AND protocol and general cyclic generator are distinct conclusions with separate author arguments. Corollary1.2 and the five-bit generator special case Theorem1.5 are not counted separately.','compared':['CP01A13326-AP-parity-product-distribution-direct-sum'] if n==19 else []},'review_paths':[],'assembly':{'preamble_spans':[{'path':str((d/'official-preamble.tex').relative_to(P)),'start_line':1,'end_line':5,'label':'Official HTML math-alttext wrapper'}],'body_spans':[dict(proof[0],role='proof'),dict(statement[0],role='statement'),dict(proof[1],role='proof')],'asset_paths':[{'path':str((d/'published.pdf').relative_to(P)),'target':'items/original-'+d.name+'.pdf'},{'path':str((d/'published.html').relative_to(P)),'target':'items/original-'+d.name+'.html'}],'bibliography_paths':[],'engine':'xelatex','allow_shell_escape':False,'bibliography_backend':'none','bibliography_style':'plainnat','editorial_notes':[note]},'status':'ready_for_assembly','ready_blockers':[]}
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

