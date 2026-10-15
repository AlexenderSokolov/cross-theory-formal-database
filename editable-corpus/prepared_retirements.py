"""Explicit retirement records for the existing prepared publication chain."""
from __future__ import annotations
import copy
import csv
from collections import Counter
from pathlib import Path
import contextlib
import sqlite3

import prepared_delivery as d

RECORD_TYPE = "explicit_material_retirement_v1"


def select(spec):
    rows = spec.get("retirements", [])
    d.require(isinstance(rows, list), "retirements must be an explicit list")
    if rows:
        d.require(not spec.get("job_paths") and not spec.get("qualification_paths"),
                  "retirements cannot mix jobs or qualifications")
    seen = set()
    for row in rows:
        d.require(isinstance(row, dict), "retirement must be an object")
        ident = row.get("problem_id")
        d.require(isinstance(ident, str) and ident.isdecimal() and ident not in seen,
                  "retirement needs a unique explicit problem ID")
        evidence = row.get("evidence")
        d.require(d.nonempty(row.get("reason")) and isinstance(evidence, (str, dict, list)) and bool(evidence),
                  "retirement reason/evidence missing")
        canonical = row.get("duplicate_of")
        d.require(canonical is None or isinstance(canonical, str) and canonical.isdecimal(),
                  "duplicate canonical ID invalid")
        seen.add(ident)
    return copy.deepcopy(rows)


def record(batch, rows, manifest):
    rows = select({"retirements": rows})
    d.require(d.ID.fullmatch(batch) and rows, "retirement batch identity/entries missing")
    by_id = {str(row["problem_id"]): row for row in manifest["items"]}
    ids = {row["problem_id"] for row in rows}
    d.require(ids <= set(by_id), "retirement targets unknown or pending problem IDs")
    for row in rows:
        canonical = row.get("duplicate_of")
        d.require(canonical is None or canonical in by_id and canonical not in ids,
                  "duplicate canonical must remain in the corpus")
    return {"schema_version": 1, "record_type": RECORD_TYPE, "batch_id": batch,
            "retirements": rows, "removed_items": [copy.deepcopy(by_id[row["problem_id"]]) for row in rows]}


def validate_record(value):
    d.require(value.get("schema_version") == 1 and value.get("record_type") == RECORD_TYPE,
              "unsupported retirement record")
    rows = select({"retirements": value.get("retirements")})
    d.require(rows and d.ID.fullmatch(str(value.get("batch_id", ""))), "retirement record identity missing")
    removed = value.get("removed_items", [])
    d.require(isinstance(removed, list) and [str(row["problem_id"]) for row in removed] ==
              [row["problem_id"] for row in rows], "retirement removed metadata differs from declared IDs")
    return value


def historical_manifest(manifest, records):
    """Make prior metadata available for qualification replay, without new certification."""
    result = copy.deepcopy(manifest)
    ids = {str(row["problem_id"]) for row in result["items"]}
    for value in records:
        validate_record(value)
        for row in value["removed_items"]:
            ident = str(row["problem_id"])
            d.require(ident not in ids, "retired ID is present in final manifest or repeated")
            result["items"].append(copy.deepcopy(row))
            ids.add(ident)
    result["verified_count"] = len(result["items"])
    return result


def project(manifest, value):
    validate_record(value)
    ids = {row["problem_id"] for row in value["retirements"]}
    present = {str(row["problem_id"]) for row in manifest["items"]}
    d.require(ids <= present, "retirement targets absent manifest IDs")
    for row in value["retirements"]:
        canonical = row.get("duplicate_of")
        d.require(canonical is None or canonical in present - ids,
                  "duplicate canonical must remain in corpus")
    manifest["items"] = [row for row in manifest["items"] if str(row["problem_id"]) not in ids]
    manifest["verified_count"] = len(manifest["items"])
    manifest["retired_problem_ids"] = sorted(set(map(str, manifest.get("retired_problem_ids", []))) | ids)
    return manifest


def apply(database, manifest, value):
    """Delete only declared problem rows and their now-unused sources in one transaction."""
    projected = project(copy.deepcopy(manifest), value)
    ids = [row["problem_id"] for row in value["retirements"]]
    with contextlib.closing(sqlite3.connect(database)) as db, db:
        db.execute("PRAGMA foreign_keys=ON")
        present = {str(row[0]) for row in db.execute("SELECT problem_id FROM problems")}
        d.require(set(ids) <= present, "retirement targets unknown or pending SQL IDs")
        d.require(present == {str(row["problem_id"]) for row in manifest["items"]},
                  "SQL and manifest IDs differ before retirement")
        placeholders = ",".join("?" for _ in ids)
        source_ids = [row[0] for row in db.execute(
            "SELECT DISTINCT source_id FROM problems WHERE problem_id IN (" + placeholders + ")", ids)]
        db.executemany("DELETE FROM problems WHERE problem_id=?", [(ident,) for ident in ids])
        db.executemany("DELETE FROM sources WHERE source_id=? AND NOT EXISTS "
                       "(SELECT 1 FROM problems WHERE problems.source_id=sources.source_id)",
                       [(ident,) for ident in source_ids])
        d.require(not db.execute("PRAGMA foreign_key_check").fetchall(), "retirement foreign-key errors")
        actual = {str(row[0]) for row in db.execute("SELECT problem_id FROM problems")}
        d.require(actual == {str(row["problem_id"]) for row in projected["items"]},
                  "SQL and manifest IDs differ after retirement")
    manifest.clear()
    manifest.update(projected)
    return {"batch_id": value["batch_id"], "retired_problem_ids": ids, "material_increment": -len(ids)}


def descriptor_entry(value, *, after_delta_count, after_qualification_count):
    validate_record(value)
    d.require(type(after_delta_count) is int and after_delta_count >= 0 and
              type(after_qualification_count) is int and after_qualification_count >= 0,
              "retirement replay frontier must contain nonnegative counts")
    return {"batch_id": value["batch_id"], "path": "retirements/" + value["batch_id"] + ".json",
            "problem_ids": [row["problem_id"] for row in value["retirements"]],
            "after_delta_count": after_delta_count, "after_qualification_count": after_qualification_count}


def check_entry(entry, value):
    d.require(entry == descriptor_entry(value, after_delta_count=entry.get("after_delta_count"),
                                       after_qualification_count=entry.get("after_qualification_count")),
              "retirement descriptor/record differs")


def validate_frontiers(descriptor):
    previous = (0, 0)
    limits = (len(descriptor.get("deltas", [])), len(descriptor.get("qualification_records", [])))
    for entry in descriptor.get("retirement_records", []):
        current = (entry.get("after_delta_count"), entry.get("after_qualification_count"))
        d.require(all(type(value) is int and low <= value <= high
                      for value, low, high in zip(current, previous, limits)),
                  "retirement replay frontiers must be monotonic and within descriptor prefixes")
        previous = current


ACTIVE_INDEX_FILES = ("INDEX.md", "catalog.json", "catalog.csv")


def write_active_indexes(corpus, manifest, previous_catalog=None):
    """Deterministic current-material projection; retain existing scoped review metadata."""
    corpus = Path(corpus)
    d.require(previous_catalog is None or isinstance(previous_catalog, dict) and
              previous_catalog.get("schema_version", 2) == 2 and isinstance(previous_catalog.get("items"), list),
              "previous catalog must be an existing items object with absent or supported schema version")
    previous = {key: copy.deepcopy(value) for key, value in (previous_catalog or {}).items() if key != "items"}
    old_rows = {str(row["problem_id"]): row for row in (previous_catalog or {}).get("items", [])}
    active = manifest["items"]
    ids = {str(row["problem_id"]) for row in active}
    d.require(len(ids) == len(active) and not ids & set(map(str, manifest.get("retired_problem_ids", []))),
              "active indexes require unique non-retired manifest IDs")
    ordered = sorted(active, key=lambda row: str(row["problem_id"]))
    rows = []
    fields = ("title", "author", "work", "source_id", "source_url", "source_version", "item_path",
              "compile_receipt", "license", "license_path", "status", "claim_key",
              "review_state", "dedup_state", "review_protocol", "qualification_set_id")
    # Older generated catalogs may already contain these manifest payloads.
    # Keep full material/locator/reason records in manifest, not in every directory row.
    material_fields = {"tex_content", "tex_body", "source_files", "contexts", "proof_spans", "statement_spans",
                       "asset_dependencies", "primary", "source_locator", "source_locator_json", "source_map",
                       "statement", "proof", "source_text", "proof_text", "difficulty_reason", "published_difficulty_reason"}
    for number, source in enumerate(ordered, 1):
        ident = str(source["problem_id"])
        row = {key: copy.deepcopy(value) for key, value in old_rows.get(ident, {}).items() if key not in material_fields}
        row.update({key: copy.deepcopy(source[key]) for key in fields if key in source})
        row.update(problem_id=ident, display_index=number, H=source.get("difficulty_level"),
                   current_item_path=source.get("item_path"),
                   version=source.get("source_version", ""))
        row.setdefault("published_title", source.get("title", ""))
        row.setdefault("published_H", source.get("difficulty_level"))
        row.setdefault("qualification_status", "not_reassessed")
        row.setdefault("confirmed_H", None)
        row.setdefault("collection_state", "retained_material")
        row.setdefault("difficulty_state", "not_reassessed")
        state = source.get("review_state")
        if state in ("current", "author_material_collection"):
            row.update(qualification_status=state, collection_state=state,
                       difficulty_state="recorded_current_difficulty" if state == "current" else "author_supplied_label",
                       current_difficulty_H=source.get("difficulty_level"))
        if (source.get("difficulty_state") == "screened_H2_H3" and
                d.nonempty(source.get("difficulty_assessed_by")) and source.get("difficulty_level") in ("H2", "H3") and
                d.nonempty(source.get("difficulty_reason"))):
            row.update(difficulty_state="screened_H2_H3", difficulty_assessed_by=source["difficulty_assessed_by"])
        rows.append(row)
    previous.update(schema_version=2, master_manifest="manifest.json", count=len(rows), items=rows,
                    published_difficulty_counts=dict(Counter(row.get("published_H") for row in rows)),
                    qualification_counts=dict(Counter(row["qualification_status"] for row in rows)),
                    current_confirmed_difficulty_counts=dict(Counter(row["confirmed_H"] for row in rows if row.get("confirmed_H"))))
    previous.setdefault("qualification_scope", "Current materials and recorded difficulty states; historical labels alone do not establish a current review.")
    corpus.mkdir(parents=True, exist_ok=True)
    d.save(corpus / "catalog.json", previous)
    columns = ("display_index", "problem_id", "title", "H", "qualification_status", "collection_state", "difficulty_state",
               "difficulty_assessed_by", "author", "source_id", "source_url", "source_version", "item_path", "current_item_path", "compile_receipt")
    with (corpus / "catalog.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    def cell(value):
        return str(value or "").replace("|", "\\|").replace("\n", " ").replace("\r", " ")
    lines = ["# 当前材料索引", "", f"当前材料：{len(rows)}。展示序号连续，稳定题号保持不变。", "",
             "| 序号 | 稳定题号 | 题名 | 难度标签 | 收集状态 | 难度状态 | 可编辑 TeX | 来源 |",
             "|---|---|---|---|---|---|---|---|"]
    for row in rows:
        item = row.get("item_path", "")
        url = row.get("source_url", "")
        values = [row["display_index"], row["problem_id"], row.get("title"), row.get("H"),
                  row["collection_state"], row["difficulty_state"],
                  f"[TeX]({item})" if item else "", f"[作者来源]({url})" if url else row.get("source_id", "")]
        lines.append("| " + " | ".join(cell(value) for value in values) + " |")
    (corpus / "INDEX.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return previous
