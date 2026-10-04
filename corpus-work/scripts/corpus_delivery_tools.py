"""Deterministic delivery mechanics; no mathematical or rights admission."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import shutil
import stat
import subprocess
import sys
import zipfile
from pathlib import Path, PurePosixPath


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load(path):
    def unique_pairs(pairs):
        value = {}
        for key, item in pairs:
            if key in value:
                raise ValueError("duplicate JSON key: " + key)
            value[key] = item
        return value
    return json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=unique_pairs)


def dump(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def pin(value):
    if len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
        raise ValueError("SHA256 must be exactly 64 lowercase hex characters")
    return value


def relative(value):
    p = PurePosixPath(value)
    if not value or not p.parts or p.is_absolute() or ".." in p.parts or "\\" in value or p.as_posix() != value:
        raise ValueError("unsafe or non-canonical relative path: " + value)
    return p


def local(root, value):
    p = Path(root).joinpath(*relative(value).parts)
    if p.is_symlink() or not p.resolve().is_relative_to(Path(root).resolve()):
        raise ValueError("symlink or escaping input: " + str(p))
    return p


def ordinary(path):
    p = Path(path)
    if p.is_symlink() or not p.is_file() or p.stat().st_mode & 0o7000:
        raise ValueError("input must be an ordinary file without special permission bits: " + str(p))
    return p


def check_report(path, expected):
    j = load(path)
    errors = list(j.get("errors", []))
    items = j.get("items", {})
    if expected < 1 or len(items) != expected or j.get("package_item_count", 0) < expected:
        errors.append("incomplete or empty selected-item report")
    for ident, item in items.items():
        errors.extend(f"{ident}: {e}" for e in item.get("errors", []))
        if item.get("status") != "qualified_editable":
            errors.append(f"{ident}: item is not qualified_editable")
    if j.get("mode") != "editable-delivery" or j.get("editable_qualified_count") != expected:
        errors.append("wrong mode or qualified count")
    if errors:
        raise ValueError("; ".join(errors))
    return {"report": str(Path(path).resolve()), "sha256": sha(path), "actual_qualified_count": expected}


def normalize_recovery(package, master, output, helper_pin, schema_pin):
    """Preserve inputs; normalize only project recovery code and rebuild full SQL."""
    package, master = (Path(p).resolve() for p in (package, master))
    output = Path(output).absolute()
    if output.exists() or output.is_symlink() or output.resolve().is_relative_to(package) or output.resolve().is_relative_to(master):
        raise ValueError("output must be a fresh directory outside immutable inputs")
    if sha(master / "rebuild_database.py") != pin(helper_pin):
        raise ValueError("fixed master helper identity mismatch")
    if sha(master / "schema.sql") != pin(schema_pin) or sha(package / "schema.sql") != schema_pin:
        raise ValueError("schema differs; do not silently migrate")
    for p in package.rglob("*"):
        if p.is_symlink():
            raise ValueError("symlink in package")
    manifest = load(package / "manifest.json")
    evidence = load(package / "delivery-evidence.json")
    if evidence.get("package_manifest_sha256") != sha(package / "manifest.json"):
        raise ValueError("evidence does not bind manifest")
    before = {x["problem_id"]: sha(local(package, x["item_path"])) for x in manifest["items"]}
    if len(before) != len(manifest["items"]):
        raise ValueError("duplicate ID")
    for row in manifest["items"]:
        if before[row["problem_id"]] != row["tex_sha256"]:
            raise ValueError("TeX identity mismatch")
    shutil.copytree(package, output, ignore=lambda directory, names: ["corpus.sqlite"] if Path(directory) == package else [])
    changes = []
    for name in ("rebuild_database.py", "restore_database.py", "test_database.py", "test_restore_database.py"):
        fixed = master / name
        if not fixed.exists():
            continue
        target = output / name
        if not target.exists() or sha(target) != sha(fixed):
            changes.append({"path": name, "old_sha256": sha(target) if target.exists() else None, "fixed_sha256": sha(fixed)})
            shutil.copy2(fixed, target)
    if (output / "corpus.sqlite.tmp").exists():
        raise ValueError("preexisting temporary database; preserve and investigate")
    spec = importlib.util.spec_from_file_location("fixed_rebuild", output / "rebuild_database.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    count = module.rebuild(output, output / "corpus.sqlite")
    after = {r["problem_id"]: sha(local(output, r["item_path"])) for r in manifest["items"]}
    if before != after or sha(output / "manifest.json") != sha(package / "manifest.json"):
        raise ValueError("unexpected mathematical input or manifest change")
    return {"status": "prepared_recovery_normalization_not_qualified", "package": str(output), "original": str(package),
            "manifest_sha256": sha(output / "manifest.json"), "sqlite_sha256": sha(output / "corpus.sqlite"),
            "items": count, "recovery_helper_changes": changes, "mathematical_inputs_unchanged": True,
            "required_next_action": "Run actual explicit editable-delivery gate with the matching build and receipts; no new compile is claimed."}


def pack_cas(spec_path, output):
    """Pack only an explicit, hash-reviewed publication file list."""
    spec = load(spec_path)
    if spec.get("status") != "public_filelist_review_complete" or not spec.get("files"):
        raise ValueError("explicit reviewed public file list required")
    output = Path(output).absolute()
    if output.exists() or output.is_symlink():
        raise ValueError("preserve existing output")
    entries, sources, paths = [], {}, set()
    for row in spec["files"]:
        name = relative(row["path"]).as_posix()
        if name in paths:
            raise ValueError("duplicate destination: " + name)
        paths.add(name)
        p = ordinary(row["source"])
        expected = pin(row["sha256"])
        if sha(p) != expected:
            raise ValueError("reviewed input changed: " + str(p))
        entries.append({"path": name, "sha256": expected, "bytes": p.stat().st_size,
                        "mode": stat.S_IMODE(p.stat().st_mode)})
        sources.setdefault(expected, p)
    output.mkdir(parents=True)
    archive = output / "materials.cas.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for digest, p in sorted(sources.items()):
            data = p.read_bytes()
            if hashlib.sha256(data).hexdigest() != digest:
                raise ValueError("input changed during pack")
            info = zipfile.ZipInfo("blobs/" + digest)
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, data)
    manifest = output / "materials.cas.manifest.json"
    record = {"schema_version": 1, "format": "sha256-content-addressed-zip", "archive_name": archive.name,
              "archive_sha256": sha(archive), "archive_bytes": archive.stat().st_size, "files": entries}
    dump(manifest, record)
    return {"status": "packed_not_restored_or_qualified", "manifest": str(manifest), "manifest_sha256": sha(manifest),
            "archive_sha256": sha(archive), "paths": len(entries), "unique_blobs": len(sources)}


def verify_cas(manifest, expected, restore_helper, restore_helper_pin, destination):
    """Use the existing strict restore adapter, then inspect every restored byte/mode."""
    manifest, destination = Path(manifest).resolve(), Path(destination).absolute()
    if sha(manifest) != pin(expected):
        raise ValueError("external manifest pin mismatch")
    if destination.exists() or destination.is_symlink():
        raise ValueError("destination must be fresh")
    if sha(ordinary(restore_helper)) != pin(restore_helper_pin):
        raise ValueError("trusted restore helper identity mismatch")
    subprocess.run([sys.executable, str(restore_helper), "--manifest", str(manifest),
                    "--expected-manifest-sha256", expected, "--destination", str(destination)], check=True)
    record = load(manifest)
    for row in record["files"]:
        p = local(destination, row["path"])
        if sha(p) != row["sha256"] or p.stat().st_size != row["bytes"] or stat.S_IMODE(p.stat().st_mode) != row["mode"]:
            raise ValueError("restored file mismatch: " + row["path"])
    return {"status": "actual_CAS_bytes_sizes_modes_verified_not_delivery_admission", "paths": len(record["files"]),
            "destination": str(destination), "required_next_action": "Run actual full SQLite projection and explicit editable-delivery gate on restored materials."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("check-report")
    p.add_argument("--report", type=Path, required=True)
    p.add_argument("--expected-count", type=int, required=True)
    p = sub.add_parser("normalize-recovery")
    for name in ("package", "master", "output"):
        p.add_argument("--" + name, type=Path, required=True)
    p.add_argument("--helper-sha256", required=True)
    p.add_argument("--schema-sha256", required=True)
    p = sub.add_parser("pack-cas")
    p.add_argument("--spec", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p = sub.add_parser("verify-cas")
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--expected-manifest-sha256", required=True)
    p.add_argument("--restore-helper", type=Path, required=True)
    p.add_argument("--restore-helper-sha256", required=True)
    p.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "check-report":
        result = check_report(args.report, args.expected_count)
    elif args.command == "normalize-recovery":
        result = normalize_recovery(args.package, args.master, args.output, args.helper_sha256, args.schema_sha256)
    elif args.command == "pack-cas":
        result = pack_cas(args.spec, args.output)
    else:
        result = verify_cas(args.manifest, args.expected_manifest_sha256, args.restore_helper, args.restore_helper_sha256, args.destination)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
