"""Focused synthetic fixtures: no author content, compilation, Git or network."""
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

from prepare_upload_manifest import LINE, prepare, safe_path


class UploadManifestTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.line = self.root / LINE
        self.tid = 'GPDOT261014-TEST-0001'
        self.identity = dict(task_id=self.tid, revision='r001', source_id='doi:test', claim_key='doi:test#1')
        self.job = self.line / 'jobs' / self.tid / 'r001'
        self.pkg = self.job / 'package-root-r001'
        self.delivery = self.line / 'delivery/batch-001'
        self.task_path = self.line / 'group/work/nested/task.json'
        source = 'group/work/source.tex'
        evidence = 'group/work/license.json'
        self.task = dict(self.identity, public_dependency_paths=['group/work/nested/task.json', source, evidence],
                         license={'evidence_path': evidence}, statement_spans=[{'path': source}], proof_spans=[{'path': source}],
                         context_spans=[], assembly={'preamble_spans': [], 'body_spans': [{'path': source}], 'asset_paths': [], 'bibliography_paths': []})
        self.write(self.task_path, self.task)
        self.write(self.line / source, 'author theorem and proof')
        self.write(self.line / evidence, {'name': 'CC BY 4.0'})
        state = dict(self.identity, status='compiled_pending_qa', package='package-root-r001', task_snapshot=f'sources/{self.tid}/prepared-task.json', receipt_root='receipts-root-r001')
        self.write(self.job / 'job-state.json', state)
        self.write(self.pkg / state['task_snapshot'], self.task)
        self.row = dict(self.identity, item_path='items/product.tex', compile_receipt='receipts/compile.json', license_path='licenses/NOTICE.txt', license_evidence_path='licenses/evidence.json', source_files=[{'path': 'sources/source.tex', 'original_path': source}], asset_dependencies=[])
        self.write(self.pkg / 'manifest.json', {'items': [self.row]})
        self.receipt = dict(self.identity, ok=True, pages=1, pdf_path='build-root-r001/product.pdf')
        self.write(self.job / 'visual-qa.json', {'task_id': self.tid, 'result': 'readable', 'pages': 1})
        self.write(self.pkg / 'receipts/compile.json', self.receipt)
        self.write(self.job / 'receipts-root-r001' / (self.tid + '.json'), self.receipt)
        for name in ('source-map.json', 'delivery-evidence.json', f'sources/{self.tid}/provenance.json', f'sources/{self.tid}/content-review.json', 'licenses/evidence.json'):
            self.write(self.pkg / name, {})
        for name in ('licenses/NOTICE.txt', 'sources/source.tex', 'items/product.tex'):
            self.write(self.pkg / name, 'public content')
        self.write(self.job / self.receipt['pdf_path'], b'%PDF-1.4\x00fixture')
        self.item = dict(self.identity, assembly_job=self.job.relative_to(self.root).as_posix(), tex_path=(self.pkg / self.row['item_path']).relative_to(self.root).as_posix(), pdf_path=(self.job / self.receipt['pdf_path']).relative_to(self.root).as_posix())
        self.write(self.delivery / 'ITEMS.jsonl', json.dumps(self.item) + '\n')
        self.write(self.delivery / 'SELECTION.json', {'task_ids': [self.tid]})
        self.write(self.delivery / 'INDEX.md', f'[TeX](../../jobs/{self.tid}/r001/package-root-r001/items/product.tex)')
        with sqlite3.connect(self.delivery / 'corpus.sqlite3') as db:
            db.execute('CREATE TABLE problems (task_id TEXT, state TEXT, tex_path TEXT, pdf_path TEXT)')
            db.execute('INSERT INTO problems VALUES (?,?,?,?)', (self.tid, 'prepared_unpublished', self.item['tex_path'], self.item['pdf_path']))
        self.write(self.line / 'operations/run.sh', '#!/bin/sh\ntrue\n')

    def write(self, path, value):
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(value, bytes):
            path.write_bytes(value)
        else:
            path.write_text(value if isinstance(value, str) else json.dumps(value))

    def test_exact_recursive_original_and_minimal_products(self):
        self.write(self.job / 'build-root-r001/product.aux', 'discard')
        self.write(self.job / 'qa-root-r001/page.png', b'discard')
        self.write(self.line / '.work/private.txt', 'discard')
        self.write(self.line / 'operations/__pycache__/run.pyc', b'discard')
        result = prepare(self.root)
        paths = {f['path'] for f in result['files']}
        self.assertEqual(result['selected_count'], 1)
        self.assertIn(self.task_path.relative_to(self.root).as_posix(), paths)
        self.assertFalse(any('.aux' in p or '/qa-' in p or '/.work/' in p or '__pycache__' in p for p in paths))
        self.assertEqual(next(f for f in result['files'] if f['path'] == self.item['pdf_path'])['encoding'], 'base64')
        self.assertEqual(result['total_bytes'], sum(f['bytes'] for f in result['files']))
        self.assertEqual(prepare(self.root), result)

    def test_duplicate_original_fails(self):
        self.write(self.line / 'elsewhere/task.json', self.task)
        with self.assertRaisesRegex(ValueError, 'exactly one original'):
            prepare(self.root)

    def test_missing_whitelist_fails(self):
        del self.task['public_dependency_paths']
        self.write(self.task_path, self.task)
        with self.assertRaisesRegex(ValueError, 'explicit public whitelist'):
            prepare(self.root)

    def test_unlisted_dependency_fails(self):
        self.task['public_dependency_paths'].remove('group/work/source.tex')
        self.write(self.task_path, self.task)
        with self.assertRaisesRegex(ValueError, 'not publicly whitelisted'):
            prepare(self.root)

    def test_missing_selected_file_fails(self):
        (self.root / self.item['pdf_path']).unlink()
        with self.assertRaisesRegex(ValueError, 'Missing file'):
            prepare(self.root)

    def test_bad_paths_even_if_whitelisted_fail(self):
        for value in ('../foreign/file.tex', '/etc/passwd', '.work/a.tex', 'private/a.tex', 'tmp/a.tex', 'nonredistributable/a.tex', 'qa-root-r001/a.png', 'build/a.aux'):
            with self.subTest(path=value), self.assertRaises(ValueError):
                safe_path(self.line, value)

    def test_symlink_fails(self):
        (self.line / 'group/work/source.tex').unlink()
        (self.line / 'group/work/source.tex').symlink_to(self.task_path)
        with self.assertRaisesRegex(ValueError, 'Symlink'):
            prepare(self.root)

    def test_selection_count_mismatch_fails(self):
        self.write(self.delivery / 'SELECTION.json', {'task_ids': [self.tid, self.tid]})
        with self.assertRaisesRegex(ValueError, 'unique tasks'):
            prepare(self.root)

    def test_cross_line_product_fails(self):
        self.item['assembly_job'] = 'research-line/another/jobs/item/r001'
        self.write(self.delivery / 'ITEMS.jsonl', json.dumps(self.item))
        with self.assertRaisesRegex(ValueError, 'unexpected job path'):
            prepare(self.root)

    def test_failed_receipt_fails(self):
        self.receipt['ok'] = False
        self.write(self.pkg / 'receipts/compile.json', self.receipt)
        with self.assertRaisesRegex(ValueError, 'invalid compile receipt'):
            prepare(self.root)

    def test_missing_visual_qa_fails(self):
        (self.job / 'visual-qa.json').unlink()
        with self.assertRaisesRegex(ValueError, 'Missing file.*visual-qa'):
            prepare(self.root)

    def test_failed_visual_qa_fails(self):
        for patch in ({'result': 'unreadable'}, {'task_id': 'OTHER'}, {'pages': 0}, {'pages': True}, {'pages': 2}):
            visual = dict(task_id=self.tid, result='readable', pages=1)
            visual.update(patch)
            self.write(self.job / 'visual-qa.json', visual)
            with self.subTest(patch=patch), self.assertRaisesRegex(ValueError, 'visual QA'):
                prepare(self.root)

    def test_unselected_sqlite_row_fails(self):
        with sqlite3.connect(self.delivery / 'corpus.sqlite3') as db:
            db.execute("INSERT INTO problems VALUES ('OTHER','excluded','','')")
        with self.assertRaisesRegex(ValueError, 'Whole SQLite'):
            prepare(self.root)

    def test_unselected_index_link_fails(self):
        self.write(self.delivery / 'INDEX.md', '[private](../../private/file.pdf)')
        with self.assertRaisesRegex(ValueError, 'INDEX link'):
            prepare(self.root)

    def test_secret_fails(self):
        self.write(self.line / 'group/work/source.tex', 'sk-' + 'a' * 30)
        with self.assertRaisesRegex(ValueError, 'Possible secret'):
            prepare(self.root)


if __name__ == '__main__':
    unittest.main()
