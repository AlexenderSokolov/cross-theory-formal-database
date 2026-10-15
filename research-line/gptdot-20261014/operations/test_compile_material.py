"""Check adapter search paths at the delivery boundary without compiling papers."""
import json
import os
from pathlib import Path
import runpy
import sys
import tempfile
import types
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).with_name("compile_material.py")


class CompileMaterialTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.job = Path(self.tmp.name) / "job with spaces"
        self.package = self.job / "package-root-r001"
        self.items = self.package / "items"
        self.items.mkdir(parents=True)
        (self.job / "job-state.json").write_text(
            json.dumps({"package": self.package.name})
        )
        (self.package / "manifest.json").write_text(
            json.dumps({"items": [{"item_path": "items/example.tex"}]})
        )

    def run_adapter(self, environment=None, resume=False):
        observed = {}
        # Stop at the shared delivery boundary: running it would compile a paper.
        delivery = types.ModuleType("prepared_delivery")

        def capture_environment():
            observed.update(environment=dict(os.environ), argv=sys.argv[:])
            return 0

        delivery.main = capture_environment
        argv = [str(SCRIPT), "--job", str(self.job)]
        if resume:
            argv.append("--resume")
        with (
            patch.dict(os.environ, environment or {}, clear=True),
            patch.dict(sys.modules, {"prepared_delivery": delivery}),
            patch.object(sys, "argv", argv),
            patch.object(sys, "path", sys.path[:]),
        ):
            with self.assertRaises(SystemExit) as stopped:
                runpy.run_path(str(SCRIPT), run_name="__main__")
            self.assertEqual(stopped.exception.code, 0)
        return observed

    def test_bibinputs_starts_with_package_root_and_keeps_default_search(self):
        actual = self.run_adapter()["environment"]
        self.assertEqual(actual.get("BIBINPUTS"), str(self.package) + os.pathsep)

    def test_existing_bibinputs_search_paths_are_preserved(self):
        previous = os.pathsep.join(["legacy-a", "", "legacy-b", ""])
        actual = self.run_adapter({"BIBINPUTS": previous})["environment"]
        self.assertEqual(
            actual.get("BIBINPUTS"), str(self.package) + os.pathsep + previous
        )

    def test_existing_bstinputs_behavior_is_preserved(self):
        previous = os.pathsep.join(["styles-a", "", "styles-b", ""])
        actual = self.run_adapter({"BSTINPUTS": previous})["environment"]
        self.assertEqual(actual["BSTINPUTS"], str(self.items) + os.pathsep + previous)

    def test_delegates_compile_command_with_resume(self):
        actual = self.run_adapter(resume=True)
        self.assertEqual(
            actual["argv"],
            [str(SCRIPT), "compile-job", "--job", str(self.job), "--resume"],
        )


if __name__ == "__main__":
    unittest.main()
