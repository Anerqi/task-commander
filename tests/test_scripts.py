import builtins
import importlib.util
import json
import os
import pathlib
import subprocess
import sys
import unittest
from unittest import mock


ROOT = pathlib.Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate-project-state.py"
SCANNER = ROOT / "scripts" / "scan-skills.py"
TEMPLATE = ROOT / "templates" / "project-status.md"


def load_scanner():
    spec = importlib.util.spec_from_file_location("scan_skills", SCANNER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FrontmatterReader:
    def __init__(self):
        self.lines = iter([
            "name: example-skill\n",
            "description: >\n",
            "  Example description\n",
            "---\n",
        ])

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def readline(self):
        return "---\n"

    def __iter__(self):
        return self

    def __next__(self):
        try:
            return next(self.lines)
        except StopIteration as exc:
            raise AssertionError("parser read beyond frontmatter") from exc


class ScanSkillsTests(unittest.TestCase):
    def test_parser_stops_at_frontmatter_boundary(self):
        scanner = load_scanner()
        with mock.patch.object(builtins, "open", return_value=FrontmatterReader()):
            parsed = scanner.parse_frontmatter("ignored")
        self.assertEqual(parsed, ("example-skill", "Example description", ""))


class ProjectStateValidationTests(unittest.TestCase):
    def run_validator(self, content, *extra_args):
        state_path = ROOT / f"_tmp_test_{os.getpid()}.md"
        try:
            state_path.write_text(content, encoding="utf-8", newline="\n")
            process = subprocess.run(
                [sys.executable, str(VALIDATOR), "--path", str(state_path), *extra_args],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            return process, json.loads(process.stdout)
        finally:
            state_path.unlink(missing_ok=True)

    def test_valid_template_passes(self):
        process, payload = self.run_validator(TEMPLATE.read_text(encoding="utf-8"))
        self.assertEqual(process.returncode, 0)
        self.assertTrue(payload["valid"])

    def test_malformed_task_row_fails(self):
        content = TEMPLATE.read_text(encoding="utf-8").replace(
            "|---|---|---|---|---|---|---|---|---|---|---|",
            "|---|---|---|---|---|---|---|---|---|---|---|\n| 01 | Broken | TODO |",
        )
        process, payload = self.run_validator(content)
        self.assertEqual(process.returncode, 1)
        self.assertFalse(payload["valid"])
        self.assertTrue(any("Malformed task table row" in error for error in payload["errors"]))

    def test_malformed_blocked_row_fails(self):
        content = TEMPLATE.read_text(encoding="utf-8").replace(
            "|---|---|---|---|---|---|",
            "|---|---|---|---|---|---|\n| 01 |",
        )
        process, payload = self.run_validator(content)
        self.assertEqual(process.returncode, 1)
        self.assertFalse(payload["valid"])
        self.assertTrue(any("Malformed blocked table row" in error for error in payload["errors"]))

    def test_duplicate_task_id_fails(self):
        row = "| 01 | Example | TODO | P1 | Executor | None | No | No | No | task-output/01/ | now |"
        content = TEMPLATE.read_text(encoding="utf-8").replace(
            "|---|---|---|---|---|---|---|---|---|---|---|",
            "|---|---|---|---|---|---|---|---|---|---|---|\n" + row + "\n" + row,
        )
        process, payload = self.run_validator(content)
        self.assertEqual(process.returncode, 1)
        self.assertTrue(any("Duplicate task id" in error for error in payload["errors"]))


if __name__ == "__main__":
    unittest.main()