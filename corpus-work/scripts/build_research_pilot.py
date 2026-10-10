"""Assemble the bounded 2026-10-10 local pilot; never admit or publish items.

Uses retained Stacks author text, existing rendering/evidence/compile/item gates.
Only the pilot output and external work directory are writable by this entrypoint.
"""
from __future__ import annotations
import argparse
import datetime as dt
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

import stacks_extract as se
import derive_stacks_evidence as evidence
import compile_editable_delivery as compiler
import editable_delivery as gate

VERSION = 'local cached snapshot; exact chapter hashes; revision unknown'
NONADJACENT_20 = ('\\noindent\nThis lemma can be improved to say that the birational transformation\n'
    'between two nonisomorphic minimal models can be factored as a sequence of\n'
    'elementary transformations as in Example \\ref{example-nonunique-in-genus-zero}.\n'
    'If we ever need this, we will precisely formulate and prove this here.')
HOLDS = {
    3: 'source-proof-gap: derived.tex:11554 claims arbitrary beta_n is killed, while 11505-11519 only kills the kernel of H_n -> H; retain author text, no generated repair.',
    13: 'source-formula-review: mixed-characteristic level proof contains unresolved core valuation and K/L, w/w^p discrepancies; no silent mathematical repair.',
    15: 'source-notation-review: M-prime in the final Mittag-Leffler argument has not been located as an author-defined object; no generated completion.',
}
# Explicit, bounded author background. A plus suffix means the complete author
# proof is retained; all other entries retain the exact statement/definition.
CONTEXT = {
  1: ['morphisms-definition-quasi-projective', 'morphisms-section-projective', 'spaces-morphisms-lemma-refined-valuative-criterion-universally-closed', 'decent-spaces-lemma-bounded-fibres', 'decent-spaces-lemma-quasi-compact-reasonable-stratification'],
  2: ['stacks-more-morphisms-lemma-etale-local-finite-inertia+', 'stacks-more-morphisms-lemma-well-nigh-affine-moduli-space+', 'stacks-more-morphisms-lemma-etale-separated-over-well-nigh-affine+'],
  4: ['derham-section-quasi-finite-syntomic', 'derham-remark-local-description', 'derham-lemma-base-change-Garel-upstairs+', 'derham-lemma-existence-base-change-Garel-upstairs+', 'discriminant-example-universal-quasi-finite-syntomic'],
  5: ['derham-lemma-Garel-upstairs+', 'discriminant-proposition-tate-map+', 'discriminant-section-finite-morphisms'],
  6: ['more-algebra-definition-henselian-pair', 'more-algebra-lemma-helper-finite+', 'more-algebra-lemma-helper-finite-type+', 'more-algebra-lemma-check-isomorphism-zariski'],
  7: ['varieties-lemma-exact-sequence-induction+', 'varieties-lemma-vanishin-h0-negative+'],
  8: ['examples-lemma-non-descending-property-projective+'],
  9: ['more-algebra-definition-solution', 'more-algebra-remark-construction', 'more-algebra-lemma-pre-characteristic-p-case+', 'more-algebra-lemma-cohen', 'more-algebra-lemma-make-degree-q-extension'],
  10: ['models-definition-type', 'models-definition-genus', 'models-lemma-top-genus', 'models-definition-top-genus', 'models-definition-type-minimal', 'models-lemma-diagonal-negative+', 'models-lemma-minus-one+', 'models-lemma-non-irreducible-minimal-type-genus-at-least-one+'],
  11: ['properties-lemma-extend+', 'properties-lemma-extend-finite-presentation+'],
  12: ['homology-definition-filtered', 'homology-definition-filtered-complex', 'derived-definition-K-injective', 'injectives-theorem-K-injective-embedding-grothendieck', 'injectives-lemma-derived-products+', 'derived-lemma-triangle-K-injective'],
  14: ['algebraization-situation-algebraize', 'algebraization-equation-delta-Z', 'algebraization-definition-s-d-inequalities', 'algebraization-lemma-helper-algebraize+', 'algebraization-lemma-when-done+'],
  16: ['defos-lemma-canonical-class+', 'defos-lemma-lift-complex+', 'defos-lemma-induced-map'],
  17: ['artin-section-axioms-functors', 'artin-lemma-base-change-versal', 'restricted-lemma-algebraize-rig-etale-affine+'],
  18: ['more-algebra-lemma-cut-complex-in-two+', 'more-algebra-lemma-last-one-flat', 'more-algebra-definition-pseudo-coherent'],
  19: ['restricted-lemma-faithful', 'restricted-lemma-algebraize-rig-etale-affine+', 'restricted-lemma-algebraize-morphism-rig-etale+'],
  20: ['models-section-models', 'models-definition-minimal-model', 'models-definition-numerical-type-model', 'models-lemma-numerical-type-minimal-model', 'models-lemma-genus-zero+'],
}
SPANS = {
  12: [('homology.tex',5957,5972,'Complete filtered-complex definition and its following notation paragraph')],
  19: [('restricted.tex',6527,6543,'Required fixed base, closed subset and completion notation')],
}
EDITORIAL = {
  10: 'Author text is retained verbatim. In the grouping paragraph Phi_j is a source notation slip for Psi_k; the zero-length-chain convention is the preceding parenthetical convention. No new proof is supplied.',
  12: 'Author text is retained verbatim. In the product over p-prime greater than p, the factor printed J^{p,bullet} is indexed by p-prime as in the surrounding displayed definitions. The composition on source line 2214 has the order of the two alpha factors reversed by type. Quotients F^p/F^{p-prime} use p-prime at least p. These are editorial reading notes, not changes to the author body.',
  7: 'Source symbols, including the printed P^1 in the hyperplane paragraph and exponents in the diagram, are preserved; editorial corrections are not inserted into author text.',
  17: 'The printed reversal A_n to B_n in the final sentence is retained. The preceding argument concerns B_n to A_n.',
}
# Each exception names only a short, actually reviewed routine omission.
OMISSIONS = {
  2: [('omit the verification that\nthis construction is compatible with base change', 'Functoriality of the explicitly glued map f', 'Pullback of the already constructed matching local maps agrees by uniqueness of sheaf gluing; this does not supply local moduli existence.'),
      ('we omit\nthe verification that the diagrams\n(\\ref{equation-fundamental-diagram}) commute.', 'Compatibility of the glued f with its defining local maps', 'The diagrams state the restrictions used to define f; the separate cartesian claim is proved in full afterwards.'),
      ('details omitted.', 'Agreement of psi_i on overlaps in the final categorical quotient argument', 'The author supplies the uniform categorical quotient f_ij as the exact uniqueness input; the global quotient and gluing construction are retained.')],
  4: [('small detail omitted.', 'Preservation of the nice conditions under polynomial extension and restriction to an open', 'Local freeness of differentials and regularity of the named delta section are preserved in the displayed polynomial/open construction; the model-comparison construction itself is fully written.')],
  5: [('small\ndetail omitted', 'Zariski locality of constructing a unique sheaf map', 'Uniqueness was already proved and provides overlap agreement; no new existence step is omitted.'),
      ('small detail omitted; hint:', 'Compatibility of the colimit construction with affine base change', 'The author gives the finite-stage factorization hint explicitly; finite presentation permits the maps between approximating affine schemes, whereas the trace construction and uniqueness are already retained.')],
  6: [('Details omitted.', 'Definition of the characteristic polynomial for finite locally free modules', 'Characteristic polynomials agree under changes of basis and hence glue on the referenced standard affine covering; this is standard linear algebra, not the factorization argument.'),
      ('details omitted', 'The chosen integral element b is a unit on the factor B-prime_1', 'Its residue is one modulo I and I lies in the Jacobson radical of an integral algebra, as established earlier in the same proof; the etale splitting argument is fully retained.')],
  7: [('details\nomitted', 'Rank growth of an ample power on a positive-dimensional support', 'The author explicitly invokes asymptotic Riemann-Roch here; the new annihilator-subspace and injectivity contradiction are fully written.')],
  17: [('Some details omitted.', 'Descent after the already displayed etale affine reduction', 'Etale descent of smoothness is an explicitly stated standard input; the uniform Rees-algebra argument is complete below.')],
  20: [('local computation omitted', 'Multiplicity of the exceptional divisor of the blowup of a regular surface point', 'The standard m-adic order of a uniformizer gives this multiplicity; the comparison of minimal models and contraction induction is fully retained.')],
}

def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8', newline='\n')

def package_manifest(row, state):
    return dict(schema_version=1,scope='Local pilot only; temporary ID, no production admission',
                assembly_state=state,verified_count=1 if state=='verified_editable_tex' else 0,items=[row])

def rebuild_db(repo, package):
    shutil.copy2(repo/'editable-corpus/schema.sql',package/'schema.sql')
    shutil.copy2(repo/'editable-corpus/rebuild_database.py',package/'rebuild_database.py')
    loader=importlib.util.spec_from_file_location('pilot_rebuild',package/'rebuild_database.py')
    mod=importlib.util.module_from_spec(loader);loader.loader.exec_module(mod)
    mod.rebuild(package,package/'corpus.sqlite')

def fail_package(repo, package, reason):
    """Failure retains source artifacts but clears every qualifying projection."""
    old=gate.read_json(package/'manifest.json') if (package/'manifest.json').exists() else {}
    previous=json.loads(json.dumps(old))
    last_gate=gate.read_json(package/'gate-result.json') if (package/'gate-result.json').exists() else None
    for row in old.get('items',[]):
        row['status']='failed'
        dump(package/'sources'/row['problem_id']/'provenance.json',row)
    dump(package/'failed-candidate.json',dict(reason=reason,previous_manifest=previous,last_gate_result=last_gate,status='failed'))
    manifest=dict(schema_version=1,scope='Failed local pilot; no qualified items',assembly_state='failed',verified_count=0,items=[])
    dump(package/'manifest.json',manifest)
    (package/'INDEX.md').write_text('# Failed local pilot\n\nNo qualified items. See failed-candidate.json.\n',encoding='utf-8',newline='\n')
    dump(package/'delivery-evidence.json',dict(schema_version=1,package_manifest_sha256=gate.digest((package/'manifest.json').read_bytes()),items={},failure=reason))
    dump(package/'gate-result.json',dict(schema_version=1,mode='assembly-hold',editable_qualified_count=0,items={},errors=[reason],note='Assembly failed; this record does not assert that the item gate was run. Any prior gate output is retained in failed-candidate.json.'))
    rebuild_db(repo,package)

def material_path(repo,c):
    ident=c['research_id']
    if not re.fullmatch(r'[A-Za-z0-9_.-]+',ident):raise ValueError('invalid research material ID')
    return repo/'research-line/archive/2026-10-10/initial_corpus/items'/(ident+'.tex')

def check_context_reviews(out, number, contexts):
    """A retained full block is not, by itself, evidence that omissions are noncore."""
    path=out/'CONTEXT_REVIEW.json'
    reviewed=gate.read_json(path).get('items',[]) if path.exists() else []
    used=[]
    for context in contexts:
        if not se.proof_flags(context['excerpt']):continue
        matches=[x for x in reviewed if x.get('candidate_number')==number and x.get('context_excerpt_sha256')==gate.digest(context['excerpt'])]
        if len(matches)!=1:raise ValueError('unreviewed or changed context omission: '+context['file']+':'+str(context['start_line']))
        checked=context['excerpt']
        for review in matches[0].get('reviews',[]):
            phrase=review.get('exact_phrase','');pos=checked.find(phrase)
            original_pos=context['excerpt'].find(phrase)
            first=context['start_line']+context['excerpt'].count('\n',0,original_pos)
            locator={'file':context['file'],'lines':[first,first+phrase.count('\n')]}
            if (not phrase or checked.count(phrase)!=1 or review.get('decision')!='accepted_as_bounded_noncore_omission'
                    or review.get('source_locator')!=locator or not review.get('scope') or not review.get('why_noncore')):
                raise ValueError('invalid bounded context omission review')
            checked=checked.replace(phrase,'[reviewed noncore detail]',1)
        if se.proof_flags(checked):raise ValueError('uncovered omission in retained author context')
        used.append(matches[0])
    return used

def tag_for(source, name):
    return name if name in source.tags else source.by_label[name]

def full_context(source, name):
    """Keep a specifically requested entire author lemma/proof, without rewriting."""
    tag=tag_for(source,name); record=source.block(tag,False)
    text, blocks=source.chapter(record['chapter'])
    start=record['start_line']; statement_end=record['end_line']
    # Locate by source line, not a text-search across similar statements.
    after=[b for b in blocks if text.count('\n',0,b[0])+1 > statement_end]
    if not after or after[0][2]!='proof':
        raise ValueError('required core has no directly identified author proof: '+name)
    statement_block=next(b for b in blocks if b[2]==record['kind'] and text.count('\n',0,b[0])+1==start)
    gap=se.clean(text[statement_block[1]:after[0][0]])
    gap=re.sub(r'\\begin\{(?:reference|history|slogan)\}.*?\\end\{(?:reference|history|slogan)\}','',gap,flags=re.S)
    if gap.strip():raise ValueError('required core proof pairing needs explicit review: '+name)
    end=after[0][1]
    for b in after[1:]:
        if b[2]!='proof' or se.clean(text[end:b[0]]).strip(): break
        end=b[1]
    return source.span(dict(file=record['file'],start_line=start,
        end_line=text.count('\n',0,end-1)+1,reason='Complete necessary source-local core: '+name))

def unique_contexts(contexts):
    """Repeated labels/overlapping chunks must not duplicate the delivered body."""
    result=[]
    for c in contexts:
        if any(c['file']==b['file'] and b['start_line']<=c['start_line'] and c['end_line']<=b['end_line'] for b in result): continue
        result=[b for b in result if not (b['file']==c['file'] and c['start_line']<=b['start_line'] and b['end_line']<=c['end_line'])]
        if any(c['file']==b['file'] and max(c['start_line'],b['start_line'])<=min(c['end_line'],b['end_line']) for b in result):
            raise ValueError('partially overlapping authored contexts require an explicit bounded span')
        result.append(c)
    return result

def review_omissions(source, tag, candidate_number):
    chapter,_=source.tags[tag]; text,_=source.chapter(chapter); reviews=[]
    for phrase,scope,why in OMISSIONS.get(candidate_number,[]):
        record=source.block(tag,False)
        # Restrict locator lookup to the candidate proof region; block later
        # verifies that each short phrase is unique within its author proof.
        start=text.find(record['statement'])+len(record['statement'])
        pos=text.find(phrase,start)
        if pos<0: raise ValueError('reviewed omission phrase changed')
        line=text.count('\n',0,pos)+1
        reviews.append(dict(exact_phrase=phrase,scope=scope,why_noncore=why,
            source_locator=dict(file=chapter+'.tex',lines=[line,line+phrase.count('\n')])))
    return reviews or None

def extraction(source,c):
    n=c['candidate_number']; tag=tag_for(source,Path(c['source_file']).stem+'-'+c['primary_label'])
    omitted=review_omissions(source,tag,n)
    try:record=source.block(tag,omitted_detail_review=omitted)
    except ValueError as exc:
        if n!=20 or str(exc)!='nonadjacent proof '+tag:raise
        # This exact interposed prose discusses an optional stronger claim; it
        # contains no second proposition. The following proof explicitly starts
        # with the two minimal models in the selected lemma. Retain the prose.
        record=source.block(tag,False);text,_=source.chapter(record['chapter'])
        a,b=c['source_match']['proof_actual_lines'];lines=text.splitlines(keepends=True)
        gap=''.join(lines[record['end_line']:a-1]).strip()
        if gap!=NONADJACENT_20:raise ValueError('P20 explicitly reviewed pairing gap changed')
        proof=''.join(lines[a-1:b]).rstrip('\n');checked=proof
        if not proof.startswith(r'\begin{proof}') or not proof.endswith(r'\end{proof}'):
            raise ValueError('P20 declared proof boundaries changed')
        for review in omitted or []:
            phrase=review['exact_phrase'];pos=proof.find(phrase)
            actual=a+proof.count('\n',0,pos)
            if proof.count(phrase)!=1 or review['source_locator']!={'file':record['file'],'lines':[actual,actual+phrase.count('\n')]}:
                raise ValueError('P20 bounded omission locator changed')
            checked=checked.replace(phrase,'[reviewed optional noncore detail]',1)
        if se.proof_flags(checked):raise ValueError('P20 unreviewed omission remains')
        record.update(proof=proof,end_line=b,excerpt=''.join(lines[record['start_line']-1:b]).rstrip('\n'))
        record['pairing_review']='Exact optional-stronger-claim prose retained; no intervening statement; proof starts with the selected minimal models.'
    contexts=[source.span(dict(file=file,start_line=a,end_line=b,reason=reason)) for file,a,b,reason in SPANS.get(n,[])]
    for name in CONTEXT.get(n,[]):
        contexts.append(full_context(source,name[:-1]) if name.endswith('+') else source.context(tag_for(source,name)))
    # Definition/situation closure only. It never recursively adds lemma proofs.
    for _ in range(8):
        contexts=unique_contexts(contexts)
        included={b['chapter']+'-'+l for b in contexts+[record] for l in se.LABEL.findall(se.clean(b['excerpt']))}
        missing=[]
        for block in contexts+[record]:
            for _,label in se.REF.findall(se.clean(block['excerpt'])):
                full=label if label in source.by_label else block['chapter']+'-'+label
                t=source.by_label.get(full)
                if t and source.tags[t][1].startswith(('definition-','situation-')) and full not in included:
                    missing.append(t)
        if not missing:break
        contexts += [source.context(t) for t in dict.fromkeys(missing)]
    else:raise ValueError('definition closure exceeds bounded eight rounds')
    record['contexts']=unique_contexts(contexts)
    if sum(len(x['excerpt'].splitlines()) for x in record['contexts'])>2500:
        raise ValueError('source-local core exceeds bounded pilot context budget (2500 lines); manual narrower review required')
    return record,omitted

def evidence_project(work, source):
    """The existing evidence helper expects this read-only project layout."""
    project=work/'pilot-evidence-project'; scripts=project/'scripts';scripts.mkdir(parents=True,exist_ok=True)
    shutil.copy2(Path(se.__file__),scripts/'stacks_extract.py')
    link=project/'corpus/raw/stacks-project';link.parent.mkdir(parents=True,exist_ok=True)
    if link.exists():
        if link.resolve()!=source.resolve():raise ValueError('existing evidence source junction points elsewhere')
    elif os.name=='nt':
        subprocess.run(['cmd','/c','mklink','/J',str(link),str(source)],check=True,capture_output=True)
    else:link.symlink_to(source,target_is_directory=True)
    return project

def assemble(repo,work,out,source,c,project,engine):
    n=c['candidate_number'];ident=str(97000000+n); result=dict(candidate_number=n,research_id=c['research_id'],temporary_problem_id=ident,production_admitted=False)
    if n in HOLDS:
        result.update(status='hold',reason=HOLDS[n]);return result
    record,omitted=extraction(source,c)
    context_reviews=check_context_reviews(out,n,record['contexts'])
    # Never substitute a different version's proof for the already read unit.
    retained=material_path(repo,c).read_text(encoding='utf-8-sig')
    statement=re.search(r'(\\begin\{(lemma|theorem|proposition)\}.*?\\end\{\2\})',retained,re.S)[1]
    proof=re.search(r'(\\begin\{proof\}.*?\\end\{proof\})',retained,re.S)[1]
    if statement!=record['statement'] or proof not in record['proof']:
        raise ValueError('candidate and selected complete source snapshot differ')
    package=out/'packages'/ident;package.mkdir(parents=True,exist_ok=True)
    spec=dict(title=c['title_zh'],difficulty_level=c['proposed_difficulty_level'],difficulty_reason=c['difficulty_reason'],source_version=VERSION)
    tex=se.render(source,record,spec)
    fontset='windows' if os.name=='nt' else 'fandol'
    geometry='a4paper,left=24mm,right=24mm,top=20mm,bottom=20mm' if n==8 else 'a4paper,margin=24mm'
    tex=tex.replace(r'\documentclass{amsart}',r'\documentclass{amsart}'+'\n'+r'\usepackage[UTF8,fontset='+fontset+r']{ctex}'+'\n'+r'\usepackage['+geometry+r']{geometry}',1)
    tex=tex.replace(r'\begin{document}',r'\hypersetup{hidelinks}'+'\n'+r'\widowpenalty=10000\clubpenalty=10000\displaywidowpenalty=10000'+'\n'+r'\begin{document}',1)
    tex=tex.replace(r'\maketitle',r'\maketitle'+'\n'+r'\noindent\textbf{Counting scope.} The primary problem is Tag '+se.escape(record['tag'])+r', marked below. All preceding numbered statements are supporting author context and are not counted as additional problems. This is a local pilot with a temporary ID, not production admission.'+'\n\n',1)
    marker=re.search(r'\\begin\{(?:lemma|theorem|proposition)\}(?:\[[^\]]*\])?\s*\\label\{'+re.escape(record['label'])+r'\}',tex)
    if not marker:raise ValueError('primary body marker not unique or missing')
    tex=tex[:marker.start()]+r'\section*{Primary problem: Tag '+se.escape(record['tag'])+'}\n'+tex[marker.start():]
    if n in EDITORIAL:
        tex=tex.replace(r'\maketitle',r'\maketitle'+'\n'+r'\noindent\textbf{Editorial reading note.} '+se.escape(EDITORIAL[n])+'\n\n',1)
    item_path='items/'+ident+'_stacks_'+record['tag']+'.tex';item=package/item_path;item.parent.mkdir(parents=True,exist_ok=True);item.write_text(tex,encoding='utf-8',newline='\n')
    declarations=[]
    for i,b in enumerate(record['contexts']+[record]):
        relative='sources/'+ident+('/primary.excerpt.tex' if b is record else '/context-'+str(i+1)+'.tex')
        ep=package/relative;ep.parent.mkdir(parents=True,exist_ok=True);ep.write_text(b['excerpt'],encoding='utf-8',newline='\n')
        declarations.append(dict(source_file=b['file'],source_sha256=b['source_sha256'],start_line=b['start_line'],end_line=b['end_line'],excerpt_path=relative,excerpt_sha256=gate.digest(b['excerpt']),tag_url='https://stacks.math.columbia.edu/tag/'+b['tag'] if not b['tag'].startswith('span-') else 'https://stacks.math.columbia.edu/'))
    now=dt.datetime.now(dt.timezone.utc).isoformat()
    row=dict(problem_id=ident,title=c['title_zh'],item_path=item_path,author='The Stacks Project Authors',work='The Stacks Project',
        source_id='stacks-project:'+record['file']+'@local-'+record['source_sha256'],source_url='https://stacks.math.columbia.edu/tag/'+record['tag'],source_version=VERSION,retrieved_at=now,
        primary=declarations[-1],contexts=declarations[:-1],external_prerequisite_references=sorted({'https://stacks.math.columbia.edu/tag/'+tag_for(source,x['target_source_file'][:-4]+'-'+x['target_label']) for x in c['reference_locations'] if x['status']=='located'}),
        license='GNU FDL 1.2 or later',license_path='licenses/COPYING',difficulty_level=c['proposed_difficulty_level'],difficulty_reason=c['difficulty_reason'],
        status='pending',origin_class='human_authored_native_tex',tex_sha256=gate.digest(tex),compile_receipt='receipts/'+ident+'.json',
        source_check=dict(checked_at=now,checks=['full primary statement and adjacent/continued author proof boundaries','exact rendered author bodies after reference-only adaptation','required context/macros and stable referenced prerequisites'],
        note='Local pilot source comparison of the full author statement/proof and explicitly attached definitions/core. Upstream revision unknown; exact original chapter hashes retained. Root production admission and semantic uniqueness are separate.',omitted_detail_reviews=omitted or []))
    (package/'licenses').mkdir(exist_ok=True);shutil.copy2(source.root/'COPYING',package/'licenses/COPYING')
    dump(package/'sources'/ident/'provenance.json',row)
    dump(package/'manifest.json',package_manifest(row,'pending'))
    dump(package/'gate-result.json',dict(schema_version=1,mode='assembly-pending',editable_qualified_count=0,items={},errors=['assembly pending; final item gate not yet run']))
    (package/'INDEX.md').write_text('| ID | Title | H | TeX | Source |\n|---|---|---|---|---|\n| '+ident+' | '+row['title']+' | '+row['difficulty_level']+' | [TeX]('+item_path+') | [Tag]('+row['source_url']+') [Provenance](sources/'+ident+'/provenance.json) |\n',encoding='utf-8',newline='\n')
    shutil.copy2(repo/'editable-corpus/schema.sql',package/'schema.sql')
    build=work/'pilot-build';receipts=work/'pilot-receipts';build.mkdir(exist_ok=True);receipts.mkdir(exist_ok=True)
    rc=compiler.compile_item(package.resolve(),row,build.resolve(),str(engine),240);dump(receipts/(ident+'.json'),rc)
    result.update(package=str(package),omitted_detail_reviews=omitted or [],context_omission_reviews=context_reviews,context_count=len(record['contexts']),compile=rc)
    if not rc['ok']:
        result.update(status='hold',reason='compile: '+rc.get('error','unknown'));return result
    dump(package/row['compile_receipt'],rc)
    (package/'pdf').mkdir(exist_ok=True);shutil.copy2(build/rc['pdf_path'],package/'pdf'/(ident+'.pdf'))
    result['pdf']=str(package/'pdf'/(ident+'.pdf'))
    # The published pilot directory remains pending/0 while the existing gate
    # evaluates a fresh external staging view with its required final schema.
    stage_root=work/'pilot-gate-stage';stage_root.mkdir(exist_ok=True)
    stage=Path(tempfile.mkdtemp(prefix=ident+'-',dir=stage_root))
    shutil.copytree(package,stage,dirs_exist_ok=True)
    row['status']='verified_editable_tex'
    dump(stage/'sources'/ident/'provenance.json',row)
    dump(stage/'manifest.json',package_manifest(row,'verified_editable_tex'))
    ev=evidence.derive(stage,project);dump(stage/'delivery-evidence.json',ev)
    if ev['derivation_holds']:raise ValueError('exact body evidence: '+str(ev['derivation_holds']))
    rebuild_db(repo,stage)
    report=gate.validate(stage,item=ident,build_root=build,receipt_root=receipts);dump(package/'gate-result.json',report)
    result['gate']=report
    if report['editable_qualified_count']!=1 or report['errors']:
        result.update(status='hold',reason='existing item gate failed');return result
    for relative in ('manifest.json','delivery-evidence.json','corpus.sqlite','rebuild_database.py','sources/'+ident+'/provenance.json'):
        shutil.copy2(stage/relative,package/relative)
    result.update(status='local_item_gate_passed',pdf=str(package/'pdf'/(ident+'.pdf')))
    return result

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--work',type=Path,required=True);ap.add_argument('--only',type=int,nargs='*');ap.add_argument('--engine',help='Explicit existing compiler driver; defaults to the platform latexmk driver');args=ap.parse_args()
    repo=Path(__file__).resolve().parents[2];out=repo/'research-line/pilot-20261010';work=args.work.resolve();work.mkdir(parents=True,exist_ok=True)
    if work.is_relative_to(repo):raise ValueError('build/receipt work must remain outside repository')
    candidates=json.loads((out/'CANDIDATES.json').read_text(encoding='utf-8-sig'))['candidates']
    mainids={str(x['problem_id']) for x in json.loads((repo/'editable-corpus/manifest.json').read_text(encoding='utf-8-sig'))['items']}
    if mainids & {str(97000000+x['candidate_number']) for x in candidates}:raise ValueError('temporary ID collides with main')
    queue=repo/'handoff/yupeng/PRODUCTION_QUEUE.json'
    if queue.exists() and any(re.search(r'(?<!\d)'+str(97000000+x['candidate_number'])+r'(?!\d)',queue.read_text(encoding='utf-8-sig')) for x in candidates):raise ValueError('temporary ID collides with local queue snapshot')
    source=se.StacksSource(args.source.resolve());project=evidence_project(work,args.source.resolve())
    engine=args.engine or str(repo/'corpus-work/scripts'/('latexmk_xelatex.cmd' if os.name=='nt' else 'latexmk_xelatex.sh'))
    if os.name=='nt' and Path(r'F:\texlive\2025\bin\windows').is_dir():
        os.environ['PATH']=r'F:\texlive\2025\bin\windows'+os.pathsep+os.environ.get('PATH','')
    previous=out/'ASSEMBLY_REPORT.json';results={x['candidate_number']:x for x in json.loads(previous.read_text(encoding='utf-8'))['items']} if previous.exists() else {}
    for c in candidates:
        if args.only and c['candidate_number'] not in args.only:continue
        try:result=assemble(repo,work,out,source,c,project,engine)
        except (OSError,ValueError,KeyError,TypeError,StopIteration,subprocess.SubprocessError) as exc:
            result=dict(candidate_number=c['candidate_number'],research_id=c['research_id'],temporary_problem_id=str(97000000+c['candidate_number']),status='hold',reason=str(exc),production_admitted=False)
        package=out/'packages'/str(97000000+c['candidate_number'])
        if result['status']=='hold' and package.exists():fail_package(repo,package,result['reason'])
        results[c['candidate_number']]=result
        dump(previous,dict(scope='Local pilot, no main count or remote mutation',source_version=VERSION,items=[results[k] for k in sorted(results)]))
        print(json.dumps({k:result.get(k) for k in ('candidate_number','status','reason','pdf')},ensure_ascii=False),flush=True)

if __name__=='__main__':main()
