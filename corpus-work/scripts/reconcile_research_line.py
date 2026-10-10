#!/usr/bin/env python3
"""Reconcile an archived research snapshot; never mutate production or raw evidence.

Only the Python standard library is required. Snapshot decisions are retained;
external reviews confirm them or open a conflict, rather than silently replacing
newer decisions. Material availability is separate from mathematical validation.
"""
from __future__ import annotations

import argparse
import collections
import json
import re
from pathlib import Path


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def relative(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")


def source_document(pid: str) -> str:
    if pid.startswith("S047-AIF-"):
        return "S047/AIF-3607"
    if pid.startswith("S047-ASNSP_"):
        return "S047/ASNSP-2013-12-4-1001"
    return pid.split("-", 1)[0]


def item_inventory(items_dir: Path) -> dict[str, list[dict]]:
    found = collections.defaultdict(list)
    for path in sorted(items_dir.glob("*.tex")):
        text = path.read_text(encoding="utf-8-sig")
        header = dict(re.findall(r"^%+\s*([\w_]+):\s*(.*)$", text, re.M))
        pid = header.get("problem_id", "").split()[0] if header.get("problem_id") else None
        if pid:
            label = re.search(r"\\label\{([^}]+)\}", text)
            found[pid].append({"path": path, "source_file": header.get("source_file"),
                               "primary_label": label[1] if label else None})
    return dict(found)


def load_reviews(review_root: Path, repo_root: Path) -> dict[str, list[dict]]:
    """Stage order is explicit; older initial reviews remain in the archive only."""
    result = collections.defaultdict(list)
    for stage, field in (("recheck", "new_level"), ("finalreview", "independent_level")):
        for path in sorted((review_root / stage).glob("*.json")):
            review = read_json(path)
            pid = review.get("problem_id")
            if pid and review.get(field):
                result[pid].append({"stage": stage, "level": review[field],
                                    "evidence_path": relative(path, repo_root),
                                    "faithful": review.get("faithful")})
    return dict(result)


def reason_sort(path: Path) -> int:
    suffix = path.stem.removeprefix("reasons")
    return int(suffix) if suffix else 1


def build_records(snapshot: Path, review_root: Path, repo_root: Path) -> tuple[list[dict], dict]:
    inventory = item_inventory(snapshot / "items")
    reviews = load_reviews(review_root, repo_root)
    records = {}
    for path in sorted(snapshot.glob("reasons*.json"), key=reason_sort):
        data = read_json(path)
        items = data.get("items", {})
        # B1's historical counted list contains only rechecked IDs, not its batch.
        counted = set(items) if path.name == "reasons.json" else set(data.get("counted", []))
        held = set(data.get("held_h1") or [])
        dropped = set(data.get("dropped") or [])
        for pid, item in sorted(items.items()):
            if pid in records:
                raise ValueError(f"Duplicate problem_id across reason files: {pid}")
            level = item.get("difficulty_level")
            issues = []
            candidates = inventory.get(pid, [])
            candidates = sorted(candidates, key=lambda c: (
                c["path"].stem not in (pid, pid.replace(":", "_")), c["path"].name))
            chosen = candidates[0] if candidates else None
            if level not in ("H1", "H2", "H3", "ineligible"):
                issues.append("invalid_difficulty_level")
            if pid in counted and pid in dropped:
                issues.append("counted_and_dropped")
            if pid in counted and pid in held:
                issues.append("counted_and_held")
            if pid in counted and level not in ("H2", "H3"):
                issues.append("counted_level_not_h2_h3")
            if pid in counted and not chosen:
                issues.append("missing_item_file")
            if pid in counted and (not item.get("statement_locator") or not item.get("proof_locator")):
                issues.append("missing_locators")
            latest_review = reviews.get(pid, [])[-1] if reviews.get(pid) else None
            applied_final = item.get("final_review", {}).get("independent_level")
            if applied_final and applied_final != level:
                issues.append("embedded_final_review_conflicts_with_snapshot")
            if latest_review and latest_review["level"] != level:
                # An applied final decision can supersede an older recheck.
                superseded = latest_review["stage"] == "recheck" and applied_final == level
                if not superseded:
                    issues.append("external_review_conflicts_with_snapshot")
            if issues:
                selection = "pending"
            elif pid in held or level == "H1":
                selection = "held_h1"
            elif pid in dropped or level == "ineligible":
                selection = "excluded"
            elif pid in counted:
                selection = "counted"
            else:
                selection = "not_counted"
            source_file = chosen["source_file"] if chosen else None
            if not source_file:
                match = re.search(r"([\w-]+\.tex)", item.get("statement_locator", ""))
                source_file = match[1] if match else None
            history = {key: item[key] for key in ("level_before_recheck", "level_before_final_review") if key in item}
            records[pid] = {
                "problem_id": pid, "title": item.get("title", pid),
                "batch": data.get("batch"), "source_id": pid.split("-", 1)[0],
                "source_document": source_document(pid), "source_file": source_file,
                "source_snapshot_level": level, "difficulty_level": level,
                "previous_levels": history, "selection_status": selection,
                "snapshot_counted": pid in counted, "snapshot_held": pid in held,
                "snapshot_dropped": pid in dropped, "issues": issues,
                "item_path": relative(chosen["path"], repo_root) if chosen else None,
                "item_aliases": [relative(c["path"], repo_root) for c in candidates[1:]],
                "primary_label": chosen["primary_label"] if chosen else None,
                "statement_locator": item.get("statement_locator"),
                "proof_locator": item.get("proof_locator"),
                "difficulty_reason": item.get("difficulty_reason", ""),
                "source_record": {"path": relative(path, repo_root), "item_key": pid},
                "review_evidence": reviews.get(pid, []),
                "review_flags": (["final_review_reports_text_deviation_requires_recheck"]
                                 if latest_review and latest_review.get("faithful") is False else []),
                "applied_final_review_level": applied_final,
                "validation_scope": "metadata reconciliation and file presence; not mathematical or compilation certification",
            }
    return sorted(records.values(), key=lambda r: r["problem_id"]), inventory


def primary_overlaps(records: list[dict], manifest_path: Path, repo_root: Path) -> list[dict]:
    main_root = manifest_path.parent
    main_index = collections.defaultdict(list)
    for item in read_json(manifest_path)["items"]:
        primary = item.get("primary", {})
        source = str(item.get("source_id", ""))
        if "stacks" not in source.lower() and item.get("work") != "The Stacks Project":
            continue
        excerpt = primary.get("excerpt_path")
        if not excerpt:
            continue
        path = main_root / excerpt
        if not path.is_file():
            raise FileNotFoundError(f"Missing main primary excerpt: {path}")
        match = re.search(r"\\label\{([^}]+)\}", path.read_text(encoding="utf-8-sig"))
        if match:
            main_index[(Path(primary.get("source_file", "")).name, match[1])].append((item, path))
    result = []
    for row in records:
        if row["source_id"] != "S001" or not row["primary_label"]:
            continue
        key = (Path(row["source_file"] or "").name, row["primary_label"])
        for item, path in main_index.get(key, []):
            result.append({"research_id": row["problem_id"], "main_problem_id": str(item["problem_id"]),
                           "match_method": "source_file_and_primary_first_label",
                           "source_file": key[0], "primary_label": key[1],
                           "primary_excerpt_path": relative(path, repo_root),
                           "research_selection_status": row["selection_status"],
                           "research_level": row["difficulty_level"], "main_level": item.get("difficulty_level"),
                           "scope": "same source claim; no context-label or semantic matching"})
    return sorted(result, key=lambda r: (r["research_id"], r["main_problem_id"]))


def license_audit(registry_path: Path, records: list[dict], manifest_path: Path, repo_root: Path) -> dict:
    registry = read_json(registry_path)
    main = read_json(manifest_path)["items"]
    stacks = [x for x in main if str(x.get("source_id", "")).startswith("stacks-project:")]
    notices = sorted({relative(manifest_path.parent / x["license_path"], repo_root)
                      for x in stacks if x.get("license_path") and (manifest_path.parent / x["license_path"]).is_file()})
    rows = []
    for source in registry["sources"]:
        sid = source["source_id"]
        explicit = {k: v for k, v in source.items() if any(t in k.lower() for t in ("license", "right", "permission", "copyright"))}
        entry = {"source_id": sid, "name": source.get("name"), "entry_url": source.get("entry_url"),
                 "research_record_count": sum(r["source_id"] == sid for r in records),
                 "counted_record_count": sum(r["source_id"] == sid and r["selection_status"] == "counted" for r in records),
                 "registry_license_metadata": explicit,
                 "rights_status": "not_established_by_registry", "existing_corpus_evidence": []}
        if sid == "S001" and notices:
            entry["rights_status"] = "existing_corpus_family_notice_available"
            entry["existing_corpus_evidence"] = [{"license": name, "notice_paths": notices,
                                                   "manifest_path": relative(manifest_path, repo_root)}
                                                  for name in sorted({x.get("license") for x in stacks if x.get("license")})]
        rows.append(entry)
    return {"registry_path": relative(registry_path, repo_root), "source_count": len(rows),
            "scope": "all source-registry entries; metadata audit only, no new redistribution clearance",
            "registry_rights_rule": registry.get("rights_rule"),
            "status_counts": dict(collections.Counter(r["rights_status"] for r in rows)), "sources": rows}


def reconcile(repo_root: Path, snapshot: Path, review_root: Path, registry: Path,
              manifest: Path, output: Path) -> dict:
    records, inventory = build_records(snapshot, review_root, repo_root)
    overlaps = primary_overlaps(records, manifest, repo_root)
    counted = [r for r in records if r["selection_status"] == "counted"]
    pending = [r for r in records if r["selection_status"] == "pending"]
    overlap_ids = {r["research_id"] for r in overlaps if r["research_selection_status"] == "counted"}
    source_index = read_jsonl(snapshot / "index.jsonl")
    source_ids = [r["problem_id"] for r in source_index]
    source_by_id = {r["problem_id"]: r for r in source_index}
    index_discrepancies = []
    for row in records:
        old = source_by_id.get(row["problem_id"])
        if bool(old) != row["snapshot_counted"] or (old and old.get("difficulty_level") != row["difficulty_level"]):
            index_discrepancies.append(row["problem_id"])
    index_discrepancies.extend(sorted(set(source_ids) - {r["problem_id"] for r in records}))
    summary = {
        "schema_version": 1, "snapshot_path": relative(snapshot, repo_root),
        "main_manifest_path": relative(manifest, repo_root),
        "scope": "research line only; never added to the production manifest",
        "decision_precedence": ["latest archived reasons snapshot preserves applied decisions and former levels",
                                "applied final_review supersedes an older recheck",
                                "external finalreview, then recheck, are comparison evidence; unresolved disagreement remains pending",
                                "missing files or contradictory counted/held/dropped status block the counted view regardless of label"],
        "source_index": {"rows": len(source_index), "unique_ids": len(set(source_ids)),
                         "levels": dict(collections.Counter(r.get("difficulty_level") for r in source_index)),
                         "duplicate_ids": [k for k, v in collections.Counter(source_ids).items() if v > 1],
                         "discrepancies_with_reasons": sorted(set(index_discrepancies))},
        "reason_record_count": len(records),
        "selection_counts": dict(collections.Counter(r["selection_status"] for r in records)),
        "counted_levels": dict(collections.Counter(r["difficulty_level"] for r in counted)),
        "counted_sources": dict(collections.Counter(r["source_document"] for r in counted)),
        "item_files": sum(len(v) for v in inventory.values()), "item_unique_ids": len(inventory),
        "unreferenced_item_ids": sorted(set(inventory) - {r["problem_id"] for r in records}),
        "pending_ids": [r["problem_id"] for r in pending],
        "review_flagged_ids": [r["problem_id"] for r in records if r["review_flags"]],
        "main_overlap": {"mapping_rows": len(overlaps), "counted_research_ids": len(overlap_ids),
                         "unmatched_counted_records": len(counted) - len(overlap_ids),
                         "unmatched_is_not_proven_novel": True},
        "validation_limits": ["file presence does not certify faithful text, mathematical eligibility, context sufficiency, or compilation",
                              "same-primary-label matching gives a content-overlap lower bound, not exhaustive semantic deduplication",
                              "existing family license notices do not clear every newly collected document for redistribution"],
    }
    audit = license_audit(registry, records, manifest, repo_root)
    output.mkdir(parents=True, exist_ok=True)
    for name, rows in (("records.jsonl", records), ("index.jsonl", counted),
                       ("holds.jsonl", [r for r in records if r["selection_status"] == "held_h1"]),
                       ("pending.jsonl", pending), ("main-overlap.jsonl", overlaps)):
        write_jsonl(output / name, rows)
    write_json(output / "summary.json", summary)
    write_json(output / "source-license-audit.json", audit)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--snapshot", default="research-line/archive/2026-10-10/initial_corpus")
    parser.add_argument("--reviews", default="research-line/archive/2026-10-10/controller-reviews")
    parser.add_argument("--registry", default="research-line/archive/2026-10-10/source_registry.json")
    parser.add_argument("--main-manifest", default="editable-corpus/manifest.json")
    parser.add_argument("--output", default="research-line")
    args = parser.parse_args()
    root = args.repo_root.resolve()
    summary = reconcile(root, root / args.snapshot, root / args.reviews,
                        root / args.registry, root / args.main_manifest, root / args.output)
    print(json.dumps({key: summary[key] for key in ("selection_counts", "counted_levels", "main_overlap")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
