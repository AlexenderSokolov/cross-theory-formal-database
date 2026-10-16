"""Assemble reviewed revision-v2 jobs without content fingerprints or byte comparison.

Inputs are explicit task/source/review records. Outputs belong to one fresh job
revision. This module deliberately does not import the legacy validation chain.
"""
from __future__ import annotations

import argparse
import copy
from collections import Counter
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import prepared_focused as focused
import shared_works as shared

POLICY = "reviewed-revision-v2"
MATERIAL_BASIS = "author_material_collection"
NATIVE_FORMAT = "native_lean"
NATIVE_ORIGIN = "author_native_lean"
NATIVE_STATUS = "verified_native_author_proof"
ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,79}\Z")
REVISION = re.compile(r"r[0-9]{3,}\Z")
TASK_FIELDS = (
    "task_id", "problem_id", "revision", "source_id", "source_version",
    "claim_key", "title", "authors", "route", "source_url", "license",
    "statement_spans", "proof_spans", "context_spans", "standard_prerequisites",
    "core_obligations", "proof_roadmap", "difficulty_level", "difficulty_reason",
    "dedup", "review_paths", "assembly", "status",
)
SPAN_FIELDS = ("path", "start_line", "end_line", "label")
REVIEW_BINDING = ("task_id", "revision", "source_id", "source_version", "claim_key",
                  "statement_spans", "proof_spans", "context_spans")
UNIQUE_DECISIONS = {"unique", "unique_within_reviewed_scope", "focused_semantic_uniqueness_supported"}
RESOLVED = {"resolved", "disclosed_nonblocking", "accepted_source_typo"}
CONFIG_FIELDS = ("task_id", "revision", "selected_by", "source_id", "source_version", "claim_key",
                 "title", "authors", "route", "source_url", "license", "statement_spans", "proof_spans", "context_spans",
                 "standard_prerequisites", "core_obligations", "proof_roadmap", "difficulty_level", "difficulty_reason",
                 "dedup", "assembly", "editorial_scope", "source_title", "work", "retrieved_at")


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    # Same-directory replacement preserves the prior parseable state if writing
    # or replacement is interrupted. Failed temporary files remain evidence.
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="\n", dir=path.parent,
                                     prefix="." + path.name + ".", suffix=".tmp", delete=False) as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
        temporary = stream.name
    os.replace(temporary, path)


def task_config(task):
    """Explicit review/approval metadata; never author source or assembled text.

    IDs assigned later, review-file locations and workflow status are excluded.
    Root's approved task JSON separately binds the final formal problem ID.
    """
    result = {key: copy.deepcopy(task.get(key)) for key in CONFIG_FIELDS}
    if task.get("material_format") == NATIVE_FORMAT:
        result.update(material_format=NATIVE_FORMAT, native_material=copy.deepcopy(task.get("native_material")))
    result["selected_by"] = task.get("selected_by", task.get("selector_id"))
    if task.get("review_protocol") == focused.PROTOCOL:
        result.update({k: copy.deepcopy(task.get(k)) for k in focused.EXTRA_CONFIG})
    return result


def scientific_scope(config):
    scope = copy.deepcopy(config)
    assembly = scope.get("assembly") or {}
    # Source body roles, prerequisite-bearing preamble locators and scientific
    # editorial text remain binding. File destinations, packages and document
    # presentation may reuse an applicable review with an explicit root note.
    scope["assembly"] = {key: copy.deepcopy(assembly.get(key)) for key in
                         ("preamble_spans", "body_spans", "editorial_note", "editorial_notes", "external_references")}
    return scope


def require_review_config(task, record):
    current, approved = task_config(task), record.get("approved_task_config")
    require(isinstance(approved, dict) and set(approved) == set(current), "review needs approved_task_config metadata snapshot")
    if approved == current:
        return
    require(scientific_scope(approved) == scientific_scope(current), "review approved scientific scope differs from current task configuration")
    reuse = record.get("scope_reuse", {})
    require(isinstance(reuse, dict) and reuse.get("kind") == "mechanical_configuration_only" and
            all(nonempty(reuse.get(key)) for key in ("confirmed_by", "source_review", "reason", "confirmed_at")),
            "mechanical configuration change needs an explicit applicable-review reuse record")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def relative_path(root, value, *, existing=False):
    require(nonempty(value), "relative path required")
    raw = Path(value)
    require(not raw.is_absolute() and ".." not in raw.parts, "path must be relative and stay in its root: " + value)
    path = (Path(root) / raw).resolve()
    require(path.is_relative_to(Path(root).resolve()), "path escapes its root: " + value)
    require(not (Path(root) / raw).is_symlink(), "symlink inputs/outputs are unsupported: " + value)
    if existing:
        require(path.is_file(), "required file missing: " + str(path))
    return path


def normalized_span(span):
    require(isinstance(span, dict), "span must be an object")
    require(all(k in span for k in SPAN_FIELDS), "span requires path/start_line/end_line/label")
    require(nonempty(span["path"]) and nonempty(span["label"]), "span path and original label required")
    a, b = span["start_line"], span["end_line"]
    require(type(a) is int and type(b) is int and 1 <= a <= b, "invalid source line interval")
    return {"path": Path(span["path"]).as_posix(), "start_line": a, "end_line": b, "label": span["label"]}


def unresolved_issues(record):
    issues = record.get("issues", [])
    require(isinstance(issues, list), "issues must be a list")
    return [x for x in issues if not isinstance(x, dict) or
            not (x.get("resolved") is True or x.get("status") in RESOLVED)]


def review_records(task, records):
    selector = task.get("selected_by", task.get("selector_id"))
    require(nonempty(selector), "selected_by is required to establish reviewer independence")
    is_focused = task.get("review_protocol") == focused.PROTOCOL
    valid = []
    for record in records:
        require(record.get("schema_version") == 2, "review schema_version must be 2")
        require_review_config(task, record)
        if is_focused:
            focused.validate_review(task, record)
        else:
            require(record.get("review_protocol") is None, "legacy task cannot reuse focused review")
        for key in REVIEW_BINDING:
            expected, actual = task[key], record.get(key)
            if key.endswith("_spans"):
                require(isinstance(actual, list), "review span list missing: " + key)
                expected = [normalized_span(s) for s in expected]
                actual = [normalized_span(s) for s in actual]
            require(actual == expected, "review belongs to another task/revision/claim/span: " + key)
        require(record.get("verdict") == task["difficulty_level"], "review verdict does not approve this difficulty")
        require(not unresolved_issues(record), "review has unresolved issues")
        complete = record.get("proof_completeness")
        require(complete is True or isinstance(complete, dict) and complete.get("status") == "complete",
                "review must explicitly confirm complete proof")
        for key in ("reviewer_id", "reason", "core_assessment", "prerequisite_assessment", "reviewed_at"):
            require(nonempty(record.get(key)), "substantive review field missing: " + key)
        require(bool(record.get("source_authorship")), "source authorship assessment missing")
        external = task["assembly"].get("external_references", [])
        if external:
            approved = record.get("non_load_bearing_references", [])
            require(isinstance(approved, list) and all(x["label"] in approved for x in external),
                    "review must explicitly approve each non-load-bearing source reference")
        who = record["reviewer_id"].strip().casefold()
        if not is_focused:
            require(who != selector.strip().casefold(), "reviewer is the initial selector")
        valid.append(who)
    needed = 2 if task["difficulty_level"] == "H3" and not is_focused else 1
    require(len(set(valid)) >= needed, f"{task['difficulty_level']} needs {needed} independent reviewer(s)")
    return records


def validate_native_record(task, *, material_only=False):
    require(task.get("material_format") == NATIVE_FORMAT, "native task format missing")
    require(task.get("schema_version") == 2 and task.get("status") == "ready_for_assembly", "native task must be ready_for_assembly")
    require(ID.fullmatch(str(task.get("task_id", ""))) and REVISION.fullmatch(str(task.get("revision", ""))), "native task/revision missing")
    require(material_only or str(task.get("problem_id", "")).isdecimal(), "parent-assigned native problem_id required")
    for key in ("source_id", "source_version", "claim_key", "title", "source_url", "difficulty_reason"):
        require(nonempty(task.get(key)), "native task field missing: " + key)
    require(task["source_version"].lower() != "latest" and task.get("difficulty_level") in ("H2", "H3"), "fixed native source/H required")
    require(isinstance(task.get("authors"), list) and task["authors"] and all(nonempty(v) for v in task["authors"]), "native authors missing")
    for key in ("statement_spans", "proof_spans", "context_spans"):
        require(isinstance(task.get(key), list) and (task[key] or key == "context_spans"), "native statement/proof/context locators required")
        for span in task[key]:
            normalized_span(span)
    dedup = task.get("dedup", {})
    require(dedup.get("decision", dedup.get("conclusion")) in UNIQUE_DECISIONS and nonempty(dedup.get("scope")) and
            any(isinstance(dedup.get(k), list) for k in ("compared", "compared_ids", "compared_claims")), "native finite semantic decision missing")
    lic = task.get("license", {})
    require(all(nonempty(lic.get(k)) for k in ("name", "evidence_path", "version_url")), "native rights observation missing")
    native = task.get("native_material", {})
    for key in ("root", "module_root", "toolchain", "toolchain_file", "build_status", "author_completion_status"):
        require(nonempty(native.get(key)), "native material field missing: " + key)
    require(native["author_completion_status"] == "complete_author_material_retained",
            "native ready requires complete retained author proof material; keep incomplete source internally")
    for key in ("files", "entry_files", "lock_files", "declarations"):
        require(isinstance(native.get(key), list) and native[key], "native material list missing: " + key)
    require(len(set(native["files"])) == len(native["files"]), "duplicate native file")
    require(isinstance(native.get("external_imports"), list) and isinstance(native.get("external_dependencies"), list), "native external dependency references missing")
    for dep in native["external_dependencies"]:
        require(all(nonempty(dep.get(k)) for k in ("name", "url", "revision")) and dep["revision"].lower() != "latest", "external dependency must be pinned")
    require(not native["external_imports"] or native["external_dependencies"], "external imports need pinned dependency references")
    return task


def lean_import_text(text):
    """Expose import syntax outside nested/line comments and string literals."""
    active, depth, quoted, escaped, line_comment = [], 0, False, False, False
    index = 0
    while index < len(text):
        char, pair = text[index], text[index:index + 2]
        if line_comment:
            active.append("\n" if char == "\n" else " ")
            line_comment = char != "\n"
        elif depth:
            if pair in ("/-", "-/"):
                depth += 1 if pair == "/-" else -1
                active.extend("  "); index += 1
            else:
                active.append("\n" if char == "\n" else " ")
        elif quoted:
            active.append("\n" if char == "\n" else " ")
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
        elif pair in ("/-", "--"):
            depth, line_comment = (1, False) if pair == "/-" else (0, True)
            active.extend("  "); index += 1
        elif char == '"':
            quoted = True; active.append(" ")
        else:
            active.append(char)
        index += 1
    return "".join(active)


def native_packet(root, task):
    """Check declared author files/imports and locations; never certify mathematics."""
    native = task["native_material"]
    source = relative_path(root, native["root"])
    require(source.is_dir(), "native source root missing")
    files = {name: relative_path(source, name, existing=True) for name in native["files"]}
    require(all(path.is_file() and not path.is_symlink() for path in files.values()), "native packet requires regular source files")
    for name in native["entry_files"] + native["lock_files"] + [native["toolchain_file"]]:
        require(name in files, "native entry/toolchain/lock not retained: " + name)
    require(any(declaration.get("path") == native["entry_files"][0] for declaration in native["declarations"]),
            "native primary entry must contain the actual principal declaration")
    require(native["toolchain"] in files[native["toolchain_file"]].read_text(encoding="utf-8-sig"), "native toolchain reference differs")
    locks = "\n".join(files[name].read_text(encoding="utf-8-sig") for name in native["lock_files"])
    require(all(dep["revision"] in locks for dep in native["external_dependencies"]), "native external pin missing from retained lock files")
    for guide in native.get("reading_guides", []):
        require(guide.get("role") == "guide_only" and guide.get("path") in files, "native reading guide must be separately labelled and retained")
    module_root = Path(native["module_root"])
    require(not module_root.is_absolute() and ".." not in module_root.parts, "native module root must be relative")
    for name, path in files.items():
        if path.suffix != ".lean":
            continue
        # Remove Lean comments only to locate import declarations, not proofs.
        text = lean_import_text(path.read_text(encoding="utf-8-sig"))
        for line in text.splitlines():
            line = line.strip()
            declaration = re.match(r"(?:(?:public|meta)\s+)*import\s+(.+)$", line)
            if not declaration:
                continue
            for module in declaration.group(1).split():
                local = (module_root / (module.replace(".", "/") + ".lean")).as_posix()
                default = (module_root / module.replace(".", "/") / "default.lean").as_posix()
                require(local in files or default in files or module in native["external_imports"], "native import not retained or externally referenced: " + module)
    for key in ("statement_spans", "proof_spans", "context_spans"):
        for span in task[key]:
            s = normalized_span(span)
            require(s["path"] in files, "native source span not retained: " + s["path"])
            lines = files[s["path"]].read_text(encoding="utf-8-sig").splitlines()
            require(s["end_line"] <= len(lines), "native source span exceeds file")
            if key == "proof_spans":
                require(any(line.strip() and not line.lstrip().startswith("--") and
                            not re.match(r"(?:(?:public|meta)\s+)*import(?:\s|$)", line.lstrip())
                            for line in lines[s["start_line"]-1:s["end_line"]]), "native proof cannot be an import-only wrapper")
    for declaration in native["declarations"]:
        s = normalized_span(declaration)
        require(nonempty(declaration.get("name")) and s["path"] in files, "native principal declaration missing")
        lines = files[s["path"]].read_text(encoding="utf-8-sig").splitlines()
        require(s["end_line"] <= len(lines) and declaration["name"] in "\n".join(lines[s["start_line"]-1:s["end_line"]]), "native principal declaration not at recorded location")
    return source, files


def validate_native_task(task, task_path, task_root, *, material_only=False):
    task.setdefault("review_paths", [])
    if material_only and task.get("problem_id") is None:
        task["problem_id"] = task.get("local_material_id", task["task_id"])
    validate_native_record(task, material_only=material_only)
    source, files = native_packet(task_root, task)
    license_path = relative_path(task_root, task["license"]["evidence_path"], existing=True)
    return {"task": task, "task_path": task_path, "task_root": task_root, "native_root": source, "native_files": files,
            "license_path": license_path, "license_evidence": load(license_path)}


def assemble_native(checked, output_root):
    task = copy.deepcopy(checked["task"])
    job = Path(output_root).resolve() / task["task_id"] / task["revision"]
    require(not job.exists() and not job.is_relative_to(checked["task_root"]), "fresh separate native output required")
    package = job / ("package-root-" + task["revision"])
    native = copy.deepcopy(task["native_material"])
    native["root"] = "native-source"
    source_files = []
    for name, src in checked["native_files"].items():
        dst = relative_path(package, "native-source/" + name)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        source_files.append({"path": "native-source/" + name, "original_path": name, "source_id": task["source_id"], "source_version": task["source_version"]})
    task["native_material"] = native
    task["license"]["evidence_path"] = "licenses/evidence.json"
    task["preparation_basis"] = MATERIAL_BASIS
    snapshot = "prepared-task.json"
    save(package / snapshot, task)
    save(package / "licenses/evidence.json", checked["license_evidence"])
    notice = package / "licenses/NOTICE.txt"
    notice.write_text("; ".join(task["authors"]) + "\n" + task["source_version"] + "\n" + task["source_url"] + "\n" + task["license"]["name"] + "\n", encoding="utf-8")
    row = {key: copy.deepcopy(task[key]) for key in ("problem_id", "task_id", "revision", "source_id", "source_version", "source_url", "title", "authors", "claim_key", "difficulty_level", "difficulty_reason", "proof_spans")}
    row.update(policy=POLICY, material_format=NATIVE_FORMAT, native_material=native, author="; ".join(task["authors"]),
               work=task.get("source_title", task.get("work", task["source_id"])), retrieved_at=task.get("retrieved_at", ""),
               primary=task["statement_spans"], contexts=task["context_spans"], item_path="native-source/" + native["entry_files"][0],
               compile_receipt=None, license=task["license"]["name"], license_path="licenses/NOTICE.txt", license_evidence_path="licenses/evidence.json",
               asset_dependencies=[], source_files=source_files, origin_class=NATIVE_ORIGIN, status=NATIVE_STATUS,
               review_state=MATERIAL_BASIS, preparation_basis=MATERIAL_BASIS, dedup_state="unique_within_reviewed_scope", publication_commit=None, tex_sha256=None)
    save(package / "manifest.json", {"schema_version": 2, "policy": POLICY, "verified_count": 1, "items": [row]})
    state = {"schema_version": 2, "policy": POLICY, **binding(task), "material_format": NATIVE_FORMAT,
             "preparation_basis": MATERIAL_BASIS, "status": "material_ready", "package": package.name, "task_snapshot": snapshot}
    save(job / "job-state.json", state)
    create_database(package, [row], package / "corpus.sqlite")
    return dict(verify_native_job(job, state, require_ready=False), job=str(job))


def verify_native_job(job, state, *, require_ready=True):
    require(state.get("policy") == POLICY and state.get("preparation_basis") == MATERIAL_BASIS, "native material policy mismatch")
    package = relative_path(job, state["package"])
    require(package.is_dir(), "native package directory missing")
    task = load(relative_path(package, state["task_snapshot"], existing=True))
    validate_native_record(task, material_only=True)
    manifest = load(package / "manifest.json")
    require(len(manifest["items"]) == manifest.get("verified_count") == 1, "one native author proof group required")
    row = manifest["items"][0]
    require(binding(task) == binding(row) == binding(state), "native job/task/item identity mismatch")
    require(row.get("origin_class") == NATIVE_ORIGIN and row.get("status") == NATIVE_STATUS and row.get("material_format") == NATIVE_FORMAT,
            "native author proof origin/status mismatch")
    require(row["native_material"] == task["native_material"] and row["primary"] == task["statement_spans"] and row["proof_spans"] == task["proof_spans"] and row["contexts"] == task["context_spans"], "native source locations differ")
    require(row["difficulty_level"] == task["difficulty_level"] and row["difficulty_reason"] == task["difficulty_reason"] and row["authors"] == task["authors"], "native H/author metadata mismatch")
    require(row["author"] == "; ".join(task["authors"]) and all(row[key] == task[key] for key in ("title", "source_url")) and
            row.get("preparation_basis") == row.get("review_state") == MATERIAL_BASIS and row.get("dedup_state") == "unique_within_reviewed_scope",
            "native source/current material metadata mismatch")
    native_packet(package, task)
    expected_sources = {"native-source/" + name for name in task["native_material"]["files"]}
    require({source["path"] for source in row["source_files"]} == expected_sources and
            all(source["source_id"] == task["source_id"] and source["source_version"] == task["source_version"] for source in row["source_files"]),
            "native copied source manifest differs")
    require(row["item_path"] == task["native_material"]["root"] + "/" + task["native_material"]["entry_files"][0] and row.get("compile_receipt") is None,
            "native primary entry/TeX receipt mismatch")
    evidence = load(relative_path(package, row["license_evidence_path"], existing=True))
    require(evidence == load(relative_path(package, task["license"]["evidence_path"], existing=True)), "native rights binding mismatch")
    for key in ("source_id", "source_version"):
        require(key not in evidence or evidence[key] == task[key], "native rights source/version mismatch")
    relative_path(package, row["license_path"], existing=True)
    sql = validate_database(package / state.get("material_database", "corpus.sqlite"), [row])
    return {"schema_version": 2, "policy": POLICY, **binding(task), "material_format": NATIVE_FORMAT,
            "preparation_basis": MATERIAL_BASIS, "status": "verified_local_prepared_job", "editable_qualified_count": 1,
            "package_item_count": 1, "errors": [], "sql": sql, "public_redistribution_supported": evidence.get("status") == "supported" and evidence.get("redistribution_allowed") is not False,
            "build_status": row["native_material"]["build_status"], "qualification_basis": MATERIAL_BASIS}


def adopt_native_material(job, output_root, reservations_path):
    verify_job(job, require_ready=False)
    original = load(job / "job-state.json")
    package = job / original["package"]
    task = load(package / original["task_snapshot"])
    fields = ("task_id", "revision", "source_id", "source_version", "claim_key")
    matches = [entry for entry in load(reservations_path)["entries"] if all(entry.get(key) == task[key] for key in fields)]
    require(len(matches) == 1 and str(matches[0]["problem_id"]).isdecimal(), "one matching formal native ID reservation required")
    ident = matches[0]["problem_id"]
    target = Path(output_root).resolve() / task["task_id"] / task["revision"]
    require(not target.is_relative_to(job) and not job.is_relative_to(target), "native adoption must preserve source job")
    if target.exists():
        state = load(target / "job-state.json")
        require(state.get("adopted_from") == str(job) and state.get("problem_id") == ident, "existing native adoption conflicts")
        prior_task = load(target / state["package"] / state["task_snapshot"])
        require(task_config(prior_task) == task_config(task), "native adoption task metadata changed")
        report = verify_job(target)
        final = target / ("final-item-root-" + task["revision"] + ".json")
        if not final.exists():
            save(final, report)
        return dict(report, job=str(target), resumed=True)
    shutil.copytree(job, target)
    state = dict(original, problem_id=ident, adopted_from=str(job), original_material_binding=binding(task))
    task["problem_id"] = ident
    manifest = load(package / "manifest.json")
    row = manifest["items"][0]
    row["problem_id"] = ident
    out = target / state["package"]
    save(target / "job-state.json", state)
    save(out / state["task_snapshot"], task)
    save(out / "manifest.json", manifest)
    state["material_database"] = "adopted-corpus.sqlite"
    save(target / "job-state.json", state)
    create_database(out, [row], out / state["material_database"])
    report = verify_job(target)
    save(target / ("final-item-root-" + task["revision"] + ".json"), report)
    return dict(report, job=str(target), resumed=False)


def validate_record(task, records, *, material_only=False):
    if task.get("material_format") == NATIVE_FORMAT:
        return validate_native_record(task, material_only=material_only)
    require(isinstance(task, dict) and task.get("schema_version") == 2, "task schema_version must be 2")
    require(material_only or task.get("review_protocol") in (None, focused.PROTOCOL), "unknown review protocol")
    require(all(k in task for k in TASK_FIELDS), "task fields missing: " + ", ".join(k for k in TASK_FIELDS if k not in task))
    require(ID.fullmatch(str(task["task_id"])), "invalid readable task_id")
    require(REVISION.fullmatch(str(task["revision"])), "revision must have form r001")
    require(material_only or (isinstance(task["problem_id"], str) and task["problem_id"].isdigit()), "parent-assigned problem_id required")
    require(task["status"] == "ready_for_assembly", "only ready_for_assembly tasks can enter this path")
    require(task["difficulty_level"] in ("H2", "H3"), "difficulty must be H2 or H3")
    for key in ("source_id", "source_version", "claim_key", "title", "route", "source_url", "difficulty_reason"):
        require(nonempty(task[key]), "nonempty task field required: " + key)
    require(task["source_version"].strip().lower() != "latest", "a fixed source version is required")
    require(isinstance(task["authors"], list) and task["authors"] and all(nonempty(x) for x in task["authors"]),
            "complete author list required")
    for key in ("statement_spans", "proof_spans", "context_spans", "standard_prerequisites", "core_obligations", "proof_roadmap", "review_paths"):
        require(isinstance(task[key], list), key + " must be a list")
    require(task["statement_spans"] and task["proof_spans"], "counted statement and complete proof spans required")
    require(task["core_obligations"] and (material_only or task["proof_roadmap"]), "specific core obligations and proof roadmap required")
    require(not unresolved_issues(task), "task has unresolved issues")
    d = task["dedup"]
    require(isinstance(d, dict), "dedup must be an object")
    decision = d.get("conclusion", d.get("decision", d.get("status")))
    require(decision in UNIQUE_DECISIONS and nonempty(d.get("scope")), "semantic uniqueness decision and scope required")
    require(any(isinstance(d.get(k), list) for k in ("compared", "compared_ids", "compared_claims", "compared_counted_prior_ids")),
            "dedup comparison objects required")
    lic = task["license"]
    require(isinstance(lic, dict) and all(nonempty(lic.get(k)) for k in ("name", "evidence_path", "version_url")),
            "license requires name/evidence_path/version_url")
    assembly = task["assembly"]
    require(isinstance(assembly, dict) and assembly.get("engine") == "xelatex" and assembly.get("allow_shell_escape") is False,
            "assembly requires xelatex with shell escape disabled")
    for key in ("preamble_spans", "body_spans", "asset_paths", "bibliography_paths"):
        require(isinstance(assembly.get(key), list), "assembly list missing: " + key)
    require(assembly.get("bibliography_backend", "bibtex") in ("none", "bibtex", "biber"), "unsupported bibliography backend")
    require(assembly.get("document_class", "amsart") in ("article", "amsart"), "supported wrapper classes: article, amsart")
    require(isinstance(assembly.get("extra_packages", []), list) and
            all(isinstance(x, str) and re.fullmatch(r"[A-Za-z0-9_-]+", x) for x in assembly.get("extra_packages", [])),
            "extra_packages must name installed TeX packages")
    require(isinstance(assembly.get("editorial_notes", []), list) and
            all(nonempty(x) for x in assembly.get("editorial_notes", [])), "editorial_notes must be a list of separate prose notes")
    counters = assembly.get("initial_counters", {})
    require(isinstance(counters, dict) and all(re.fullmatch(r"[A-Za-z][A-Za-z0-9]*", name) and type(value) is int and value >= 0
                                              for name, value in counters.items()), "initial_counters requires names and nonnegative integers")
    external = assembly.get("external_references", [])
    require(isinstance(external, list), "external_references must be a list")
    reference_labels = []
    for reference in external:
        require(isinstance(reference, dict) and reference.get("non_load_bearing") is True and nonempty(reference.get("reason")),
                "external reference requires a reviewed non-load-bearing reason")
        # Native TeX labels can contain ordinary spaces (e.g. the JEP317
        # label "thm:fact into k parts") and slashes (e.g. the JEP135 labels
        # "Prop:A/C", "Rec:A/C", "it:A/C-d"); retain those author identifiers.
        # The label is only embedded in \newlabel{...} keys, where both are legal.
        # 2026-10-14 CONTROL 8.8.100 (Chief-approved, lane-x4 sigma case;
        # originally drafted as 8.8.95, renumbered on landing):
        # parentheses and the arrow ">" are also legal in \newlabel keys
        # (author labels "prop: grading of Jac(f)", "thm:ccn->2ps").
        # 2026-10-14 CONTROL (be) ignition (Chief-approved, lane-x4 evidence
        # pack): "=" and "+" are legal -- external-label layer only,
        # claim_key layer untouched; downstream-splitting audit found no
        # splitting semantics; unparks univ-fin / S5fmp / 029-tw-refl and
        # the sigma-2023-023 "+" park (labels "eq DC+", "impliSH2=PHI").
        # 2026-10-14 CONTROL (bg) merge ruling (Chief-approved): "*" joins
        # the same classes in one edit (label "eq:PgLambdaT*Mcoord");
        # tri-char single regression run, no second window.
        # 2026-10-14 CONTROL (bh) expansion (Chief-approved, lane-s12 jep.153
        # evidence pack): "!" and "&" join the same classes in one edit --
        # external-label layer only, claim_key layer untouched; unparks
        # L32301 ("thm:biv_A1minus&Wittcoh") and L32303 ("rem:f_! constructibles").
        # 2026-10-14 CONTROL (bi) fifth expansion (Chief-approved): "^" joins
        # the same classes; evidence = lane-x4 full-corpus scan of 32513
        # external refs, single hit "prop:Ex^*! pro-etale" (L32304), zero
        # collateral; external-label layer only, claim_key layer untouched.
        # 2026-10-15 CONTROL 2d01901b ruling (duty manager, lane-s12 jep.241
        # evidence): the comma joins the same classes.  Evidence = the three
        # parked lane-s12 cards; the one truly failing label was
        # "theo-specialcaseSL(n,R)" -- the comma was the only character outside
        # the charset (spaces and leading dashes were already allowed), so a
        # slugified key was not needed and would have broken the \ref in the
        # delivered body, which uses the original key.  External-label layer
        # only, claim_key layer untouched, \newlabel accepts the comma.
        # 2026-10-15 17:4x merged widening (Chief consolidation order, one patch
        # not three): the apostrophe, the open bracket and the close bracket
        # join the same classes.  Evidence (three faces, all author-verbatim
        # labels in the pinned sources, cards neither rewriting nor forging
        # them): "eqn:Young's-rule" + "sec:Saliola'smap" (alco-412 pair) and
        # "lem:det(X_0/[n])" (upper-interval-stab-rep).  Same shape as the
        # earlier comma/star/etc. widenings: pure character-set increment,
        # external-label layer only, claim_key layer untouched, \newlabel
        # accepts all three, every pre-existing label keeps its verdict.
        require(re.fullmatch(r"[A-Za-z0-9:_.\-/()>+=*!&^$,'\[\]][A-Za-z0-9:_. \-/()>+=*!&^$,'\[\]]*", str(reference.get("label", ""))), "invalid external label")
        require(str(reference.get("label", "")).count("$") % 2 == 0, "unbalanced $ in external label")
        require(str(reference.get("kind", "")).lower() in ("lemma", "theorem", "proposition", "corollary", "definition", "equation", "section", "remark", "exercise") + (("reference",) if material_only else ()),
                "external reference kind required")
        require(re.fullmatch(r"[A-Za-z0-9.()-]+", str(reference.get("number", ""))), "original reference number required")
        normalized_span(reference.get("source_span"))
        reference_labels.append(reference["label"])
    require(len(reference_labels) == len(set(reference_labels)), "duplicate external reference label")
    for name in ("statement_spans", "proof_spans", "context_spans"):
        for span in task[name]:
            normalized_span(span)
    body_by_role = {role: [] for role in ("statement", "proof", "context")}
    for span in assembly["body_spans"]:
        require(span.get("role") in body_by_role, "assembly body role must be statement/proof/context")
        body_by_role[span["role"]].append(normalized_span(span))
    for role, spans in body_by_role.items():
        # This compares declared locator metadata, never author/assembled text.
        require(spans == [normalized_span(s) for s in task[role + "_spans"]], "assembly differs from reviewed " + role + " locators")
    if not material_only:
        review_records(task, records)


def copied_asset(spec, kind):
    if isinstance(spec, str):
        return {"path": spec, "target": "items/" + Path(spec).name, "kind": kind}
    require(isinstance(spec, dict) and nonempty(spec.get("path")) and nonempty(spec.get("target")),
            "asset requires a relative path or {path,target}")
    return {"path": spec["path"], "target": spec["target"], "kind": kind}


def validate_task(task_path, task_root, *, material_only=False):
    task_root = Path(task_root).resolve()
    task_path = Path(task_path).resolve()
    require(task_path.is_relative_to(task_root), "task JSON must be inside task-root")
    task = load(task_path)
    if task.get("material_format") == NATIVE_FORMAT:
        return validate_native_task(task, task_path, task_root, material_only=material_only)
    if material_only:
        task.setdefault("review_paths", [])
        task.setdefault("proof_roadmap", [])
    require(isinstance(task.get("review_paths"), list), "review_paths must be a list")
    records = [] if material_only else [load(relative_path(task_root, p, existing=True)) for p in task["review_paths"]]
    if material_only and task.get("problem_id") is None:
        task["problem_id"] = task.get("local_material_id", task["task_id"])  # Local material name, never a reserved public ID.
    validate_record(task, records, material_only=material_only)
    sources = {}
    all_spans = task["assembly"]["preamble_spans"] + task["assembly"]["body_spans"]
    all_spans += [x["source_span"] for x in task["assembly"].get("external_references", [])]
    for span in all_spans:
        s = normalized_span(span)
        if s["path"] not in sources:
            path = relative_path(task_root, s["path"], existing=True)
            sources[s["path"]] = {"path": path, "lines": path.read_text(encoding="utf-8-sig").splitlines()}
        require(s["end_line"] <= len(sources[s["path"]]["lines"]), "source span exceeds available lines: " + s["path"])
    assets = []
    targets = set()
    for kind, key in (("asset", "asset_paths"), ("bibliography", "bibliography_paths")):
        for raw in task["assembly"][key]:
            spec = copied_asset(raw, kind)
            spec["source"] = relative_path(task_root, spec["path"], existing=True)
            require(Path(spec["target"]).parts[:1] == ("items",), "asset target must be inside package/items")
            relative_path(task_root, spec["target"])
            require(spec["target"] not in targets, "duplicate asset target")
            targets.add(spec["target"])
            assets.append(spec)
    evidence_path = relative_path(task_root, task["license"]["evidence_path"], existing=True)
    if material_only:
        evidence = load(evidence_path) if evidence_path.suffix.lower() == ".json" else {"source_notice": evidence_path.read_text(encoding="utf-8-sig")}
    else:
        require(evidence_path.suffix.lower() == ".json", "public license evidence must be structured JSON")
        evidence = load(evidence_path)
        require(evidence.get("status") == "supported", "source license evidence is not supported")
        for key in ("source_id", "source_version"):
            if key in evidence:
                if key == "source_version" and form_equivalent(evidence[key], task[key], evidence_path):
                    continue
                require(evidence[key] == task[key], "license evidence belongs to another " + key)
    return {"task": task, "reviews": records, "sources": sources, "assets": assets,
            "license_evidence": evidence, "license_path": evidence_path, "task_path": task_path,
            "task_root": task_root}


def binding(task):
    return {k: task[k] for k in ("task_id", "problem_id", "revision", "source_id", "source_version", "claim_key") + (("review_protocol",) if task.get("review_protocol") else ())}


def tex_escape(value):
    substitutions = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#",
                     "_": r"\_", "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}
    return "".join(substitutions.get(c, c) for c in str(value).replace("\n", " ").replace("\r", " "))


def active_tex(text):
    return re.sub(r"(?<!\\)%[^\n]*", "", text)


def assemble(task_path, task_root, output_root, *, compile_now=True, material_only=False, refresh=False):
    checked = validate_task(task_path, task_root, material_only=material_only)
    task = checked["task"]
    if task.get("material_format") == NATIVE_FORMAT:
        return assemble_native(checked, output_root)
    root = Path(output_root).resolve()
    require(root != checked["task_root"], "output-root must be separate from the input root")
    job = root / task["task_id"] / task["revision"]
    # Source/review input locations are read-only even if output-root is under P.
    protected = [v["path"] for v in checked["sources"].values()] + [checked["task_path"], checked["license_path"]]
    protected += [relative_path(checked["task_root"], p, existing=True) for p in task["review_paths"]]
    protected += [asset["source"] for asset in checked["assets"]]
    require(not any(job.is_relative_to(p.parent) for p in protected), "job output would write inside an input directory")
    require(not job.exists() or (refresh and load(job / "job-state.json")["status"] == "needs_codex"), "existing successful job is preserved; only failed jobs can be refreshed")
    require(not (refresh and job.exists()),
            'preserve failed outputs; use compile-job --resume or a fresh explicit output root')
    job.mkdir(parents=True, exist_ok=refresh)
    revision, ident = task["revision"], task["problem_id"]
    package = job / ("package-root-" + revision)
    package.mkdir(exist_ok=refresh)
    for folder in ("items", "licenses", "receipts", "sources/" + ident):
        (package / folder).mkdir(parents=True, exist_ok=True)
    state = {"schema_version": 2, "policy": POLICY, **binding(task), "status": "assembling",
             "created_at": utc_now(), "package": package.name,
             "build_root": "build-root-" + revision, "receipt_root": "receipts-root-" + revision,
             "qa_root": "qa-root-" + revision, "task_snapshot": "sources/" + ident + "/prepared-task.json"}
    if material_only:
        state["material_only"] = True
    save(job / "job-state.json", state)
    try:
        save(package / state["task_snapshot"], task)
        save(package / ("sources/" + ident + "/content-review.json"),
             {"schema_version": 2, "policy": POLICY, **binding(task), "reviews": checked["reviews"], "dedup": task["dedup"]})
        source_map = []
        for i, (original, src) in enumerate(checked["sources"].items()):
            target = f"sources/{ident}/source-{i:02d}{src['path'].suffix or '.tex'}"
            shutil.copyfile(src["path"], package / target)
            source_map.append({"original_path": original, "path": target, "source_id": task["source_id"],
                               "source_version": task["source_version"]})
        OLP_SHORTHAND = (("!!^a{", "\\olup{"), ("!!^b{", "\\olup{"))
        def excerpt(span):
            s = normalized_span(span)
            text = "\n".join(checked["sources"][s["path"]]["lines"][s["start_line"] - 1:s["end_line"]]) + "\n"
            # The OLP active-! shorthand accents (!!^a{..}, !!^b{..}) cannot be typeset by xelatex;
            # the adapter layer implements that family as identity-through-\olup, so the swap is
            # semantics-preserving.  Keeps every other extraction path byte-identical.
            for pat, rep in OLP_SHORTHAND:
                text = text.replace(pat, rep)
            return text
        preamble = "".join(excerpt(s) for s in task["assembly"]["preamble_spans"])
        require(r"\begin{document}" not in active_tex(preamble), "preamble spans must end before begin document")
        extras = "".join("\\usepackage{" + name + "}\n" for name in task["assembly"].get("extra_packages", []))
        if not re.search(r"\\documentclass(?:\[[^]]*\])?\{", active_tex(preamble)):
            preamble = ("\\documentclass[10pt,a4paper]{" + task["assembly"].get("document_class", "amsart") + "}\n"
                        "\\usepackage{amsmath,amssymb,amsthm,graphicx}\n") + extras + preamble
        else:
            preamble += extras
        references = task["assembly"].get("external_references", [])
        if references and not re.search(r"\\usepackage(?:\[[^]]*\])?\{[^}]*\bcleveref\b", preamble):
            preamble += "\\usepackage{cleveref}\n"
        # Label metadata identifies the original-source pointer; no replacement
        # theorem or proof is manufactured in the delivered mathematical body.
        for i, reference in enumerate(references, 1):
            label, kind, number = reference["label"], reference["kind"], reference["number"]
            # 2026-10-15 CONTROL 8.8.193 (duty manager, Chief merged ruling for
            # the lane-s13/lane-s12 pointer cases): the pointer block name is the
            # label prefix (the text before the first colon) so it matches the
            # name the delivered body actually writes; prefix-less labels keep
            # the historical synthetic name.  Host probes t1/t5 (2026-10-15,
            # xelatex): cleveref takes the type from the @cref entry and accepts
            # either name without demanding a counter, so the rename is safe.
            # The real r001-r004 failure was initial_counters \setcounter on an
            # undeclared counter, resolved by the chain before \begin{document}.
            name = label.split(":", 1)[0] if ":" in label else ""
            if not name:
                name = "original" + kind
            preamble += "\\crefname{" + name + "}{original " + kind + "}{original " + kind + "s}\n"
            preamble += "\\Crefname{" + name + "}{Original " + kind + "}{Original " + kind + "s}\n"
            preamble += "\\makeatletter\n\\newlabel{" + label + "}{{" + number + "}{source}{}{sourcepointer-" + str(i) + "}{}}\n"
            preamble += "\\newlabel{" + label + "@cref}{{[" + name + "][0][]" + number + "}{[1][0][]source}{}{}{}}\n\\makeatother\n"
        out = preamble.splitlines()
        out += [r"\title{" + tex_escape(task["title"]) + "}",
                r"\author{" + tex_escape(", ".join(task["authors"])) + "}",
                r"\date{" + tex_escape(task["source_id"] + "; " + task["license"]["name"]) + "}",
                r"\begin{document}", r"\maketitle"]
        # 2026-10-15 CONTROL 8.8.193 (duty manager, Chief merged ruling):
        # initial_counters keys must resolve to a real counter before
        # \setcounter is emitted.  Resolution order: explicit
        # assembly.counter_map, then discovery in the card preamble (the key
        # is a counter itself, or a theorem environment whose declared parent
        # chain ends in one), then fail closed -- a bare \setcounter on an
        # undeclared name is exactly the lane-s12 alco-491 r001-r004 failure
        # ("No counter 'lemma' defined", host log l.99).  An environment
        # alias (\newtheorem{X}[Y]{..}) shares Y's counter and creates none,
        # which is why the alias shim alone never fixed it.
        declared_parents = {}
        own_counters = set()
        for m in re.finditer(r"\\newtheorem(\*?)\{([^}]+)\}(?:\[([^\]]+)\])?\{", preamble):
            if m.group(1):
                continue
            env_name = m.group(2).strip()
            parent = (m.group(3) or "").strip()
            if parent:
                declared_parents[env_name] = parent
            else:
                own_counters.add(env_name)
        own_counters.update(("section", "subsection", "subsubsection", "paragraph", "subparagraph",
                             "equation", "figure", "table", "footnote", "page", "enumi", "enumii", "enumiii", "enumiv"))
        counter_map = task["assembly"].get("counter_map")
        require(counter_map is None or isinstance(counter_map, dict), "counter_map must be an object")
        counter_map = counter_map or {}

        def resolve_counter(key, seen=None):
            key = str(key).strip()
            if key in counter_map:
                mapped = str(counter_map[key]).strip()
                require(mapped != key, "counter_map entry for " + key + " maps to itself")
                resolved = resolve_counter(mapped, set()) if mapped in counter_map else resolve_counter(mapped)
                require(resolved is not None, "counter_map maps " + key + " to undeclared counter " + mapped)
                return resolved
            if key in own_counters:
                return key
            if key in declared_parents:
                seen = set() if seen is None else seen
                require(key not in seen, "cyclic theorem counter alias at " + key)
                seen.add(key)
                return resolve_counter(declared_parents[key], seen)
            return None

        for counter_key, value in task["assembly"].get("initial_counters", {}).items():
            counter_name = resolve_counter(counter_key)
            require(counter_name is not None,
                    "initial_counters key " + str(counter_key) + " does not resolve to a declared counter; "
                    "declare the family in the card preamble or add assembly.counter_map")
            out.append(r"\setcounter{" + counter_name + "}{" + str(value) + "}")
        if task["assembly"].get("editorial_note"):
            out.append(r"\noindent\textit{Editorial scope.} " + tex_escape(task["assembly"]["editorial_note"]) + r"\par\medskip")
        for note in task["assembly"].get("editorial_notes", []):
            out.append(r"\noindent\textit{Editorial note.} " + tex_escape(note) + r"\par\medskip")
        scope = task.get("editorial_scope")
        if nonempty(scope):
            out.append(r"\noindent\textit{Editorial scope.} " + tex_escape(scope) + r"\par\medskip")
        if task["standard_prerequisites"]:
            out.append(r"\noindent\textit{Allowed standard prerequisites (editorial).}\begin{itemize}")
            for prerequisite in task["standard_prerequisites"]:
                if isinstance(prerequisite, dict):
                    prose = ". ".join(str(prerequisite[k]) for k in ("name", "statement", "source_reference", "use") if prerequisite.get(k))
                    require(bool(prose), "standard prerequisite needs a visible name/statement/source/use")
                else:
                    require(nonempty(prerequisite), "standard prerequisite must be text or an explicit object")
                    prose = prerequisite
                out.append(r"\item " + tex_escape(prose))
            out.append(r"\end{itemize}\medskip")
        for i, reference in enumerate(references, 1):
            s = reference["source_span"]
            out.append(r"\ifdefined\hypertarget\hypertarget{sourcepointer-" + str(i) + r"}{}\fi")
            note = ("Original " + reference["kind"] + " " + reference["number"] + ": " + s["path"] +
                    f", source lines {s['start_line']}--{s['end_line']}. " + reference["reason"])
            out.append(r"\noindent\textit{Source reference.} " + tex_escape(note) + r"\par\medskip")
        bodies = []
        for s in task["assembly"]["body_spans"]:
            start = len(out) + 1
            body = excerpt(s)
            require(not re.search(r"\\(?:begin|end)\{document\}", active_tex(body)), "body span contains document boundary")
            out.extend(body.splitlines())
            bodies.append({"role": s["role"], "source_span": normalized_span(s), "tex_lines": [start, len(out)]})
            out.append("")
        if task["assembly"].get("bibliography_command"):
            command = task["assembly"]["bibliography_command"]
            require(re.fullmatch(r"\\bibliographystyle\{[\w-]+\}\s*\\bibliography\{[\w,./-]+\}", command),
                    "bibliography_command must contain only bibliographystyle and bibliography")
            out.extend(command.splitlines())
        elif task["assembly"]["bibliography_paths"] and not re.search(r"\\(?:bibliography\{|begin\{thebibliography\})", active_tex("\n".join(out))):
            style = task["assembly"].get("bibliography_style", "plain")
            require(re.fullmatch(r"[\w-]+", style), "invalid bibliography style")
            names = [str(Path(a["target"]).relative_to("items").with_suffix("")).replace("\\", "/")
                     for a in checked["assets"] if a["kind"] == "bibliography" and Path(a["target"]).suffix.lower() == ".bib"]
            fragments = [a for a in checked["assets"] if a["kind"] == "bibliography" and Path(a["target"]).suffix.lower() in (".tex", ".bbl")]
            require(bool(names) != bool(fragments), "declare either .bib inputs or flattened .tex/.bbl bibliography fragments")
            if names:
                if task["assembly"].get("bibliography_backend") == "biber":
                    require("biblatex" in active_tex(preamble) and r"\addbibresource" in active_tex(preamble),
                            "biber tasks must provide original biblatex/addbibresource preamble")
                    if r"\printbibliography" not in active_tex("\n".join(out)):
                        out.append(r"\printbibliography")
                else:
                    out += [r"\bibliographystyle{" + style + "}", r"\bibliography{" + ",".join(names) + "}"]
            else:
                bibliography = "\n".join(a["source"].read_text(encoding="utf-8-sig") for a in fragments)
                require(not re.search(r"\\(?:begin|end)\{document\}", active_tex(bibliography)), "bibliography contains a document boundary")
                if r"\begin{thebibliography}" not in active_tex(bibliography):
                    out.append(r"\begin{thebibliography}{99}")
                    out.extend(bibliography.splitlines())
                    out.append(r"\end{thebibliography}")
                else:
                    out.extend(bibliography.splitlines())
        out.append(r"\end{document}")
        if re.search(r"[\u3400-\u9fff]", "\n".join(out)) and not re.search(r"\\usepackage(?:\[[^]]*\])?\{(?:ctex|xeCJK)\}", preamble):
            # Installed Fandol fonts render actual Chinese notes/authors. Glyph
            # errors remain errors; this does not replace missing characters.
            document_start = out.index(r"\begin{document}")
            out.insert(document_start, r"\usepackage[UTF8,fontset=fandol]{ctex}")
            for body in bodies:
                body["tex_lines"] = [n + 1 for n in body["tex_lines"]]
        tex = "\n".join(out) + "\n"
        active = active_tex(tex)
        require(not re.search(r"\\(?:input|include)\b", active), "task must flatten all TeX input/include passages")
        require(not re.search(r"\\begin\{filecontents\*?\}", active), "declare bibliography files instead of filecontents output")
        item_path = f"items/{ident}_author_proof.tex"
        (package / item_path).write_text(tex, encoding="utf-8", newline="\n")
        assets = []
        for spec in checked["assets"]:
            target = relative_path(package, spec["target"])
            require(refresh or not target.exists(), "asset would overwrite another package file")
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(spec["source"], target)
            assets.append({"path": spec["target"], "kind": spec["kind"]})
        save(package / "licenses/evidence.json", checked["license_evidence"])
        (package / "licenses/NOTICE.txt").write_text(
            "; ".join(task["authors"]) + "\n" + task.get("source_title", task.get("work", task["source_id"])) + "\n" + task["source_version"] +
            "\nSource: " + task["source_url"] + "\nLicence: " + task["license"]["name"] +
            "\nVersion-specific evidence: " + task["license"]["version_url"] + "\n", encoding="utf-8", newline="\n")
        row = {"problem_id": ident, "task_id": task["task_id"], "revision": revision, "policy": POLICY,
               "title": task["title"], "author": "; ".join(task["authors"]), "authors": task["authors"],
               "work": task.get("source_title", task.get("work", task["source_id"])), "source_id": task["source_id"], "source_url": task["source_url"],
               "source_version": task["source_version"], "retrieved_at": task.get("retrieved_at", ""),
               "difficulty_level": task["difficulty_level"], "difficulty_reason": task["difficulty_reason"],
               "claim_key": task["claim_key"], "primary": task["statement_spans"], "proof_spans": task["proof_spans"],
               "contexts": task["context_spans"], "item_path": item_path, "compile_receipt": f"receipts/{ident}.json",
               "license": task["license"]["name"], "license_path": "licenses/NOTICE.txt",
               "license_evidence_path": "licenses/evidence.json", "asset_dependencies": assets,
               "source_files": source_map, "status": "pending", "tex_sha256": None,
               "origin_class": "human_authored_native_tex", "review_state": "current",
               "dedup_state": "unique_within_reviewed_scope", "publication_commit": None}
        if task.get("review_protocol"):
            row["review_protocol"] = task["review_protocol"]
        save(package / "manifest.json", {"schema_version": 2, "policy": POLICY, "verified_count": 0, "items": [row]})
        save(package / "source-map.json", {"schema_version": 2, "policy": POLICY, "sources": source_map, "bodies": bodies})
        save(package / "delivery-evidence.json", {"schema_version": 2, "policy": POLICY, **binding(task),
             "assembly_basis": "declared source spans, task revision and substantive review", "bodies": bodies})
        save(package / f"sources/{ident}/provenance.json", row)
        state.update(status="assembled", assembled_at=utc_now())
        save(job / "job-state.json", state)
        if compile_now:
            return compile_job(job)
        return {"status": "assembled", "job": str(job), "policy": POLICY, **binding(task)}
    except Exception as exc:
        state.update(status="needs_codex", error=str(exc))
        save(job / "job-state.json", state)
        raise


def tool(name):
    path = shutil.which(name)
    require(path is not None, "installed tool missing: " + name + "; no dependency will be installed")
    return path


def run_tool(argv, log, *, cwd=None, env=None, timeout=300):
    result = subprocess.run(argv, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, encoding="utf-8", errors="replace", timeout=timeout)
    Path(log).write_text(result.stdout, encoding="utf-8", newline="\n")
    require(result.returncode == 0, "tool exit " + str(result.returncode) + ": " + str(argv[0]) + "; see " + str(log))
    return result.stdout


# TeX echoes the offending box's content on the lines following an
# Overfull/Underfull report and terminates that dump with a blank line; the
# dump is unbounded (nested boxes, long paragraphs), so the former fixed
# three-line continuation budget misclassified later dump lines that start
# with "!" as errors (L60114, lane-p1 L40423).  The scan now skips the whole
# dump segment up to its blank-line terminator, capped only as a guard
# against a pathological log whose dump never ends; a real error later in
# the log is scanned once the cap expires.  Deliberately NOT a keyword
# allowlist: real errors such as "! Display math should end with $$." or
# "! Too many }'s." carry no allowlisted keyword and would be missed.
BOX_DUMP_SCAN_LIMIT = 500


def engine_log_errors(text):
    errors = []
    box_dump_lines = 0
    for line in text.splitlines():
        if re.match(r"^(?:Overfull|Underfull)\s+\\[hv]box", line):
            box_dump_lines = BOX_DUMP_SCAN_LIMIT
            continue
        if box_dump_lines:
            box_dump_lines -= 1
            if line.strip() == "":
                box_dump_lines = 0
            continue
        if re.search(
            r"undefined references|undefined citations|(?:Reference|Citation) .+ undefined|Missing character:|multiply.defined labels|Label\\(s\\) may have changed|Rerun to get|^!", line, re.I):
            errors.append(line)
    return errors


def compile_job(job, *, resume=False):
    require(load(Path(job) / "job-state.json").get("material_format") != NATIVE_FORMAT,
            "native Lean retains authored toolchain/build status; compile-job is the TeX compiler")
    job = Path(job).resolve()
    state = load(job / "job-state.json")
    require(state["policy"] == POLICY and (state["status"] == "assembled" or (resume and state["status"] == "needs_codex")), "job is not an assembled revision or failed build")
    package = job / state["package"]
    row = load(package / "manifest.json")["items"][0]
    tex = relative_path(package, row["item_path"], existing=True)
    build = job / state["build_root"] / row["problem_id"]
    receipt_root = job / state["receipt_root"]
    qa_root = job / state["qa_root"]
    build.mkdir(parents=True, exist_ok=resume)
    receipt_root.mkdir(exist_ok=resume)
    qa_root.mkdir(exist_ok=resume)
    task = load(package / state["task_snapshot"])
    has_bib = any(a["kind"] == "bibliography" and Path(a["path"]).suffix.lower() == ".bib" for a in row["asset_dependencies"])
    backend = task["assembly"].get("bibliography_backend", "bibtex" if has_bib else "none")
    receipt = {"schema_version": 2, "policy": POLICY, **binding(state), "ok": False,
               "compile_run_id": state["task_id"] + "/" + state["revision"] + "/compile-001",
               "engine": "xelatex", "driver": "explicit_xelatex", "latexmk_used": False,
               "shell_escape": False, "started_at": utc_now(), "bibliography_backend": backend, "bibliography_runs": 0,
               "engine_runs": 0, "asset_paths": [a["path"] for a in row["asset_dependencies"]]}
    try:
        xelatex, pdfinfo, render = tool("xelatex"), tool("pdfinfo"), tool("pdftoppm")
        env = os.environ.copy()
        env["openin_any"], env["openout_any"] = "r", "p"
        for name in ("TEXMFVAR", "TEXMFCONFIG", "XDG_CACHE_HOME"):
            directory = job / "tmp" / name.lower()
            directory.mkdir(parents=True, exist_ok=True)
            env[name] = str(directory)
        passes = 2 if backend == "none" else 3
        for attempt in range(1, passes + 1):
            argv = [xelatex, "-no-shell-escape", "-interaction=nonstopmode", "-halt-on-error",
                    "-file-line-error", "-recorder", "-output-directory=" + str(build), tex.name]
            run_tool(argv, build / f"xelatex-{attempt}.stdout", cwd=tex.parent, env=env)
            receipt["engine_runs"] += 1
            if attempt == 1 and backend != "none" and (backend != "bibtex" or "\\citation" in (build / (tex.stem + ".aux")).read_text(encoding="utf-8", errors="replace")):
                env["BIBINPUTS"] = str(tex.parent) + os.pathsep + env.get("BIBINPUTS", "")
                argv = [tool(backend), tex.stem] if backend == "bibtex" else [tool("biber"), "--input-directory", str(build), "--output-directory", str(build), tex.stem]
                run_tool(argv, build / (backend + ".stdout"), cwd=build, env=env)
                receipt["bibliography_runs"] += 1
        final_log = build / (tex.stem + ".log")
        text = final_log.read_text(encoding="utf-8", errors="replace")
        # Hyperref outlines can require an additional pass after references settle.
        if re.search(r"Label\(s\) may have changed|Rerun to get", text, re.I):
            run_tool([xelatex, "-no-shell-escape", "-interaction=nonstopmode", "-halt-on-error",
                      "-file-line-error", "-recorder", "-output-directory=" + str(build), tex.name],
                     build / f"xelatex-{passes + 1}.stdout", cwd=tex.parent, env=env)
            receipt["engine_runs"] += 1
            text = final_log.read_text(encoding="utf-8", errors="replace")
        # Box-dump handling lives in engine_log_errors (PD window 2026-10-15
        # GAP-2, CONTROL 8.8.168): the former fixed three-line skip budget
        # misread longer dumps (L60114, lane-p1 L40423).
        errors = engine_log_errors(text)
        require(not errors, "final engine log has unresolved errors: " + "; ".join(errors[:4]))
        fls = build / (tex.stem + ".fls")
        require(fls.is_file(), "TeX recorder output missing")
        declared = {relative_path(package, p, existing=True) for p in receipt["asset_paths"]}
        declared.add(tex)
        for line in fls.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.startswith("INPUT "):
                path = Path(line[6:])
                path = (path if path.is_absolute() else tex.parent / path).resolve()
                if path.is_relative_to(package):
                    require(path in declared, "undeclared package input: " + str(path))
        pdf = build / (tex.stem + ".pdf")
        info = run_tool([pdfinfo, str(pdf)], build / "pdfinfo.log")
        match = re.search(r"^Pages:\s+(\d+)\s*$", info, re.M)
        require(match and int(match[1]) > 0, "PDF has no readable pages")
        pages = int(match[1])
        run_tool([render, "-r", "95", "-png", str(pdf), str(qa_root / "page")], qa_root / "render.log")
        images = sorted(qa_root.glob("page-*.png"))
        require(len(images) == pages, "not every PDF page was rendered")
        receipt.update(ok=True, completed_at=utc_now(), pages=pages, passes=receipt["engine_runs"],
                       pdf_path=str(pdf.relative_to(job)).replace("\\", "/"),
                       compiler_log_path=str(final_log.relative_to(job)).replace("\\", "/"),
                       rendered_pages=[str(p.relative_to(job)).replace("\\", "/") for p in images],
                       final_log_errors=[])
        require(receipt["engine_runs"] >= 2, "two actual xelatex engine runs were not observed")
        state.update(status="compiled_pending_qa", compile_run_id=receipt["compile_run_id"])
    except Exception as exc:
        receipt["ok"] = False
        receipt["error"] = str(exc)
        state.update(status="needs_codex", error=str(exc))
        raise
    finally:
        save(receipt_root / (row["problem_id"] + ".json"), receipt)
        save(package / row["compile_receipt"], receipt)
        save(job / "job-state.json", state)
    return {"status": state["status"], "job": str(job), "compile_run_id": receipt["compile_run_id"], "receipt": str(receipt_root / (row["problem_id"] + ".json")),
            "pdf": str(pdf), "pages": pages, "rendered_pages": receipt["rendered_pages"], "policy": POLICY}


LEGACY_COLUMNS = ("problem_id", "title", "difficulty_level", "difficulty_reason", "source_id",
                  "source_locator_json", "tex_path", "tex_content", "tex_sha256", "origin_class",
                  "status", "compile_receipt_path")
ADDED_COLUMNS = {"task_id": "TEXT", "revision": "TEXT", "validation_policy": "TEXT DEFAULT 'legacy'",
                 "claim_key": "TEXT", "review_state": "TEXT", "dedup_state": "TEXT", "publication_commit": "TEXT",
                 "qualification_set_id": "TEXT", "review_protocol": "TEXT"}
SOURCE_COLUMNS = ("source_id", "author", "work", "source_url", "source_version", "retrieved_at", "license", "license_path")
SOURCE_SQL = """CREATE TABLE sources (
source_id TEXT PRIMARY KEY, author TEXT NOT NULL, work TEXT NOT NULL,
source_url TEXT NOT NULL, source_version TEXT NOT NULL, retrieved_at TEXT NOT NULL,
license TEXT NOT NULL, license_path TEXT NOT NULL)"""


def problem_schema(table="problems"):
    require(table in ("problems", "problems_v2_migration"), "unsupported schema target")
    return f"""CREATE TABLE {table} (
problem_id TEXT PRIMARY KEY, title TEXT NOT NULL,
difficulty_level TEXT NOT NULL CHECK(difficulty_level IN ('H1','H2','H3')),
difficulty_reason TEXT NOT NULL, source_id TEXT NOT NULL REFERENCES sources(source_id),
source_locator_json TEXT NOT NULL, tex_path TEXT UNIQUE, tex_content TEXT,
tex_sha256 TEXT, origin_class TEXT NOT NULL CHECK(origin_class IN ('human_authored_native_tex','human_authored_proof_assistant_transcription','human_authored_checked_published_transcription','author_native_lean')),
status TEXT NOT NULL CHECK(status IN ('verified_editable_tex','verified_native_author_proof','complete_author_material')), compile_receipt_path TEXT,
task_id TEXT, revision TEXT, validation_policy TEXT DEFAULT 'legacy', claim_key TEXT,
review_state TEXT, dedup_state TEXT, publication_commit TEXT, qualification_set_id TEXT, review_protocol TEXT,
CHECK (status='complete_author_material' OR (origin_class='author_native_lean' AND status='verified_native_author_proof' AND tex_path IS NULL AND tex_content IS NULL AND compile_receipt_path IS NULL)
OR (origin_class!='author_native_lean' AND status='verified_editable_tex' AND tex_path IS NOT NULL AND tex_content IS NOT NULL AND compile_receipt_path IS NOT NULL)))"""


def locator(row):
    result = dict(copy.deepcopy(row.get('locator_extensions', {})), primary=row.get('primary', []), contexts=row.get('contexts', []))
    if row.get("policy") == POLICY:
        result["proof_spans"] = row.get("proof_spans", [])
    if row.get("material_format") == NATIVE_FORMAT:
        result["native_material"] = copy.deepcopy(row["native_material"])
    for key in ("work_ref", "statement_spans", "context_spans", "material_state", "run_state", "materials"):
        if key in row:
            result[key] = copy.deepcopy(row[key])
    return result


def locator_metadata(value):
    """Exclude opaque historical fingerprints from locator metadata checks."""
    if isinstance(value, dict):
        return {k: locator_metadata(v) for k, v in value.items()
                if not any(token in k.lower() for token in ("sha256", "checksum", "digest", "hash"))}
    if isinstance(value, list):
        return [locator_metadata(v) for v in value]
    return value


def create_database(package, rows, destination):
    """Create a new per-job database. Reading text for insertion is not comparison."""
    destination = Path(destination)
    require(not destination.exists(), "database output already exists")
    destination.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(destination)
    try:
        db.execute("PRAGMA foreign_keys=ON")
        with db:
            db.execute(SOURCE_SQL)
            db.execute(problem_schema())
            sources = {}
            for row in rows:
                require(row.get("policy") == POLICY and row.get("tex_sha256") is None, "new rows use v2 with NULL legacy digest")
                native = row.get("material_format") == NATIVE_FORMAT
                reference = row.get('status') == shared.STATUS
                require(row.get("status") == (shared.STATUS if reference else NATIVE_STATUS if native else "verified_editable_tex"), "database requires completed local material")
                if reference:
                    require(row.get("material_state") == "complete" and row.get("eligible") is True,
                            "shared reference must retain complete qualified material")
                source = tuple(row.get(k, "") for k in SOURCE_COLUMNS)
                if row["source_id"] in sources:
                    require(source == sources[row["source_id"]], "conflicting metadata for the same fixed source")
                else:
                    db.execute("INSERT INTO sources VALUES (?,?,?,?,?,?,?,?)", source)
                    sources[row["source_id"]] = source
                text = None if native or reference else relative_path(package, row["item_path"], existing=True).read_text(encoding="utf-8")
                values = (row["problem_id"], row["title"], row["difficulty_level"], row["difficulty_reason"], row["source_id"],
                          json.dumps(locator(row), ensure_ascii=False), None if native or reference else row["item_path"], text, None, row["origin_class"],
                          row["status"], row["compile_receipt"], row["task_id"], row["revision"], POLICY, row["claim_key"],
                          row["review_state"], row["dedup_state"], row.get("publication_commit"), None, row.get("review_protocol"))
                db.execute("INSERT INTO problems VALUES (" + ",".join("?" for _ in values) + ")", values)
            db.execute("PRAGMA user_version=2")
    finally:
        db.close()
    return validate_database(destination, rows)


def migrate_database(source, output):
    """Copy an existing DB with SQLite backup, then migrate only the new copy.

    Historical tex_sha256 values are copied as opaque history. No digest is
    calculated or used as an acceptance condition.
    """
    source, output = Path(source).resolve(), Path(output).resolve()
    require(source.is_file() and source != output and not output.exists(), "migration needs an existing source and fresh output")
    output.parent.mkdir(parents=True, exist_ok=True)
    src = sqlite3.connect(source.as_uri() + "?mode=ro", uri=True)
    dst = sqlite3.connect(output)
    try:
        src.backup(dst)
        info = {row[1]: row for row in dst.execute("PRAGMA table_info(problems)")}
        require(set(LEGACY_COLUMNS) <= set(info), "unsupported legacy problem schema")
        dst.execute("PRAGMA foreign_keys=OFF")
        with dst:
            original_schema = dst.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='problems'").fetchone()[0]
            if info["tex_sha256"][3] or NATIVE_ORIGIN not in original_schema or info["tex_content"][3] or shared.STATUS not in original_schema:
                extra_sql = [row[0] for row in dst.execute(
                    "SELECT sql FROM sqlite_master WHERE tbl_name='problems' AND type IN ('index','trigger') AND sql IS NOT NULL")]
                # Transform the existing definition, retaining custom columns,
                # defaults, table constraints, indexes and triggers verbatim.
                upgraded = "CREATE TABLE problems_v2_migration " + original_schema[original_schema.index("("):]
                for name in ("tex_path", "tex_content", "compile_receipt_path", "tex_sha256"):
                    identifier = r'(?<![A-Za-z0-9_])(?:"' + name + r'"|' + name + r')(?![A-Za-z0-9_])'
                    upgraded = re.sub(r'(' + identifier + r'\s+(?:TEXT|BLOB|VARCHAR(?:\([0-9]+\))?))\s+NOT\s+NULL', r'\1', upgraded, flags=re.I)
                if NATIVE_ORIGIN not in original_schema:
                    upgraded = re.sub(r"(?<![A-Za-z0-9_])(origin_class\s+IN\s*\()", r"\1'author_native_lean',", upgraded, flags=re.I)
                upgraded = re.sub(r"CHECK\s*\(\s*status\s*=\s*'verified_editable_tex'\s*\)", "CHECK(status IN ('verified_editable_tex','verified_native_author_proof','complete_author_material'))", upgraded, flags=re.I)
                upgraded = re.sub(r"(CHECK\s*\(\s*status\s+IN\s*\()(?!'complete_author_material')", r"\1'complete_author_material',", upgraded, flags=re.I)
                # Preserve unrelated custom CHECKs. Only the legacy TeX-storage
                # constraint gains a separate branch for a complete source reference.
                positions = list(re.finditer(r'\bCHECK\s*\(', upgraded, re.I))
                for match in reversed(positions):
                    start, cursor, depth, quoted = match.end(), match.end(), 1, False
                    while cursor < len(upgraded) and depth:
                        char = upgraded[cursor]
                        if char == "'":
                            if quoted and cursor + 1 < len(upgraded) and upgraded[cursor + 1] == "'":
                                cursor += 2
                                continue
                            quoted = not quoted
                        elif not quoted:
                            depth += (char == '(') - (char == ')')
                        cursor += 1
                    expression = upgraded[start:cursor - 1]
                    if any(name in expression for name in ('tex_path', 'tex_content', 'compile_receipt_path')):
                        upgraded = upgraded[:start] + "status='complete_author_material' OR (" + expression + ")" + upgraded[cursor - 1:]
                end = upgraded.rfind(")")
                upgraded = upgraded[:end] + ", CHECK (status='complete_author_material' OR (origin_class='author_native_lean' AND status='verified_native_author_proof' AND tex_path IS NULL AND tex_content IS NULL AND compile_receipt_path IS NULL) OR (origin_class!='author_native_lean' AND tex_path IS NOT NULL AND tex_content IS NOT NULL AND compile_receipt_path IS NOT NULL))" + upgraded[end:]
                dst.execute(upgraded)
                columns = ",".join(info)
                dst.execute("INSERT INTO problems_v2_migration (" + columns + ") SELECT " + columns + " FROM problems")
                dst.execute("DROP TABLE problems")
                dst.execute("ALTER TABLE problems_v2_migration RENAME TO problems")
                for sql in extra_sql:
                    dst.execute(sql)
            for name, definition in ADDED_COLUMNS.items():
                if name not in info:
                    dst.execute("ALTER TABLE problems ADD COLUMN " + name + " " + definition)
            dst.execute("PRAGMA user_version=2")
        dst.execute("PRAGMA foreign_keys=ON")
    finally:
        src.close()
        dst.close()
    return {"status": "migrated_copy", "database": str(output), **validate_database(output)}


def validate_database(path, expected_rows=None, *, publication_annotations=None):
    """Validate structure, counts and metadata, never stored/full-file text equality."""
    path = Path(path).resolve()
    require(path.is_file(), "database missing")
    db = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)
    db.row_factory = sqlite3.Row
    try:
        require(db.execute("PRAGMA integrity_check").fetchone()[0] == "ok", "SQLite integrity check failed")
        require(not db.execute("PRAGMA foreign_key_check").fetchall(), "SQLite foreign-key errors")
        info = {r[1]: r for r in db.execute("PRAGMA table_info(problems)")}
        require((set(LEGACY_COLUMNS) | set(ADDED_COLUMNS)) - {"qualification_set_id", "review_protocol"} <= set(info), "revision-v2 database columns missing")
        require(info["tex_sha256"][3] == 0, "historical tex_sha256 must be nullable")
        require(db.execute("SELECT count(*) FROM problems WHERE validation_policy=? AND tex_sha256 IS NOT NULL", (POLICY,)).fetchone()[0] == 0,
                "new revision-v2 rows must not invent a digest")
        require(db.execute("SELECT count(*) FROM problems WHERE status!='complete_author_material' AND origin_class!='author_native_lean' AND (tex_content IS NULL OR length(tex_content)=0)").fetchone()[0] == 0, "empty stored TeX")
        require(db.execute("SELECT count(*) FROM problems WHERE origin_class='author_native_lean' AND (status NOT IN ('verified_native_author_proof','complete_author_material') OR tex_content IS NOT NULL OR tex_path IS NOT NULL OR compile_receipt_path IS NOT NULL)").fetchone()[0] == 0,
                "native Lean must not masquerade as TeX")
        for native in db.execute("SELECT source_locator_json FROM problems WHERE origin_class='author_native_lean'"):
            require(isinstance(json.loads(native[0]).get("native_material"), dict), "native SQL material locator missing")
        for reference in db.execute("SELECT source_locator_json FROM problems WHERE status='complete_author_material'"):
            metadata = json.loads(reference[0])
            require(bool(metadata.get('work_ref', {}).get('work_key')) and metadata.get('material_state') == 'complete',
                    'shared SQL material reference missing')
        require(not db.execute("SELECT claim_key FROM problems WHERE review_state IN ('current','author_material_collection') AND claim_key IS NOT NULL GROUP BY claim_key HAVING count(*)>1").fetchall(),
                "duplicate claim identity in current qualified rows")
        actual_count = db.execute("SELECT count(*) FROM problems").fetchone()[0]
        if expected_rows is not None:
            ids = {r["problem_id"] for r in expected_rows}
            require(len(ids) == len(expected_rows), "duplicate expected problem IDs")
            columns = [c for c in LEGACY_COLUMNS if c not in ("tex_content", "tex_sha256")] + list(ADDED_COLUMNS)
            projection = [c if c in info else "NULL AS " + c for c in columns]
            actual = {r["problem_id"]: dict(r) for r in db.execute("SELECT " + ",".join(projection) + " FROM problems")}
            require(set(actual) == ids, "database IDs differ from manifest")
            sources = {r["source_id"]: dict(r) for r in db.execute("SELECT " + ",".join(SOURCE_COLUMNS) + " FROM sources")}
            require(set(sources) == {r["source_id"] for r in expected_rows}, "database source set differs from manifest")
            for row in expected_rows:
                a = actual[row["problem_id"]]
                fields = {"problem_id": "problem_id", "title": "title", "difficulty_level": "difficulty_level",
                          "difficulty_reason": "difficulty_reason", "source_id": "source_id", "tex_path": "item_path",
                          "origin_class": "origin_class", "status": "status", "compile_receipt_path": "compile_receipt"}
                for column, key in fields.items():
                    wanted = None if (row.get("material_format") == NATIVE_FORMAT or row.get('status') == shared.STATUS) and column in ("tex_path", "compile_receipt_path") else row[key]
                    require(a[column] == wanted, "SQL metadata differs: " + column)
                require(locator_metadata(json.loads(a["source_locator_json"])) == locator_metadata(locator(row)), "SQL source locators differ")
                if row.get("policy") == POLICY or row.get("qualification_set_id"):
                    for field in ADDED_COLUMNS:
                        expected = row.get("policy", "legacy") if field == "validation_policy" else row.get(field)
                        if field == 'publication_commit' and expected is None and publication_annotations and a[field] is not None:
                            require(a[field] == publication_annotations.get(row['problem_id']), 'SQL publication annotation differs from confirmed history')
                            continue
                        require(a[field] == expected, "SQL revision metadata differs: " + field)
                    if row.get("qualification_set_id"):
                        whole_work = row.get("qualification_basis") == "whole_author_work_difficulty_screening"
                        allowed_policies = ("legacy", POLICY) if whole_work else ("legacy",)
                        require(a["validation_policy"] in allowed_policies and sources[row["source_id"]]["source_version"] == row["source_version"],
                                "qualification source/version/policy differs")
                if row.get("policy") == POLICY:
                    for field in SOURCE_COLUMNS:
                        require(sources[row["source_id"]][field] == row.get(field, ""), "SQL source metadata differs: " + field)
        q = db.execute("""SELECT count(DISTINCT claim_key) FROM problems
            WHERE difficulty_level IN ('H2','H3') AND status IN ('verified_editable_tex','verified_native_author_proof','complete_author_material')
            AND review_state IN ('current','author_material_collection') AND dedup_state='unique_within_reviewed_scope'
            AND claim_key IS NOT NULL AND publication_commit IS NOT NULL AND length(publication_commit)>0""").fetchone()[0]
        prepared_q = db.execute("""SELECT count(DISTINCT claim_key) FROM problems
            WHERE validation_policy=? AND difficulty_level IN ('H2','H3') AND status IN ('verified_editable_tex','verified_native_author_proof','complete_author_material')
            AND review_state IN ('current','author_material_collection') AND dedup_state='unique_within_reviewed_scope'
            AND claim_key IS NOT NULL AND publication_commit IS NOT NULL AND length(publication_commit)>0""", (POLICY,)).fetchone()[0]
        group_expr = "COALESCE(review_protocol, validation_policy, 'legacy')" if "review_protocol" in info else "COALESCE(validation_policy, 'legacy')"
        group_expr = "CASE WHEN review_state='author_material_collection' THEN 'author_material_collection' ELSE " + group_expr + " END"
        groups = dict(db.execute("SELECT " + group_expr + ", count(DISTINCT claim_key) FROM problems WHERE difficulty_level IN ('H2','H3') AND status IN ('verified_editable_tex','verified_native_author_proof','complete_author_material') AND review_state IN ('current','author_material_collection') AND dedup_state='unique_within_reviewed_scope' AND claim_key IS NOT NULL AND publication_commit IS NOT NULL AND length(publication_commit)>0 GROUP BY " + group_expr).fetchall())
        return {"qualified_published_by_basis": groups, "qualified_published_by_review_protocol": groups, "problem_count": actual_count, "source_count": db.execute("SELECT count(*) FROM sources").fetchone()[0],
                "integrity": "ok", "foreign_key_errors": [], "metadata_projection_consistent": expected_rows is not None,
                "qualified_current_published_count": q, "qualified_prepared_published_count": prepared_q, "policy": POLICY}
    finally:
        db.close()


# --- D-prime form equivalence (Chief ruling 2026-10-14) ---------------------------------------
# One pinned source can be recorded in two shapes:
#   git  form  "Stacks Project git a04446e57ec1 (2026-07-28); file pione.tex; corpus local snapshot 20261012"
#   tree form  "Stacks Project source tree, file pione.tex, corpus local snapshot 20261012"
# The 2026-10-14 chapter-level licence refresh moved the observations to the tree form while older
# cards keep the git form.  The two shapes are equivalent ONLY when they name the same source file,
# the same local snapshot, AND the hash is the pinned commit recorded for that source
# (sources/<dir>/SOURCE.json).  A mapping that is not on record is NOT exempted.
_GIT_FORM = re.compile(
    r"git\s+([0-9a-f]{7,40})\s*\((\d{4}-\d{2}-\d{2})\)[;,]\s*file\s+([^;,]+?)[;,]\s*corpus local snapshot\s*(\d{8})")
_TREE_FORM = re.compile(r"source tree,\s*file\s+([^,]+?),\s*corpus local snapshot\s*(\d{8})")
_REGISTRY_CACHE = {}


def _conn_form(value):
    """Parse a recorded source_version shape, or None when it is neither recorded shape."""
    if not isinstance(value, str):
        return None
    m = _GIT_FORM.search(value)
    if m:
        return {"form": "git", "hash": m.group(1).lower(), "file": m.group(3).strip(),
                "snapshot": m.group(4)}
    m = _TREE_FORM.search(value)
    if m:
        return {"form": "tree", "hash": None, "file": m.group(1).strip(), "snapshot": m.group(2)}
    return None


def _registry_sources_root():
    for root in (Path(__file__).resolve().parents[2], Path(__file__).resolve().parents[3]):
        for candidate in (root / "research-line" / "harness-ready-20261011" / "sources", root / "sources"):
            if candidate.is_dir():
                return candidate
    return None


def _registry_for(source_dir=None, file_name=None):
    """(pinned_commit, snapshot_date) for a source dir, or by file name over the sources tree."""
    key = (str(source_dir), file_name)
    if key in _REGISTRY_CACHE:
        return _REGISTRY_CACHE[key]
    value = None
    record = None
    if source_dir is not None:
        candidate = Path(source_dir) / "SOURCE.json"
        if candidate.exists():
            record = candidate
    if record is None and file_name:
        root = _registry_sources_root()
        if root is not None:
            for candidate in sorted(root.glob("*/SOURCE.json")):
                try:
                    probe = json.loads(candidate.read_text(encoding="utf-8"))
                except ValueError:
                    continue
                sid = probe.get("source_id") or ""
                if "file %s" % file_name in sid or sid.endswith(":%s:" % file_name) or file_name in sid:
                    record = candidate
                    break
    if record is not None:
        try:
            r = json.loads(record.read_text(encoding="utf-8"))
            m = re.search(r"local-snapshot-(\d{8})", r.get("source_id") or "")
            value = ((r.get("pinned_commit") or "").lower(), m.group(1) if m else None)
        except ValueError:
            value = None
    _REGISTRY_CACHE[key] = value
    return value


def form_equivalent(left, right, evidence_path=None):
    """True for the recorded shapes of the same pinned source (Chief ruling D').

    1. Same recorded shape with every parsed field equal (git: hash+file+snapshot;
       tree: file+snapshot): a separator or whitespace difference (";" vs ",")
       carries no identity change and involves no cross-form mapping, so no
       registry lookup is needed.  2026-10-14 CONTROL (br) root-fix, S3-co
       batch-198 case: the assembled package evidence kept the ";" spelling
       while the task string used ",", the same-form guard below rejected the
       pair, adopt-material died before writing final-item and prepare lost
       those items batch after batch.
    2. Cross-shape git vs tree of the same source, proven through the pinned
       commit recorded for that source (sources/<dir>/SOURCE.json).  A mapping
       that is not on record is NOT exempted.
    """
    a, b = _conn_form(left), _conn_form(right)
    if not a or not b:
        return False
    if a["form"] == b["form"]:
        return (a["hash"] == b["hash"] and a["file"] == b["file"]
                and a["snapshot"] == b["snapshot"])
    if a["file"] != b["file"] or a["snapshot"] != b["snapshot"]:
        return False
    git_side = a if a["form"] == "git" else b
    reg = _registry_for(Path(evidence_path).parent if evidence_path else None, git_side["file"])
    if not reg or not reg[0]:
        return False
    commit, snapshot = reg
    if not (commit.startswith(git_side["hash"][:12]) or git_side["hash"].startswith(commit[:12])):
        return False
    if snapshot and snapshot != git_side["snapshot"]:
        return False
    return True


def verify_job(job, *, require_ready=True):
    job = Path(job).resolve()
    state = load(job / "job-state.json")
    if state.get('work_ref'):
        return verify_reference_job(job, state, require_ready=require_ready)
    if state.get("material_format") == NATIVE_FORMAT:
        return verify_native_job(job, state, require_ready=require_ready)
    require(state.get("policy") == POLICY, "unsupported job policy")
    package = relative_path(job, state["package"])
    manifest = load(relative_path(package, "manifest.json", existing=True))
    require(manifest.get("schema_version") == 2 and manifest.get("policy") == POLICY and len(manifest.get("items", [])) == 1,
            "one revision-v2 package item required")
    row = manifest["items"][0]
    task = load(relative_path(package, state["task_snapshot"], existing=True))
    material = state.get("preparation_basis") == MATERIAL_BASIS
    if material:
        require(task.get("preparation_basis") == row.get("preparation_basis") == MATERIAL_BASIS and
                row.get("review_state") == MATERIAL_BASIS, "material basis metadata mismatch")
        validate_record(task, [], material_only=True)
        require(binding(task) == binding(state) == binding(row), "job/task/manifest metadata mismatch")
    else:
        reviewed = load(relative_path(package, f"sources/{row['problem_id']}/content-review.json", existing=True))
        validate_record(task, reviewed["reviews"])
        require(binding(task) == binding(state) == binding(row) == binding(reviewed), "job/task/manifest/review metadata mismatch")
        require(reviewed["dedup"] == task["dedup"], "recorded semantic decision differs from task")
    require(row["status"] == "verified_editable_tex" and manifest["verified_count"] == 1 and row.get("tex_sha256") is None,
            "package is not locally completed under v2")
    require(row["difficulty_level"] == task["difficulty_level"] and row["difficulty_reason"] == task["difficulty_reason"],
            "difficulty differs from reviewed task")
    require(row["authors"] == task["authors"] and row["author"] == "; ".join(task["authors"]), "author list mismatch")
    require(row["primary"] == task["statement_spans"] and row["proof_spans"] == task["proof_spans"] and row["contexts"] == task["context_spans"],
            "manifest source locators differ from reviewed task")
    require(relative_path(package, row["item_path"], existing=True).stat().st_size > 0, "empty editable TeX")
    require(row["source_files"], "copied author source missing")
    for source in row["source_files"]:
        relative_path(package, source["path"], existing=True)
        require(source["source_id"] == task["source_id"] and source["source_version"] == task["source_version"], "wrong copied source version")
    for asset in row["asset_dependencies"]:
        relative_path(package, asset["path"], existing=True)
    evidence = load(relative_path(package, row["license_evidence_path"], existing=True))
    retained_license = (nonempty(evidence.get("source_notice")) or
                        all(nonempty(evidence.get(k)) for k in ("name", "version_url", "prior_license_path", "basis")) or
                        all(nonempty(evidence.get(k)) for k in ("license", "license_url", "source_url", "publisher_rights_fact")))
    require(evidence.get("status") == "supported" or
            (material and evidence.get("status") is None and retained_license),
            "supported licence observation or retained source notice missing")
    for key in ("source_id", "source_version"):
        require(key not in evidence or evidence[key] == task[key] or
                (key == "source_version" and form_equivalent(evidence[key], task[key])),
                "licence belongs to another " + key)
    relative_path(package, row["license_path"], existing=True)
    receipt = load(relative_path(package, row["compile_receipt"], existing=True))
    external = load(relative_path(job, state["receipt_root"] + "/" + row["problem_id"] + ".json", existing=True))
    for record in (receipt, external):
        require(record.get("policy") == POLICY and binding(record) == binding(task) and record.get("ok") is True,
                "compile receipt does not belong to this successful revision")
        wanted_runs = 2 if record.get("bibliography_backend") == "none" else 3
        require(record.get("shell_escape") is False and record.get("driver") == "explicit_xelatex" and
                record.get("latexmk_used") is False and
                (record.get("engine_runs", 0) >= wanted_runs if material else record.get("engine_runs") == wanted_runs),
                "real isolated compilation evidence missing")
        require(not record.get("final_log_errors"), "final engine errors recorded")
    receipt_fields = (("compile_run_id", "pdf_path", "pages", "engine_runs") if material else
                      ("compile_run_id", "pdf_path", "compiler_log_path", "pages", "engine_runs", "rendered_pages"))
    require(all(receipt[k] == external[k] for k in receipt_fields), "compile receipt metadata mismatch")
    relative_path(job, receipt["pdf_path"], existing=True)
    require(type(receipt["pages"]) is int and receipt["pages"] > 0, "positive PDF page count required")
    if not material:
        relative_path(job, receipt["compiler_log_path"], existing=True)
        require(len(receipt["rendered_pages"]) == receipt["pages"], "rendered page count differs")
        for p in receipt["rendered_pages"]:
            relative_path(job, p, existing=True)
        qa = load(relative_path(job, "PAGE_QA-root-" + task["revision"] + ".json", existing=True))
        validate_qa(task, receipt, qa)
    sql = validate_database(package / state.get("material_database", "corpus.sqlite"), manifest["items"])
    if require_ready and not material:
        ready = load(relative_path(job, "READY-root-" + task["revision"] + ".json", existing=True))
        require(ready.get("policy") == POLICY and binding(ready) == binding(task), "READY metadata mismatch")
        expected_paths = {"package": package, "build_root": job / state["build_root"],
                          "receipt_root": job / state["receipt_root"],
                          "accepted_report": job / ("final-item-root-" + task["revision"] + ".json"),
                          "actual_item_gate": job / ("final-item-root-" + task["revision"] + ".json"),
                          "content_review": package / f"sources/{row['problem_id']}/content-review.json",
                          "page_QA": job / ("PAGE_QA-root-" + task["revision"] + ".json")}
        for field, expected in expected_paths.items():
            require(Path(ready[field]).resolve() == expected.resolve(), "READY path mismatch: " + field)
        require(ready.get("compile_run_id") == receipt["compile_run_id"] and
                ready.get("actual_compile_passes") == receipt["engine_runs"] and
                ready.get("actual_output_pages") == receipt["pages"], "READY compile metadata mismatch")
        require(ready.get("H_proposed") == task["difficulty_level"] and
                ready.get("specific_H_residual") == task["difficulty_reason"], "READY difficulty metadata mismatch")
        require(ready.get("final_revision_frozen") is True and not ready.get("holds"), "READY is not frozen or has holds")
        report = load(relative_path(job, "final-item-root-" + task["revision"] + ".json", existing=True))
        require(report.get("policy") == POLICY and binding(report) == binding(task) and
                report.get("editable_qualified_count") == 1 and not report.get("errors"), "final local report failed")
    return {"schema_version": 2, "policy": POLICY, **binding(task), "status": "verified_local_prepared_job",
            "editable_qualified_count": 1, "package_item_count": 1, "errors": [], "sql": sql,
            "preparation_basis": MATERIAL_BASIS if material else None,
            "qualification_basis": MATERIAL_BASIS if material else "recorded substantive reviews, fixed source version, claim locators, actual compilation and page QA"}



def assemble_reference(task_path, registry, output_root):
    task = load(task_path)
    ident = task.get('problem_id') or task.get('local_material_id') or task['task_id']
    require(ID.fullmatch(task['task_id']) and REVISION.fullmatch(task['revision']), 'reference task identity required')
    job = Path(output_root).resolve() / task['task_id'] / task['revision']
    require(not job.exists(), 'preserve existing reference output; use a fresh explicit output root')
    package = job / ('package-root-' + task['revision'])
    row = shared.prepare_entry(task, registry, package / 'references')
    require(row['eligible'], 'reference candidate remains pending: ' + row['material_state'])
    task = dict(task, problem_id=ident)
    row['problem_id'] = ident
    state = dict(binding(task), schema_version=2, policy=POLICY, status='material_ready',
                 package=package.name, task_snapshot='prepared-task.json',
                 work_ref=row['work_ref'], work_registry=str(Path(registry).resolve()),
                 material_format=row['material_format'], preparation_basis=MATERIAL_BASIS)
    save(package / 'prepared-task.json', task)
    save(package / 'manifest.json', {'schema_version': 2, 'policy': POLICY, 'verified_count': 1, 'items': [row]})
    save(job / 'job-state.json', state)
    create_database(package, [row], package / 'corpus.sqlite')
    return dict(verify_reference_job(job, state), job=str(job))


def verify_reference_job(job, state, *, require_ready=True, registry=None):
    registry = registry or state.get('work_registry')
    require(registry is not None, 'public reference verification requires an explicit work registry')
    package = relative_path(job, state['package'])
    require(package.is_dir(), 'reference package directory missing')
    task = load(relative_path(package, state['task_snapshot'], existing=True))
    manifest = load(package / 'manifest.json')
    require(len(manifest['items']) == manifest['verified_count'] == 1, 'one reference material per job required')
    row = manifest['items'][0]
    require(binding(state) == binding(task) == binding(row), 'reference material identity mismatch')
    require(row.get('work_ref') == state['work_ref'] and row.get('status') == shared.STATUS, 'reference material binding/status differs')
    require((task.get('work_key') or task.get('work_ref', {}).get('work_key')) == row['work_ref']['work_key'],
            'reference task work identity differs')
    for key in ('title', 'authors', 'difficulty_level', 'difficulty_reason', 'statement_spans', 'proof_spans', 'context_spans'):
        require(row.get(key) == task.get(key), 'reference task metadata differs: ' + key)
    result = shared.resolve_entry(row, registry)
    require(result['eligible'] and row.get('material_state') == 'complete', 'reference material incomplete or unscreened')
    work = shared.read_registry(registry)[row['work_ref']['work_key']]
    sql = validate_database(package / state.get('material_database', 'corpus.sqlite'), [row])
    return dict(binding(task), schema_version=2, policy=POLICY, work_ref=row['work_ref'],
                material_format=row['material_format'], preparation_basis=MATERIAL_BASIS,
                status='verified_local_prepared_job', editable_qualified_count=1, package_item_count=1,
                errors=[], sql=sql, public_redistribution_supported=work.get('public_redistribution_supported') is True,
                build_status=row['run_state'], qualification_basis=MATERIAL_BASIS)


def adopt_reference_material(job, output_root, reservations_path):
    original = load(job / 'job-state.json')
    verify_reference_job(job, original)
    package = job / original['package']
    task = load(package / original['task_snapshot'])
    fields = ('task_id', 'revision', 'source_id', 'source_version', 'claim_key')
    matches = [r for r in load(reservations_path)['entries'] if all(r.get(k) == task[k] for k in fields)]
    require(len(matches) == 1 and str(matches[0]['problem_id']).isdecimal(), 'one formal reference ID reservation required')
    ident = str(matches[0]['problem_id'])
    target = Path(output_root).resolve() / task['task_id'] / task['revision']
    require(not target.exists() and not target.is_relative_to(job), 'fresh separate reference adoption required')
    # Reference jobs contain local metadata/SQL only, never the author work.
    shutil.copytree(job, target)
    state = dict(original, problem_id=ident, adopted_from=str(job), material_database='adopted-corpus.sqlite')
    task['problem_id'] = ident
    manifest = load(package / 'manifest.json')
    manifest['items'][0]['problem_id'] = ident
    material_format = manifest['items'][0]['material_format']
    manifest['items'][0]['item_path'] = ('lean' if material_format == NATIVE_FORMAT else 'tex') + '/entries/' + ident + '/entry.json'
    out = target / state['package']
    save(target / 'job-state.json', state)
    save(out / state['task_snapshot'], task)
    save(out / 'manifest.json', manifest)
    create_database(out, manifest['items'], out / state['material_database'])
    report = verify_reference_job(target, state)
    save(target / ('final-item-root-' + task['revision'] + '.json'), report)
    return dict(report, job=str(target))


def adopt_material(job, output_root, reservations_path):
    """Assign a reserved public ID to a copy of an existing compiled material.

    Editable TeX, PDF and source files keep their original names and contents.
    Compilation receipts retain their original binding as origin metadata; only
    the delivery identity changes. No reviews or page-QA records are invented.
    """
    job, output_root = Path(job).resolve(), Path(output_root).resolve()
    original = load(job / "job-state.json")
    if original.get('work_ref'):
        return adopt_reference_material(job, output_root, reservations_path)
    if original.get("material_format") == NATIVE_FORMAT:
        return adopt_native_material(job, output_root, reservations_path)
    require(original.get("policy") == POLICY and original.get("status") in
            ("compiled_pending_qa", "built", "material_ready"), "existing successful compiled job required")
    package = relative_path(job, original["package"])
    task = load(relative_path(package, original["task_snapshot"], existing=True))
    validate_record(task, [], material_only=True)
    reservations = load(reservations_path)["entries"]
    fields = ("task_id", "revision", "source_id", "source_version", "claim_key")
    matches = [entry for entry in reservations if all(entry.get(k) == task[k] for k in fields)
               and entry.get("review_protocol") == task.get("review_protocol")]
    require(len(matches) == 1, "one matching formal ID reservation required")
    ident = matches[0]["problem_id"]
    require(isinstance(ident, str) and ident.isdecimal(), "reserved formal ID required")
    target = output_root / task["task_id"] / task["revision"]
    require(not target.is_relative_to(job) and not job.is_relative_to(target), "adoption must preserve the source job")
    if target.exists():
        state = load(target / "job-state.json")
        require(state.get("adopted_from") == str(job) and state.get("problem_id") == ident and
                state.get("preparation_basis") == MATERIAL_BASIS, "existing adoption conflicts with source or reservation")
        report = verify_job(target)
        final_report = target / ("final-item-root-" + task["revision"] + ".json")
        if not final_report.exists():
            save(final_report, report)
        return dict(report, job=str(target), resumed=True)
    # Copy the existing package and declared compile outputs; no rebuilding.
    manifest = load(package / "manifest.json")
    require(len(manifest["items"]) == 1, "one material per job required")
    row = manifest["items"][0]
    receipt = load(relative_path(package, row["compile_receipt"], existing=True))
    require(receipt.get("ok") is True and binding(receipt) == binding(task), "successful matching compilation required")
    paths = {"job-state.json", receipt["pdf_path"]}
    paths.update(path.relative_to(job).as_posix() for path in package.rglob("*") if path.is_file())
    for name in paths:
        relative_path(job, name, existing=True)
    for source in row["source_files"]:
        relative_path(package, source["path"], existing=True)
    for asset in row["asset_dependencies"]:
        relative_path(package, asset["path"], existing=True)
    for name in sorted(paths):
        src = relative_path(job, name, existing=True)
        require(not src.is_symlink(), "symlink in material job")
        dst = relative_path(target, name)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
    state = dict(original)
    old_binding = binding(task)
    for record in (state, task, row):
        record.update(problem_id=ident, preparation_basis=MATERIAL_BASIS)
    state.update(status="material_ready", adopted_from=str(job), original_material_binding=old_binding)
    state.pop("error", None)
    row.update(status="verified_editable_tex", review_state=MATERIAL_BASIS, publication_commit=None)
    manifest["verified_count"] = 1
    receipt.update(problem_id=ident, original_material_binding=old_binding)
    package = target / state["package"]
    save(target / "job-state.json", state)
    save(package / state["task_snapshot"], task)
    save(package / "manifest.json", manifest)
    save(package / row["compile_receipt"], receipt)
    save(target / state["receipt_root"] / (ident + ".json"), receipt)
    # A compiled input normally has no database. If it has one, preserve it and
    # place this formal-ID projection at a fresh path.
    database = package / "corpus.sqlite"
    if database.exists():
        state["material_database"] = "author-material.sqlite"
        database = package / state["material_database"]
        save(target / "job-state.json", state)
    create_database(package, [row], database)
    report = verify_job(target)
    save(target / ("final-item-root-" + task["revision"] + ".json"), report)
    return dict(report, job=str(target), resumed=False)


def validate_qa(task, receipt, qa):
    require(qa.get("schema_version") == 2 and qa.get("policy") == POLICY, "QA requires schema_version2 and the revision-v2 policy")
    for field in ("task_id", "problem_id", "revision"):
        require(qa.get(field) == task[field], "QA belongs to another " + field)
    require(qa.get("compile_run_id") == receipt["compile_run_id"], "QA belongs to another compilation")
    require(qa.get("pages_viewed") == list(range(1, receipt["pages"] + 1)), "QA must cover every actual PDF page")
    require(qa.get("verdict") == "pass" and nonempty(qa.get("reviewer_id")) and nonempty(qa.get("notes")), "actual positive page review required")
    require(not unresolved_issues(qa), "page QA has unresolved issues")


def record_qa(job, review_path):
    job = Path(job).resolve()
    state = load(job / "job-state.json")
    revision, ident = state["revision"], state["problem_id"]
    require(state.get("status") == "compiled_pending_qa" and not (job / ("READY-root-" + revision + ".json")).exists(),
            "QA accepts only a not-yet-completed compiled revision")
    package = job / state["package"]
    manifest = load(package / "manifest.json")
    task = load(package / state["task_snapshot"])
    receipt = load(package / manifest["items"][0]["compile_receipt"])
    qa = load(review_path)
    validate_qa(task, receipt, qa)
    row = manifest["items"][0]
    row["status"] = "verified_editable_tex"
    create_database(package, [row], package / "corpus.sqlite")
    manifest["verified_count"] = 1
    save(package / "manifest.json", manifest)
    save(package / f"sources/{ident}/provenance.json", row)
    save(job / ("PAGE_QA-root-" + revision + ".json"), qa)
    report = verify_job(job, require_ready=False)
    report_path = job / ("final-item-root-" + revision + ".json")
    save(report_path, report)
    ready = {"schema_version": 2, "policy": POLICY, **binding(task), "status": "PREPARED_READY_PENDING_OWNER_ADMISSION",
             "package": str(package), "build_root": str(job / state["build_root"]),
             "receipt_root": str(job / state["receipt_root"]), "accepted_report": str(report_path),
             "actual_item_gate": str(report_path), "author": row["author"], "work": row["work"],
             "H_proposed": row["difficulty_level"], "specific_H_residual": row["difficulty_reason"],
             "content_review": str(package / f"sources/{ident}/content-review.json"),
             "page_QA": str(job / ("PAGE_QA-root-" + revision + ".json")), "compile_run_id": receipt["compile_run_id"],
             "actual_compile_passes": receipt["engine_runs"], "actual_output_pages": receipt["pages"],
             "final_revision_frozen": True, "main_count_increment": 0, "holds": []}
    path = job / ("READY-root-" + revision + ".json")
    save(path, ready)
    state.update(status="built", completed_at=utc_now())
    save(job / "job-state.json", state)
    return {"status": "prepared_ready_not_admitted", "policy": POLICY, "ready": str(path), **binding(task)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("validate-task", "assemble"):
        p = sub.add_parser(name)
        p.add_argument("--task", type=Path, required=True)
        p.add_argument("--task-root", type=Path, required=True)
        if name == "assemble":
            p.add_argument("--output-root", type=Path, required=True)
            p.add_argument("--assemble-only", action="store_true")
            p.add_argument("--refresh", action="store_true", help="Reassemble a failed local build after correcting its material layout")
            p.add_argument("--material-only", action="store_true", help="Assemble local materials without review approval or a reserved public ID")
    p = sub.add_parser("adopt-material")
    p.add_argument("--job", type=Path, required=True)
    p.add_argument("--output-root", type=Path, required=True)
    p.add_argument("--reservations", type=Path, required=True)
    p = sub.add_parser("compile-job")
    p.add_argument("--job", type=Path, required=True)
    p.add_argument("--resume", action="store_true")
    p = sub.add_parser("qa")
    p.add_argument("--job", type=Path, required=True)
    p.add_argument("--review", type=Path, required=True)
    p = sub.add_parser("verify-job")
    p.add_argument("--job", type=Path, required=True)
    p = sub.add_parser("migrate-db")
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p = sub.add_parser("verify-db")
    p.add_argument("--database", type=Path, required=True)
    p.add_argument("--manifest", type=Path)
    p = sub.add_parser('register-work')
    p.add_argument('--record', type=Path, required=True)
    p.add_argument('--registry', type=Path, required=True)
    p.add_argument('--index-root', type=Path, required=True)
    p = sub.add_parser('assemble-reference')
    p.add_argument('--task', type=Path, required=True)
    p.add_argument('--registry', type=Path, required=True)
    p.add_argument('--output-root', type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == 'register-work':
            result = shared.register_work(args.registry, load(args.record), index_root=args.index_root)
        elif args.command == 'assemble-reference':
            result = assemble_reference(args.task, args.registry, args.output_root)
        elif args.command == "validate-task":
            checked = validate_task(args.task, args.task_root)
            result = {"status": "ready_for_assembly", "policy": POLICY, **binding(checked["task"]),
                      "reviewers": [r["reviewer_id"] for r in checked["reviews"]]}
        elif args.command == "assemble":
            result = assemble(args.task, args.task_root, args.output_root, compile_now=not args.assemble_only, material_only=args.material_only, refresh=args.refresh)
        elif args.command == "adopt-material":
            result = adopt_material(args.job, args.output_root, args.reservations)
        elif args.command == "compile-job":
            result = compile_job(args.job, resume=args.resume)
        elif args.command == "qa":
            result = record_qa(args.job, args.review)
        elif args.command == "verify-job":
            result = verify_job(args.job)
        elif args.command == "migrate-db":
            result = migrate_database(args.source, args.output)
        else:
            result = validate_database(args.database, load(args.manifest)["items"] if args.manifest else None)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, KeyError, TypeError, sqlite3.DatabaseError, subprocess.TimeoutExpired) as exc:
        print(json.dumps({"status": "needs_codex", "error": str(exc), "policy": POLICY}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
