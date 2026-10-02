"""Derive current body bindings from existing Stacks source-review declarations.

This records existing declarations and byte comparisons, not new mathematical review.
It only writes the requested external sidecar. Unsupported families stay explicit holds.
"""
import argparse
import datetime
import importlib.util
import json
from pathlib import Path
import re
import sys

import editable_delivery as gate


def entry_from_existing(row, sources, bodies, derived_at):
    check = row.get('source_check', {})
    checks = ' '.join(check.get('checks', []))
    if not check.get('note') or not ('complete' in checks or 'full primary' in checks or 'full original author body' in checks):
        raise ValueError('existing bounded author-completeness declaration absent')
    return dict(item_sha256=row['tex_sha256'], claim_key=row['source_id'] + ':' + json.dumps(row['primary'], sort_keys=True),
                independent_problem_unit=True, sources=sources, bodies=bodies,
                source_check=dict(checked_at=check.get('checked_at', derived_at),
                                  method='existing-declaration-plus-current-source-map-byte-binding',
                                  note=check['note'] + ' Current derivation binds bytes only; it is not a new source or mathematical review.',
                                  complete_statement=True, complete_proof=True, required_context_preserved=True,
                                  above_ordinary_phd_quals=True, source_authorship='named-human-author',
                                  declaration_basis=dict(existing_source_check=check,
                                                         difficulty_level=row['difficulty_level'],
                                                         difficulty_reason=row['difficulty_reason'])))


def derive_mapped(package, row, project, derived_at):
    """Supported portable native excerpts with explicit original-line maps only."""
    mapping_path = row['primary'].get('source_map_path')
    mapping = gate.read_json(gate.local(package, mapping_path))
    excerpt_path = 'sources/' + row['problem_id'] + '/author-excerpts.tex'
    if not (package/excerpt_path).is_file():
        if isinstance(mapping.get('author_text_units'),list):
            stage=project/'candidates/tex-proof-remediation-afst'/row['problem_id']
            qa=gate.read_json(stage/'pilot-source-and-render-qa.json')
            candidate=stage/(row['problem_id']+'_full_human_proof.tex')
            return derive_reviewed_transcription(package,row,mapping,qa,candidate.read_bytes().decode('utf-8'),str(candidate.relative_to(project)),derived_at)
        return derive_page_map(package,row,mapping,derived_at)
    excerpt = gate.local(package, excerpt_path).read_text(encoding='utf-8')
    original_hash = mapping.get('source_tex_sha256')
    if original_hash != row['primary'].get('source_tex_sha256') or not gate.HASH.fullmatch(str(original_hash)):
        raise ValueError('native source-map hash provenance mismatch')
    delivered = gate.local(package, row['item_path']).read_text(encoding='utf-8')
    excerpt_lines = excerpt.splitlines()
    blocks = mapping.get('blocks')
    if not isinstance(blocks, list) or not blocks:
        raise ValueError('unsupported native source-map schema')
    offsets = []
    sources = [dict(root='package', path=excerpt_path, sha256=gate.digest(excerpt),
                    original_source_sha256=original_hash, original_locator={'source_map':mapping_path})]
    bodies = []
    for block in blocks:
        a, b = block['source_lines']
        marker = '% Original source lines ' + str(a) + '--' + str(b)
        places = [i for i, line in enumerate(excerpt_lines) if line == marker]
        if len(places) != 1:
            raise ValueError('native block marker absent or duplicate')
        first = places[0] + 2
        interval = [first, first + b - a]
        original = gate.lines(excerpt, interval)
        if gate.digest(original + '\n') != block.get('content_sha256_lf'):
            raise ValueError('source-map native block hash mismatch')
        adapted=original;replacements=[]
        for image in re.finditer(r'(\\includegraphics(?:\[[^]]*\])?)\{([^{}]+)\}',original):
            possible=[a for a in row.get('asset_dependencies',[]) if Path(a['path']).name==Path(image[2]).name]
            if len(possible)!=1:
                raise ValueError('native figure path does not identify one declared original asset')
            name='../'+possible[0]['path'];new=image[1]+'{'+name+'}'
            adapted=adapted.replace(image[0],new);replacements.append(dict(original=image[0],delivered=new))
        position = delivered.find(adapted)
        if position < 0 or delivered.find(adapted, position + 1) >= 0:
            raise ValueError('full mapped author block absent or nonunique in delivered TeX')
        delivered_first = delivered.count('\n', 0, position) + 1
        offsets.append((a,b,first,delivered_first))
        body_interval = [delivered_first,delivered_first+b-a]
        bodies.append(dict(role='context',tex_lines=body_interval,tex_sha256=gate.digest(gate.lines(delivered,body_interval)),
                           source_index=0,source_lines=interval,method='literal_asset_path_adaptation' if replacements else 'exact_tex',
                           replacements=replacements,source_excerpt_path=excerpt_path))
    primary = []
    for role, field in [('primary_statement','statement_source_lines'),('primary_proof','proof_source_lines')]:
        ranges = mapping.get(field)
        if not isinstance(ranges,list) or not ranges:
            raise ValueError('primary original range mapping missing: ' + role)
        # Nonconsecutive selected ranges need a family-specific receipt; never fill gaps by guessing.
        if len(ranges) != 1:
            raise ValueError('unsupported nonconsecutive primary range schema: ' + role)
        a,b = ranges[0]
        match = next((entry for entry in offsets if entry[0] <= a <= b <= entry[1]), None)
        if match is None:
            raise ValueError('selected primary range is outside retained exact source blocks')
        source_interval = [match[2]+a-match[0], match[2]+b-match[0]]
        target_interval = [match[3]+a-match[0], match[3]+b-match[0]]
        primary.append(dict(role=role, tex_lines=target_interval,tex_sha256=gate.digest(gate.lines(delivered,target_interval)),
                            source_index=0,source_lines=source_interval,method='exact_tex',source_excerpt_path=excerpt_path))
    return entry_from_existing(row,sources,primary+bodies,derived_at)


def derive_page_map(package,row,mapping,derived_at):
    """Adapt retained full-block hashes, never infer a proof from a theorem name."""
    map_path = row['primary']['source_map_path']
    if isinstance(mapping.get('author_page_tex_line_spans'),list):
        return derive_retained_page_excerpts(package,row,mapping,derived_at)
    map_hash = gate.digest(gate.local(package,map_path).read_bytes())
    original_hash = mapping.get('source_sha256')
    if original_hash != row['primary'].get('source_sha256') or not gate.HASH.fullmatch(str(original_hash)):
        raise ValueError('unsupported page-map original hash schema')
    delivered = gate.local(package,row['item_path']).read_text(encoding='utf-8')
    entries = []
    if isinstance(mapping.get('blocks'),list):
        for block in mapping['blocks']:
            if block.get('source_language_and_mathematical_order_preserved') is not True or not block.get('fresh_source_boundary_comparison'):
                raise ValueError('page-map block lacks existing bounded original comparison')
            entries.append(dict(interval=[block['tex_first_line'],block['tex_last_line']],
                                sha256=block['tex_block_sha256'],block_id=block['block_id']))
    elif isinstance(mapping.get('page_map'),list):
        for block in mapping['page_map']:
            entries.append(dict(interval=block['native_tex_lines'],sha256=block['transcribed_block_sha256'],
                                page=block['original_physical_page']))
    elif isinstance(mapping.get('pages'),list):
        for block in mapping['pages']:
            entries.append(dict(interval=block['tex_line_range_1based'],sha256=block['tex_span_sha256'],
                                page=block['physical_source_page']))
    else:
        raise ValueError('unsupported page-map block schema; explicit current body hashes needed')
    if not entries:
        raise ValueError('page-map has no retained author blocks')
    for entry in entries:
        if gate.digest(gate.lines(delivered,entry['interval'])+'\n') != entry['sha256']:
            raise ValueError('published author block differs from retained source-map hash')
    sources=[dict(root='package',path=map_path,sha256=map_hash,original_source_sha256=original_hash,
                  kind='retained-original-source-page-fidelity-map')]
    bodies=[]
    def body(role,selected):
        if not selected:
            raise ValueError('selected original primary source pages not covered: '+role)
        interval=[min(x['interval'][0] for x in selected),max(x['interval'][1] for x in selected)]
        content_hash=gate.digest(gate.lines(delivered,interval))
        locator=dict(original_source_sha256=original_hash,source_map_path=map_path,
                     retained_blocks=[x for x in selected])
        receipt=dict(schema_version=1,checked=True,item_sha256=row['tex_sha256'],body_sha256=content_hash,
                     source_sha256=map_hash,role=role,checked_at=derived_at,
                     method='existing-source-page-fidelity-map-current-byte-binding',source_locator=locator,
                     note='Retained original bounded source comparison and per-block hashes rebound to unchanged delivered author bytes; no new source review.')
        return dict(role=role,tex_lines=interval,tex_sha256=content_hash,source_index=0,
                    method='bounded_source_comparison',fidelity_receipt=receipt)
    for role,prefix,field in [('primary_statement','T','statement_pages'),('primary_proof','P','proof_pages')]:
        if 'block_id' in entries[0]:
            selected=[x for x in entries if x['block_id'].startswith(prefix)]
        else:
            pages=row['primary'].get(field,row['primary'].get('proof_and_core_support_pages',[]))
            selected=[x for x in entries if x['page'] in pages]
            if set(pages) != {x['page'] for x in selected}:
                raise ValueError('primary page locator not covered by source-map')
        bodies.append(body(role,selected))
    bodies.extend(body('context',[entry]) for entry in entries)
    return entry_from_existing(row,sources,bodies,derived_at)


def derive_retained_page_excerpts(package,row,mapping,derived_at):
    if mapping.get('source_sha256')!=row['primary'].get('source_sha256'):
        raise ValueError('retained page excerpt original provenance mismatch')
    text=gate.local(package,row['item_path']).read_bytes().decode('utf-8')
    sources=[];contexts=[];entries=[];by_path={}
    for block in mapping['author_page_tex_line_spans']:
        path=block['tex_path'];raw=gate.local(package,path).read_bytes();original_text=raw.decode('utf-8')
        source_interval=[block['start_line'],block['end_line']];original=gate.lines(original_text,source_interval)
        if gate.digest(original+'\n')!=block['excerpt_sha256']:
            raise ValueError('retained author page excerpt hash differs')
        if path not in by_path:
            by_path[path]=len(sources);sources.append(dict(root='package',path=path,sha256=gate.digest(raw),original_source_sha256=mapping['source_sha256']))
        index=by_path[path];adapted=original;replacements=[]
        for image in re.finditer(r'(\\includegraphics(?:\[[^]]*\])?)\{([^{}]+)\}',original):
            assets=[a for a in row.get('asset_dependencies',[]) if Path(a['path']).name==Path(image[2]).name]
            if len(assets)!=1:raise ValueError('retained page figure not uniquely declared')
            new=image[1]+'{../'+assets[0]['path']+'}';adapted=adapted.replace(image[0],new);replacements.append(dict(original=image[0],delivered=new))
        start=text.find(adapted)
        if start<0 or text.find(adapted,start+1)>=0:raise ValueError('complete retained original page absent or nonunique')
        first=text.count('\n',0,start)+1;interval=[first,first+len(adapted.splitlines())-1]
        try:page=int(block['source_page'])
        except ValueError:page=None
        entries.append(dict(page=page,source_index=index,source_interval=source_interval,interval=interval))
        contexts.append(dict(role='context',tex_lines=interval,tex_sha256=gate.digest(gate.lines(text,interval)),source_index=index,
                             source_lines=source_interval,method='literal_asset_path_adaptation' if replacements else 'exact_tex',replacements=replacements))
    primary=[]
    for role,field in [('primary_statement','statement_pages'),('primary_proof','proof_pages')]:
        pages=row['primary'][field];selected=[x for x in entries if x['page'] in pages]
        if set(pages)!={x['page'] for x in selected}:raise ValueError('primary source pages not covered by retained excerpts')
        interval=[min(x['interval'][0] for x in selected),max(x['interval'][1] for x in selected)]
        source_interval=[min(x['source_interval'][0] for x in selected),max(x['source_interval'][1] for x in selected)]
        if len({x['source_index'] for x in selected})!=1:raise ValueError('nonconsecutive primary source excerpt files need explicit mapping')
        index=selected[0]['source_index'];h=gate.digest(gate.lines(text,interval))
        primary.append(dict(role=role,tex_lines=interval,tex_sha256=h,source_index=index,source_lines=source_interval,method='exact_tex'))
    return entry_from_existing(row,sources,primary+contexts,derived_at)


def derive_reviewed_transcription(package,row,mapping,qa,candidate,source_name,derived_at):
    original_hash=row['primary'].get('source_sha256')
    if (mapping.get('original_sha256')!=original_hash or qa.get('source_sha256')!=original_hash or
            gate.digest(candidate)!=qa.get('tex_sha256') or qa.get('full_editable_statement_and_author_proof') is not True or
            qa.get('source_formulas_and_arrows_compared') is not True or not qa.get('comparison_method')):
        raise ValueError('existing original-source/transcription QA is missing or stale')
    theorem=''.join(row['primary'].get('source_locator',{}).get('theorem','').split())
    if theorem not in [''.join(v.split()) for v in qa.get('authored_proofs_complete',[])]:
        raise ValueError('existing QA does not declare the selected authored proof complete')
    text=gate.local(package,row['item_path']).read_bytes().decode('utf-8')
    sources=[];contexts=[];entries=[]
    for unit in mapping['author_text_units']:
        interval=[unit['tex_line_start'],unit['tex_line_end']];raw=gate.lines(candidate,interval)+'\n'
        start=text.find(raw.rstrip('\n'))
        if start<0 or text.find(raw.rstrip('\n'),start+1)>=0:
            raise ValueError('existing fully reviewed author unit is absent or nonunique in publication')
        first=text.count('\n',0,start)+1;target=[first,first+len(raw.splitlines())-1]
        index=len(sources)
        sources.append(dict(root='inline',inline_text=raw,sha256=gate.digest(raw),original_source_sha256=qa['tex_sha256'],
                            kind='preserved-checked-transcription-of-original-human-source',
                            original_locator=dict(source_file=source_name,source_version=row['source_version'],lines=interval,
                                                  original_pdf_sha256=original_hash,physical_source_pages=unit['physical_pages'],
                                                  existing_qa=qa)))
        body=dict(role='context',tex_lines=target,tex_sha256=gate.digest(gate.lines(text,target)),source_index=index,
                  source_lines=[1,len(raw.splitlines())],method='exact_tex')
        contexts.append(body);entries.append((unit,body))
    statement=[v for v in entries if set(v[0]['physical_pages']).intersection(row['primary']['statement_pages'])]
    proofs=[v for v in entries if 'Proofof'+theorem in ''.join(v[0]['unit'].split())]
    if len(statement)!=1 or len(proofs)!=1:
        raise ValueError('existing reviewed units lack unambiguous selected statement/proof boundaries')
    primary=[statement[0][1]|{'role':'primary_statement'},proofs[0][1]|{'role':'primary_proof'}]
    return entry_from_existing(row,sources,primary+contexts,derived_at)


def derive_existing_bindings(package,row,record,derived_at):
    """Rebind preserved deterministic source-worker evidence without re-reviewing math."""
    if record.get('problem_id') != row['problem_id'] or record.get('delivered_tex_sha256') != row['tex_sha256']:
        raise ValueError('existing fidelity binding is stale or belongs to a different item')
    text=gate.local(package,row['item_path']).read_bytes().decode('utf-8')
    declarations=gate.source_declarations(row)
    sources=[];contexts=[];matched=[]
    for binding in record.get('bindings',[]):
        possible=[d for d in declarations if Path(d['excerpt_path']).name==Path(binding['original_excerpt']).name and d['excerpt_sha256']==binding['original_sha256']]
        if len(possible)!=1:
            raise ValueError('existing binding does not identify a unique retained source excerpt')
        declaration=possible[0];path=declaration['excerpt_path'];raw=gate.local(package,path).read_bytes()
        if gate.digest(raw)!=binding['original_sha256']:
            raise ValueError('retained original excerpt hash changed')
        interval=[binding['delivered_start_line'],binding['delivered_end_line']]
        content=gate.lines(text,interval)
        if binding.get('verified_contiguous_substring') is not True or gate.digest(content+'\n')!=binding.get('deterministic_adapted_excerpt_sha256'):
            raise ValueError('delivered original-author span differs from existing deterministic binding')
        sources.append(dict(root='package',path=path,sha256=binding['original_sha256'],original_source_sha256=declaration['source_sha256']))
        matched.append((binding,declaration,len(sources)-1))
        def make(role,target,b=binding,source_index=len(sources)-1,p=path):
            h=gate.digest(gate.lines(text,target))
            receipt=dict(schema_version=1,checked=True,item_sha256=row['tex_sha256'],body_sha256=h,
                         source_sha256=b['original_sha256'],role=role,checked_at=derived_at,
                         method='existing-deterministic-source-excerpt-binding',source_locator=b,
                         note=record.get('derivation','Existing source-worker bounded fidelity record.')+' No new source review.')
            return dict(role=role,tex_lines=target,tex_sha256=h,source_index=source_index,
                        source_excerpt_path=p,method='bounded_source_comparison',fidelity_receipt=receipt)
        contexts.append(make('context',interval))
    if len(matched)!=len(declarations):
        raise ValueError('required retained excerpt lacks an existing delivered fidelity binding')
    locator=row['primary'].get('primary_locator')
    primary=[]
    if isinstance(locator,dict):
        for role,key in [('primary_statement','statement'),('primary_proof','proof')]:
            selected=locator.get(key)
            ranges=[selected] if selected else locator.get('continued_primary_proof',[]) if role=='primary_proof' else []
            targets=[]
            source_index=None
            for a,b in ranges:
                match=next((v for v in matched if v[0].get('source_start_line') is not None and v[0]['source_start_line']<=a<=b<=v[0]['source_end_line']),None)
                if match is None:
                    raise ValueError('selected primary locator not covered by existing source binding')
                binding,declaration,source_index=match
                if binding['delivered_end_line']-binding['delivered_start_line'] != binding['source_end_line']-binding['source_start_line']:
                    raise ValueError('selected primary mapping changes line cardinality; explicit mapped primary needed')
                targets.append([binding['delivered_start_line']+a-binding['source_start_line'],binding['delivered_start_line']+b-binding['source_start_line']])
            if not targets:
                raise ValueError('selected primary locator missing')
            target=[min(x[0] for x in targets),max(x[1] for x in targets)]
            binding,declaration,index=matched[source_index]
            h=gate.digest(gate.lines(text,target))
            receipt=dict(schema_version=1,checked=True,item_sha256=row['tex_sha256'],body_sha256=h,
                         source_sha256=binding['original_sha256'],role=role,checked_at=derived_at,
                         method='existing-deterministic-source-excerpt-primary-locator',source_locator={'primary':locator,'binding':binding},
                         note=record['derivation']+' Current byte binding only; no new source review.')
            primary.append(dict(role=role,tex_lines=target,tex_sha256=h,source_index=index,method='bounded_source_comparison',fidelity_receipt=receipt))
    else:
        match=next((v for v in matched if v[1] is row['primary']),None)
        if match is None:
            raise ValueError('primary excerpt binding missing')
        binding,declaration,index=match
        first,last=binding['delivered_start_line'],binding['delivered_end_line']
        span=gate.lines(text,[first,last])
        proof=re.search(r'\\begin\{proof\}',span)
        ends=list(re.finditer(r'\\end\{proof\}',span))
        if proof is None or not ends:
            raise ValueError('primary split boundaries absent; preserve narrative organization with explicit locator')
        proof_first=first+span.count('\n',0,proof.start())
        proof_last=first+span.count('\n',0,ends[-1].end()-1)
        for role,target in [('primary_statement',[first,proof_first-1]),('primary_proof',[proof_first,proof_last])]:
            h=gate.digest(gate.lines(text,target))
            receipt=dict(schema_version=1,checked=True,item_sha256=row['tex_sha256'],body_sha256=h,
                         source_sha256=binding['original_sha256'],role=role,checked_at=derived_at,
                         method='existing-deterministic-source-excerpt-binding',source_locator=binding,
                         note=record['derivation']+' Current byte binding of preserved statement/proof; no new source review.')
            primary.append(dict(role=role,tex_lines=target,tex_sha256=h,source_index=index,method='bounded_source_comparison',fidelity_receipt=receipt))
    return entry_from_existing(row,sources,primary+contexts,derived_at)


def derive_native_worker_binding(package,row,record,project,derived_at):
    if record.get('id')!=row['problem_id'] or record.get('delivered_input_sha256')!=row['tex_sha256']:
        raise ValueError('native worker binding has stale delivered input')
    native=gate.local(project,record['native_source']).read_bytes()
    if gate.digest(native)!=record.get('native_source_sha256'):
        raise ValueError('worker-verified native source bytes changed')
    native_text=native.decode('utf-8');text=gate.local(package,row['item_path']).read_bytes().decode('utf-8')
    sources=[];bodies=[]
    statement_roles={'primary_statement','selected_statement_clause_c','selected_statement_part_2'}
    proof_roles={'complete_primary_proof','complete_case_c_proof_with_operator_context','complete_primary_hard_potential_barrier_proof'}
    for binding in record['bindings']:
        original=gate.lines(native_text,binding['native_source_lines_1based'])+'\n'
        interval=binding['delivered_item_lines_1based'];delivered=gate.lines(text,interval)
        if (binding.get('author_math_text_unchanged') is not True or gate.digest(original)!=binding['native_excerpt_sha256'] or
                gate.digest(delivered+'\n')!=binding['delivered_span_sha256']):
            raise ValueError('original or current author-body worker binding differs')
        role='primary_statement' if binding['role'] in statement_roles else 'primary_proof' if binding['role'] in proof_roles else 'context'
        sources.append(dict(root='inline',inline_text=original,sha256=gate.digest(original),original_source_sha256=record['native_source_sha256'],
                            original_locator=dict(source_file=record['native_source'],source_version=row['source_version'],lines=binding['native_source_lines_1based'])))
        body=dict(role=role,tex_lines=interval,tex_sha256=gate.digest(delivered),source_index=len(sources)-1)
        if delivered.strip()==original.strip():
            body.update(method='exact_tex',source_lines=[1,len(original.splitlines())])
        else:
            if binding.get('only_disclosed_figure_includes_changed') is not True:
                raise ValueError('unrecorded native-to-delivered author-body change')
            body.update(method='bounded_source_comparison',fidelity_receipt=dict(schema_version=1,checked=True,
                        item_sha256=row['tex_sha256'],body_sha256=body['tex_sha256'],source_sha256=gate.digest(original),role=role,
                        checked_at=derived_at,method='existing-native-worker-figure-only-binding',source_locator=binding,
                        note=record['scope'],publication_transformations=record.get('publication_transformations',[])))
        bodies.append(body)
    whole=record.get('whole_author_body_binding')
    if whole:
        source_path='sources/'+row['problem_id']+'/original-author-body.tex'
        raw=gate.local(package,source_path).read_bytes()
        interval=whole['delivered_author_body_lines_1based'];content=gate.lines(text,interval)
        if (whole.get('preserved_body_is_byte_exact_native_excerpt') is not True or gate.digest(raw)!=whole['preserved_source_body_sha256'] or
                gate.digest(content+'\n')!=whole['delivered_author_body_sha256']):
            raise ValueError('complete retained native core binding differs')
        sources.append(dict(root='package',path=source_path,sha256=gate.digest(raw),original_source_sha256=record['native_source_sha256']))
        h=gate.digest(content)
        bodies.append(dict(role='context',tex_lines=interval,tex_sha256=h,source_index=len(sources)-1,method='bounded_source_comparison',
                           fidelity_receipt=dict(schema_version=1,checked=True,item_sha256=row['tex_sha256'],body_sha256=h,
                            source_sha256=gate.digest(raw),role='context',checked_at=derived_at,method='existing-full-native-core-and-figure-only-binding',
                            source_locator=whole,note=record['scope'],publication_transformations=record.get('publication_transformations',[]))))
    return entry_from_existing(row,sources,bodies,derived_at)


def derive(package, project, bindings_paths=()):
    spec = importlib.util.spec_from_file_location('source_extractor', project / 'scripts/stacks_extract.py')
    se = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(se)
    source = se.StacksSource(project / 'corpus/raw/stacks-project')
    manifest = gate.read_json(package / 'manifest.json')
    existing_bindings={}
    for path in bindings_paths:
        records=gate.read_json(path)
        if isinstance(records,dict) and isinstance(records.get('items'),list):records=records['items']
        if not isinstance(records,list):raise ValueError('unsupported existing fidelity-bindings schema')
        for record in records:
            ident=record.get('problem_id',record.get('id'))
            if ident in existing_bindings:
                raise ValueError('duplicate existing fidelity binding')
            existing_bindings[ident]=record
    items = {}
    failures = {}
    derived_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    for row in manifest['items']:
        ident = row['problem_id']
        items[ident] = {}
        try:
            if ident in existing_bindings:
                record=existing_bindings[ident]
                items[ident]=derive_native_worker_binding(package,row,record,project,derived_at) if 'native_source' in record else derive_existing_bindings(package,row,record,derived_at)
                continue
            if not row['source_id'].startswith('stacks-project:'):
                items[ident] = derive_mapped(package,row,project,derived_at)
                continue
            check = row.get('source_check', {})
            required_checks = ['full primary statement and adjacent/continued author proof boundaries',
                               'exact rendered author bodies after reference-only adaptation',
                               'required context/macros and stable referenced prerequisites']
            if not gate.dated(check.get('checked_at')) or not all(c in check.get('checks', []) for c in required_checks):
                raise ValueError('existing bounded completeness/fidelity source declaration absent')
            declarations = row['contexts'] + [row['primary']]
            local_labels = set()
            for declaration in declarations:
                chapter = Path(declaration.get('source_file', declaration.get('file'))).stem
                excerpt = gate.local(package, declaration['excerpt_path']).read_text(encoding='utf-8')
                local_labels.update(chapter + '-' + label for label in se.LABEL.findall(se.clean(excerpt)))
            primary_chapter = Path(row['primary']['source_file']).stem
            def local_label(label):
                return label[len(primary_chapter) + 1:] if label.startswith(primary_chapter + '-') else label
            sources = []
            bodies = []
            delivered = gate.local(package, row['item_path']).read_text(encoding='utf-8')
            for declaration in declarations:
                path = declaration['excerpt_path']
                excerpt = gate.local(package, path).read_text(encoding='utf-8')
                if gate.digest(excerpt) != declaration['excerpt_sha256']:
                    raise ValueError('excerpt hash mismatch: ' + path)
                chapter = Path(declaration.get('source_file', declaration.get('file'))).stem
                sources.append(dict(root='package', path=path, sha256=declaration['excerpt_sha256'],
                                    original_source_sha256=declaration['source_sha256'],
                                    original_locator={'file':declaration.get('source_file', declaration.get('file')),
                                                      'lines':[declaration['start_line'],declaration['end_line']],
                                                      'version':row['source_version']}))
                replacements = {}
                def full(label):
                    return label if label in source.by_label or label in local_labels else chapter + '-' + label
                def replace_ref(match):
                    label = full(match[2])
                    if label in local_labels:
                        result = '\\' + match[1] + '{' + local_label(label) + '}'
                    else:
                        tag = source.by_label.get(label)
                        if not tag:
                            raise ValueError('unresolved source reference: ' + label)
                        result = r'\href{https://stacks.math.columbia.edu/tag/' + tag + '}{' + se.escape(source.tags[tag][1].replace('-', ' ')) + ' (Tag ' + tag + ')}'
                    replacements[match[0]] = result
                    return result
                adapted = se.REF.sub(replace_ref, excerpt)
                def replace_label(match):
                    result = r'\label{' + local_label(chapter + '-' + match[1]) + '}'
                    replacements[match[0]] = result
                    return result
                adapted = se.LABEL.sub(replace_label, adapted)
                def replace_cite(match):
                    result = r'\href{https://stacks.math.columbia.edu/bibliography}{' + se.escape('Bibliography: ' + match[2] + (' (' + match[1] + ')' if match[1] else '')) + '}'
                    replacements[match[0]] = result
                    return result
                adapted = re.sub(r'\\cite(?:\[([^]]*)\])?\{([^}]+)\}', replace_cite, adapted)
                start = delivered.find(adapted.strip())
                if start < 0 or delivered.find(adapted.strip(), start + 1) >= 0:
                    raise ValueError('full adapted source excerpt is not unique in delivered text: ' + path)
                first = delivered.count('\n', 0, start) + 1
                if declaration is row['primary']:
                    blocks = se.blocks(excerpt)
                    statement = next((b for b in blocks if b[2] in ['theorem','proposition','lemma']), None)
                    proofs = [b for b in blocks if b[2] == 'proof']
                    if statement is None or not proofs:
                        raise ValueError('source primary boundaries are unsupported')
                    ranges = [('primary_statement', statement[0], statement[1]),
                              ('primary_proof', min(b[0] for b in proofs), max(b[1] for b in proofs))]
                else:
                    ranges = [('context', 0, len(excerpt.rstrip()))]
                for role, a, b in ranges:
                    source_interval = [excerpt.count('\n', 0, a) + 1, excerpt.count('\n', 0, b - 1) + 1]
                    original = gate.lines(excerpt, source_interval)
                    kept = [dict(original=old, delivered=new) for old,new in replacements.items() if old in original]
                    rendered = original
                    for replacement in kept:
                        rendered = rendered.replace(replacement['original'], replacement['delivered'])
                    location = delivered.find(rendered.strip(), start)
                    if location < 0:
                        raise ValueError('selected body not present in delivered text: ' + role)
                    interval = [delivered.count('\n',0,location)+1,
                                delivered.count('\n',0,location+len(rendered.strip())-1)+1]
                    actual = gate.lines(delivered, interval)
                    if actual.strip() != rendered.strip():
                        raise ValueError('selected body has unrecorded non-reference edits: ' + role)
                    bodies.append(dict(role=role, tex_lines=interval, tex_sha256=gate.digest(actual),
                                       source_index=len(sources)-1, source_lines=source_interval,
                                       method='reference_only_adaptation', replacements=kept,
                                       source_excerpt_path=path))
            items[ident] = dict(item_sha256=row['tex_sha256'], claim_key=row['primary']['tag_url'],
                                independent_problem_unit=True, sources=sources, bodies=bodies,
                                source_check=dict(checked_at=check['checked_at'],
                                                  method='existing-declaration-plus-current-exact-reference-adaptation',
                                                  note=check['note'], complete_statement=True, complete_proof=True,
                                                  required_context_preserved=True, above_ordinary_phd_quals=True,
                                                  source_authorship='named-human-author',
                                                  declaration_basis=dict(existing_source_check=check,
                                                                         difficulty_level=row['difficulty_level'],
                                                                         difficulty_reason=row['difficulty_reason'],
                                                                         provenance_path='sources/'+ident+'/provenance.json',
                                                                         provenance_sha256=gate.digest(gate.local(package,'sources/'+ident+'/provenance.json').read_bytes()))))
        except (OSError, ValueError, TypeError, KeyError, StopIteration) as exc:
            failures[ident] = str(exc)
            items[ident] = dict(missing_evidence=str(exc))
    return dict(schema_version=1, derived_at=derived_at,
                derivation_scope='Current mechanical bindings of existing source-review declarations; no new math review.',
                package_manifest_sha256=gate.digest((package/'manifest.json').read_bytes()),
                items=items, derivation_holds=failures)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', type=Path, required=True)
    parser.add_argument('--project-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--bindings',type=Path,action='append',default=[],help='Existing exact source-worker fidelity bindings; never substitutes a new review.')
    args = parser.parse_args()
    if args.output.resolve().is_relative_to(args.package.resolve()):
        parser.error('output must be outside the read-only package')
    result = derive(args.package.resolve(), args.project_root.resolve(),args.bindings)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(dict(bound=len(result['items'])-len(result['derivation_holds']), holds=result['derivation_holds']),ensure_ascii=False,indent=2))
