"""Focused source review, bounded source authorization and independent sampling."""
import argparse
import json
import math
from pathlib import Path
import random

PROTOCOL = 'focused-source-check-v1'
CHECKS = ('authorship', 'paired_scope', 'key_hypotheses', 'core_obligations', 'semantic_neighbors')
EXTRA_CONFIG = ('review_protocol', 'source_authorization')

def require(ok, message):
    if not ok:
        raise ValueError(message)

def text(value):
    return isinstance(value, str) and bool(value.strip())

def validate_review(task, record):
    require(record.get('review_protocol') == PROTOCOL, 'focused review protocol mismatch')
    require(1 <= len(task['core_obligations']) <= 3 and all(text(x) for x in task['core_obligations']), 'focused review requires 1..3 concrete core obligations')
    require(task.get('red_flags', []) == [], 'focused task has unresolved red flags')
    require(record.get('red_flags') == [], 'focused review has missing or unresolved red flags')
    checks = record.get('checks', {})
    for key in CHECKS:
        check = checks.get(key, {})
        require(isinstance(check, dict) and check.get('status') == 'pass' and text(check.get('evidence')) and check['evidence'].strip().lower() not in ('pass', 'true', 'ok'), 'focused check needs substantive evidence: ' + key)

def assembly_files(task):
    """Use the original input path, exactly as prepared_delivery.copied_asset."""
    result = []
    for key in ('asset_paths', 'bibliography_paths'):
        for item in task['assembly'].get(key, []):
            path = item if isinstance(item, str) else item.get('path') if isinstance(item, dict) else None
            require(text(path), 'assembly file needs an original source path')
            result.append(Path(path).as_posix())
    return result

def material_paths(task):
    spans = task['statement_spans'] + task['proof_spans'] + task['context_spans'] + task['assembly']['preamble_spans']
    spans += [r['source_span'] for r in task['assembly'].get('external_references', [])]
    return {Path(s['path']).as_posix() for s in spans} | set(assembly_files(task))

def material_ranges(task):
    result={}
    spans=task['statement_spans']+task['proof_spans']+task['context_spans']+task['assembly']['preamble_spans']
    spans += [r['source_span'] for r in task['assembly'].get('external_references',[])]
    for span in spans:
        result.setdefault(Path(span['path']).as_posix(),[]).append([span['start_line'],span['end_line']])
    for path in assembly_files(task):result[path]=None
    return result

def validate_authorization(task, authorization):
    route = authorization.get('route', {})
    ref = task.get('source_authorization', {})
    require(route.get('status') == 'approved' and route.get('approved_by') == 'Codex' and text(route.get('route_id')), 'Codex approved route required')
    require(ref.get('route_id') == route['route_id'], 'source route authorization mismatch')
    source_allowed = task['source_id'] in route.get('allowed_sources', []) or (any(task['source_id'].startswith(p) for p in route.get('allowed_source_prefixes', []) if text(p)) and any(task['source_url'].startswith(p) for p in route.get('allowed_url_prefixes', []) if text(p)))
    require(source_allowed and task['route'] in route.get('allowed_routes', []) and task['license']['name'] in route.get('allowed_licenses', []), 'source outside approved route boundary')
    matches = [r for r in authorization.get('source_records', []) if r.get('source_record_id') == ref.get('source_record_id')]
    require(len(matches) == 1, 'unique fixed source record required')
    record = matches[0]
    require(all(record.get(k) == task.get(k) for k in ('source_id', 'source_version')) and record.get('route_id') == route['route_id'], 'source record version or route mismatch')
    require(record.get('source_url') == task['source_url'] and record.get('license') == task['license'], 'fixed source URL or license evidence mismatch')
    allowed, excluded = record.get('allowed_scope'), record.get('exclusions')
    require(isinstance(allowed, list) and allowed and isinstance(excluded, list), 'source scope and exclusions required')
    def interval(s):
        require(isinstance(s, dict) and text(s.get('path')) and type(s.get('start_line')) is int and type(s.get('end_line')) is int and 1 <= s['start_line'] <= s['end_line'], 'invalid authorized source interval')
        return (Path(s['path']).as_posix(), s['start_line'], s['end_line'])
    allowed, excluded = list(map(interval, allowed)), list(map(interval, excluded))
    allowed_files = record.get('allowed_files', [])
    require(isinstance(allowed_files, list) and all(text(p) for p in allowed_files), 'allowed_files must list exact original source paths')
    allowed_files = {Path(p).as_posix() for p in allowed_files}
    for path in assembly_files(task):
        require(path in allowed_files, 'assembly file outside approved allowed_files: ' + path)
        require(not any(p == path for p, lo, hi in excluded), 'whole-file assembly input intersects source exclusion: ' + path)
    spans = task['statement_spans'] + task['proof_spans'] + task['context_spans'] + task['assembly']['preamble_spans']
    spans += [r['source_span'] for r in task['assembly'].get('external_references', [])]
    for s in spans:
        path, a, b = interval(s)
        require(any(p == path and lo <= a <= b <= hi for p, lo, hi in allowed), 'task exceeds allowed source scope')
        require(not any(p == path and a <= hi and lo <= b for p, lo, hi in excluded), 'task intersects source exclusion')

def binding(row):
    return {k: row[k] for k in ('task_id', 'problem_id', 'revision', 'source_id', 'source_version', 'claim_key', 'review_protocol')}

def select_sample(tasks, main_session_id):
    require(1 <= len(tasks) <= 25 and text(main_session_id), 'sample requires 1..25 frozen tasks and main session')
    frozen = [binding(t) for t in tasks]
    require(all(r['review_protocol'] == PROTOCOL for r in frozen) and len({r['problem_id'] for r in frozen}) == len(frozen), 'sample requires unique focused tasks')
    return {'review_protocol': PROTOCOL, 'frozen_batch': frozen, 'main_session_id': main_session_id, 'sampled': random.SystemRandom().sample(frozen, math.ceil(len(frozen) / 10)), 'sample_reviews': []}

def validate_sample(record, tasks, evidence_root=None):
    expected = [binding(t) for t in tasks]
    require(record.get('review_protocol') == PROTOCOL and record.get('frozen_batch') == expected, 'sample frozen batch mismatch')
    sampled = record.get('sampled', [])
    require(len(sampled) == math.ceil(len(expected) / 10) and len({r['problem_id'] for r in sampled}) == len(sampled) and all(r in expected for r in sampled), 'incorrect independent sample size or identity')
    main = record.get('main_session_id')
    require(text(main), 'main session required')
    reviews = record.get('sample_reviews', [])
    require(len(reviews) == len(sampled), 'all sampled tasks require independent records')
    for row in sampled:
        matched = [r for r in reviews if binding(r) == row]
        require(len(matched) == 1, 'sample review binding mismatch')
        r = matched[0]
        require(text(r.get('session_id')) and r['session_id'].strip().casefold() != main.strip().casefold(), 'sample review must use independent context session')
        require(r.get('initial_rationale_provided') is False and r.get('full_materials_read') is True and isinstance(r.get('materials_read'), list) and r['materials_read'] and all(text(x) for x in r['materials_read']), 'sample must read full materials without initial rationale')
        require(r.get('conclusion') == 'pass' and text(r.get('evidence')) and r.get('red_flags') == [], 'sample unresolved or lacks conclusion evidence')
        require(evidence_root is not None, 'sample session evidence root required')
        def evidence_file(value):
            require(text(value), 'session evidence path required')
            root = Path(evidence_root).resolve()
            path = (root / value).resolve()
            require(not Path(value).is_absolute() and path.is_relative_to(root) and path.is_file(), 'session evidence file missing or outside evidence root')
            return path
        evidence = json.loads(evidence_file(r.get('session_evidence_path')).read_text(encoding='utf-8-sig'))
        normalized_path = evidence.get('normalized_session_result_path')
        origin = 'native_session_log_projection' if normalized_path else 'native_tool_result'
        require(evidence.get('evidence_origin') == origin and evidence.get('session_id') == r['session_id'] and evidence.get('parent_session_id') == main, 'actual independent session evidence mismatch')
        require(not (normalized_path and evidence.get('raw_session_result_path')), 'use a distinct normalized projection path, not a raw alias')
        raw_path = evidence_file(normalized_path or evidence.get('raw_session_result_path'))
        raw = json.loads(raw_path.read_text(encoding='utf-8-sig'))
        task = next(t for t in tasks if binding(t) == row)
        if raw.get('schema') == 'dsh-native-review-normalized-v1':
            require(normalized_path, 'DSH normalized projection must use normalized_session_result_path')
            import prepared_dsh_evidence as dsh
            raw = dsh.validate_normalized(raw, task, material_ranges(task), evidence_root)
        else:
            require(not normalized_path, 'unsupported normalized session evidence schema')
        # A wrapper indexes native evidence; it cannot supply missing request,
        # tool-call or result facts on behalf of the underlying session.
        require(isinstance(raw, dict) and raw.get('session_id') == r['session_id'] and raw.get('parent_session_id') == main, 'raw native session identity mismatch')
        task = next(t for t in tasks if binding(t) == row)
        required_paths = material_paths(task)
        request = raw.get('request', {})
        result = raw.get('result', {})
        require(isinstance(request, dict) and isinstance(result, dict), 'raw native request/result missing')
        for key in ('task_id', 'revision'):
            require(request.get(key) == row[key] and result.get(key) == row[key], 'raw native request/result task binding mismatch: ' + key)
        requested = request.get('materials')
        require(isinstance(requested, list) and all(text(x) for x in requested) and required_paths <= set(requested), 'raw request omits actual assembly material')
        require(request.get('initial_rationale_provided') is False, 'raw request does not establish neutral independent input')
        require(result.get('conclusion') == 'pass' and result.get('red_flags') == [] and text(result.get('evidence')), 'raw native conclusion is not an unflagged pass')
        read = result.get('materials_read')
        require(isinstance(read, list) and all(text(x) for x in read) and required_paths <= set(read), 'raw result did not read every actual assembly material')
        for key in ('materials_read', 'conclusion', 'red_flags', 'evidence'):
            require(r.get(key) == result.get(key), 'sample wrapper differs from raw result: ' + key)
        require(evidence.get('initial_rationale_provided') is False and evidence.get('materials_read') == read, 'session wrapper materials or rationale mismatch')
        calls = raw.get('tool_calls', [])
        require(isinstance(calls, list), 'raw tool call list missing')
        for path in read:
            require(any(isinstance(call, dict) and call.get('name') == 'read_file' and call.get('status') == 'completed' and
                        isinstance(call.get('arguments'), dict) and call['arguments'].get('path') == path
                        for call in calls), 'raw session lacks successful read_file for material: ' + path)
    return record

def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('select-sample'); p.add_argument('--tasks', required=True); p.add_argument('--main-session-id', required=True); p.add_argument('--output', required=True)
    p = sub.add_parser('validate-sample'); p.add_argument('--tasks', required=True); p.add_argument('--sample', required=True)
    args = parser.parse_args()
    tasks = json.loads(Path(args.tasks).read_text(encoding='utf-8-sig'))
    if args.command == 'select-sample':
        result = select_sample(tasks, args.main_session_id)
        with Path(args.output).open('x', encoding='utf-8') as stream:
            json.dump(result, stream, ensure_ascii=False, indent=2)
    else:
        validate_sample(json.loads(Path(args.sample).read_text(encoding='utf-8-sig')), tasks, Path(args.sample).resolve().parent)
    print(json.dumps({'status': 'sample_selected' if args.command == 'select-sample' else 'sample_validated'}))

if __name__ == '__main__':
    main()
