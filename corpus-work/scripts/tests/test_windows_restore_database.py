"""A verified temporary SQLite file must be closable for atomic publication."""
import gc
import hashlib
import importlib.util
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location("restore_database", REPO / "editable-corpus/restore_database.py")
restore = importlib.util.module_from_spec(spec)
spec.loader.exec_module(restore)


class WindowsRestoreTests(unittest.TestCase):
    @unittest.skipUnless(sys.platform == "win32", "Windows denies renaming SQLite files with open handles")
    def test_validation_releases_handle_before_atomic_publish(self):
        root = Path(tempfile.mkdtemp(prefix="corpus-restore-handle-"))
        text = "\\begin{document}Author proof\\end{document}\n"
        (root / "one.tex").write_text(text, encoding="utf8", newline="\n")
        digest = hashlib.sha256(text.encode()).hexdigest()
        path = root / "staging.sqlite"
        db = sqlite3.connect(path)
        db.execute("CREATE TABLE problems(problem_id TEXT,status TEXT,tex_content TEXT,tex_sha256 TEXT,source_id TEXT)")
        db.execute("INSERT INTO problems VALUES(?,?,?,?,?)", ("001", "verified_editable_tex", text, digest, "source-one"))
        db.commit(); db.close()
        manifest = {"items": [dict(problem_id="001", status="verified_editable_tex", item_path="one.tex",
                                    tex_sha256=digest, source_id="source-one")]}
        enabled = gc.isenabled(); gc.disable()
        try:
            restore.validate_database(path, root, manifest, 1)
            path.rename(root / "published.sqlite")
            self.assertTrue((root / "published.sqlite").exists())
        finally:
            if enabled:
                gc.enable()
            gc.collect()


if __name__ == "__main__":
    unittest.main()
