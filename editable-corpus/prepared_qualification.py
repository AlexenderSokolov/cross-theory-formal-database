"""Apply explicit existing-public qualification metadata to the same problems rows.

No author text, legacy fingerprints or source rows are updated or compared.
"""
import copy
import contextlib
from pathlib import PurePosixPath
import re
import sqlite3

import prepared_delivery as d

RECORD_TYPE = "applicable_public_qualification_reuse"
SCREENING_RECORD_TYPE = "whole_author_work_difficulty_screening"
QUAL_COLUMNS = ("task_id", "revision", "claim_key", "review_state", "dedup_state", "publication_commit", "qualification_set_id")
SCREENING_SQL_COLUMNS = tuple(key for key in QUAL_COLUMNS if key != "publication_commit") + ("difficulty_level", "difficulty_reason")
CHECKS = ("complete_counted_statement_and_original_proof", "necessary_local_core_retained",
          "source_license_supported", "focused_semantic_uniqueness_review")


def validate_record(record):
    if record.get("record_type") == SCREENING_RECORD_TYPE:
        return validate_screening_record(record)
    d.require(record.get("review_protocol") is None, "historical qualification cannot adopt focused protocol")
    d.require(record.get("schema_version") == 2 and record.get("record_type") == RECORD_TYPE and
              record.get("status") == "approved_metadata_projection_pending_public_delivery" and record.get("material_increment") == 0,
              "explicit approved existing-qualification metadata record required")
    d.require(d.ID.fullmatch(str(record.get("qualification_set_id", ""))) and d.nonempty(record.get("approved_by")) and
              re.fullmatch(r"[0-9a-f]{40}", str(record.get("basis_public_commit", ""))), "qualification set approval/identity missing")
    rows = record.get("qualifications")
    d.require(isinstance(rows, list) and rows, "qualification set cannot be empty")
    for field in ("problem_id", "task_id", "claim_key"):
        d.require(len({row[field] for row in rows}) == len(rows), "duplicate qualification " + field)
    for row in rows:
        d.require(row.get("review_protocol") is None, "historical qualification row cannot adopt focused protocol")
        for key in ("problem_id", "task_id", "source_id", "source_version", "claim_key", "applicability_basis"):
            d.require(d.nonempty(row.get(key)), "qualification metadata missing: " + key)
        d.require(d.REVISION.fullmatch(str(row.get("revision", ""))) and row.get("difficulty_level") in ("H2", "H3") and
                  row.get("review_state") == "current" and row.get("dedup_state") == "unique_within_reviewed_scope" and
                  re.fullmatch(r"[0-9a-f]{40}", str(row.get("publication_commit", ""))), "qualification revision/H/public state invalid")
        evidence = row.get("review_evidence", {})
        path = PurePosixPath(str(evidence.get("path", "")))
        d.require(not path.is_absolute() and ".." not in path.parts and path.parts[:2] == ("editable-corpus", "sources") and
                  re.fullmatch(r"[0-9a-f]{40}", str(evidence.get("commit", ""))), "qualification must reference a published source review")
        d.require(all(evidence.get(key) is True for key in ("proof_complete", "local_core_complete", "license_supported", "semantic_comparison_supported")),
                  "qualification applicability checks incomplete")
        primary = row.get("counted_primary", {})
        d.require(d.nonempty(primary.get("source_file")) and d.nonempty(primary.get("theorem")) and
                  type(primary.get("start_line")) is int and type(primary.get("end_line")) is int and
                  1 <= primary["start_line"] <= primary["end_line"], "qualification counted primary locator invalid")
    return record


def metadata(record):
    return d.locator_metadata(record)


def claim_label(value):
    return re.sub(r"[\s:_-]+", "-", str(value).strip()).casefold()


def validate_review(row, manifest_row, review):
    d.require(review.get("review_protocol") is None and manifest_row.get("review_protocol") is None, "historical qualification cannot reuse focused review")
    for key in ("problem_id", "source_id", "revision"):
        d.require(str(review.get(key)) == row[key], "published qualification review mismatch: " + key)
    d.require(review.get("confirmed_H") == row["difficulty_level"] == manifest_row["difficulty_level"], "qualification H mismatch")
    d.require(manifest_row["source_id"] == row["source_id"] and manifest_row["source_version"] == row["source_version"],
              "qualification source/version mismatch")
    d.require(review.get("decision") == "content_review_complete_pending_public_restore" and
              all(review.get("checks", {}).get(key) is True for key in CHECKS), "published substantive review is incomplete")
    primary = row["counted_primary"]
    actual_primary = manifest_row.get("primary", {})
    d.require(isinstance(actual_primary, dict) and all(actual_primary.get(key) == value for key, value in primary.items()),
              "qualification counted primary differs from manifest")
    counted = review.get("claim_key", review.get("counted_claim"))
    label, key = claim_label(counted), claim_label(row["claim_key"])
    d.require(bool(counted) and (key == label or key.endswith("-" + label)), "qualification claim differs from published review")
    statement = [primary["start_line"], primary["end_line"]]
    explicit = review.get("counted_statement_lines", review.get("counted_unit", {}).get("primary_source_lines"))
    if explicit is not None:
        d.require(explicit == statement, "qualification statement range differs from review")
    else:
        d.require(any(span[0] <= statement[0] <= statement[1] <= span[1] for span in review.get("original_source_spans_reviewed", [])),
                  "qualification counted statement not covered by actual review")
    evidence = row["review_evidence"]
    d.require(d.nonempty(review.get("difficulty_reason")) and review["difficulty_reason"] == evidence.get("difficulty_reason"),
              "qualification reason does not match actual published opinion")
    reviewers = review.get("reviewers", review.get("review_witnesses", []))
    d.require(reviewers and metadata(reviewers) == metadata(evidence.get("reviewers")), "qualification reviewer metadata mismatch")
    d.require(review.get("dedup") and review.get("license_witness"), "published semantic comparison/licence witness missing")
    if row["source_id"].startswith("arxiv:"):
        d.require(str(review["license_witness"].get("fixed_version_url", "")).rstrip("/").endswith("/" + row["source_id"].split(":", 1)[1]),
                  "published licence witness names another source version")
    if row["difficulty_level"] == "H3":
        witnesses = review.get("independent_h3_reviews", [])
        names, proofs = set(), []
        for witness in witnesses:
            d.require(d.nonempty(witness.get("reviewer")) and d.nonempty(witness.get("basis")) and
                      witness.get("verdict") == "H3" and claim_label(witness.get("counted_claim")) == claim_label(review.get("counted_claim")) and
                      witness.get("statement_lines") == statement and witness.get("proof_lines"), "H3 review must bind this claim and statement/proof")
            names.add(witness["reviewer"].strip().casefold()); proofs.append(witness["proof_lines"])
        d.require(len(names) >= 2 and all(proof == proofs[0] for proof in proofs) and
                  (not review.get("counted_proof_lines") or proofs[0] == review["counted_proof_lines"]) and
                  metadata(witnesses) == metadata(evidence.get("independent_h3_reviews")), "H3 needs two independent applicable reviews")


def reviewed_rows(manifest, record, read_review):
    validate_record(record)
    if record["record_type"] == SCREENING_RECORD_TYPE:
        return screened_rows(manifest, record)
    by_id = {row["problem_id"]: row for row in manifest["items"]}
    prepared = []
    for row in record["qualifications"]:
        d.require(row["problem_id"] in by_id, "qualification cannot add a material row")
        original = by_id[row["problem_id"]]
        d.require(original.get("policy", "legacy") == "legacy" and original.get("qualification_set_id") in (None, record["qualification_set_id"]),
                  "qualification targets a different policy/set")
        validate_review(row, original, read_review(row["review_evidence"]["path"]))
        prepared.append((row, original))
    return prepared


def project_rows(prepared, record):
    for row, original in prepared:
        original.update({key: copy.deepcopy(row[key] if key != "qualification_set_id" else record[key]) for key in QUAL_COLUMNS})
        original["qualification_basis"] = record["record_type"]
        if record["record_type"] == SCREENING_RECORD_TYPE:
            original.update(difficulty_level=row["difficulty_level"], difficulty_reason=row["difficulty_reason"],
                            difficulty_state="screened_H2_H3", difficulty_assessed_by=copy.deepcopy(row["assessed_by"]))


def apply(master, manifest, record, read_review):
    """Update qualification metadata only; repeated identical application is idempotent."""
    if record.get("record_type") == SCREENING_RECORD_TYPE:
        return apply_screening(master, manifest, record)
    prepared = reviewed_rows(manifest, record, read_review)
    with contextlib.closing(sqlite3.connect(master)) as db, db:
        info = {part[1] for part in db.execute("PRAGMA table_info(problems)")}
        if "qualification_set_id" not in info:
            db.execute("ALTER TABLE problems ADD COLUMN qualification_set_id TEXT")
        for row, original in prepared:
            actual = db.execute("SELECT p.source_id,s.source_version,p.difficulty_level,p.validation_policy,p.qualification_set_id FROM problems p JOIN sources s USING(source_id) WHERE p.problem_id=?", (row["problem_id"],)).fetchone()
            d.require(actual and actual[:4] == (row["source_id"], row["source_version"], row["difficulty_level"], "legacy") and
                      actual[4] in (None, record["qualification_set_id"]), "SQL legacy qualification source/H/version/policy mismatch")
            values = [row[key] if key != "qualification_set_id" else record[key] for key in QUAL_COLUMNS]
            db.execute("UPDATE problems SET " + ",".join(key + "=?" for key in QUAL_COLUMNS) + " WHERE problem_id=?", (*values, row["problem_id"]))
        d.require(not db.execute("SELECT claim_key FROM problems WHERE review_state='current' AND claim_key IS NOT NULL GROUP BY claim_key HAVING count(*)>1").fetchall(),
                  "qualification creates a duplicate current claim")
    project_rows(prepared, record)
    return {"qualification_set_id": record["qualification_set_id"], "updated_existing_problem_ids": [r["problem_id"] for r, _ in prepared], "material_increment": 0}


def validate_screening_record(record):
    """Screen author material for difficulty and usability, without certifying mathematics."""
    d.require(record.get("schema_version") == 2 and
              record.get("status") == "approved_metadata_projection_pending_public_delivery" and
              record.get("material_increment") == 0, "approved whole-author-work screening record required")
    d.require(d.ID.fullmatch(str(record.get("qualification_set_id", ""))) and d.nonempty(record.get("approved_by")) and
              re.fullmatch(r"[0-9a-f]{40}", str(record.get("basis_public_commit", ""))), "screening set approval/identity missing")
    rows = record.get("qualifications")
    d.require(isinstance(rows, list) and rows and all(isinstance(row, dict) for row in rows), "screening rows required")
    for key in ("problem_id", "claim_key"):
        d.require(all(d.nonempty(row.get(key)) for row in rows) and len({row[key] for row in rows}) == len(rows),
                  "missing or duplicate screening " + key)
    for row in rows:
        for key in ("source_id", "source_version", "difficulty_reason", "assessed_by"):
            d.require(d.nonempty(row.get(key)), "screening metadata missing: " + key)
        d.require("task_id" in row and (row["task_id"] is None or d.nonempty(row["task_id"])) and
                  "revision" in row and (row["revision"] is None or d.REVISION.fullmatch(str(row["revision"]))) and
                  row.get("difficulty_level") in ("H2", "H3") and
                  row.get("review_state") == "current" and row.get("dedup_state") == "unique_within_reviewed_scope" and
                  "publication_commit" in row and (row["publication_commit"] is None or
                  re.fullmatch(r"[0-9a-f]{40}", str(row["publication_commit"]))), "screening revision/H/public state invalid")
        primary = row.get("counted_primary", {})
        d.require(isinstance(primary, (dict, list)) and bool(primary) and
                  (not isinstance(primary, list) or all(isinstance(span, dict) and span for span in primary)),
                  "screening counted primary invalid")
        material, reuse, dedup = (row.get(key, {}) for key in ("author_material", "material_reuse", "semantic_dedup"))
        d.require(material.get("complete") is True and d.nonempty(material.get("basis")), "complete author material basis missing")
        d.require(reuse.get("confirmed") is True and all(d.nonempty(reuse.get(key)) for key in ("compile_receipt", "pdf", "basis")) and
                  type(reuse.get("pages_viewed")) is int and reuse["pages_viewed"] > 0, "existing compile/actual page reuse basis missing")
        compared = dedup.get("compared_problem_ids")
        d.require(d.nonempty(dedup.get("scope")) and isinstance(compared, list) and compared and
                  all(d.nonempty(value) for value in compared) and len(set(compared)) == len(compared) and
                  row["problem_id"] not in compared and dedup.get("decision") == "unique_within_reviewed_scope" and
                  d.nonempty(dedup.get("reason")), "finite semantic comparison scope/IDs/decision missing")
    return record


def screened_rows(manifest, record):
    by_id = {row["problem_id"]: row for row in manifest["items"]}
    prepared = []
    for row in record["qualifications"]:
        original = by_id.get(row["problem_id"])
        d.require(original is not None, "screening cannot add a material row")
        for key in ("task_id", "revision", "source_id", "source_version", "claim_key", "publication_commit"):
            d.require(original.get(key) == row[key], "screening existing metadata mismatch: " + key)
        d.require(metadata(original.get("primary")) == metadata(row["counted_primary"]), "screening counted primary differs from manifest")
        d.require(set(row["semantic_dedup"]["compared_problem_ids"]) <= set(by_id), "screening comparison names unknown material IDs")
        if original.get("qualification_set_id") == record["qualification_set_id"]:
            d.require(original.get("difficulty_level") == row["difficulty_level"] and
                      original.get("difficulty_reason") == row["difficulty_reason"] and
                      original.get("difficulty_assessed_by") == row["assessed_by"], "screening set conflicts with existing projection")
        prepared.append((row, original))
    return prepared


def apply_screening(master, manifest, record):
    validate_screening_record(record)
    prepared = screened_rows(manifest, record)
    with contextlib.closing(sqlite3.connect(master)) as db, db:
        db.row_factory = sqlite3.Row
        info = {part[1] for part in db.execute("PRAGMA table_info(problems)")}
        d.require(set(QUAL_COLUMNS) | {"difficulty_level", "difficulty_reason", "source_locator_json"} <= info,
                  "screening requires the existing migrated metadata schema")
        for row, original in prepared:
            actual = db.execute("SELECT p.*,s.source_version FROM problems p JOIN sources s USING(source_id) WHERE p.problem_id=?",
                                (row["problem_id"],)).fetchone()
            d.require(actual is not None, "screening SQL material missing")
            for key in ("task_id", "revision", "source_id", "source_version", "claim_key"):
                d.require(actual[key] == row[key], "screening SQL existing metadata mismatch: " + key)
            d.require(row["publication_commit"] is None or actual["publication_commit"] == row["publication_commit"],
                      "screening SQL publication metadata mismatch")
            d.require(metadata(d.json.loads(actual["source_locator_json"]).get("primary")) == metadata(row["counted_primary"]),
                      "screening SQL counted primary mismatch")
            if actual["qualification_set_id"] == record["qualification_set_id"]:
                d.require(actual["difficulty_level"] == row["difficulty_level"] and actual["difficulty_reason"] == row["difficulty_reason"],
                          "screening SQL set conflicts with existing projection")
            columns = SCREENING_SQL_COLUMNS
            values = [record[key] if key == "qualification_set_id" else row[key] for key in columns]
            db.execute("UPDATE problems SET " + ",".join(key + "=?" for key in columns) + " WHERE problem_id=?", (*values, row["problem_id"]))
        d.require(not db.execute("SELECT claim_key FROM problems WHERE review_state='current' AND claim_key IS NOT NULL GROUP BY claim_key HAVING count(*)>1").fetchall(),
                  "screening creates a duplicate current claim")
    project_rows(prepared, record)
    return {"qualification_set_id": record["qualification_set_id"], "updated_existing_problem_ids": [row["problem_id"] for row, _ in prepared], "material_increment": 0}
