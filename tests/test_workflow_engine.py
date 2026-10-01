from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = ROOT / "scripts"
TEMPLATES_DIR = ROOT / "templates"


class TestWorkflowEngine(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
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
        self.assertIn("TASK-01", data["completed_tasks"])
        self.assertIn("TASK-02", data["completed_tasks"])
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

        self.assertEqual(final_data["status"], "COMPLETED")
        self.assertEqual(len(final_data["completed_tasks"]), 4)

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


if __name__ == "__main__":
    unittest.main()
