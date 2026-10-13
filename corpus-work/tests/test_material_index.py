"""Read-only navigation must never renumber or admit corpus materials."""
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOL = Path(__file__).resolve().parents[1] / 'tools/render_material_index.py'


def row(ident, **extra):
    return dict(problem_id=ident, title='Item '+ident, difficulty_level='H2',
                item_path='items/'+ident+'.tex', license_path='licenses/'+ident+'.txt',
                source_url='https://example.org/source', status='verified_editable_tex', **extra)


class MaterialIndexTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.original_index = '|001|Existing|H2|[TeX](items/001.tex)|source|\n'
        (self.root/'INDEX.md').write_text(self.original_index, encoding='utf8')

    def run_tool(self, rows, *flags):
        (self.root/'manifest.json').write_text(json.dumps({'items':rows}), encoding='utf8')
        result = subprocess.run([sys.executable, '-B', str(TOOL), '--package', str(self.root),
                                 '--snapshot', '1'*40, *flags], capture_output=True, text=True,
                                encoding='utf8')
        return result

    def test_numeric_order_preserves_original_ids_and_continuous_ordinals(self):
        rows = [row(i) for i in ['100000000','1000','999','001']]
        result = self.run_tool(rows)
        self.assertEqual(result.returncode, 0, result.stderr)
        text = (self.root/'MATERIAL_INDEX.md').read_text(encoding='utf8')
        entries = re.findall(r'^\| (\d+) \| ([0-9]+) \|', text, re.M)
        self.assertEqual(entries, [('1','001'),('2','999'),('3','1000'),('4','100000000')])
        self.assertEqual((self.root/'INDEX.md').read_text(), self.original_index)
        before = (self.root/'MATERIAL_INDEX.md').read_bytes()
        self.assertEqual(self.run_tool(rows).returncode, 0)
        self.assertEqual((self.root/'MATERIAL_INDEX.md').read_bytes(), before)

    def test_duplicate_stable_id_is_rejected_without_output(self):
        result = self.run_tool([row('1001'),row('1001')])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('duplicate', result.stderr)
        self.assertFalse((self.root/'MATERIAL_INDEX.md').exists())

    def test_numeric_alias_is_rejected_without_renaming(self):
        result = self.run_tool([row('1001'),row('01001')])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('numeric alias', result.stderr)
        self.assertFalse((self.root/'MATERIAL_INDEX.md').exists())

    def test_duplicate_item_path_is_rejected(self):
        rows = [row('1001'),row('1002')]
        rows[1]['item_path'] = rows[0]['item_path']
        result = self.run_tool(rows)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('duplicate item path', result.stderr)

    def test_markdown_escaping_and_material_state_do_not_grant_qualification(self):
        rows = [row('001'),row('100000000', policy='reviewed-revision-v2',
                               review_state='author_material_collection',
                               preparation_basis='author_material_collection')]
        rows[1]['title'] = 'A | B\nC'
        rows[1]['source_url'] = 'https://example.org/a(b)'
        result = self.run_tool(rows)
        self.assertEqual(result.returncode, 0, result.stderr)
        text = (self.root/'MATERIAL_INDEX.md').read_text(encoding='utf8')
        self.assertIn('A &#124; B C', text)
        self.assertIn('https://example.org/a%28b%29', text)
        self.assertIn('legacy', text)
        self.assertIn('review_state=author_material_collection', text)
        self.assertNotIn('qualified', text.lower())
        lines = [l for l in text.splitlines() if re.match(r'^\| \d+ \|',l)]
        self.assertTrue(all(len(l.strip('|').split('|')) == 7 for l in lines))

    def test_check_detects_stale_missing_or_extra_rows_without_overwriting(self):
        rows = [row('001'),row('1000')]
        self.assertEqual(self.run_tool(rows).returncode, 0)
        output = self.root/'MATERIAL_INDEX.md'
        good = output.read_bytes()
        self.assertEqual(self.run_tool(rows, '--check').returncode, 0)
        for bad in [good.replace(b'| 2 | 1000 |',b'| 2 | 9999 |'), good+b'| 3 | 9000 | extra |\n']:
            output.write_bytes(bad)
            result = self.run_tool(rows, '--check')
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(output.read_bytes(), bad)
        output.unlink()
        self.assertNotEqual(self.run_tool(rows, '--check').returncode, 0)

    def test_natural_alphanumeric_order_and_unsafe_paths(self):
        result = self.run_tool([row('L10'),row('L2'),row('001')])
        self.assertEqual(result.returncode, 0, result.stderr)
        text = (self.root/'MATERIAL_INDEX.md').read_text(encoding='utf8')
        self.assertLess(text.index('| L2 |'), text.index('| L10 |'))
        bad = row('1000'); bad['item_path'] = '../private.tex'
        self.assertNotEqual(self.run_tool([bad]).returncode, 0)

    def test_check_accepts_checkout_line_endings_without_rewriting(self):
        rows = [row('001')]
        self.assertEqual(self.run_tool(rows).returncode, 0)
        output = self.root/'MATERIAL_INDEX.md'
        checkout_bytes = output.read_bytes().replace(b'\n',b'\r\n')
        output.write_bytes(checkout_bytes)
        result = self.run_tool(rows,'--check')
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(output.read_bytes(),checkout_bytes)


if __name__ == '__main__':
    unittest.main()
