"""Attention view and compare-and-set revision checks for the status validator.

These cases guard the optional coordination metadata added in the authority and
attention upgrade: the "Needs you now" section and the "- Status revision" line.
A file that omits both must stay valid, so the legacy cases matter as much as
the rejection cases.
"""

import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate-project-state.py"
TEMPLATE = ROOT / "templates" / "project-status.md"
TASK_SEPARATOR = "|---|---|---|---|---|---|---|---|---|---|---|"
BLOCKED_SEPARATOR = "|---|---|---|---|---|---|"
NEEDS_BLOCK = "## Needs you now\n\n"
NEEDS_HEADER = "| Task | Question | Resume when |\n|---|---|---|"


def task_row(task_id, state="TODO"):
    return (f"| {task_id} | Example | {state} | P1 | Executor | - | No | No | No "
            f"| task-output/{task_id}/ | now |")


def needs_row(task_id, question="May I publish this draft?"):
    return f"| {task_id} | {question} | The draft is reviewed |"


class AttentionAndRevisionTests(unittest.TestCase):
    def build(self, tasks=(), blocked=(), needs=(), revision=1, drop_needs_section=False):
        content = TEMPLATE.read_text(encoding="utf-8")
        if tasks:
            content = content.replace(
                TASK_SEPARATOR, TASK_SEPARATOR + "\n" + "\n".join(tasks), 1)
        if blocked:
            content = content.replace(
                "\n" + BLOCKED_SEPARATOR + "\n",
                "\n" + BLOCKED_SEPARATOR + "\n" + "\n".join(blocked) + "\n", 1)
        if needs:
            content = content.replace(
                NEEDS_HEADER, NEEDS_HEADER + "\n" + "\n".join(needs), 1)
        if revision is None:
            content = content.replace("- Status revision: 1\n", "", 1)
        elif revision != 1:
            content = content.replace("- Status revision: 1",
                                      f"- Status revision: {revision}", 1)
        if drop_needs_section:
            head, separator, tail = content.partition(NEEDS_BLOCK)
            if separator:
                content = head + "## Task list" + tail.split("## Task list", 1)[-1]
        return content

    def run_validator(self, content, *extra):
        with tempfile.TemporaryDirectory(prefix="_tmp_attention_") as directory:
            path = pathlib.Path(directory) / "project-status.md"
            path.write_text(content, encoding="utf-8", newline="\n")
            process = subprocess.run(
                [sys.executable, str(VALIDATOR), "--path", str(path), *extra],
                capture_output=True, text=True, encoding="utf-8",
                cwd=directory, check=False, timeout=30)
            self.assertEqual(process.stderr, "")
            return process, json.loads(process.stdout)

    def assert_error(self, payload, fragment):
        self.assertFalse(payload["valid"], payload)
        self.assertTrue(any(fragment in error for error in payload["errors"]), payload["errors"])

    def test_template_ships_an_empty_attention_view_and_revision(self):
        process, payload = self.run_validator(self.build())
        self.assertEqual(process.returncode, 0, payload)
        self.assertTrue(payload["valid"])
        self.assertEqual(payload["needs_you_count"], 0)
        self.assertEqual(payload["status_revision"], 1)

    def test_attention_row_for_a_waiting_task_is_accepted(self):
        process, payload = self.run_validator(self.build(
            tasks=[task_row("01", "Awaiting Acceptance")],
            needs=[needs_row("01")]))
        self.assertEqual(process.returncode, 0, payload)
        self.assertEqual(payload["needs_you_count"], 1)

    def test_unknown_task_in_the_attention_view_fails(self):
        _, payload = self.run_validator(self.build(
            tasks=[task_row("01", "Awaiting Acceptance")],
            needs=[needs_row("99")]))
        self.assert_error(payload, "Needs you now references unknown task")

    def test_finished_task_in_the_attention_view_fails(self):
        for state in ("Completed", "Cancelled"):
            with self.subTest(state=state):
                _, payload = self.run_validator(self.build(
                    tasks=[task_row("01", state)],
                    needs=[needs_row("01")]))
                self.assert_error(payload, "Needs you now lists a finished task")

    def test_attention_row_without_a_question_fails(self):
        for question in ("", "-", "   "):
            with self.subTest(question=repr(question)):
                _, payload = self.run_validator(self.build(
                    tasks=[task_row("01", "Awaiting Acceptance")],
                    needs=[f"| 01 | {question} | Later |"]))
                self.assert_error(payload, "has no concrete question")

    def test_attention_view_is_capped_at_five_rows(self):
        tasks = [task_row(f"0{index}", "Awaiting Acceptance") for index in range(1, 7)]
        needs = [needs_row(f"0{index}") for index in range(1, 6)]
        _, payload = self.run_validator(self.build(tasks=tasks, needs=needs))
        self.assertTrue(payload["valid"], payload)

        needs.append(needs_row("06"))
        _, payload = self.run_validator(self.build(tasks=tasks, needs=needs))
        self.assert_error(payload, "the attention budget is 5")

    def test_attention_row_with_extra_columns_fails(self):
        _, payload = self.run_validator(self.build(
            tasks=[task_row("01", "Awaiting Acceptance")],
            needs=["| 01 | Question | Later | extra |"]))
        self.assert_error(payload, "Malformed needs-you-now row")

    def test_expected_revision_matches_and_mismatches(self):
        process, payload = self.run_validator(self.build(), "--expected-revision", "1")
        self.assertEqual(process.returncode, 0, payload)

        process, payload = self.run_validator(self.build(), "--expected-revision", "2")
        self.assertEqual(process.returncode, 1)
        self.assert_error(payload, "Status revision mismatch")

    def test_expected_revision_requires_the_line(self):
        _, payload = self.run_validator(
            self.build(revision=None), "--expected-revision", "1")
        self.assert_error(payload, "Missing status revision line")

    def test_non_numeric_revision_is_rejected(self):
        content = self.build().replace("- Status revision: 1", "- Status revision: two", 1)
        _, payload = self.run_validator(content)
        self.assert_error(payload, "Invalid status revision")

    def test_files_without_the_new_metadata_stay_valid(self):
        legacy = self.build(revision=None, drop_needs_section=True)
        self.assertNotIn("Status revision", legacy)
        process, payload = self.run_validator(legacy)
        self.assertEqual(process.returncode, 0, payload)
        self.assertIsNone(payload["status_revision"])
        self.assertEqual(payload["needs_you_count"], 0)


if __name__ == "__main__":
    unittest.main()
