"""Acquisition only: download exact public sources before any proof extraction.

Raw pages remain private local cache. This is not an admission/publication tool.
No upstream scripts, auth, source classes, proof generation or stable-ID changes.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import datetime as dt
import hashlib
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import shutil
import threading
import time
from urllib.parse import urljoin,urlsplit
import urllib.error
import urllib.request

ROOT=Path('/disks/sata1/yupeng/human-proof-corpus')
REPO=ROOT/'repo'
CACHE=ROOT/'source-cache/catalog-r001'
LOCK=threading.Lock(); HOSTLOCK=threading.Lock(); HOSTS={}; RESULTS=[]
MAX_BYTES=100*1024*1024

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def dump(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def safe_url(u):
    p=urlsplit(u)
    return p.scheme in ('http','https') and p.hostname and not p.username and not p.password
def semaphore(u):
    host=urlsplit(u).hostname
    with HOSTLOCK:return HOSTS.setdefault(host,threading.Semaphore(2))
def object_path(h):return CACHE/'objects'/h[:2]/h
def save_object(part):
    h=sha(part);target=object_path(h);target.parent.mkdir(parents=True,exist_ok=True)
    # Each download preserves its incoming file; only exact objects are reused.
    with LOCK:
        if target.exists():assert sha(target)==h
        else:shutil.copyfile(part,target);target.chmod(0o444)
    return h,str(target.relative_to(CACHE))
def reuse_local(refs):
    found=[]
    for ref in refs:
        name=ref.get('path','');rel=Path(name)
        if rel.is_absolute() or '..' in rel.parts:continue
        if not (rel.suffix.lower() in ('.pdf','.zip','.gz','.tgz') or (rel.suffix.lower()=='.tex' and ('/sources/' in name or '/raw/' in name))):continue
        p=REPO/rel
        if not p.is_file() or p.is_symlink() or sha(p)!=ref.get('sha256'):continue
        h,local=save_object(p)
        found.append({'status':'reused_exact_catalog_hash','historical_path':name,'sha256':h,'bytes':p.stat().st_size,'local_object':local,'suffix':p.suffix})
    return found
def fetch(u,role,folder):
    if not safe_url(u):return {'url':u,'role':role,'status':'hold_unsafe_or_missing_url'}
    stem=hashlib.sha256(u.encode()).hexdigest()
    attempts=[]
    for attempt in range(2):
        stamp=dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
        part=folder/f'{stem}.{stamp}.attempt{attempt}.incoming'
        started=dt.datetime.now(dt.timezone.utc).isoformat();began=time.monotonic()
        try:
            # Ignore proxy variables and login-shell injections explicitly.
            opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
            request=urllib.request.Request(u,headers={'User-Agent':'HumanProofCorpus-source-acquisition/1.0 (public research corpus; acquisition only)'})
            with semaphore(u):
                with opener.open(request,timeout=35) as response,part.open('xb') as out:
                    total=0
                    while True:
                        data=response.read(1024*1024)
                        if not data:break
                        total+=len(data)
                        if total>MAX_BYTES:raise ValueError('response exceeds100MiB: explicit large-source handling needed')
                        out.write(data)
                    code=response.status;final=response.geturl();ctype=response.headers.get('Content-Type','').split(';')[0]
                time.sleep(0.15)
            if total==0:raise ValueError('empty response')
            with part.open('rb') as stream:magic=stream.read(8)
            if urlsplit(u).path.lower().endswith('.pdf') and not magic.startswith(b'%PDF'):
                raise ValueError('PDF URL did not yield PDF magic; preserved local response')
            h,path=save_object(part)
            return {'url':u,'final_url':final,'role':role,'status':'downloaded','http_status':code,'content_type':ctype,'sha256':h,'bytes':total,'local_object':path,'attempts':attempts,'started_at':started,'elapsed_seconds':round(time.monotonic()-began,3),'rights_status':'not_yet_admitted_for_publication'}
        except Exception as error:
            record={'attempt':attempt,'started_at':started,'error':type(error).__name__+': '+str(error),'local_incoming_preserved':str(part.relative_to(CACHE)) if part.exists() else None}
            attempts.append(record)
            # A access denial is a hold, never an auth/mirror bypass.
            if isinstance(error,urllib.error.HTTPError) and error.code in (401,403,404,410,429):break
            if attempt==0:time.sleep(1)
    return {'url':u,'role':role,'status':'hold_access','attempts':attempts,'rights_status':'not_admitted'}

class Links(HTMLParser):
    def __init__(self):super().__init__();self.links=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='a' and a.get('href'):self.links.append(a['href'])
        if tag=='meta' and a.get('name','').lower()=='citation_pdf_url' and a.get('content'):self.links.append(a['content'])

def explicit_assets(u,record):
    if record.get('status')!='downloaded' or 'html' not in record.get('content_type',''):return []
    p=CACHE/record['local_object']
    if p.stat().st_size>8*1024*1024:return []
    parser=Links();parser.feed(p.read_text(encoding='utf-8',errors='replace'))
    base=record.get('final_url',u);host=urlsplit(base).hostname; selected=[]
    for link in parser.links:
        absolute=urljoin(base,link);parts=urlsplit(absolute);path=parts.path.lower()
        if not safe_url(absolute) or parts.query or parts.fragment:continue
        # Only actual landing-page links, never guessed native paths or bib PDFs.
        if parts.hostname!=host:continue
        is_asset=path.endswith(('.pdf','.tex','.zip','.tar.gz','.tgz','.bib')) or '/file/src/' in path
        if is_asset and absolute not in selected:selected.append(absolute)
    # A page may contain many related articles; first6 explicit document assets
    # only. Full source page remains available for later acquisition follow-up.
    return selected[:6]

def build_queue():
    rows=[json.loads(x) for x in (REPO/'handoff/catalog/candidate_catalog.jsonl').read_text().splitlines() if x.strip()]
    grouped={}; missing=[]
    for r in rows:
        u=r.get('metadata',{}).get('source_url','')
        if not u:missing.append({'problem_id':r.get('problem_id'),'candidate_key':r.get('unassigned_candidate_key'),'status':'hold_missing_source_url'});continue
        grouped.setdefault(u,[]).append(r)
    queue=[]
    for u,rs in grouped.items():
        queue.append({'url':u,'url_key':hashlib.sha256(u.encode()).hexdigest(),'candidate_ids':[r.get('problem_id') or r.get('unassigned_candidate_key') for r in rs],'work_keys':sorted({r.get('work_identity_key','') for r in rs}),'artifact_refs':[ref for r in rs for ref in r.get('artifact_refs',[])]})
    dump(CACHE/'acquisition-queue.json',{'schema_version':1,'candidate_rows':len(rows),'unique_source_urls':len(queue),'missing_url_rows':len(missing),'mode':'acquisition_only_download_before_extraction','queue':queue,'missing_source_rows':missing})
    return queue
def summarize(total):
    records=[r for x in RESULTS for r in x['downloads']]
    value={'updated_at':dt.datetime.now(dt.timezone.utc).isoformat(),'phase':'acquisition_only','target_urls':total,'completed_urls':len(RESULTS),'source_urls_with_download_success':sum(any(r['status']=='downloaded' for r in x['downloads']) for x in RESULTS),'source_urls_with_exact_local_reuse':sum(bool(x['reused_local']) for x in RESULTS),'downloaded_files':sum(r['status']=='downloaded' for r in records),'downloaded_bytes':sum(r.get('bytes',0) for r in records if r['status']=='downloaded'),'hold_access_files':sum(r['status']=='hold_access' for r in records),'qualified_items_added':0,'extraction_started':False,'all_download_work_units_finished':len(RESULTS)==total}
    dump(CACHE/'PROGRESS.json',value)
def worker(job,total):
    folder=CACHE/'url-records'/job['url_key'];receipt=folder/'receipt.json'
    if receipt.exists():
        result=json.loads(receipt.read_text())
    else:
        folder.mkdir(parents=True,exist_ok=True)
        reuse=reuse_local(job['artifact_refs']);page=fetch(job['url'],'catalog_source',folder);downloads=[page]
        for asset in explicit_assets(job['url'],page):downloads.append(fetch(asset,'explicit_landing_page_document_asset',folder))
        result={'schema_version':1,'url':job['url'],'candidate_ids':job['candidate_ids'],'work_keys':job['work_keys'],'reused_local':reuse,'downloads':downloads,'qualified_count':0,'extraction_started':False,'raw_sources_private_cache_only':True}
        dump(receipt,result)
    with LOCK:
        RESULTS.append(result)
        with (CACHE/'acquisition-results.jsonl').open('a') as out:out.write(json.dumps(result,ensure_ascii=False)+'\n')
        summarize(total)
        if len(RESULTS)%50==0:print('acquired-work-units',len(RESULTS),'/',total,flush=True)
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--workers',type=int,default=16);ap.add_argument('--limit',type=int);args=ap.parse_args()
    if not 1<=args.workers<=32:raise ValueError('workers outside bounded range')
    CACHE.mkdir(parents=True,exist_ok=True)
    queue=build_queue()
    if args.limit:queue=queue[:args.limit]
    dump(CACHE/'RUN.json',{'pid':os.getpid(),'started_at':dt.datetime.now(dt.timezone.utc).isoformat(),'workers':args.workers,'max_per_host':2,'target_urls':len(queue),'acquisition_only':True,'max_file_bytes':MAX_BYTES,'cache':str(CACHE),'code_sha256':sha(Path(__file__))})
    with ThreadPoolExecutor(max_workers=args.workers) as pool:list(pool.map(lambda j:worker(j,len(queue)),queue))
    print((CACHE/'PROGRESS.json').read_text(),flush=True)
if __name__=='__main__':main()
