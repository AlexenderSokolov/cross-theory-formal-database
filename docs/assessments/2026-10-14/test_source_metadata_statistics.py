"""Small metadata-only regression tests; no corpus compile or source-text reads."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest


HELPER = Path(__file__).with_name("source_metadata_statistics.py")
if HELPER.exists():
    spec = importlib.util.spec_from_file_location("source_metadata_statistics", HELPER)
    stats = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(stats)
else:
    stats = None


def row(source_id, source_url="", **extra):
    return {"problem_id": "1", "source_id": source_id,
            "source_url": source_url, "author": "Credit", **extra}


class MetadataStatisticsTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(stats, "The read-only statistics helper has not been implemented")

    def test_work_ids_strip_arxiv_versions_and_casefold_doi(self):
        self.assertEqual(stats.canonical_work(row("arxiv:2402.11616v3")),
                         "arxiv:2402.11616")
        self.assertEqual(stats.canonical_work(row("doi:10.3842/SIGMA.2015.034")),
                         "doi:10.3842/sigma.2015.034")

    def test_source_id_doi_wins_over_pdf_download_url(self):
        material = row("doi:10.5802/afst.1805",
                       "https://afst.centre-mersenne.org/articles/10.5802/afst.1805.pdf")
        self.assertEqual(stats.canonical_work(material), "doi:10.5802/afst.1805")
        self.assertEqual(stats.canonical_work(row("publisher-record", material["source_url"])),
                         "doi:10.5802/afst.1805")

    def test_book_and_project_grouping_keeps_chapter_locators_distinct(self):
        a = "stacks-project:morphisms.tex:local-snapshot-20261012"
        b = "stacks-project:stacks-morphisms.tex:local-snapshot-20261012"
        self.assertEqual(stats.canonical_work(row(a)), stats.canonical_work(row(b)))
        self.assertNotEqual(stats.source_locator_identity(a), stats.source_locator_identity(b))
        self.assertIn("stacks-morphisms.tex", stats.source_locator_identity(b))
        for source_id, expected in [("hott-book:commit", "work:HoTT-book"),
                                    ("openlogic:chapter:revision", "work:OpenLogic"),
                                    ("aljabr2:commit:293", "work:AlJabr-2")]:
            self.assertEqual(stats.canonical_work(row(source_id)), expected)

    def test_explicit_same_row_doi_arxiv_aliases_merge_without_title_matching(self):
        rows = [row("doi:10.19086/da.1", "https://arxiv.org/pdf/2301.00001v2"),
                row("arxiv:2301.00001v3"), row("doi:10.19086/da.2", title="Same title"),
                row("arxiv:2301.00002v1", title="Same title")]
        result = stats.statistics(rows, "a" * 40)
        self.assertEqual(result["explicit_alias_row_count"], 1)
        self.assertEqual(result["explicit_alias_pair_count"], 1)
        self.assertEqual(result["strata"]["all"]["raw_source_ids"], 4)
        self.assertEqual(result["strata"]["all"]["normalized_work_ids"], 3)
        self.assertEqual(result["strata"]["all"]["top10_works"][0], ["doi:10.19086/da.1", 2])
        self.assertEqual(result["strata"]["all"]["family_counts"],
                         {"DOI 10.19086": 2, "arXiv": 2})

    def test_primary_and_source_entry_tags_are_separate_from_reference_tags(self):
        rows = [row("stacks-project:a.tex@hash", primary={"tag_url":
                    "https://stacks.math.columbia.edu/tag/000A"},
                    external_prerequisite_references=["https://stacks.math.columbia.edu/tag/000A",
                                                      "https://stacks.math.columbia.edu/tag/000B"]),
                row("stacks-project:b.tex:local-snapshot-20261012",
                    "https://stacks.math.columbia.edu/tag/000C", policy="reviewed-revision-v2",
                    primary=[{"label": "000D"}], review_state="current", authors=["Collective credit"])]
        result = stats.statistics(rows, "a" * 40)["strata"]
        self.assertEqual(result["legacy"]["stacks_explicit_primary_tag_rows"], 1)
        self.assertEqual(result["legacy"]["stacks_unique_explicit_tags"], 2)
        self.assertEqual(result["legacy"]["stacks_tag_reference_count"], 2)
        self.assertEqual(result["prepared"]["stacks_explicit_primary_tag_rows"], 0)
        self.assertEqual(result["prepared"]["stacks_primary_tag_unknown_rows"], 1)
        self.assertEqual(result["prepared"]["stacks_source_entry_tag_rows"], 1)
        self.assertEqual(result["prepared"]["stacks_distinct_source_entry_tags"], 1)
        self.assertEqual(result["prepared"]["review_state_counts"], {"current": 1})

    def test_top_counts_use_canonical_id_tie_break_and_year_is_only_id_proxy(self):
        rows = [row("arxiv:2402.00002v2"), row("arxiv:2402.00001v1"),
                row("doi:10.5802/jep.1", source_version="published 1990", retrieved_at="2026-01-01")]
        result = stats.statistics(rows, "a" * 40)["strata"]["all"]
        self.assertEqual(result["top10_works"][:2], [["arxiv:2402.00001", 1], ["arxiv:2402.00002", 1]])
        self.assertEqual(result["arxiv_identifier_year_counts"], {"2024": 2})
        self.assertEqual(result["structured_publication_year_rows"], 0)

    def test_authors_correction_sensitivity_does_not_reclassify_source_or_mutate_rows(self):
        conflict = row("doi:10.5802/jep.177", "https://jep.centre-mersenne.org/articles/10.5802/jep.177/",
                       problem_id="900000403", author="Charles Boubel; Nicolas Juillet",
                       authors=["The Univalent Foundations Program"], policy="reviewed-revision-v2")
        rows = [conflict, row("hott-book:commit", authors=["The Univalent Foundations Program"],
                             policy="reviewed-revision-v2"),
                row("doi:10.5802/jep.178", authors=["Charles Boubel", "Nicolas Juillet"],
                    policy="reviewed-revision-v2")]
        before = copy.deepcopy(rows)
        result = stats.statistics(rows, "a" * 40)
        self.assertEqual(rows, before)
        self.assertEqual(result["strata"]["prepared"]["unique_explicit_authors_list_strings"], 3)
        sensitivity = result["metadata_conflict_900000403_sensitivity"]
        self.assertTrue(sensitivity["source_counts_unchanged"])
        self.assertEqual(sensitivity["unique_explicit_authors_list_strings_before"], 3)
        self.assertEqual(sensitivity["unique_explicit_authors_list_strings_after"], 3)

    def test_cli_reads_fixed_git_snapshot_and_leaves_worktree_untouched(self):
        # Integration read of the audit snapshot, without fixture commits,
        # staging, corpus edits, or traversal of proof/source files.
        repo = HELPER.parents[3]
        snapshot = "41b4ab870b5b24d235c74e7123bccba6d9b9b042"
        manifest = repo / "editable-corpus" / "manifest.json"
        def status():
            return subprocess.check_output(["git", "-C", str(repo), "status", "--porcelain"], text=True)
        before_status, before_bytes = status(), manifest.read_bytes()
        process = subprocess.run([sys.executable, "-X", "utf8", str(HELPER),
                                  "--repo", str(repo), "--snapshot", snapshot],
                                 capture_output=True, text=True,
                                 env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        self.assertEqual(process.returncode, 0, process.stderr)
        result = json.loads(process.stdout)
        self.assertEqual(result["snapshot"], snapshot)
        self.assertEqual(result["strata"]["all"]["materials"], 19789)
        self.assertEqual(process.stderr, "")
        self.assertEqual(status(), before_status)
        self.assertEqual(manifest.read_bytes(), before_bytes)

    def test_cli_rejects_non_full_snapshot_before_git(self):
        process = subprocess.run([sys.executable, "-X", "utf8", str(HELPER),
                                  "--repo", "nonexistent-repo", "--snapshot", "HEAD"],
                                 capture_output=True, text=True)
        self.assertEqual(process.returncode, 2)
        self.assertIn("40", process.stderr)
        self.assertEqual(process.stdout, "")


if __name__ == "__main__":
    unittest.main()
