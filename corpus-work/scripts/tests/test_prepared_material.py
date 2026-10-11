"""Focused author-material adoption tests; existing compile outputs, no models/Git/network."""
import copy
import json
import os
from pathlib import Path
import sqlite3
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
import prepared_delivery as d
import prepared_publish as p

ROOT = SCRIPTS.parents[1]

class AuthorMaterialTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Retain test artifacts; do not remove user or fixture files.
        cls.output = Path(tempfile.mkdtemp(prefix="author-material-tests-"))
        worklist = ROOT / "research-line/harness-ready-20261011/PREPARATION_WORKLIST.jsonl"
        entries = [json.loads(line) for line in worklist.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
        entry = next(x for x in entries if x.get("assembly_job") and x.get("state") == "prepared_unpublished")
        cls.source = Path(entry["assembly_job"])
        if not cls.source.is_absolute():
            cls.source = ROOT / cls.source
        state = d.load(cls.source / "job-state.json")
        cls.task = d.load(cls.source / state["package"] / state["task_snapshot"])
        cls.reservations = cls.output / "reservations.json"
        cls.reserved = dict(d.binding(cls.task), problem_id="900999990")
        d.save(cls.reservations, {"entries": [cls.reserved]})

    def adopt(self, name):
        with patch.object(d, "review_records", side_effect=AssertionError("no mathematical review")), \
             patch.object(d, "validate_qa", side_effect=AssertionError("no QA gate")), \
             patch.object(d, "compile_job", side_effect=AssertionError("no recompilation")):
            return d.adopt_material(self.source, self.output / name, self.reservations)

    def test_adoption_without_reviews_preserves_final_material_and_resume(self):
        result = self.adopt("success")
        job = Path(result["job"])
        state = d.load(job / "job-state.json")
        row = d.load(job / state["package"] / "manifest.json")["items"][0]
        receipt = d.load(job / state["package"] / row["compile_receipt"])
        source_state = d.load(self.source / "job-state.json")
        self.assertEqual((job / state["package"] / row["item_path"]).read_bytes(),
                         (self.source / source_state["package"] / row["item_path"]).read_bytes())
        self.assertEqual((job / receipt["pdf_path"]).read_bytes(), (self.source / receipt["pdf_path"]).read_bytes())
        self.assertEqual(row["review_state"], d.MATERIAL_BASIS)
        self.assertEqual(result["sql"]["qualified_current_published_count"], 0)
        self.assertTrue(self.adopt("success")["resumed"])
        self.assertFalse((job / ("PAGE_QA-root-" + state["revision"] + ".json")).exists())
        spec = {"preparation_basis": d.MATERIAL_BASIS, "job_paths": [str(job)], "reservations_path": str(self.reservations)}
        self.assertEqual(len(p.select_jobs(spec)), 1)
        with self.assertRaisesRegex(ValueError, "duplicate"):
            p.select_jobs(dict(spec, job_paths=[str(job), str(job)]))
        # Exercise the publication artifact projection and restored verification.
        corpus = self.output / "public-copy"
        exported, names = p.public_job(job, corpus, result)
        restored = corpus / exported["prepared_job"]
        self.assertEqual(d.verify_job(restored, require_ready=False)["problem_id"], self.reserved["problem_id"])
        database = corpus / "delta.sqlite"
        d.create_database(corpus, [exported], database)
        with sqlite3.connect(database) as db:
            db.execute("UPDATE problems SET publication_commit=?", ("a" * 40,))
        db.close()
        counts = d.validate_database(database)
        self.assertEqual(counts["qualified_published_by_basis"], {d.MATERIAL_BASIS: 1})

    def test_uploaded_material_set_needs_no_build_logs_or_rendered_pages(self):
        reduced = self.output / "uploaded-input"
        source_state = d.load(self.source / "job-state.json")
        package = self.source / source_state["package"]
        row = d.load(package / "manifest.json")["items"][0]
        receipt = d.load(package / row["compile_receipt"])
        paths = {"job-state.json", receipt["pdf_path"]}
        paths.update(path.relative_to(self.source).as_posix() for path in package.rglob("*") if path.is_file())
        for name in paths:
            dst = reduced / name
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(self.source / name, dst)
        self.assertFalse((reduced / receipt["compiler_log_path"]).exists())
        self.assertTrue(all(not (reduced / name).exists() for name in receipt["rendered_pages"]))
        result = d.adopt_material(reduced, self.output / "from-upload", self.reservations)
        job = Path(result["job"])
        self.assertEqual(d.verify_job(job)["preparation_basis"], d.MATERIAL_BASIS)
        corpus = self.output / "uploaded-public-copy"
        exported, names = p.public_job(job, corpus, result)
        restored = corpus / exported["prepared_job"]
        self.assertEqual(d.verify_job(restored, require_ready=False)["problem_id"], self.reserved["problem_id"])
        self.assertFalse((restored / receipt["compiler_log_path"]).exists())
        self.assertTrue(all(not (restored / name).exists() for name in receipt["rendered_pages"]))

    def test_missing_material_is_rejected(self):
        result = self.adopt("missing")
        job = Path(result["job"])
        state = d.load(job / "job-state.json")
        path = job / state["package"] / "manifest.json"
        manifest = d.load(path)
        manifest["items"][0]["source_files"][0]["path"] = "missing-author-source.tex"
        d.save(path, manifest)
        with self.assertRaisesRegex(ValueError, "missing|exist"):
            d.verify_job(job)

    def test_existing_material_protocol_reserves_and_resumes_without_relabeling(self):
        folder = self.output / "material-protocol"
        folder.mkdir()
        master = folder / "master.sqlite"
        with sqlite3.connect(master) as db:
            db.execute("CREATE TABLE problems (problem_id TEXT PRIMARY KEY)")
        db.close()
        actor = {"owner": "material-collector", "generation": 1}
        d.save(folder / "owner.json", actor)
        d.save(folder / "queue.json", {})
        d.save(folder / "flow.json", {})
        request = dict(d.binding(self.task), task_id="existing-material-protocol", review_protocol="material-preparation-v1")
        request.pop("problem_id")
        spec = {"state_root": str(folder), "actor": actor, "master_db": str(master),
                "queue_path": str(folder / "queue.json"), "flow_path": str(folder / "flow.json"),
                "reservations_path": str(folder / "reservations.json"), "requests": [request],
                "preparation_basis": d.MATERIAL_BASIS}
        first = p.reserve(spec)
        self.assertEqual(first["entries"][0]["review_protocol"], "material-preparation-v1")
        self.assertEqual(first, p.reserve(spec))
        with self.assertRaisesRegex(ValueError, "unknown reservation"):
            p.reserve(dict(spec, preparation_basis=None))

    def test_material_source_reconciliation_accepts_collector_record(self):
        fields = {"author": "Author", "work": "Source", "source_url": "https://example.invalid/v1",
                  "source_version": "v1", "license": "CC BY 4.0"}
        baseline = dict(fields, source_id="same-source", license_path="old-notice.txt")
        material = dict(baseline, preparation_basis=d.MATERIAL_BASIS, work="Source title spelling")
        record = {"source_id": "same-source", "recorded_by": "material-collector",
                  "reason": "Retain the existing title spelling for the shared source row",
                  "task_metadata": {key: material[key] for key in fields}, "public_metadata": fields}
        p.normalize_source_rows([material], [baseline], [record])
        self.assertEqual(material["work"], baseline["work"])
        self.assertEqual(material["source_metadata_reconciliation"]["recorded_by"], "material-collector")
        changed = dict(baseline, preparation_basis=d.MATERIAL_BASIS, source_version="v2")
        with self.assertRaisesRegex(ValueError, "actual fixed-version"):
            p.normalize_source_rows([changed], [baseline], [record])

    def test_retained_license_formats_without_new_approval_records(self):
        result = self.adopt("license-formats")
        job = Path(result["job"])
        state = d.load(job / "job-state.json")
        row = d.load(job / state["package"] / "manifest.json")["items"][0]
        path = job / state["package"] / row["license_evidence_path"]
        fixtures = [
            {"source_notice": "Fixture retained author license notice"},
            {"name": "CC BY 4.0", "version_url": self.task["source_url"],
             "prior_license_path": "retained-license.txt", "basis": "Existing retained license record"},
            {"license": "CC BY 4.0", "license_url": "https://creativecommons.org/licenses/by/4.0/",
             "source_url": self.task["source_url"], "publisher_rights_fact": "Existing publisher rights statement"},
        ]
        for evidence in fixtures:
            d.save(path, evidence)
            self.assertEqual(d.verify_job(job)["preparation_basis"], d.MATERIAL_BASIS)
        d.save(path, {})
        with self.assertRaisesRegex(ValueError, "licence"):
            d.verify_job(job)

    def test_conflicting_reservation_cannot_resume(self):
        self.adopt("conflict")
        changed = self.output / "different-reservation.json"
        d.save(changed, {"entries": [dict(self.reserved, problem_id="900999991")]})
        with self.assertRaisesRegex(ValueError, "conflicts"):
            d.adopt_material(self.source, self.output / "conflict", changed)

if __name__ == "__main__":
    unittest.main()
