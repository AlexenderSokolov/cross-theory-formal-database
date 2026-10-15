"""Synthetic fixtures only: never compile or modify a production job."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).with_name('format_source_pointers.py')
PREFIX = r'\noindent\textit{Source reference.}'


class SourcePointerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.job = Path(self.temp.name)
        self.package = self.job / 'package-root-r002'
        self.tex = self.package / 'items/test.tex'
        self.tex.parent.mkdir(parents=True)
        self.state = dict(status='assembled', package=self.package.name,
                          build_root='build-root-r002', receipt_root='receipts-root-r002')
        self.save_state()
        (self.package / 'manifest.json').write_text(json.dumps({'items': [
            {'item_path': 'items/test.tex', 'compile_receipt': 'receipts/test.json'}]}))
        self.original = (r'\documentclass{article}' + '\r\n' + PREFIX +
            r' Original theorem 2: group/work/main\_source.tex, source lines 1--9. Reason a/b.' +
            r'\par\medskip' + '\r\n' +
            r'\noindent\textit{Editorial note.} group/work/file.tex' + '\r\n' +
            ' ' + PREFIX + r' Original theorem 2: untouched/path.tex, source lines 1--2.' + '\r\n' +
            r'\begin{theorem} $a/b$; \input{body/path} \end{theorem}' + '\r\n')
        self.tex.write_bytes(self.original.encode())

    def save_state(self):
        (self.job / 'job-state.json').write_text(json.dumps(self.state))

    def run_adapter(self):
        return subprocess.run([sys.executable, str(SCRIPT), '--job', str(self.job)],
                              capture_output=True, text=True)

    def test_only_source_path_changes_and_is_idempotent(self):
        result = self.run_adapter()
        self.assertEqual(result.returncode, 0, result.stderr)
        actual = self.tex.read_bytes()
        expected = self.original.replace('group/work/main',
                                         r'group/\allowbreak{}work/\allowbreak{}main')
        self.assertEqual(actual, expected.encode())
        self.assertEqual(actual.count(b'\n'), self.original.count('\n'))
        self.assertEqual(actual.splitlines()[2:], self.original.encode().splitlines()[2:])
        self.assertEqual(self.run_adapter().returncode, 0)
        self.assertEqual(self.tex.read_bytes(), actual)

    def test_compiled_status_is_rejected_without_edit(self):
        self.state['status'] = 'compiled_pending_qa'
        self.save_state()
        result = self.run_adapter()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('compiled jobs cannot be edited', result.stderr)
        self.assertEqual(self.tex.read_bytes(), self.original.encode())

    def test_compile_run_id_is_rejected_without_edit(self):
        self.state['compile_run_id'] = 'test/r002/compile-001'
        self.save_state()
        result = self.run_adapter()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('compiled jobs cannot be edited', result.stderr)
        self.assertEqual(self.tex.read_bytes(), self.original.encode())

    def test_existing_build_is_rejected_without_edit(self):
        (self.job / self.state['build_root']).mkdir()
        result = self.run_adapter()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('compiled jobs cannot be edited', result.stderr)
        self.assertEqual(self.tex.read_bytes(), self.original.encode())

    def test_existing_receipt_is_rejected_without_edit(self):
        receipt = self.package / 'receipts/test.json'
        receipt.parent.mkdir()
        receipt.write_text('{}')
        result = self.run_adapter()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('compiled jobs cannot be edited', result.stderr)
        self.assertEqual(self.tex.read_bytes(), self.original.encode())


if __name__ == '__main__':
    unittest.main()
