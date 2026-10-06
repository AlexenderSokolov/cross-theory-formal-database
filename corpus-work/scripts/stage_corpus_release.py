"""Stage the explicit release list; reuse unchanged files and replace changed inodes."""
from pathlib import Path
import argparse
import json
import os
import shlex
import shutil
import subprocess
import tempfile


def load(path):
    return json.loads(Path(path).read_text(encoding="utf8"))


def atomic_copy(source, destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=destination.parent, delete=False) as output:
        with source.open("rb") as stream:
            shutil.copyfileobj(stream, output)
        temporary = output.name
    os.replace(temporary, destination)


def recovery_command(preparation):
    roots = preparation.get("artifact_archive_roots")
    if not roots:
        return "python3 restore_validation_artifacts.py --destination /absolute/new/artifacts"
    argv = ["python3", "restore_validation_chain.py", "--chain", "validation-chain.json",
            "--expected-chain-sha256", preparation["validation_chain_sha256"]]
    for ident, relative in roots.items():
        argv.extend(["--archive-root", ident + "=" + relative])
    argv.extend(["--schema1-helper", "restore_validation_artifacts.py", "--expected-helper-sha256",
                 preparation["schema1_restore_helper_sha256"], "--output", "/absolute/new/artifacts"])
    return shlex.join(argv)


def _stage_files(batch, project=Path("/disks/sata1/yupeng/human-proof-corpus")):
    batch = Path(batch).resolve()
    info = load(batch / "batch.json")
    completed = batch / "publish/result.json"
    release = Path(load(completed).get("release_root", batch / "release")) if completed.is_file() else batch / "release"
    prep = load(release / "release-preparation.json")
    if prep["status"] != "prepared_editable_release_not_restored_or_remote_verified" or prep["items"] != info["expected_count"]:
        raise ValueError("prepared release required")
    repo = Path(project) / "repo"
    publication = load(release / "PUBLIC_FILELIST.json")
    old_path = prep.get("previous_public_filelist")
    old = {row["path"]: row for row in load(old_path)["files"]} if old_path else {}
    planned = []
    for row in publication["files"]:
        rel = Path(row["path"])
        if rel.is_absolute() or ".." in rel.parts or "\\" in row["path"] or rel.as_posix() != row["path"]:
            raise ValueError("invalid prepared public path")
        if row["path"] == "RECOVERY_CURRENT.md":
            raise ValueError("exclude inherited recovery instructions from prepared list")
        planned.append((row, rel))
    handoff = repo / "handoff/yupeng" / ("main" + str(info["expected_count"]))
    metadata = [(release / "PUBLIC_FILELIST.json", handoff / "PUBLIC_FILELIST.json"),
                (batch / "merge/batch-result.json", handoff / "batch-result.json"),
                (batch / "material-review.json", handoff / "material-review.json")]
    recovery = repo / "editable-corpus/RECOVERY_CURRENT.md"
    queue_name = "handoff/yupeng/PRODUCTION_QUEUE.json"
    allowed = {"editable-corpus/" + rel.as_posix() for row, rel in planned}
    allowed.update(destination.relative_to(repo).as_posix() for source, destination in metadata)
    allowed.update([recovery.relative_to(repo).as_posix(), queue_name])
    staged = set(subprocess.check_output(["git", "-C", str(repo), "diff", "--cached", "--name-only"], text=True).splitlines())
    if staged - allowed:
        raise ValueError("unrelated staged files preserved; publish requires explicit index scope: " + ", ".join(sorted(staged - allowed)))
    changed = set(subprocess.check_output(["git", "-C", str(repo), "diff", "--name-only", "HEAD", "--", "editable-corpus"], text=True).splitlines())
    paths, skipped = [], []
    for row, rel in planned:
        source = release / "package" / rel
        dest = repo / "editable-corpus" / rel
        git_path = "editable-corpus/" + rel.as_posix()
        if (rel.as_posix() in old and all(row[key] == old[rel.as_posix()][key] for key in ("sha256", "bytes"))
                and dest.is_file() and not dest.is_symlink() and git_path not in changed):
            skipped.append(rel.as_posix())
            continue
        atomic_copy(source, dest)
        paths.append(git_path)
    for source, dest in metadata:
        atomic_copy(source, dest)
        paths.append(dest.relative_to(repo).as_posix())
    text = f"""# {info['expected_count']}题主库恢复

正文、INDEX与全文SQLite的当前版本以本目录manifest及database-delivery.json为准。
历史文件保留；只恢复当前描述中列出的分段，不把旧备份再次计数。

```sh
python3 restore_database.py
{recovery_command(prep)}
```

然后执行corpus-work/scripts/validate_corpus.py --mode editable-delivery，传入实际package、delivery-evidence、恢复后的build和receipts及独立report。公开完整恢复成功后才更新交付数。当前组批复用未变题证编译及合并aggregate；公开恢复仍执行必要完整gate。
"""
    recovery.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=recovery.parent, delete=False, mode="w", encoding="utf8") as stream:
        stream.write(text)
        temporary = stream.name
    os.replace(temporary, recovery)
    paths.extend([recovery.relative_to(repo).as_posix(), queue_name])
    for index in range(0, len(paths), 200):
        subprocess.run(["git", "-C", str(repo), "add", "--", *paths[index:index + 200]], check=True)
    result = {"status": "explicit_prepared_files_staged_not_pushed", "count": info["expected_count"],
              "paths": paths, "unchanged_public_files_skipped": len(skipped)}
    (batch / "git-staging.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf8")
    print(json.dumps({"status": result["status"], "count": result["count"], "files": len(paths), "skipped": len(skipped)}))
    return result


def stage(batch, project=Path("/disks/sata1/yupeng/human-proof-corpus"), owner=None, generation=None,
          state_root=None, guard_held=False, publication_guard_token=None):
    if not owner or type(generation) is not int:
        raise ValueError("explicit staging owner/generation required")
    if guard_held and not publication_guard_token:
        raise ValueError("held publication guard token required")
    from corpus_control_protocol import require_owner, controller_guard, publication_guard, assert_publication_guard
    state = Path(state_root) if state_root else Path(project) / "operations/corpusctl"
    if guard_held:
        assert_publication_guard(state, publication_guard_token)
        require_owner(state, owner, generation)
        return _stage_files(batch, project)
    with publication_guard(state), controller_guard(state, owner, generation):
        return _stage_files(batch, project)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("batch")
    parser.add_argument("--project", type=Path, default=Path("/disks/sata1/yupeng/human-proof-corpus"))
    parser.add_argument("--owner", required=True)
    parser.add_argument("--generation", required=True, type=int)
    parser.add_argument("--state-root", type=Path)
    parser.add_argument("--guard-held", action="store_true")
    parser.add_argument("--publication-guard")
    args = parser.parse_args()
    stage(args.batch, args.project, args.owner, args.generation, args.state_root, args.guard_held, args.publication_guard)
