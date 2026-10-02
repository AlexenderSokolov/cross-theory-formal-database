"""Read-only mechanical delivery gate; bounded source evidence is not a math referee."""
import hashlib
import json
from pathlib import Path
import re
import sqlite3

ID = re.compile(r'^[0-9]{3,}$')
HASH = re.compile(r'^[0-9a-f]{64}$')
LIMITATIONS = ('Checks delivery bytes and declared bounded source/fidelity evidence; '
               'does not certify mathematical correctness, human authorship, semantic uniqueness, '
               'or above-qualification difficulty independently.')


def digest(data):
    return hashlib.sha256(data.encode('utf-8') if isinstance(data, str) else data).hexdigest()


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate JSON key: ' + key)
        result[key] = value
    return result


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique_object)


def local(root, path):
    if not isinstance(path, str) or not path:
        raise ValueError('missing declared local path')
    result = (root / path).resolve()
    if not result.is_relative_to(root.resolve()) or not result.is_file():
        raise ValueError('missing or escaping declared file: ' + path)
    return result


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def dated(value):
    return nonempty(value) and bool(re.match(r'^\d{4}-\d{2}-\d{2}(?:T|$)', value))


def lines(text, interval):
    if not isinstance(text, str):
        raise ValueError('declared source is not readable editable text')
    parts = text.splitlines()
    if (not isinstance(interval, list) or len(interval) != 2 or
            any(type(i) is not int for i in interval) or not 1 <= interval[0] <= interval[1] <= len(parts)):
        raise ValueError('invalid body/source line range')
    return '\n'.join(parts[interval[0] - 1:interval[1]])


def active_tex(text):
    text = re.sub(r'(?<!\\)%[^\n]*', '', text)
    return re.sub(r'\\begin\{(?:comment|reference|history|slogan)\}.*?\\end\{(?:comment|reference|history|slogan)\}', '', text, flags=re.S)


def substantive_body(text):
    text = active_tex(text)
    text = re.sub(r'\\(?:begin|end)\{[^}]+\}(?:\[[^]]*\])?', '', text)
    text = re.sub(r'\\(?:label|input|include|includegraphics|includepdf)(?:\[[^]]*\])?\{[^}]*\}', '', text)
    return bool(text.strip(' \n\t{}$'))


def index_rows(root):
    rows = {}
    for line in local(root, 'INDEX.md').read_text(encoding='utf-8').splitlines():
        if line.startswith('|'):
            cols = [s.strip() for s in line.strip().strip('|').split('|')]
            if cols and ID.fullmatch(cols[0]):
                rows.setdefault(cols[0], []).append(cols)
    return rows


def exclusion_decisions(path):
    data = read_json(path)
    if type(data.get('schema_version')) is not int or data['schema_version'] != 1 or not isinstance(data.get('decisions'), list):
        raise ValueError('unsupported exclusion evidence schema')
    decisions = {}
    for row in data['decisions']:
        if not ID.fullmatch(str(row.get('id', ''))) or not nonempty(row.get('reason')):
            raise ValueError('invalid exclusion decision')
        source = (path.parent / row.get('source_path', '')).resolve()
        if not source.is_file() or digest(source.read_bytes()) != row.get('source_sha256'):
            raise ValueError('exclusion decision evidence hash mismatch')
        key = str(int(row['id']))
        if key in decisions:
            raise ValueError('duplicate exclusion decision')
        decisions[key] = row['reason']
    return decisions


def source_declarations(row):
    """Retained excerpt provenance may stand in for the full pinned original file."""
    declarations = []
    for entry in [row.get('primary', {})] + row.get('contexts', []):
        if not isinstance(entry, dict):
            raise ValueError('invalid source/context declaration')
        if entry.get('excerpt_path'):
            declarations.append(entry)
    return declarations


def check_bodies(root, row, evidence, source_root):
    errors = []
    def error(message):
        errors.append(message)
    if evidence.get('item_sha256') != row.get('tex_sha256'):
        error('source/fidelity evidence item hash mismatch')
    if evidence.get('independent_problem_unit') is not True:
        error('independent problem unit not declared')
    if not nonempty(evidence.get('claim_key')):
        error('missing independent claim key')
    review = evidence.get('source_check', {})
    if not isinstance(review, dict):
        review = {}
    for key in ['complete_statement', 'complete_proof', 'required_context_preserved', 'above_ordinary_phd_quals']:
        if review.get(key) is not True:
            error('bounded source_check missing ' + key)
    if (not dated(review.get('checked_at')) or not nonempty(review.get('method')) or
            not nonempty(review.get('note')) or review.get('source_authorship') != 'named-human-author'):
        error('bounded human-source comparison declaration missing')
    sources = evidence.get('sources')
    if not isinstance(sources, list) or not sources:
        return errors + ['missing declared sources']
    source_texts = []
    available_hashes = set()
    for source in sources:
        try:
            if not isinstance(source, dict):
                raise ValueError('source must be object')
            scope = source.get('root', 'source')
            if scope not in ['source', 'package','inline']:
                raise ValueError('unsupported source root schema')
            if 'inline_text' in source:
                if scope!='inline' or 'path' in source:
                    raise ValueError('inline and file-backed source forms are mutually exclusive')
                locator=source.get('original_locator',{})
                interval=locator.get('lines') if isinstance(locator,dict) else None
                if (not isinstance(source['inline_text'],str) or not HASH.fullmatch(str(source.get('original_source_sha256',''))) or
                        not isinstance(locator,dict) or not nonempty(locator.get('source_file')) or not nonempty(locator.get('source_version')) or
                        not isinstance(interval,list) or len(interval)!=2 or any(type(i) is not int for i in interval) or
                        not 1<=interval[0]<=interval[1] or interval[1]-interval[0]+1 != len(source['inline_text'].splitlines())):
                    raise ValueError('inline original source locator/hash/version missing or inconsistent')
                raw=source['inline_text'].encode('utf-8');pdf=False
            else:
                if scope=='inline':
                    raise ValueError('inline original source text missing')
                path = local(source_root if scope == 'source' else root, source.get('path'))
                raw = path.read_bytes();pdf=path.suffix.lower()=='.pdf'
            if not HASH.fullmatch(str(source.get('sha256', ''))) or digest(raw) != source['sha256']:
                error('declared source hash mismatch: ' + str(source.get('path')))
            available_hashes.add(source.get('original_source_sha256', source.get('sha256')))
            available_hashes.add(source.get('sha256'))
            source_texts.append(raw.decode('utf-8') if not pdf else None)
        except (OSError, ValueError, TypeError, UnicodeError) as exc:
            error('declared source: ' + str(exc))
            source_texts.append(None)
    for declaration in source_declarations(row):
        try:
            excerpt = local(root, declaration['excerpt_path']).read_bytes().decode('utf-8')
            if digest(excerpt) != declaration.get('excerpt_sha256'):
                error('source excerpt hash mismatch')
            if declaration.get('source_sha256') not in available_hashes:
                error('source excerpt original provenance absent from declared sources')
            matching = [i for i, s in enumerate(sources) if s.get('sha256') == declaration.get('source_sha256')]
            if matching and declaration.get('start_line') is not None:
                original = lines(source_texts[matching[0]], [declaration.get('start_line'), declaration.get('end_line')])
                if excerpt.strip() != original.strip():
                    error('source excerpt does not match declared original range')
        except (OSError, ValueError, TypeError, KeyError) as exc:
            error('source excerpt: ' + str(exc))
    bodies = evidence.get('bodies')
    if not isinstance(bodies, list):
        return errors + ['missing primary_statement and primary_proof bodies']
    roles = [b.get('role') for b in bodies if isinstance(b, dict)]
    for role in ['primary_statement', 'primary_proof']:
        if roles.count(role) != 1:
            error('exactly one declared ' + role + ' body required')
    text = local(root, row['item_path']).read_bytes().decode('utf-8')
    checked_spans = []
    for body in bodies:
        try:
            if not isinstance(body, dict) or body.get('role') not in ['primary_statement', 'primary_proof', 'context']:
                raise ValueError('unsupported body evidence schema')
            if 'tex_spans' in body or 'source_spans' in body:
                raise ValueError('unsupported supplemental span fields; use checked spans form')
            if 'spans' in body:
                scalar_fields = {'tex_lines', 'tex_sha256', 'source_index', 'source_lines',
                                 'method', 'replacements', 'fidelity_receipt'}
                if scalar_fields.intersection(body):
                    raise ValueError('scalar and multi-span body forms are mutually exclusive')
                if not isinstance(body['spans'], list) or not body['spans']:
                    raise ValueError('body spans must be a nonempty list')
                spans = []
                for span in body['spans']:
                    if not isinstance(span, dict) or {'role', 'spans', 'tex_spans', 'source_spans'}.intersection(span):
                        raise ValueError('unsupported nested body span schema')
                    spans.append(dict(span, role=body['role']))
            else:
                spans = [body]
            fragments = []
            previous_end = 0
            for span in spans:
                fragment = lines(text, span.get('tex_lines'))
                if span['tex_lines'][0] <= previous_end:
                    raise ValueError('body spans must be ordered and nonoverlapping')
                previous_end = span['tex_lines'][1]
                fragments.append(fragment)
            if not substantive_body('\n'.join(fragments)):
                error('empty ' + body['role'] + ' body')
            checked_spans.extend(spans)
        except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
            error('body evidence: ' + str(exc))
    for context in row.get('contexts', []):
        if context.get('excerpt_path') and not any(b.get('role') == 'context' and b.get('source_excerpt_path') == context['excerpt_path'] for b in checked_spans):
            error('declared context body absent from delivered evidence: ' + context['excerpt_path'])
    for body in checked_spans:
        try:
            if not isinstance(body, dict) or body.get('role') not in ['primary_statement', 'primary_proof', 'context']:
                raise ValueError('unsupported body evidence schema')
            role = body['role']
            delivered = lines(text, body.get('tex_lines'))
            if digest(delivered) != body.get('tex_sha256'):
                error('delivered ' + role + ' body hash mismatch')
            source_index = body.get('source_index')
            if type(source_index) is not int or not 0 <= source_index < len(sources):
                raise ValueError('invalid declared body source index')
            source = sources[source_index]
            method = body.get('method')
            if method in ['exact_tex', 'reference_only_adaptation','literal_asset_path_adaptation']:
                original = lines(source_texts[source_index], body.get('source_lines'))
                if method in ['reference_only_adaptation','literal_asset_path_adaptation']:
                    replacements = body.get('replacements')
                    if not isinstance(replacements, list):
                        raise ValueError('reference-only replacements must be a list')
                    for replacement in replacements:
                        old, new = replacement.get('original'), replacement.get('delivered')
                        if method=='literal_asset_path_adaptation':
                            old_match=re.fullmatch(r'(\\includegraphics(?:\[[^]]*\])?)\{([^{}]+)\}',str(old))
                            new_match=re.fullmatch(r'(\\includegraphics(?:\[[^]]*\])?)\{([^{}]+)\}',str(new))
                            target=(local(root,row['item_path']).parent/new_match[2]).resolve() if new_match else None
                            declared={local(root,a['path']) for a in row.get('asset_dependencies',[])}
                            if (not old_match or not new_match or old_match[1]!=new_match[1] or
                                    Path(old_match[2]).name!=Path(new_match[2]).name or target not in declared or old not in original):
                                raise ValueError('unsupported literal asset-path replacement')
                            original=original.replace(old,new)
                            continue
                        safe_new=new if isinstance(new,str) else ''
                        display=re.fullmatch(r'\\href\{(https?://[^{}]+)\}\{(.*)\}',safe_new,re.S)
                        if display:
                            safe_new=safe_new[:display.start(2)]+display[2].replace(r'\textbackslash{}','<literal-textbackslash>')+safe_new[display.end(2):]
                        if (not isinstance(old, str) or not isinstance(new, str) or
                                not re.fullmatch(r'\\(?:ref|eqref|pageref|label|cite)(?:\[[^]]*\])?\{[^{}]+\}', old) or
                                not re.fullmatch(r'\\(?:(?:ref|eqref|pageref|label)\{[^{}]+\}|href\{https?://[^{}]+\}\{[^{}]*\})', safe_new) or
                                old not in original):
                            raise ValueError('unsupported reference-only replacement')
                        original = original.replace(old, new)
                if delivered.strip() != original.strip():
                    error('source/body fidelity mismatch: ' + role)
            elif method == 'bounded_source_comparison':
                receipt = body.get('fidelity_receipt')
                if not isinstance(receipt, dict):
                    receipt = read_json(local(root, receipt))
                if (type(receipt.get('schema_version')) is not int or receipt['schema_version'] != 1 or receipt.get('checked') is not True or
                        receipt.get('item_sha256') != row['tex_sha256'] or
                        receipt.get('body_sha256') != body.get('tex_sha256') or
                        receipt.get('source_sha256') != source.get('sha256') or
                        receipt.get('role') != role or not dated(receipt.get('checked_at')) or
                        not nonempty(receipt.get('method')) or not nonempty(receipt.get('note')) or
                        not receipt.get('source_locator')):
                    error('fidelity receipt unsupported, stale, or incomplete')
            else:
                error('unsupported body fidelity method')
        except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
            error(('fidelity receipt: ' if isinstance(body, dict) and body.get('method') == 'bounded_source_comparison' else 'body evidence: ') + str(exc))
    return errors


def check_compile(root, row, build_root,receipt_root=None):
    errors = []
    try:
        receipt = read_json(local(receipt_root,row['problem_id']+'.json') if receipt_root else local(root,row.get('compile_receipt')))
        if (receipt.get('problem_id') != row['problem_id'] or receipt.get('ok') is not True or
                type(receipt.get('passes')) is not int or receipt['passes'] < 2 or
                receipt.get('shell_escape') is not False or not dated(receipt.get('compiled_at')) or
                not nonempty(receipt.get('engine')) or receipt.get('unresolved_references') != [] or
                receipt.get('missing_characters', []) != [] or receipt.get('rerun_requests',[]) != [] or
                type(receipt.get('pages')) is not int or receipt['pages'] < 1):
            errors.append('compile receipt failed or incomplete')
        if receipt.get('input_sha256') != row['tex_sha256']:
            errors.append('compile input hash mismatch')
        text = local(root, row['item_path']).read_bytes().decode('utf-8')
        assets = {}
        for asset in row.get('asset_dependencies', []):
            path = local(root, asset.get('path'))
            if digest(path.read_bytes()) != asset.get('sha256'):
                errors.append('asset dependency hash mismatch')
            assets[asset['path']] = asset['sha256']
        for name in re.findall(r'\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}', active_tex(text)):
            path = (local(root, row['item_path']).parent / name).resolve()
            if not path.is_relative_to(root) or str(path.relative_to(root)) not in assets:
                errors.append('undeclared figure dependency: ' + name)
        if receipt.get('dependency_sha256', {}) != assets:
            errors.append('compile dependency hash mismatch')
        default = row['problem_id'] + '/' + Path(row['item_path']).stem
        pdf = local(build_root, receipt.get('pdf_path', default + '.pdf'))
        if not pdf.read_bytes().startswith(b'%PDF-') or digest(pdf.read_bytes()) != receipt.get('pdf_sha256'):
            errors.append('compile PDF hash/signature mismatch')
        log = local(build_root, receipt.get('compiler_log_path', row['problem_id'] + '/compiler.log'))
        if digest(log.read_bytes()) != receipt.get('compiler_log_sha256'):
            errors.append('compile log hash mismatch')
        # Compiler stdout is hash-bound above and may concatenate multiple passes.
        # Only the final engine invocation determines reference stability.
        output = log.read_text(encoding='utf-8', errors='replace')
        banners = list(re.finditer(r'^This is (?:XeTeX|pdfTeX|LuaHBTeX|LuaTeX|e-TeX|TeX),', output, re.M))
        final_output = output[banners[-1].start():] if banners else output
        if re.search(r'Label\(s\) may have changed|Rerun to get (?:cross-references|outlines|bookmarks) right|Rerun to get /PageLabels entry|Package rerunfilecheck Warning:.*has changed', final_output, re.I):
            errors.append('final compiler pass requests rerun')
        if re.search(r'Label .+ multiply defined|multiply-defined labels', final_output, re.I):
            errors.append('final compiler pass has multiply-defined labels')
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
        errors.append('compile receipt/artifacts: ' + str(exc))
    return errors


def check_sqlite(root, rows):
    errors = []
    try:
        path = local(root, 'corpus.sqlite')
        with sqlite3.connect(path.as_uri() + '?mode=ro', uri=True) as db:
            db.row_factory = sqlite3.Row
            if db.execute('PRAGMA integrity_check').fetchone()[0] != 'ok' or db.execute('PRAGMA foreign_key_check').fetchall():
                errors.append('SQLite integrity/foreign key failure')
            problems = db.execute('SELECT * FROM problems').fetchall()
            ids = [r['problem_id'] for r in problems]
            expected_ids = [r['problem_id'] for r in rows]
            if len(set(ids)) != len(ids) or set(ids) != set(expected_ids):
                errors.append('SQLite problem IDs differ from manifest')
            by_id = {r['problem_id']: r for r in problems}
            sources = {s['source_id']: s for s in db.execute('SELECT * FROM sources')}
            if set(sources) != {r['source_id'] for r in rows}:
                errors.append('SQLite source IDs differ from manifest')
            for row in rows:
                actual = by_id.get(row['problem_id'])
                if actual is None:
                    continue
                for key in ['title','difficulty_level','difficulty_reason','source_id','tex_sha256','origin_class','status']:
                    if actual[key] != row.get(key):
                        errors.append('SQLite ' + key + ' mismatch: ' + row['problem_id'])
                for key, field in [('tex_path','item_path'),('compile_receipt_path','compile_receipt')]:
                    if actual[key] != row.get(field):
                        errors.append('SQLite ' + key + ' mismatch: ' + row['problem_id'])
                if actual['tex_content'] != local(root, row['item_path']).read_bytes().decode('utf-8'):
                    errors.append('SQLite tex_content differs from full delivered TeX: ' + row['problem_id'])
                if json.loads(actual['source_locator_json']) != {'primary':row['primary'],'contexts':row.get('contexts', [])}:
                    errors.append('SQLite source locator mismatch: ' + row['problem_id'])
                source = sources.get(row['source_id'])
                if source is None or any(source[k] != row.get(k) for k in ['author','work','source_url','source_version','retrieved_at','license','license_path']):
                    errors.append('SQLite source metadata mismatch: ' + row['problem_id'])
    except (OSError, ValueError, sqlite3.Error, KeyError, TypeError, IndexError) as exc:
        errors.append('SQLite: ' + str(exc))
    return errors


def validate(package, item=None, evidence_path=None, source_root=None, build_root=None, exclusions_path=None,receipt_root=None):
    root = package.resolve()
    report = dict(schema_version=1, mode='editable-delivery', editable_qualified_count=0,
                  package_item_count=0, items={}, errors=[], limitations=LIMITATIONS)
    report['receipt_set']=str(receipt_root.resolve()) if receipt_root else 'packaged-original-receipts'
    try:
        manifest = read_json(local(root, 'manifest.json'))
        if type(manifest.get('schema_version')) is not int or manifest['schema_version'] != 1 or not isinstance(manifest.get('items'), list):
            raise ValueError('unsupported editable manifest schema')
        rows = manifest['items']
        report['package_item_count'] = len(rows)
        evidence = read_json(evidence_path or root / 'delivery-evidence.json')
        if type(evidence.get('schema_version')) is not int or evidence['schema_version'] != 1 or not isinstance(evidence.get('items'), dict):
            raise ValueError('unsupported evidence schema')
        if evidence.get('package_manifest_sha256') is not None and evidence['package_manifest_sha256']!=digest(local(root,'manifest.json').read_bytes()):
            raise ValueError('evidence package manifest hash mismatch')
        excluded = exclusion_decisions(Path(__file__).with_name('editable_exclusions.json'))
        if exclusions_path:
            for key,reason in exclusion_decisions(exclusions_path).items():
                if key in excluded and excluded[key] != reason:
                    raise ValueError('additional exclusion evidence conflicts with pinned decision')
                excluded[key] = reason
        index = index_rows(root)
    except (OSError, ValueError, TypeError, AttributeError) as exc:
        report['errors'].append('manifest/evidence/INDEX: ' + str(exc))
        return report
    ids = []
    for row in rows:
        if not isinstance(row, dict) or not ID.fullmatch(str(row.get('problem_id', ''))):
            report['errors'].append('invalid manifest problem ID')
            continue
        ident = row['problem_id']
        if str(int(ident)) in [str(int(i)) for i in ids]:
            report['errors'].append('duplicate problem ID: ' + ident)
        ids.append(ident)
        if str(int(ident)) in excluded:
            report['errors'].append('excluded ' + ident + ': ' + excluded[str(int(ident))])
    if len(ids) != len(rows):
        return report
    if type(manifest.get('verified_count')) is not int or manifest['verified_count'] != len(set(ids)):
        report['errors'].append('manifest verified_count differs from unique actual items')
    if set(index) != set(ids):
        report['errors'].append('INDEX problem IDs differ from manifest')
    if set(evidence['items']) != set(ids):
        report['errors'].append('evidence problem IDs differ from manifest')
    if item is not None and item not in ids:
        report['errors'].append('requested item absent from manifest: ' + item)
    claims = {}
    for ident, entry in evidence['items'].items():
        if not isinstance(entry, dict):
            report['errors'].append('invalid per-item evidence schema: ' + ident)
            continue
        key = ' '.join(str(entry.get('claim_key', '')).casefold().split())
        if key and key in claims:
            report['errors'].append('duplicate independent claim key: ' + ident + '/' + claims[key])
        claims[key] = ident
    primary_claims = {}
    for row in rows:
        primary = {k:v for k,v in row.get('primary', {}).items() if k not in ['excerpt_path','excerpt_sha256','source_map_path','tag_url']}
        identity = json.dumps([row.get('source_url', '').split('#')[0], primary], sort_keys=True, ensure_ascii=False)
        if identity in primary_claims:
            report['errors'].append('duplicate primary source identity: ' + row['problem_id'] + '/' + primary_claims[identity])
        primary_claims[identity] = row['problem_id']
    report['errors'].extend(check_sqlite(root, rows))
    source_root = (source_root or root).resolve()
    build_root = (build_root or root.parent / 'build').resolve()
    for row in rows:
        ident = row['problem_id']
        errors = []
        for key in ['title','author','work','source_id','source_url','source_version','retrieved_at','license','difficulty_reason']:
            if not nonempty(row.get(key)):
                errors.append('missing ' + key)
        if row.get('difficulty_level') not in ['H1','H2','H3'] or row.get('status') != 'verified_editable_tex' or row.get('admission_hold'):
            errors.append('unqualified difficulty/status or admission_hold')
        if row.get('origin_class') not in ['human_authored_native_tex','human_authored_proof_assistant_transcription']:
            errors.append('unsupported source origin schema')
        try:
            path = local(root, row.get('item_path'))
            text = path.read_bytes().decode('utf-8')
            if digest(text) != row.get('tex_sha256'):
                errors.append('delivered TeX hash mismatch')
            if not path.name.startswith(ident + '_'):
                errors.append('TeX filename ID mismatch')
            if re.search(r'\\includepdf\b', active_tex(text)):
                errors.append('PDF-page wrapper cannot qualify as editable delivery')
            if re.search(r'\\(?:input|include)\b', active_tex(text)):
                errors.append('full per-item body must be embedded; editable inputs are not flattened')
            if not re.search(r'\\begin\{document\}', active_tex(text)) or not re.search(r'\\end\{document\}', active_tex(text)):
                errors.append('full independent TeX document missing')
            local(root, row.get('license_path'))
            provenance = read_json(local(root, 'sources/' + ident + '/provenance.json'))
            if provenance != row:
                errors.append('provenance differs from manifest')
            entries = index.get(ident, [])
            if len(entries) != 1:
                errors.append('INDEX must have exactly one row')
            elif (len(entries[0]) != 5 or entries[0][1] != row.get('title') or entries[0][2] != row.get('difficulty_level') or
                  '(' + row['item_path'] + ')' not in entries[0][3] or
                  row.get('primary', {}).get('tag_url', row['source_url']) not in entries[0][4] or
                  '(sources/' + ident + '/provenance.json)' not in entries[0][4]):
                errors.append('INDEX metadata mismatch')
            if item is None or item == ident:
                entry = evidence['items'].get(ident)
                if not isinstance(entry, dict):
                    errors.append('missing per-item evidence')
                else:
                    errors.extend(check_bodies(root, row, entry, source_root))
                errors.extend(check_compile(root, row, build_root,receipt_root.resolve() if receipt_root else None))
        except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
            errors.append('item evidence: ' + str(exc))
        if item is None or item == ident:
            report['items'][ident] = dict(status='failed' if errors else 'qualified_editable', errors=errors)
        elif errors:
            report['errors'].append('package consistency ' + ident + ': ' + '; '.join(errors))
    if not report['errors']:
        report['editable_qualified_count'] = sum(r['status'] == 'qualified_editable' for r in report['items'].values())
    return report
