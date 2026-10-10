"""Focused regression tests for research provenance and fail-closed counting."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "reconcile_research_line.py"
spec = importlib.util.spec_from_file_location("reconcile_research_line", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class ReconcileTests(unittest.TestCase):
    def setUp(self):
        # Keep test evidence; repository policy forbids automatic bulk deletion.
        self.root = Path(tempfile.mkdtemp(prefix="research-reconcile-test-"))
        self.snapshot = self.root / "snapshot"
        (self.snapshot / "items").mkdir(parents=True)
        self.reviews = self.root / "reviews"
        (self.reviews / "finalreview").mkdir(parents=True)
        (self.reviews / "recheck").mkdir()

    def write(self, path, data):
        path.write_text(json.dumps(data), encoding="utf-8")

    def reason(self, pid, level="H2", **extra):
        value = {"difficulty_level": level, "statement_locator": "algebra.tex:1-3",
                 "proof_locator": "algebra.tex:4-9", "difficulty_reason": "fixture", **extra}
        self.write(self.snapshot / "reasons2.json", {"items": {pid: value}, "counted": [pid]})

    def item(self, pid, label="lemma-x"):
        (self.snapshot / "items" / (pid.replace(":", "_") + ".tex")).write_text(
            f"% problem_id: {pid}\n% source_file: algebra.tex\n\\begin{{lemma}}\n\\label{{{label}}}\nX\n", encoding="utf-8")

    def records(self):
        return mod.build_records(self.snapshot, self.reviews, self.root)[0]

    def test_counted_dropped_and_missing_file_cannot_reenter(self):
        pid = "S046-thm:settopos"
        self.reason(pid)
        data = mod.read_json(self.snapshot / "reasons2.json")
        data["dropped"] = [pid]
        self.write(self.snapshot / "reasons2.json", data)
        row = self.records()[0]
        self.assertEqual(row["selection_status"], "pending")
        self.assertEqual(row["difficulty_level"], "H2")  # retain the source decision
        self.assertIn("counted_and_dropped", row["issues"])
        self.assertIn("missing_item_file", row["issues"])

    def test_disagreeing_review_does_not_silently_overwrite(self):
        pid = "S001-lemma-x"
        self.reason(pid, "H3")
        self.item(pid)
        self.write(self.reviews / "finalreview" / "x.json", {"problem_id": pid, "independent_level": "H2"})
        row = self.records()[0]
        self.assertEqual(row["difficulty_level"], "H3")
        self.assertEqual(row["selection_status"], "pending")

    def test_applied_final_decision_supersedes_older_recheck(self):
        pid = "S001-lemma-x"
        self.reason(pid, "H2", level_before_final_review="H3", final_review={"independent_level": "H2"})
        self.item(pid)
        self.write(self.reviews / "recheck" / "x.json", {"problem_id": pid, "new_level": "H3"})
        row = self.records()[0]
        self.assertEqual(row["selection_status"], "counted")
        self.assertEqual(row["previous_levels"], {"level_before_final_review": "H3"})

    def test_primary_overlap_does_not_match_later_context_label(self):
        pid = "S001-lemma-x"
        self.reason(pid)
        self.item(pid)
        main = self.root / "main"
        main.mkdir()
        (main / "primary.tex").write_text("\\label{lemma-different}\nX\n\\label{lemma-x}\n", encoding="utf-8")
        self.write(main / "manifest.json", {"items": [{"problem_id": "101", "source_id": "stacks-project:test",
                    "primary": {"source_file": "algebra.tex", "excerpt_path": "primary.tex"}}]})
        self.assertEqual(mod.primary_overlaps(self.records(), main / "manifest.json", self.root), [])
        (main / "primary.tex").write_text("\\label{lemma-x}\n", encoding="utf-8")
        self.assertEqual(mod.primary_overlaps(self.records(), main / "manifest.json", self.root)[0]["main_problem_id"], "101")

    def test_duplicate_reason_ids_are_rejected(self):
        pid = "S001-lemma-x"
        self.reason(pid)
        self.item(pid)
        self.write(self.snapshot / "reasons3.json", mod.read_json(self.snapshot / "reasons2.json"))
        with self.assertRaisesRegex(ValueError, "Duplicate problem_id"):
            self.records()


if __name__ == "__main__":
    unittest.main()
