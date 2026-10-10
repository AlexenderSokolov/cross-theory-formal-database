"""Current reader catalog must not confuse delivery with content qualification."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
import refresh_catalog as catalog


def item(pid="100008", reason="Specific geometric construction", level="H2"):
    return dict(problem_id=pid, title="Published title", author="Author", work="Work",
                source_id="arxiv:1234.5678v2", source_url="https://arxiv.org/abs/1234.5678v2",
                source_version="v2", license="CC BY 4.0", license_path="licenses/source.txt",
                item_path=f"items/{pid}.tex", tex_sha256="a" * 64,
                difficulty_level=level, difficulty_reason=reason,
                primary={"theorem": "Theorem 1", "start_line": 1, "end_line": 4})


class CatalogTests(unittest.TestCase):
    def test_title_correction_does_not_certify_content(self):
        review = dict(problem_id="100008", review_scope="title", status="confirmed",
                      title="Actual article title", evidence=[{"path": "source.tex", "lines": [1, 2]}])
        row = catalog.make_catalog([item()], [review])["items"][0]
        self.assertEqual(row["title"], "Actual article title")
        self.assertEqual(row["published_title"], "Published title")
        self.assertEqual(row["qualification_status"], "not_reassessed")
        self.assertIsNone(row["confirmed_H"])

    def test_pairing_hold_overrides_published_H(self):
        review = dict(problem_id="100008", review_scope="content", status="hold",
                      difficulty_level=None, issue="Proof belongs to another proposition", evidence=["source:240-296"])
        row = catalog.make_catalog([item()], [review])["items"][0]
        self.assertEqual(row["qualification_status"], "hold")
        self.assertEqual(row["published_H"], "H2")
        self.assertIsNone(row["confirmed_H"])

    def test_unreviewed_research_identity_is_not_difficulty_evidence(self):
        reason = "it is a research contribution of the article in math.AG and is therefore strictly above ordinary PhD qualifying level"
        row = catalog.make_catalog([item(reason=reason)], [])["items"][0]
        self.assertEqual(row["qualification_status"], "needs_review")
        self.assertIn("venue_as_difficulty", row["review_flags"])

    def test_H3_proposal_cannot_be_promoted_without_second_review(self):
        review = dict(problem_id="100008", review_scope="content", status="confirmed",
                      difficulty_level="H3", difficulty_reason="A specific obstruction is resolved here.",
                      review_stage="needs_second_review", evidence=["source:1-40"])
        row = catalog.make_catalog([item()], [review])["items"][0]
        self.assertEqual(row["qualification_status"], "needs_review")
        self.assertIsNone(row["confirmed_H"])

    def test_H3_second_review_must_be_explicit_independent_agreement(self):
        first = dict(problem_id="100008", review_scope="content", status="confirmed",
                     difficulty_level="H3", difficulty_reason="Specific obstruction.",
                     evidence=["source:1-40"], review_stage="completed")
        bad = [True, "pending", {"status": "hold"}, {"status": "needs_review"},
               {"status": "confirmed", "difficulty_level": "H2", "reviewer": "independent", "independent": True, "evidence": ["source:1-40"]}]
        for value in bad:
            with self.subTest(value=value):
                row = catalog.make_catalog([item()], [dict(first, second_review=value)])["items"][0]
                self.assertIsNone(row["confirmed_H"])
        second = dict(status="confirmed", difficulty_level="H3", reviewer="other-agent",
                      independent=True, evidence=["source:1-40"])
        self.assertEqual(catalog.make_catalog([item()], [dict(first, second_review=second)])["items"][0]["confirmed_H"], "H3")
        row = catalog.make_catalog([item()], [dict(first, second_review=second, independent_second_review_completed=False)])["items"][0]
        self.assertIsNone(row["confirmed_H"])

    def test_catalog_has_every_record_license_and_stable_order(self):
        rows = [item("200001"), item("001")]
        original = json.dumps(rows, sort_keys=True)
        result = catalog.make_catalog(rows, [])
        self.assertEqual(result["count"], 2)
        self.assertEqual([x["problem_id"] for x in result["items"]], ["001", "200001"])
        self.assertTrue(all(x["license"] == "CC BY 4.0" for x in result["items"]))
        self.assertEqual(json.dumps(rows, sort_keys=True), original)
        self.assertEqual(result, catalog.make_catalog(rows, []))

    def test_validated_revision_is_linked_without_changing_published_identity(self):
        r = dict(problem_id="100008", review_scope="content", status="confirmed", difficulty_level="H2",
                 difficulty_reason="Repaired author context establishes the remaining obligation.", evidence=["source:1-40"],
                 replacement=dict(item_path="../curation/revisions/100008/items/100008.tex",
                                  pdf_path="../curation/revisions/100008/pdf/100008.pdf",
                                  status="local_validated_not_merged", tex_sha256="b" * 64))
        row = catalog.make_catalog([item(level="H3")], [r])["items"][0]
        self.assertEqual(row["published_H"], "H3")
        self.assertEqual(row["confirmed_H"], "H2")
        self.assertEqual(row["tex_sha256"], "a" * 64)
        self.assertEqual(row["current_item_path"], r["replacement"]["item_path"])
        self.assertEqual(row["current_revision_status"], "local_validated_not_merged")

    def test_research_evidence_is_attached_without_double_counting_or_promotion(self):
        data = catalog.make_catalog([item()], [])
        records = [dict(problem_id="S001-lemma-one", difficulty_level="H3", difficulty_reason="Research-line opinion",
                        selection_status="counted", source_record={"path": "research/reason.json"}, review_evidence=[])]
        catalog.attach_research(data, [dict(main_problem_id="100008", research_id="S001-lemma-one")], records)
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["research_linked_main_count"], 1)
        self.assertEqual(data["items"][0]["qualification_status"], "not_reassessed")
        self.assertIsNone(data["items"][0]["confirmed_H"])
        self.assertEqual(data["items"][0]["research_reviews"][0]["research_id"], "S001-lemma-one")

    def test_unknown_or_duplicate_review_is_rejected(self):
        r = dict(problem_id="999", review_scope="content", status="hold")
        with self.assertRaisesRegex(ValueError, "unknown"):
            catalog.make_catalog([item()], [r])
        r["problem_id"] = "100008"
        with self.assertRaisesRegex(ValueError, "duplicate"):
            catalog.make_catalog([item()], [r, r])

    def test_intervening_proposition_is_detected_but_not_called_invalid(self):
        source = "\\begin{thm}\nA\n\\end{thm}\n\\begin{prop}\nB\n\\end{prop}\n\\begin{proof}\nProof B\n\\end{proof}"
        self.assertEqual(catalog.intervening_statement(source, [1, 3], [7, 9]), ["prop"])
        self.assertEqual(catalog.intervening_statement(source, [4, 6], [7, 9]), [])

    def test_human_catalog_pages_keep_every_id_once(self):
        data = catalog.make_catalog([item(str(100000 + i)) for i in range(501)], [])
        output = catalog.render_outputs(data)
        pages = [text for path, text in output.items() if "/catalog-pages/" in path]
        self.assertEqual(len(pages), 2)
        ids = []
        for text in pages:
            ids.extend(line.split("|")[1].strip() for line in text.splitlines()
                       if line.startswith("| 100"))
        self.assertEqual(len(ids), 501)
        self.assertEqual(len(set(ids)), 501)
        self.assertIn("catalog-pages/001.md", output["editable-corpus/CORPUS_INDEX.md"])

    def test_explicit_model_solution_header_is_flagged_not_AI_topic(self):
        text = "A paper about GPT-4.\n\\begin{proof}[Solution (GPT-4)]\nA solution\n\\end{proof}"
        self.assertEqual(catalog.model_solution_headers(text), [2])
        self.assertEqual(catalog.model_solution_headers("A theorem about GPT-4 training.\n\\begin{proof}\nHuman proof.\n\\end{proof}"), [])


if __name__ == "__main__":
    unittest.main()
