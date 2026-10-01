from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = ROOT / "scripts"
TEMPLATES_DIR = ROOT / "templates"


def load_script(name):
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), SCRIPTS_DIR / name)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ENGINE = load_script("run-workflow.py")
RENDERER = load_script("render-workflow.py")


class TestWorkflowEngine(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory(prefix="_tmp_workflow_tests_", dir=ROOT)
        self.work_path = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_run_workflow_dry_run_and_checkpoint(self):
        """Test dry run execution, DAG resolution, and checkpoint creation."""
        plan_path = TEMPLATES_DIR / "workflow-plan.template.py"
        ckpt_path = self.work_path / "test-checkpoint.json"

        # 1. Run workflow in dry-run mode (should pause at TASK-03 because requires_checkpoint=True)
        cmd = [
            sys.executable,
            str(SCRIPTS_DIR / "run-workflow.py"),
            "--plan",
            str(plan_path),
            "--checkpoint",
            str(ckpt_path),
            "--dry-run",
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"run-workflow failed: {res.stderr}")
        self.assertTrue(ckpt_path.is_file(), "Checkpoint file was not created")

        # 2. Inspect checkpoint state
        with open(ckpt_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertEqual(data["status"], "CHECKPOINT_SUSPENDED")
        self.assertEqual(data["checkpoint_task"], "TASK-03")
        self.assertEqual(data["completed_tasks"], [])
        self.assertIn("TASK-01", data["simulated_tasks"])
        self.assertIn("TASK-02", data["simulated_tasks"])
        self.assertEqual(data["task_states"]["TASK-03"]["status"], "CHECKPOINT_SUSPENDED")

        # 3. Approve checkpoint for TASK-03
        approve_cmd = [
            sys.executable,
            str(SCRIPTS_DIR / "run-workflow.py"),
            "--checkpoint",
            str(ckpt_path),
            "--approve",
            "TASK-03",
        ]
        res_approve = subprocess.run(approve_cmd, capture_output=True, text=True)
        self.assertEqual(res_approve.returncode, 0, f"Approve failed: {res_approve.stderr}")

        # 4. Resume execution from checkpoint
        resume_cmd = [
            sys.executable,
            str(SCRIPTS_DIR / "run-workflow.py"),
            "--resume-from",
            str(ckpt_path),
            "--dry-run",
        ]
        res_resume = subprocess.run(resume_cmd, capture_output=True, text=True)
        self.assertEqual(res_resume.returncode, 0, f"Resume failed: {res_resume.stderr}")

        # 5. Check completed status
        with open(ckpt_path, "r", encoding="utf-8") as f:
            final_data = json.load(f)

        self.assertEqual(final_data["status"], "SIMULATED")
        self.assertEqual(final_data["completed_tasks"], [])
        self.assertEqual(len(final_data["simulated_tasks"]), 4)

    def test_render_workflow_text_and_mermaid(self):
        """Test render-workflow outputs text board, mermaid diagrams, and json."""
        ckpt_template = TEMPLATES_DIR / "workflow-checkpoint.json"

        # Text render
        cmd_text = [
            sys.executable,
            str(SCRIPTS_DIR / "render-workflow.py"),
            str(ckpt_template),
            "--format",
            "text",
        ]
        res_text = subprocess.run(cmd_text, capture_output=True, text=True)
        self.assertEqual(res_text.returncode, 0)
        self.assertIn("TASK COMMANDER WORKFLOW BOARD", res_text.stdout)
        self.assertIn("TASK-01", res_text.stdout)

        # Mermaid render
        cmd_mermaid = [
            sys.executable,
            str(SCRIPTS_DIR / "render-workflow.py"),
            str(ckpt_template),
            "--format",
            "mermaid",
        ]
        res_mermaid = subprocess.run(cmd_mermaid, capture_output=True, text=True)
        self.assertEqual(res_mermaid.returncode, 0)
        self.assertIn("```mermaid", res_mermaid.stdout)
        self.assertIn("graph TD", res_mermaid.stdout)
        self.assertIn("TASK-01", res_mermaid.stdout)

        # Render from project-status.md
        status_template = TEMPLATES_DIR / "project-status.md"
        cmd_status = [
            sys.executable,
            str(SCRIPTS_DIR / "render-workflow.py"),
            str(status_template),
            "--format",
            "text",
        ]
        res_status = subprocess.run(cmd_status, capture_output=True, text=True)
        self.assertEqual(res_status.returncode, 0)
        self.assertIn("TASK COMMANDER WORKFLOW BOARD", res_status.stdout)

    def plan(self, tasks=None):
        return {"id": "wf-test", "max_concurrency": 1,
                "tasks": tasks or [{"id": "01", "command": [sys.executable, "-c", "print('ok')"]}]}

    def cli(self, *args):
        return subprocess.run([sys.executable, "-B", str(SCRIPTS_DIR / "run-workflow.py"),
                               "--project-root", str(self.work_path), *map(str, args)],
                              capture_output=True, encoding="utf-8")

    def start(self, plan, dry_run=False):
        plan_path = self.work_path / "plan.json"
        checkpoint = self.work_path / "checkpoint.json"
        plan_path.write_text(json.dumps(plan), encoding="utf-8")
        flags = ["--dry-run"] if dry_run else []
        result = self.cli("--plan", plan_path, "--checkpoint", checkpoint, *flags)
        return checkpoint, result

    def read_state(self, path):
        return json.loads(path.read_text(encoding="utf-8"))

    def marker_command(self, name):
        return [sys.executable, "-c",
                "from pathlib import Path; import sys; p=Path(sys.argv[1]); "
                "p.write_text(p.read_text()+'x' if p.exists() else 'x')", name]

    def test_resume_executes_saved_command_and_skips_successful_prefix(self):
        plan = self.plan([
            {"id": "01", "command": self.marker_command("first.txt")},
            {"id": "02", "risk_level": "HIGH", "requires_checkpoint": False,
             "depends_on": ["01"], "command": self.marker_command("second.txt")},
        ])
        checkpoint, result = self.start(plan)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.work_path / "second.txt").exists())
        self.assertEqual(self.read_state(checkpoint)["task_states"]["02"]["status"], "CHECKPOINT_SUSPENDED")
        approval = self.cli("--checkpoint", checkpoint, "--approve", "02")
        self.assertEqual(approval.returncode, 0, approval.stderr)
        self.assertFalse((self.work_path / "second.txt").exists())
        resumed = self.cli("--resume-from", checkpoint)
        self.assertEqual(resumed.returncode, 0, resumed.stderr)
        self.assertEqual((self.work_path / "first.txt").read_text(), "x")
        self.assertEqual((self.work_path / "second.txt").read_text(), "x")
        self.assertEqual(self.read_state(checkpoint)["status"], "COMPLETED")
        self.assertIn("project gates remain separate", resumed.stdout)

    def test_all_high_risk_levels_suspend_without_flag(self):
        for risk in ("HIGH", "CRITICAL"):
            with self.subTest(risk=risk):
                checkpoint, result = self.start(self.plan([
                    {"id": "01", "risk_level": risk, "requires_checkpoint": False,
                     "command": self.marker_command("unsafe.txt")},
                ]))
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(self.read_state(checkpoint)["status"], "CHECKPOINT_SUSPENDED")
                self.assertFalse((self.work_path / "unsafe.txt").exists())
                checkpoint.unlink()

    def test_ready_without_scoped_approval_is_rejected(self):
        checkpoint, _ = self.start(self.plan([
            {"id": "01", "risk_level": "HIGH", "command": self.marker_command("unsafe.txt")},
        ]))
        state = self.read_state(checkpoint)
        state["task_states"]["01"]["status"] = "READY"
        state["checkpoint_task"] = None
        checkpoint.write_text(json.dumps(state), encoding="utf-8")
        result = self.cli("--resume-from", checkpoint)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("scoped approval", result.stderr)
        self.assertFalse((self.work_path / "unsafe.txt").exists())

    def test_missing_or_empty_command_rejected_even_in_dry_run(self):
        for command in (None, "", "  ", [], [""], [1]):
            with self.subTest(command=command):
                checkpoint, result = self.start(self.plan([{"id": "01", "command": command}]), True)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("requires a nonempty command", result.stderr)
                self.assertFalse(checkpoint.exists())

    def test_corrupt_checkpoint_is_preserved_without_replay(self):
        checkpoint = self.work_path / "checkpoint.json"
        raw = '{"task_states":'
        checkpoint.write_text(raw, encoding="utf-8")
        result = self.cli("--resume-from", checkpoint)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(checkpoint.read_text(encoding="utf-8"), raw)
        self.assertFalse(checkpoint.with_name(checkpoint.name + ".lock").exists())

    def test_existing_checkpoint_requires_explicit_resume(self):
        checkpoint, _ = self.start(self.plan())
        before = checkpoint.read_bytes()
        result = self.cli("--plan", self.work_path / "plan.json", "--checkpoint", checkpoint)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("already exists", result.stderr)
        self.assertEqual(checkpoint.read_bytes(), before)

    def test_legacy_checkpoint_is_not_silently_migrated(self):
        checkpoint = self.work_path / "old.json"
        checkpoint.write_text('{"workflow_id": "old", "task_states": {}}', encoding="utf-8")
        before = checkpoint.read_bytes()
        result = self.cli("--resume-from", checkpoint)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Unsupported checkpoint schema", result.stderr)
        self.assertEqual(checkpoint.read_bytes(), before)

    def test_render_only_example_cannot_resume(self):
        result = self.cli("--resume-from", TEMPLATES_DIR / "workflow-checkpoint.json")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Render-only", result.stderr)

    def test_changed_plan_is_rejected_without_running_action(self):
        checkpoint, _ = self.start(self.plan(), True)
        changed = self.plan([{"id": "01", "command": self.marker_command("changed.txt")}])
        plan_path = self.work_path / "changed.json"
        plan_path.write_text(json.dumps(changed), encoding="utf-8")
        before = checkpoint.read_bytes()
        result = self.cli("--resume-from", checkpoint, "--plan", plan_path, "--dry-run")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("different or changed plan", result.stderr)
        self.assertEqual(checkpoint.read_bytes(), before)
        self.assertFalse((self.work_path / "changed.txt").exists())

    def test_tampered_plan_hash_is_rejected(self):
        checkpoint, _ = self.start(self.plan(), True)
        state = self.read_state(checkpoint)
        state["plan"]["tasks"][0]["command"] = self.marker_command("tampered.txt")
        checkpoint.write_text(json.dumps(state), encoding="utf-8")
        result = self.cli("--resume-from", checkpoint, "--dry-run")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("hash mismatch", result.stderr)
        self.assertFalse((self.work_path / "tampered.txt").exists())

    def test_checkpoint_root_mismatch_rejected(self):
        checkpoint, _ = self.start(self.plan(), True)
        alternate = self.work_path / "other"
        alternate.mkdir()
        result = self.cli("--resume-from", checkpoint, "--dry-run", "--project-root", alternate)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("project root changed", result.stderr)

    def test_dry_run_never_executes_and_cannot_certify_real_work(self):
        checkpoint, result = self.start(self.plan([
            {"id": "01", "command": self.marker_command("real.txt")},
        ]), True)
        self.assertEqual(result.returncode, 0, result.stderr)
        state = self.read_state(checkpoint)
        self.assertEqual(state["completed_tasks"], [])
        self.assertEqual(state["simulated_tasks"], ["01"])
        self.assertEqual(state["status"], "SIMULATED")
        self.assertNotIn("exit_code", state["task_states"]["01"])
        self.assertFalse((self.work_path / "real.txt").exists())
        before = checkpoint.read_bytes()
        resumed = self.cli("--resume-from", checkpoint)
        self.assertNotEqual(resumed.returncode, 0)
        self.assertIn("cannot be interchanged", resumed.stderr)
        self.assertEqual(checkpoint.read_bytes(), before)

    def test_real_checkpoint_cannot_be_resumed_as_simulation(self):
        checkpoint, result = self.start(self.plan())
        self.assertEqual(result.returncode, 0, result.stderr)
        result = self.cli("--resume-from", checkpoint, "--dry-run")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("cannot be interchanged", result.stderr)

    def test_interrupted_task_does_not_replay_without_retry_authorization(self):
        plan = self.plan([{"id": "01", "command": self.marker_command("attempts.txt")}])
        checkpoint = self.work_path / "checkpoint.json"
        engine = ENGINE.WorkflowOrchestrator(plan, checkpoint, self.work_path)
        engine.state["task_states"]["01"].update(status="RUNNING", started_at=ENGINE.now())
        engine.save_checkpoint()
        result = self.cli("--resume-from", checkpoint)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.read_state(checkpoint)["status"], "RECOVERY_REQUIRED")
        self.assertFalse((self.work_path / "attempts.txt").exists())
        retry = self.cli("--checkpoint", checkpoint, "--retry", "01")
        self.assertEqual(retry.returncode, 0, retry.stderr)
        self.assertFalse((self.work_path / "attempts.txt").exists())
        result = self.cli("--resume-from", checkpoint)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.work_path / "attempts.txt").read_text(), "x")
        self.assertEqual(self.read_state(checkpoint)["task_states"]["01"]["attempt_history"][0]["status"], "RUNNING")

    def test_failed_command_blocks_retry_and_downstream_commands(self):
        plan = self.plan([
            {"id": "01", "command": [sys.executable, "-c", "raise SystemExit(7)"]},
            {"id": "02", "depends_on": ["01"], "command": self.marker_command("downstream.txt")},
        ])
        checkpoint, result = self.start(plan)
        self.assertNotEqual(result.returncode, 0)
        state = self.read_state(checkpoint)
        self.assertEqual(state["task_states"]["01"]["exit_code"], 7)
        self.assertEqual(state["task_states"]["02"]["status"], "PENDING")
        before = checkpoint.read_bytes()
        result = self.cli("--resume-from", checkpoint)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(checkpoint.read_bytes(), before)
        self.assertFalse((self.work_path / "downstream.txt").exists())

    def test_high_risk_retry_preserves_attempt_and_clears_approval(self):
        checkpoint, _ = self.start(self.plan([
            {"id": "01", "risk_level": "HIGH", "command": [sys.executable, "-c", "raise SystemExit(3)"]},
        ]))
        self.assertEqual(self.cli("--checkpoint", checkpoint, "--approve", "01").returncode, 0)
        self.assertNotEqual(self.cli("--resume-from", checkpoint).returncode, 0)
        self.assertEqual(self.cli("--checkpoint", checkpoint, "--retry", "01").returncode, 0)
        info = self.read_state(checkpoint)["task_states"]["01"]
        self.assertNotIn("approved_at", info)
        self.assertEqual(info["attempt_history"][0]["exit_code"], 3)
        result = self.cli("--resume-from", checkpoint)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.read_state(checkpoint)["status"], "CHECKPOINT_SUSPENDED")

    def test_approve_cannot_approve_pending_or_completed_node(self):
        checkpoint, _ = self.start(self.plan())
        before = checkpoint.read_bytes()
        result = self.cli("--checkpoint", checkpoint, "--approve", "01")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(checkpoint.read_bytes(), before)

    def test_atomic_replace_failure_preserves_checkpoint_and_cleans_temp(self):
        checkpoint = self.work_path / "checkpoint.json"
        engine = ENGINE.WorkflowOrchestrator(self.plan(), checkpoint, self.work_path)
        engine.save_checkpoint()
        before = checkpoint.read_bytes()
        with patch.object(ENGINE.os, "replace", side_effect=OSError("simulated replace failure")):
            with self.assertRaises(OSError):
                engine.save_checkpoint(status="FAILED")
        self.assertEqual(checkpoint.read_bytes(), before)
        self.assertEqual(list(self.work_path.glob("_tmp_workflow_*")), [])

    def test_checkpoint_is_saved_before_real_command_and_after_interrupt(self):
        checkpoint = self.work_path / "checkpoint.json"
        engine = ENGINE.WorkflowOrchestrator(self.plan(), checkpoint, self.work_path)
        observed = []
        def interrupt(*args, **kwargs):
            observed.append(self.read_state(checkpoint)["task_states"]["01"]["status"])
            raise KeyboardInterrupt()
        with patch.object(ENGINE.subprocess, "run", side_effect=interrupt), contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(KeyboardInterrupt):
                engine.run()
        self.assertEqual(observed, ["RUNNING"])
        self.assertEqual(self.read_state(checkpoint)["status"], "RECOVERY_REQUIRED")
        self.assertEqual(self.read_state(checkpoint)["task_states"]["01"]["status"], "RUNNING")

    def test_lock_is_exclusive_and_existing_lock_is_not_deleted(self):
        checkpoint = self.work_path / "checkpoint.json"
        lock = checkpoint.with_name(checkpoint.name + ".lock")
        with ENGINE.checkpoint_lock(checkpoint):
            self.assertTrue(lock.exists())
            result = self.cli("--resume-from", checkpoint)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Checkpoint locked", result.stderr)
            self.assertTrue(lock.exists())
        self.assertFalse(lock.exists())

    def test_invalid_dag_and_concurrency_rejected_before_execution(self):
        invalid = [
            self.plan([{"id": "01", "command": "echo x"}, {"id": "01", "command": "echo y"}]),
            self.plan([{"id": "01", "command": "echo x", "depends_on": ["missing"]}]),
            self.plan([{"id": "01", "command": "echo x", "depends_on": ["01"]}]),
            self.plan([{"id": "01", "command": "echo x", "depends_on": "01"}]),
            self.plan([{"id": "01", "command": "echo x", "risk_level": "Unknown"}]),
            self.plan([{"id": "01", "command": "echo x", "requires_checkpoint": "false"}]),
            dict(self.plan(), max_concurrency=2),
            dict(self.plan(), tasks=[]),
        ]
        for plan in invalid:
            with self.subTest(plan=plan):
                checkpoint, result = self.start(plan)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(checkpoint.exists())

    def test_checkpoint_completion_list_and_dependencies_are_validated(self):
        checkpoint, _ = self.start(self.plan(), True)
        original = self.read_state(checkpoint)
        mutations = [
            lambda state: state.update(completed_tasks=["01"]),
            lambda state: state.update(simulated_tasks=[]),
            lambda state: state["task_states"]["01"].update(status="UNKNOWN"),
            lambda state: state.update(checkpoint_task="01"),
            lambda state: state["task_states"]["01"].update(depends_on=["missing"]),
            lambda state: state["task_states"]["01"].update(risk_level="HIGH"),
        ]
        for mutate in mutations:
            with self.subTest(mutation=mutate):
                state = json.loads(json.dumps(original))
                mutate(state)
                checkpoint.write_text(json.dumps(state), encoding="utf-8")
                before = checkpoint.read_bytes()
                result = self.cli("--resume-from", checkpoint, "--dry-run")
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(checkpoint.read_bytes(), before)

    def test_completed_node_cannot_skip_unsatisfied_dependency(self):
        plan = self.plan([
            {"id": "01", "command": self.marker_command("first.txt")},
            {"id": "02", "depends_on": ["01"], "command": self.marker_command("second.txt")},
        ])
        checkpoint = self.work_path / "checkpoint.json"
        engine = ENGINE.WorkflowOrchestrator(plan, checkpoint, self.work_path)
        engine.state["task_states"]["02"].update(status="COMPLETED", exit_code=0,
                                                  started_at=ENGINE.now(), completed_at=ENGINE.now())
        engine.state["completed_tasks"] = ["02"]
        engine.save_checkpoint()
        result = self.cli("--resume-from", checkpoint)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unsatisfied dependencies", result.stderr)
        self.assertFalse((self.work_path / "first.txt").exists())
        self.assertFalse((self.work_path / "second.txt").exists())

    def test_failed_precommand_save_never_executes_command(self):
        checkpoint = self.work_path / "checkpoint.json"
        engine = ENGINE.WorkflowOrchestrator(self.plan(), checkpoint, self.work_path)
        engine.save_checkpoint()
        before = checkpoint.read_bytes()
        with patch.object(ENGINE.os, "replace", side_effect=OSError("save failed")), \
                patch.object(ENGINE.subprocess, "run") as command, contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(OSError):
                engine.run()
            command.assert_not_called()
        self.assertEqual(checkpoint.read_bytes(), before)

    def test_renderer_distinguishes_simulation_and_project_states(self):
        data = {"record_kind": "command-progress", "dry_run": True,
                "task_states": {"end": {"name": 'A "quoted" task', "status": "SIMULATED"}}}
        text = RENDERER.render_terminal(data)
        self.assertIn("not project acceptance", text)
        self.assertIn("[SIM]", text)
        mermaid = RENDERER.render_mermaid(data)
        self.assertIn("node_0", mermaid)
        self.assertIn("&quot;", mermaid)
        self.assertIn(":::simulated", mermaid)
        project = {"record_kind": "project-status", "task_states": {
            "01": {"status": "Completed"}, "02": {"status": "In Progress"}, "03": {"status": "Blocked"}}}
        text = RENDERER.render_terminal(project)
        self.assertIn("[OK] Completed", text)
        self.assertIn("[>>] In Progress", text)
        self.assertIn("[PAUSED] Blocked", text)

    def test_started_task_cannot_be_rewound_to_ready_or_pending(self):
        checkpoint, _ = self.start(self.plan([
            {"id": "01", "risk_level": "HIGH", "command": self.marker_command("replay.txt")},
        ]))
        self.assertEqual(self.cli("--checkpoint", checkpoint, "--approve", "01").returncode, 0)
        approved = self.read_state(checkpoint)
        for status in ("READY", "PENDING"):
            with self.subTest(status=status):
                state = json.loads(json.dumps(approved))
                state["task_states"]["01"].update(status=status, started_at=ENGINE.now())
                checkpoint.write_text(json.dumps(state), encoding="utf-8")
                before = checkpoint.read_bytes()
                result = self.cli("--resume-from", checkpoint)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("current-attempt evidence", result.stderr)
                self.assertEqual(checkpoint.read_bytes(), before)
                self.assertFalse((self.work_path / "replay.txt").exists())

    def test_approval_is_bound_to_current_attempt(self):
        checkpoint, _ = self.start(self.plan([
            {"id": "01", "risk_level": "HIGH", "command": [sys.executable, "-c", "raise SystemExit(1)"]},
        ]))
        self.assertEqual(self.cli("--checkpoint", checkpoint, "--approve", "01").returncode, 0)
        first = self.read_state(checkpoint)["task_states"]["01"]
        self.assertNotEqual(self.cli("--resume-from", checkpoint).returncode, 0)
        self.assertEqual(self.cli("--checkpoint", checkpoint, "--retry", "01").returncode, 0)
        state = self.read_state(checkpoint)
        info = state["task_states"]["01"]
        self.assertEqual(info["attempt"], 2)
        info.update(status="READY", approved_at=first["approved_at"],
                    approval_plan_hash=first["approval_plan_hash"], approval_attempt=first["approval_attempt"])
        checkpoint.write_text(json.dumps(state), encoding="utf-8")
        result = self.cli("--resume-from", checkpoint)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("scoped approval", result.stderr)

    def test_workflow_stop_state_must_match_task_frontier(self):
        engine = ENGINE.WorkflowOrchestrator(self.plan([
            {"id": "01", "command": self.marker_command("unexpected.txt")},
        ]), self.work_path / "checkpoint.json", self.work_path)
        for status in ("RECOVERY_REQUIRED", "FAILED", "CHECKPOINT_SUSPENDED", "COMPLETED"):
            with self.subTest(status=status):
                engine.save_checkpoint(status=status)
                before = engine.checkpoint_path.read_bytes()
                result = self.cli("--resume-from", engine.checkpoint_path)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("inconsistent with task frontier", result.stderr)
                self.assertEqual(engine.checkpoint_path.read_bytes(), before)
                self.assertFalse((self.work_path / "unexpected.txt").exists())

    def test_multiple_sequential_frontiers_rejected_before_retry_write(self):
        engine = ENGINE.WorkflowOrchestrator(self.plan([
            {"id": "01", "command": self.marker_command("first.txt")},
            {"id": "02", "risk_level": "HIGH", "command": self.marker_command("second.txt")},
        ]), self.work_path / "checkpoint.json", self.work_path)
        engine.state["task_states"]["01"].update(status="RUNNING", started_at=ENGINE.now())
        engine.state["task_states"]["02"]["status"] = "CHECKPOINT_SUSPENDED"
        engine.save_checkpoint(status="CHECKPOINT_SUSPENDED", checkpoint_task="02")
        before = engine.checkpoint_path.read_bytes()
        result = self.cli("--checkpoint", engine.checkpoint_path, "--retry", "01")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("sequential execution frontier", result.stderr)
        self.assertEqual(engine.checkpoint_path.read_bytes(), before)
        self.assertFalse((self.work_path / "first.txt").exists())

    def test_null_metadata_is_rejected_before_runner_execution(self):
        for field in ("name", "agent", "type", "output_dir"):
            with self.subTest(field=field):
                checkpoint, result = self.start(self.plan([
                    {"id": "01", "command": self.marker_command("unexpected.txt"), field: None},
                ]))
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("metadata", result.stderr)
                self.assertFalse(checkpoint.exists())
                self.assertFalse((self.work_path / "unexpected.txt").exists())

    def test_renderer_handles_null_display_fields_and_rejects_null_task(self):
        source = self.work_path / "display.json"
        source.write_text(json.dumps({"task_states": {"01": {"agent": None, "name": None}}}), encoding="utf-8")
        data = RENDERER.load_state_data(source)
        self.assertIn("Unknown", RENDERER.render_terminal(data))
        source.write_text(json.dumps({"task_states": {"01": None}}), encoding="utf-8")
        result = subprocess.run([sys.executable, "-B", str(SCRIPTS_DIR / "render-workflow.py"), str(source)],
                                capture_output=True, encoding="utf-8")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Invalid checkpoint display entry", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_markdown_renderer_preserves_escaped_pipes_and_state_columns(self):
        source = self.work_path / "status.md"
        source.write_text(
            "## Task list\n"
            "| ID | Name | Status | Priority | Agent | Depends |\n"
            "| --- | --- | --- | --- | --- | --- |\n"
            r"| 01 | A \| B | In Progress | P1 | Executor | - |" "\n"
            "## Blocked\n"
            "| Task | Pre-block state | Reason | Owner | Done-when | Next check |\n"
            r"| 01 | In Progress | foo \| bar | User | ready | tomorrow |" "\n",
            encoding="utf-8",
        )
        data = RENDERER.load_state_data(source)
        self.assertEqual(data["task_states"]["01"]["name"], "A | B")
        self.assertEqual(data["task_states"]["01"]["status"], "In Progress")
        self.assertEqual(data["task_states"]["01"]["agent"], "Executor")
        self.assertEqual(data["task_states"]["01"]["depends_on"], [])
        self.assertEqual(data["blocked_items"][0]["reason"], "foo | bar")
        self.assertEqual(data["blocked_items"][0]["owner"], "User")

    def test_runner_does_not_modify_central_project_status(self):
        status = self.work_path / "project-status.md"
        original = "Central records belong to Commander.\n"
        status.write_text(original, encoding="utf-8")
        _, result = self.start(self.plan())
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(status.read_text(encoding="utf-8"), original)


if __name__ == "__main__":
    unittest.main()
