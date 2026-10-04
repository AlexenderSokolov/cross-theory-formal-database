"""Prepare reviewed editable data and real validation artifacts for offline release.

OUTPUT/package is the public candidate; OUTPUT/work is private transport scratch.
No source admission, compilation, Git mutation or remote delivery count occurs.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import shutil
import sqlite3
import stat
import sys
import zipfile

import corpus_delivery_tools as delivery
import merge_editable_packages as merge

CHUNK_BYTES = 4 * 1024 * 1024
HELPERS = ("schema.sql", "rebuild_database.py", "restore_database.py",
           "test_database.py", "test_restore_database.py", "restore_validation_artifacts.py")
ARTIFACT_SUFFIXES = {".pdf", ".log", ".fls", ".aux", ".out"}
TRANSPORT_NAMES = {"corpus.sqlite", "corpus.sqlite.gz", "database-delivery.json",
                   "validation-artifact-delivery.json", "merge-preparation.json"}


def sha(path):
    return delivery.sha(path)


def dump(path, value):
    delivery.dump(path, value)


def digest(value):
    return delivery.pin(value)


def load_pinned(path, expected):
    path = delivery.ordinary(path)
    if sha(path) != digest(expected):
        raise ValueError("external input pin mismatch: " + str(path))
    return delivery.load(path)


def public_path(value):
    path = delivery.relative(value)
    blocked = {".ssh", ".aws", ".azure", ".env", "auth.json", "credentials.json",
               "events.jsonl", "private-events", "private_events", "__pycache__"}
    if (set(path.parts) & blocked or path.suffix.lower() in {".html", ".htm", ".har", ".jsonl", ".pyc"}):
        raise ValueError("private/raw cache material cannot enter release: " + value)
    return path


def check_sql(package, manifest):
    """Read-only check of every problem/source column, not just body/count."""
    path = delivery.ordinary(package / "corpus.sqlite")
    rows = manifest["items"]
    ids = {row["problem_id"] for row in rows}
    if not rows or len(ids) != len(rows):
        raise ValueError("empty or duplicate manifest IDs")
    with sqlite3.connect(path.as_uri() + "?mode=ro", uri=True) as db:
        if db.execute("PRAGMA integrity_check").fetchone()[0] != "ok" or db.execute("PRAGMA foreign_key_check").fetchall():
            raise ValueError("SQLite integrity or foreign key failure")
        actual = {row[0]: row for row in db.execute("SELECT * FROM problems")}
        if len(actual) != len(rows) or set(actual) != ids:
            raise ValueError("SQLite problem ID/count mismatch")
        sources = {}
        for row in rows:
            text_path = delivery.ordinary(merge.local(package, row["item_path"]))
            text = text_path.read_text(encoding="utf8")
            if row["status"] != "verified_editable_tex" or sha(text_path) != row["tex_sha256"]:
                raise ValueError("unqualified or changed mathematical input")
            expected = (row["problem_id"], row["title"], row["difficulty_level"], row["difficulty_reason"],
                        row["source_id"], json.dumps({"primary": row["primary"], "contexts": row["contexts"]},
                        sort_keys=True, ensure_ascii=False), row["item_path"], text, row["tex_sha256"],
                        row["origin_class"], row["status"], row["compile_receipt"])
            if actual[row["problem_id"]] != expected:
                raise ValueError("SQLite full problem projection mismatch: " + row["problem_id"])
            source = tuple(row[key] for key in ("source_id", "author", "work", "source_url", "source_version",
                                               "retrieved_at", "license", "license_path"))
            if row["source_id"] in sources and sources[row["source_id"]] != source:
                raise ValueError("source metadata conflict")
            sources[row["source_id"]] = source
        if {row[0]: row for row in db.execute("SELECT * FROM sources")} != sources:
            raise ValueError("SQLite full source projection mismatch")
    return {"problem_count": len(rows), "source_count": len(sources), "integrity": "ok",
            "foreign_key_errors": [], "full_problem_and_source_projection": True, "sqlite_sha256": sha(path)}


def preflight(package, build, receipts, aggregate, aggregate_pin, public_list, public_pin, output, master):
    package, build, receipts, master = (Path(path).resolve() for path in (package, build, receipts, master))
    output = Path(output).absolute()
    if output.exists() or output.is_symlink():
        raise ValueError("output must be fresh; preserve existing output")
    for root in (package, build, receipts, master):
        if not root.is_dir() or output.resolve().is_relative_to(root):
            raise ValueError("output cannot be inside immutable input roots")
    review = load_pinned(public_list, public_pin)
    if review.get("schema_version") != 1 or review.get("status") != "public_filelist_review_complete":
        raise ValueError("explicit completed public filelist review required")
    manifest, evidence = merge.load_package(package)
    ids = {row["problem_id"] for row in manifest["items"]}
    if (review.get("package_manifest_sha256") != sha(package / "manifest.json") or
            review.get("aggregate_report_sha256") != aggregate_pin):
        raise ValueError("review does not bind manifest and actual aggregate report")
    actual_report = load_pinned(aggregate, aggregate_pin)
    report_check = delivery.check_report(aggregate, len(ids))
    if set(actual_report["items"]) != ids or actual_report.get("package_item_count") != len(ids):
        raise ValueError("aggregate is not the complete actual package report")
    merge.verify_filemap(package, review.get("reviewed_package_filemap"))
    merge.index_rows(package, ids)
    pins = review.get("master_helper_sha256", {})
    if set(pins) != set(HELPERS):
        raise ValueError("all fixed Repo helper pins required")
    for name in HELPERS:
        path = delivery.ordinary(master / name)
        if sha(path) != digest(pins[name]):
            raise ValueError("fixed Repo helper identity mismatch: " + name)
        if (package / name).exists() and sha(delivery.ordinary(package / name)) != pins[name]:
            raise ValueError("normalize recovery helpers before preparing release: " + name)
    sql = check_sql(package, manifest)
    entries = review.get("files")
    if not isinstance(entries, list) or not entries:
        raise ValueError("explicit public files required")
    roots = {"package": package, "build": build, "receipts": receipts, "master_helpers": master}
    public, artifacts, selected = {}, {}, {key: set() for key in roots}
    for row in entries:
        kind, name = row.get("root"), row.get("path")
        if kind not in roots:
            raise ValueError("unknown public file root")
        relative = public_path(name)
        path = delivery.ordinary(merge.local(roots[kind], name))
        if sha(path) != digest(row.get("sha256")):
            raise ValueError("reviewed public file changed: " + kind + ":" + name)
        if name in selected[kind]:
            raise ValueError("duplicate public input row")
        selected[kind].add(name)
        if kind in {"package", "master_helpers"}:
            if relative.parts[0] in {"database-parts", "validation-artifact-parts"} or name in TRANSPORT_NAMES:
                raise ValueError("old derived transport is not a public input")
            if kind == "master_helpers" and name not in HELPERS:
                raise ValueError("unknown master helper")
            if name in public:
                raise ValueError("duplicate public destination: " + name)
            public[name] = path
        else:
            if kind == "build" and (len(relative.parts) != 2 or relative.parts[0] not in ids or path.suffix not in ARTIFACT_SUFFIXES):
                raise ValueError("only explicitly reviewed per-ID real compile artifacts are accepted")
            if kind == "receipts" and (len(relative.parts) != 1 or name not in {ident + ".json" for ident in ids}):
                raise ValueError("only per-ID real receipts are accepted")
            destination = kind + "/" + name
            if destination in artifacts:
                raise ValueError("duplicate artifact destination")
            artifacts[destination] = path
    required = {"manifest.json", "INDEX.md", "delivery-evidence.json", *HELPERS}
    for item in manifest["items"]:
        ident = item["problem_id"]
        required.update([item["item_path"], item["license_path"], item["compile_receipt"],
                         "sources/" + ident + "/provenance.json"])
        required.update(asset["path"] for asset in item.get("asset_dependencies", []))
        for locator in [item["primary"], *item["contexts"]]:
            if locator.get("excerpt_path"):
                required.add(locator["excerpt_path"])
        witness = evidence["items"][ident]
        for source in witness["sources"]:
            if source.get("root") == "inline":
                content = source.get("inline_text")
                if not isinstance(content, str) or hashlib.sha256(content.encode("utf8")).hexdigest() != digest(source.get("sha256")):
                    raise ValueError("changed or unsupported inline source witness")
                continue  # These exact original bytes are already in required delivery-evidence.json.
            if source.get("root") != "package":
                raise ValueError("release requires self-contained package source witnesses")
            required.add(source["path"])
        for body in witness["bodies"]:
            for span in [body, *body.get("spans", [])]:
                for field in ("fidelity_receipt", "source_excerpt_path"):
                    if isinstance(span.get(field), str):
                        required.add(span[field])
        receipt_name = ident + ".json"
        if receipt_name not in selected["receipts"]:
            raise ValueError("missing reviewed actual receipt: " + ident)
        receipt = delivery.load(receipts / receipt_name)
        if (receipt.get("ok") is not True or receipt.get("passes") not in range(2, 5) or
                receipt.get("shell_escape") is not False or receipt.get("input_sha256") != item["tex_sha256"]):
            raise ValueError("unqualified actual compile receipt: " + ident)
        for field in ("pdf_path", "compiler_log_path"):
            if receipt[field] not in selected["build"]:
                raise ValueError("required receipt-bound artifact not reviewed: " + receipt[field])
            bound = artifacts["build/" + receipt[field]]
            if sha(bound) != receipt["pdf_sha256" if field == "pdf_path" else "compiler_log_sha256"]:
                raise ValueError("actual receipt-bound artifact mismatch")
        directory = merge.local(build, ident)
        actual_files = {ident + "/" + path.name for path in directory.iterdir()
                        if path.is_file() and path.suffix in ARTIFACT_SUFFIXES}
        if not actual_files <= selected["build"]:
            raise ValueError("explicit public list omits actual PDF/log/FLS/aux/out files: " + ident)
    if not required <= set(public):
        raise ValueError("public list omits required package files: " + ", ".join(sorted(required - set(public))))
    for name in HELPERS:
        if sha(public[name]) != pins[name]:
            raise ValueError("public recovery helper is not the pinned Repo helper")
    return package, build, receipts, master, manifest, review, public, artifacts, sql, report_check


def immutable_copy(source, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    if source.stat().st_dev == target.parent.stat().st_dev:
        os.link(source, target)
    else:
        shutil.copy2(source, target)


def split_parts(path, package, subdirectory, prefix):
    destination = package / subdirectory
    destination.mkdir()
    parts = []
    with path.open("rb") as stream:
        index = 0
        while data := stream.read(CHUNK_BYTES):
            part = destination / (prefix + f"{index:05d}")
            part.write_bytes(data)
            parts.append({"index": index, "path": part.relative_to(package).as_posix(),
                          "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
            index += 1
    return parts


def prepare(package, build, receipts, aggregate, aggregate_pin, public_list, public_pin, output):
    program_sha256 = sha(Path(__file__))
    master = Path(__file__).resolve().parent.parent.parent / "editable-corpus"
    data = preflight(package, build, receipts, aggregate, aggregate_pin, public_list, public_pin, output, master)
    package, build, receipts, master, manifest, review, public, artifacts, sql, report_check = data
    output = Path(output).absolute()
    output.mkdir(parents=True)
    candidate, work = output / "package", output / "work"
    candidate.mkdir(); work.mkdir()
    publication = {}
    for name, path in sorted(public.items()):
        immutable_copy(path, candidate / name)
        publication[name] = {"sha256": sha(path), "bytes": path.stat().st_size}
    compressed = work / "corpus.sqlite.gz"
    with compressed.open("wb") as target, gzip.GzipFile(filename="", fileobj=target, mode="wb", mtime=0) as zipped:
        with (package / "corpus.sqlite").open("rb") as source:
            shutil.copyfileobj(source, zipped)
    parts = split_parts(compressed, candidate, "database-parts", "corpus.sqlite.gz.part-")
    database = {"schema_version": 2, "format": "ordered gzip-compressed SQLite parts", "chunk_bytes": CHUNK_BYTES,
                "part_count": len(parts), "parts": parts, "gzip_sha256": sha(compressed),
                "sqlite_sha256": sql["sqlite_sha256"], "gzip_bytes": compressed.stat().st_size,
                "sqlite_bytes": (package / "corpus.sqlite").stat().st_size, "problem_count": len(manifest["items"]),
                "manifest_sha256": sha(candidate / "manifest.json"), "restore_command": "python3 restore_database.py"}
    dump(candidate / "database-delivery.json", database)
    archive = work / "validation-artifacts.zip"
    inventory = {}
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zipped:
        for name, path in sorted(artifacts.items()):
            content = path.read_bytes()
            expected = sha(path)
            if hashlib.sha256(content).hexdigest() != expected:
                raise ValueError("artifact changed during packaging")
            info = zipfile.ZipInfo(name)
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            zipped.writestr(info, content)
            inventory[name] = {"bytes": len(content), "sha256": expected}
        zipped.writestr("ARTIFACT_FILEMAP.json", json.dumps(inventory, ensure_ascii=False, indent=2) + "\n")
    artifact_parts = split_parts(archive, candidate, "validation-artifact-parts", "fresh-build.zip.part-")
    artifact_delivery = {"schema_version": 1, "format": "ordered zip parts with exact filemap",
                         "part_count": len(artifact_parts), "parts": artifact_parts,
                         "archive_sha256": sha(archive), "archive_bytes": archive.stat().st_size, "file_count": len(inventory),
                         "restore_command": "python3 restore_validation_artifacts.py --destination /absolute/new/external/artifacts",
                         "receipt_set_relative": "receipts", "build_root_relative": "build"}
    dump(candidate / "validation-artifact-delivery.json", artifact_delivery)
    generated = ["database-delivery.json", "validation-artifact-delivery.json", *[p["path"] for p in parts + artifact_parts]]
    for name in generated:
        path = candidate / name
        publication[name] = {"sha256": sha(path), "bytes": path.stat().st_size}
    # Recheck every signed original after preparation; source hashes/modes are never changed.
    preflight(package, build, receipts, aggregate, aggregate_pin, public_list, public_pin, output / "unused-preflight-marker", master)
    for name, original in public.items():
        if sha(candidate / name) != sha(original):
            raise ValueError("public output differs from reviewed original")
    if sha(package / "corpus.sqlite") != database["sqlite_sha256"]:
        raise ValueError("source SQLite changed during release preparation")
    if sha(Path(__file__)) != program_sha256:
        raise ValueError("prepare programme changed during execution; preserve partial output")
    public_record = {"schema_version": 1, "status": "prepared_public_filelist_not_remote_verified",
                     "package_relative": "package", "files": [{"path": name, **info} for name, info in sorted(publication.items())]}
    dump(output / "PUBLIC_FILELIST.json", public_record)
    result = {"status": "prepared_editable_release_not_restored_or_remote_verified", "package": str(candidate),
              "public_filelist": str(output / "PUBLIC_FILELIST.json"), "public_filelist_sha256": sha(output / "PUBLIC_FILELIST.json"),
              "input_public_review_sha256": public_pin, "input_aggregate": report_check,
              "manifest_sha256": sha(candidate / "manifest.json"), "items": len(manifest["items"]), "sql": sql,
              "database_part_count": len(parts), "artifact_part_count": len(artifact_parts), "artifact_files": len(inventory),
              "fixed_master_helper_sha256": review["master_helper_sha256"], "prepare_program_sha256": program_sha256,
              "fresh_compilation_performed": False, "remote_delivered_increment": 0,
              "immutable_inputs_and_outputs": "Never edit/chmod the hardlinked package files; changed inputs require new output roots.",
              "required_next_action": "Copy only PUBLIC_FILELIST entries to a fresh directory, actually restore SQL and artifacts, then run full editable-delivery; publisher separately verifies exact remote restoration.",
              "work_directory_private": str(work)}
    dump(output / "release-preparation.json", result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("package", "build-root", "receipt-root", "aggregate-report", "public-filelist", "output"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--aggregate-report-sha256", required=True)
    parser.add_argument("--public-filelist-sha256", required=True)
    args = parser.parse_args()
    print(json.dumps(prepare(args.package, args.build_root, args.receipt_root, args.aggregate_report,
                             args.aggregate_report_sha256, args.public_filelist, args.public_filelist_sha256,
                             args.output), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    sys.dont_write_bytecode = True
    main()
