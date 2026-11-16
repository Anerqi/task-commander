"""Attention view and compare-and-set revision checks for the status validator.

These cases guard the optional coordination metadata added in the authority and
attention upgrade: the "Needs you now" section and the "- Status revision" line.
A file that omits both must stay valid, so the legacy cases matter as much as
the rejection cases.
"""

import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate-project-state.py"
TEMPLATE = ROOT / "templates" / "project-status.md"
TASK_SEPARATOR = "|---|---|---|---|---|---|---|---|---|---|---|"
BLOCKED_SEPARATOR = "|---|---|---|---|---|---|"
NEEDS_BLOCK = "### Needs you now\n\n"
NEEDS_HEADER = "| Task | Question | Resume when |\n|---|---|---|"


def task_row(task_id, state="TODO"):
    return (f"| {task_id} | Example | {state} | P1 | Executor | - | No | No | No "
            f"| task-output/{task_id}/ | now |")


def needs_row(task_id, question="May I publish this draft?"):
    return f"| {task_id} | {question} | The draft is reviewed |"


def without_attention(content):
    return re.sub(r"(?ms)^#{2,3} Needs you now\n.*?(?=^#{1,6} |\Z)", "", content)


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
            content = without_attention(content)
        return content

    def run_validator(self, content, *extra, spec=None):
        with tempfile.TemporaryDirectory(prefix="_tmp_attention_", dir=ROOT) as directory:
            path = pathlib.Path(directory) / "project-status.md"
            path.write_text(content, encoding="utf-8", newline="\n")
            if spec is not None:
                spec_path = pathlib.Path(directory) / "state-spec.txt"
                spec_path.write_text(spec, encoding="utf-8", newline="\n")
                extra = (*extra, "--spec-path", str(spec_path))
            process = subprocess.run(
                [sys.executable, str(VALIDATOR), "--path", str(path), *extra],
                capture_output=True, text=True, encoding="utf-8",
                env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"),
                cwd=directory, check=False, timeout=30)
            self.assertEqual(process.stderr, "")
            return process, json.loads(process.stdout)

    def assert_error(self, payload, fragment):
        self.assertFalse(payload["valid"], payload)
        self.assertTrue(any(fragment in error for error in payload["errors"]), payload["errors"])

    def test_template_ships_an_empty_attention_view_and_revision(self):
        template = TEMPLATE.read_text(encoding="utf-8")
        self.assertIn(NEEDS_BLOCK, template.split("## Coordination\n", 1)[1])
        self.assertNotIn("\n## Needs you now\n", template)
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

    def test_legacy_top_level_attention_remains_supported(self):
        content = self.build(tasks=[task_row("01")], drop_needs_section=True)
        content += "\n## Needs you now\n\n" + NEEDS_HEADER + "\n" + needs_row("01") + "\n"
        process, payload = self.run_validator(content)
        self.assertEqual(process.returncode, 0, payload)
        self.assertEqual(payload["needs_you_count"], 1)

    def test_attention_stops_at_eof_or_any_following_heading(self):
        base = self.build(tasks=[task_row("01")], drop_needs_section=True)
        attention = "\n## Coordination\n\n" + NEEDS_BLOCK + NEEDS_HEADER + "\n" + needs_row("01")
        for suffix in ("", "\n### Active windows\n| A | B | C | D |",
                       "\n#### Detail\n| 99 | unrelated | table |",
                       "\n## Other\n| 99 | unrelated | table |"):
            with self.subTest(suffix=suffix):
                process, payload = self.run_validator(base + attention + suffix)
                self.assertEqual(process.returncode, 0, payload)
                self.assertEqual(payload["needs_you_count"], 1)

    def test_duplicate_attention_sections_are_rejected(self):
        for heading in ("##", "###"):
            with self.subTest(heading=heading):
                _, payload = self.run_validator(self.build() + f"\n{heading} Needs you now\n")
                self.assert_error(payload, "Duplicate Needs you now sections")

    def test_fenced_attention_headings_and_rows_are_ignored(self):
        content = self.build(tasks=[task_row("01")])
        content = content.replace(NEEDS_HEADER, NEEDS_HEADER + "\n```md\n"
                                  + needs_row("99") + "\n## Needs you now\n```", 1)
        process, payload = self.run_validator(content)
        self.assertEqual(process.returncode, 0, payload)
        self.assertEqual(payload["needs_you_count"], 0)

    def test_blank_attention_task_id_fails(self):
        _, payload = self.run_validator(self.build(needs=[needs_row("")]))
        self.assert_error(payload, "task id must be nonblank")
        self.assertEqual(payload["needs_you_count"], 1)

    def test_attention_default_limit_and_legacy_override(self):
        spec = (ROOT / "templates" / "task-state-spec.txt").read_text(encoding="utf-8")
        spec = "\n".join(line for line in spec.splitlines()
                         if not line.startswith("needs_you_"))
        tasks = [task_row(str(index)) for index in range(6)]
        content = self.build(tasks=tasks, needs=[needs_row(str(index)) for index in range(6)])
        _, payload = self.run_validator(content, spec=spec)
        self.assert_error(payload, "the attention budget is 5")
        process, payload = self.run_validator(content, spec=spec + "\nneeds_you_max_rows=6\n")
        self.assertEqual(process.returncode, 0, payload)
        self.assertEqual(payload["needs_you_count"], 6)

    def test_completed_warning_boundary_excludes_cancelled(self):
        for count in (10, 11):
            with self.subTest(count=count):
                tasks = [task_row(str(index), "cOmPlEtEd") for index in range(count)]
                tasks += [task_row("cancelled-" + str(index), "Cancelled") for index in range(12)]
                process, payload = self.run_validator(self.build(tasks=tasks))
                self.assertEqual(process.returncode, 0, payload)
                self.assertTrue(payload["valid"], payload)
                self.assertEqual(payload["completed_count"], count)
                self.assertEqual(len(payload["warnings"]), int(count > 10))
                self.assertEqual(payload["errors"], [])

    def test_completed_count_uses_unique_valid_parsed_task_ids(self):
        tasks = [task_row("A", "Completed"), task_row("a", "Completed"),
                 task_row("", "Completed"), task_row("bad", "Completed") + " extra |"]
        _, payload = self.run_validator(self.build(tasks=tasks))
        self.assert_error(payload, "Duplicate task id")
        self.assertEqual(payload["completed_count"], 1)
        self.assertEqual(payload["task_count"], 1)
        self.assertEqual(payload["warnings"], [])

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
