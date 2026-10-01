"""Fail-closed evidence/compilation gate; does not prove mathematics or difficulty."""
import argparse, contextvars, hashlib, io, json, re, sys
from pathlib import Path
from contextlib import contextmanager
ID_RE=re.compile(r'^[0-9]{3,}$')
_validation_cache=contextvars.ContextVar('validation_file_cache',default=None)
def snapshot(path):
 path=path.resolve();stat=path.stat();signature=(stat.st_mtime_ns,stat.st_ctime_ns,stat.st_size,stat.st_ino)
 key=(path,signature);cache=_validation_cache.get()
 if cache is not None and key in cache:return cache[key]
 data=path.read_bytes();after=path.stat()
 if signature!=(after.st_mtime_ns,after.st_ctime_ns,after.st_size,after.st_ino):raise OSError('file changed while reading: '+str(path))
 result={'bytes':data}
 if cache is not None:cache[key]=result
 return result
def file_bytes(path):return snapshot(path)['bytes']
def file_text(path):
 state=snapshot(path)
 if 'text' not in state:state['text']=state['bytes'].decode('utf-8')
 return state['text']
def file_lines(path):
 state=snapshot(path)
 if 'lines' not in state:state['lines']=file_text(path).splitlines()
 return state['lines']
def sha(path):
 state=snapshot(path)
 if 'sha' not in state:state['sha']=hashlib.sha256(state['bytes']).hexdigest()
 return state['sha']
def pdf_page_count(path):
 state=snapshot(path)
 if 'page_count' not in state:
  from pypdf import PdfReader
  state['page_count']=len(PdfReader(io.BytesIO(state['bytes'])).pages)
 return state['page_count']
def local(corpus,name):
 if not isinstance(name,str) or not name:raise ValueError('missing local path')
 p=(corpus/name).resolve()
 if not p.is_relative_to(corpus.resolve()):raise ValueError('path escapes corpus: '+name)
 if not p.is_file():raise ValueError('missing file: '+name)
 return p

def read_json(path):
 return json.loads(file_text(path))
def write_json(path,data):
 path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');tmp.replace(path)
def dependencies(corpus,meta):
 """Hash provenance and all transitive literal local TeX/assets; reject dynamic paths."""
 deps={};seen=set()
 def visit(p):
  p=p.resolve()
  if p in seen:return
  seen.add(p)
  if not p.is_relative_to(corpus.resolve()):raise ValueError('dependency escapes corpus')
  deps[str(p.relative_to(corpus.resolve()))]=sha(p)
  if p.suffix.lower()!='.tex':return
  text=file_text(p);text=re.sub(r'(?<!\\)%[^\n]*','',text)
  for command,name in re.findall(r'\\(input|include|includegraphics|includepdf)(?:\s*\[[^\]]*\])?\s*\{([^}]+)\}',text):
   if '\\' in name or '#' in name:raise ValueError('dynamic dependency path unsupported: '+name)
   bases=[p.parent/name,corpus/'tex'/name]
   suffixes=['']+(['.tex'] if command in ('input','include') else ['.pdf','.png','.jpg','.jpeg','.eps'])
   found=next((b.with_suffix(s) if s else b for b in bases for s in suffixes if (b.with_suffix(s) if s else b).is_file()),None)
   if found is None:raise ValueError('missing dependency: '+name)
   visit(found)
  # TeX also permits unbraced input; reject rather than silently omit it.
  if re.search(r'\\(?:input|include)\s+(?!\{)',text):raise ValueError('unbraced input unsupported; use a literal braced local path')
 for name in [meta.get(field) for field in ('source_path','excerpt_path','license_path')]+meta.get('extra_source_paths',[]):
  if name:
   provenance=local(corpus,name);deps[str(provenance.relative_to(corpus.resolve()))]=sha(provenance)
 visit(local(corpus,meta['tex_path']))
 deps.pop(meta['tex_path'],None)
 return deps

def index_rows(corpus):
 path=corpus/'INDEX.md'
 if not path.is_file():raise ValueError('INDEX missing')
 rows={}
 for line in file_text(path).splitlines():
  if not line.startswith('|'):continue
  cols=[x.strip() for x in line.strip().strip('|').split('|')]
  if cols and ID_RE.fullmatch(cols[0]):rows.setdefault(cols[0],[]).append(cols)
 return rows

def check_item(corpus,item,record,rows,receipts):
 errors=[];meta={}
 def error(s):errors.append(s)
 try:meta=read_json(local(corpus,record.get('metadata')))
 except (OSError,ValueError,TypeError) as e:return {'status':'failed','errors':['metadata: '+str(e)]},meta
 if not isinstance(meta,dict):return {'status':'failed','errors':['metadata must be object']},{}
 if meta.get('id')!=item:error('metadata id mismatch')
 if meta.get('admission_hold'):error('admission_hold blocks qualification')
 for key in ('title','author','source_url','source_version','retrieved_at','license','difficulty_reason','dedup_key'):
  if not isinstance(meta.get(key),str) or not meta[key].strip():error('missing '+key)
 if not re.match(r'^https?://',str(meta.get('source_url',''))):error('source_url must be HTTP(S)')
 alea_pdf=re.fullmatch(r'https?://(?:www\.)?alea\.impa\.br(?::[0-9]+)?/articles/v([0-9]+)/([0-9]+)-[0-9]+\.pdf(?:[?#].*)?',str(meta.get('source_url','')),flags=re.I)
 if alea_pdf and int(alea_pdf[1])!=int(alea_pdf[2]):error('ALEA PDF URL volume conflicts between directory and filename')
 if not re.match(r'^\d{4}-\d{2}-\d{2}',str(meta.get('retrieved_at',''))):error('retrieved_at must be dated')
 locator=meta.get('source_locator')
 if isinstance(locator,dict) and isinstance(locator.get('doi'),str):
  expected_doi=locator['doi'].casefold().rstrip('.,;:')
  version_dois=re.findall(r'10\.\d{4,9}/[^\s<>"]+',str(meta.get('source_version','')),flags=re.I)
  if any(doi.casefold().rstrip('.,;:')!=expected_doi for doi in version_dois):error('source_version DOI conflicts with source_locator DOI')
 if meta.get('difficulty_level') not in ('H1','H2','H3'):error('difficulty_level unqualified')
 review=meta.get('proof_review',{})
 if not isinstance(review,dict) or review.get('reviewed') is not True or review.get('context_checked') is not True or not all(isinstance(review.get(k),str) and review[k].strip() for k in ('method','note')):error('proof_review missing authored completeness/context comparison')
 if meta.get('proof_complete') is not True:error('proof_complete not reviewed')
 try:
  source=local(corpus,meta.get('source_path'));tex=local(corpus,meta.get('tex_path'));local(corpus,meta.get('license_path'))
  if sha(source)!=meta.get('source_sha256'):error('source hash mismatch')
  if not re.match(r'^'+re.escape(item)+r'_',tex.name):error('tex filename id mismatch')
  if meta.get('excerpt_path') and sha(local(corpus,meta['excerpt_path']))!=meta.get('excerpt_sha256'):error('excerpt hash mismatch')
  mode=meta.get('evidence_mode')
  if mode=='native_tex':
   locator=meta.get('source_locator');lines=file_lines(source)
   if not isinstance(locator,dict) or not isinstance(locator.get('start_line'),int) or not isinstance(locator.get('end_line'),int) or not 1<=locator['start_line']<=locator['end_line']<=len(lines):error('source_locator invalid line range')
   else:
    excerpt='\n'.join(lines[locator['start_line']-1:locator['end_line']])
    if '\\begin{proof}' not in excerpt or '\\end{proof}' not in excerpt:error('source proof environment missing in locator')
    if meta.get('excerpt_path') and file_text(local(corpus,meta['excerpt_path'])).strip()!=excerpt.strip():error('source excerpt does not exactly match locator')
   if '\\begin{proof}' not in file_text(tex):error('tex proof environment missing')
  elif mode=='source_pdf_pages':
   if not file_bytes(source).startswith(b'%PDF-'):error('source PDF signature missing')
   for field in ('statement_pages','proof_pages','context_pages'):
    pages=meta.get(field,[])
    if not isinstance(pages,list) or (field!='context_pages' and not pages) or any(type(x)!=int or x<1 for x in pages):error(field+' invalid')
   if not meta.get('source_locator'):error('source_locator missing')
   try:
    count=pdf_page_count(source)
    if any(page>count for field in ('statement_pages','proof_pages','context_pages') for page in meta.get(field,[]) if type(page)==int):error('source PDF page out of bounds')
    includes=re.findall(r'\\includepdf(?:\[([^\]]*)\])?\{([^}]+)\}',file_text(tex))
    covered=set()
    for options,name in includes:
     included=(tex.parent/name).resolve()
     if included!=source:continue
     pages_match=re.search(r'pages\s*=\s*(\{[^}]*\}|[^,]+)',options)
     spec=pages_match[1].strip('{} ') if pages_match else '1'
     if spec=='-':covered.update(range(1,count+1));continue
     for piece in spec.split(','):
      piece=piece.strip()
      if piece.isdigit():covered.add(int(piece))
      elif re.fullmatch(r'\d+-\d+',piece):
       first,last=map(int,piece.split('-'));covered.update(range(first,last+1))
    if not set(meta.get('statement_pages',[])+meta.get('proof_pages',[])+meta.get('context_pages',[])).issubset(covered):error('PDF evidence wrapper must include original required source pages')
   except ImportError:error('PDF page verification requires pypdf')
   except Exception as e:error('source PDF unreadable: '+str(e))
  else:error('evidence_mode unsupported')
  contexts=meta.get('contexts',[])
  if not isinstance(contexts,list):error('contexts must be a list');contexts=[]
  for context in contexts:
   if not isinstance(context,dict):error('context metadata must be object');continue
   candidates=[name for name in meta.get('extra_source_paths',[]) if Path(name).name==context.get('file')]
   if Path(meta.get('source_path','')).name==context.get('file'):candidates.append(meta['source_path'])
   candidates=list(dict.fromkeys(candidates))
   if len(candidates)!=1:error('context source must identify exactly one declared raw path');continue
   context_source=local(corpus,candidates[0])
   if sha(context_source)!=context.get('source_sha256'):error('context source hash mismatch')
   context_excerpt=local(corpus,context.get('excerpt_path'))
   if sha(context_excerpt)!=context.get('excerpt_sha256'):error('context excerpt hash mismatch')
   start,end=context.get('start_line'),context.get('end_line')
   context_lines=file_lines(context_source)
   if type(start)!=int or type(end)!=int or not 1<=start<=end<=len(context_lines):error('context source line range invalid')
   elif file_text(context_excerpt).strip()!='\n'.join(context_lines[start-1:end]).strip():error('context excerpt does not exactly match source lines')
  deps=dependencies(corpus,meta)
  receipt=receipts.get(item,{})
  if not isinstance(receipt,dict) or receipt.get('ok') is not True or receipt.get('passes')!=2:error('compile missing/failed two-pass receipt')
  else:
   if receipt.get('input_sha256')!=sha(tex):error('compile input hash mismatch')
   if receipt.get('dependency_sha256')!=deps:error('compile dependency hash mismatch')
   try:
    pdf=local(corpus,receipt.get('pdf'))
    if not file_bytes(pdf).startswith(b'%PDF-') or receipt.get('pdf_sha256')!=sha(pdf):error('compile PDF hash/signature mismatch')
   except (OSError,ValueError,TypeError) as e:error('compile PDF: '+str(e))
 except (OSError,ValueError,KeyError,TypeError,UnicodeError) as e:error('source/tex/dependency: '+str(e))
 entry=rows.get(item,[])
 if len(entry)!=1:error('INDEX must have exactly one row')
 elif len(entry[0])!=5 or entry[0][1]!=meta.get('title') or entry[0][2]!=meta.get('difficulty_level') or meta.get('source_url','missing-url') not in entry[0][4]:error('INDEX metadata mismatch')
 return {'status':'qualified' if not errors else 'failed','errors':errors},meta

def _validate(root,item=None):
 corpus=root/'corpus';report={'schema_version':1,'qualified_count':0,'active_count':0,'quarantined_count':0,'items':{},'errors':[]}
 try:
  manifest=read_json(corpus/'item_status.json')
  if manifest.get('schema_version')!=1 or not isinstance(manifest.get('items'),dict):raise ValueError('invalid manifest schema')
  records=manifest['items']
 except (OSError,ValueError,AttributeError) as e:
  report['errors'].append('manifest: '+str(e));return report
 try:rows=index_rows(corpus)
 except (OSError,ValueError) as e:rows={};report['errors'].append(str(e))
 try:receipts=read_json(corpus/'.work/compile_report.json')
 except (OSError,ValueError):receipts={}
 if not isinstance(receipts,dict):receipts={}
 files={}
 for p in (corpus/'tex').glob('*.tex'):
  m=re.match(r'([0-9]{3,})_',p.name)
  if not m:report['errors'].append('invalid tex filename: '+p.name);continue
  files.setdefault(m[1],[]).append(p)
  if m[1] not in records:report['errors'].append('tex absent from manifest: '+m[1])
 if item is not None and item not in records:report['errors'].append('requested item absent from manifest: '+item)
 all_results={};metas={}
 for n,record in records.items():
  if not ID_RE.fullmatch(n) or not isinstance(record,dict):report['errors'].append('invalid manifest item: '+n);continue
  status=record.get('status')
  if status=='quarantined':all_results[n]={'status':'quarantined','errors':[],'reason':record.get('reason','')};continue
  if status!='active':all_results[n]={'status':'failed','errors':['manifest status must be active or quarantined']};continue
  result,meta=check_item(corpus,n,record,rows,receipts);all_results[n]=result;metas[n]=meta
  if len(files.get(n,[]))!=1:result['errors'].append('exactly one tex filename required');result['status']='failed'
 # Check uniqueness against every active item even for --item.
 keys={};claims={}
 for n,m in metas.items():
  for registry,key,label in ((keys,' '.join(str(m.get('dedup_key','')).casefold().split()),'dedup_key'),(claims,json.dumps([m.get('source_url'),m.get('source_locator')],sort_keys=True),'source identity')):
   if not key:continue
   if key in registry:
    for dup in (n,registry[key]):all_results[dup]['errors'].append('duplicate '+label);all_results[dup]['status']='failed'
   else:registry[key]=n
 for n in rows:
  if n not in records or not isinstance(records[n],dict) or records[n].get('status')!='active':report['errors'].append('INDEX contains nonactive item: '+n)
 report['items']={n:r for n,r in all_results.items() if item is None or n==item}
 report['qualified_count']=sum(r['status']=='qualified' for r in report['items'].values())
 report['active_count']=sum(r['status']!='quarantined' for r in report['items'].values())
 report['quarantined_count']=sum(r['status']=='quarantined' for r in report['items'].values())
 return report

@contextmanager
def validation_session():
 """Caller-owned cache for intermediate gates; exit before final validate()."""
 token=_validation_cache.set({})
 try:yield
 finally:_validation_cache.reset(token)

def validate_in_session(root,item=None):
 """Explicit intermediate gate; standalone validate() remains fresh."""
 if _validation_cache.get() is None:raise RuntimeError('validation session required')
 return _validate(root,item)

def validate(root,item=None):
 # Per-call ContextVar scope avoids cross-validation staleness and thread races.
 token=_validation_cache.set({})
 try:return _validate(root,item)
 finally:_validation_cache.reset(token)

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);parser.add_argument('--item');args=parser.parse_args()
 report=validate(args.root.resolve(),args.item);write_json(args.root/'corpus/.work/validation_report.json',report)
 print(json.dumps(report,ensure_ascii=False,indent=2));return int(bool(report['errors']) or any(r['status']=='failed' for r in report['items'].values()))
if __name__=='__main__':sys.exit(main())
