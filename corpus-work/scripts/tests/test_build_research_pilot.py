import importlib.util
import json
import sqlite3
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from contextlib import redirect_stdout, closing
import io

SCRIPTS=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(SCRIPTS))
import stacks_extract as se
import build_research_pilot as pilot


class PilotTests(unittest.TestCase):
    def source(self,root):
        (root/'tags').mkdir()
        (root/'tags/tags').write_text('AAAA,one-lemma-main\n',encoding='utf-8')
        text=('\\begin{lemma}\n\\label{lemma-main} The result.\n\\end{lemma}\n'
              '\\begin{proof}\nThe main construction is written here.\n'
              'First optional calculation is omitted.\n'
              'Second optional calculation is omitted.\n\\end{proof}\n')
        (root/'one.tex').write_text(text,encoding='utf-8')
        return se.StacksSource(root),text

    def reviews(self):
        return [dict(exact_phrase=word+' optional calculation is omitted.',
            scope=word+' explicitly optional calculation',
            why_noncore='The full main construction precedes this optional calculation.',
            source_locator=dict(file='one.tex',lines=[line,line]))
            for word,line in [('First',6),('Second',7)]]

    def test_multiple_bounded_reviews_preserve_original(self):
        with tempfile.TemporaryDirectory() as td:
            source,text=self.source(Path(td))
            record=source.block('AAAA',omitted_detail_review=self.reviews())
            self.assertIn(record['excerpt'],text)
            self.assertIn('First optional calculation is omitted.',record['proof'])
            self.assertIn('Second optional calculation is omitted.',record['proof'])

    def test_unreviewed_omission_still_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            source,_=self.source(Path(td))
            with self.assertRaisesRegex(ValueError,'incomplete proof'):
                source.block('AAAA',omitted_detail_review=self.reviews()[:1])

    def test_wrong_source_locator_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            source,_=self.source(Path(td));reviews=self.reviews()
            reviews[0]['source_locator']['lines']=[7,7]
            with self.assertRaisesRegex(ValueError,'source locator'):
                source.block('AAAA',omitted_detail_review=reviews)

    def test_old_dict_contract_still_supported(self):
        with tempfile.TemporaryDirectory() as td:
            source,text=self.source(Path(td))
            (Path(td)/'one.tex').write_text(text.replace('Second optional calculation is omitted.','Second calculation is written.'),encoding='utf-8')
            record=source.block('AAAA',omitted_detail_review=self.reviews()[0])
            self.assertIn('First optional calculation is omitted.',record['proof'])

    def test_explicit_unknown_version_never_claims_old_pin(self):
        with tempfile.TemporaryDirectory() as td:
            source,_=self.source(Path(td));record=source.block('AAAA',False)
            spec=dict(title='Test',difficulty_level='H2',difficulty_reason='Concrete task',source_version=pilot.VERSION)
            tex=se.render(source,record,spec)
            self.assertIn(pilot.VERSION,tex)
            self.assertNotIn(se.PIN,tex)
            del spec['source_version']
            self.assertIn(se.PIN,se.render(source,record,spec))

    def test_json_writer_preserves_lf_byte_identity(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'receipt.json';pilot.dump(path,{'text':'实际证据'})
            raw=path.read_bytes()
            self.assertNotIn(b'\r',raw)
            self.assertEqual(json.loads(raw),{'text':'实际证据'})

    def test_cli_metadata_uses_explicit_source_version(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);source,text=self.source(root)
            (root/'one.tex').write_text(text.replace(' is omitted',' is fully supplied'),encoding='utf-8')
            (root/'COPYING').write_text('Fixture license notice',encoding='utf-8')
            spec=root/'spec.json';spec.write_text(json.dumps(dict(difficulty_level='H2',difficulty_reason='Concrete task',source_version=pilot.VERSION)),encoding='utf-8')
            out=root/'output'
            with patch.object(sys,'argv',['stacks_extract.py','--source',str(root),'extract','AAAA','--spec',str(spec),'--out-dir',str(out)]),redirect_stdout(io.StringIO()):
                se.main()
            self.assertEqual(json.loads((out/'AAAA.metadata.json').read_text())['source_version'],pilot.VERSION)

    def test_core_pairing_rejects_interposed_unreviewed_prose(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);source,text=self.source(root)
            (root/'one.tex').write_text(text.replace('\\end{lemma}\n','\\end{lemma}\nAnother unlabelled claim follows.\n'),encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'pairing needs explicit review'):
                pilot.full_context(source,'AAAA')

    def test_nested_contexts_do_not_repeat_author_text(self):
        a=dict(file='one.tex',start_line=1,end_line=10)
        b=dict(file='one.tex',start_line=3,end_line=5)
        self.assertEqual(pilot.unique_contexts([b,a]),[a])
        with self.assertRaisesRegex(ValueError,'partially overlapping'):
            pilot.unique_contexts([a,dict(file='one.tex',start_line=9,end_line=14)])

    def test_failed_attempt_cannot_leave_green_manifest_or_sqlite(self):
        with tempfile.TemporaryDirectory() as td:
            package=Path(td);row=dict(problem_id='97000099',status='verified_editable_tex')
            pilot.dump(package/'manifest.json',dict(schema_version=1,verified_count=1,items=[row]))
            pilot.dump(package/'gate-result.json',dict(editable_qualified_count=1,errors=[]))
            pilot.fail_package(SCRIPTS.parents[1],package,'actual compiler failure')
            manifest=json.loads((package/'manifest.json').read_text(encoding='utf-8'))
            self.assertEqual(manifest['verified_count'],0)
            self.assertEqual(manifest['items'],[])
            self.assertEqual(manifest['assembly_state'],'failed')
            self.assertEqual(json.loads((package/'gate-result.json').read_text())['editable_qualified_count'],0)
            ev=json.loads((package/'delivery-evidence.json').read_text())
            self.assertEqual(ev['items'],{})
            self.assertEqual(ev['package_manifest_sha256'],pilot.gate.digest((package/'manifest.json').read_bytes()))
            with closing(sqlite3.connect(package/'corpus.sqlite')) as db:self.assertEqual(db.execute('SELECT COUNT(*) FROM problems').fetchone()[0],0)
            previous=json.loads((package/'failed-candidate.json').read_text())
            self.assertEqual(previous['previous_manifest']['items'][0]['status'],'verified_editable_tex')

    def test_pending_manifest_is_zero_and_material_path_is_relocatable(self):
        self.assertEqual(pilot.package_manifest({'status':'pending'},'pending')['verified_count'],0)
        root=Path('/new-checkout')
        candidate={'research_id':'S001-lemma-test','material_path':'C:/old-machine/private/item.tex'}
        self.assertEqual(pilot.material_path(root,candidate),root/'research-line/archive/2026-10-10/initial_corpus/items/S001-lemma-test.tex')
        with self.assertRaises(ValueError):pilot.material_path(root,{'research_id':'../../outside'})

    def test_context_omission_requires_matching_reviewed_bytes(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);text='\\begin{proof}\nA complete construction.\nSome details omitted.\n\\end{proof}'
            context=dict(file='one.tex',start_line=100,excerpt=text)
            with self.assertRaisesRegex(ValueError,'unreviewed or changed'):
                pilot.check_context_reviews(root,1,[context])
            review=dict(candidate_number=1,context_excerpt_sha256=pilot.gate.digest(text),reviews=[dict(exact_phrase='Some details omitted.',source_locator={'file':'one.tex','lines':[102,102]},scope='Explicit optional compatibility',why_noncore='The complete construction is supplied before this standard compatibility.',decision='accepted_as_bounded_noncore_omission')])
            pilot.dump(root/'CONTEXT_REVIEW.json',{'items':[review]})
            self.assertEqual(len(pilot.check_context_reviews(root,1,[context])),1)
            context['excerpt']=text.replace('complete construction','different unreviewed construction')
            with self.assertRaisesRegex(ValueError,'unreviewed or changed'):
                pilot.check_context_reviews(root,1,[context])


if __name__=='__main__':unittest.main()
