#!/usr/bin/env python3
"""Fail-closed extraction of pinned Stacks author text; screening is supplied by humans."""
import argparse, hashlib, json, re, shutil
from pathlib import Path
PIN='a04446e57ec1fbc252a871afcec7752fb2807b14'
ENV=re.compile(r'\\(begin|end)\{([^}]+)\}')
LABEL=re.compile(r'\\label\{([^}]+)\}')
REF=re.compile(r'\\(ref|eqref|autoref|pageref)\{([^}]+)\}')
KINDS={'theorem','proposition','lemma','definition','situation','remark','remarks','example'}
def clean(s): return re.sub(r'(?<!\\)%[^\n]*',lambda m:' '*len(m[0]),s)
def digest(s): return hashlib.sha256(s.encode()).hexdigest()
def blocks(s):
    stack=[]; result=[]
    for m in ENV.finditer(clean(s)):
        if m[1]=='begin': stack.append((m[2],m.start()))
        elif not stack or stack[-1][0]!=m[2]: raise ValueError('unbalanced source environment')
        else:
            kind,start=stack.pop()
            if kind in KINDS|{'proof'}: result.append((start,m.end(),kind))
    if stack: raise ValueError('unclosed source environment')
    return sorted(result)
def proof_flags(proof):
    p=clean(proof); text=re.sub(r'\\(?:begin|end)\{proof\}','',p).strip()
    flags=[]
    if re.search(r'\b(omitted|proof sketch|sketch of (?:the )?proof|left to (?:the )?reader|exercise for (?:the )?reader)\b',text,re.I): flags.append('incomplete')
    if re.search(r'\b(?:we omit|we leave|the reader (?:verifies|shows|checks|can verify|can show|can check))\b',text,re.I): flags.append('partial_omission_requires_review')
    if re.match(r'^(?:See|This follows from|This is|Apply)\s',text) and len(text)<240: flags.append('reference_only_or_short_delegate')
    if not text: flags.append('empty')
    return flags
class StacksSource:
    def __init__(self,root):
        self.root=Path(root); self.tags={}; self.by_label={}; self.cache={}
        chapters={p.stem for p in self.root.glob('*.tex')}
        for line in (self.root/'tags/tags').read_text().splitlines():
            if line.startswith('#') or ',' not in line: continue
            tag,full=line.split(',',1)
            possible=[c for c in chapters if full.startswith(c+'-')]
            if not possible: continue
            chapter=max(possible,key=len); label=full[len(chapter)+1:]
            self.tags[tag]=(chapter,label); self.by_label[full]=tag
    def chapter(self,chapter):
        if chapter not in self.cache:
            s=(self.root/(chapter+'.tex')).read_text(); self.cache[chapter]=(s,blocks(s))
        return self.cache[chapter]
    def block(self,tag,require_proof=True,omitted_detail_review=None):
        if tag not in self.tags: raise ValueError('absent tag '+tag)
        chapter,label=self.tags[tag]; s,bs=self.chapter(chapter)
        found=[b for b in bs if b[2] in KINDS and label in LABEL.findall(clean(s[b[0]:b[1]]))]
        if len(found)!=1: raise ValueError('tag is not a unique statement block '+tag)
        a,b,kind=found[0]; statement=s[a:b]; proof=''; end=b
        if require_proof:
            following=[q for q in bs if q[0]>=b]
            if not following or following[0][2]!='proof': raise ValueError('absent full proof '+tag)
            q=following[0]
            gap=clean(s[b:q[0]])
            gap=re.sub(r'\\begin\{(?:reference|history|slogan)\}.*?\\end\{(?:reference|history|slogan)\}','',gap,flags=re.S)
            if gap.strip(): raise ValueError('nonadjacent proof '+tag)
            end=q[1]
            for extra in following[1:]:
                if extra[2]!='proof' or clean(s[end:extra[0]]).strip(): break
                end=extra[1]
            proof=s[q[0]:end]
            checked=proof
            if omitted_detail_review:
                phrase=omitted_detail_review.get('exact_phrase','')
                if len(phrase.split())<2 or checked.count(phrase)!=1 or not all(omitted_detail_review.get(k) for k in ('scope','why_noncore')):
                    raise ValueError('invalid bounded omitted-detail review '+tag)
                checked=checked.replace(phrase,'[reviewed optional noncore detail]',1)
            if proof_flags(checked): raise ValueError('incomplete proof '+tag+': '+','.join(proof_flags(checked)))
        return dict(tag=tag,file=chapter+'.tex',chapter=chapter,label=label,kind=kind,start_line=s.count('\n',0,a)+1,end_line=s.count('\n',0,end-1)+1,statement=statement,proof=proof,excerpt=s[a:end],source_sha256=digest(s))
    def context(self,tag):
        if tag not in self.tags: raise ValueError('absent context tag '+tag)
        chapter,label=self.tags[tag]; s,bs=self.chapter(chapter); masked=clean(s)
        matches=list(re.finditer(r'\\label\{'+re.escape(label)+r'\}',masked))
        if len(matches)!=1: raise ValueError('nonunique context label '+tag)
        pos=matches[0].start()
        if label.startswith('section-'):
            starts=list(re.finditer(r'\\(?:sub)*section(?:\[[^]]*\])?\{',masked[:pos]))
            if not starts: raise ValueError('context section has no heading '+tag)
            a=starts[-1].start()
            nexts=[q[0] for q in bs if q[0]>pos and q[2] in KINDS]
            nexts += [m.start()+pos for m in re.finditer(r'\\(?:sub)*section\{',masked[pos:])]
            b=min(nexts) if nexts else masked.find(r'\end{document}',pos)
            if b<0: raise ValueError('unbounded section context '+tag)
            kind='section'
        elif label.startswith('equation-'):
            starts=list(re.finditer(r'\\begin\{(equation\*?|align\*?|gather\*?)\}',masked[:pos]))
            if not starts: raise ValueError('unsupported equation context '+tag)
            begin=starts[-1]; end=masked.find(r'\end{'+begin[1]+'}',pos)
            if end<0: raise ValueError('unclosed equation context '+tag)
            a=masked.rfind('\n\n',0,begin.start())+2
            b=end+len(r'\end{'+begin[1]+'}')
            # Include the following explanatory paragraph up to a blank line.
            tail=re.match(r'[^\n]*\n(?!\n)(?:(?!\n\n).)*',masked[b:],re.S)
            if tail: b+=tail.end()
            kind='equation'
        elif label.startswith('item-'):
            enclosing=[q for q in bs if q[0]<pos<q[1] and q[2] in KINDS]
            if enclosing: return self.block(tag,False)
            previous=[q[1] for q in bs if q[1]<pos and q[2] in KINDS|{'proof'}]
            following=[q[0] for q in bs if q[0]>pos and q[2] in KINDS]
            if not previous or not following: raise ValueError('unbounded item context '+tag)
            a=max(previous);b=min(following);kind='item_setup'
            while a<b and s[a].isspace(): a+=1
            if re.search(r'\\(?:sub)*section\{',masked[a:b]): raise ValueError('item setup crosses section '+tag)
            blocks(s[a:b]) # Do not emit an incomplete enclosing environment.
        else: return self.block(tag,False)
        excerpt=s[a:b]
        return dict(tag=tag,file=chapter+'.tex',chapter=chapter,label=label,kind=kind,start_line=s.count('\n',0,a)+1,end_line=s.count('\n',0,b-1)+1,statement=excerpt,proof='',excerpt=excerpt,source_sha256=digest(s))
    def span(self,spec):
        file=spec.get('file',''); chapter=Path(file).stem
        if file!=chapter+'.tex' or chapter not in {c for c,l in self.tags.values()}: raise ValueError('invalid span source file')
        a,b=spec.get('start_line'),spec.get('end_line');s,_=self.chapter(chapter);lines=s.splitlines(keepends=True)
        if type(a)!=int or type(b)!=int or not 1<=a<=b<=len(lines) or not spec.get('reason'): raise ValueError('invalid authored context span')
        excerpt=''.join(lines[a-1:b]);blocks(excerpt)
        if clean(excerpt).count('$$')%2: raise ValueError('incomplete display math in context span')
        return dict(tag='span-'+chapter+'-'+str(a)+'-'+str(b),file=file,chapter=chapter,label='',kind='explicit_prose_span',start_line=a,end_line=b,statement=excerpt,proof='',excerpt=excerpt,source_sha256=digest(s),reason=spec['reason'])
    def extract(self,tag,context_tags=(),omitted_detail_review=None,context_spans=()):
        r=self.block(tag,omitted_detail_review=omitted_detail_review); context_tags=[self.by_label.get(t,t) for t in context_tags]; contexts=[self.context(t) for t in context_tags]+[self.span(p) for p in context_spans]; included=set(context_tags)
        missing=set()
        for block in [r]+contexts:
            for _,label in REF.findall(clean(block['excerpt'])):
                full=label if label in self.by_label else block['chapter']+'-'+label
                t=self.by_label.get(full)
                if t and (self.tags[t][1].startswith(('situation-','definition-'))) and t not in included:
                    missing.add(t)
        if missing: raise ValueError('required context tags '+','.join(sorted(missing)))
        r['contexts']=contexts; return r

def escape(s): return ''.join({'\\':r'\textbackslash{}','&':r'\&','%':r'\%','$':r'\$','#':r'\#','_':r'\_','{':r'\{','}':r'\}','^':r'\textasciicircum{}','~':r'\textasciitilde{}'}.get(c,c) for c in str(s))
def render(source,record,spec):
    if spec.get('difficulty_level') not in {'H1','H2','H3'} or not spec.get('difficulty_reason'): raise ValueError('authored difficulty metadata required')
    allblocks=record.get('contexts',[])+[record]
    local={b['chapter']+'-'+l for b in allblocks for l in LABEL.findall(clean(b['excerpt']))}
    def local_label(f): return f[len(record['chapter'])+1:] if f.startswith(record['chapter']+'-') else f
    texts=[]
    for b in allblocks:
        def full(label): return label if label in source.by_label or label in local else b['chapter']+'-'+label
        def reference(m):
            f=full(m[2])
            if f in local: return '\\'+m[1]+'{'+local_label(f)+'}'
            tag=source.by_label.get(f)
            if not tag: raise ValueError('unresolved reference '+f)
            label=source.tags[tag][1].replace('-',' ')
            return r'\href{https://stacks.math.columbia.edu/tag/'+tag+'}{'+escape(label)+' (Tag '+tag+')}'
        t=REF.sub(reference,b['excerpt']); t=LABEL.sub(lambda m:r'\label{'+local_label(b['chapter']+'-'+m[1])+'}',t)
        t=re.sub(r'\\cite(?:\[([^]]*)\])?\{([^}]+)\}',lambda m:r'\href{https://stacks.math.columbia.edu/bibliography}{'+escape('Bibliography: '+m[2]+(' ('+m[1]+')' if m[1] else ''))+'}',t)
        texts.append(t)
    # Original macros/packages, with amsart instead of project-specific class and no xr machinery.
    pre=(source.root/'preamble.tex').read_text() if (source.root/'preamble.tex').exists() else r'\documentclass{amsart}\usepackage{hyperref}\newtheorem{theorem}{Theorem}\newtheorem{lemma}{Lemma}\newtheorem{situation}{Situation}'
    if pre.startswith(r'\IfFileExists{stacks-project.cls}'):
        pre=r'\documentclass{amsart}'+ '\n' + '% For dealing with references' + pre.split('% For dealing with references',1)[1]
    pre=re.sub(r'^.*(?:externaldocument|usepackage\{xr-hyper\}).*\n','',pre,flags=re.M)
    header=r'\begin{document}'+'\n'+r'\title[Stacks Project, Tag '+escape(record['tag'])+']{'+escape(spec.get('title','Stacks Tag '+record['tag']))+'}\n'+r'\maketitle'+'\n'
    header+=r'\noindent Copyright (C) 2005--2025 Johan de Jong. Stacks Project authors. Source: \href{https://stacks.math.columbia.edu/tag/'+record['tag']+'}{Tag '+record['tag']+'}.\n\n'
    header+='\\noindent Difficulty '+escape(spec['difficulty_level'])+': '+escape(spec['difficulty_reason'])+'.\n\n'
    header+='\\noindent History: excerpt from revision '+escape(PIN)+', '+escape(record['file'])+', lines '+str(record['start_line'])+'--'+str(record['end_line'])+'. Only reference presentation was adapted. Licensed under GNU FDL 1.2 or later; no invariant sections or cover texts. See accompanying COPYING.\n\n'
    return pre+'\n'+header+'\n\n'.join(texts)+'\n\\end{document}\n'

def main():
    p=argparse.ArgumentParser(); p.add_argument('--source',default='corpus/raw/stacks-project'); sub=p.add_subparsers(dest='cmd',required=True)
    d=sub.add_parser('discover'); d.add_argument('--out',required=True)
    e=sub.add_parser('extract'); e.add_argument('tag'); e.add_argument('--spec',required=True); e.add_argument('--out-dir',required=True)
    a=p.parse_args(); src=StacksSource(a.source)
    if a.cmd=='discover':
        out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True);count=0
        with out.open('w') as f:
            for tag,(chapter,label) in src.tags.items():
                if not label.startswith(('theorem-','proposition-')): continue
                try: r=src.block(tag)
                except ValueError: continue
                r['mechanical_flags']=[];r['screening_required']=True;f.write(json.dumps(r)+'\n');count+=1
        print(json.dumps({'discovered':count,'out':str(out)}));return
    spec=json.loads(Path(a.spec).read_text());spec.setdefault('difficulty_level',spec.get('level'));spec.setdefault('difficulty_reason',spec.get('reason'));r=src.extract(a.tag,spec.get('context_tags',[]),spec.get('omitted_detail_review'),spec.get('context_spans',[]));tex=render(src,r,spec)
    out=Path(a.out_dir);out.mkdir(parents=True,exist_ok=True)
    (out/(a.tag+'.tex')).write_text(tex);(out/(a.tag+'.excerpt.tex')).write_text(r['excerpt'])
    for c in r['contexts']: (out/(a.tag+'.context-'+c['tag']+'.tex')).write_text(c['excerpt'])
    shutil.copyfile(src.root/'COPYING',out/'COPYING')
    meta=dict(spec);meta.update(author='The Stacks Project Authors',source_url='https://stacks.math.columbia.edu/tag/'+a.tag,source_locator={'start_line':r['start_line'],'end_line':r['end_line']},source_path=str(src.root/r['file']),source_sha256=r['source_sha256'],license='GNU FDL 1.2 or later',license_path=str(out/'COPYING'),source_version=PIN,evidence_mode='native_tex',tex_path=str(out/(a.tag+'.tex')),excerpt_path=str(out/(a.tag+'.excerpt.tex')),excerpt_sha256=digest(r['excerpt']),proof_complete=True,dedup_key='stacks:'+a.tag)
    meta['extra_source_paths']=sorted({str(src.root/c['file']) for c in r['contexts']})
    meta['contexts']=[{k:c[k] for k in ('tag','file','label','kind','start_line','end_line','source_sha256')} | {'excerpt_sha256':digest(c['excerpt']), 'excerpt_path':str(out/(a.tag+'.context-'+c['tag']+'.tex'))} for c in r['contexts']]
    meta.setdefault('proof_review',{'reviewed':False,'context_checked':False,'method':'pending','note':'Requires substantive screening'})
    (out/(a.tag+'.metadata.json')).write_text(json.dumps(meta,indent=2)+'\n');print(json.dumps({'tag':a.tag,'out_dir':str(out)}))
if __name__=='__main__': main()
