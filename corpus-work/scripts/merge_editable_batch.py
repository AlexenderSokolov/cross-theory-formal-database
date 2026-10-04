"""Merge explicitly reviewed editable packets into a fresh batch directory.

SPEC names base/incoming package, manifest_sha256, build_root and receipt_root,
plus fixed master_helpers and compile_launcher paths. ROOT review must externally bind the
original manifests, complete package/build/receipt filemaps, programme/helper
hashes and semantic/source basis. This CLI never creates a material approval,
compiles mathematics, publishes, or increments a remote delivery count.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import merge_editable_packages as core
from corpus_delivery_tools import check_report, normalize_recovery, load as strict_load

HELPERS = ("schema.sql", "rebuild_database.py", "test_database.py",
           "restore_database.py", "test_restore_database.py")


def load(path):
    return strict_load(path)


def pin(value):
    if not isinstance(value, str) or len(value) != 64 or any(x not in "0123456789abcdef" for x in value):
        raise ValueError("SHA256 must be exactly 64 lowercase hex characters")
    return value


def filemap(root):
    return {p.relative_to(root).as_posix(): core.sha(p)
            for p in sorted(root.rglob("*")) if p.is_file()}


def programme_paths():
    scripts = Path(__file__).resolve().parent
    return {name: scripts / name for name in (
        "merge_editable_packages.py", "merge_editable_batch.py",
        "corpus_delivery_tools.py", "validate_corpus.py",
        "editable_delivery.py", "compile_editable_delivery.py")}


def preflight(spec, review, output):
    """Pure input inspection: no admission and no filesystem writes."""
    output = Path(output).absolute()
    if output.exists() or output.is_symlink():
        raise ValueError("output must be new; existing outputs are preserved")
    incoming = spec.get("incoming")
    if not isinstance(incoming, list) or not incoming:
        raise ValueError("explicit nonempty incoming package list required")
    inputs = [spec["base"], *incoming]
    master = Path(spec["master_helpers"]).resolve()
    for entry in inputs:
        for field in ("package", "build_root", "receipt_root"):
            root = Path(entry[field]).resolve()
            if not root.is_dir() or output.resolve().is_relative_to(root):
                raise ValueError("output cannot be inside immutable input roots")
        pin(entry["manifest_sha256"])
    if output.resolve().is_relative_to(master):
        raise ValueError("output cannot be inside fixed master helper root")
    if (review.get("schema_version") != 1 or review.get("status") != "material_review_complete"
            or review.get("holds") != [] or review.get("duplicates") != []
            or not isinstance(review.get("basis"), str) or not review["basis"].strip()
            or not isinstance(review.get("compile_reuse_basis"), str) or not review["compile_reuse_basis"].strip()):
        raise ValueError("explicit complete external semantic/source and compile-reuse review required")
    if (review.get("base_manifest_sha256") != inputs[0]["manifest_sha256"]
            or review.get("incoming_manifest_sha256") != [e["manifest_sha256"] for e in incoming]):
        raise ValueError("review does not bind original base and ordered incoming manifests")
    programs = programme_paths()
    programs['compile_launcher'] = Path(spec['compile_launcher']).resolve()
    if set(review.get("programme_sha256", {})) != set(programs):
        raise ValueError("complete programme identity pins required")
    for name, path in programs.items():
        if core.sha(path) != pin(review["programme_sha256"][name]):
            raise ValueError("programme identity mismatch: " + name)
    hp = review.get("master_helper_sha256", {})
    if set(hp) != set(HELPERS):
        raise ValueError("fixed master recovery helper pins required")
    for name in HELPERS:
        if core.sha(master / name) != pin(hp[name]):
            raise ValueError("fixed master helper identity mismatch: " + name)
    maps = review.get("reviewed_filemaps", {})
    artifact_maps = review.get("reviewed_artifact_filemaps", {})
    if len(maps.get("incoming", [])) != len(incoming) or len(artifact_maps.get("incoming", [])) != len(incoming):
        raise ValueError("complete incoming filemaps required")
    package_maps = [maps.get("base"), *maps.get("incoming", [])]
    artifacts = [artifact_maps.get("base"), *artifact_maps.get("incoming", [])]
    packages = []
    for entry, mapping, artifact in zip(inputs, package_maps, artifacts):
        root = Path(entry["package"]).resolve()
        if core.sha(root / "manifest.json") != entry["manifest_sha256"]:
            raise ValueError("pinned manifest identity mismatch")
        package = core.load_package(root)
        core.verify_filemap(root, mapping)
        if not isinstance(artifact, dict):
            raise ValueError("complete build/receipt filemap required")
        core.verify_filemap(Path(entry["build_root"]).resolve(), artifact.get("build"))
        core.verify_filemap(Path(entry["receipt_root"]).resolve(), artifact.get("receipts"))
        if core.sha(root / "schema.sql") != hp["schema.sql"]:
            raise ValueError("schema differs; no automatic migration")
        core.index_rows(root, {row["problem_id"] for row in package[0]["items"]})
        packages.append(package)
    core.validate_union(packages)
    ids = [r["problem_id"] for m, _ in packages[1:] for r in m["items"]]
    if sorted(review.get("incoming_ids", [])) != sorted(ids):
        raise ValueError("review incoming IDs do not match all incoming packages")
    # No late cross-file surprise: helpers alone may be replaced by pinned master.
    seen = {}
    for mapping in package_maps:
        for name, digest in mapping.items():
            if name.split("/")[0] == "database-parts" or name in core.GLOBAL_FILES or name in HELPERS or name == "merge-preparation.json":
                continue
            if name in seen and seen[name] != digest:
                raise ValueError("conflicting reviewed package file: " + name)
            seen[name] = digest
    return inputs, packages, master


def gate(package, build, receipts, report):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    rr = subprocess.run(
        [sys.executable, "-B", str(programme_paths()["validate_corpus.py"]),
         "--mode", "editable-delivery", "--package", str(package),
         "--evidence", str(package / "delivery-evidence.json"),
         "--build-root", str(build), "--receipt-root", str(receipts),
         "--report", str(report)],
        env=env, capture_output=True, text=True)
    report.with_suffix(".stdout").write_text(rr.stdout, encoding="utf8")
    report.with_suffix(".stderr").write_text(rr.stderr, encoding="utf8")
    if rr.returncode:
        raise ValueError("actual editable-delivery gate failed: " + str(report))
    return check_report(report, len(load(package / "manifest.json")["items"]))


def merge_batch(spec_path, review_path, review_sha256, output):
    sys.dont_write_bytecode = True
    spec, review = load(spec_path), load(review_path)
    if core.sha(Path(review_path)) != pin(review_sha256):
        raise ValueError("external root review hash mismatch")
    inputs, packages, master = preflight(spec, review, output)
    output = Path(output).absolute()
    output.mkdir(parents=True)
    for directory in ("normalized", "steps", "reviews", "reports", "build", "receipts"):
        (output / directory).mkdir()
    records = []
    normalized = []
    for n, entry in enumerate(inputs):
        raw = Path(entry["package"]).resolve()
        changed = any(not (raw / name).is_file() or core.sha(raw / name) != review["master_helper_sha256"][name] for name in HELPERS)
        current = raw
        if changed:
            current = output / "normalized" / str(n)
            record = normalize_recovery(raw, master, current,
                        review["master_helper_sha256"]["rebuild_database.py"],
                        review["master_helper_sha256"]["schema.sql"])
            # Fixed master restore adapter is a neutral recovery file, never an author asset.
            for name in HELPERS:
                if not (current / name).is_file() or core.sha(current / name) != review["master_helper_sha256"][name]:
                    shutil.copy2(master / name, current / name)
            if core.sha(current / "manifest.json") != entry["manifest_sha256"]:
                raise ValueError("normalization changed an admitted manifest")
            records.append({"input": n, "normalization": record,
                            "fixed_helper_sha256": review["master_helper_sha256"]})
        normalized.append(current)
        # Incoming closure is small; the base is checked by the actual final aggregate.
        if n:
            actual = gate(current, Path(entry["build_root"]).resolve(),
                          Path(entry["receipt_root"]).resolve(),
                          output / "reports" / ("incoming-" + str(n) + ".json"))
            records.append({"input": n, "actual_incoming_gate": actual})
    current = normalized[0]
    for n, incoming in enumerate(normalized[1:], 1):
        derived = dict(status=review["status"], holds=review["holds"], duplicates=review["duplicates"],
            incoming_ids=[r["problem_id"] for r in load(incoming / "manifest.json")["items"]],
            base_manifest_sha256=core.sha(current / "manifest.json"),
            incoming_manifest_sha256=core.sha(incoming / "manifest.json"),
            reviewed_filemaps={"base": filemap(current), "incoming": filemap(incoming)},
            basis=review["basis"], external_root_review_sha256=review_sha256,
            original_base_manifest_sha256=review["base_manifest_sha256"],
            original_incoming_manifest_sha256=review["incoming_manifest_sha256"],
            derivation="Only byte-preserved admitted items plus explicitly pinned fixed recovery helpers; no new semantic/source admission.")
        rp = output / "reviews" / ("step-" + str(n) + ".json")
        core.dump(rp, derived)
        new = output / "steps" / ("step-" + str(n))
        receipt = core.merge_packets(current, incoming, new, master / "rebuild_database.py",
                                     derived["base_manifest_sha256"], derived["incoming_manifest_sha256"], rp)
        records.append({"step": n, "base": str(current), "incoming": str(incoming),
                        "output": str(new), "preparation": receipt,
                        "derived_review_sha256": core.sha(rp)})
        current = new
    # Reuse actual immutable compile files without claiming a new compile.
    for entry, (manifest, _) in zip(inputs, packages):
        for row in manifest["items"]:
            ident = row["problem_id"]
            source = Path(entry["build_root"]).resolve() / ident
            receipt = Path(entry["receipt_root"]).resolve() / (ident + ".json")
            if not source.is_dir():
                raise ValueError("current compile helper per-ID build root missing")
            shutil.copytree(source, output / "build" / ident, copy_function=reuse_immutable)
            reuse_immutable(receipt, output / "receipts" / (ident + ".json"))
    aggregate = gate(current, output / "build", output / "receipts",
                     output / "reports" / "aggregate.json")
    # Recheck all immutable review-bound originals and programs after preparation.
    preflight(spec, review, output / "nonexistent-preflight-marker")
    result = {"status": "actual_editable_batch_gate_passed_not_remote",
              "package": str(current), "build_root": str(output / "build"),
              "receipt_root": str(output / "receipts"), "actual_aggregate": aggregate,
              "manifest_sha256": core.sha(current / "manifest.json"),
              "SQLite_sha256": core.sha(current / "corpus.sqlite"),
              "root_semantic_review_sha256": review_sha256, "steps": records,
              "fixed_master_helper_sha256": review["master_helper_sha256"],
              "programme_sha256": review["programme_sha256"],
              "actual_compile_reuse_basis_from_external_root": review["compile_reuse_basis"],
              "fresh_compilation_performed": False, "remote_delivered_increment": 0,
              "compile_reuse_roots_immutable": True,
              "reuse_rule": "Same-filesystem immutable artifacts are hardlinked; cross-filesystem copies use copy2. Never chmod/edit these shared artifacts or use these build/receipt roots for recompilation. Changed inputs require fresh output roots.",
              "not_independent_mathematical_certification": True}
    core.dump(output / "batch-result.json", result)
    return result


def reuse_immutable(source, target):
    """Reuse only immutable compile artifacts; never chmod or recompile here."""
    source, target = Path(source), Path(target)
    if source.stat().st_dev == target.parent.stat().st_dev:
        os.link(source, target)
        return target
    return shutil.copy2(source, target)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("spec", "semantic-review", "output"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--semantic-review-sha256", required=True)
    a = parser.parse_args()
    print(json.dumps(merge_batch(a.spec, a.semantic_review, a.semantic_review_sha256, a.output),
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()