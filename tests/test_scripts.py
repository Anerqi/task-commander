import builtins
import importlib.util
import json
import pathlib
import subprocess
import sys
import tempfile
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
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.directory = pathlib.Path(temporary.name)
        self.root = self.directory / "explicit skills"
        self.root.mkdir()

    def write_skill(self, folder, name, description="", *, root=None,
                    filename="SKILL.md", extra=""):
        path = (self.root if root is None else root) / folder / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            f'---\nname: "{name}"\ndescription: "{description}"\n{extra}---\n',
            encoding="utf-8", newline="\n",
        )
        return str(path.resolve())

    def run_scanner(self, *arguments):
        return subprocess.run(
            [sys.executable, str(SCANNER), "--roots", str(self.root), *arguments],
            cwd=self.directory, capture_output=True, check=False, timeout=30,
        )

    def scan(self, *arguments):
        process = self.run_scanner(*arguments)
        self.assertEqual(process.returncode, 0, process.stderr.decode("utf-8"))
        self.assertEqual(process.stderr, b"")
        self.assertFalse(process.stdout.startswith(b"\xef\xbb\xbf"))
        payload = json.loads(process.stdout.decode("utf-8"))
        self.assertEqual(payload["candidates_returned"], len(payload["candidates"]))
        return payload

    def test_scoring_normalizes_terms_accumulates_and_filters(self):
        self.write_skill("exact", "Build", "BUILD and lint")
        self.write_skill("substring", "build-tools", "build helpers")
        self.write_skill("other-exact", "lint")
        self.write_skill("description", "docs", "build and lint")
        self.write_skill("unmatched", "unrelated", "nothing relevant")
        payload = self.scan("--query-terms", " BUILD ", "lint", "build", "  ")
        self.assertEqual(payload["query_terms"], ["build", "lint"])
        self.assertEqual(payload["unique_skills_scanned"], 5)
        self.assertEqual(
            [(item["name"], item["score"], item["matched_terms"])
             for item in payload["candidates"]],
            [("Build", 18, ["build", "lint"]), ("lint", 12, ["lint"]),
             ("build-tools", 11, ["build"]), ("docs", 6, ["build", "lint"])],
        )
        limited = self.scan("--query-terms", "build", "lint", "--max-results", "2")
        self.assertEqual(limited["unique_skills_scanned"], 5)
        self.assertEqual([item["name"] for item in limited["candidates"]], ["Build", "lint"])
        unmatched = self.scan("--query-terms", "not-present")
        self.assertEqual(unmatched["unique_skills_scanned"], 5)
        self.assertEqual(unmatched["candidates"], [])

    def test_no_terms_includes_all_and_ties_sort_case_insensitively(self):
        self.write_skill("first", "Zulu", "shared")
        self.write_skill("second", "alpha", "shared")
        self.write_skill("third", "Beta", "shared")
        for terms, score, matched in (([], 0, []), (["  "], 0, []),
                                      (["shared"], 3, ["shared"])):
            with self.subTest(terms=terms):
                payload = self.scan("--query-terms", *terms)
                self.assertEqual(
                    [(item["name"], item["score"], item["matched_terms"])
                     for item in payload["candidates"]],
                    [(name, score, matched) for name in ("alpha", "Beta", "Zulu")],
                )

    def test_name_dedupe_keeps_first_scanned_metadata_before_scoring(self):
        later_root = self.directory / "later"
        winner = self.write_skill("a-first", " Shared ", "first description",
                                  extra="disable-model-invocation: true\n")
        same_root = self.write_skill("z-second", "SHARED", "needle")
        later = self.write_skill("one", "shared", "needle", root=later_root)
        unique = self.write_skill("two", "Other", root=later_root)
        arguments = ("--roots", str(self.root), str(later_root))
        payload = self.scan(*arguments)
        self.assertEqual(payload["roots"], [str(self.root.resolve()),
                                           str(later_root.resolve())])
        self.assertEqual(payload["unique_skills_scanned"], 2)
        self.assertEqual([item["path"] for item in payload["candidates"]],
                         [unique, winner])
        self.assertEqual(payload["candidates"][1], {
            "name": "Shared", "description": "first description", "path": winner,
            "score": 0, "matched_terms": [], "disable_model_invocation": "true",
            "duplicate_paths": [same_root, later],
        })
        self.assertEqual(self.scan(*arguments, "--query-terms", "needle")["candidates"], [])
        reversed_roots = self.scan("--roots", str(later_root), str(self.root),
                                   "--query-terms", "needle")
        self.assertEqual(reversed_roots["candidates"][0]["path"], later)
        self.assertEqual(reversed_roots["candidates"][0]["score"], 3)
        self.assertEqual(reversed_roots["candidates"][0]["duplicate_paths"],
                         [winner, same_root])

    def test_explicit_roots_skip_missing_paths_and_do_not_discover_defaults(self):
        selected = self.write_skill("nested/deeper", "selected", filename="sKiLl.Md")
        self.write_skill("ignored", "default-only",
                         root=self.directory / ".agents" / "skills")
        self.write_skill("not-a-skill", "wrong-filename", filename="README.md")
        missing = self.directory / "missing"
        regular_file = self.directory / "file"
        regular_file.write_text("not a directory", encoding="utf-8")
        payload = self.scan("--roots", str(missing), str(regular_file), " ",
                            "explicit skills")
        self.assertEqual(payload["roots"], [str(self.root.resolve())])
        self.assertEqual(payload["unique_skills_scanned"], 1)
        self.assertEqual([item["path"] for item in payload["candidates"]], [selected])
        empty = self.scan("--roots", str(missing))
        self.assertEqual(empty["roots"], [])
        self.assertEqual(empty["unique_skills_scanned"], 0)
        self.assertEqual(empty["candidates"], [])

    def test_max_results_boundaries_and_default_truncate_after_sorting(self):
        # Reverse folder order ensures truncation cannot precede name sorting.
        for index in range(501):
            self.write_skill(f"{500 - index:03}", f"skill-{index:03}")
        for arguments, count in (([], 30), (["--max-results", "1"], 1),
                                 (["--max-results", "500"], 500)):
            with self.subTest(arguments=arguments):
                payload = self.scan(*arguments)
                self.assertEqual(payload["unique_skills_scanned"], 501)
                self.assertEqual(payload["candidates_returned"], count)
                self.assertEqual([item["name"] for item in payload["candidates"]],
                                 [f"skill-{index:03}" for index in range(count)])

    def test_invalid_max_results_is_an_argument_error_without_output(self):
        output = self.directory / "must-not-exist.json"
        for value in ("0", "-1", "501", "1.5", "invalid"):
            with self.subTest(value=value):
                process = self.run_scanner("--max-results", value,
                                           "--output-path", str(output))
                self.assertEqual(process.returncode, 2)
                self.assertEqual(process.stdout, b"")
                self.assertIn(b"--max-results", process.stderr)
                self.assertFalse(output.exists())

    def test_output_file_creates_parents_and_uses_utf8_lf_without_stdout(self):
        self.write_skill("unicode", "caf\u00e9", "\u4e2d\u6587 description")
        output = self.directory / "new" / "nested" / "scan.json"
        process = self.run_scanner("--output-path", str(output))
        self.assertEqual(process.returncode, 0, process.stderr.decode("utf-8"))
        self.assertEqual(process.stdout, b"")
        self.assertEqual(process.stderr, b"")
        raw = output.read_bytes()
        self.assertFalse(raw.startswith(b"\xef\xbb\xbf"))
        self.assertNotIn(b"\r", raw)
        self.assertTrue(raw.endswith(b"\n"))
        self.assertIn("caf\u00e9".encode("utf-8"), raw)
        self.assertIn("\u4e2d\u6587".encode("utf-8"), raw)
        payload = json.loads(raw.decode("utf-8"))
        stdout_payload = self.scan()
        # Timestamp is generated per invocation; every other field must agree.
        self.assertIsInstance(payload.pop("generated_at"), str)
        stdout_payload.pop("generated_at")
        self.assertEqual(payload, stdout_payload)

    def test_real_frontmatter_boundaries_and_missing_names(self):
        contents = {
            "body-only": "---\ndescription: no name\n---\nname: body-only\n",
            "no-opening": "name: no-opening\n---\n",
            "blank-name": "---\nname: '   '\n---\n",
            "at-limit": "---\n" + "# padding\n" * 198 + "name: at-limit\n---\n",
            "past-limit": "---\n" + "# padding\n" * 199 + "name: past-limit\n---\n",
            "valid": "\ufeff---\nNAME: 'Valid'\nDESCRIPTION: >-\n"
                     "  first line\n  second line\n---\nname: body-override\n",
        }
        for folder, content in contents.items():
            path = self.root / folder / "SKILL.md"
            path.parent.mkdir()
            path.write_text(content, encoding="utf-8", newline="\n")
        payload = self.scan()
        self.assertEqual(payload["unique_skills_scanned"], 2)
        self.assertEqual([(item["name"], item["description"])
                          for item in payload["candidates"]],
                         [("at-limit", ""), ("Valid", "first line second line")])

    def test_parser_stops_at_frontmatter_boundary(self):
        scanner = load_scanner()
        with mock.patch.object(builtins, "open", return_value=FrontmatterReader()):
            parsed = scanner.parse_frontmatter("ignored")
        self.assertEqual(parsed, ("example-skill", "Example description", ""))


class ProjectStateValidationTests(unittest.TestCase):
    def run_validator(self, content, *extra_args):
        with tempfile.TemporaryDirectory() as directory:
            state_path = pathlib.Path(directory) / "project-status.md"
            state_path.write_text(content, encoding="utf-8", newline="\n")
            process = subprocess.run(
                [sys.executable, str(VALIDATOR), "--path", str(state_path), *extra_args],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
                cwd=directory,
                timeout=30,
            )
            self.assertEqual(process.stderr, "")
            payload = json.loads(process.stdout)
            self.assertEqual(payload["path"], str(state_path.resolve()))
            return process, payload

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
            "\n|---|---|---|---|---|---|\n",
            "\n|---|---|---|---|---|---|\n| 01 |\n",
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

    # Explicit expectations, not loaded from the spec: an accidental change to
    # an edge in the production transition table must fail this regression test.
    STATES = ("TODO", "In Progress", "In Review", "Needs Revision", "QA Pending",
              "Awaiting Acceptance", "Completed", "Blocked", "Cancelled")
    ALLOWED = {
        "TODO": {"In Progress", "Blocked", "Cancelled"},
        "In Progress": {"In Review", "QA Pending", "Awaiting Acceptance",
                        "Needs Revision", "Blocked", "Cancelled"},
        "In Review": {"Needs Revision", "QA Pending", "Awaiting Acceptance",
                      "Blocked", "Cancelled"},
        "Needs Revision": {"In Progress", "Blocked", "Cancelled"},
        "QA Pending": {"Needs Revision", "Awaiting Acceptance", "Blocked", "Cancelled"},
        "Awaiting Acceptance": {"Completed", "Needs Revision", "Blocked", "Cancelled"},
        "Completed": set(),
        "Cancelled": set(),
    }

    def state_content(self, state="TODO", *, reviewer="No", qa="No", blocked=()):
        content = TEMPLATE.read_text(encoding="utf-8")
        task_row = (f"| TC-01 | Example | {state} | P1 | Executor | None | No | "
                    f"{reviewer} | {qa} | task-output/01/ | now |")
        task_separator = "|---|---|---|---|---|---|---|---|---|---|---|"
        blocked_separator = "|---|---|---|---|---|---|"
        content = content.replace(task_separator, task_separator + "\n" + task_row)
        rows = [f"| {task_id} | {before} | Dependency | Commander | Resolved | now |"
                for task_id, before in blocked]
        return content.replace("\n" + blocked_separator + "\n",
                               "\n" + blocked_separator + "\n" + "\n".join(rows) + "\n")

    def assert_transition(self, content, source, target, *, valid=True,
                          error=None, task_id=None):
        arguments = ["--from-state", source, "--to-state", target]
        if task_id is not None:
            arguments.extend(["--task-id", task_id])
        process, payload = self.run_validator(content, *arguments)
        self.assertEqual(process.returncode, 0 if valid else 1, payload)
        self.assertEqual(payload["valid"], valid, payload)
        self.assertEqual(payload["task_count"], 1)
        if valid:
            self.assertEqual(payload["errors"], [])
        else:
            self.assertEqual(payload["errors"], [error or
                             f"Invalid state transition: {source} -> {target}"])

    def test_transition_matrix_including_terminal_states_and_self_transitions(self):
        for source, targets in self.ALLOWED.items():
            for target in self.STATES:
                with self.subTest(source=source, target=target):
                    self.assert_transition(self.state_content(source), source, target,
                                           valid=target in targets)

    def test_optional_reviewer_and_qa_paths_still_require_acceptance(self):
        # These are supported routes, not enforcement of the Reviewer/QA cells:
        # the current validator checks edges, not per-task gate configuration.
        for reviewer, qa, middle in (
            ("Yes", "Yes", ["In Review", "QA Pending"]),
            ("Yes", "No", ["In Review"]),
            ("No", "Yes", ["QA Pending"]),
            ("No", "No", []),
        ):
            path = ["In Progress", *middle, "Awaiting Acceptance", "Completed"]
            for source, target in zip(path, path[1:]):
                with self.subTest(reviewer=reviewer, qa=qa, source=source, target=target):
                    self.assert_transition(
                        self.state_content(source, reviewer=reviewer, qa=qa), source, target)
            with self.subTest(reviewer=reviewer, qa=qa, direct_completion=True):
                self.assert_transition(
                    self.state_content("In Progress", reviewer=reviewer, qa=qa),
                    "In Progress", "Completed", valid=False)

    def test_transition_lookup_ignores_case_and_surrounding_whitespace(self):
        self.assert_transition(self.state_content("in progress"),
                               "  IN PROGRESS ", " awaiting ACCEPTANCE  ")

    def test_transition_arguments_must_be_paired_and_states_known(self):
        for arguments, error in (
            (["--from-state", "TODO"], "FromState and ToState must be provided together"),
            (["--to-state", "In Progress"], "FromState and ToState must be provided together"),
            (["--from-state", "Unknown", "--to-state", "TODO"], "Invalid source state: Unknown"),
            (["--from-state", "TODO", "--to-state", "Unknown"], "Invalid target state: Unknown"),
        ):
            with self.subTest(arguments=arguments):
                process, payload = self.run_validator(self.state_content(), *arguments)
                self.assertEqual(process.returncode, 1)
                self.assertFalse(payload["valid"])
                self.assertEqual(payload["errors"], [error])

    def test_blocked_restores_each_nonterminal_previous_state_by_task_id(self):
        for previous in self.ALLOWED:
            if previous in ("Completed", "Cancelled"):
                continue
            with self.subTest(previous=previous):
                content = self.state_content("Blocked", blocked=[("TC-01", previous)])
                self.assert_transition(content, " blocked ", previous.upper(),
                                       task_id=" tc-01 ")

    def test_blocked_recovery_requires_task_id_and_matching_record(self):
        content = self.state_content("Blocked", blocked=[
            ("TC-OTHER", "QA Pending"), ("TC-01", "In Review"),
        ])
        cases = (
            (None, "In Review", "Blocked recovery requires --task-id to verify the pre-block state"),
            ("missing", "In Review", "Task missing is not listed in the blocked section"),
            ("TC-01", "QA Pending", "Invalid state transition: Blocked -> QA Pending "
             "(pre-block state of task TC-01 is In Review)"),
            ("TC-01", "Completed", "Invalid state transition: Blocked -> Completed "
             "(pre-block state of task TC-01 is In Review)"),
        )
        for task_id, target, error in cases:
            with self.subTest(task_id=task_id, target=target):
                self.assert_transition(content, "Blocked", target, valid=False,
                                       task_id=task_id, error=error)
        self.assert_transition(content, "Blocked", "In Review", task_id="TC-01")
        self.assert_transition(self.state_content("Blocked"), "Blocked", "In Review",
                               valid=False, task_id="TC-01",
                               error="Task TC-01 is not listed in the blocked section")

    def test_blocked_cancellation_does_not_require_recovery_metadata(self):
        self.assert_transition(self.state_content("Blocked"), "Blocked", "Cancelled")

    def test_duplicate_blocked_records_use_first_previous_state(self):
        content = self.state_content("Blocked", blocked=[
            ("TC-01", "In Progress"), ("tc-01", "QA Pending"),
        ])
        self.assert_transition(content, "Blocked", "In Progress", task_id="TC-01")
        self.assert_transition(content, "Blocked", "QA Pending", valid=False,
                               task_id="TC-01",
                               error="Invalid state transition: Blocked -> QA Pending "
                               "(pre-block state of task TC-01 is In Progress)")


if __name__ == "__main__":
    unittest.main()