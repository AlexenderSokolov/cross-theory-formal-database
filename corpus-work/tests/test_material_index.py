"""Read-only navigation must never renumber or admit corpus materials."""
import json
import importlib.util
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

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
        self.git('init','--quiet')
        self.git('config','core.autocrlf','false')
        self.git('config','user.name','Index fixture')
        self.git('config','user.email','fixture@example.invalid')
        (self.root/'no-hooks').mkdir()
        self.git('config','core.hooksPath',str(self.root/'no-hooks'))

    def git(self,*args):
        return subprocess.check_output(['git','-C',str(self.root),*args],text=True,encoding='utf8',stderr=subprocess.DEVNULL).strip()

    def commit_input(self):
        self.git('add','manifest.json')
        diff = subprocess.run(['git','-C',str(self.root),'diff','--cached','--quiet']).returncode
        if diff:
            self.git('-c','commit.gpgSign=false','commit','--quiet','-m','fixture manifest')
        return self.git('rev-parse','HEAD')

    def run_tool(self, rows, *flags):
        (self.root/'manifest.json').write_text(json.dumps({'items':rows}), encoding='utf8')
        snapshot = self.commit_input()
        return self.invoke(snapshot,*flags)

    def invoke(self,snapshot,*flags):
        result = subprocess.run([sys.executable, '-B', str(TOOL), '--package', str(self.root),
                                 '--snapshot', snapshot, *flags], capture_output=True, text=True,
                                encoding='utf8')
        return result

    def rendered_rows(self):
        pages = sorted((self.root/'material-index').glob('page-*.md'))
        files = pages or [self.root/'MATERIAL_INDEX.md']
        return [line for file in files for line in file.read_text(encoding='utf8').splitlines() if re.match(r'^\| \d+ \|',line)]

    def test_numeric_order_preserves_original_ids_and_continuous_ordinals(self):
        rows = [row(i) for i in ['100000000','1000','999','001']]
        result = self.run_tool(rows)
        self.assertEqual(result.returncode, 0, result.stderr)
        text = (self.root/'MATERIAL_INDEX.md').read_text(encoding='utf8')
        entries = re.findall(r'^\| (\d+) \| ([0-9]+) \|', '\n'.join(self.rendered_rows()), re.M)
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
        text = '\n'.join(self.rendered_rows())
        self.assertIn('A &#124; B C', text)
        self.assertIn('https://example.org/a%28b%29', text)
        self.assertIn('legacy', text)
        self.assertIn(r'review\_state=author\_material\_collection', text)
        self.assertNotIn('qualified', text.lower())
        lines = [l for l in text.splitlines() if re.match(r'^\| \d+ \|',l)]
        self.assertTrue(all(len(l.strip('|').split('|')) == 7 for l in lines))

    def test_check_detects_stale_missing_or_extra_rows_without_overwriting(self):
        rows = [row('001'),row('1000')]
        self.assertEqual(self.run_tool(rows).returncode, 0)
        output = self.root/'material-index/page-001.md'
        good = output.read_bytes()
        self.assertEqual(self.run_tool(rows, '--check').returncode, 0)
        for bad in [good.replace(b'| 2 | 1000 |',b'| 2 | 9999 |'), good+b'| 3 | 9000 | extra |\n']:
            output.write_bytes(bad)
            result = self.run_tool(rows, '--check')
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(output.read_bytes(), bad)
        output.unlink()
        self.assertNotEqual(self.run_tool(rows, '--check').returncode, 0)

    def test_extra_page_is_rejected_without_removing_or_overwriting_it(self):
        rows = [row('001')]
        self.assertEqual(self.run_tool(rows).returncode,0)
        extra = self.root/'material-index/page-999.md'
        extra.write_text('retained old page',encoding='utf8')
        result = self.run_tool(rows,'--check')
        self.assertNotEqual(result.returncode,0)
        self.assertEqual(extra.read_text(), 'retained old page')

    def test_natural_alphanumeric_order_and_unsafe_paths(self):
        result = self.run_tool([row('L10'),row('L2'),row('001')])
        self.assertEqual(result.returncode, 0, result.stderr)
        text = '\n'.join(self.rendered_rows())
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

    def test_source_link_preserves_recorded_exact_tag_locator(self):
        item = row('001')
        item['source_url'] = 'https://stacks.math.columbia.edu/'
        item['primary'] = {'tag_url':'https://stacks.math.columbia.edu/tag/01XF'}
        self.assertEqual(self.run_tool([item]).returncode,0)
        text = '\n'.join(self.rendered_rows())
        self.assertIn('[来源](https://stacks.math.columbia.edu/tag/01XF)',text)

    def test_pagination_is_one_copy_with_global_ordinals_and_correct_relative_links(self):
        rows = [row(str(n)) for n in range(201,0,-1)]
        self.assertEqual(self.run_tool(rows).returncode,0)
        pages = sorted((self.root/'material-index').glob('page-*.md'))
        self.assertEqual([p.name for p in pages],['page-001.md','page-002.md'])
        self.assertEqual(len(self.rendered_rows()),201)
        self.assertTrue(self.rendered_rows()[0].startswith('| 1 | 1 |'))
        self.assertTrue(self.rendered_rows()[-1].startswith('| 201 | 201 |'))
        entry = (self.root/'MATERIAL_INDEX.md').read_text(encoding='utf8')
        self.assertEqual(re.findall(r'^\| \d+ \|',entry,re.M),[],msg='entry must not duplicate material rows')
        self.assertIn('material-index/page-002.md',entry)
        self.assertIn('(../items/201.tex)',pages[-1].read_text(encoding='utf8'))
        self.assertIn('(../MATERIAL_INDEX.md)',pages[-1].read_text(encoding='utf8'))

    def test_duplicate_json_keys_preserve_every_existing_output(self):
        self.assertEqual(self.run_tool([row('001')]).returncode,0)
        old = {p:p.read_bytes() for p in [self.root/'MATERIAL_INDEX.md',*sorted((self.root/'material-index').glob('*.md'))]}
        one = json.dumps(row('1001'))
        duplicate_item = one.replace('"problem_id": "1001"','"problem_id": "001", "problem_id": "1001"')
        for raw in ['{"items":[],"items":['+one+']}', '{"items":['+duplicate_item+']}']:
            (self.root/'manifest.json').write_text(raw,encoding='utf8')
            snapshot = self.commit_input()
            result = self.invoke(snapshot)
            self.assertNotEqual(result.returncode,0)
            self.assertIn('duplicate JSON key',result.stderr)
            self.assertEqual({p:p.read_bytes() for p in old},old)

    def test_snapshot_mismatch_preserves_outputs(self):
        self.assertEqual(self.run_tool([row('001')]).returncode,0)
        snapshot = self.git('rev-parse','HEAD')
        output = self.root/'MATERIAL_INDEX.md'; before = output.read_bytes()
        (self.root/'manifest.json').write_text(json.dumps({'items':[row('002')]}),encoding='utf8')
        result = self.invoke(snapshot)
        self.assertNotEqual(result.returncode,0)
        self.assertIn('snapshot',result.stderr)
        self.assertEqual(output.read_bytes(),before)

    def test_real_math_title_markdown_characters_stay_literal(self):
        titles = [
            'The genus-two SU(2) WRT module at level p=2*r1*r2 is irreducible when r1,r2 are distinct odd primes and the specified even CRT color x satisfies 3*x>p-4',
            "The law of Arratia's random integer J_x^*: P[J_x^* = j] = (1/(j log x))(1 + O(1/log x))",
            r'J_x^* `code` \alpha',
        ]
        for title in titles:
            item = row('1654'); item['title'] = title
            self.assertEqual(self.run_tool([item]).returncode,0)
            cell_text = self.rendered_rows()[0].strip('|').split('|')[2].strip()
            self.assertNotRegex(cell_text,r'(?<!\\)[*`_]')
            # Literal Markdown escaping must preserve the original math spelling.
            import html
            self.assertEqual(html.unescape(re.sub(r'\\([\\*_`\[\]])',r'\1',cell_text)),title)

    def test_directory_at_later_page_preserves_the_complete_old_view(self):
        self.assertEqual(self.run_tool([row('001')]).returncode,0)
        entry = self.root/'MATERIAL_INDEX.md'
        first = self.root/'material-index/page-001.md'
        before = {entry:entry.read_bytes(), first:first.read_bytes()}
        conflict = self.root/'material-index/page-002.md'
        conflict.mkdir()
        result = self.run_tool([row(str(i)) for i in range(1,202)])
        self.assertNotEqual(result.returncode,0)
        self.assertEqual({p:p.read_bytes() for p in before},before)
        self.assertTrue(conflict.is_dir())

    def test_middle_publish_io_failure_restores_all_old_bytes(self):
        self.assertEqual(self.run_tool([row('001')]).returncode,0)
        entry = self.root/'MATERIAL_INDEX.md'
        first = self.root/'material-index/page-001.md'
        before = {entry:entry.read_bytes(),first:first.read_bytes()}
        spec = importlib.util.spec_from_file_location('material_index_publish_test',TOOL)
        module = importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        (self.root/'manifest.json').write_text(json.dumps({'items':[row(str(i)) for i in range(1,202)]}),encoding='utf8')
        snapshot = self.commit_input()
        import os
        replace = os.replace
        failed = []
        def fail_navigation(source,destination):
            if Path(destination)==entry and not failed:
                failed.append(True)
                raise OSError('injected navigation publication failure')
            return replace(source,destination)
        args = ['render_material_index.py','--package',str(self.root),'--snapshot',snapshot]
        with patch.object(os,'replace',side_effect=fail_navigation),patch.object(sys,'argv',args):
            with self.assertRaises(SystemExit) as stopped:
                module.main()
        self.assertNotEqual(stopped.exception.code,0)
        self.assertTrue(failed)
        self.assertEqual({p:p.read_bytes() for p in before},before)
        self.assertFalse((self.root/'material-index/page-002.md').exists())


if __name__ == '__main__':
    unittest.main()
