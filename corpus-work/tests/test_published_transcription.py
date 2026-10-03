"""Synthetic provenance fixtures; no mathematical or publication-rights certification."""
import copy
import json
from pathlib import Path
import sqlite3
import unittest

import test_editable_delivery as fixture

digest = fixture.digest

ORIGIN = 'human_authored_checked_published_transcription'


class PublishedTranscription(unittest.TestCase):
    save = fixture.EditableDelivery.save
    run_gate = fixture.EditableDelivery.run_gate
    assert_fails = fixture.EditableDelivery.assert_fails

    def setUp(self):
        fixture.EditableDelivery.setUp(self)
        self.row['origin_class'] = ORIGIN
        self.pdf_path = 'sources/1001/published.pdf'
        self.transcription_path = 'sources/1001/transcription.tex'
        self.record_path = 'sources/1001/published-transcription.json'
        (self.package / self.pdf_path).write_bytes(b'%PDF-1.4\nSynthetic published original\n')
        (self.package / self.transcription_path).write_text(self.raw)
        self.row['primary']['source_pdf_sha256'] = digest((self.package / self.pdf_path).read_bytes())
        self.evidence_item['sources'] = [dict(root='package', path=self.transcription_path,
                                             sha256=digest(self.raw))]
        self.record = dict(schema_version=1, problem_id='1001',
                           representation='checked_published_transcription',
                           source_url=self.row['source_url'], source_version=self.row['source_version'],
                           license=self.row['license'], published_pdf_path=self.pdf_path,
                           published_pdf_sha256=self.row['primary']['source_pdf_sha256'],
                           transcription_source_path=self.transcription_path,
                           transcription_source_sha256=digest(self.raw),
                           comparison=dict(method='synthetic-page-comparison',
                                           notes='Synthetic complete-page comparison declaration only.',
                                           source_pages=[1], output_pages=[1],
                                           complete_statement=True, complete_proof=True,
                                           required_context_preserved=True),
                           private_upstream_archive_or_classes_included=False,
                           private_upstream_classes_executed=False)
        self.bind_record()

    def bind_record(self, raw=None):
        if raw is None:
            raw = json.dumps(self.record).encode('utf-8')
        (self.package / self.record_path).write_bytes(raw)
        self.row['published_transcription_evidence'] = dict(path=self.record_path, sha256=digest(raw))
        self.save()

    def assert_rejected(self, message='published transcription', *args):
        self.assert_fails(message, *args)

    def test_fully_bound_published_transcription_passes_full_gate(self):
        result, report = self.run_gate()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(report['editable_qualified_count'], 1)
        self.assertEqual(report['items']['1001']['status'], 'qualified_editable')
        self.assertIn('does not certify', report['limitations'])

    def test_fully_bound_published_transcription_passes_single_item_gate(self):
        result, report = self.run_gate('--item', '1001')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(report['editable_qualified_count'], 1)

    def test_single_item_keeps_other_published_origin_evidence_in_package_consistency_scope(self):
        other = copy.deepcopy(self.row)
        other.update(problem_id='1002', title='Independent native fixture',
                     item_path='items/1002_example.tex', source_id='source:revision:otherclaim',
                     source_url='https://example.org/other-original',
                     origin_class='human_authored_native_tex', compile_receipt='receipts/1002.json')
        del other['published_transcription_evidence']
        other['primary']['excerpt_path'] = 'sources/1002/primary.tex'
        self.manifest['items'].append(other)
        self.manifest['verified_count'] = 2
        other_evidence = copy.deepcopy(self.evidence_item)
        other_evidence['claim_key'] = 'independent-other-original-claim'
        other_evidence['sources'] = [dict(root='source', path='raw/source.tex', sha256=digest(self.raw))]
        self.evidence['items']['1002'] = other_evidence
        self.save()
        (self.package / 'sources/1002').mkdir()
        (self.package / other['item_path']).write_text(self.tex)
        (self.package / other['primary']['excerpt_path']).write_text(self.statement + '\n' + self.proof + '\n')
        (self.package / 'sources/1002/provenance.json').write_text(json.dumps(other))
        other_receipt = dict(self.receipt, problem_id='1002')
        (self.package / other['compile_receipt']).write_text(json.dumps(other_receipt))
        with (self.package / 'INDEX.md').open('a') as index:
            index.write('| 1002 | ' + other['title'] + ' | H2 | [TeX](' + other['item_path'] +
                        ') | [Source](' + other['source_url'] + ') · [Provenance](sources/1002/provenance.json) |\n')
        with sqlite3.connect(self.package / 'corpus.sqlite') as db:
            db.execute('INSERT INTO sources VALUES (?,?,?,?,?,?,?,?)',
                       tuple(other[k] for k in ['source_id','author','work','source_url','source_version','retrieved_at','license','license_path']))
            db.execute('INSERT INTO problems VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',
                       tuple(other[k] for k in ['problem_id','title','difficulty_level','difficulty_reason','source_id']) +
                       (json.dumps(dict(primary=other['primary'], contexts=other['contexts']), sort_keys=True),
                        other['item_path'], self.tex, other['tex_sha256'], other['origin_class'],
                        other['status'], other['compile_receipt']))
        result, report = self.run_gate('--item', '1002')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(report['editable_qualified_count'], 1)
        del self.row['published_transcription_evidence']
        (self.package / 'manifest.json').write_text(json.dumps(self.manifest))
        (self.package / 'sources/1001/provenance.json').write_text(json.dumps(self.row))
        self.assert_rejected('published transcription', '--item', '1002')

    def test_existing_native_origin_passes_without_published_evidence(self):
        self.row['origin_class'] = 'human_authored_native_tex'
        del self.row['published_transcription_evidence']
        self.save()
        result, report = self.run_gate()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(report['editable_qualified_count'], 1)

    def test_existing_proof_assistant_origin_passes_without_published_evidence(self):
        self.row['origin_class'] = 'human_authored_proof_assistant_transcription'
        del self.row['published_transcription_evidence']
        self.save()
        result, report = self.run_gate()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(report['editable_qualified_count'], 1)

    def test_unknown_origin_fails(self):
        self.row['origin_class'] = 'human_authored_unknown_transcription'
        self.save()
        self.assert_rejected('unsupported source origin schema')

    def test_missing_or_malformed_evidence_descriptor_fails(self):
        for value in [None, False, [], '', {}, {'path': self.record_path},
                      {'sha256': digest((self.package / self.record_path).read_bytes())}]:
            with self.subTest(descriptor=value):
                self.row['published_transcription_evidence'] = value
                self.save()
                self.assert_rejected('published transcription')
        del self.row['published_transcription_evidence']
        self.save()
        self.assert_rejected('published transcription')

    def test_bad_record_hash_fails(self):
        valid = copy.deepcopy(self.row['published_transcription_evidence'])
        for value in [None, True, 1, '', 'bad', '0' * 63, 'A' * 64, '0' * 64]:
            with self.subTest(sha256=value):
                self.row['published_transcription_evidence'] = dict(valid, sha256=value)
                self.save()
                self.assert_rejected('published transcription')

    def test_missing_record_file_fails(self):
        (self.package / self.record_path).unlink()
        self.assert_rejected('published transcription')

    def test_record_path_must_stay_in_same_per_id_sources(self):
        raw = (self.package / self.record_path).read_bytes()
        for path in ['published-transcription.json', 'sources/1002/record.json',
                     'sources/1001/../1002/record.json']:
            target = self.package / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
            with self.subTest(path=path):
                self.row['published_transcription_evidence']['path'] = path
                self.save()
                self.assert_rejected('published transcription')
        for path in [str(self.package / self.record_path), '../outside.json', '', None, True]:
            with self.subTest(path=path):
                self.row['published_transcription_evidence']['path'] = path
                self.save()
                self.assert_rejected('published transcription')

    def test_record_symlink_cannot_escape_same_id(self):
        other = self.package / 'sources/1002/record.json'
        other.parent.mkdir(parents=True)
        other.write_bytes((self.package / self.record_path).read_bytes())
        (self.package / self.record_path).unlink()
        (self.package / self.record_path).symlink_to(other)
        self.assert_rejected('published transcription')

    def test_malformed_nonobject_and_duplicate_key_record_fails(self):
        valid = json.dumps(self.record)
        for raw in [b'{', b'null', b'[]', b'true', b'"record"', b'\xff',
                    ('{"schema_version":1,' + valid[1:]).encode(),
                    valid.replace('"complete_proof": true',
                                  '"complete_proof": false, "complete_proof": true').encode()]:
            with self.subTest(raw=raw[:80]):
                self.bind_record(raw)
                self.assert_rejected('published transcription')

    def test_wrong_schema_id_representation_and_source_metadata_fail(self):
        baseline = copy.deepcopy(self.record)
        mutations = [('schema_version', v) for v in [None, True, False, '1', 1.0, 0, 2]]
        mutations += [('problem_id', v) for v in [None, 1001, '1002']]
        mutations += [('representation', v) for v in [None, '', 'native_tex']]
        mutations += [(k, v) for k in ['source_url', 'source_version', 'license'] for v in [None, '', 'different']]
        for key, value in mutations:
            with self.subTest(field=key, value=value):
                self.record = dict(baseline, **{key: value})
                self.bind_record()
                self.assert_rejected('published transcription')

    def test_required_record_fields_cannot_be_missing(self):
        baseline = copy.deepcopy(self.record)
        for key in baseline:
            with self.subTest(field=key):
                self.record = copy.deepcopy(baseline)
                del self.record[key]
                self.bind_record()
                self.assert_rejected('published transcription')

    def test_pdf_path_missing_escaping_cross_id_or_noncanonical_fails(self):
        raw = (self.package / self.pdf_path).read_bytes()
        other = self.package / 'sources/1002/published.pdf'
        other.parent.mkdir(parents=True)
        other.write_bytes(raw)
        for path in ['sources/1001/missing.pdf', 'sources/1002/published.pdf',
                     'sources/1001/../1002/published.pdf', '../published.pdf',
                     str(self.package / self.pdf_path), None, False]:
            with self.subTest(path=path):
                self.record['published_pdf_path'] = path
                self.bind_record()
                self.assert_rejected('published transcription')

    def test_pdf_symlink_cannot_escape_same_id(self):
        other = self.package / 'sources/1002/published.pdf'
        other.parent.mkdir(parents=True)
        other.write_bytes((self.package / self.pdf_path).read_bytes())
        (self.package / self.pdf_path).unlink()
        (self.package / self.pdf_path).symlink_to(other)
        self.assert_rejected('published transcription')

    def test_pdf_wrong_bytes_hash_or_header_fails(self):
        baseline = (self.package / self.pdf_path).read_bytes()
        for raw, bind_hash in [(b'%PDF-1.4\nchanged original', False),
                               (b'NOTPDF\nchanged original', True)]:
            with self.subTest(raw=raw, bind_hash=bind_hash):
                (self.package / self.pdf_path).write_bytes(raw)
                if bind_hash:
                    self.record['published_pdf_sha256'] = digest(raw)
                    self.row['primary']['source_pdf_sha256'] = digest(raw)
                self.bind_record()
                self.assert_rejected('published transcription')
        (self.package / self.pdf_path).write_bytes(baseline)

    def test_pdf_record_and_primary_hashes_must_agree(self):
        self.row['primary']['source_pdf_sha256'] = '0' * 64
        self.save()
        self.assert_rejected('published transcription')
        del self.row['primary']['source_pdf_sha256']
        self.save()
        self.assert_rejected('published transcription')

    def test_pdf_and_transcription_hashes_require_lowercase_sha256(self):
        baseline = copy.deepcopy(self.record)
        for key in ['published_pdf_sha256', 'transcription_source_sha256']:
            for value in [None, True, 1, '', 'bad', 'f' * 63, 'F' * 64, '0' * 64]:
                with self.subTest(field=key, value=value):
                    self.record = dict(baseline, **{key: value})
                    self.bind_record()
                    self.assert_rejected('published transcription')

    def test_transcription_path_missing_escaping_or_cross_id_fails(self):
        other = self.package / 'sources/1002/transcription.tex'
        other.parent.mkdir(parents=True)
        other.write_text(self.raw)
        for path in ['sources/1001/missing.tex', 'sources/1002/transcription.tex',
                     'sources/1001/../1002/transcription.tex', '../transcription.tex',
                     str(self.package / self.transcription_path), None, False]:
            with self.subTest(path=path):
                self.record['transcription_source_path'] = path
                self.bind_record()
                self.assert_rejected('published transcription')

    def test_transcription_symlink_cannot_escape_same_id(self):
        other = self.package / 'sources/1002/transcription.tex'
        other.parent.mkdir(parents=True)
        other.write_text(self.raw)
        (self.package / self.transcription_path).unlink()
        (self.package / self.transcription_path).symlink_to(other)
        self.assert_rejected('published transcription')

    def test_transcription_bytes_and_readable_text_are_checked(self):
        for raw, bind_hash in [(b'Changed source', False), (b'\xff\xfe\x00', True)]:
            with self.subTest(raw=raw, bind_hash=bind_hash):
                (self.package / self.transcription_path).write_bytes(raw)
                if bind_hash:
                    self.record['transcription_source_sha256'] = digest(raw)
                    self.evidence_item['sources'][0]['sha256'] = digest(raw)
                self.bind_record()
                self.assert_rejected('published transcription')

    def test_transcription_source_must_appear_as_exact_package_path_and_hash(self):
        baseline = copy.deepcopy(self.evidence_item['sources'][0])
        for source in [dict(baseline, path='raw/source.tex', root='source'),
                       dict(baseline, sha256='0' * 64),
                       dict(baseline, root='source'),
                       dict(baseline, root='inline', inline_text=self.raw)]:
            with self.subTest(source=source):
                self.evidence_item['sources'] = [source]
                self.save()
                self.assert_rejected('published transcription')

    def test_default_source_root_can_bind_when_it_is_the_delivered_package(self):
        del self.evidence_item['sources'][0]['root']
        self.save()
        result, report = self.run_gate('--source-root', str(self.package))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(report['editable_qualified_count'], 1)

    def test_primary_statement_and_proof_must_use_transcription_source_index(self):
        self.evidence_item['sources'].append(dict(root='source', path='raw/source.tex', sha256=digest(self.raw)))
        for role in ['primary_statement', 'primary_proof']:
            body = next(b for b in self.evidence_item['bodies'] if b['role'] == role)
            for value in [1, True, False, '0', None]:
                with self.subTest(role=role, source_index=value):
                    body['source_index'] = value
                    self.save()
                    self.assert_rejected('published transcription')
            body['source_index'] = 0

    def test_every_primary_multispan_must_use_transcription_source_index(self):
        first = r'\begin{proof}The complete retained first argument.'
        second = r'The retained concluding argument.\end{proof}'
        self.raw = '\n'.join(['% Original human source', self.statement, first, second, ''])
        self.tex = '\n'.join([r'\documentclass{article}', r'\begin{document}',
                              self.statement, first, second, r'\end{document}', ''])
        (self.sources / 'raw/source.tex').write_text(self.raw)
        (self.package / self.transcription_path).write_text(self.raw)
        (self.package / self.row['item_path']).write_text(self.tex)
        excerpt = '\n'.join([self.statement, first, second, ''])
        (self.package / self.row['primary']['excerpt_path']).write_text(excerpt)
        self.row['primary'].update(end_line=4, source_sha256=digest(self.raw), excerpt_sha256=digest(excerpt))
        self.row['tex_sha256'] = self.receipt['input_sha256'] = self.evidence_item['item_sha256'] = digest(self.tex)
        self.record['transcription_source_sha256'] = digest(self.raw)
        self.evidence_item['sources'][0]['sha256'] = digest(self.raw)
        self.evidence_item['sources'].append(dict(root='source', path='raw/source.tex', sha256=digest(self.raw)))
        spans = [dict(tex_lines=[4, 4], tex_sha256=digest(first), source_index=0, source_lines=[3, 3], method='exact_tex'),
                 dict(tex_lines=[5, 5], tex_sha256=digest(second), source_index=0, source_lines=[4, 4], method='exact_tex')]
        self.evidence_item['bodies'][1] = dict(role='primary_proof', spans=spans)
        self.bind_record()
        result, report = self.run_gate()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        spans[1]['source_index'] = 1
        self.save()
        self.assert_rejected('published transcription')

    def test_context_may_use_another_existing_hash_bound_source(self):
        self.evidence_item['sources'].append(dict(root='source', path='raw/source.tex', sha256=digest(self.raw)))
        self.evidence_item['bodies'].append(dict(self.evidence_item['bodies'][1], role='context', source_index=1))
        self.save()
        result, report = self.run_gate()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(report['editable_qualified_count'], 1)

    def test_comparison_must_be_object_with_nonempty_method_and_notes(self):
        baseline = copy.deepcopy(self.record['comparison'])
        for value in [None, [], '', True]:
            with self.subTest(comparison=value):
                self.record['comparison'] = value
                self.bind_record()
                self.assert_rejected('published transcription')
        for key in ['method', 'notes']:
            for value in [None, '', '   ', True, 1, []]:
                with self.subTest(field=key, value=value):
                    self.record['comparison'] = dict(baseline, **{key: value})
                    self.bind_record()
                    self.assert_rejected('published transcription')
            self.record['comparison'] = copy.deepcopy(baseline)
            del self.record['comparison'][key]
            self.bind_record()
            self.assert_rejected('published transcription')

    def test_source_and_output_pages_require_unique_positive_strict_integers(self):
        baseline = copy.deepcopy(self.record['comparison'])
        for key in ['source_pages', 'output_pages']:
            for value in [None, [], {}, '1', [0], [-1], [True], [False], ['1'], [1.0], [1, 1], [1, None], [[1]]]:
                with self.subTest(field=key, value=value):
                    self.record['comparison'] = dict(baseline, **{key: value})
                    self.bind_record()
                    self.assert_rejected('published transcription')
            self.record['comparison'] = copy.deepcopy(baseline)
            del self.record['comparison'][key]
            self.bind_record()
            self.assert_rejected('published transcription')

    def test_comparison_completeness_flags_require_literal_true(self):
        baseline = copy.deepcopy(self.record['comparison'])
        for key in ['complete_statement', 'complete_proof', 'required_context_preserved']:
            for value in [None, False, 0, 1, 'true', [], {}]:
                with self.subTest(field=key, value=value):
                    self.record['comparison'] = dict(baseline, **{key: value})
                    self.bind_record()
                    self.assert_rejected('published transcription')
            self.record['comparison'] = copy.deepcopy(baseline)
            del self.record['comparison'][key]
            self.bind_record()
            self.assert_rejected('published transcription')

    def test_private_material_flags_require_literal_false_without_defaults(self):
        baseline = copy.deepcopy(self.record)
        for key in ['private_upstream_archive_or_classes_included', 'private_upstream_classes_executed']:
            for value in [None, True, 0, 1, 'false', [], {}]:
                with self.subTest(field=key, value=value):
                    self.record = dict(baseline, **{key: value})
                    self.bind_record()
                    self.assert_rejected('published transcription')
            self.record = copy.deepcopy(baseline)
            del self.record[key]
            self.bind_record()
            self.assert_rejected('published transcription')

    def test_new_origin_does_not_bypass_manifest_source_admission(self):
        self.row['source_check']['root_admission_pending'] = True
        self.save()
        self.assert_rejected('manifest source_check admission pending')
        self.assert_rejected('manifest source_check admission pending', '--item', '1001')

    def test_new_origin_does_not_bypass_body_source_admission(self):
        self.evidence_item['source_check']['root_admission_pending'] = True
        self.save()
        self.assert_rejected('body evidence source_check admission pending')
        self.assert_rejected('body evidence source_check admission pending', '--item', '1001')

    def test_new_origin_does_not_bypass_admission_hold(self):
        self.row['admission_hold'] = 'Unresolved source material'
        self.save()
        self.assert_rejected('admission_hold')

    def test_new_origin_does_not_bypass_body_hash_or_source_fidelity(self):
        self.evidence_item['bodies'][1]['tex_sha256'] = '0' * 64
        self.save()
        self.assert_rejected('body hash mismatch')
        self.evidence_item['bodies'][1]['tex_sha256'] = digest(self.proof)
        self.evidence_item['bodies'][1]['source_lines'] = [2, 2]
        self.save()
        self.assert_rejected('source/body fidelity mismatch')

    def test_new_origin_does_not_bypass_pdf_wrappers(self):
        fixture.EditableDelivery.test_pdf_wrapper_rejected_even_with_compile_receipt(self)

    def test_new_origin_does_not_bypass_failed_compile(self):
        self.receipt['ok'] = False
        self.save()
        self.assert_rejected('compile receipt failed or incomplete')

    def test_new_origin_does_not_bypass_final_compile_instability(self):
        fixture.EditableDelivery.test_final_compile_rerun_warning_rejected_despite_empty_receipt(self)

    def test_new_origin_does_not_bypass_inconsistent_sqlite(self):
        with sqlite3.connect(self.package / 'corpus.sqlite') as db:
            db.execute("UPDATE problems SET tex_content = 'altered editable text'")
        self.assert_rejected('SQLite tex_content differs from full delivered TeX')
        self.assert_rejected('SQLite tex_content differs from full delivered TeX', '--item', '1001')

    def test_validation_keeps_the_package_read_only(self):
        fixture.EditableDelivery.test_reads_without_writing_to_package(self)


if __name__ == '__main__':
    unittest.main()
