"""Synthetic transport fault tests; no corpus gates, source work or public evidence."""
import hashlib
import json
from pathlib import Path
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import prepare_public_transport as transport


def save(path, value):
    path.write_text(json.dumps(value), encoding="utf8")
    return transport.digest(path)


def entry(name, content):
    return {"path": name, "bytes": len(content), "sha256": hashlib.sha256(content).hexdigest()}


class ResumeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.cache = self.root / "cache"
        self.cache.mkdir()
        self.stable = b"cached successful original"
        self.fresh = b"new exact public bytes"
        (self.cache / "a-stable.txt").write_bytes(self.stable)
        self.old = self.root / "old.json"
        self.old_pin = save(self.old, {"schema_version": 1, "files": [entry("a-stable.txt", self.stable)]})
        self.current = self.root / "current.json"
        self.current_pin = save(self.current, {"schema_version": 1, "files": [entry("a-stable.txt", self.stable), entry("z-fresh.txt", self.fresh)]})
        self.proof = self.root / "proof.json"
        self.old_commit = "1" * 40
        self.proof_pin = save(self.proof, {"status": "test_local_fixture_previous_bytes_only_not_public",
            "cache_root": str(self.cache), "public_files_verified": 1, "verified_corpus_commit": self.old_commit,
            "public_filelist_sha256": self.old_pin})
        self.requests = []
        self.failures = 1
        owner = self
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                owner.requests.append(self.path)
                body = owner.fresh
                if owner.failures:
                    owner.failures -= 1
                    body = body[:4]
                self.send_response(200)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            def log_message(self, *args):
                pass
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.http = "http://127.0.0.1:" + str(self.server.server_port)
        self.output = self.root / "output"

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
        self.temp.cleanup()

    def prepare(self, attempts=1, commit="2" * 40):
        return transport.prepare(commit, self.current, self.current_pin, self.cache, self.old, self.old_pin,
            self.proof, self.proof_pin, self.old_commit, self.output, self.http, attempts, 0)

    def test_interruption_resume_only_incomplete_file(self):
        with self.assertRaises(ValueError):
            self.prepare()
        stable = self.output / "package/a-stable.txt"
        stamp = stable.stat().st_mtime_ns
        result = self.prepare()
        self.assertEqual(stable.stat().st_mtime_ns, stamp)
        self.assertEqual(result["files_completed"], 2)
        self.assertEqual(result["reused_files"], 1)
        self.assertEqual(len(self.requests), 2)
        self.assertTrue(all(p.endswith("/z-fresh.txt") for p in self.requests))
        self.prepare()
        self.assertEqual(len(self.requests), 2)

    def test_bounded_retry_completes_short_response(self):
        result = self.prepare(attempts=2)
        self.assertEqual(result["files_completed"], 2)
        self.assertEqual(len(self.requests), 2)

    def test_mismatched_commit_cannot_resume(self):
        with self.assertRaises(ValueError):
            self.prepare()
        with self.assertRaisesRegex(ValueError, "identity mismatch"):
            self.prepare(commit="3" * 40)
        self.assertEqual(len(self.requests), 1)

    def test_T03_identity_rejection_does_not_create_package(self):
        self.output.mkdir()
        receipt = self.output / "TRANSPORT_RECEIPT.json"
        save(receipt, {"repository": transport.REPOSITORY, "current_commit": "3" * 40})
        original = receipt.read_bytes()
        with self.assertRaisesRegex(ValueError, "identity mismatch"):
            self.prepare()
        self.assertFalse((self.output / "package").exists())
        self.assertEqual(receipt.read_bytes(), original)
        self.assertEqual(self.requests, [])

    def test_invalid_existing_file_is_refetched(self):
        self.failures = 0
        self.prepare()
        (self.output / "package/z-fresh.txt").write_bytes(b"truncated")
        self.prepare()
        self.assertEqual(len(self.requests), 2)
        self.assertEqual((self.output / "package/z-fresh.txt").read_bytes(), self.fresh)


if __name__ == "__main__":
    unittest.main()
