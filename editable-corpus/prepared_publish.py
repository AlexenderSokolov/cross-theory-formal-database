"""Bounded reviewed-v2 publication: existing owner locks, isolated Git, SQL deltas.

This path uses no application content fingerprints or byte comparison and never
imports the old compile/gate/publication chain. Git commits identify versions.
"""
from __future__ import annotations
import argparse
import contextlib
import copy
import gzip
import json
import os
from pathlib import Path
import re
import shutil
import sqlite3
import subprocess
import sys
import time

import prepared_focused as focused
import prepared_delivery as d
import prepared_qualification as qualification

FIRST_ID, LAST_ID = 900000000, 900999999
COMMIT = re.compile(r"[0-9a-f]{40}\Z")
CONSUMER_HELPERS = ("prepared_delivery.py", "prepared_qualification.py", "prepared_publish.py", "prepared_focused.py", "prepared_dsh_evidence.py")


def git(argv, *, cwd=None, env=None, output=None):
    clean = os.environ.copy()
    for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE"):
        clean.pop(key, None)
    if env:
        clean.update(env)
    if output is None:
        result = subprocess.run(["git", *map(str, argv)], cwd=cwd, env=clean, capture_output=True,
                                text=True, encoding="utf-8", errors="replace")
    else:
        with Path(output).open("xb") as stream:
            result = subprocess.run(["git", *map(str, argv)], cwd=cwd, env=clean, stdout=stream,
                                    stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
    d.require(result.returncode == 0, "Git command failed: " + result.stderr.strip())
    return (result.stdout or "").strip()


def git_json(repo, commit, path):
    return json.loads(git(["--git-dir", repo, "show", commit + ":" + path]))


def git_file(repo, commit, path, output):
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    git(["--git-dir", repo, "show", commit + ":" + path], output=output)


def require_owner(state, actor):
    current = d.load(Path(state) / "owner.json")
    d.require(isinstance(actor, dict) and type(actor.get("generation")) is int and
              (actor.get("owner"), actor["generation"]) == (current.get("owner"), current.get("generation")),
              "controller actor rejected: owner/generation differs")
    return current


@contextlib.contextmanager
def file_guard(path, wait=False):
    """Same controller.lock/publication.lock as the existing Linux protocol."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+b") as stream:
        stream.seek(0)
        if os.name == "nt":
            import msvcrt
            deadline = time.monotonic() + (60 if wait else 0)
            while True:
                try:
                    msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
                    break
                except OSError:
                    if time.monotonic() >= deadline:
                        raise ValueError("control lock is held: " + str(path))
                    time.sleep(.05)
            try:
                yield
            finally:
                stream.seek(0)
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl
            fcntl.flock(stream, fcntl.LOCK_EX | (0 if wait else fcntl.LOCK_NB))
            try:
                yield
            finally:
                fcntl.flock(stream, fcntl.LOCK_UN)


@contextlib.contextmanager
def control(spec, publication=False):
    state = Path(spec["state_root"])
    with file_guard(state / "publication.lock") if publication else contextlib.nullcontext():
        with file_guard(state / "controller.lock", wait=True):
            require_owner(state, spec["actor"])
            yield


def idle_queue(spec):
    q = d.load(spec["queue_path"])
    d.require(not q.get("active_batch") and not q.get("queued_new_root_admitted"), "legacy queue must be idle before prepared publication")
    d.require(q["base"]["local_count"] == q["base"]["remote_main_count"], "legacy local material is awaiting publication")
    for filename in ("pending-publication.json", "publication-external.json"):
        path = Path(spec["state_root"]) / filename
        if path.exists():
            record = d.load(path)
            last = q.get("last_publication") or {}
            legacy_delivered = (filename == "pending-publication.json" and record.get("status") == "delivered" and
                                record.get("commit") == last.get("commit") and bool(last.get("commit")) and
                                record.get("count") == last.get("count") == q["base"]["remote_main_count"])
            legacy_terminal = (filename == "publication-external.json" and record.get("state") == "terminal" and
                               record.get("operation") == "verified" and bool(last.get("batch_id")) and
                               record.get("batch_id") == last["batch_id"] and bool(last.get("commit")) and
                               last.get("count") == q["base"]["remote_main_count"])
            d.require(not record or legacy_delivered or legacy_terminal or record.get("stage") == "reconciled" or
                      record.get("status", record.get("state")) in ("complete", "completed", "verified", "reconciled"),
                      "previous publication requires recovery: " + filename)
    return q


def problem_ids(value):
    result = set()
    if isinstance(value, dict):
        if "problem_id" in value:
            result.add(str(value["problem_id"]))
        for key, part in value.items():
            if key in ("unit_ids", "incoming_ids", "problem_ids") and isinstance(part, list):
                result.update(map(str, part))
            elif isinstance(part, (dict, list)):
                result.update(problem_ids(part))
    elif isinstance(value, list):
        for part in value:
            result.update(problem_ids(part))
    return result


def reserve(spec):
    """Root calls this against the actual current master, queue and FLOW."""
    with control(spec):
        master = Path(spec["master_db"]).resolve()
        d.require(master.is_file(), "current master database missing")
        with contextlib.closing(sqlite3.connect(master.as_uri() + "?mode=ro", uri=True)) as db:
            used = {str(r[0]) for r in db.execute("SELECT problem_id FROM problems")}
        used |= problem_ids(d.load(spec["queue_path"])) | problem_ids(d.load(spec["flow_path"]))
        path = Path(spec["reservations_path"])
        record = d.load(path) if path.exists() else {"schema_version": 2, "policy": d.POLICY, "entries": []}
        d.require(record.get("policy") == d.POLICY, "unsupported reservation policy")
        used |= problem_ids(record)
        output = []
        for request in spec["requests"]:
            protocols = (None, focused.PROTOCOL, "material-preparation-v1") if spec.get("preparation_basis") == d.MATERIAL_BASIS else (None, focused.PROTOCOL)
            d.require(request.get("review_protocol") in protocols, "unknown reservation review protocol")
            fields = ("task_id", "revision", "source_id", "source_version", "claim_key") + (("review_protocol",) if request.get("review_protocol") else ())
            d.require(all(d.nonempty(request.get(k)) for k in fields), "reservation needs exact task/revision/source/claim")
            old = [r for r in record["entries"] if r["task_id"] == request["task_id"]]
            if old:
                d.require(len(old) == 1 and all(old[0].get(k) == request[k] for k in fields) and old[0].get("review_protocol") == request.get("review_protocol"), "task already reserved with different revision/claim")
                output.append(old[0])
                continue
            ident = next((str(i) for i in range(FIRST_ID, LAST_ID + 1) if str(i) not in used), None)
            d.require(ident is not None, "approved ID namespace exhausted")
            row = {k: request[k] for k in fields}
            row.update(problem_id=ident, reserved_at=d.utc_now(), actor=spec["actor"], status="reserved_not_produced")
            record["entries"].append(row)
            output.append(row)
            used.add(ident)
        d.save(path, record)
        return {"status": "reserved_not_produced", "entries": output, "material_increment": 0}


def select_qualifications(spec):
    paths = spec.get("qualification_paths", [])
    d.require(isinstance(paths, list), "qualification_paths must be an explicit root-approved list")
    records = [qualification.validate_record(d.load(path)) for path in paths]
    d.require(len({record["qualification_set_id"] for record in records}) == len(records), "duplicate qualification set ID")
    return records


def select_jobs(spec, qualification_records=None):
    paths = spec["job_paths"]
    records = select_qualifications(spec) if qualification_records is None else qualification_records
    if paths == []:
        d.require(bool(records), "empty jobs require a nonempty approved existing-qualification set")
        return []
    d.require(not records, "publish new jobs and existing-qualification updates in separate bounded batches")
    if spec.get("preparation_basis") == d.MATERIAL_BASIS:
        d.require(isinstance(paths, list) and 1 <= len(paths) <= 200, "a publication batch must contain 1..200 explicit jobs")
        reservations = d.load(spec["reservations_path"])["entries"]
        jobs, seen, claims = [], set(), set()
        for path in paths:
            job = Path(path).resolve()
            verified = d.verify_job(job)
            ident = verified["problem_id"]
            d.require(verified.get("preparation_basis") == d.MATERIAL_BASIS, "material publication requires explicitly adopted material")
            d.require(ident not in seen and verified["claim_key"] not in claims and ident.isdecimal() and
                      FIRST_ID <= int(ident) <= LAST_ID, "duplicate or unreserved-namespace problem ID/claim")
            d.require(any(d.binding(r) == d.binding(verified) for r in reservations), "job has no matching ID reservation")
            seen.add(ident); claims.add(verified["claim_key"])
            jobs.append((job, verified))
        return jobs
    white = d.load(spec["whitelist_path"])
    focused_mode = white.get("review_protocol") == focused.PROTOCOL
    d.require(white.get("schema_version") == 2 and white.get("policy") == d.POLICY and d.nonempty(white.get("created_by") if focused_mode else white.get("approved_by")),
              "explicit approved revision-v2 whitelist required")
    allowed = white.get("entries", [])
    d.require(allowed and len({r["task_id"] for r in allowed}) == len(allowed), "whitelist must be finite with unique tasks")
    paths = spec["job_paths"]
    d.require(isinstance(paths, list) and 1 <= len(paths) <= 200, "a publication batch must contain 1..200 explicit jobs")
    reservations = d.load(spec["reservations_path"])["entries"]
    jobs, seen, tasks = [], set(), []
    for path in paths:
        job = Path(path).resolve()
        verified = d.verify_job(job)
        ident = verified["problem_id"]
        d.require(ident not in seen and ident.isdecimal() and FIRST_ID <= int(ident) <= LAST_ID, "duplicate or unreserved-namespace problem ID")
        seen.add(ident)
        matching = [r for r in allowed if d.binding(r) == d.binding(verified)]
        d.require(len(matching) == 1 and matching[0].get("status") == "approved_for_automatic_publication", "job not approved in finite whitelist")
        state = d.load(job / "job-state.json")
        task = d.load(job / state["package"] / state["task_snapshot"])
        if focused_mode:
            d.require(task.get("review_protocol") == focused.PROTOCOL, "focused whitelist requires focused task")
            auth_path = d.relative_path(Path(spec["whitelist_path"]).resolve().parent, white.get("source_authorization_path"), existing=True)
            focused.validate_authorization(task, d.load(auth_path))
        else:
            d.require(task.get("review_protocol") is None, "focused task requires source-authorized whitelist")
        check_approved_task(matching[0], spec["whitelist_path"], job, task)
        tasks.append(task)
        d.require(any(d.binding(r) == d.binding(verified) for r in reservations), "job has no matching root ID reservation")
        jobs.append((job, verified))
    if focused_mode:
        sample_path = d.relative_path(Path(spec["whitelist_path"]).resolve().parent, white.get("sample_record_path"), existing=True)
        focused.validate_sample(d.load(sample_path), tasks, sample_path.parent)
    return jobs


def check_approved_task(entry, whitelist_path, job, task):
    """Root-owned snapshot is referenced by the root-owned finite whitelist."""
    approved_path = d.relative_path(Path(whitelist_path).resolve().parent, entry.get("approved_task_path"), existing=True)
    d.require(not approved_path.is_relative_to(Path(job).resolve()), "approved task snapshot cannot be inside a worker job")
    approved = d.load(approved_path)
    d.require(d.binding(approved) == d.binding(task) and d.task_config(approved) == d.task_config(task),
              "worker task configuration differs from root-approved task snapshot")


def isolated_git(repo, work, base, branch, origin):
    repo, work = Path(repo).resolve(), Path(work).resolve()
    d.require(COMMIT.fullmatch(base), "explicit full public Git commit required")
    d.require(git(["--git-dir", repo, "cat-file", "-t", base]) == "commit", "public base commit unavailable")
    objects = repo / "objects"
    d.require(objects.is_dir() and not work.exists(), "fresh isolated publication directory required")
    git(["init", str(work)])
    gitdir = work / ".git"
    if os.name == "nt":
        git(["-C", work, "config", "core.longpaths", "true"])
    (gitdir / "objects/info/alternates").write_text(objects.as_posix() + "\n", encoding="utf-8", newline="\n")
    # Alternates share objects, but Git's shallow-history boundary is per repo.
    # Preserve that metadata so revision walks do not request absent ancestors.
    if (repo / "shallow").is_file():
        shutil.copyfile(repo / "shallow", gitdir / "shallow")
    for name in ("user.name", "user.email"):
        value = git(["--git-dir", repo, "config", "--get", name])
        d.require(bool(value), "existing Git author identity required")
        git(["-C", work, "config", name, value])
    git(["-C", work, "remote", "add", "origin", origin])
    git(["-C", work, "update-ref", "refs/heads/" + branch, base])
    git(["-C", work, "symbolic-ref", "HEAD", "refs/heads/" + branch])
    git(["-C", work, "read-tree", base])
    return gitdir


def public_job(job, corpus, task):
    """Copy only one reviewed job's declared deliverables into its own namespace."""
    state = d.load(job / "job-state.json")
    package = job / state["package"]
    row = d.load(package / "manifest.json")["items"][0]
    relative = Path("prepared-jobs") / task["task_id"] / task["revision"]
    target = corpus / relative
    paths = {"job-state.json", "PAGE_QA-root-" + task["revision"] + ".json",
             "final-item-root-" + task["revision"] + ".json"}
    if state.get("preparation_basis") == d.MATERIAL_BASIS:
        paths.discard("PAGE_QA-root-" + task["revision"] + ".json")
    # Package consists only of declared source/asset/evidence/SQL outputs created
    # by prepared_delivery; no runtime cache or unrelated parent tree is copied.
    for path in package.rglob("*"):
        d.require(not path.is_symlink(), "symlink in job package")
        if path.is_file():
            paths.add(path.relative_to(job).as_posix())
    receipt = d.load(package / row["compile_receipt"])
    paths.add(state["receipt_root"] + "/" + task["problem_id"] + ".json")
    paths.add(receipt["pdf_path"])
    if state.get("preparation_basis") != d.MATERIAL_BASIS:
        paths.update(receipt["rendered_pages"])
        paths.add(receipt["compiler_log_path"])
        for path in (job / receipt["pdf_path"]).parent.iterdir():
            if path.is_file() and path.suffix in (".aux", ".fls", ".out", ".bbl", ".blg"):
                paths.add(path.relative_to(job).as_posix())
    for name in sorted(paths):
        src = d.relative_path(job, name, existing=True)
        dst = d.relative_path(target, name)
        d.require(not dst.exists(), "fresh public job output required")
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
    return exported_row(row, relative, state), [(relative / name).as_posix() for name in sorted(paths)]


def exported_row(row, relative, state):
    prefix = (relative / state["package"]).as_posix() + "/"
    exported = copy.deepcopy(row)
    for key in ("item_path", "compile_receipt", "license_path", "license_evidence_path"):
        exported[key] = prefix + row[key]
    for key in ("asset_dependencies", "source_files"):
        for asset in exported[key]:
            asset["path"] = prefix + asset["path"]
    exported["prepared_job"] = relative.as_posix()
    return exported


def normalize_source_rows(rows, baseline, reconciliations=()):
    # sources has one row per fixed source. Multiple claims keep their own
    # evidence paths while the common source-level NOTICE points to the first.
    known = {row["source_id"]: row for row in baseline}
    for row in rows:
        old = known.get(row["source_id"])
        if old:
            fields = ("author", "work", "source_url", "source_version", "license")
            if any(row[key] != old[key] for key in fields):
                matches = [entry for entry in reconciliations if entry.get("source_id") == row["source_id"]]
                material = row.get("preparation_basis") == d.MATERIAL_BASIS
                d.require(len(matches) == 1, "same-source metadata conflict needs an explicit reconciliation")
                entry = matches[0]
                recorder = entry.get("recorded_by", entry.get("approved_by")) if material else entry.get("approved_by")
                d.require(d.nonempty(recorder) and d.nonempty(entry.get("reason")),
                          "source reconciliation needs the recorder and a reason" if material else
                          "source reconciliation needs an explicit root decision")
                d.require(entry.get("task_metadata") == {key: row[key] for key in fields} and
                          entry.get("public_metadata") == {key: old[key] for key in fields},
                          "source reconciliation does not match the actual fixed-version metadata")
                # Preserve the reviewed task identity inside its immutable job;
                # the shared sources table retains the existing public spelling.
                row["reviewed_task_source_metadata"] = {key: row[key] for key in fields}
                row["source_metadata_reconciliation"] = entry
                for key in fields:
                    row[key] = old[key]
            row["license_path"], row["retrieved_at"] = old["license_path"], old.get("retrieved_at", "")
        else:
            known[row["source_id"]] = row


def apply_delta(master, delta):
    with sqlite3.connect(master) as db:
        db.execute("PRAGMA foreign_keys=ON")
        db.execute("ATTACH DATABASE ? AS incoming", (str(delta),))
        # Compare source metadata only; stored author mathematics is inserted,
        # never used in a content comparison or fingerprint operation.
        for source in db.execute("SELECT " + ",".join(d.SOURCE_COLUMNS) + " FROM incoming.sources").fetchall():
            old = db.execute("SELECT " + ",".join(d.SOURCE_COLUMNS) + " FROM sources WHERE source_id=?", (source[0],)).fetchone()
            d.require(old is None or old == source, "delta source metadata conflicts with current database")
            if old is None:
                db.execute("INSERT INTO sources VALUES (?,?,?,?,?,?,?,?)", source)
        columns = (*d.LEGACY_COLUMNS, *d.ADDED_COLUMNS)
        available = {row[1] for row in db.execute("PRAGMA incoming.table_info(problems)")}
        d.require(set(columns) - available <= {"qualification_set_id", "review_protocol"}, "incoming delta schema is missing required columns")
        source_columns = [name if name in available else "NULL" for name in columns]
        db.execute("INSERT INTO problems (" + ",".join(columns) + ") SELECT " + ",".join(source_columns) + " FROM incoming.problems")


def validate_restore_batch(descriptor, batch_id):
    if batch_id is None:  # Explicit standalone all-assets restoration.
        return
    job_batches = {entry["batch_id"] for entry in descriptor.get("deltas", [])}
    qualification_batches = {entry["batch_id"] for entry in descriptor.get("qualification_records", []) if entry.get("batch_id")}
    d.require(batch_id in job_batches | qualification_batches, "requested restore batch is not present in descriptor")
    d.require(not (batch_id in job_batches and batch_id in qualification_batches), "requested restore batch has ambiguous delivery types")
    pending_jobs = {entry["batch_id"] for entry in descriptor.get("deltas", []) if not entry.get("published_commit")}
    d.require(pending_jobs <= {batch_id}, "requested restore batch would skip an unpublished new delta")


def restore_database(repo, commit, destination, *, corpus_prefix="editable-corpus", batch_id=None):
    """Read all inputs from one actual Git commit, never from local job roots."""
    repo, destination = Path(repo).resolve(), Path(destination).resolve()
    d.require(COMMIT.fullmatch(commit) and not destination.exists(), "restore needs a full commit and fresh destination")
    destination.mkdir(parents=True)
    manifest = git_json(repo, commit, corpus_prefix + "/manifest.json")
    try:
        descriptor = git_json(repo, commit, corpus_prefix + "/prepared-database.json")
    except ValueError as exc:
        # A base without v2 is explicitly recognized by its tree, not by
        # swallowing a damaged/malformed prepared descriptor.
        names = git(["--git-dir", repo, "ls-tree", "--name-only", commit + ":" + corpus_prefix]).splitlines()
        if "prepared-database.json" in names:
            raise exc
        old = git_json(repo, commit, corpus_prefix + "/database-delivery.json")
        descriptor = {"schema_version": 2, "policy": d.POLICY, "base": {
            "format": old["format"], "parts": [{"index": p["index"], "path": p["path"]} for p in old["parts"]]}, "deltas": []}
    d.require(descriptor.get("policy") == d.POLICY, "unsupported restoration policy")
    validate_restore_batch(descriptor, batch_id)
    parts = descriptor["base"]["parts"]
    d.require([p["index"] for p in parts] == list(range(len(parts))) and parts, "base parts must have explicit contiguous order")
    d.require(descriptor["base"]["format"] == "ordered gzip-compressed SQLite parts", "unsupported base SQLite delivery")
    compressed = destination / "base.sqlite.gz"
    with compressed.open("xb") as out:
        for part in parts:
            rel = part["path"]
            d.relative_path(destination, rel)
            result = subprocess.run(["git", "--git-dir", str(repo), "show", commit + ":" + corpus_prefix + "/" + rel],
                                    stdout=out, stderr=subprocess.PIPE)
            d.require(result.returncode == 0, "public database part missing: " + rel)
    base_db, master = destination / "base.sqlite", destination / "corpus.sqlite"
    with gzip.open(compressed, "rb") as source, base_db.open("xb") as target:
        shutil.copyfileobj(source, target)
    d.migrate_database(base_db, master)
    seen = set()
    for delta in descriptor["deltas"]:
        d.require(delta["batch_id"] not in seen, "duplicate database delta")
        seen.add(delta["batch_id"])
        path = d.relative_path(destination, delta["path"])
        git_file(repo, commit, corpus_prefix + "/" + delta["path"], path)
        d.validate_database(path)
        apply_delta(master, path)
    qualification_ids, qualification_updates, reviewed = set(), [], {}
    def published_review(path):
        if path not in reviewed:
            d.relative_path(destination, path)
            reviewed[path] = git_json(repo, commit, path)
            d.save(destination / path, reviewed[path])
        return reviewed[path]
    for entry in descriptor.get("qualification_records", []):
        d.require(entry["qualification_set_id"] not in qualification_ids, "duplicate published qualification set ID")
        qualification_ids.add(entry["qualification_set_id"])
        d.relative_path(destination, entry["path"])
        record = git_json(repo, commit, corpus_prefix + "/" + entry["path"])
        d.require(record["qualification_set_id"] == entry["qualification_set_id"], "qualification descriptor/record ID conflict")
        d.save(destination / corpus_prefix / entry["path"], record)
        qualification_updates.append(qualification.apply(master, manifest, record, published_review))
    sql = d.validate_database(master, manifest["items"])
    d.require(sql["problem_count"] == manifest["verified_count"], "restored material count differs from manifest")
    return {"database": str(master), "manifest": manifest, "descriptor": descriptor, "sql": sql, "qualification_updates": qualification_updates}


def stage_explicit(worktree, pathspec, *, style=None):
    """Stage only the named paths; Unix supports Git predating pathspec files."""
    worktree, pathspec = Path(worktree).resolve(), Path(pathspec).resolve()
    paths = pathspec.read_text(encoding="utf-8").split("\0")
    d.require(paths and paths[-1] == "", "stage path list must be NUL-terminated")
    paths.pop()
    d.require(paths and len(paths) == len(set(paths)), "stage path list must be nonempty and unique")
    for name in paths:
        d.require(name.startswith("editable-corpus/"), "staging is limited to explicit corpus paths")
        d.relative_path(worktree, name, existing=True)
    style = style or ("pathspec-file" if os.name == "nt" else "argv")
    d.require(style in ("pathspec-file", "argv"), "unknown explicit staging style")
    env = {"GIT_LITERAL_PATHSPECS": "1"}
    if style == "pathspec-file":
        git(["-C", worktree, "add", "--pathspec-from-file=" + str(pathspec), "--pathspec-file-nul"], env=env)
    else:
        chunk, size = [], 0
        for name in paths:
            width = len(name.encode("utf-8")) + 1
            d.require(width <= 8192, "one explicit stage path exceeds the argument budget")
            if chunk and (len(chunk) >= 64 or size + width > 8192):
                git(["-C", worktree, "add", "--", *chunk], env=env)
                chunk, size = [], 0
            chunk.append(name); size += width
        if chunk:
            git(["-C", worktree, "add", "--", *chunk], env=env)
    return paths


def commit_staged(folder, state):
    spec = state["spec"]
    work = folder / "worktree"
    d.require(git(["-C", work, "rev-parse", "HEAD"]) == spec["public_base_commit"],
              "isolated HEAD is no longer the frozen public base; reconcile the existing commit")
    paths = stage_explicit(work, folder / state["stage_paths"])
    staged = git(["-C", work, "diff", "--cached", "--name-only", "-z", spec["public_base_commit"]]).split("\0")
    d.require({p for p in staged if p} <= set(paths), "private index contains an undeclared staged path")
    title = "Publish author proof materials " if state["spec"].get("preparation_basis") == d.MATERIAL_BASIS else "Publish reviewed mathematical tasks "
    git(["-C", work, "commit", "-m", title + state["batch_id"]])
    commit = git(["-C", work, "rev-parse", "HEAD"])
    parents = git(["-C", work, "show", "-s", "--format=%P", commit]).split()
    d.require(parents == [spec["public_base_commit"]], "candidate parent is not the exact public base")
    state.update(stage="prepared_not_pushed", candidate_commit=commit, prepared_at=d.utc_now())
    d.save(folder / "publication.json", state)
    return {k: v for k, v in state.items() if k != "spec"}


def prepare(spec):
    """Prepare a local candidate commit only. Root separately calls publish."""
    with control(spec, publication=True):
        q = idle_queue(spec)
        qualifications = select_qualifications(spec)
        jobs = select_jobs(spec, qualifications)
        batch = spec["batch_id"]
        d.require(d.ID.fullmatch(batch), "invalid batch name")
        folder = Path(spec["publication_root"]).resolve() / batch
        d.require(not folder.exists(), "batch output exists; preserve it and use resume/status")
        folder.mkdir(parents=True)
        state = {"schema_version": 2, "policy": d.POLICY, "batch_id": batch, "actor": spec["actor"],
                 "stage": "preparing", "public_base_commit": spec["public_base_commit"], "created_at": d.utc_now(),
                 "incoming": [d.binding(t) for _, t in jobs], "qualification_set_ids": [r["qualification_set_id"] for r in qualifications], "spec": spec}
        d.save(folder / "publication.json", state)
        try:
            repo = isolated_git(spec["base_git_dir"], folder / "worktree", spec["public_base_commit"], spec["branch"], spec["origin_url"])
            baseline = restore_database(repo, spec["public_base_commit"], folder / "base-restore")
            d.require(baseline["sql"]["problem_count"] == q["base"]["remote_main_count"], "public baseline differs from current controller material count")
            corpus = folder / "worktree/editable-corpus"
            corpus.mkdir(parents=True)
            manifest, descriptor = baseline["manifest"], baseline["descriptor"]
            ids = {str(r["problem_id"]) for r in manifest["items"]}
            claims = {r["claim_key"] for r in manifest["items"] if r.get("claim_key")}
            rows, assets = [], []
            for job, task in jobs:
                d.require(task["problem_id"] not in ids and task["claim_key"] not in claims, "duplicate published ID/claim")
                row, names = public_job(job, corpus, task)
                rows.append(row); assets.extend(names)
                ids.add(task["problem_id"]); claims.add(task["claim_key"])
            normalize_source_rows(rows, manifest["items"], spec.get("source_reconciliations", spec.get("approved_source_reconciliations", [])))
            new_paths = []
            if rows:
                delta_path = "prepared-deltas/" + batch + ".sqlite"
                d.create_database(corpus, rows, corpus / delta_path)
                apply_delta(baseline["database"], corpus / delta_path)
                new_paths.append(delta_path)
            manifest["items"].extend(rows)
            manifest.update(schema_version=2, verified_count=len(manifest["items"]), prepared_policy=d.POLICY)
            for delta in descriptor["deltas"]:
                if not delta.get("published_commit"):
                    delta["published_commit"] = spec["public_base_commit"]
            if rows:
                descriptor["deltas"].append({"batch_id": batch, "path": delta_path, "problem_ids": [r["problem_id"] for r in rows],
                                             "job_paths": [r["prepared_job"] for r in rows], "artifact_paths": assets,
                                             "published_commit": None})
            entries = descriptor.setdefault("qualification_records", [])
            for record in qualifications:
                sid = record["qualification_set_id"]
                previous = [entry for entry in entries if entry["qualification_set_id"] == sid]
                if previous:
                    old = git_json(repo, spec["public_base_commit"], "editable-corpus/" + previous[0]["path"])
                    d.require(qualification.metadata(old) == qualification.metadata(record), "qualification set ID conflicts with published metadata")
                    raise ValueError("qualification set already published; reuse its existing completion")
                d.require(record["basis_public_commit"] == spec["public_base_commit"], "qualification approval must name this exact public baseline")
                path = "qualifications/" + sid + ".json"
                qualification.apply(baseline["database"], manifest, record,
                                    lambda path: git_json(repo, spec["public_base_commit"], path))
                d.save(corpus / path, record)
                entries.append({"qualification_set_id": sid, "path": path, "batch_id": batch})
                new_paths.append(path)
            descriptor["material_count"] = len(manifest["items"])
            d.save(corpus / "manifest.json", manifest)
            d.save(corpus / "prepared-database.json", descriptor)
            sql = d.validate_database(baseline["database"], manifest["items"])
            # Consumers receive the same no-fingerprint tools used here.
            for name in CONSUMER_HELPERS:
                shutil.copyfile(Path(__file__).with_name(name), corpus / name)
            files = assets + new_paths + ["manifest.json", "prepared-database.json", *CONSUMER_HELPERS]
            pathspec = folder / "stage-paths.txt"
            pathspec.write_text("\0".join("editable-corpus/" + p for p in files) + "\0", encoding="utf-8")
            state.update(stage="ready_to_stage", prepare_checkpoint="ready_to_stage", stage_paths=pathspec.name,
                         material_count=len(manifest["items"]), increment=len(rows), sql=sql, git_dir=str(repo))
            d.save(folder / "publication.json", state)
            return commit_staged(folder, state)
        except Exception as exc:
            state.update(stage="needs_codex", error=str(exc))
            d.save(folder / "publication.json", state)
            raise


def resume_prepare(folder, *, approve_existing_stage=False):
    """Resume only an existing completed projection, never repeat its build/SQL writes."""
    folder = Path(folder).resolve()
    state = d.load(folder / "publication.json")
    spec = state["spec"]
    with control(spec, publication=True):
        state = d.load(folder / "publication.json")
        d.require(state.get("policy") == d.POLICY and state.get("actor") == spec["actor"], "prepared recovery actor/policy conflict")
        d.require(folder == Path(spec["publication_root"]).resolve() / spec["batch_id"] and
                  state["batch_id"] == spec["batch_id"] and state["public_base_commit"] == spec["public_base_commit"],
                  "prepared recovery batch/base/location conflict")
        d.require(state["stage"] in ("ready_to_stage", "needs_codex") and not state.get("candidate_commit"),
                  "stage-only recovery requires an uncommitted preparation")
        checkpoint = state.get("prepare_checkpoint") == "ready_to_stage"
        d.require(checkpoint or approve_existing_stage, "older preparation needs explicit --approve-existing-stage")
        q = idle_queue(spec)
        qualifications = select_qualifications(spec)
        jobs = select_jobs(spec, qualifications)
        d.require(state["incoming"] == [d.binding(t) for _, t in jobs], "prepared recovery incoming whitelist/revision conflict")
        d.require(state.get("qualification_set_ids", []) == [r["qualification_set_id"] for r in qualifications], "prepared qualification whitelist conflict")
        work, corpus = folder / "worktree", folder / "worktree/editable-corpus"
        repo, base = work / ".git", spec["public_base_commit"]
        d.require(git(["-C", work, "rev-parse", "HEAD"]) == base, "prepared HEAD already advanced; reconcile the existing commit")
        d.require(git(["-C", work, "symbolic-ref", "HEAD"]) == "refs/heads/" + spec["branch"] and
                  git(["-C", work, "remote", "get-url", "origin"]) == spec["origin_url"], "prepared Git branch/origin conflict")
        baseline = git_json(repo, base, "editable-corpus/manifest.json")
        base_rows = baseline["items"]
        d.require(baseline["verified_count"] == len(base_rows) == q["base"]["remote_main_count"], "prepared recovery public baseline/count conflict")
        names = git(["--git-dir", repo, "ls-tree", "--name-only", base + ":editable-corpus"]).splitlines()
        if "prepared-database.json" in names:
            prior_descriptor = git_json(repo, base, "editable-corpus/prepared-database.json")
        else:
            delivery = git_json(repo, base, "editable-corpus/database-delivery.json")
            prior_descriptor = {"base": {"format": delivery["format"],
                                "parts": [{"index": part["index"], "path": part["path"]} for part in delivery["parts"]]}, "deltas": []}
        expected_prior = copy.deepcopy(prior_descriptor["deltas"])
        for delta in expected_prior:
            if not delta.get("published_commit"):
                delta["published_commit"] = base
        manifest, descriptor = d.load(corpus / "manifest.json"), d.load(corpus / "prepared-database.json")
        d.require(descriptor.get("policy") == d.POLICY and descriptor["base"] == prior_descriptor["base"] and
                  (descriptor["deltas"][:-1] == expected_prior if jobs else descriptor["deltas"] == expected_prior) and
                  len(descriptor["deltas"]) == len(expected_prior) + (1 if jobs else 0), "prepared recovery database chain metadata conflict")
        delta = descriptor["deltas"][-1] if jobs else None
        incoming_ids = [t["problem_id"] for _, t in jobs]
        job_paths = ["prepared-jobs/" + t["task_id"] + "/" + t["revision"] for _, t in jobs]
        d.require(not jobs or (delta["batch_id"] == state["batch_id"] and delta["problem_ids"] == incoming_ids and
                  delta["job_paths"] == job_paths and delta.get("published_commit") is None and
                  delta["path"] == "prepared-deltas/" + state["batch_id"] + ".sqlite"), "prepared recovery delta identity conflict")
        qualification_paths = []
        expected_entries = copy.deepcopy(prior_descriptor.get("qualification_records", []))
        for record in qualifications:
            sid = record["qualification_set_id"]
            d.require(not any(entry["qualification_set_id"] == sid for entry in expected_entries), "qualification set already present in baseline")
            path = "qualifications/" + sid + ".json"
            d.require(qualification.metadata(d.load(corpus / path)) == qualification.metadata(record) and record["basis_public_commit"] == base,
                      "prepared qualification record differs from root approval/base")
            expected_entries.append({"qualification_set_id": sid, "path": path, "batch_id": state["batch_id"]})
            qualification_paths.append(path)
            qualification.project_rows(qualification.reviewed_rows(baseline, record, lambda path: git_json(repo, base, path)), record)
        d.require(descriptor.get("qualification_records", []) == expected_entries, "prepared qualification sequence differs")
        by_id = {r["problem_id"]: r for r in manifest["items"]}
        d.require(len(by_id) == len(manifest["items"]) and set(by_id) == {r["problem_id"] for r in base_rows} | set(incoming_ids),
                  "prepared recovery material ID set conflict")
        expected_count = len(base_rows) + len(jobs)
        d.require(manifest["verified_count"] == descriptor["material_count"] == len(by_id) == expected_count,
                  "prepared recovery material count conflict")
        fields = ("title", "difficulty_level", "difficulty_reason", "source_id", "item_path", "origin_class", "status", "compile_receipt")
        for row in base_rows:
            actual = by_id[row["problem_id"]]
            d.require(all(actual.get(k) == row.get(k) for k in fields) and
                      d.locator_metadata(d.locator(actual)) == d.locator_metadata(d.locator(row)),
                      "prepared recovery legacy metadata differs from public base")
            if row.get("qualification_set_id"):
                d.require(all(actual.get(key) == row.get(key) for key in qualification.QUAL_COLUMNS), "prepared legacy qualification metadata conflict")
        rows = []
        for (original, task), relative in zip(jobs, job_paths):
            public = corpus / relative
            restored = d.verify_job(public, require_ready=False)
            d.require(d.binding(restored) == d.binding(task), "prepared copied job identity conflict")
            js = d.load(public / "job-state.json")
            task_copy = d.load(public / js["package"] / js["task_snapshot"])
            original_state = d.load(original / "job-state.json")
            task_original = d.load(original / original_state["package"] / original_state["task_snapshot"])
            d.require(d.task_config(task_copy) == d.task_config(task_original), "prepared copied task configuration conflict")
            row = d.load(public / js["package"] / "manifest.json")["items"][0]
            rows.append(exported_row(row, Path(relative), js))
        normalize_source_rows(rows, base_rows, spec.get("source_reconciliations", spec.get("approved_source_reconciliations", [])))
        # These objects contain metadata and locators, not the author TeX body.
        d.require(rows == [by_id[ident] for ident in incoming_ids], "prepared incoming row metadata conflict")
        if jobs:
            d.validate_database(d.relative_path(corpus, delta["path"], existing=True), rows)
        sql = d.validate_database(folder / "base-restore/corpus.sqlite", manifest["items"])
        new_files = delta["artifact_paths"] + [delta["path"]] if jobs else qualification_paths
        expected_files = ["editable-corpus/" + name for name in new_files +
                          ["manifest.json", "prepared-database.json", *CONSUMER_HELPERS]]
        d.require(not jobs or all(any(name.startswith(job + "/") for job in job_paths) for name in delta["artifact_paths"]),
                  "prepared delta declares an asset outside incoming jobs")
        stage_path = folder / "stage-paths.txt"
        declared = stage_path.read_text(encoding="utf-8").split("\0")
        d.require(declared and declared[-1] == "" and len(declared) - 1 == len(set(expected_files)) and
                  set(declared[:-1]) == set(expected_files), "prepared explicit stage path set conflict")
        for name in expected_files:
            d.relative_path(work, name, existing=True)
        if checkpoint:
            d.require(state["material_count"] == expected_count and state["increment"] == len(jobs) and
                      state["sql"]["problem_count"] == sql["problem_count"], "saved stage checkpoint/count conflict")
        history = folder / "preparation-recovery"
        number = int(state.get("prepare_resume_attempts", 0)) + 1
        snapshot = history / ("attempt-" + str(number).zfill(3))
        d.require(not snapshot.exists(), "recovery evidence directory already exists")
        snapshot.mkdir(parents=True)
        d.save(snapshot / "prior-publication.json", state)
        # Update just the declared consumer helpers, retaining their old copies;
        # mathematical packages, assets and existing databases are untouched.
        for name in CONSUMER_HELPERS:
            shutil.copyfile(corpus / name, snapshot / name)
            shutil.copyfile(Path(__file__).with_name(name), corpus / name)
        state.update(stage="ready_to_stage", prepare_checkpoint="ready_to_stage", stage_paths=stage_path.name,
                     material_count=expected_count, increment=len(jobs), sql=sql, git_dir=str(repo),
                     prepare_resume_attempts=number, existing_stage_approved=bool(approve_existing_stage), resumed_at=d.utc_now())
        if "error" in state:
            state["previous_prepare_error"] = state.pop("error")
        d.save(folder / "publication.json", state)
        try:
            return commit_staged(folder, state)
        except Exception as exc:
            state.update(stage="needs_codex", error=str(exc))
            d.save(folder / "publication.json", state)
            raise


def restore_release(repo, commit, output, *, batch_id=None):
    restored = restore_database(repo, commit, output, batch_id=batch_id)
    output = Path(output).resolve()
    reports = []
    for delta in restored["descriptor"]["deltas"]:
        if batch_id is not None and delta["batch_id"] != batch_id:
            continue
        for name in delta["artifact_paths"]:
            dst = d.relative_path(output, "editable-corpus/" + name)
            git_file(repo, commit, "editable-corpus/" + name, dst)
        for job in delta["job_paths"]:
            report = d.verify_job(output / "editable-corpus" / job, require_ready=False)
            state = d.load(output / "editable-corpus" / job / "job-state.json")
            row = d.load(output / "editable-corpus" / job / state["package"] / "manifest.json")["items"][0]
            receipt = d.load(output / "editable-corpus" / job / state["package"] / row["compile_receipt"])
            pdf = output / "editable-corpus" / job / receipt["pdf_path"]
            # Poppler on Windows does not accept deep file names/cwd. Its
            # supported stdin mode reads the real restored PDF without a copy.
            with pdf.open("rb") as stream:
                info = subprocess.run([d.tool("pdfinfo"), "-"], stdin=stream, stdout=subprocess.PIPE,
                                      stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace")
            text = info.stdout
            pdf.with_suffix(".restored-pdfinfo.log").write_text(text, encoding="utf-8")
            d.require(info.returncode == 0, "restored PDF is unreadable; see restored-pdfinfo.log")
            d.require(re.search(r"^Pages:\s+" + str(receipt["pages"]) + r"\s*$", text, re.M), "restored PDF page count differs")
            reports.append(report)
    # The receipt's exact commit becomes the SQL publication state only after
    # all Git-sourced assets/metadata above have actually restored successfully.
    with sqlite3.connect(restored["database"]) as db:
        for delta in restored["descriptor"]["deltas"]:
            for ident in delta["problem_ids"]:
                db.execute("UPDATE problems SET publication_commit=? WHERE problem_id=? AND validation_policy=?",
                           (delta.get("published_commit") or commit, ident, d.POLICY))
    final_sql = d.validate_database(restored["database"])
    final_sql["metadata_projection_consistent"] = restored["sql"]["metadata_projection_consistent"]
    final_sql["metadata_projection_checked_before_publication_annotation"] = True
    result = {"schema_version": 2, "policy": d.POLICY, "status": "exact_commit_restored", "verified_corpus_commit": commit,
              "material_count": restored["sql"]["problem_count"], "restored_prepared_jobs": len(reports),
              "asset_restore_scope": "all_prepared_jobs" if batch_id is None else "current_batch_only", "asset_batch_id": batch_id,
              "database": restored["database"], "sql": final_sql, "jobs": reports,
              "existing_qualification_updates": restored.get("qualification_updates", [])}
    d.save(output / "RESTORE_RESULT.json", result)
    d.save(output / "editable-corpus/manifest.json", restored["manifest"])
    return result


def remote_commit(repo, origin, branch):
    text = git(["--git-dir", repo, "ls-remote", origin, "refs/heads/" + branch])
    records = [line.split() for line in text.splitlines() if line.strip()]
    d.require(len(records) == 1 and records[0][1] == "refs/heads/" + branch and COMMIT.fullmatch(records[0][0]),
              "public branch does not resolve to one exact commit")
    return records[0][0]


def finish_reconciled_marker(state, spec, folder):
    """Complete only this batch's final marker from existing verified receipts.

    Called with both protocol locks held. No Git command, re-count or asset
    restoration occurs on this recovery edge.
    """
    candidate = state.get("verified_corpus_commit")
    d.require(COMMIT.fullmatch(str(candidate)) and candidate == state.get("candidate_commit"), "reconciled commit binding conflict")
    receipt = d.load(state["public_restore_result"])
    queue = d.load(spec["queue_path"])
    last = queue.get("last_publication", {})
    d.require(receipt.get("status") == "exact_commit_restored" and receipt.get("verified_corpus_commit") == candidate and
              receipt.get("material_count") == state["material_count"], "reconciled public restore receipt conflict")
    d.require(last.get("batch_id") == state["batch_id"] and last.get("verified_corpus_commit") == candidate and
              last.get("material_count") == state["material_count"] and
              queue["base"].get("verified_corpus_commit") == candidate and
              queue["base"]["local_count"] == queue["base"]["remote_main_count"] == state["material_count"],
              "reconciled queue/commit/count conflict")
    # Update only the current recovery pointers, retaining any old aggregate
    # paths explicitly as legacy evidence. Counts above have already matched.
    stale = {key: queue["base"].pop(key) for key in ("build_root", "receipt_root", "accepted_report") if key in queue["base"]}
    changed = bool(stale)
    if stale:
        legacy = queue["base"].setdefault("legacy_metadata", {})
        d.require(not set(stale) & set(legacy), "legacy metadata fields already exist; preserve conflicting history")
        legacy.update(stale, status="legacy_only_not_current_assets", captured_from_base_material_count=queue["base"]["local_count"])
    pointers = {"restore_report": state["public_restore_result"],
                "prepared_assets_root": (str(Path(receipt["database"]).parent / "editable-corpus/prepared-jobs")
                                         if receipt.get("restored_prepared_jobs") != 0 else None)}
    for key, value in pointers.items():
        if queue["base"].get(key) != value:
            queue["base"][key] = value
            changed = True
    if changed:
        d.save(spec["queue_path"], queue)
    marker = Path(spec["state_root"]) / "publication-external.json"
    external_complete = False
    if marker.exists():
        previous = d.load(marker)
        d.require(previous.get("batch_id") == state["batch_id"], "external marker belongs to another batch")
        marked_commit = previous.get("verified_corpus_commit", previous.get("candidate_commit"))
        d.require(marked_commit == candidate, "external marker commit conflict")
        external_complete = previous.get("state") == "completed"
    if not external_complete:
        d.save(marker, {"schema_version": 2, "policy": d.POLICY, "batch_id": state["batch_id"], "state": "completed",
                        "verified_corpus_commit": candidate, "completed_at": state["completed_at"], "marker_recovered_at": d.utc_now()})
    pending = Path(spec["state_root"]) / "pending-publication.json"
    completed = {"schema_version": 2, "policy": d.POLICY, "batch_id": state["batch_id"], "stage": "reconciled",
                 "status": "reconciled", "verified_corpus_commit": candidate, "count": state["material_count"],
                 "public_restore_result": state["public_restore_result"], "completed_at": state["completed_at"]}
    if pending.exists():
        previous = d.load(pending)
        if all(previous.get(key) == value for key, value in completed.items()):
            return
        d.require(not previous or previous.get("batch_id") == state["batch_id"] or previous.get("stage") == "reconciled" or
                  previous.get("status", previous.get("state")) in ("delivered", "complete", "completed", "verified", "reconciled"),
                  "pending publication belongs to another unfinished batch")
        history = Path(folder) / "completion-marker-history" / ("pending-before-" + str(time.time_ns()) + ".json")
        d.save(history, previous)
    d.save(pending, completed)


def begin_relay(folder):
    """Authorize one existing candidate for the trusted local Git relay."""
    folder = Path(folder).resolve()
    state = d.load(folder / "publication.json")
    spec = state["spec"]
    with control(spec, publication=True):
        state = d.load(folder / "publication.json")
        d.require(state.get("policy") == d.POLICY and state.get("actor") == spec["actor"] and
                  folder == Path(spec["publication_root"]).resolve() / spec["batch_id"] and state["batch_id"] == spec["batch_id"],
                  "relay batch/actor/location conflict")
        candidate, base, repo = state["candidate_commit"], state["public_base_commit"], state["git_dir"]
        envelope = {"schema_version": 2, "policy": d.POLICY, "batch_id": state["batch_id"], "actor": spec["actor"],
                    "candidate_commit": candidate, "public_base_commit": base, "branch": spec["branch"],
                    "origin_url": spec["origin_url"], "material_count": state["material_count"], "bundle_path": None}
        if state["stage"] == "reconciled":
            finish_reconciled_marker(state, spec, folder)
            if "error" in state:
                state["previous_external_error"] = state.pop("error")
                d.save(folder / "publication.json", state)
            return dict(envelope, status="reconciled", verified_corpus_commit=state["verified_corpus_commit"],
                        public_restore_result=state["public_restore_result"])
        d.require(state["stage"] in ("prepared_not_pushed", "external_write_unknown", "restoring", "needs_restore"),
                  "relay requires a committed prepared candidate")
        q = d.load(spec["queue_path"])
        d.require(not q.get("active_batch") and not q.get("queued_new_root_admitted") and
                  q["base"]["local_count"] == q["base"]["remote_main_count"] and
                  q["base"]["remote_main_count"] in (state["material_count"] - state["increment"], state["material_count"]),
                  "relay controller material boundary changed")
        if q["base"].get("verified_corpus_commit"):
            d.require(q["base"]["verified_corpus_commit"] in (base, candidate), "relay queue public commit conflict")
        qualifications = select_qualifications(spec)
        jobs = select_jobs(spec, qualifications)
        d.require(state["incoming"] == [d.binding(task) for _, task in jobs], "relay incoming whitelist/revision conflict")
        d.require(state.get("qualification_set_ids", []) == [record["qualification_set_id"] for record in qualifications],
                  "relay qualification whitelist conflict")
        d.require(COMMIT.fullmatch(candidate) and COMMIT.fullmatch(base) and
                  git(["--git-dir", repo, "rev-parse", "HEAD"]) == candidate and
                  git(["--git-dir", repo, "show", "-s", "--format=%P", candidate]) == base,
                  "relay candidate HEAD/parent conflict")
        descriptor = git_json(repo, candidate, "editable-corpus/prepared-database.json")
        d.require(descriptor["material_count"] == state["material_count"], "relay committed material count conflict")
        if jobs:
            delta = descriptor["deltas"][-1]
            d.require(delta["batch_id"] == state["batch_id"] and delta["problem_ids"] == [task["problem_id"] for _, task in jobs],
                      "relay committed delta identity conflict")
        for record in qualifications:
            matches = [entry for entry in descriptor.get("qualification_records", []) if entry["qualification_set_id"] == record["qualification_set_id"]]
            d.require(len(matches) == 1 and matches[0].get("batch_id") == state["batch_id"], "relay qualification descriptor conflict")
            committed = git_json(repo, candidate, "editable-corpus/" + matches[0]["path"])
            d.require(qualification.metadata(committed) == qualification.metadata(record), "relay qualification record differs from root approval")
        for original, task in jobs:
            js = d.load(original / "job-state.json")
            approved_task = d.load(original / js["package"] / js["task_snapshot"])
            path = "editable-corpus/prepared-jobs/" + task["task_id"] + "/" + task["revision"] + "/" + js["package"] + "/" + js["task_snapshot"]
            committed_task = git_json(repo, candidate, path)
            d.require(d.binding(committed_task) == d.binding(approved_task) and d.task_config(committed_task) == d.task_config(approved_task),
                      "relay committed task differs from current approved configuration")
        observed = remote_commit(repo, spec["origin_url"], spec["branch"])
        d.require(observed in (base, candidate), "relay public branch moved away from frozen base/candidate")
        marker = Path(spec["state_root"]) / "publication-external.json"
        if marker.exists():
            previous = d.load(marker)
            d.require(previous.get("batch_id") == state["batch_id"] or previous.get("state") in ("completed", "reconciled"),
                      "another external publication requires recovery")
        state.update(stage="external_write_unknown", relay_authorized_at=d.utc_now(), relay_observed_commit=observed)
        d.save(folder / "publication.json", state)
        d.save(marker, {"schema_version": 2, "policy": d.POLICY, "batch_id": state["batch_id"], "actor": spec["actor"],
                        "state": "unknown", "operation": "local_git_relay", "candidate_commit": candidate, "public_base_commit": base,
                        "branch": spec["branch"], "registered_at": d.utc_now()})
        if observed == candidate:
            return dict(envelope, status="awaiting_public_restore", observed_public_commit=observed)
        relay = state.get("relay_bundle")
        if relay:
            bundle = d.relative_path(folder, relay["path"], existing=True)
            d.require(relay.get("candidate_commit") == candidate and relay.get("public_base_commit") == base,
                      "existing relay bundle metadata conflict")
            heads = git(["--git-dir", repo, "bundle", "list-heads", bundle, "HEAD"]).split()
            d.require(heads == [candidate, "HEAD"], "existing relay bundle HEAD conflict")
            git(["--git-dir", repo, "bundle", "verify", bundle])
        else:
            attempt = int(state.get("relay_bundle_attempts", 0)) + 1
            state["relay_bundle_attempts"] = attempt
            d.save(folder / "publication.json", state)
            bundle = folder / "relay" / ("candidate-" + str(attempt).zfill(3) + ".bundle")
            bundle.parent.mkdir(exist_ok=True)
            d.require(not bundle.exists(), "relay bundle attempt already exists; preserve it")
            git(["--git-dir", repo, "bundle", "create", bundle, base + "..HEAD"])
            heads = git(["--git-dir", repo, "bundle", "list-heads", bundle, "HEAD"]).split()
            d.require(heads == [candidate, "HEAD"], "new relay bundle HEAD conflict")
            state["relay_bundle"] = {"path": bundle.relative_to(folder).as_posix(), "candidate_commit": candidate, "public_base_commit": base}
            d.save(folder / "publication.json", state)
        return dict(envelope, status="relay_ready", observed_public_commit=observed, bundle_path=str(bundle))


def publish(folder, *, restore_only=False):
    """Root-owned serial push/fetch/restore/reconcile; retry first observes Git.

    An interrupted external write is never treated as a fresh blind push. The
    origin ref must still be the frozen base or already be this exact candidate.
    """
    folder = Path(folder).resolve()
    state = d.load(folder / "publication.json")
    spec = state["spec"]
    with control(spec, publication=True):
        state = d.load(folder / "publication.json")
        d.require(state.get("policy") == d.POLICY and state["actor"] == spec["actor"], "publication actor binding differs")
        if state["stage"] == "reconciled":
            finish_reconciled_marker(state, spec, folder)
            if "error" in state:
                state["previous_external_error"] = state.pop("error")
                d.save(folder / "publication.json", state)
            return {k: v for k, v in state.items() if k != "spec"}
        d.require(state["stage"] in ("prepared_not_pushed", "external_write_unknown", "restoring", "needs_restore"),
                  "publication is not prepared or a resumable external stage")
        q = d.load(spec["queue_path"])
        d.require(not q.get("active_batch") and not q.get("queued_new_root_admitted"), "another controller batch is active")
        base_count = state["material_count"] - state["increment"]
        d.require(q["base"]["remote_main_count"] in (base_count, state["material_count"]) and
                  q["base"]["local_count"] == q["base"]["remote_main_count"], "controller material boundary changed")
        repo, candidate = state["git_dir"], state["candidate_commit"]
        d.require(COMMIT.fullmatch(candidate) and git(["--git-dir", repo, "show", "-s", "--format=%P", candidate]) == state["public_base_commit"],
                  "prepared candidate parent differs from frozen public base")
        marker = Path(spec["state_root"]) / "publication-external.json"
        if marker.exists():
            previous = d.load(marker)
            d.require(previous.get("batch_id") == state["batch_id"] or previous.get("state") in ("completed", "reconciled"),
                      "another external publication requires recovery")
        d.save(marker, {"schema_version": 2, "policy": d.POLICY, "batch_id": state["batch_id"], "actor": spec["actor"],
                        "state": "running", "candidate_commit": candidate, "started_at": d.utc_now()})
        try:
            observed = remote_commit(repo, spec["origin_url"], spec["branch"])
            d.require(observed in (state["public_base_commit"], candidate), "public branch moved; preserve this batch for reconciliation")
            d.require(not restore_only or observed == candidate, "restore-only requires the exact candidate already public; no server push attempted")
            if observed != candidate:
                # Candidate is proven to be the one-parent child of the leased
                # base. This compare-and-swap cannot replace another writer.
                state.update(stage="external_write_unknown", push_started_at=d.utc_now())
                d.save(folder / "publication.json", state)
                require_owner(spec["state_root"], spec["actor"])
                git(["--git-dir", repo, "push", "--force-with-lease=refs/heads/" + spec["branch"] + ":" + observed,
                     spec["origin_url"], candidate + ":refs/heads/" + spec["branch"]])
            d.require(remote_commit(repo, spec["origin_url"], spec["branch"]) == candidate, "public ref is not the candidate after push")
            state.update(stage="restoring", publicly_observed_commit=candidate)
            d.save(folder / "publication.json", state)
            attempt = int(state.get("restore_attempts", 0)) + 1
            state["restore_attempts"] = attempt
            d.save(folder / "publication.json", state)
            consumer = folder / ("public-consumer-" + str(attempt).zfill(3))
            d.require(not consumer.exists(), "restore attempt already exists; preserve it")
            git(["init", consumer])
            if os.name == "nt":
                git(["-C", consumer, "config", "core.longpaths", "true"])
            git(["-C", consumer, "remote", "add", "origin", spec["origin_url"]])
            # Git 2.17 requires this repository extension before filtered fetch;
            # remote.origin.promisor alone is the newer configuration spelling.
            git(["-C", consumer, "config", "core.repositoryformatversion", "1"])
            git(["-C", consumer, "config", "extensions.partialClone", "origin"])
            git(["-C", consumer, "config", "remote.origin.promisor", "true"])
            git(["-C", consumer, "config", "remote.origin.partialclonefilter", "blob:none"])
            git(["-C", consumer, "fetch", "--depth=1", "--filter=blob:none", "--no-tags", "origin", candidate])
            d.require(git(["-C", consumer, "rev-parse", "FETCH_HEAD"]) == candidate, "fresh public fetch did not return exact candidate")
            result = restore_release(consumer / ".git", candidate, folder / ("public-restore-" + str(attempt).zfill(3)), batch_id=state["batch_id"])
            d.require(result["material_count"] == state["material_count"], "public restored material count differs")
            require_owner(spec["state_root"], spec["actor"])
            q = d.load(spec["queue_path"])
            d.require(not q.get("active_batch") and not q.get("queued_new_root_admitted"), "controller queue changed during publication")
            stale = {key: q["base"].pop(key) for key in ("build_root", "receipt_root", "accepted_report") if key in q["base"]}
            if stale:
                legacy = q["base"].setdefault("legacy_metadata", {})
                d.require(not set(stale) & set(legacy), "legacy metadata fields already exist; preserve conflicting history")
                legacy.update(stale, status="legacy_only_not_current_assets", captured_from_base_material_count=q["base"]["local_count"])
            q["base"].update(local_count=result["material_count"], remote_main_count=result["material_count"],
                             validation_policy=d.POLICY, package=str(Path(result["database"]).parent / "editable-corpus"),
                             master_database=result["database"], verified_corpus_commit=candidate,
                             restore_report=str(Path(result["database"]).parent / "RESTORE_RESULT.json"),
                             prepared_assets_root=(str(Path(result["database"]).parent / "editable-corpus/prepared-jobs")
                                                   if result["restored_prepared_jobs"] else None))
            q["last_publication"] = {"batch_id": state["batch_id"], "policy": d.POLICY, "status": "verified_public",
                                     "verified_corpus_commit": candidate, "material_count": result["material_count"],
                                     "public_restore_result": str(Path(result["database"]).parent / "RESTORE_RESULT.json")}
            d.save(spec["queue_path"], q)
            state.update(stage="reconciled", verified_corpus_commit=candidate, restored_database=result["database"],
                         public_restore_result=q["last_publication"]["public_restore_result"],
                         current_qualified_prepared=result["sql"]["qualified_prepared_published_count"],
                         current_qualified_count=result["sql"]["qualified_current_published_count"], completed_at=d.utc_now())
            if "error" in state:
                state["previous_external_error"] = state.pop("error")
            d.save(folder / "publication.json", state)
            finish_reconciled_marker(state, spec, folder)
            return {k: v for k, v in state.items() if k != "spec"}
        except Exception as exc:
            # Once reconciliation is saved, a final-marker write error must
            # keep that checkpoint so retry only completes the marker.
            next_stage = state["stage"] if state["stage"] in ("external_write_unknown", "reconciled") else "needs_restore"
            state.update(stage=next_stage, error=str(exc))
            d.save(folder / "publication.json", state)
            d.save(marker, {"schema_version": 2, "policy": d.POLICY, "batch_id": state["batch_id"], "state": "unknown",
                            "candidate_commit": candidate, "error": str(exc), "at": d.utc_now()})
            raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    for action in ("reserve", "prepare"):
        p = sub.add_parser(action); p.add_argument("--spec", type=Path, required=True)
    p = sub.add_parser("resume-prepare")
    p.add_argument("--batch", type=Path, required=True)
    p.add_argument("--approve-existing-stage", action="store_true")
    p = sub.add_parser("begin-relay")
    p.add_argument("--batch", type=Path, required=True)
    p = sub.add_parser("publish")
    p.add_argument("--batch", type=Path, required=True)
    p.add_argument("--restore-only", action="store_true")
    p = sub.add_parser("restore")
    p.add_argument("--git-dir", type=Path, required=True); p.add_argument("--commit", required=True); p.add_argument("--output", type=Path, required=True)
    scope = p.add_mutually_exclusive_group(required=True)
    scope.add_argument("--batch-id")
    scope.add_argument("--all-prepared-assets", action="store_true")
    args = parser.parse_args()
    try:
        if args.action in ("reserve", "prepare"):
            result = (reserve if args.action == "reserve" else prepare)(d.load(args.spec))
        elif args.action == "resume-prepare":
            result = resume_prepare(args.batch, approve_existing_stage=args.approve_existing_stage)
        elif args.action == "begin-relay":
            result = begin_relay(args.batch)
        elif args.action == "publish":
            result = publish(args.batch, restore_only=args.restore_only)
        else:
            result = restore_release(args.git_dir, args.commit, args.output, batch_id=args.batch_id)
        print(json.dumps(result, ensure_ascii=False, indent=2)); return 0
    except (OSError, ValueError, KeyError, TypeError, sqlite3.DatabaseError) as exc:
        print(json.dumps({"status": "needs_codex", "error": str(exc)}, ensure_ascii=False), file=sys.stderr); return 1


if __name__ == "__main__":
    raise SystemExit(main())
