"""Same-ID maintenance operations inside the existing prepared publisher."""
import contextlib
import copy
from pathlib import Path
import re
import sqlite3

import prepared_delivery as d

RECORD_TYPE = "existing_material_update_v1"
BINDING_FIELDS = ("task_id", "revision", "source_id", "source_version", "claim_key")
CAS_FIELDS = BINDING_FIELDS + ("title", "author", "authors", "difficulty_level", "difficulty_reason", "primary", "proof_spans", "contexts",
    "item_path", "compile_receipt", "prepared_job", "policy", "origin_class", "status", "review_state", "dedup_state", "publication_commit",
    "qualification_set_id", "qualification_basis", "review_protocol", "difficulty_state", "difficulty_assessed_by", "material_update_id")
MATERIAL_FIELDS = ("title", "revision", "difficulty_level", "difficulty_reason", "primary", "proof_spans", "contexts", "item_path", "compile_receipt",
    "prepared_job", "origin_class", "status", "source_files", "asset_dependencies", "license_evidence_path", "material_format", "native_material")
SQL_FIELDS = ("title", "revision", "difficulty_level", "difficulty_reason", "source_locator_json", "tex_path", "tex_content", "origin_class", "status", "compile_receipt_path")


def snapshot(row):
    return {key: copy.deepcopy(row.get(key)) for key in CAS_FIELDS}


def associated_materials(entry):
    materials = copy.deepcopy(entry.get("expected_materials") or [])
    d.require(isinstance(materials, list), "existing associated materials must be a list")
    material = entry.get("material", {})
    d.require(isinstance(material, dict) and d.nonempty(material.get("material_key")) and
              material.get("same_problem_as") == entry["problem_id"] and
              material.get("relation") in ("alternate_proof", "alternate_author_presentation"),
              "explicit same-problem author material required")
    ref = material.get("work_ref", {})
    d.require(d.nonempty(ref.get("work_key")) and d.nonempty(ref.get("source_version")) and
              all(isinstance(material.get(key), list) and material[key] for key in
                  ("statement_spans", "proof_spans", "context_spans")), "associated fixed-work spans required")
    reader = material.get("reader_path", "")
    d.require(d.nonempty(reader) and not Path(reader).is_absolute() and ".." not in Path(reader).parts,
              "associated public reader path required")
    matching = [item for item in materials if item.get("material_key") == material["material_key"]]
    d.require(not matching or matching == [material], "associated material key already has different metadata")
    if not matching:
        materials.append(copy.deepcopy(material))
    return materials


def validate_record(value):
    d.require(value.get("schema_version") == 2 and value.get("record_type") == RECORD_TYPE and
              value.get("material_increment") == 0 and value.get("status") == "approved_metadata_projection_pending_public_delivery",
              "explicit approved same-ID maintenance record required")
    d.require(d.ID.fullmatch(str(value.get("qualification_set_id", ""))) and d.nonempty(value.get("approved_by")) and
              re.fullmatch(r"[0-9a-f]{40}", str(value.get("basis_public_commit", ""))), "maintenance approval/base missing")
    entries = value.get("updates")
    d.require(isinstance(entries, list) and entries, "maintenance targets required")
    ids = set()
    for entry in entries:
        ident = entry.get("problem_id")
        d.require(isinstance(ident, str) and ident.isdecimal() and ident not in ids, "unique exact stable ID required")
        ids.add(ident)
        d.require(entry.get("kind") in ("authors_only", "material_revision", "material_association") and d.nonempty(entry.get("reason")) and
                  isinstance(entry.get("expected"), dict) and set(entry["expected"]) == set(CAS_FIELDS), "maintenance kind/expected metadata/reason missing")
        if entry["kind"] == "authors_only":
            authors = entry.get("authors")
            d.require(isinstance(authors, list) and authors and all(d.nonempty(author) for author in authors) and
                      "; ".join(authors) == entry["expected"]["author"], "authors correction must match the already correct scalar author")
        elif entry["kind"] == "material_association":
            d.require("expected_materials" in entry, "association requires the previous material list")
            materials = associated_materials(entry)
            if "changes" in entry:
                d.require(set(entry["changes"]) <= {"materials"} and
                          entry["changes"].get("materials", entry["expected_materials"]) == materials,
                          "association must only append the declared author material")
        else:
            binding = entry.get("replacement_binding", {})
            d.require(set(binding) == set(BINDING_FIELDS) and all(binding.get(key) == entry["expected"].get(key) for key in BINDING_FIELDS if key != "revision") and
                      binding.get("revision") != entry["expected"]["revision"] and d.REVISION.fullmatch(str(binding.get("revision", ""))), "replacement must retain task/source/claim and change revision")
            d.require(d.nonempty(entry.get("same_claim_basis")) and entry.get("difficulty_level") in ("H2", "H3") and
                      d.nonempty(entry.get("difficulty_reason")) and d.nonempty(entry.get("assessed_by")), "same-claim material/H basis missing")
            if "changes" not in entry:
                d.require(d.nonempty(entry.get("replacement_job")) and d.nonempty(entry.get("replacement_qa_path")), "compiled replacement job/actual QA required")
    return value


def select(spec):
    paths = spec.get("material_update_paths", [])
    d.require(isinstance(paths, list), "material updates require explicit paths")
    records = [validate_record(d.load(path)) for path in paths]
    d.require(not records or not any(spec.get(key) for key in ("job_paths", "qualification_paths", "retirements")), "same-ID updates require a separate zero-increment batch")
    d.require(len({record["qualification_set_id"] for record in records}) == len(records), "duplicate maintenance operation ID")
    return records


def checked_row(manifest, entry, *, projected=False):
    ident = entry["problem_id"]
    d.require(ident not in set(map(str, manifest.get("retired_problem_ids", []))), "maintenance cannot target a retired ID")
    rows = [row for row in manifest["items"] if row["problem_id"] == ident]
    d.require(len(rows) == 1, "maintenance requires an existing active ID")
    expected = copy.deepcopy(entry["expected"])
    if projected:
        expected.update({key: value for key, value in entry["changes"].items() if key in CAS_FIELDS})
    d.require(snapshot(rows[0]) == expected, "maintenance expected old/current metadata differs")
    if entry["kind"] == "material_association":
        expected_materials = entry["changes"].get("materials", entry["expected_materials"]) if projected else entry["expected_materials"]
        d.require(rows[0].get("materials") == expected_materials, "associated material list changed")
    return rows[0]


def validate_qa(entry, row, receipt, qa):
    d.require(receipt.get("ok") is True and d.binding(receipt) == d.binding(row) and
              qa.get("task_id") == row["task_id"] and qa.get("revision") == row["revision"] and
              qa.get("canonical_problem_id") == entry["problem_id"] and qa.get("result") == "pass" and
              qa.get("mathematics_modified") is False and qa.get("pages") == receipt.get("pages") and
              qa.get("all_pages_visually_read") == list(range(1, receipt["pages"] + 1)), "replacement actual all-page QA differs from compiled revision")


def build_record(approved, manifest, replacement):
    """Resolve declared compiled jobs into public metadata; local paths stay out of Git."""
    validate_record(approved)
    result = copy.deepcopy(approved)
    for entry in result["updates"]:
        old = checked_row(manifest, entry)
        if entry["kind"] == "authors_only":
            changes = {"authors": entry["authors"]}
        elif entry["kind"] == "material_association":
            changes = {"materials": associated_materials(entry)}
            entry.pop("material_work_registry", None)
        else:
            row, receipt, qa = replacement(entry)
            d.require(all(row.get(key) == entry["replacement_binding"][key] for key in BINDING_FIELDS) and row["problem_id"] == entry["problem_id"], "replacement copied job binding differs")
            d.require(row["primary"] == old["primary"] and row.get("proof_spans") == old.get("proof_spans"), "replacement counted statement/proof locators differ")
            d.require(row["difficulty_level"] == entry["difficulty_level"] and row["difficulty_reason"] == entry["difficulty_reason"], "replacement difficulty differs from approval")
            validate_qa(entry, row, receipt, qa)
            changes = {key: copy.deepcopy(row.get(key)) for key in MATERIAL_FIELDS if key in row or key in old}
            changes.update(difficulty_state="screened_H2_H3", difficulty_assessed_by=entry["assessed_by"], material_update_id=result["qualification_set_id"])
            entry["visual_qa"] = qa
            entry["compile_metadata"] = {key: copy.deepcopy(receipt[key]) for key in ("problem_id", *BINDING_FIELDS, "pages", "ok")}
            entry["replacement_row"] = row
            entry.pop("replacement_job", None); entry.pop("replacement_qa_path", None)
        entry["changes"] = {key: value for key, value in changes.items() if old.get(key) != value or key not in old}
        entry["old_values"] = {key: copy.deepcopy(old.get(key)) for key in entry["changes"]}
        entry["old_missing_fields"] = [key for key in entry["changes"] if key not in old]
    return result


def project_rows(prepared, record):
    for entry, row in prepared:
        row.update(copy.deepcopy(entry["changes"]))


def reviewed_rows(manifest, record):
    validate_record(record)
    prepared = []
    for entry in record["updates"]:
        d.require(isinstance(entry.get("changes"), dict) and isinstance(entry.get("old_values"), dict), "published maintenance projection missing")
        allowed = ({"authors"} if entry["kind"] == "authors_only" else {"materials"} if entry["kind"] == "material_association"
                   else set(MATERIAL_FIELDS) | {"difficulty_state", "difficulty_assessed_by", "material_update_id"})
        d.require(set(entry["changes"]) <= allowed and set(entry["old_values"]) == set(entry["changes"]), "maintenance changes exceed the explicit field scope")
        if entry["kind"] == "authors_only":
            d.require(entry["changes"].get("authors", entry["expected"]["authors"]) == entry["authors"], "published authors correction differs")
        elif entry["kind"] == "material_association":
            d.require(entry["changes"].get("materials", entry["expected_materials"]) == associated_materials(entry),
                      "published associated material differs")
        else:
            row = entry["replacement_row"]
            d.require(row["problem_id"] == entry["problem_id"] and all(row.get(key) == entry["replacement_binding"][key] for key in BINDING_FIELDS) and
                      row["primary"] == entry["expected"]["primary"] and row.get("proof_spans") == entry["expected"]["proof_spans"], "published replacement identity/counting unit differs")
            d.require(all(value == row.get(key) for key, value in entry["changes"].items() if key in MATERIAL_FIELDS) and
                      entry["changes"].get("revision") == entry["replacement_binding"]["revision"] and
                      row["difficulty_level"] == entry["difficulty_level"] and row["difficulty_reason"] == entry["difficulty_reason"], "published replacement material projection differs")
        try:
            row = checked_row(manifest, entry)
        except ValueError:
            row = checked_row(manifest, entry, projected=True)
        prepared.append((entry, row))
    return prepared


def historical_manifest(manifest, records):
    result = copy.deepcopy(manifest)
    by_id = {row["problem_id"]: row for row in result["items"]}
    for record in reversed(records):
        for entry in reversed(record["updates"]):
            d.require(entry["problem_id"] in by_id, "maintenance history missing active/retired metadata")
            row = by_id[entry["problem_id"]]
            row.update(copy.deepcopy(entry["old_values"]))
            # Later qualifications can introduce manifest-only CAS metadata
            # (for example qualification_basis). Restore the captured stage,
            # not just fields this maintenance operation itself changed.
            for key, value in entry["expected"].items():
                if key in row or value is not None:
                    row[key] = copy.deepcopy(value)
            for key in entry.get("old_missing_fields", []):
                row.pop(key, None)
    return result


def apply(master, manifest, record, read_review, read_file):
    prepared = reviewed_rows(manifest, record)
    replacement_db = read_file("editable-corpus/" + record["replacement_delta"]) if record.get("replacement_delta") else None
    if replacement_db:
        d.validate_database(replacement_db, [entry["replacement_row"] for entry in record["updates"] if entry["kind"] == "material_revision"])
    with contextlib.closing(sqlite3.connect(master)) as db, db:
        db.row_factory = sqlite3.Row
        if replacement_db:
            db.execute("ATTACH DATABASE ? AS replacement", (str(replacement_db),))
        for entry, old in prepared:
            actual = db.execute("SELECT p.*,s.source_version,s.author AS source_author FROM problems p JOIN sources s USING(source_id) WHERE problem_id=?", (entry["problem_id"],)).fetchone()
            d.require(actual is not None, "maintenance SQL ID missing")
            for key in BINDING_FIELDS:
                wanted = old.get(key)
                d.require(actual[key] == wanted or (key == "claim_key" and actual[key] is None and actual["validation_policy"] == "legacy"), "maintenance SQL binding mismatch: " + key)
            d.require(actual["source_author"] == old["author"], "maintenance SQL scalar source author differs")
            d.require(actual["validation_policy"] == old.get("policy", "legacy"), "maintenance SQL policy differs")
            d.require(old.get("publication_commit") is None or actual["publication_commit"] == old["publication_commit"], "maintenance SQL publication metadata differs")
            for key in ("title", "difficulty_level", "difficulty_reason", "revision", "review_state", "dedup_state", "qualification_set_id", "review_protocol"):
                d.require(actual[key] == old.get(key), "maintenance SQL current metadata differs: " + key)
            d.require(d.locator_metadata(d.json.loads(actual["source_locator_json"])) == d.locator_metadata(d.locator(old)), "maintenance SQL counted locations differ")
            if entry["kind"] == "authors_only":
                continue
            if entry["kind"] == "material_association":
                locator = d.json.loads(actual["source_locator_json"])
                locator["materials"] = copy.deepcopy(entry["changes"].get("materials", old.get("materials")))
                db.execute("UPDATE problems SET source_locator_json=? WHERE problem_id=?",
                           (d.json.dumps(locator, ensure_ascii=False), entry["problem_id"]))
                continue
            incoming = db.execute("SELECT * FROM replacement.problems WHERE problem_id=?", (entry["problem_id"],)).fetchone()
            d.require(incoming is not None and all(incoming[key] == entry["replacement_binding"][key] for key in BINDING_FIELDS if key != "source_version"), "replacement SQL row binding mismatch")
            receipt = entry["compile_metadata"]
            validate_qa(entry, entry["replacement_row"], receipt, entry["visual_qa"])
            if actual["revision"] == incoming["revision"]:
                d.require(all(actual[key] == incoming[key] for key in SQL_FIELDS if key != "tex_content"), "repeated maintenance SQL projection differs")
                continue
            # Retain every existing review/publication/custom column. Only these
            # material fields are taken from the same-ID replacement payload.
            db.execute("UPDATE problems SET " + ",".join(key + "=?" for key in SQL_FIELDS) + " WHERE problem_id=?",
                       (*[incoming[key] for key in SQL_FIELDS], entry["problem_id"]))
    project_rows(prepared, record)
    return {"qualification_set_id": record["qualification_set_id"], "updated_existing_problem_ids": [entry["problem_id"] for entry, _ in prepared], "material_increment": 0}


def approval_metadata(record):
    result = copy.deepcopy(record)
    result.pop("replacement_delta", None)
    for entry in result["updates"]:
        for key in ("replacement_job", "replacement_qa_path", "replacement_row", "visual_qa", "compile_metadata", "changes", "old_values", "old_missing_fields", "material_work_registry"):
            entry.pop(key, None)
    return result


def adopt_existing(job, output_root, approved, manifest):
    """An operation-scoped reservation reuses the approved active ID, never an allocator."""
    validate_record(approved)
    state = d.load(Path(job) / "job-state.json")
    task = d.load(Path(job) / state["package"] / state["task_snapshot"])
    entries = [entry for entry in approved["updates"] if entry["kind"] == "material_revision" and
               all(task.get(key) == entry["replacement_binding"][key] for key in BINDING_FIELDS)]
    d.require(len(entries) == 1, "replacement job has no unique same-ID operation")
    entry = entries[0]; checked_row(manifest, entry)
    reservation = dict(entry["replacement_binding"], problem_id=entry["problem_id"])
    root = Path(output_root).resolve()
    path = root / (approved["qualification_set_id"] + "-existing-id-reservation.json")
    if path.exists():
        d.require(d.load(path) == {"entries": [reservation], "existing_id_operation": approved["qualification_set_id"]}, "operation reservation conflict")
    else:
        d.save(path, {"entries": [reservation], "existing_id_operation": approved["qualification_set_id"]})
    return d.adopt_material(job, root, path)
