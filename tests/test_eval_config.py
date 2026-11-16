"""Checks for the pre-validation agent-judge model renderer."""

import shutil
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


class PhaseCompactionFixtureTests(unittest.TestCase):
    def test_case_08_wires_fixture_and_disk_check(self):
        case = ROOT / "evals" / "cases" / "08-phase-compaction.yaml"
        fixture = ROOT / "tests" / "fixtures" / "behavioral-smoke" / "08-phase-compaction"
        disk_check = ROOT / "evals" / "scripts" / "check_08_phase_compaction.py"
        self.assertTrue(case.is_file())
        self.assertTrue(disk_check.is_file())
        self.assertTrue((fixture / "input.md").is_file())
        project = fixture / "project"
        self.assertTrue((project / "project-status.md").is_file())
        self.assertTrue((project / "background" / "02_skill_list.md").is_file())
        self.assertFalse((project / "CONTEXT.md").exists())
        prompt = case.read_text(encoding="utf-8").split("judges:", 1)[0]
        self.assertIn("explicitly approved adopting Task Commander Version 3", prompt)
        self.assertIn("No archive destination or retention has been approved", prompt)

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


class ContextHandoffOptimizationTests(unittest.TestCase):
    def handoff_route(self):
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        return skill.split("**Handoff only**:", 1)[1].split(
            "\n  - **Initialize or recover**:", 1)[0]

    def test_handoff_checks_recorded_protocol_before_shortcut(self):
        route = self.handoff_route()
        for condition in ("exactly one", "well-formed", "authoritative Project section",
                          "current version `3`", "Missing", "below-3", "invalid", "duplicate",
                          "unrecognized", "future versions", "**Initialize or recover**",
                          "references/23-protocol-upgrade.md"):
            with self.subTest(condition=condition):
                self.assertIn(condition, route)
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("never an automatic metadata upgrade", skill)

    def test_handoff_uses_current_inventory_and_optional_legacy_records(self):
        route = self.handoff_route()
        self.assertIn("Reuse `Available skills` in the background", route)
        self.assertIn("`CONTEXT.md` only if present", route)
        self.assertIn("`background/02_skill_list.md` only if present as legacy input", route)
        template = (ROOT / "templates" / "commander-handoff.md").read_text(encoding="utf-8")
        for name in ("CONTEXT.md", "background/02_skill_list.md"):
            line, = [line for line in template.splitlines() if "/" + name in line]
            self.assertIn("if present", line)
        self.assertIn("never assume `3` or upgrade metadata", template)

    def test_handoff_only_route_uses_records_template_and_validation(self):
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        for marker in (
            "**Handoff only**",
            "templates/commander-handoff.md",
            "scripts/validate-project-state.py --path",
            "**Initialize or recover**",
            "Do not load full-initialization references on this successful path",
            "without changing project files",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, skill)

    def test_commander_handoff_is_separate_from_context_brief(self):
        context = (ROOT / "references" / "01-context-brief.md").read_text(encoding="utf-8")
        template = (ROOT / "templates" / "commander-handoff.md").read_text(encoding="utf-8")
        self.assertIn("templates/commander-handoff.md", context)
        self.assertNotIn("You are the Commander for this project.", context)
        for marker in (
            "You are the Commander for this project.",
            "references/02-commander.md",
            "references/15-collaboration.md",
            "references/11-task-state-machine.md",
            "templates/task-continuation.md",
            "Do not load its listed references in the current Context Agent window",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, template)

    def test_existing_agents_noop_write_is_avoided(self):
        context = (ROOT / "references" / "01-context-brief.md").read_text(encoding="utf-8")
        self.assertIn("byte-for-byte identical", context)
        self.assertIn("leave it untouched", context)
        self.assertIn("as early as practical", context)

    def test_context_reference_loading_is_conditional(self):
        context = (ROOT / "references" / "01-context-brief.md").read_text(encoding="utf-8")
        for marker in (
            "only when defining or changing policy",
            "only when creating status or reconstructing/recovering",
            "only when creating or maintaining the layer",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, context)

    def test_case_02_disk_check_guards_existing_agents_file(self):
        script = (ROOT / "evals" / "scripts" / "check_02_context_handoff.py").read_text(encoding="utf-8")
        self.assertIn("pre-existing AGENTS.md remains unchanged", script)

    def test_case_02_checker_rejects_changed_agents_rules(self):
        checker = ROOT / "evals" / "scripts" / "check_02_context_handoff.py"
        fixture = ROOT / "tests" / "fixtures" / "behavioral-smoke" / "02-context-handoff" / "project"
        with tempfile.TemporaryDirectory(prefix="_tmp_handoff_check_", dir=ROOT) as directory:
            project = Path(directory) / "project"
            shutil.copytree(fixture, project)
            baseline = subprocess.run([sys.executable, str(checker)], cwd=project,
                                      capture_output=True, text=True, encoding="utf-8", check=False)
            self.assertEqual(baseline.returncode, 0, baseline.stdout + baseline.stderr)
            agents = project / "AGENTS.md"
            agents.write_text(agents.read_text(encoding="utf-8") + "\n- Unapproved new rule.\n",
                              encoding="utf-8", newline="\n")
            changed = subprocess.run([sys.executable, str(checker)], cwd=project,
                                     capture_output=True, text=True, encoding="utf-8", check=False)
            self.assertEqual(changed.returncode, 1, changed.stdout + changed.stderr)
            self.assertIn("FAIL pre-existing AGENTS.md remains unchanged", changed.stdout)

            original_bytes = (fixture / "AGENTS.md").read_bytes()
            self.assertNotIn(b"\r\n", original_bytes)
            agents.write_bytes(original_bytes.replace(b"\n", b"\r\n"))
            changed_newlines = subprocess.run([sys.executable, str(checker)], cwd=project,
                                             capture_output=True, text=True, encoding="utf-8", check=False)
            self.assertEqual(changed_newlines.returncode, 1,
                             changed_newlines.stdout + changed_newlines.stderr)
            self.assertIn("FAIL pre-existing AGENTS.md remains unchanged", changed_newlines.stdout)

    def test_case_02_disk_check_accepts_v3_without_optional_legacy_records(self):
        fixture = ROOT / "tests" / "fixtures" / "behavioral-smoke" / "02-context-handoff" / "project"
        with tempfile.TemporaryDirectory(prefix="_tmp_handoff_v3_", dir=ROOT) as directory:
            project = Path(directory) / "project"
            shutil.copytree(fixture, project)
            for name in ("CONTEXT.md", "background/02_skill_list.md"):
                (project / name).unlink(missing_ok=True)
            shutil.copyfile(ROOT / "templates" / "project-status.md", project / "project-status.md")
            for script, arguments in (
                (ROOT / "scripts" / "validate-project-state.py", ["--path", str(project / "project-status.md")]),
                (ROOT / "evals" / "scripts" / "check_02_context_handoff.py", []),
            ):
                with self.subTest(script=script.name):
                    result = subprocess.run([sys.executable, str(script), *arguments], cwd=project,
                                            capture_output=True, text=True, encoding="utf-8", check=False)
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
