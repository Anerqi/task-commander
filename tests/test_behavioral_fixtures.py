"""Packaging/runnability checks for synthetic inputs, not model-behavior scores."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "behavioral-smoke"
CASES = (
    "01-fast-lane", "02-context-handoff", "03-parallel-ownership",
    "04-continuation", "05-window-recovery", "06-missing-evidence",
)


class BehavioralFixtureTests(unittest.TestCase):
    def run_python(self, cwd, *arguments):
        return subprocess.run(
            [sys.executable, *map(str, arguments)], cwd=cwd,
            env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8"),
            capture_output=True, text=True, encoding="utf-8", timeout=30, check=False,
        )

    def test_each_case_has_separate_input_and_project(self):
        for name in CASES:
            with self.subTest(case=name):
                case = FIXTURES / name
                self.assertTrue((case / "project").is_dir())
                prompt = (case / "input.md").read_text(encoding="utf-8")
                self.assertIn("<project-root>", prompt)
                self.assertIn("<skill-root>", prompt)
        # An independent small request must not be seeded with a registered task.
        self.assertFalse((FIXTURES / CASES[0] / "project" / "project-status.md").exists())

    def test_registered_seed_states_pass_the_validator(self):
        for name in CASES[1:]:
            with self.subTest(case=name):
                project = FIXTURES / name / "project"
                result = self.run_python(
                    project, ROOT / "scripts" / "validate-project-state.py",
                    "--path", project / "project-status.md",
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertEqual(result.stderr, "")
                self.assertTrue(json.loads(result.stdout)["valid"])

    def test_python_seed_tests_run_in_a_disposable_copy(self):
        # This verifies test setup, not the unperformed work or a model's receipt.
        for name in ("05-window-recovery", "06-missing-evidence"):
            with self.subTest(case=name), tempfile.TemporaryDirectory(
                    prefix="_tmp_smoke_tests_", dir=ROOT) as directory:
                project = Path(directory) / "project"
                shutil.copytree(FIXTURES / name / "project", project,
                                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
                result = self.run_python(project, "-m", "unittest", "discover", "-s", "tests", "-v")
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn("Ran 1 test", result.stderr)
                self.assertIn("OK", result.stderr)


if __name__ == "__main__":
    unittest.main()
