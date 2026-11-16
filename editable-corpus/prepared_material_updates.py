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
NATIVE_SQL_CAS = ("problem_id", "title", "difficulty_level", "difficulty_reason", "source_id", "source_locator_json",
                  "tex_path", "tex_content", "origin_class", "status", "compile_receipt_path", "task_id", "revision",
                  "validation_policy", "claim_key", "review_state", "dedup_state", "publication_commit",
                  "qualification_set_id", "review_protocol")
NATIVE_SOURCE_CAS = ("source_id", "source_version", "author")
NATIVE_REFERENCE_KEYS = ("problem_id", "material_format", "work_ref", "statement_spans", "context_spans")
NATIVE_LOCATOR_SPANS = ("primary", "contexts", "proof_spans", "statement_spans", "context_spans")
NATIVE_LOCATOR_KEYS = NATIVE_LOCATOR_SPANS + ("work_ref", "material_state", "run_state")
EDITORIAL_FIELDS = {"title", "difficulty_level", "difficulty_reason", "primary", "proof_spans", "contexts",
    "statement_spans", "context_spans", "statement_scope", "source_caveats", "item_path", "compile_receipt",
    "review_state", "dedup_state", "difficulty_state", "difficulty_assessed_by", "material_update_id",
    "duplicate_of", "canonical_problem_id", "counting_state", "qualification_state", "qualification_hold_reason", "eligible", "reading_pdf", "tex_sha256"}


def validate_editorial(entry, operation_id):
    """Bound same-ID corrections; source identity and unknown fields stay immutable."""
    changes = entry.get("changes")
    d.require(isinstance(changes, dict) and changes and set(changes) <= EDITORIAL_FIELDS,
              "editorial correction exceeds its explicit field scope")
    d.require(changes.get("material_update_id") == operation_id and
              isinstance(entry.get("expected_editorial"), dict) and
              set(entry["expected_editorial"]) == set(changes), "editorial old/new field snapshot missing")
    d.require(isinstance(entry.get("expected_sql_material"), dict) and
              set(entry["expected_sql_material"]) == {"tex_path", "tex_content", "compile_receipt_path", "tex_sha256"},
              "editorial SQL material baseline required")
    d.require(changes.get("difficulty_level", entry["expected"].get("difficulty_level")) in ("H1", "H2", "H3"),
              "editorial difficulty must be H1/H2/H3")
    d.require(d.nonempty(changes.get("difficulty_reason", entry["expected"].get("difficulty_reason"))) and
              isinstance(entry.get("evidence"), list) and entry["evidence"], "editorial author evidence/reason required")
    duplicate = changes.get("duplicate_of")
    if duplicate is not None:
        d.require(isinstance(duplicate, str) and duplicate.isdecimal() and duplicate != entry["problem_id"] and
                  changes.get("eligible") is False and changes.get("dedup_state") == "duplicate_alias" and
                  changes.get("counting_state") == "duplicate_alias", "duplicate must retain an explicit non-counting alias")
    if changes.get("difficulty_level", entry["expected"].get("difficulty_level")) == "H1":
        d.require(changes.get("eligible") is False, "H1 cannot remain eligible for the advanced collection")
    sql = entry.get("sql_changes", {})
    d.require(isinstance(sql, dict) and set(sql) <= {"tex_content", "tex_sha256"} and sql.get('tex_sha256') is None,
              "editorial SQL scope exceeds derived TeX or invents a digest")
    if sql:
        qa = entry.get("derived_readability", {})
        d.require(d.nonempty(sql.get("tex_content")) and qa.get("compiled") is True and
                  qa.get("problem_id") == entry["problem_id"] and qa.get("material_update_id") == operation_id and
                  type(qa.get("pages")) is int and qa["pages"] > 0 and qa.get("checked_pages") and
                  all(type(p) is int and 1 <= p <= qa["pages"] for p in qa["checked_pages"]) and
                  d.nonempty(changes.get("item_path")) and d.nonempty(changes.get("compile_receipt")),
                  "changed derived TeX requires actual compile and scoped visual evidence")
    assets = entry.get("asset_sources", {})
    d.require(isinstance(assets, dict), "editorial assets must be explicit")
    for name, path in assets.items():
        d.require(isinstance(name, str) and not Path(name).is_absolute() and ".." not in Path(name).parts and
                  d.nonempty(path), "editorial asset path invalid")


def native_spans(value):
    d.require(isinstance(value, list), "native locator spans required")
    return [d.normalized_span(span) for span in value]


def native_work_ref(value):
    d.require(isinstance(value, dict), "native work reference required")
    return {key: value.get(key) for key in ("work_key", "source_version")}


def native_reference(row):
    return {"problem_id": row.get("problem_id"), "material_format": row.get("material_format"),
            "work_ref": native_work_ref(row.get("work_ref")), "statement_spans": native_spans(row.get("statement_spans")),
            "context_spans": native_spans(row.get("context_spans"))}


def native_locator(value):
    value = d.locator_metadata(value)
    d.require(isinstance(value, dict), "native locator object required")
    result = {key: native_spans(value.get(key)) for key in NATIVE_LOCATOR_SPANS}
    result["work_ref"] = native_work_ref(value.get("work_ref"))
    result["material_state"] = value.get("material_state")
    result["run_state"] = value.get("run_state")
    return result


def native_snapshot(row):
    result = snapshot(row)
    for key in ("primary", "proof_spans", "contexts"):
        result[key] = native_spans(result[key])
    return result


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
        d.require(entry.get("kind") in ("authors_only", "material_revision", "material_association", "native_metadata", "editorial_correction") and d.nonempty(entry.get("reason")) and
                  isinstance(entry.get("expected"), dict) and set(entry["expected"]) == set(CAS_FIELDS), "maintenance kind/expected metadata/reason missing")
        if entry["kind"] == "editorial_correction":
            validate_editorial(entry, value["qualification_set_id"])
        elif entry["kind"] == "native_metadata":
            allowed = {"problem_id", "kind", "reason", "expected", "expected_context_spans", "expected_reference", "expected_sql", "expected_source", "difficulty_reason", "context_spans",
                       "changes", "old_values", "old_missing_fields"}
            d.require(set(entry) <= allowed and set(entry) >= {"problem_id", "kind", "reason", "expected", "expected_context_spans", "expected_reference", "expected_sql", "expected_source", "difficulty_reason", "context_spans"},
                      "native metadata operation contains unauthorized fields")
            d.require(isinstance(entry["expected_reference"], dict) and isinstance(entry["expected_sql"], dict) and
                      isinstance(entry["expected_source"], dict) and set(entry["expected_reference"]) == set(NATIVE_REFERENCE_KEYS) and
                      entry["expected_reference"].get("context_spans") == entry["expected_context_spans"] and
                      set(entry["expected_sql"].get("source_locator_json", {})) == set(NATIVE_LOCATOR_KEYS) and
                      set(entry["expected_sql"]) == set(NATIVE_SQL_CAS) and set(entry["expected_source"]) == set(NATIVE_SOURCE_CAS),
                      "native reference and bounded SQL baseline required")
            d.require(d.nonempty(entry["difficulty_reason"]) and isinstance(entry["context_spans"], list) and entry["context_spans"] and
                      isinstance(entry["expected_context_spans"], list) and entry["expected"]["contexts"] == entry["expected_context_spans"],
                      "native metadata old/new context and reason required")
            d.require(native_spans(entry["context_spans"]) == entry["context_spans"] and
                      native_spans(entry["expected_context_spans"]) == entry["expected_context_spans"],
                      "native contexts must use public span fields")
        elif entry["kind"] == "authors_only":
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
    current = native_snapshot(rows[0]) if entry["kind"] == "native_metadata" else snapshot(rows[0])
    d.require(current == expected, "maintenance expected old/current metadata differs")
    if entry["kind"] == "editorial_correction":
        wanted = entry["changes"] if projected else entry["expected_editorial"]
        d.require(all(rows[0].get(k) == v for k, v in wanted.items()), "editorial field baseline differs")
        canonical = entry["changes"].get("duplicate_of")
        effective = copy.deepcopy(rows[0]); effective.update(entry["changes"])
        d.require(not effective.get("duplicate_of") or (effective.get("eligible") is False and
                  effective.get("dedup_state") == effective.get("counting_state") == "duplicate_alias"),
                  "an existing duplicate alias cannot regain eligibility")
        if canonical:
            targets = [r for r in manifest["items"] if r["problem_id"] == canonical]
            d.require(len(targets) == 1 and not targets[0].get("duplicate_of"), "duplicate canonical ID must be a retained non-alias")
    if entry["kind"] == "native_metadata":
        reference = copy.deepcopy(entry["expected_reference"])
        if projected:
            reference["context_spans"] = copy.deepcopy(entry["changes"]["context_spans"])
        d.require(native_reference(rows[0]) == reference, "native reference baseline differs")
        context = entry["changes"]["context_spans"] if projected else entry["expected_context_spans"]
        d.require(rows[0].get("context_spans") == context and rows[0].get("contexts") == context and
                  rows[0].get("material_format") == d.NATIVE_FORMAT and rows[0].get("status") == "complete_author_material" and
                  rows[0].get("origin_class") == "author_native_lean" and isinstance(rows[0].get("work_ref"), dict),
                  "native metadata context or reference state differs")
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
        if entry["kind"] == "editorial_correction":
            changes = copy.deepcopy(entry["changes"])
            entry.pop("asset_sources", None)
        elif entry["kind"] == "native_metadata":
            changes = {"difficulty_reason": entry["difficulty_reason"], "contexts": copy.deepcopy(entry["context_spans"]),
                       "context_spans": copy.deepcopy(entry["context_spans"])}
            d.require(any(old.get(k) != v for k, v in changes.items()), "native metadata operation has no changes")
        elif entry["kind"] == "authors_only":
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
        entry["changes"] = (changes if entry["kind"] in ("native_metadata", "editorial_correction") else
                            {key: value for key, value in changes.items() if old.get(key) != value or key not in old})
        entry["old_values"] = {key: copy.deepcopy(old.get(key)) for key in entry["changes"]}
        if entry["kind"] == "native_metadata":
            for key in ("contexts", "context_spans"):
                entry["old_values"][key] = native_spans(entry["old_values"][key])
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
        allowed = (EDITORIAL_FIELDS if entry["kind"] == "editorial_correction" else {"difficulty_reason", "contexts", "context_spans"} if entry["kind"] == "native_metadata" else {"authors"} if entry["kind"] == "authors_only" else {"materials"} if entry["kind"] == "material_association"
                   else set(MATERIAL_FIELDS) | {"difficulty_state", "difficulty_assessed_by", "material_update_id"})
        d.require(set(entry["changes"]) <= allowed and set(entry["old_values"]) == set(entry["changes"]), "maintenance changes exceed the explicit field scope")
        if entry["kind"] == "editorial_correction":
            d.require(entry["old_values"] == entry["expected_editorial"], "published editorial previous fields differ")
        elif entry["kind"] == "native_metadata":
            proposed = {"difficulty_reason": entry["difficulty_reason"], "contexts": entry["context_spans"], "context_spans": entry["context_spans"]}
            previous = {"difficulty_reason": entry["expected"]["difficulty_reason"], "contexts": entry["expected"]["contexts"],
                        "context_spans": entry["expected_context_spans"]}
            d.require(entry["changes"] == proposed and entry["old_values"] == previous and entry.get("old_missing_fields") == [],
                      "published native metadata projection differs")
        elif entry["kind"] == "authors_only":
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
                # Native span snapshots are normalized; retain any unrecorded
                # locator extensions while restoring the other CAS metadata.
                if entry["kind"] == "native_metadata" and key in ("primary", "proof_spans", "contexts"):
                    continue
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
            if entry["kind"] == "native_metadata":
                sql_expected = copy.deepcopy(entry["expected_sql"])
                d.require(set(NATIVE_SQL_CAS) <= set(actual.keys()), "native required SQL columns missing")
                source_expected = entry["expected_source"]
                source_actual = db.execute("SELECT source_id,source_version,author FROM sources WHERE source_id=?", (old["source_id"],)).fetchone()
                d.require(source_actual is not None and dict(source_actual) == source_expected,
                          "native SQL source baseline differs")
                projected_sql = copy.deepcopy(sql_expected)
                projected_locator = copy.deepcopy(sql_expected["source_locator_json"])
                projected_locator["contexts"] = copy.deepcopy(entry["changes"]["contexts"])
                projected_locator["context_spans"] = copy.deepcopy(entry["changes"]["context_spans"])
                projected_sql["difficulty_reason"] = entry["changes"]["difficulty_reason"]
                projected_sql["source_locator_json"] = projected_locator
                projected = (old.get("difficulty_reason") == entry["difficulty_reason"] and
                             native_spans(old.get("context_spans")) == entry["context_spans"])
                target_sql = projected_sql if projected else sql_expected
                observed = {k: actual[k] for k in sql_expected}
                observed["source_locator_json"] = native_locator(d.json.loads(actual["source_locator_json"]))
                d.require(observed == target_sql, "native SQL baseline differs")
            for key in BINDING_FIELDS:
                wanted = old.get(key)
                d.require(actual[key] == wanted or (key == "claim_key" and actual[key] is None and actual["validation_policy"] == "legacy"), "maintenance SQL binding mismatch: " + key)
            d.require(actual["source_author"] == old["author"], "maintenance SQL scalar source author differs")
            d.require(actual["validation_policy"] == old.get("policy", "legacy"), "maintenance SQL policy differs")
            d.require(old.get("publication_commit") is None or actual["publication_commit"] == old["publication_commit"], "maintenance SQL publication metadata differs")
            for key in ("title", "difficulty_level", "difficulty_reason", "revision", "review_state", "dedup_state", "qualification_set_id", "review_protocol"):
                d.require(actual[key] == old.get(key), "maintenance SQL current metadata differs: " + key)
            if entry["kind"] != "native_metadata":
                d.require(d.locator_metadata(d.json.loads(actual["source_locator_json"])) == d.locator_metadata(d.locator(old)), "maintenance SQL counted locations differ")
            if entry["kind"] == "editorial_correction":
                proposed = copy.deepcopy(old)
                proposed.update(copy.deepcopy(entry["changes"]))
                previous = entry["expected_sql_material"]
                projected_material = copy.deepcopy(previous)
                projected_material.update(entry.get("sql_changes", {}))
                if proposed.get("status") != "complete_author_material" and proposed.get("origin_class") != "author_native_lean":
                    for name, column in (("item_path", "tex_path"), ("compile_receipt", "compile_receipt_path")):
                        if name in entry["changes"]:
                            projected_material[column] = proposed[name]
                observed = {key: actual[key] for key in previous}
                d.require(observed == previous or observed == projected_material,
                          "editorial SQL material changed after approval")
                columns = {key: proposed[key] for key in ("title", "difficulty_level", "difficulty_reason", "review_state", "dedup_state")
                           if key in entry["changes"]}
                columns["source_locator_json"] = d.json.dumps(d.locator(proposed), ensure_ascii=False)
                if proposed.get("status") != "complete_author_material" and proposed.get("origin_class") != "author_native_lean":
                    for name, column in (("item_path", "tex_path"), ("compile_receipt", "compile_receipt_path")):
                        if name in entry["changes"]:
                            columns[column] = proposed[name]
                columns.update(entry.get("sql_changes", {}))
                db.execute("UPDATE problems SET " + ",".join(k + "=?" for k in columns) + " WHERE problem_id=?",
                           (*columns.values(), entry["problem_id"]))
                continue
            if entry["kind"] == "authors_only":
                continue
            if entry["kind"] == "native_metadata":
                locator = d.json.loads(actual["source_locator_json"])
                locator["contexts"] = copy.deepcopy(entry["changes"]["contexts"])
                locator["context_spans"] = copy.deepcopy(entry["changes"]["context_spans"])
                db.execute("UPDATE problems SET difficulty_reason=?, source_locator_json=? WHERE problem_id=?",
                           (entry["changes"]["difficulty_reason"], d.json.dumps(locator, ensure_ascii=False), entry["problem_id"]))
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
        for key in ("replacement_job", "replacement_qa_path", "replacement_row", "visual_qa", "compile_metadata", "old_values", "old_missing_fields", "material_work_registry", "asset_sources"):
            entry.pop(key, None)
        if entry["kind"] != "editorial_correction":
            entry.pop("changes", None)
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
