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
