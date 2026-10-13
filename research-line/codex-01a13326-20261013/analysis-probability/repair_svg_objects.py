from pathlib import Path
import sys,json,urllib.request,urllib.parse,copy,os
import pymupdf
R=Path('/disks/sata1/yupeng/human-proof-corpus/operations/codex-work-01a13326')
P=R/'research-line/codex-01a13326-20261013'
lane=P/'analysis-probability'
os.environ['PATH']='/disks/sata1/yupeng/human-proof-corpus/runtime/texlive/2025/bin/x86_64-linux:'+os.environ['PATH']
sys.path.insert(0,str(lane))
import convert_drops_html as c
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def repair(suffix):
 td=lane/'drafts'/('CP01A13326-AP-'+suffix)
 tf=td/('task-r002.json' if suffix=='gln-dnf-separating-distribution' else 'task.json')
 task=json.loads(tf.read_text())
 revision='r003' if suffix=='gln-dnf-separating-distribution' else 'r002'
 current=json.loads((td/'task.json').read_text())
 if current['revision']>=revision:
  print(json.dumps({'task':current['task_id'],'revision':current['revision'],'status':'existing repaired revision preserved'}),flush=True)
  return lane/'jobs'/current['task_id']/current['revision']
 source=P/task['statement_spans'][0]['path']
 d=source.parent;sn=d.name
 parser=c.Parser();parser.feed((d/'published.html').read_text())
 article=next(c.nodes(parser.root,'article'))
 obs=[o for o in c.nodes(article,'object') if o.a.get('type')=='image/svg+xml']
 base=urllib.parse.urljoin('https://drops.dagstuhl.de',next(c.nodes(parser.root,'base')).a['href'])
 original_dir=d/'svg-originals';original_dir.mkdir(exist_ok=True)
 converted_dir=d/'svg-pdf';converted_dir.mkdir(exist_ok=True)
 records=[];assets=[]
 for i,o in enumerate(obs,1):
  url=urllib.parse.urljoin(base,o.a['data'])
  svg=original_dir/Path(urllib.parse.urlparse(url).path).name
  if not svg.exists():svg.write_bytes(urllib.request.urlopen(url,timeout=60).read())
  pdf=converted_dir/(sn+'-svg-'+str(i).zfill(2)+'.pdf')
  doc=pymupdf.open(svg)
  pdf.write_bytes(doc.convert_to_pdf())
  check=pymupdf.open(pdf)
  assert len(check)==1 and check[0].get_drawings(), 'SVG did not yield vector graphics'
  target='items/'+pdf.name
  c.GRAPHICS[o.a['data']]=pdf.name
  records.append({'object_id':o.a.get('id'),'html_data':o.a['data'],'official_url':url,'svg_path':str(svg.relative_to(P)),'pdf_path':str(pdf.relative_to(P)),'target':target,'license':'CC BY 4.0','license_evidence_path':task['license']['evidence_path'],'conversion':'PyMuPDF '+pymupdf.VersionBind+' SVG convert_to_pdf, original vector content retained','page_rect':list(check[0].rect)})
  assets.extend([{'path':str(svg.relative_to(P)),'target':'items/'+sn+'-original-svg-'+str(i).zfill(2)+'.svg'},{'path':str(pdf.relative_to(P)),'target':target}])
 # Generated paragraph anchors locate the image insertion in the existing corrected text.
 # Keep every original line; no regeneration of author mathematics or prior wrapper fixes.
 generated='\n'.join(c.render(n) for n in article.c if isinstance(n,c.N) and n.t=='section').splitlines()
 old=source.read_text().splitlines()
 insertions={}
 for i,line in enumerate(generated):
  if r'\includegraphics[' not in line:continue
  located=None
  for j in range(i-1,max(-1,i-30),-1):
   anchor=generated[j]
   if not anchor.strip() or r'\includegraphics[' in anchor:continue
   matches=[k+1 for k,text in enumerate(old) if text==anchor]
   if len(matches)==1:
    assert all(not x.strip() for x in generated[j+1:i]), 'Intervening author text must not be displaced'
    located=matches[0];break
  assert located is not None,'No unambiguous paragraph anchor'
  insertions.setdefault(located,[]).append(line)
 assert sum(map(len,insertions.values()))==len(obs)
 result=[]
 for i,line in enumerate(old,1):
  result.append(line)
  result.extend(insertions.get(i,[]))
 newsource=d/('official-source-svg-'+revision+'.tex')
 newsource.write_text('\n'.join(result)+'\n')
 ledger=d/'svg-asset-ledger.json'
 save(ledger,{'html_path':str((d/'published.html').relative_to(P)),'html_base_url':base,'license_evidence_path':task['license']['evidence_path'],'objects':records,'source_object_count':len(obs),'inserted_asset_count':len(obs)})
 assets.append({'path':str(ledger.relative_to(P)),'target':'items/'+sn+'-svg-asset-ledger.json'})
 oldpath=str(source.relative_to(P));newpath=str(newsource.relative_to(P))
 for spans in [task['statement_spans'],task['proof_spans'],task['context_spans'],task['assembly']['body_spans']]:
  for span in spans:
   if span['path']!=oldpath:continue
   start,end=span['start_line'],span['end_line']
   span['path']=newpath
   span['start_line']=start+sum(len(v) for k,v in insertions.items() if k<start)
   span['end_line']=end+sum(len(v) for k,v in insertions.items() if k<=end)
 task['revision']=revision
 task['assembly']['asset_paths'].extend(assets)
 task['assembly']['editorial_notes'].append('SVG assembly correction: official HTML object graphics restored at their original paragraph positions. Original SVGs, faithful vector PDF conversions and URL/license ledger are included; all existing author text and captions are retained.')
 canonical=td/'task.json'
 prior=json.loads(canonical.read_text())
 alias=td/('task-'+prior['revision']+'.json')
 if not alias.exists():save(alias,prior)
 save(td/('task-'+revision+'.json'),task)
 save(canonical,task)
 originals=json.loads((lane/'ORIGINAL_SOURCES.json').read_text())
 record=next((x for x in originals if x['source_id']==task['source_id']),None)
 if record is None:
  record={'source_id':task['source_id'],'paths':[]};originals.append(record)
 for x in records:
  if x['svg_path'] not in record['paths']:record['paths'].append(x['svg_path'])
 save(lane/'ORIGINAL_SOURCES.json',originals)
 sys.path.insert(0,str(R/'corpus-work/scripts'))
 import prepared_delivery as delivery
 job=delivery.assemble(canonical,P,lane/'jobs',material_only=True)
 print(json.dumps({'task':task['task_id'],'revision':revision,'assembly_result':job,'objects':len(obs)},ensure_ascii=False),flush=True)
 return job
if __name__=='__main__':
 for suffix in sys.argv[1:]:repair(suffix)

