"""Shared status-table behavior exercised through the two public CLIs."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
TEMPLATE = ROOT / "templates" / "project-status.md"
TASK_SEPARATOR = "|---|---|---|---|---|---|---|---|---|---|---|"
BLOCKED_SEPARATOR = "|---|---|---|---|---|---|"


class StatusTableCLITests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="_tmp_table_tests_", dir=ROOT)
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)
        self.path = self.directory / "project-status.md"
        self.environment = dict(os.environ, PYTHONIOENCODING="utf-8",
                                PYTHONDONTWRITEBYTECODE="1")

    def state_content(self, task_row, blocked_row=None):
        content = TEMPLATE.read_text(encoding="utf-8").replace(
            TASK_SEPARATOR, TASK_SEPARATOR + "\n" + task_row, 1)
        if blocked_row is not None:
            content = content.replace(
                "\n" + BLOCKED_SEPARATOR + "\n",
                "\n" + BLOCKED_SEPARATOR + "\n" + blocked_row + "\n", 1)
        return content

    def run_cli(self, script, *arguments):
        return subprocess.run(
            [sys.executable, str(SCRIPTS / script), *map(str, arguments)],
            cwd=self.directory, env=self.environment, capture_output=True,
            text=True, encoding="utf-8", timeout=30, check=False,
        )

    def run_tools(self, content):
        self.path.write_text(content, encoding="utf-8", newline="\n")
        validation = self.run_cli("validate-project-state.py", "--path", self.path)
        rendering = self.run_cli("render-workflow.py", self.path, "--format", "json")
        self.assertEqual(rendering.returncode, 0, rendering.stderr)
        self.assertEqual(rendering.stderr, "")
        return validation, json.loads(rendering.stdout)

    def assert_valid(self, process, task_count=1):
        self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
        self.assertEqual(process.stderr, "")
        payload = json.loads(process.stdout)
        self.assertTrue(payload["valid"], payload)
        self.assertEqual(payload["task_count"], task_count)
        self.assertEqual(payload["errors"], [])

    def test_escaped_pipes_preserve_task_and_blocked_fields(self):
        content = self.state_content(
            r"| 01 | Guide \| API | Blocked | P1 | Executor | - | No | Yes | Yes | task-output/01/ | now |",
            r"| 01 | In Review | Need A \| B | Ops \| QA | Evidence available | next |",
        )
        validation, rendered = self.run_tools(content)
        self.assertEqual(rendered["task_states"]["01"]["name"], "Guide | API")
        self.assertEqual(rendered["task_states"]["01"]["status"], "Blocked")
        self.assertEqual(rendered["task_states"]["01"]["depends_on"], [])
        self.assertEqual(rendered["blocked_items"], [{
            "task": "01", "reason": "Need A | B", "owner": "Ops | QA",
            "done_when": "Evidence available",
        }])
        self.assert_valid(validation)

    def test_optional_closing_border_preserves_final_and_empty_cells(self):
        for ending in ("now", r"now\|", "|", "now|"):
            with self.subTest(ending=ending):
                content = self.state_content(
                    "| 01 | 指南 | Blocked | P1 | Executor | - | No | Yes | Yes | task-output/01/ |" + ending,
                    "| 01 | In Review | Need evidence | QA | Check complete | next",
                )
                validation, rendered = self.run_tools(content)
                self.assert_valid(validation)
                self.assertEqual(rendered["task_states"]["01"]["name"], "指南")
                self.assertEqual(rendered["blocked_items"][0]["done_when"], "Check complete")

    def test_aligned_separators_and_indentation_do_not_create_tasks(self):
        content = self.state_content(
            "  \t| 01 | Guide | Blocked | P1 | Executor | - | No | Yes | Yes | out | now |  ",
            "  \t| 01 | In Review | Need evidence | QA | Verified | next |  ",
        ).replace(TASK_SEPARATOR, "| :--- | ---: | :---: | --- | --- | --- | --- | --- | --- | --- | --- |")
        content = content.replace(
            "\n" + BLOCKED_SEPARATOR + "\n", "\n| :--- | ---: | :---: | --- | --- | --- |\n")
        validation, rendered = self.run_tools(content)
        self.assert_valid(validation)
        self.assertEqual(list(rendered["task_states"]), ["01"])
        self.assertEqual(rendered["blocked_items"][0]["owner"], "QA")

    def test_blank_task_id_does_not_become_a_display_task(self):
        validation, rendered = self.run_tools(self.state_content(
            "|| No task | TODO | P1 | Executor | - | No | No | No | out | now |"))
        self.assert_valid(validation, task_count=0)
        self.assertEqual(rendered["task_states"], {})

    def test_backslash_parity_and_non_pipe_backslashes_are_preserved(self):
        cases = (
            (r"Guide \| API", "Guide | API"),
            (r"Guide \\\| API", r"Guide \\| API"),
            (r"C:\temp\guide", r"C:\temp\guide"),
            (r"Path\\", r"Path\\"),
        )
        for source, expected in cases:
            with self.subTest(source=source):
                validation, rendered = self.run_tools(self.state_content(
                    "| 01 | " + source + "| TODO | P1 | Executor | - | No | No | No | out | now |"))
                self.assert_valid(validation)
                self.assertEqual(rendered["task_states"]["01"]["name"], expected)
                self.assertEqual(rendered["task_states"]["01"]["status"], "TODO")

    def test_extra_unescaped_pipes_still_fail_task_column_validation(self):
        for name in ("Guide | API", r"Guide \\| API"):
            with self.subTest(name=name):
                validation, _ = self.run_tools(self.state_content(
                    "| 01 | " + name + " | TODO | P1 | Executor | - | No | No | No | out | now |"))
                self.assertEqual(validation.returncode, 1)
                payload = json.loads(validation.stdout)
                self.assertFalse(payload["valid"])
                self.assertTrue(any("expected 11 columns, found 12" in error
                                    for error in payload["errors"]), payload)

    def test_extra_blocked_columns_are_not_silently_accepted(self):
        validation, _ = self.run_tools(self.state_content(
            "| 01 | Guide | Blocked | P1 | Executor | - | No | No | No | out | now |",
            "| 01 | In Review | Need A | B | QA | Verified | next |",
        ))
        self.assertEqual(validation.returncode, 1)
        payload = json.loads(validation.stdout)
        self.assertFalse(payload["valid"])
        self.assertTrue(any("expected 6 columns, found 7" in error
                            for error in payload["errors"]), payload)
        self.assertTrue(any("Missing blocked record" in error for error in payload["errors"]))

    def test_malformed_alignment_row_still_fails_column_validation(self):
        content = self.state_content(
            "| 01 | Guide | TODO | P1 | Executor | - | No | No | No | out | now |"
        ).replace(TASK_SEPARATOR, "| :--- | ---: |")
        validation, _ = self.run_tools(content)
        self.assertEqual(validation.returncode, 1)
        self.assertTrue(any("expected 11 columns, found 2" in error
                            for error in json.loads(validation.stdout)["errors"]))

    def test_task_id_starting_with_dashes_is_not_an_alignment_row(self):
        validation, rendered = self.run_tools(self.state_content(
            "|---task | Guide | TODO | P1 | Executor | - | No | No | No | out | now |"))
        self.assert_valid(validation)
        self.assertEqual(list(rendered["task_states"]), ["---task"])


if __name__ == "__main__":
    unittest.main()
