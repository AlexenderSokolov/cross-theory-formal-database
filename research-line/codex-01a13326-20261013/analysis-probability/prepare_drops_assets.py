from pathlib import Path
import sys,json,urllib.request,urllib.parse
import pymupdf
import convert_drops_html as c
lane=Path(__file__).resolve().parent
P=lane.parent
def prepare(sn):
 d=lane/'sources'/sn
 parser=c.Parser();parser.feed((d/'published.html').read_text())
 article=next(c.nodes(parser.root,'article'))
 objects=[o for o in c.nodes(article,'object') if o.a.get('type')=='image/svg+xml']
 base=urllib.parse.urljoin('https://drops.dagstuhl.de',next(c.nodes(parser.root,'base')).a['href'])
 records=[]
 for i,o in enumerate(objects,1):
  url=urllib.parse.urljoin(base,o.a['data']);svg=d/'svg-originals'/Path(urllib.parse.urlparse(url).path).name
  svg.parent.mkdir(exist_ok=True)
  if not svg.exists():svg.write_bytes(urllib.request.urlopen(url,timeout=60).read())
  pdf=d/'svg-pdf'/(sn+'-svg-'+str(i).zfill(2)+'.pdf');pdf.parent.mkdir(exist_ok=True)
  if not pdf.exists():pdf.write_bytes(pymupdf.open(svg).convert_to_pdf())
  assert len(pymupdf.open(pdf))==1
  c.GRAPHICS[o.a['data']]=pdf.name
  records.append({'object_id':o.a.get('id'),'html_data':o.a['data'],'official_url':url,'svg_path':str(svg.relative_to(P)),'pdf_path':str(pdf.relative_to(P)),'target':'items/'+pdf.name,'license':'CC BY 4.0','license_evidence_path':str((d/'rights-facts.json').relative_to(P)),'conversion':'PyMuPDF '+pymupdf.VersionBind+' SVG convert_to_pdf'})
 if objects:
  (d/'svg-asset-ledger.json').write_text(json.dumps({'objects':records,'html_path':str((d/'published.html').relative_to(P)),'html_base_url':base,'source_object_count':len(objects),'inserted_asset_count':len(objects)},indent=2)+'\n')
 source=d/'official-source.tex'
 if not source.exists():source.write_text('\n'.join(c.render(s) for s in article.c if isinstance(s,c.N) and s.t=='section'))
 print(sn,len(source.read_text().splitlines()),'lines',len(objects),'SVG')
if __name__=='__main__':
 for sn in sys.argv[1:]:prepare(sn)

