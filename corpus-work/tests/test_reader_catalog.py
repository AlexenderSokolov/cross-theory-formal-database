"""Reader-facing catalog contracts, independent of generator implementation."""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import re
import sys
import tempfile
import unittest
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "reader_catalog_under_test", ROOT / "editable-corpus" / "reader_catalog.py"
)
reader_catalog = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(reader_catalog)


def problem_records(value):
    """Inspect records, regardless of the documented page envelope shape."""
    if isinstance(value, dict):
        if "problem_id" in value:
            yield value
        else:
            for child in value.values():
                yield from problem_records(child)
    elif isinstance(value, list):
        for child in value:
            yield from problem_records(child)


def markdown_links(files, corpus):
    for name, text in files.items():
        if not name.endswith(".md"):
            continue
        for destination in re.findall(r"\]\(([^\s)]+)\)", text):
            destination = destination.strip("<>")
            parsed = urlsplit(destination)
            if not parsed.scheme and not parsed.netloc and parsed.path:
                yield name, destination, (
                    corpus / name
                ).parent.joinpath(unquote(parsed.path)).resolve()


class ReaderCatalogTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.corpus = Path(self.temporary.name) / "editable-corpus"
        self.corpus.mkdir()

    def save(self, name, text):
        path = self.corpus / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def fixture(self, count=1):
        rows = []
        for number in range(count):
            ident = f"{number + 1:03d}"
            native = number % 3 == 0
            row = {
                "problem_id": ident,
                "title": f"Author theorem {ident} — 代数与几何",
                "author": "Human Author",
                "source_id": "author-work",
                "source_version": "fixed-version-1",
                "source_url": "https://example.org/paper?v=1&part=proof",
                "item_path": (
                    f"lean/entries/{ident}/entry.json"
                    if native else f"items/{ident}_author.tex"
                ),
                "difficulty_level": "H2",
                "status": "complete_author_material" if native else "verified_editable_tex",
                "unknown_original_field": {"must_remain": [ident]},
            }
            if native:
                row["material_format"] = "native_lean"
            rows.append(row)
        manifest = {
            "verified_count": count,
            "items": list(reversed(rows)),
            "unknown_manifest_field": {"retain": True},
        }
        catalog = {
            "schema_version": 2,
            "count": count + 1,
            "unknown_catalog_field": {"retain": [1, 2, 3]},
            "items": [
                {
                    "problem_id": row["problem_id"],
                    "title": "OUTDATED CATALOG TITLE",
                    "collection_state": "retained_material",
                    "difficulty_state": "not_reassessed",
                    "unknown_catalog_row_field": {"retain": row["problem_id"]},
                }
                for row in rows
            ] + [{"problem_id": "retired-999", "title": "RETIRED SHOULD NOT APPEAR"}],
        }
        return manifest, catalog

    def rendered(self, manifest, catalog):
        result = reader_catalog.render_reader_files(self.corpus, manifest, catalog)
        self.assertIsInstance(result, dict)
        for name, text in result.items():
            self.assertIsInstance(name, str)
            self.assertIsInstance(text, str)
        return result

    def page_jsons(self, files):
        return {
            name: json.loads(text)
            for name, text in files.items()
            if re.fullmatch(r"browse/(tex|lean)/\d+\.json", name)
        }

    def assert_bounded_pages(self, files):
        for name in files:
            if re.fullmatch(r"browse/(tex|lean)/\d+\.(?:md|json)", name):
                self.assertLessEqual(len(files[name].encode("utf-8")), 64 * 1024, name)

    def test_partitioned_pages_cover_active_ids_once_and_keep_string_ids(self):
        manifest, catalog = self.fixture(340)
        before = copy.deepcopy((manifest, catalog))
        files = self.rendered(manifest, catalog)
        required = {
            "INDEX.md", "CORPUS_INDEX.md", "README.md", "browse/README.md",
            "browse/summary.json", "browse/tex/README.md", "browse/lean/README.md",
            "browse/sources.md",
        }
        self.assertTrue(required <= set(files))
        summary = json.loads(files["browse/summary.json"])
        self.assertEqual(summary["material_count"], 340)
        self.assertEqual(summary["format_counts"], {"tex": 226, "lean": 114})
        self.assertTrue(summary["pages"])
        expected = {row["problem_id"] for row in manifest["items"]}
        seen = []
        display = []
        for name, page in self.page_jsons(files).items():
            paired = name.removesuffix(".json") + ".md"
            self.assertIn(paired, files)
            rows = list(problem_records(page))
            self.assertGreater(len(rows), 0, name)
            self.assertLessEqual(len(rows), 100, name)
            for row in rows:
                self.assertIsInstance(row["problem_id"], str)
                seen.append(row["problem_id"])
                if "display_index" in row:
                    display.append(row["display_index"])
        self.assertEqual(set(seen), expected)
        self.assertEqual(len(seen), len(expected))
        self.assertIn("001", seen)
        if display:
            self.assertEqual(sorted(display), list(range(1, 341)))
        summary_ids = []
        for page in summary["pages"]:
            self.assertIn(page["path"], files)
            self.assertIn(page["json_path"], files)
            self.assertEqual(page["path"].removesuffix(".md") + ".json", page["json_path"])
            page_ids = [row["problem_id"] for row in problem_records(json.loads(files[page["json_path"]]))]
            self.assertEqual(page["count"], len(page_ids))
            summary_ids.extend(page_ids)
        self.assertEqual(set(summary_ids), expected)
        self.assertEqual(len(summary_ids), len(expected))
        self.assertNotIn("OUTDATED CATALOG TITLE", "\n".join(files.values()))
        self.assertNotIn("RETIRED SHOULD NOT APPEAR", "\n".join(files.values()))
        self.assertIn("not_reassessed", "\n".join(files.values()))
        self.assertLess(len(files["INDEX.md"].encode("utf-8")), 64 * 1024)
        self.assert_bounded_pages(files)
        self.assertEqual((manifest, catalog), before)

    def test_encoded_paths_open_original_entry_reader_and_exact_proof_lines(self):
        manifest, catalog = self.fixture()
        row = manifest["items"][0]
        root = "lean/works/Author%20source with space"
        row["item_path"] = "lean/entries/A%20B with space/entry.json"
        row["work_ref"] = {"work_key": "published-author-work"}
        row["proof_spans"] = [{"path": "src/Proof with %.lean", "start_line": 7, "end_line": 12}]
        explicit_reader = root + "/readers/author %.pdf"
        row["materials"] = [{"reader_path": explicit_reader}]
        registry = {
            "work_key": "published-author-work", "root": root, "state": "published",
            "material_format": "native_lean", "source_id": "author-work",
            "source_version": "fixed-version-1",
            "files": ["src/Proof with %.lean", "readers/author %.pdf"],
        }
        self.save("work-registry.jsonl", json.dumps(registry) + "\n")
        entry = self.save(row["item_path"], "{}\n")
        proof = self.save(root + "/src/Proof with %.lean", "-- author lines\n" * 20)
        reader = self.save(explicit_reader, "%PDF fixture, do not compile\n")
        files = self.rendered(manifest, catalog)
        links = list(markdown_links(files, self.corpus))
        destinations = {target for _, _, target in links}
        self.assertIn(entry.resolve(), destinations)
        self.assertIn(proof.resolve(), destinations)
        self.assertIn(reader.resolve(), destinations)
        proof_links = [url for _, url, target in links if target == proof.resolve()]
        self.assertTrue(any(url.endswith("#L7-L12") for url in proof_links))
        entry_links = [url for _, url, target in links if target == entry.resolve()]
        self.assertTrue(any("A%2520B%20with%20space" in url for url in entry_links))
        self.assertIn(row["source_url"], "\n".join(files.values()))

    def test_missing_reader_is_not_invented_and_unpublished_work_is_not_linked(self):
        manifest, catalog = self.fixture()
        row = manifest["items"][0]
        row["work_ref"] = {"work_key": "unpublished"}
        row["proof_spans"] = [{"path": "Missing.lean", "start_line": 2, "end_line": 4}]
        self.save("work-registry.jsonl", json.dumps({
            "work_key": "unpublished", "state": "unresolved", "root": None,
            "material_format": "native_lean",
        }) + "\n")
        files = self.rendered(manifest, catalog)
        links = list(markdown_links(files, self.corpus))
        self.assertFalse(any(".pdf" in url for _, url, _ in links))
        self.assertFalse(any("Missing.lean" in url for _, url, _ in links))

    def test_legacy_preparation_span_needs_an_explicit_registered_source_alias(self):
        manifest, catalog = self.fixture()
        row = manifest["items"][0]
        root = "lean/works/registered-author"
        old_span_path = "prepared-jobs/prior-task/r001/package/source/Main.lean"
        canonical_path = "originals/Main.lean"
        row["work_ref"] = {"work_key": "fixed-registered-author"}
        row["proof_spans"] = [{"path": old_span_path, "start_line": 11, "end_line": 21}]
        registry = {
            "work_key": "fixed-registered-author", "root": root, "state": "published",
            "material_format": "native_lean", "source_id": row["source_id"],
            "source_version": row["source_version"], "files": [canonical_path],
        }
        entry = self.save(row["item_path"], "{}\n").resolve()
        canonical = self.save(root + "/" + canonical_path, "-- author original\n" * 25).resolve()
        self.save("work-registry.jsonl", json.dumps(registry) + "\n")
        unaliased = self.rendered(manifest, catalog)
        unaliased_links = list(markdown_links(unaliased, self.corpus))
        self.assertIn(entry, {target for _, _, target in unaliased_links})
        self.assertNotIn(canonical, {target for _, _, target in unaliased_links})
        self.assertFalse(any(target.suffix == ".lean" for _, _, target in unaliased_links))
        self.assertFalse(any(old_span_path in url for _, url, _ in unaliased_links))
        registry["path_aliases"] = {old_span_path: canonical_path}
        self.save("work-registry.jsonl", json.dumps(registry) + "\n")
        aliased = self.rendered(manifest, catalog)
        aliased_links = list(markdown_links(aliased, self.corpus))
        self.assertIn(entry, {target for _, _, target in aliased_links})
        proof_links = [url for _, url, target in aliased_links if target == canonical]
        self.assertTrue(any(url.endswith("#L11-L21") for url in proof_links))
        self.assertFalse(any(old_span_path in url for _, url, _ in aliased_links))

    def test_duplicate_manifest_id_is_rejected(self):
        manifest, catalog = self.fixture()
        manifest["items"].append(copy.deepcopy(manifest["items"][0]))
        with self.assertRaises(ValueError):
            self.rendered(manifest, catalog)

    def test_parent_path_never_becomes_an_outside_link(self):
        manifest, catalog = self.fixture()
        manifest["items"][0]["item_path"] = "../outside.tex"
        try:
            files = self.rendered(manifest, catalog)
        except ValueError:
            return
        bad = [url for _, url, target in markdown_links(files, self.corpus)
               if target.name == "outside.tex" and not target.is_relative_to(self.corpus)]
        self.assertEqual(bad, [])

    def test_oversized_display_title_is_bounded_without_changing_canonical_title(self):
        manifest, catalog = self.fixture(3)
        giant_title = "极长作者题名|with [Markdown](text) 和空格 " * 5000
        manifest["items"][0]["title"] = giant_title
        before = copy.deepcopy((manifest, catalog))
        files = self.rendered(manifest, catalog)
        self.assert_bounded_pages(files)
        self.assertTrue(self.page_jsons(files))
        self.assertEqual((manifest, catalog), before)
        self.assertEqual(manifest["items"][0]["title"], giant_title)

    def test_render_is_read_only_and_write_preserves_originals(self):
        manifest, catalog = self.fixture(4)
        originals = {
            "manifest.json": json.dumps(manifest, ensure_ascii=False),
            "catalog.json": json.dumps(catalog, ensure_ascii=False),
            "work-registry.jsonl": "",
            "items/author_original.tex": "author original, preserve exact bytes\n",
            "unknown-retained.txt": "unknown retained file\n",
        }
        for name, text in originals.items():
            self.save(name, text)
        before_files = {path.relative_to(self.corpus).as_posix(): path.read_bytes()
                        for path in self.corpus.rglob("*") if path.is_file()}
        before_values = copy.deepcopy((manifest, catalog))
        files = self.rendered(manifest, catalog)
        self.assertEqual(files, self.rendered(manifest, catalog))
        after_render = {path.relative_to(self.corpus).as_posix(): path.read_bytes()
                        for path in self.corpus.rglob("*") if path.is_file()}
        self.assertEqual(after_render, before_files)
        written = reader_catalog.write_reader_catalog(self.corpus, manifest, catalog)
        self.assertEqual(set(written), set(files))
        for name, text in files.items():
            self.assertEqual((self.corpus / name).read_bytes(), text.encode("utf-8"))
        for name, content in before_files.items():
            self.assertEqual((self.corpus / name).read_bytes(), content, name)
        self.assertEqual((manifest, catalog), before_values)

    def test_empty_corpus_has_a_usable_zero_count_entry(self):
        manifest, catalog = self.fixture(0)
        files = self.rendered(manifest, catalog)
        summary = json.loads(files["browse/summary.json"])
        self.assertEqual(summary["material_count"], 0)
        self.assertEqual(summary["format_counts"], {"tex": 0, "lean": 0})
        self.assertEqual(summary["pages"], [])
        self.assertIn("INDEX.md", files)

    def test_normal_projection_preserves_review_metadata_and_stages_every_reader_page(self):
        original_path = list(sys.path)
        try:
            sys.path.insert(0, str(ROOT / "editable-corpus"))
            spec = importlib.util.spec_from_file_location(
                "prepared_retirements_reader_test", ROOT / "editable-corpus" / "prepared_retirements.py"
            )
            projection = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(projection)
        finally:
            sys.path[:] = original_path
        manifest, catalog = self.fixture(4)
        for row in manifest["items"]:
            if row.get("material_format") == "native_lean":
                row["native_material"] = {
                    "toolchain": "leanprover/lean4:v4.19.0",
                    "build_status": "not_run",
                    "author_completion_status": "author_complete",
                }
        historical_time = "2026-10-08T08:21:49+0800"
        catalog["generated_at"] = historical_time
        catalog["items"][0]["human_review_annotation"] = {
            "reviewer": "math collaborator", "notes": ["preserve this prior judgment"]
        }
        before = copy.deepcopy((manifest, catalog))
        projected = projection.write_active_indexes(self.corpus, manifest, catalog)
        generated = {path.relative_to(self.corpus).as_posix(): path.read_bytes()
                     for path in self.corpus.rglob("*") if path.is_file()}
        allowed = set(projection.active_index_files(self.corpus, manifest, projected))
        self.assertEqual(set(generated), allowed)
        self.assertTrue(any(re.fullmatch(r"browse/lean/\d+\.md", name) for name in allowed))
        self.assertTrue(any(re.fullmatch(r"browse/tex/\d+\.json", name) for name in allowed))
        saved_catalog = json.loads(generated["catalog.json"])
        self.assertEqual(saved_catalog["historical_catalog_generated_at"], historical_time)
        self.assertNotEqual(saved_catalog.get("generated_at"), historical_time)
        self.assertEqual(saved_catalog["unknown_catalog_field"], catalog["unknown_catalog_field"])
        by_id = {row["problem_id"]: row for row in saved_catalog["items"]}
        prior_row = catalog["items"][0]
        self.assertEqual(by_id[prior_row["problem_id"]]["human_review_annotation"],
                         prior_row["human_review_annotation"])
        self.assertEqual(set(by_id), {row["problem_id"] for row in manifest["items"]})
        self.assertEqual((manifest, catalog), before)
        repeated = projection.write_active_indexes(self.corpus, manifest, projected)
        regenerated = {path.relative_to(self.corpus).as_posix(): path.read_bytes()
                       for path in self.corpus.rglob("*") if path.is_file()}
        self.assertEqual(regenerated, generated)
        self.assertEqual(set(projection.active_index_files(self.corpus, manifest, repeated)), allowed)

    def test_previous_reader_pages_become_noncurrent_without_showing_old_material(self):
        manifest, catalog = self.fixture(3)
        stale_md = "browse/tex/099.md"
        stale_json = "browse/tex/099.json"
        catalog["reader_files"] = [stale_md, stale_json]
        self.save(stale_md, "# STALE AUTHOR PROOF MUST DISAPPEAR\n\n| 999999 | obsolete item |\n")
        self.save(stale_json, json.dumps([{
            "problem_id": "999999", "title": "STALE AUTHOR PROOF MUST DISAPPEAR"
        }]))
        before = copy.deepcopy((manifest, catalog))
        files = self.rendered(manifest, catalog)
        self.assertIn(stale_md, files.keys())
        self.assertIn(stale_json, files.keys())
        self.assertNotIn("STALE AUTHOR PROOF MUST DISAPPEAR", files[stale_md] + files[stale_json])
        self.assertNotIn("999999", files[stale_md] + files[stale_json])
        self.assertEqual(list(problem_records(json.loads(files[stale_json]))), [])
        self.assertTrue(any(word in files[stale_md].lower()
                            for word in ("当前", "过期", "noncurrent", "no longer", "stale")))
        summary = json.loads(files["browse/summary.json"])
        summary_paths = {value for page in summary["pages"] for value in
                         (page["path"], page["json_path"])}
        self.assertNotIn(stale_md, summary_paths)
        self.assertNotIn(stale_json, summary_paths)
        written = reader_catalog.write_reader_catalog(self.corpus, manifest, catalog)
        self.assertIn(stale_md, written)
        self.assertIn(stale_json, written)
        self.assertEqual((self.corpus / stale_md).read_bytes(), files[stale_md].encode("utf-8"))
        self.assertEqual((self.corpus / stale_json).read_bytes(), files[stale_json].encode("utf-8"))
        self.assertEqual((manifest, catalog), before)

    def stage_contract(self):
        original_path = list(sys.path)
        try:
            sys.path.insert(0, str(ROOT / "editable-corpus"))
            spec = importlib.util.spec_from_file_location(
                "prepared_publish_reader_test", ROOT / "editable-corpus" / "prepared_publish.py"
            )
            publication = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(publication)
        finally:
            sys.path[:] = original_path
        expected = ["editable-corpus/" + name for name in
                    ["manifest.json", "prepared-database.json", *publication.CONSUMER_HELPERS]]
        legacy = ["editable-corpus/" + name for name in ("INDEX.md", "catalog.json", "catalog.csv")]
        current_indexes = legacy + ["editable-corpus/" + name for name in (
            "README.md", "CORPUS_INDEX.md", "browse/README.md", "browse/summary.json",
            "browse/tex/001.md", "browse/tex/001.json",
        )]
        return publication, expected, current_indexes, legacy

    def create_declared_stage(self, names, missing=None):
        for name in names:
            if name != missing:
                self.save(name.removeprefix("editable-corpus/"), "completed preparation fixture\n")

    def test_recovery_accepts_old_completed_stage_before_new_helper_is_copied(self):
        publication, expected, indexes, legacy = self.stage_contract()
        old_names = [name for name in expected if name != "editable-corpus/reader_catalog.py"] + legacy
        self.create_declared_stage(old_names)
        self.assertFalse((self.corpus / "reader_catalog.py").exists())
        self.assertFalse((self.corpus / "browse/tex/001.md").exists())
        publication.validate_stage_paths(
            self.corpus.parent, old_names + [""], expected, indexes, legacy
        )
        self.assertFalse((self.corpus / "reader_catalog.py").exists())

    def test_recovery_accepts_current_helper_and_nested_reader_pages(self):
        publication, expected, indexes, legacy = self.stage_contract()
        new_names = expected + indexes
        self.create_declared_stage(new_names)
        publication.validate_stage_paths(
            self.corpus.parent, new_names + [""], expected, indexes, legacy
        )
        self.assertTrue((self.corpus / "browse/tex/001.md").is_file())
        self.assertTrue((self.corpus / "browse/tex/001.json").is_file())

    def test_recovery_rejects_extra_paths_and_missing_declared_files(self):
        publication, expected, indexes, legacy = self.stage_contract()
        old_names = [name for name in expected if name != "editable-corpus/reader_catalog.py"] + legacy
        extra_names = old_names + ["editable-corpus/unexpected.txt"]
        self.create_declared_stage(extra_names)
        with self.subTest("unexpected existing file cannot enter the stage whitelist"):
            with self.assertRaises(ValueError):
                publication.validate_stage_paths(
                    self.corpus.parent, extra_names + [""], expected, indexes, legacy
                )
        new_names = expected + indexes
        missing = "editable-corpus/browse/tex/001.json"
        self.create_declared_stage(new_names, missing=missing)
        self.assertFalse((self.corpus / "browse/tex/001.json").exists())
        with self.subTest("a legal declared set still requires every declared file"):
            with self.assertRaises(ValueError):
                publication.validate_stage_paths(
                    self.corpus.parent, new_names + [""], expected, indexes, legacy
                )


if __name__ == "__main__":
    unittest.main()
