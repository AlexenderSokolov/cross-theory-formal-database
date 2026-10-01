#!/usr/bin/env python3
"""Build a reviewable cover + exact original PDF pages, never admit to corpus."""
import argparse,hashlib,json,re,sys
from pathlib import Path
from pypdf import PdfReader
sys.path.insert(0,str(Path(__file__).resolve().parent))
from stacks_extract import escape
from admit_staged import corpus_path

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def build(corpus,spec):
    corpus=Path(corpus).resolve();m=dict(spec)
    for field in ('title','author','difficulty_reason','source_url','source_version','source_sha256','license','dedup_key','retrieved_at'):
        if not isinstance(m.get(field),str) or not m[field].strip():raise ValueError('authored '+field+' required')
    if m.get('difficulty_level') not in {'H1','H2','H3'}:raise ValueError('authored difficulty required')
    locator=m.get('source_locator')
    if not isinstance(locator,dict) or not any(isinstance(locator.get(k),str) and locator[k].strip() for k in ('theorem','label','statement_identifier')):raise ValueError('unique theorem source_locator required')
    for field in ('source_path','license_path'):m[field]=corpus_path(corpus,m[field])
    source=corpus/m['source_path']
    if not source.read_bytes().startswith(b'%PDF-'):raise ValueError('source is not PDF')
    if sha(source)!=m['source_sha256']:raise ValueError('source hash mismatch')
    if not re.fullmatch(r'[A-Za-z0-9_./-]+',m['source_path']):raise ValueError('source path requires TeX-safe filename')
    count=len(PdfReader(source).pages)
    union=set()
    for field in ('statement_pages','proof_pages','context_pages'):
        pages=m.get(field,[])
        if not isinstance(pages,list) or (field!='context_pages' and not pages) or any(type(p)!=int or not 1<=p<=count for p in pages):raise ValueError('page range invalid: '+field)
        m[field]=sorted(set(pages));union.update(pages)
    if not re.match(r'^https?://',m['source_url']) or re.search(r'[\\{}\s]',m['source_url']):raise ValueError('invalid source URL')
    review=m.get('proof_review',{})
    if not isinstance(review,dict):raise ValueError('proof_review must be authored object')
    complete=review.get('reviewed') is True and review.get('context_checked') is True and all(isinstance(review.get(k),str) and review[k].strip() for k in ('method','note'))
    m['evidence_mode']='source_pdf_pages';m['proof_complete']=bool(complete and not m.get('admission_hold'));m['included_pages']=sorted(union)
    fields=[('Author',m['author']),('Difficulty',m['difficulty_level']+': '+m['difficulty_reason']),('Source theorem',json.dumps(locator,ensure_ascii=False)),('Source version',m['source_version']),('License',m['license']),('History','Cover added; original selected PDF pages reproduced unchanged')]
    tex=r'''\documentclass[11pt]{article}
\usepackage[a4paper,margin=25mm]{geometry}
\usepackage{fontspec}
\setmainfont{Noto Serif CJK SC}
\XeTeXlinebreaklocale "zh"
\XeTeXlinebreakskip=0pt plus 1pt
\usepackage{pdfpages}
\usepackage{xurl}
\usepackage{hyperref}
\begin{document}
'''
    tex+=r'\begin{center}\Large '+escape(m['title'])+r'\end{center}'+'\n'
    for label,value in fields:tex+=r'\noindent\textbf{'+label+r':} '+escape(value)+r'\par\medskip'+'\n'
    tex+=r'\noindent\textbf{Original:} \url{'+m['source_url']+r'}\par\medskip'+'\n'
    if m.get('admission_hold'):tex+=r'\noindent\textbf{Admission hold:} '+escape(m['admission_hold'])+r'\par'+'\n'
    tex+=r'\includepdf[pages={'+','.join(map(str,sorted(union)))+r'},pagecommand={}]{../'+m['source_path']+'}\n'+r'\end{document}'+'\n'
    return tex,m

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--spec',required=True,type=Path);p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--out-dir',required=True,type=Path);a=p.parse_args()
    try:
        tex,meta=build(a.root/'corpus',json.loads(a.spec.read_text()));a.out_dir.mkdir(parents=True,exist_ok=True)
        stem=re.sub(r'[^A-Za-z0-9_-]+','-',meta['dedup_key']).strip('-')
        path=a.out_dir/(stem+'.tex');path.write_text(tex);meta['tex_path']=str(path.resolve())
        meta_path=a.out_dir/(stem+'.metadata.json');meta_path.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
        print(json.dumps({'tex_path':str(path),'metadata_path':str(meta_path),'included_pages':meta['included_pages'],'admission_hold':meta.get('admission_hold')}));return 0
    except (OSError,ValueError,KeyError,TypeError) as e:print(json.dumps({'error':str(e)}));return 1
if __name__=='__main__':sys.exit(main())
