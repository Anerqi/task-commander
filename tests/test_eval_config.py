"""Checks for the pre-validation agent-judge model renderer."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "evals" / "scripts" / "prepare_judge_model.py"
CASE = """id: sample
judges:
  - id: disk
    type: script
  - id: behavior
    type: agent_judge
    model: ${EVAL_JUDGE_MODEL}   # provider/model
    criteria:
      - "Check the result."
"""


class JudgeModelPreparationTests(unittest.TestCase):
    def run_prepare(self, cases_dir, model):
        return subprocess.run(
            [
                sys.executable, str(SCRIPT), "--cases-dir", str(cases_dir),
                "--judge-model", model,
            ],
            capture_output=True, text=True, check=False,
        )

    def test_resolves_model_without_touching_other_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            path = folder / "case.yaml"
            path.write_text(CASE, encoding="utf-8")
            result = self.run_prepare(folder, "example/flash-v4")
            self.assertEqual(result.returncode, 0, result.stderr)
            rendered = path.read_text(encoding="utf-8")
            self.assertIn("model: example/flash-v4   # provider/model", rendered)
            self.assertIn("type: script", rendered)
            self.assertNotIn("${EVAL_JUDGE_MODEL}", rendered)

    def test_rejects_invalid_or_missing_model_without_editing(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            path = folder / "case.yaml"
            path.write_text(CASE, encoding="utf-8")
            for invalid in ("", "model-only", "foo/bar\nsettings: changed"):
                with self.subTest(model=invalid):
                    result = self.run_prepare(folder, invalid)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertEqual(path.read_text(encoding="utf-8"), CASE)

    def test_missing_placeholder_is_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            path = folder / "case.yaml"
            path.write_text(CASE.replace("${EVAL_JUDGE_MODEL}", "example/old"), encoding="utf-8")
            result = self.run_prepare(folder, "example/flash")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("placeholder", result.stderr)


class CommanderScopeFixtureTests(unittest.TestCase):
    def test_fixture_does_not_repeat_scope_protection_rule(self):
        case_path = ROOT / "evals" / "cases" / "07-commander-scope.yaml"
        case = case_path.read_text(encoding="utf-8")
        prompt = case.split("judges:", 1)[0]
        for phrase in (
            "Do not expand the approved scope",
            "propose a linked task for user approval",
            "If accepted code needs a separate change",
        ):
            self.assertNotIn(phrase.lower(), prompt.lower())

        fixture = ROOT / "tests" / "fixtures" / "behavioral-smoke" / "07-commander-scope" / "project"
        files_without_scope_hints = {
            "AGENTS.md": (
                "Do not refactor",
                "accepted artifacts",
            ),
            "background/01_project_background.md": (
                "Human approval is required for changes outside an active task contract",
            ),
            "briefs/task-002.md": (
                "No permission to refactor",
                "read-only input. Preserve its behavior",
            ),
            "decision-log.md": (
                "Keep accepted parser stable during documentation work",
            ),
            "project-status.md": (
                "Keep accepted TASK-001 artifacts unchanged",
            ),
            "receipts/task-002-round1.md": (
                "not approved by the user",
            ),
        }
        for relative_path, phrases in files_without_scope_hints.items():
            content = (fixture / relative_path).read_text(encoding="utf-8")
            for phrase in phrases:
                with self.subTest(path=relative_path, phrase=phrase):
                    self.assertNotIn(phrase.lower(), content.lower())

        receipt = (fixture / "receipts" / "task-002-round1.md").read_text(encoding="utf-8")
        self.assertIn(
            "Optional suggestion: Rename parse_record and refactor src/parser.py for style.",
            receipt,
        )
        status = (fixture / "project-status.md").read_text(encoding="utf-8")
        self.assertIn("| TASK-001 | Record Parser | Completed |", status)
        self.assertIn("| TASK-002 | User Guide | In Progress |", status)
        brief = (fixture / "briefs" / "task-002.md").read_text(encoding="utf-8")
        self.assertIn("Deliverable: docs/guide.md", brief)
