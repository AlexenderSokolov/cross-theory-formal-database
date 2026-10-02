"""Synthetic fixtures test delivery evidence, not mathematical validity."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / 'scripts/validate_corpus.py'


def digest(data):
    if isinstance(data, str):
        data = data.encode('utf-8')
    return hashlib.sha256(data).hexdigest()


class EditableDelivery(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.package = self.root / 'package'
        self.sources = self.root / 'originals'
        self.package.mkdir()
        (self.sources / 'raw').mkdir(parents=True)
        for directory in ['items', 'sources/1001', 'licenses', 'receipts', 'build/1001']:
            (self.package / directory).mkdir(parents=True)
        self.statement = r'\begin{theorem}The retained original statement.\end{theorem}'
        self.proof = r'\begin{proof}The complete retained author argument.\end{proof}'
        self.tex = '\n'.join([r'\documentclass{article}', r'\begin{document}',
                              self.statement, self.proof, r'\end{document}', ''])
        self.raw = '\n'.join(['% Original human source', self.statement, self.proof, ''])
        (self.sources / 'raw/source.tex').write_text(self.raw)
        (self.package / 'items/1001_example.tex').write_text(self.tex)
        (self.package / 'sources/1001/primary.tex').write_text(self.statement + '\n' + self.proof + '\n')
        (self.package / 'licenses/source.txt').write_text('License fixture')
        self.row = dict(problem_id='1001', title='Retained original example',
                        item_path='items/1001_example.tex', author='Named human author',
                        work='Original named work', source_id='source:revision:claim',
                        source_url='https://example.org/original', source_version='revision1',
                        retrieved_at='2026-10-02', license='Example open license',
                        license_path='licenses/source.txt', difficulty_level='H2',
                        difficulty_reason='Specific nonroutine construction retained in the author proof.',
                        status='verified_editable_tex', origin_class='human_authored_native_tex',
                        tex_sha256=digest(self.tex), compile_receipt='receipts/1001.json',
                        primary=dict(source_path='raw/source.tex', source_sha256=digest(self.raw),
                                     start_line=2, end_line=3, excerpt_path='sources/1001/primary.tex',
                                     excerpt_sha256=digest(self.statement + '\n' + self.proof + '\n')),
                        contexts=[], source_check=dict(checks=['full original statement and proof'],
                                                       note='Bounded materials comparison; no mathematical referee.'))
        self.manifest = dict(schema_version=1, verified_count=1, items=[self.row])
        self.evidence_item = dict(item_sha256=digest(self.tex), claim_key='example-original-claim',
                                 independent_problem_unit=True,
                                 source_check=dict(checked_at='2026-10-02T00:00:00+00:00',
                                                   method='bounded-original-source-comparison',
                                                   note='Compared the exact complete selected original author unit.',
                                                   complete_statement=True, complete_proof=True,
                                                   required_context_preserved=True,
                                                   above_ordinary_phd_quals=True,
                                                   source_authorship='named-human-author'),
                                 sources=[dict(path='raw/source.tex', sha256=digest(self.raw))],
                                 bodies=[dict(role='primary_statement', tex_lines=[3, 3],
                                              tex_sha256=digest(self.statement), source_index=0,
                                              source_lines=[2, 2], method='exact_tex'),
                                         dict(role='primary_proof', tex_lines=[4, 4],
                                              tex_sha256=digest(self.proof), source_index=0,
                                              source_lines=[3, 3], method='exact_tex')])
        self.evidence = dict(schema_version=1, items={'1001': self.evidence_item})
        (self.package / 'build/1001/output.pdf').write_bytes(b'%PDF-1.4\nfixture')
        (self.package / 'build/1001/compiler.log').write_text('Two-pass fixture: no unresolved references\n')
        self.receipt = dict(problem_id='1001', input_sha256=digest(self.tex), engine='xelatex',
                            shell_escape=False, passes=2, ok=True,
                            compiled_at='2026-10-02T00:00:00+00:00', unresolved_references=[],
                            missing_characters=[], pages=1, dependency_sha256={},
                            pdf_path='1001/output.pdf', compiler_log_path='1001/compiler.log',
                            pdf_sha256=digest((self.package / 'build/1001/output.pdf').read_bytes()),
                            compiler_log_sha256=digest((self.package / 'build/1001/compiler.log').read_bytes()))
        self.save()

    def save(self):
        (self.package / 'manifest.json').write_text(json.dumps(self.manifest))
        (self.package / 'sources/1001/provenance.json').write_text(json.dumps(self.row))
        (self.package / 'receipts/1001.json').write_text(json.dumps(self.receipt))
        (self.root / 'evidence.json').write_text(json.dumps(self.evidence))
        (self.package / 'INDEX.md').write_text('| 1001 | ' + self.row['title'] + ' | H2 | [TeX](' + self.row['item_path'] + ') | [Source](' + self.row['source_url'] + ') · [Provenance](sources/1001/provenance.json) |\n')
        db_path = self.package / 'corpus.sqlite'
        if db_path.exists():
            db_path.unlink()
        db = sqlite3.connect(db_path)
        db.executescript('CREATE TABLE sources (source_id TEXT PRIMARY KEY, author TEXT, work TEXT, source_url TEXT, source_version TEXT, retrieved_at TEXT, license TEXT, license_path TEXT); CREATE TABLE problems (problem_id TEXT PRIMARY KEY,title TEXT,difficulty_level TEXT,difficulty_reason TEXT,source_id TEXT REFERENCES sources(source_id),source_locator_json TEXT,tex_path TEXT,tex_content TEXT,tex_sha256 TEXT,origin_class TEXT,status TEXT,compile_receipt_path TEXT);')
        db.execute('INSERT INTO sources VALUES (?,?,?,?,?,?,?,?)', tuple(self.row[k] for k in ['source_id','author','work','source_url','source_version','retrieved_at','license','license_path']))
        db.execute('INSERT INTO problems VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',
                   tuple(self.row[k] for k in ['problem_id','title','difficulty_level','difficulty_reason','source_id']) +
                   (json.dumps(dict(primary=self.row['primary'], contexts=self.row['contexts']), sort_keys=True),
                    self.row['item_path'], self.tex, self.row['tex_sha256'], self.row['origin_class'],
                    self.row['status'], self.row['compile_receipt']))
        db.commit()
        db.close()

    def run_gate(self, *args):
        command = [sys.executable, str(CLI), '--mode', 'editable-delivery', '--package', str(self.package),
                   '--source-root', str(self.sources), '--build-root', str(self.package / 'build'),
                   '--evidence', str(self.root / 'evidence.json')]
        result = subprocess.run(command + list(args), capture_output=True, text=True)
        try:
            report = json.loads(result.stdout)
        except json.JSONDecodeError:
            self.fail('Gate must produce JSON, including failures: ' + result.stderr + result.stdout)
        return result, report

    def assert_fails(self, message, *args):
        result, report = self.run_gate(*args)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(message, str(report))
        self.assertEqual(report['editable_qualified_count'], 0)

    def test_complete_source_bound_fixture_passes(self):
        result, report = self.run_gate('--item', '1001')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(report['mode'], 'editable-delivery')
        self.assertEqual(report['editable_qualified_count'], 1)
        self.assertIn('does not certify', report['limitations'])

    def test_manifest_source_check_pending_admission_fails_closed(self):
        self.row['source_check']['root_admission_pending'] = True
        self.save()
        self.assert_fails('manifest source_check admission pending')
        self.assert_fails('manifest source_check admission pending', '--item', '1001')

    def test_body_evidence_source_check_pending_admission_fails_closed(self):
        self.evidence_item['source_check']['root_admission_pending'] = True
        self.save()
        self.assert_fails('body evidence source_check admission pending')
        self.assert_fails('body evidence source_check admission pending', '--item', '1001')

    def test_current_source_check_cleared_admission_passes(self):
        self.row['source_check']['root_admission_pending'] = False
        self.evidence_item['source_check']['root_admission_pending'] = False
        self.save()
        result, report = self.run_gate()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(report['editable_qualified_count'], 1)

    def test_current_source_check_malformed_admission_flag_fails_closed(self):
        for label, declaration in [('manifest', self.row['source_check']),
                                   ('body evidence', self.evidence_item['source_check'])]:
            for value in [None, 0, 1, 'false', 'true', [], {}]:
                with self.subTest(scope=label, value=value):
                    declaration['root_admission_pending'] = value
                    self.save()
                    self.assert_fails(label + ' source_check malformed root_admission_pending')
            declaration.pop('root_admission_pending')

    def test_historical_source_check_pending_admission_is_preserved(self):
        for declaration in [self.row['source_check'], self.evidence_item['source_check']]:
            declaration['original_stage_source_check'] = dict(root_admission_pending=True)
        for current_cleared in [False, True]:
            with self.subTest(current_flag_present=current_cleared):
                if current_cleared:
                    self.row['source_check']['root_admission_pending'] = False
                    self.evidence_item['source_check']['root_admission_pending'] = False
                self.save()
                result, report = self.run_gate()
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertEqual(report['editable_qualified_count'], 1)

    def test_reads_without_writing_to_package(self):
        before = {str(p.relative_to(self.package)): digest(p.read_bytes()) for p in self.package.rglob('*') if p.is_file()}
        result, _ = self.run_gate()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        after = {str(p.relative_to(self.package)): digest(p.read_bytes()) for p in self.package.rglob('*') if p.is_file()}
        self.assertEqual(before, after)

    def test_missing_evidence_fails_closed(self):
        (self.root / 'evidence.json').unlink()
        self.assert_fails('evidence')

    def test_unsupported_evidence_schema_fails_closed(self):
        self.evidence['schema_version'] = 99
        self.save()
        self.assert_fails('evidence schema')

    def test_missing_primary_statement_body_fails(self):
        self.evidence_item['bodies'] = self.evidence_item['bodies'][1:]
        self.save()
        self.assert_fails('primary_statement')

    def test_empty_primary_proof_is_rejected_without_length_threshold(self):
        self.tex = self.tex.replace(self.proof, r'\begin{proof}\end{proof}')
        self.proof = r'\begin{proof}\end{proof}'
        (self.package / self.row['item_path']).write_text(self.tex)
        self.row['tex_sha256'] = self.receipt['input_sha256'] = self.evidence_item['item_sha256'] = digest(self.tex)
        self.evidence_item['bodies'][1]['tex_sha256'] = digest(self.proof)
        self.save()
        self.assert_fails('empty primary_proof')

    def test_pdf_wrapper_rejected_even_with_compile_receipt(self):
        self.tex = self.tex.replace(self.proof, r'\includepdf{original.pdf}')
        (self.package / self.row['item_path']).write_text(self.tex)
        self.row['tex_sha256'] = self.receipt['input_sha256'] = digest(self.tex)
        self.save()
        self.assert_fails('PDF-page wrapper')

    def test_final_compile_rerun_warning_rejected_despite_empty_receipt(self):
        log = self.package / 'build/1001/compiler.log'
        log.write_text('This is XeTeX, Version fixture\nStable first pass\nThis is XeTeX, Version fixture\nLaTeX Warning: Label(s) may have changed. Rerun to get cross-references right.\n')
        self.receipt['compiler_log_sha256'] = digest(log.read_bytes())
        self.receipt['rerun_requests'] = []
        self.save()
        self.assert_fails('final compiler pass requests rerun')

    def test_final_compile_duplicate_label_rejected(self):
        log = self.package / 'build/1001/compiler.log'
        log.write_text("This is XeTeX, Version fixture\nLaTeX Warning: Label `x' multiply defined.\n")
        self.receipt['compiler_log_sha256'] = digest(log.read_bytes())
        self.save()
        self.assert_fails('final compiler pass has multiply-defined labels')

    def test_resolved_earlier_pass_warning_is_not_final_warning(self):
        log = self.package / 'build/1001/compiler.log'
        log.write_text('This is XeTeX, Version fixture\nLaTeX Warning: Label(s) may have changed. Rerun to get cross-references right.\nThis is XeTeX, Version fixture\nStable final pass\n')
        self.receipt['compiler_log_sha256'] = digest(log.read_bytes())
        self.save()
        result, report = self.run_gate()
        self.assertEqual(result.returncode, 0, report)

    def multi_span_proof_fixture(self, first=r'\begin{proof}The original first argument.',
                                 second=r'The original concluding argument.\end{proof}'):
        self.raw = '\n'.join(['% Original human source', self.statement, first,
                              '% Non-proof source annotation', second, ''])
        self.tex = '\n'.join([r'\documentclass{article}', r'\begin{document}',
                              self.statement, first, '% Editorial separation',
                              second, r'\end{document}', ''])
        (self.sources / 'raw/source.tex').write_text(self.raw)
        (self.package / self.row['item_path']).write_text(self.tex)
        excerpt = '\n'.join(self.raw.splitlines()[1:]) + '\n'
        (self.package / self.row['primary']['excerpt_path']).write_text(excerpt)
        self.row['primary'].update(end_line=5, source_sha256=digest(self.raw),
                                   excerpt_sha256=digest(excerpt))
        self.evidence_item['sources'][0]['sha256'] = digest(self.raw)
        self.row['tex_sha256'] = self.receipt['input_sha256'] = self.evidence_item['item_sha256'] = digest(self.tex)
        self.evidence_item['bodies'][1] = dict(role='primary_proof', spans=[
            dict(tex_lines=[4, 4], tex_sha256=digest(first), source_index=0,
                 source_lines=[3, 3], method='exact_tex'),
            dict(tex_lines=[6, 6], tex_sha256=digest(second), source_index=0,
                 source_lines=[5, 5], method='exact_tex')])
        self.save()

    def test_nonconsecutive_primary_proof_checks_each_exact_span(self):
        self.multi_span_proof_fixture()
        result, report = self.run_gate()
        self.assertEqual(result.returncode, 0, report)
        self.assertEqual(report['editable_qualified_count'], 1)

    def test_multispan_second_hash_cannot_be_ignored(self):
        self.multi_span_proof_fixture()
        self.evidence_item['bodies'][1]['spans'][1]['tex_sha256'] = '0' * 64
        self.save()
        self.assert_fails('body hash mismatch')

    def test_multispan_primary_may_include_structural_only_fragment(self):
        self.multi_span_proof_fixture(first=r'\begin{proof}')
        result, report = self.run_gate()
        self.assertEqual(result.returncode, 0, report)

    def test_multispan_all_structural_is_not_a_proof(self):
        self.multi_span_proof_fixture(first=r'\begin{proof}', second=r'\end{proof}')
        self.assert_fails('empty primary_proof body')

    def test_grouped_context_checks_structural_fragment_and_its_substance(self):
        self.multi_span_proof_fixture()
        fragments = [r'\begin{gather}', r'f=0\end{gather}']
        self.tex = self.tex.replace(r'\end{document}', '\n'.join(fragments + [r'\end{document}']))
        (self.package / self.row['item_path']).write_text(self.tex)
        self.row['tex_sha256'] = self.receipt['input_sha256'] = self.evidence_item['item_sha256'] = digest(self.tex)
        spans = []
        for index, fragment in enumerate(fragments, 1):
            path = 'sources/1001/context-' + str(index) + '.tex'
            (self.package / path).write_text(fragment)
            self.row['contexts'].append(dict(excerpt_path=path, excerpt_sha256=digest(fragment),
                source_sha256=digest(fragment), start_line=1, end_line=1))
            self.evidence_item['sources'].append(dict(root='package', path=path, sha256=digest(fragment)))
            spans.append(dict(tex_lines=[6 + index, 6 + index], tex_sha256=digest(fragment),
                source_index=index, source_lines=[1, 1], method='exact_tex', source_excerpt_path=path))
        self.evidence_item['bodies'].append(dict(role='context', spans=spans))
        self.save()
        result, report = self.run_gate()
        self.assertEqual(result.returncode, 0, report)

    def test_multispan_second_source_cannot_be_ignored(self):
        self.multi_span_proof_fixture()
        self.evidence_item['bodies'][1]['spans'][1]['source_lines'] = [3, 3]
        self.save()
        self.assert_fails('source/body fidelity mismatch')

    def test_multispan_cannot_mix_scalar_anchor(self):
        self.multi_span_proof_fixture()
        self.evidence_item['bodies'][1]['tex_lines'] = [4, 4]
        self.save()
        self.assert_fails('scalar and multi-span body forms are mutually exclusive')

    def test_multispan_cannot_be_empty(self):
        self.multi_span_proof_fixture()
        self.evidence_item['bodies'][1]['spans'] = []
        self.save()
        self.assert_fails('body spans must be a nonempty list')

    def test_multispan_cannot_overlap_or_reverse_delivered_ranges(self):
        self.multi_span_proof_fixture()
        self.evidence_item['bodies'][1]['spans'].reverse()
        self.save()
        self.assert_fails('body spans must be ordered and nonoverlapping')

    def test_unchecked_supplemental_span_fields_are_rejected(self):
        self.evidence_item['bodies'][1]['tex_spans'] = [[4, 4], [99, 100]]
        self.save()
        self.assert_fails('unsupported supplemental span fields')

    def test_stale_compile_input_is_rejected(self):
        self.receipt['input_sha256'] = '0' * 64
        self.save()
        self.assert_fails('compile input hash')

    def test_missing_compile_receipt_is_rejected(self):
        (self.package / self.row['compile_receipt']).unlink()
        self.assert_fails('compile receipt')

    def test_stale_compile_pdf_is_rejected(self):
        (self.package / 'build/1001/output.pdf').write_bytes(b'%PDF-1.4\nchanged')
        self.assert_fails('compile PDF hash')

    def test_stale_compile_log_is_rejected(self):
        (self.package / 'build/1001/compiler.log').write_text('changed')
        self.assert_fails('compile log hash')

    def test_dependency_hash_required_for_declared_asset(self):
        (self.package / 'items/figure.png').write_bytes(b'figure')
        self.row['asset_dependencies'] = [dict(path='items/figure.png', sha256=digest(b'figure'))]
        self.save()
        self.assert_fails('compile dependency')

    def test_source_hash_change_rejected(self):
        (self.sources / 'raw/source.tex').write_text('changed original')
        self.assert_fails('declared source hash')

    def test_declared_original_source_must_exist(self):
        (self.sources / 'raw/source.tex').unlink()
        self.assert_fails('declared source')

    def test_excerpt_source_range_mismatch_rejected(self):
        self.row['primary']['end_line'] = 2
        self.save()
        self.assert_fails('source excerpt')

    def test_delivered_body_missing_from_source_rejected(self):
        self.evidence_item['bodies'][1]['source_lines'] = [2, 2]
        self.save()
        self.assert_fails('source/body fidelity')

    def test_adapted_body_requires_bounded_comparison_receipt(self):
        self.evidence_item['bodies'][1]['method'] = 'bounded_source_comparison'
        self.save()
        self.assert_fails('fidelity receipt')

    def test_false_completeness_declaration_rejected(self):
        self.evidence_item['source_check']['complete_proof'] = False
        self.save()
        self.assert_fails('complete_proof')

    def test_supporting_only_decision_rejected_with_reason(self):
        self.row['problem_id'] = '543'
        self.manifest['items'] = [self.row]
        self.save()
        self.assert_fails('supporting-only')

    def test_pinned_stacks_difficulty_hold_rejected(self):
        self.row['problem_id'] = '292'
        self.save()
        self.assert_fails('Non-counting pending difficulty review')

    def test_duplicate_manifest_ids_rejected(self):
        self.manifest['items'].append(dict(self.row))
        self.save()
        self.assert_fails('duplicate problem ID')

    def test_duplicate_json_object_keys_rejected(self):
        (self.root / 'evidence.json').write_text('{"schema_version":1,"items":{"1001":{},"1001":{}}}')
        self.assert_fails('duplicate JSON key')

    def test_per_item_still_requires_sqlite(self):
        (self.package / 'corpus.sqlite').unlink()
        self.assert_fails('SQLite', '--item', '1001')

    def test_per_item_still_checks_unexpected_sqlite_rows(self):
        with sqlite3.connect(self.package / 'corpus.sqlite') as db:
            db.execute("INSERT INTO problems SELECT '1002',title,difficulty_level,difficulty_reason,source_id,source_locator_json,tex_path,tex_content,tex_sha256,origin_class,status,compile_receipt_path FROM problems")
        self.assert_fails('SQLite problem IDs', '--item', '1001')

    def test_sqlite_full_tex_content_must_match(self):
        with sqlite3.connect(self.package / 'corpus.sqlite') as db:
            db.execute("UPDATE problems SET tex_content='summary only'")
        self.assert_fails('SQLite tex_content')

    def test_sqlite_source_record_must_match(self):
        with sqlite3.connect(self.package / 'corpus.sqlite') as db:
            db.execute("UPDATE sources SET author='Different author'")
        self.assert_fails('SQLite source metadata')

    def test_index_must_include_correct_file(self):
        (self.package / 'INDEX.md').write_text('| 1001 | '+self.row['title']+' | H2 | [TeX](items/missing.tex) | '+self.row['source_url']+' |\n')
        self.assert_fails('INDEX metadata')

    def test_duplicate_index_rows_rejected(self):
        p = self.package / 'INDEX.md'
        p.write_text(p.read_text() * 2)
        self.assert_fails('INDEX must have exactly one row')

    def test_manifest_count_must_equal_actual_unique_items(self):
        self.manifest['verified_count'] = 3000
        self.save()
        self.assert_fails('manifest verified_count')

    def test_provenance_must_match_manifest(self):
        p = self.package / 'sources/1001/provenance.json'
        data = json.loads(p.read_text())
        data['title'] = 'Different statement'
        p.write_text(json.dumps(data))
        self.assert_fails('provenance differs')

    def test_explicit_report_cannot_write_inside_package(self):
        self.assert_fails('report path must be outside', '--report', str(self.package / 'gate-report.json'))

    def test_portable_pinned_excerpt_does_not_need_full_original(self):
        self.evidence_item['sources'] = [dict(root='package', path=self.row['primary']['excerpt_path'],
                                            sha256=self.row['primary']['excerpt_sha256'],
                                            original_source_sha256=self.row['primary']['source_sha256'])]
        self.evidence_item['bodies'][0]['source_lines'] = [1, 1]
        self.evidence_item['bodies'][1]['source_lines'] = [2, 2]
        (self.sources / 'raw/source.tex').unlink()
        self.save()
        result, report = self.run_gate()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(report['editable_qualified_count'], 1)

    def test_reference_only_adaptation_preserves_all_other_tokens(self):
        source = self.statement + '\n' + self.proof.replace('argument.', r'argument using \ref{lemma-original}.') + '\n'
        (self.package / self.row['primary']['excerpt_path']).write_text(source)
        self.row['primary']['excerpt_sha256'] = digest(source)
        self.evidence_item['sources'] = [dict(root='package', path=self.row['primary']['excerpt_path'],
                                            sha256=digest(source), original_source_sha256=digest(self.raw))]
        self.evidence_item['bodies'][0]['source_lines'] = [1, 1]
        body = self.evidence_item['bodies'][1]
        body.update(source_lines=[2, 2], method='reference_only_adaptation',
                    replacements=[dict(original=r'\ref{lemma-original}',
                                       delivered=r'\href{https://example.org/lemma}{Lemma original}')])
        self.tex = self.tex.replace(self.proof, self.proof.replace('argument.', r'argument using \href{https://example.org/lemma}{Lemma original}.'))
        body['tex_sha256'] = digest(self.tex.splitlines()[3])
        self.row['tex_sha256'] = self.receipt['input_sha256'] = self.evidence_item['item_sha256'] = digest(self.tex)
        (self.package / self.row['item_path']).write_text(self.tex)
        self.save()
        result, _ = self.run_gate()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_reference_adaptation_cannot_replace_math(self):
        body = self.evidence_item['bodies'][1]
        body.update(method='reference_only_adaptation', replacements=[dict(original='author argument', delivered='generated argument')])
        self.save()
        self.assert_fails('reference-only replacement')

    def test_unknown_source_evidence_method_rejected(self):
        self.evidence_item['bodies'][1]['method'] = 'AI-proof-vote'
        self.save()
        self.assert_fails('unsupported body fidelity method')

    def test_same_primary_identity_cannot_be_counted_twice(self):
        duplicate = dict(self.row, problem_id='1002')
        self.manifest['items'].append(duplicate)
        self.save()
        self.assert_fails('duplicate primary source identity')

    def test_numeric_id_alias_cannot_be_counted_twice(self):
        self.manifest['items'].append(dict(self.row, problem_id='01001'))
        self.save()
        self.assert_fails('duplicate problem ID')

    def test_unresolved_references_cannot_use_success_receipt(self):
        self.receipt['unresolved_references'] = ['Reference foo undefined']
        self.save()
        self.assert_fails('compile receipt failed')

    def test_shell_escape_receipt_is_rejected(self):
        self.receipt['shell_escape'] = True
        self.save()
        self.assert_fails('compile receipt failed')

    def test_external_report_is_written_without_package_mutation(self):
        result, report = self.run_gate('--report', str(self.root / 'outside-report.json'))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads((self.root / 'outside-report.json').read_text()), report)

    def test_hash_bound_adapted_comparison_receipt_passes(self):
        body = self.evidence_item['bodies'][1]
        body.update(method='bounded_source_comparison', fidelity_receipt='sources/1001/fidelity.json')
        receipt = dict(schema_version=1, checked=True, item_sha256=self.row['tex_sha256'],
                       body_sha256=body['tex_sha256'], source_sha256=digest(self.raw), role='primary_proof',
                       checked_at='2026-10-02T00:00:00+00:00', method='retained-source-page-comparison',
                       note='Existing bounded check of this exact source and body.', source_locator={'lines': [3, 3]})
        (self.package / body['fidelity_receipt']).write_text(json.dumps(receipt))
        self.save()
        result, _ = self.run_gate()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_complete_author_construction_needs_no_proof_environment(self):
        narrative = 'The author constructs the required object here, with the complete original argument.'
        self.tex = self.tex.replace(self.proof, narrative)
        self.raw = self.raw.replace(self.proof, narrative)
        self.proof = narrative
        (self.package / self.row['item_path']).write_text(self.tex)
        (self.sources / 'raw/source.tex').write_text(self.raw)
        (self.package / self.row['primary']['excerpt_path']).write_text(self.statement + '\n' + self.proof + '\n')
        self.row['tex_sha256'] = self.receipt['input_sha256'] = self.evidence_item['item_sha256'] = digest(self.tex)
        self.row['primary']['source_sha256'] = self.evidence_item['sources'][0]['sha256'] = digest(self.raw)
        self.row['primary']['excerpt_sha256'] = digest(self.statement + '\n' + self.proof + '\n')
        self.evidence_item['bodies'][1]['tex_sha256'] = digest(narrative)
        self.save()
        result, _ = self.run_gate()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_declared_context_cannot_be_missing_from_delivered_bodies(self):
        context = 'Necessary original core construction.'
        (self.package / 'sources/1001/context.tex').write_text(context)
        self.row['contexts'] = [dict(excerpt_path='sources/1001/context.tex', excerpt_sha256=digest(context),
                                     source_sha256=digest(self.raw), start_line=2, end_line=2)]
        self.save()
        self.assert_fails('declared context body absent')

    def test_mapped_native_excerpt_adapter_binds_source_ranges(self):
        sys.path.insert(0, str(ROOT / 'scripts'))
        try:
            import derive_stacks_evidence as derive
            self.assertTrue(hasattr(derive, 'derive_mapped'), 'mapped source-range adapter is missing')
            self.row['source_id'] = 'doi:example-native-source'
            self.row['primary'] = dict(source_tex_sha256=digest(self.raw), source_map_path='sources/1001/source-map.json',
                                       statement_source_lines=[[2, 2]], proof_source_lines=[[3, 3]])
            self.row['source_check'] = dict(checks=['complete author primary proof and required context preserved'], note='Existing bounded source review.')
            excerpt = '% Original source lines 2--3\n' + self.statement + '\n' + self.proof + '\n'
            (self.package / 'sources/1001/author-excerpts.tex').write_text(excerpt)
            mapping = dict(source_tex_sha256=digest(self.raw), blocks=[dict(source_lines=[2,3], content_sha256_lf=digest(self.statement+'\n'+self.proof+'\n'))],
                           statement_source_lines=[[2,2]], proof_source_lines=[[3,3]])
            (self.package / 'sources/1001/source-map.json').write_text(json.dumps(mapping))
            entry = derive.derive_mapped(self.package, self.row, self.sources, '2026-10-02T00:00:00+00:00')
            self.assertEqual([b['role'] for b in entry['bodies'] if b['role'].startswith('primary_')], ['primary_statement','primary_proof'])
            self.assertEqual(entry['bodies'][1]['tex_sha256'], digest(self.proof))
        finally:
            sys.path.pop(0)

    def test_staged_skill_separates_current_delivery_from_historical_wrapper_gate(self):
        skill = (ROOT / 'docs/editable-gate/proposed-SKILL.md').read_text()
        self.assertIn('--mode editable-delivery', skill)
        self.assertIn('Historical evidence-only workflow', skill)
        self.assertIn('problems.tex_content', skill)
        self.assertIn('editable_qualified_count', skill)
        self.assertNotIn('Final qualified count comes from validation_report.json', skill)

    def test_inline_hash_bound_comparison_receipt_is_supported(self):
        body = self.evidence_item['bodies'][1]
        body.update(method='bounded_source_comparison', fidelity_receipt=dict(schema_version=1, checked=True,
                    item_sha256=self.row['tex_sha256'], body_sha256=body['tex_sha256'], source_sha256=digest(self.raw),
                    role='primary_proof', checked_at='2026-10-02T00:00:00+00:00',
                    method='existing-source-fidelity-record-current-byte-binding', note='No new source review.',
                    source_locator={'lines':[3,3]}))
        self.save()
        result, _ = self.run_gate()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_newline_byte_change_cannot_hide_stale_compile_input(self):
        path=self.package/self.row['item_path']
        path.write_bytes(path.read_bytes().replace(b'\n',b'\r\n'))
        self.assert_fails('delivered TeX hash')

    def test_optional_exclusions_cannot_remove_known_source_holds(self):
        self.row['problem_id']='2604'
        self.save()
        extra=self.root/'empty-exclusions.json'
        extra.write_text(json.dumps(dict(schema_version=1,decisions=[])))
        self.assert_fails('Statement/proof correspondence hold','--exclusions',str(extra))

    def test_boolean_schema_version_is_not_supported(self):
        self.evidence['schema_version']=True
        self.save()
        self.assert_fails('evidence schema')

    def test_bare_legacy_item_cli_cannot_claim_qualification(self):
        import test_pipeline as fixtures
        legacy=fixtures.Pipeline()
        legacy.setUp()
        self.addCleanup(legacy.tearDown)
        result=subprocess.run([sys.executable,str(CLI),'--root',str(legacy.root),'--item','1001'],capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0)
        self.assertIn('explicit --mode',result.stdout+result.stderr)
        self.assertFalse((legacy.c/'.work/validation_report.json').exists())

    def test_package_supplied_without_mode_selects_editable_delivery(self):
        result=subprocess.run([sys.executable,str(CLI),'--package',str(self.package),'--evidence',str(self.root/'evidence.json'),
                               '--source-root',str(self.sources),'--build-root',str(self.package/'build'),'--item','1001'],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertEqual(json.loads(result.stdout)['mode'],'editable-delivery')

    def test_existing_excerpt_binding_adapter_preserves_current_hashes(self):
        sys.path.insert(0,str(ROOT/'scripts'))
        try:
            import derive_stacks_evidence as derive
            self.assertTrue(hasattr(derive,'derive_existing_bindings'),'existing exact fidelity-binding adapter is missing')
            self.row['source_check']=dict(checks=['complete author primary proof and required context preserved'],note='Existing bounded check.')
            record=dict(problem_id='1001',delivered_tex_sha256=self.row['tex_sha256'],derivation='Existing deterministic reference-only transformation.',bindings=[
                dict(original_excerpt='1001/source-excerpts/primary.tex',original_sha256=self.row['primary']['excerpt_sha256'],
                     source_start_line=2,source_end_line=3,delivered_start_line=3,delivered_end_line=4,
                     deterministic_adapted_excerpt_sha256=digest(self.statement+'\n'+self.proof+'\n'),verified_contiguous_substring=True)])
            entry=derive.derive_existing_bindings(self.package,self.row,record,'2026-10-02T00:00:00+00:00')
            self.assertEqual(entry['bodies'][0]['role'],'primary_statement')
            self.assertEqual(entry['bodies'][1]['role'],'primary_proof')
            self.assertEqual(entry['bodies'][1]['tex_sha256'],digest(self.proof))
        finally:
            sys.path.pop(0)

    def test_asset_path_adaptation_requires_identical_options_and_declared_asset(self):
        old=r'\includegraphics[width=1cm]{plot.pdf}'
        new=r'\includegraphics[width=1cm]{./plot.pdf}'
        self.raw=self.raw.replace('author argument.','author argument. '+old)
        self.tex=self.tex.replace('author argument.','author argument. '+new)
        self.proof=self.tex.splitlines()[3]
        (self.sources/'raw/source.tex').write_text(self.raw)
        (self.package/self.row['item_path']).write_text(self.tex)
        excerpt=self.statement+'\n'+self.raw.splitlines()[2]+'\n'
        (self.package/self.row['primary']['excerpt_path']).write_text(excerpt)
        (self.package/'items/plot.pdf').write_bytes(b'%PDF-fixture-figure')
        self.row['asset_dependencies']=[dict(path='items/plot.pdf',sha256=digest(b'%PDF-fixture-figure'))]
        self.receipt['dependency_sha256']={'items/plot.pdf':digest(b'%PDF-fixture-figure')}
        self.row['tex_sha256']=self.receipt['input_sha256']=self.evidence_item['item_sha256']=digest(self.tex)
        self.row['primary']['source_sha256']=self.evidence_item['sources'][0]['sha256']=digest(self.raw)
        self.row['primary']['excerpt_sha256']=digest(excerpt)
        self.evidence_item['bodies'][1].update(tex_sha256=digest(self.proof),method='literal_asset_path_adaptation',replacements=[dict(original=old,delivered=new)])
        self.save()
        result,_=self.run_gate()
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)

    def inline_source(self):
        self.evidence_item['sources']=[dict(root='inline',inline_text=self.raw,sha256=digest(self.raw),
            original_source_sha256=digest(self.raw),original_locator=dict(source_file='raw/source.tex',source_version='revision1',lines=[1,3]))]

    def test_portable_inline_original_source_excerpt_passes(self):
        self.inline_source();self.save()
        (self.sources/'raw/source.tex').unlink()
        result,_=self.run_gate();self.assertEqual(result.returncode,0,result.stdout+result.stderr)

    def test_altered_inline_original_source_hash_fails(self):
        self.inline_source();self.evidence_item['sources'][0]['inline_text']=self.raw.replace('author','robot');self.save()
        self.assert_fails('declared source hash')

    def test_inline_and_file_source_forms_are_mutually_exclusive(self):
        self.inline_source();self.evidence_item['sources'][0]['path']='raw/source.tex';self.save()
        self.assert_fails('mutually exclusive')

    def test_inline_original_source_locator_is_required(self):
        self.inline_source();self.evidence_item['sources'][0].pop('original_locator');self.save()
        self.assert_fails('inline original source locator')

    def test_worker_native_primary_binding_adapter_keeps_exact_inline_originals(self):
        sys.path.insert(0,str(ROOT/'scripts'))
        try:
            import derive_stacks_evidence as derive
            self.assertTrue(hasattr(derive,'derive_native_worker_binding'),'native worker-binding adapter missing')
            self.row['source_check']=dict(checks=['full original author body and required local support retained'],note='Existing bounded source review.')
            record=dict(id='1001',delivered_input_sha256=digest(self.tex),native_source='raw/source.tex',native_source_sha256=digest(self.raw),bindings=[
                dict(role='primary_statement',native_source_lines_1based=[2,2],native_excerpt_sha256=digest(self.statement+'\n'),delivered_item_lines_1based=[3,3],delivered_span_sha256=digest(self.statement+'\n'),author_math_text_unchanged=True),
                dict(role='complete_primary_proof',native_source_lines_1based=[3,3],native_excerpt_sha256=digest(self.proof+'\n'),delivered_item_lines_1based=[4,4],delivered_span_sha256=digest(self.proof+'\n'),author_math_text_unchanged=True)],publication_transformations=[],scope='Existing source-worker binding; no new review.')
            entry=derive.derive_native_worker_binding(self.package,self.row,record,self.sources,'2026-10-02T00:00:00+00:00')
            self.assertEqual(entry['sources'][0]['inline_text'],self.statement+'\n')
            self.assertEqual(entry['bodies'][1]['role'],'primary_proof')
        finally:
            sys.path.pop(0)

    def test_retained_page_excerpt_adapter_uses_existing_exact_hashes(self):
        sys.path.insert(0,str(ROOT/'scripts'))
        try:
            import derive_stacks_evidence as derive
            self.assertTrue(hasattr(derive,'derive_retained_page_excerpts'),'retained-page excerpt adapter missing')
            self.row['primary']=dict(source_sha256=digest(b'Original PDF'),statement_pages=[1],proof_pages=[2],source_map_path='sources/1001/source-map.json')
            self.row['source_check']=dict(checks=['complete author primary proof and required context preserved'],note='Existing bounded page comparison.')
            content=self.statement+'\n'+self.proof+'\n'
            (self.package/'sources/1001/original-body.tex').write_text(content)
            mapping=dict(source_sha256=digest(b'Original PDF'),author_page_tex_line_spans=[
                dict(source_page='1',tex_path='sources/1001/original-body.tex',start_line=1,end_line=1,excerpt_sha256=digest(self.statement+'\n')),
                dict(source_page='2',tex_path='sources/1001/original-body.tex',start_line=2,end_line=2,excerpt_sha256=digest(self.proof+'\n'))])
            entry=derive.derive_retained_page_excerpts(self.package,self.row,mapping,'2026-10-02T00:00:00+00:00')
            self.assertEqual(entry['bodies'][0]['role'],'primary_statement')
            self.assertEqual(entry['bodies'][1]['tex_sha256'],digest(self.proof))
        finally:
            sys.path.pop(0)

    def test_existing_reviewed_transcription_units_rebind_without_new_review(self):
        sys.path.insert(0,str(ROOT/'scripts'))
        try:
            import derive_stacks_evidence as derive
            self.assertTrue(hasattr(derive,'derive_reviewed_transcription'),'reviewed-transcription adapter missing')
            self.row['primary']=dict(source_sha256=digest(b'Original PDF'),statement_pages=[1],proof_pages=[2],source_locator={'theorem':'Theorem1.4'})
            self.row['source_check']=dict(checks=['complete author primary proof and required context preserved'],note='Existing bounded transcription/source page comparison.')
            mapping=dict(original_sha256=digest(b'Original PDF'),author_text_units=[
                dict(unit='Complete Theorem1.4 statement',physical_pages=[1],tex_line_start=2,tex_line_end=2),
                dict(unit='Complete authored Proof of Theorem1.4',physical_pages=[2],tex_line_start=3,tex_line_end=3)])
            qa=dict(source_sha256=digest(b'Original PDF'),tex_sha256=digest(self.raw),full_editable_statement_and_author_proof=True,
                    source_formulas_and_arrows_compared=True,authored_proofs_complete=['Theorem1.4'],comparison_method='Existing actual original source comparison.')
            entry=derive.derive_reviewed_transcription(self.package,self.row,mapping,qa,self.raw,'existing.tex','2026-10-02T00:00:00+00:00')
            self.assertEqual(entry['sources'][1]['inline_text'],self.proof+'\n')
            self.assertEqual(entry['bodies'][1]['role'],'primary_proof')
        finally:
            sys.path.pop(0)

    def test_external_receipt_set_can_be_selected_without_changing_packaged_receipt(self):
        external=self.root/'new-receipts';external.mkdir()
        (external/'1001.json').write_text(json.dumps(self.receipt))
        (self.package/self.row['compile_receipt']).unlink()
        result,report=self.run_gate('--receipt-root',str(external))
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertEqual(report['receipt_set'],str(external.resolve()))

    def test_stale_external_receipt_input_is_rejected(self):
        external=self.root/'new-receipts';external.mkdir()
        receipt=dict(self.receipt,input_sha256='0'*64)
        (external/'1001.json').write_text(json.dumps(receipt))
        self.assert_fails('compile input hash','--receipt-root',str(external))

    def test_external_receipt_artifact_paths_cannot_escape_build_root(self):
        external=self.root/'new-receipts';external.mkdir()
        receipt=dict(self.receipt,pdf_path='../outside.pdf')
        (external/'1001.json').write_text(json.dumps(receipt))
        self.assert_fails('escaping declared file','--receipt-root',str(external))

    def test_checkout_compile_helper_keeps_package_unchanged(self):
        helper=ROOT/'scripts/compile_editable_delivery.py'
        self.assertTrue(helper.is_file(),'checkout compile helper missing')
        engine=self.root/'fake-xelatex'
        engine.write_text('#!'+sys.executable+'\nimport sys\nfrom pathlib import Path\nfrom pypdf import PdfWriter\na=sys.argv[1:]\nassert "-no-shell-escape" in a\nout=Path(next(x.split("=",1)[1] for x in a if x.startswith("-output-directory=")))\ntex=Path(a[-1]);base=out/tex.stem\nw=PdfWriter();w.add_blank_page(width=100,height=100)\nwith base.with_suffix(".pdf").open("wb") as f:w.write(f)\nbase.with_suffix(".log").write_text("Successful fixture pass")\nbase.with_suffix(".fls").write_text("INPUT "+str(tex.resolve())+"\\n")\n')
        engine.chmod(0o755)
        before={str(p.relative_to(self.package)):digest(p.read_bytes())for p in self.package.rglob('*')if p.is_file()}
        build=self.root/'checkout-build';receipts=self.root/'checkout-receipts'
        result=subprocess.run([sys.executable,str(helper),'--package',str(self.package),'--build-root',str(build),
                               '--receipt-root',str(receipts),'--engine',str(engine),'--item','1001'],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        actual=json.loads((receipts/'1001.json').read_text());self.assertTrue(actual['ok']);self.assertEqual(actual['passes'],2)
        after={str(p.relative_to(self.package)):digest(p.read_bytes())for p in self.package.rglob('*')if p.is_file()}
        self.assertEqual(before,after)

    def test_checkout_compile_helper_refuses_output_inside_package(self):
        helper=ROOT/'scripts/compile_editable_delivery.py'
        self.assertTrue(helper.is_file(),'checkout compile helper missing')
        result=subprocess.run([sys.executable,str(helper),'--package',str(self.package),'--build-root',str(self.package/'overwrite-build'),
                               '--receipt-root',str(self.root/'receipts')],capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0)
        self.assertIn('outside',result.stdout+result.stderr)

    def test_stale_external_receipt_asset_is_rejected(self):
        external=self.root/'new-receipts';external.mkdir()
        (self.package/'items/figure.png').write_bytes(b'original figure')
        self.row['asset_dependencies']=[dict(path='items/figure.png',sha256=digest(b'original figure'))]
        self.receipt['dependency_sha256']={'items/figure.png':digest(b'original figure')}
        self.save();(external/'1001.json').write_text(json.dumps(self.receipt))
        (self.package/'items/figure.png').write_bytes(b'changed figure')
        self.assert_fails('asset dependency hash','--receipt-root',str(external))

    def test_checkout_compile_helper_rejects_undeclared_graphic_before_engine(self):
        self.tex += '\n'+r'\includegraphics{../../outside.pdf}'
        self.row['tex_sha256']=digest(self.tex)
        (self.package/self.row['item_path']).write_text(self.tex);self.save()
        helper=ROOT/'scripts/compile_editable_delivery.py';receipts=self.root/'receipts'
        result=subprocess.run([sys.executable,str(helper),'--package',str(self.package),'--build-root',str(self.root/'build'),
                               '--receipt-root',str(receipts),'--engine','true','--item','1001'],capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0)
        self.assertIn('undeclared figure',json.loads((receipts/'1001.json').read_text())['error'])

    def test_checkout_compile_helper_rejects_escaping_log_symlink(self):
        build=self.root/'build';(build/'1001').mkdir(parents=True)
        outside=self.root/'outside.log';outside.write_text('must remain unchanged')
        (build/'1001/compiler.log').symlink_to(outside)
        helper=ROOT/'scripts/compile_editable_delivery.py';receipts=self.root/'receipts'
        result=subprocess.run([sys.executable,str(helper),'--package',str(self.package),'--build-root',str(build),
                               '--receipt-root',str(receipts),'--engine','true','--item','1001'],capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0)
        self.assertIn('escapes external',json.loads((receipts/'1001.json').read_text())['error'])
        self.assertEqual(outside.read_text(),'must remain unchanged')

    def test_declared_package_manifest_binding_cannot_be_stale(self):
        self.evidence['package_manifest_sha256']='0'*64
        self.save();self.assert_fails('evidence package manifest hash')

    def test_reference_display_allows_only_known_literal_text_escapes(self):
        old=r"\cite[Expos\'e V]{SGA1}"
        new=r"\href{https://stacks.math.columbia.edu/bibliography}{Bibliography: SGA1 (Expos\textbackslash{}'e V)}"
        self.raw=self.raw.replace('author argument.','author argument using '+old+'.')
        self.tex=self.tex.replace('author argument.','author argument using '+new+'.')
        self.proof=self.tex.splitlines()[3]
        (self.sources/'raw/source.tex').write_text(self.raw)
        (self.package/self.row['item_path']).write_text(self.tex)
        excerpt=self.statement+'\n'+self.raw.splitlines()[2]+'\n'
        (self.package/self.row['primary']['excerpt_path']).write_text(excerpt)
        self.row['tex_sha256']=self.receipt['input_sha256']=self.evidence_item['item_sha256']=digest(self.tex)
        self.row['primary']['source_sha256']=self.evidence_item['sources'][0]['sha256']=digest(self.raw)
        self.row['primary']['excerpt_sha256']=digest(excerpt)
        self.evidence_item['bodies'][1].update(tex_sha256=digest(self.proof),method='reference_only_adaptation',replacements=[dict(original=old,delivered=new)])
        self.save();result,_=self.run_gate();self.assertEqual(result.returncode,0,result.stdout+result.stderr)

    def test_reference_display_still_rejects_arbitrary_nested_tex(self):
        self.evidence_item['bodies'][1].update(method='reference_only_adaptation',replacements=[dict(
            original=r'\ref{source}',delivered=r'\href{https://example.org/source}{\texttt{invented nested text}}')])
        self.save();self.assert_fails('unsupported reference-only replacement')

    def stabilization_engine(self,stable_at):
        engine=self.root/'stabilizing-xelatex'
        engine.write_text('#!'+sys.executable+'\nimport sys\nfrom pathlib import Path\nfrom pypdf import PdfWriter\na=sys.argv[1:];out=Path(next(x.split("=",1)[1] for x in a if x.startswith("-output-directory=")))\ntex=Path(a[-1]);base=out/tex.stem;c=out/"calls.txt"\nn=int(c.read_text())+1 if c.exists() else 1;c.write_text(str(n))\nw=PdfWriter();w.add_blank_page(width=100,height=100)\nwith base.with_suffix(".pdf").open("wb") as f:w.write(f)\nbase.with_suffix(".log").write_text("LaTeX Warning: Label(s) may have changed. Rerun to get cross-references right." if n<'+str(stable_at)+' else "Stable final pass")\nbase.with_suffix(".fls").write_text("INPUT "+str(tex.resolve())+"\\n")\n')
        engine.chmod(0o755);return engine

    def test_checkout_compile_helper_stabilizes_page_labels(self):
        engine=self.stabilization_engine(3)
        engine.write_text(engine.read_text().replace('LaTeX Warning: Label(s) may have changed. Rerun to get cross-references right.', 'Package hyperref Warning: Rerun to get /PageLabels entry.'))
        receipts=self.root/'receipts'
        result=subprocess.run([sys.executable,str(ROOT/'scripts/compile_editable_delivery.py'),'--package',str(self.package),
            '--build-root',str(self.root/'build'),'--receipt-root',str(receipts),'--engine',str(engine),'--item','1001'],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        receipt=json.loads((receipts/'1001.json').read_text())
        self.assertEqual(receipt['passes'],3)
        self.assertEqual(receipt['rerun_requests'],[])

    def test_checkout_compile_helper_rejects_duplicate_labels(self):
        engine=self.stabilization_engine(1)
        engine.write_text(engine.read_text().replace('"Stable final pass"',repr("LaTeX Warning: Label `same' multiply defined.")))
        receipts=self.root/'receipts'
        result=subprocess.run([sys.executable,str(ROOT/'scripts/compile_editable_delivery.py'),'--package',str(self.package),
            '--build-root',str(self.root/'build'),'--receipt-root',str(receipts),'--engine',str(engine),'--item','1001'],capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0)
        receipt=json.loads((receipts/'1001.json').read_text())
        self.assertFalse(receipt['ok'])
        self.assertIn('multiply-defined',receipt['error'])

    def test_checkout_compile_helper_runs_third_pass_when_labels_request_it(self):
        engine=self.stabilization_engine(3);receipts=self.root/'receipts'
        result=subprocess.run([sys.executable,str(ROOT/'scripts/compile_editable_delivery.py'),'--package',str(self.package),
            '--build-root',str(self.root/'build'),'--receipt-root',str(receipts),'--engine',str(engine),'--item','1001'],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        receipt=json.loads((receipts/'1001.json').read_text());self.assertTrue(receipt['ok']);self.assertEqual(receipt['passes'],3)
        self.assertEqual(receipt['rerun_requests'],[])

    def test_checkout_compile_helper_fails_if_labels_never_stabilize_at_four_passes(self):
        engine=self.stabilization_engine(999);receipts=self.root/'receipts'
        result=subprocess.run([sys.executable,str(ROOT/'scripts/compile_editable_delivery.py'),'--package',str(self.package),
            '--build-root',str(self.root/'build'),'--receipt-root',str(receipts),'--engine',str(engine),'--item','1001'],capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0)
        receipt=json.loads((receipts/'1001.json').read_text());self.assertFalse(receipt['ok']);self.assertEqual(receipt['passes'],4)
        self.assertIn('did not stabilize',receipt['error'])

    def test_explicit_unstable_reference_receipt_cannot_qualify(self):
        self.receipt['rerun_requests']=['Label(s) may have changed']
        self.save();self.assert_fails('compile receipt failed')

    def test_rerunfilecheck_package_banner_is_not_a_rerun_request(self):
        engine=self.stabilization_engine(1)
        engine.write_text(engine.read_text().replace('"Stable final pass"',repr('Package: rerunfilecheck 2022-07-10 v1.10 Rerun checks for auxiliary files (HO)')))
        receipts=self.root/'receipts'
        result=subprocess.run([sys.executable,str(ROOT/'scripts/compile_editable_delivery.py'),'--package',str(self.package),
            '--build-root',str(self.root/'build'),'--receipt-root',str(receipts),'--engine',str(engine),'--item','1001'],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        receipt=json.loads((receipts/'1001.json').read_text());self.assertEqual(receipt['passes'],2);self.assertEqual(receipt['rerun_requests'],[])

    def test_exact_page_map_adapter_binds_retained_statement_and_proof(self):
        sys.path.insert(0,str(ROOT / 'scripts'))
        try:
            import derive_stacks_evidence as derive
            self.assertTrue(hasattr(derive,'derive_page_map'),'page-map adapter is missing')
            self.row['primary'] = dict(source_sha256=digest(b'original PDF'), source_map_path='sources/1001/source-map.json', statement_pages=[1],proof_pages=[2])
            self.row['source_check'] = dict(checks=['complete author primary proof and required context preserved'],note='Existing declared full bounded source check.')
            mapping = dict(source_sha256=digest(b'original PDF'), blocks=[
                dict(block_id='T1',tex_first_line=3,tex_last_line=3,tex_block_sha256=digest(self.statement+'\n'),source_language_and_mathematical_order_preserved=True,fresh_source_boundary_comparison='Original full statement compared.'),
                dict(block_id='P1',tex_first_line=4,tex_last_line=4,tex_block_sha256=digest(self.proof+'\n'),source_language_and_mathematical_order_preserved=True,fresh_source_boundary_comparison='Original full author proof compared.')])
            (self.package / self.row['primary']['source_map_path']).write_text(json.dumps(mapping))
            entry = derive.derive_page_map(self.package,self.row,mapping,'2026-10-02T00:00:00+00:00')
            self.assertEqual(entry['bodies'][0]['role'],'primary_statement')
            self.assertEqual(entry['bodies'][1]['role'],'primary_proof')
            self.assertEqual(entry['bodies'][1]['tex_sha256'],digest(self.proof))
        finally:
            sys.path.pop(0)


if __name__ == '__main__':
    unittest.main()
