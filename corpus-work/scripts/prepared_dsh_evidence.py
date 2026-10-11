"""Offline, fail-closed projection of DSH v4 one-shot spawn review evidence.

Reads native logs only. Does not make model requests or read source files.
Natural-language requests retain unknown neutrality; packet reads never become
claims of direct reads of the original source. Output is not publication approval.
"""
import argparse
import json
import ntpath
import re
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def text_blocks(content):
    return "".join(b.get("text", "") for b in content if b.get("type") == "text")


def object_text(value):
    value = value.strip()
    if value.startswith("```json") and value.endswith("```"):
        value = value[7:-3].strip()
    elif value.startswith("```") and value.endswith("```"):
        value = value[3:-3].strip()
    parsed = json.loads(value)
    require(isinstance(parsed, dict), "expected a JSON object")
    return parsed


def load_log(path, *, parent=False):
    rows = [json.loads(line) for line in Path(path).read_text(encoding="utf-8-sig").splitlines()]
    require(rows and rows[0].get("type") == "session" and rows[0].get("version") == 4,
            "expected native DSH v4 session header")
    events = rows[1:]
    require([e.get("seq") for e in events] == list(range(len(events))), "incomplete or reordered native event sequence")
    if parent:
        return rows[0], events
    ends = [e for e in events if e.get("type") == "turn/end"]
    require(len([e for e in events if e.get("type") == "turn/start"]) == 1, "exactly one native turn required")
    require(len(ends) == 1 and ends[0]["data"].get("reason", {}).get("kind") == "completed",
            "exactly one completed native turn required")
    require(not any(e.get("type") == "turn/start" and e["seq"] > ends[0]["seq"] for e in events),
            "unfinished later turn")
    return rows[0], events


def canonical(path, cwd):
    return ntpath.normcase(ntpath.normpath(path if ntpath.isabs(path) else ntpath.join(cwd, path)))


def result_for(events, call):
    matches = [e for e in events if e.get("type") == "tool/result"
               and e.get("surfaceOp") == "append"
               and e["data"]["message"].get("toolCallId") == call["data"]["callId"]]
    require(len(matches) == 1, "tool call must have exactly one appended native result")
    result = matches[0]
    require(result["seq"] > call["seq"] and result["data"]["message"].get("isError") is False,
            "tool call did not complete successfully")
    return result


def packet_spans(lines, packet_path):
    mappings = []
    for line_no, line in lines.items():
        match = re.fullmatch(r"## (\w+) \| (.+) \| (\d+)-(\d+)", line)
        if not match:
            continue
        kind, source, first, last = match.groups()
        first, last = int(first), int(last)
        require(first <= last, "invalid packet source span")
        positions = []
        for number in sorted(n for n in lines if n > line_no):
            body = lines[number]
            if body.startswith("## "):
                break
            row = re.match(r"^(\d+):(?: |$)", body)
            if row:
                positions.append((number, int(row.group(1))))
        require([n for _, n in positions] == list(range(first, last + 1)), "packet source numbering incomplete")
        mappings.append({"packet_path": packet_path, "packet_start_line": positions[0][0],
                         "packet_end_line": positions[-1][0], "source_path": source,
                         "source_start_line": first, "source_end_line": last, "kind": kind,
                         "mapping_basis": "packet labels, not original-source verification",
                         "direct_source_read": False})
    return mappings


def normalize_ranges(value):
    if value is None:
        return None
    require(isinstance(value,list) and value, 'required source ranges must be a nonempty list or null')
    require(all(isinstance(r,list) and len(r)==2 and type(r[0]) is int and type(r[1]) is int and 1 <= r[0] <= r[1] for r in value), 'invalid required source range')
    return sorted(value)

def observed_ranges(lines):
    result=[]
    for number in sorted(lines):
        if result and number==result[-1][1]+1:result[-1][1]=number
        else:result.append([number,number])
    return result

def parse_request(value):
    try:return object_text(value)
    except (ValueError,TypeError):pass
    begin,end='BEGIN_REVIEW_REQUEST_JSON','END_REVIEW_REQUEST_JSON'
    if begin not in value and end not in value:return None
    require(value.count(begin)==value.count(end)==1, 'ambiguous structured request block')
    prefix,rest=value.split(begin);body,suffix=rest.split(end)
    allowed={'You are an independent read-only reviewer.', 'Return only the required JSON object.', 'Use only the read tool.', 'Do not write files or use other tools.'}
    require(all(line.strip() in allowed for line in (prefix+'\n'+suffix).splitlines() if line.strip()), 'non-neutral wrapper outside request JSON')
    return object_text(body)


def export_review(parent_path, child_path, materials, neutral_material=None, ranges=None, evidence_root=None):
    parent, pe = load_log(parent_path, parent=True)
    child, ce = load_log(child_path)
    require(child.get("origin") == "subagent" and child.get("isSeeded") is False
            and child.get("parentSession") == parent.get("id") and child["id"] != parent["id"],
            "native fresh-child lineage missing")
    descriptors = [e for e in ce if e.get("type") == "subagent/descriptor"]
    require(len(descriptors) == 1 and descriptors[0]["data"].get("provider") == "spawn"
            and descriptors[0]["data"].get("mode") == "one-shot", "one-shot spawn descriptor required")
    requests = [e for e in ce if e.get("type") == "user/message" and e["data"].get("source", {}).get("kind") == "user"]
    require(len(requests) == 1, "exactly one original child request required")
    request_event = requests[0]
    request_text = text_blocks(request_event["data"]["content"])
    delegations = [e for e in pe if e.get("type") == "tool/call" and e["data"].get("name") == "subagent"
                   and json.loads(e["data"]["arguments"]).get("prompt") == request_text]
    require(len(delegations) == 1, "parent delegation does not uniquely bind child's actual request")
    delegation_result = result_for(pe, delegations[0])
    delegation = delegations[0]
    starts = [e for e in pe if e.get('type') == 'turn/start' and e['seq'] < delegation['seq']]
    require(starts and not any(e.get('type') in ('turn/start','turn/end') and delegation['seq'] < e['seq'] < delegation_result['seq'] for e in pe), 'delegation/result cross parent turn boundary')
    require(not any(e.get('type') == 'turn/end' and starts[-1]['seq'] < e['seq'] < delegation['seq'] for e in pe), 'parent delegation outside active turn')
    answers = [e for e in ce if e.get("type") == "assistant/message" and text_blocks(e["data"]["message"]["content"]).strip()]
    require(answers, "no child assistant result")
    final = answers[-1]
    final_text = text_blocks(final["data"]["message"]["content"])
    require(text_blocks(delegation_result["data"]["message"]["content"]) == final_text,
            "parent result does not match native child's final output")
    result = object_text(final_text)
    require(result.get("conclusion") in ("pass", "needs_review") and isinstance(result.get("red_flags"), list)
            and result.get("evidence"), "child result lacks review conclusion/evidence")
    cwd = child["cwd"]
    requested = {canonical(m, cwd): m for m in materials}
    require(len(requested) == len(materials) and requested, "materials must be nonempty and unique")
    for material in materials:
        require(material in request_text or ntpath.basename(material) in request_text,
                "expected material absent from actual child request: " + material)
    coverage = {p: {} for p in requested}
    totals = {}
    calls = []
    for call in [e for e in ce if e.get("type") == "tool/call"]:
        require(call["data"].get("name") == "read", "unexpected child capability: " + str(call["data"].get("name")))
        args = json.loads(call["data"]["arguments"])
        path = canonical(args["file_path"], cwd)
        require(path in requested, "child read outside declared material scope")
        response = result_for(ce, call)
        require(response["seq"] < final["seq"], "read completed after final review")
        meta = response["data"].get("meta", {})
        require(canonical(meta.get("path", ""), cwd) == path, "read result path differs from call")
        require(not meta.get("truncatedByBytes"), "read result truncated by bytes")
        total = meta.get("totalLines")
        require(isinstance(total, int) and total > 0 and totals.get(path, total) == total, "inconsistent file line count")
        totals[path] = total
        lines = meta.get("lines", [])
        nums = [line.get("number") for line in lines]
        require(nums and nums == list(range(meta.get("offset", 0), meta.get("offset", 0) + len(lines))), "noncontiguous read result lines")
        require(meta.get("offset") == args.get("offset", 1) and nums[-1] <= total, "read window mismatch")
        if "limit" in args:
            require(len(lines) <= args["limit"], "read window exceeds requested limit")
        # Check native coverage/truncation metadata and visible line labels, not
        # an automated comparison of author text or repeated-read contents.
        rendered = text_blocks(response["data"]["message"]["content"])
        visible_numbers = {int(n) for n in re.findall(r"(?m)^(\d+):", rendered)}
        require(set(nums) <= visible_numbers, "native read result omits declared line labels")
        for line in lines:
            require(not line.get("truncated") and isinstance(line.get("text"), str), "truncated or invalid read line")
            require(not re.search(r"\.\.\. \(line truncated to \d+ chars\)$", line["text"]), "native line-length truncation")
            coverage[path][line["number"]] = line["text"]
        calls.append({"name": "read_file", "arguments": {"path": requested[path]}, "status": "completed",
                      "native_name": "read", "native_arguments": args, "native_call_id": call["data"]["callId"],
                      "source_event_seq": call["seq"], "result_event_seq": response["seq"],
                      "observed_path": meta["path"], "lines_covered": [nums[0], nums[-1]], "total_lines": total})
    required = {p: None for p in requested}
    if ranges is not None:
        require(isinstance(ranges, dict) and {canonical(p, cwd) for p in ranges} == set(requested), 'range map must exactly cover declared materials')
        required = {canonical(p, cwd): normalize_ranges(value) for p, value in ranges.items()}
    for path in requested:
        require(path in totals, 'incomplete material read: ' + requested[path])
        needed = [[1, totals[path]]] if required[path] is None else required[path]
        require(all(1 <= start <= end <= totals[path] and set(range(start, end + 1)) <= set(coverage[path]) for start, end in needed), 'incomplete material read: ' + requested[path])
    structured_request = parse_request(request_text)
    if structured_request is not None:
        require(isinstance(structured_request.get("materials"), list)
                and {canonical(m, cwd) for m in structured_request["materials"]} == set(requested),
                "structured request material scope differs from requested export")
    neutral = None
    if neutral_material:
        neutral_path = canonical(neutral_material, cwd)
        require(neutral_path in coverage, "neutral input not read")
        require(required[neutral_path] is None, "neutral JSON must be read in full")
        neutral = object_text("\n".join(coverage[neutral_path][i] for i in sorted(coverage[neutral_path])))
    binding = structured_request or neutral
    require(binding is not None, "structured task request or fully read neutral JSON required")
    for key in ("task_id", "revision"):
        require(isinstance(binding.get(key), str) and result.get(key) == binding[key], "task/result binding mismatch: " + key)
    rationale = structured_request.get("initial_rationale_provided") if structured_request else None
    if ranges is not None:
        require(structured_request is not None and rationale is False, 'direct-range review requires a structured neutral request')
        require(set(structured_request) <= {'task_id', 'revision', 'materials', 'initial_rationale_provided', 'required_ranges'}, 'direct request contains non-neutral or unsupported fields')
        declared = structured_request.get('required_ranges')
        require(isinstance(declared, dict) and {canonical(p,cwd):normalize_ranges(v) for p,v in declared.items()} == required, 'native request ranges differ from requested export')
        if neutral is not None:
            forbidden = {'difficulty_reason','difficulty_level','review','reviews','reviewer_id','checks','core_assessment','prerequisite_assessment','reason','verdict','red_flags','conclusion'}
            def neutral_keys(value):
                if isinstance(value, dict):
                    require(not set(value) & forbidden, 'neutral input contains initial review/rationale fields')
                    for v in value.values():neutral_keys(v)
                elif isinstance(value,list):
                    for v in value:neutral_keys(v)
            neutral_keys(neutral)
            for key in ('task_id','revision'):
                require(neutral.get(key, neutral.get('binding',{}).get(key)) == binding[key], 'neutral material binding mismatch')
    if ranges is not None:
        require(isinstance(result.get('materials_read'),list) and {canonical(p,cwd) for p in result['materials_read']} == set(requested), 'native final material list differs from actual requested reads')
    native_result = result
    normalized_result = dict(result, materials_read=list(materials),
                             evidence=result["evidence"] if isinstance(result["evidence"], str) else json.dumps(result["evidence"], ensure_ascii=False))
    mapping = []
    for path, material in requested.items():
        mapping.extend(packet_spans(coverage[path], material))
    def provenance_path(path):
        resolved=Path(path).resolve()
        if evidence_root is None:
            return str(resolved)
        root=Path(evidence_root).resolve()
        require(resolved.is_relative_to(root), 'native log outside evidence root')
        return resolved.relative_to(root).as_posix()
    return {"schema": "dsh-native-review-normalized-v1", "session_id": child["id"], "parent_session_id": parent["id"],
            "evidence_origin": "native_session_log_projection", "scope": "packet_calibration" if mapping else "direct_material_review",
            "publication_eligible": False,
            "request": {"task_id": binding["task_id"], "revision": binding["revision"], "materials": list(materials),
                        "initial_rationale_provided": rationale, "native_text": request_text,
                        "binding_basis": "structured request" if structured_request else "neutral input actually read by child"},
            "tool_calls": calls, "result": normalized_result, "native_result": native_result,
            "source_span_mapping": mapping,
            "required_ranges": {requested[p]:v for p,v in required.items()},
            "neutral_material": neutral_material,
            "read_coverage": {requested[p]:{'observed_ranges':observed_ranges(coverage[p]),'total_lines':totals[p]} for p in requested},
            "provenance": {"parent_native_jsonl": provenance_path(parent_path), "child_native_jsonl": provenance_path(child_path),
                           "path_basis": "evidence_root" if evidence_root is not None else "legacy_absolute",
                           "parent_header": parent, "child_header": child, "descriptor_event_seq": descriptors[0]["seq"],
                           "request_event_seq": request_event["seq"], "parent_delegation_event_seq": delegations[0]["seq"],
                           "parent_result_event_seq": delegation_result["seq"], "final_event_seq": final["seq"],
                           "read_mapping": "read(file_path,offset,limit) -> read_file(path); range evidence retained",
                           "neutrality": "unknown for natural-language request; fresh context verified separately" if rationale is None else "request declaration retained; not a semantic neutrality proof"}}


def validate_normalized(normalized, task, expected_ranges, evidence_root=None):
    """Reproject retained native logs; a normalized wrapper is not native evidence."""
    require(normalized.get('schema') == 'dsh-native-review-normalized-v1' and normalized.get('scope') == 'direct_material_review', 'packet calibration cannot enter direct-source sample')
    provenance=normalized.get('provenance',{})
    resolved={}
    relative=provenance.get('path_basis') == 'evidence_root'
    require(not relative or evidence_root is not None, 'relative native provenance requires evidence_root')
    for key in ('parent_native_jsonl','child_native_jsonl'):
        value=provenance.get(key)
        require(isinstance(value,str) and value, 'complete native session provenance missing: '+key)
        if relative:
            root=Path(evidence_root).resolve()
            require(not ntpath.isabs(value) and not Path(value).is_absolute() and '..' not in Path(value.replace('\\','/')).parts, 'native provenance must stay relative to evidence root')
            path=(root/value).resolve()
            require(path.is_relative_to(root), 'native provenance escapes evidence root')
        else:
            path=Path(value)
        require(path.is_file(), 'complete native session provenance missing: '+key)
        resolved[key]=path
    materials=normalized.get('request',{}).get('materials')
    require(isinstance(materials,list), 'normalized request materials missing')
    ranges=normalized.get('required_ranges')
    require(isinstance(ranges,dict), 'normalized direct-source required ranges missing')
    actual=export_review(resolved['parent_native_jsonl'],resolved['child_native_jsonl'],materials,normalized.get('neutral_material'),ranges,evidence_root if relative else None)
    require(actual['scope']=='direct_material_review', 'packet calibration cannot enter direct-source sample')
    require(actual['result']['conclusion']=='pass' and actual['result']['red_flags']==[], 'native independent review is not an unflagged pass')
    for key in ('session_id','parent_session_id','request','result','read_coverage'):
        require(normalized.get(key)==actual[key], 'normalized projection differs from native logs: '+key)
    for key in ('task_id','revision'):
        require(actual['request'][key]==task[key], 'native review belongs to a different task/revision')
    cwd=actual['provenance']['child_header']['cwd']
    observed={canonical(p,cwd):v for p,v in actual['read_coverage'].items()}
    required={canonical(p,cwd):normalize_ranges(v) for p,v in expected_ranges.items()}
    neutral=actual.get('neutral_material')
    extra={canonical(neutral,cwd)} if neutral else set()
    require(set(observed)==set(required)|extra, 'native direct review material paths differ from task inputs')
    for path,intervals in required.items():
        evidence=observed[path]
        needed=[[1,evidence['total_lines']]] if intervals is None else intervals
        for start,end in needed:
            require(any(lo<=start<=end<=hi for lo,hi in evidence['observed_ranges']), 'native reads do not cover task source ranges')
    return actual


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parent-log", required=True)
    parser.add_argument("--child-log", required=True)
    parser.add_argument("--material", action="append", required=True)
    parser.add_argument("--neutral-material")
    parser.add_argument("--ranges", help="JSON path -> required inclusive intervals; null means complete file")
    parser.add_argument("--evidence-root", required=True, help="Root containing both native logs; stored provenance paths are relative to this root")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = export_review(args.parent_log, args.child_log, args.material, args.neutral_material,
                           json.loads(Path(args.ranges).read_text(encoding="utf-8-sig")) if args.ranges else None, args.evidence_root)
    with Path(args.output).open("x", encoding="utf-8") as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(json.dumps({"output": str(Path(args.output).resolve()), "session_id": result["session_id"],
                      "conclusion": result["result"]["conclusion"], "scope": result["scope"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
