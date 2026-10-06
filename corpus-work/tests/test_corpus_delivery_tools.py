"""Regression checks for actual delivery failures; scratch directories retained."""
import importlib.util
import json
import os
import stat
import tempfile
import unittest
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "corpus-work/scripts/corpus_delivery_tools.py"
spec = importlib.util.spec_from_file_location("delivery_tools", SCRIPT)
tools = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tools)


class DeliveryToolsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(tempfile.mkdtemp(prefix="corpus-reuse-test-", dir=os.environ.get("CORPUS_TEST_ROOT")))

    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix=self._testMethodName + "-", dir=self.__class__.root))

    def report(self, value):
        path = self.root / "report.json"
        tools.dump(path, value)
        return path

    def test_nested_failed_item_cannot_hide_behind_empty_global_errors(self):
        p = self.report({"mode": "editable-delivery", "package_item_count": 1,
                         "editable_qualified_count": 1, "errors": [],
                         "items": {"1": {"status": "failed", "errors": ["source mismatch"]}}})
        with self.assertRaises(ValueError):
            tools.check_report(p, 1)

    def test_duplicate_json_key_cannot_replace_failure(self):
        p = self.root / "report.json"
        p.write_text('{"mode":"editable-delivery","package_item_count":1,"editable_qualified_count":1,"errors":[],"items":{"1":{"status":"failed","errors":["bad"]},"1":{"status":"qualified_editable","errors":[]}}}')
        with self.assertRaises(ValueError):
            tools.check_report(p, 1)

    def test_success_requires_complete_selected_items(self):
        p = self.report({"mode": "editable-delivery", "package_item_count": 1,
                         "editable_qualified_count": 1, "errors": [], "items": {}})
        with self.assertRaises(ValueError):
            tools.check_report(p, 1)

    def test_old_mode_cannot_admit_editable_delivery(self):
        p = self.report({"mode": "historical-evidence", "package_item_count": 1,
                         "editable_qualified_count": 1, "errors": [],
                         "items": {"1": {"status": "qualified_editable", "errors": []}}})
        with self.assertRaises(ValueError):
            tools.check_report(p, 1)

    def test_complete_actual_report_is_recognized_without_new_admission(self):
        p = self.report({"mode": "editable-delivery", "package_item_count": 1,
                         "editable_qualified_count": 1, "errors": [],
                         "items": {"1": {"status": "qualified_editable", "errors": []}}})
        self.assertEqual(tools.check_report(p, 1)["actual_qualified_count"], 1)

    def public_spec(self):
        p = self.root / "source.txt"
        p.write_text("hash-bound test bytes\n", encoding="utf-8")
        spec_path = self.root / "files.json"
        tools.dump(spec_path, {"status": "public_filelist_review_complete",
                              "files": [{"source": str(p), "path": "package/source.txt", "sha256": tools.sha(p)}]})
        return p, spec_path

    def test_changed_reviewed_input_is_rejected_before_pack(self):
        source, spec_path = self.public_spec()
        source.write_text("changed bytes")
        out = self.root / "packed"
        with self.assertRaises(ValueError):
            tools.pack_cas(spec_path, out)
        self.assertFalse(out.exists())

    def test_duplicate_and_escaping_destinations_are_rejected(self):
        _, spec_path = self.public_spec()
        value = tools.load(spec_path)
        value["files"].append(dict(value["files"][0]))
        tools.dump(spec_path, value)
        with self.assertRaises(ValueError):
            tools.pack_cas(spec_path, self.root / "duplicate")
        for name in ("../escape", "/absolute", "same//path", "."):
            with self.subTest(name=name), self.assertRaises(ValueError):
                tools.relative(name)

    def packed(self):
        _, spec_path = self.public_spec()
        result = tools.pack_cas(spec_path, self.root / "packed")
        return Path(result["manifest"]), result["manifest_sha256"]

    def test_zip_members_have_real_regular_file_type_and_restore_roundtrip(self):
        manifest, pin = self.packed()
        value = tools.load(manifest)
        with zipfile.ZipFile(manifest.parent / value["archive_name"]) as z:
            self.assertTrue(all(stat.S_ISREG(i.external_attr >> 16) for i in z.infolist()))
        helper = REPO / "handoff/materials/restore_history.py"
        result = tools.verify_cas(manifest, pin, helper, tools.sha(helper), self.root / "restored")
        self.assertEqual(result["paths"], 1)
        self.assertEqual((self.root / "restored/package/source.txt").read_text(), "hash-bound test bytes\n")

    def test_wrong_external_pin_writes_no_destination(self):
        manifest, _ = self.packed()
        out = self.root / "not-created"
        helper = REPO / "handoff/materials/restore_history.py"
        with self.assertRaises(ValueError):
            tools.verify_cas(manifest, "0" * 64, helper, tools.sha(helper), out)
        self.assertFalse(out.exists())

    def test_symlink_destination_is_not_resolved_into_a_writable_target(self):
        manifest, pin = self.packed()
        target = self.root / "actual-target"
        destination = self.root / "requested-link"
        destination.symlink_to(target, target_is_directory=True)
        helper = REPO / "handoff/materials/restore_history.py"
        with self.assertRaises(ValueError):
            tools.verify_cas(manifest, pin, helper, tools.sha(helper), destination)
        self.assertFalse(target.exists())

    def test_existing_destination_is_preserved(self):
        manifest, pin = self.packed()
        destination = self.root / "existing"
        destination.mkdir()
        sentinel = destination / "user.txt"
        sentinel.write_text("retain original")
        helper = REPO / "handoff/materials/restore_history.py"
        with self.assertRaises(ValueError):
            tools.verify_cas(manifest, pin, helper, tools.sha(helper), destination)
        self.assertEqual(sentinel.read_text(), "retain original")


if __name__ == "__main__":
    unittest.main()
