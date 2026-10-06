"""Run actual SQLite DDL; test only the narrow origin enum and existing constraints."""
import sqlite3
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
NEW = 'human_authored_checked_published_transcription'
OLD = ('human_authored_native_tex', 'human_authored_proof_assistant_transcription')
SOURCE_COLUMNS = ('source_id', 'author', 'work', 'source_url', 'source_version', 'retrieved_at', 'license', 'license_path')
PROBLEM_COLUMNS = ('problem_id', 'title', 'difficulty_level', 'difficulty_reason', 'source_id', 'source_locator_json',
                   'tex_path', 'tex_content', 'tex_sha256', 'origin_class', 'status', 'compile_receipt_path')
SOURCE = dict(zip(SOURCE_COLUMNS, ('source:fixture', 'Named human author', 'Published work', 'https://example.org/source',
                                  'version1', '2026-10-02', 'Fixture license', 'licenses/source.txt')))
PROBLEM = dict(zip(PROBLEM_COLUMNS, ('2445', 'Source-grounded statement', 'H2', 'Bounded fixture reason', 'source:fixture',
                                    '{"primary":{},"contexts":[]}', 'items/2445_author_proof.tex',
                                    '\\documentclass{article}\\begin{document}Fixture\\end{document}', '0' * 64,
                                    NEW, 'verified_editable_tex', 'receipts/2445.json')))


class SchemaEnum(unittest.TestCase):
    def database(self, filename='schema.sql', source=True):
        db = sqlite3.connect(':memory:')
        self.addCleanup(db.close)
        db.executescript((ROOT / filename).read_text(encoding='utf-8'))
        self.assertEqual(db.execute('PRAGMA foreign_keys').fetchone()[0], 1)
        if source:
            self.insert_source(db)
        return db

    def insert_source(self, db, **changes):
        row = dict(SOURCE, **changes)
        db.execute('INSERT INTO sources VALUES (?,?,?,?,?,?,?,?)', tuple(row[k] for k in SOURCE_COLUMNS))

    def insert_problem(self, db, **changes):
        row = dict(PROBLEM, **changes)
        db.execute('INSERT INTO problems VALUES (?,?,?,?,?,?,?,?,?,?,?,?)', tuple(row[k] for k in PROBLEM_COLUMNS))

    def test_new_origin_is_accepted_by_actual_schema(self):
        db = self.database()
        try:
            self.insert_problem(db)
        except sqlite3.IntegrityError as exc:
            self.fail('new accurate origin rejected by actual SQLite DDL: ' + str(exc))
        self.assertEqual(db.execute('SELECT origin_class FROM problems').fetchone()[0], NEW)
        self.assertEqual(db.execute('PRAGMA integrity_check').fetchone()[0], 'ok')
        self.assertEqual(db.execute('PRAGMA foreign_key_check').fetchall(), [])

    def test_historical_schema_rejects_new_origin(self):
        db = self.database('schema.before.sql')
        with self.assertRaisesRegex(sqlite3.IntegrityError, 'CHECK constraint failed: origin_class IN'):
            self.insert_problem(db)
        self.assertEqual(db.execute('SELECT count(*) FROM problems').fetchone()[0], 0)

    def test_old_origins_remain_accepted_in_old_and_new_schema(self):
        for filename in ['schema.before.sql', 'schema.sql']:
            for origin in OLD:
                with self.subTest(schema=filename, origin=origin):
                    db = self.database(filename)
                    self.insert_problem(db, origin_class=origin)
                    self.assertEqual(db.execute('SELECT origin_class FROM problems').fetchone()[0], origin)

    def test_unknown_origins_remain_rejected(self):
        for value in ['unknown', 'ai_generated', '', NEW.upper(), NEW + ' ', 1, False]:
            with self.subTest(origin=value):
                db = self.database()
                with self.assertRaisesRegex(sqlite3.IntegrityError, 'CHECK constraint failed: origin_class IN'):
                    self.insert_problem(db, origin_class=value)
                self.assertEqual(db.execute('SELECT count(*) FROM problems').fetchone()[0], 0)

    def test_all_three_existing_difficulty_levels_remain_accepted(self):
        for level in ['H1', 'H2', 'H3']:
            with self.subTest(level=level):
                db = self.database()
                self.insert_problem(db, difficulty_level=level)
                self.assertEqual(db.execute('SELECT difficulty_level FROM problems').fetchone()[0], level)

    def test_invalid_difficulty_remains_rejected_for_new_origin(self):
        for value in ['H0', 'H4', '', 'h2', 'H2 ', 2, False]:
            with self.subTest(difficulty=value):
                db = self.database()
                with self.assertRaisesRegex(sqlite3.IntegrityError, 'CHECK constraint failed: difficulty_level IN'):
                    self.insert_problem(db, difficulty_level=value)

    def test_invalid_status_remains_rejected_for_new_origin(self):
        for value in ['pending', 'source_body_compile_checked_pending_origin_gate', '', 'verified_editable_tex ', 1, False]:
            with self.subTest(status=value):
                db = self.database()
                with self.assertRaisesRegex(sqlite3.IntegrityError, 'CHECK constraint failed: status='):
                    self.insert_problem(db, status=value)

    def test_duplicate_problem_id_remains_rejected(self):
        db = self.database()
        self.insert_problem(db)
        with self.assertRaisesRegex(sqlite3.IntegrityError, 'UNIQUE constraint failed: problems.problem_id'):
            self.insert_problem(db, tex_path='items/2446_other_path.tex')
        self.assertEqual(db.execute('SELECT count(*) FROM problems').fetchone()[0], 1)

    def test_duplicate_tex_path_remains_rejected(self):
        db = self.database()
        self.insert_problem(db)
        with self.assertRaisesRegex(sqlite3.IntegrityError, 'UNIQUE constraint failed: problems.tex_path'):
            self.insert_problem(db, problem_id='2446')
        self.assertEqual(db.execute('SELECT count(*) FROM problems').fetchone()[0], 1)

    def test_duplicate_source_id_remains_rejected(self):
        db = self.database()
        with self.assertRaisesRegex(sqlite3.IntegrityError, 'UNIQUE constraint failed: sources.source_id'):
            self.insert_source(db)
        self.assertEqual(db.execute('SELECT count(*) FROM sources').fetchone()[0], 1)

    def test_missing_foreign_source_remains_rejected(self):
        db = self.database()
        with self.assertRaisesRegex(sqlite3.IntegrityError, 'FOREIGN KEY constraint failed'):
            self.insert_problem(db, source_id='source:missing')
        self.assertEqual(db.execute('SELECT count(*) FROM problems').fetchone()[0], 0)

    def test_referenced_source_cannot_be_deleted(self):
        db = self.database()
        self.insert_problem(db)
        with self.assertRaisesRegex(sqlite3.IntegrityError, 'FOREIGN KEY constraint failed'):
            db.execute('DELETE FROM sources')
        self.assertEqual(db.execute('SELECT count(*) FROM sources').fetchone()[0], 1)

    def test_foreign_key_update_still_rejects_missing_source(self):
        db = self.database()
        self.insert_problem(db)
        with self.assertRaisesRegex(sqlite3.IntegrityError, 'FOREIGN KEY constraint failed'):
            db.execute("UPDATE problems SET source_id='source:missing'")
        self.assertEqual(db.execute('SELECT source_id FROM problems').fetchone()[0], SOURCE['source_id'])

    def test_existing_source_not_null_constraints_remain(self):
        for field in SOURCE_COLUMNS[1:]:
            with self.subTest(field=field):
                db = self.database(source=False)
                with self.assertRaisesRegex(sqlite3.IntegrityError, 'NOT NULL constraint failed: sources.' + field):
                    self.insert_source(db, **{field: None})

    def test_existing_problem_not_null_constraints_remain_including_paths(self):
        for field in PROBLEM_COLUMNS[1:]:
            with self.subTest(field=field):
                db = self.database()
                with self.assertRaisesRegex(sqlite3.IntegrityError, 'NOT NULL constraint failed: problems.' + field):
                    self.insert_problem(db, **{field: None})

    def test_only_exact_origin_enum_bytes_change(self):
        before = (ROOT / 'schema.before.sql').read_bytes()
        after = (ROOT / 'schema.sql').read_bytes()
        old_enum = b"origin_class IN ('human_authored_native_tex','human_authored_proof_assistant_transcription')"
        new_enum = b"origin_class IN ('human_authored_native_tex','human_authored_proof_assistant_transcription','human_authored_checked_published_transcription')"
        self.assertEqual(before.count(old_enum), 1)
        self.assertEqual(after, before.replace(old_enum, new_enum, 1))
        self.assertEqual(after.count(NEW.encode()), 1)

    def test_tables_columns_indices_and_foreign_key_structure_unchanged(self):
        before = self.database('schema.before.sql', source=False)
        after = self.database('schema.sql', source=False)
        for db in [before, after]:
            self.assertEqual(db.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall(),
                             [('problems',), ('sources',)])
            self.assertEqual(db.execute("SELECT count(*) FROM sqlite_master WHERE type='trigger'").fetchone()[0], 0)
        for table in ['sources', 'problems']:
            for pragma in ['table_info', 'index_list', 'foreign_key_list']:
                self.assertEqual(before.execute('PRAGMA '+pragma+'('+table+')').fetchall(),
                                 after.execute('PRAGMA '+pragma+'('+table+')').fetchall())


if __name__ == '__main__':
    unittest.main()
