#!/usr/bin/env python3
"""run-workflow.py - Dynamic Workflow Orchestrator for Task Commander.

Executes DAG workflows with concurrency control, risk checkpoints,
receipt generation, and resume capabilities.
"""

from __future__ import annotations

import argparse
import datetime
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


def load_workflow_plan(plan_path: Path) -> Dict[str, Any]:
    """Loads workflow definition from a python file or json file."""
    if not plan_path.is_file():
        raise FileNotFoundError(f"Workflow plan not found: {plan_path}")

    if plan_path.suffix == ".py":
        spec = importlib.util.spec_from_file_location("dynamic_plan", plan_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load module from {plan_path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if not hasattr(module, "WORKFLOW"):
            raise ValueError(f"Workflow python file {plan_path} must define 'WORKFLOW' dict")
        return getattr(module, "WORKFLOW")
    elif plan_path.suffix == ".json":
        with open(plan_path, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        raise ValueError(f"Unsupported plan format: {plan_path.suffix}. Expected .py or .json")


def validate_dag(tasks: List[Dict[str, Any]]) -> List[str]:
    """Validates DAG structure, checks for circular dependencies, returns topological order."""
    task_map = {t["id"]: t for t in tasks}
    in_degree = {t["id"]: 0 for t in tasks}
    adjacency: Dict[str, List[str]] = {t["id"]: [] for t in tasks}

    for t in tasks:
        deps = t.get("depends_on", [])
        for dep in deps:
            if dep not in task_map:
                raise ValueError(f"Task {t['id']} depends on nonexistent task {dep}")
            adjacency[dep].append(t["id"])
            in_degree[t["id"]] += 1

    queue = [tid for tid, deg in in_degree.items() if deg == 0]
    order = []

    while queue:
        curr = queue.pop(0)
        order.append(curr)
        for nxt in adjacency[curr]:
            in_degree[nxt] -= 1
            if in_degree[nxt] == 0:
                queue.append(nxt)

    if len(order) != len(tasks):
        raise ValueError("Cyclic dependency detected in workflow DAG!")

    return order


class WorkflowOrchestrator:
    def __init__(
        self,
        plan: Dict[str, Any],
        checkpoint_path: Path,
        project_root: Path,
        dry_run: bool = False,
    ):
        self.plan = plan
        self.checkpoint_path = checkpoint_path
        self.project_root = project_root
        self.dry_run = dry_run
        self.tasks: List[Dict[str, Any]] = plan.get("tasks", [])
        self.task_map: Dict[str, Dict[str, Any]] = {t["id"]: t for t in self.tasks}
        self.max_concurrency: int = max(1, plan.get("max_concurrency", 2))

        self.execution_order = validate_dag(self.tasks)
        self.state: Dict[str, Any] = self._init_or_load_state()

    def _init_or_load_state(self) -> Dict[str, Any]:
        if self.checkpoint_path.is_file():
            try:
                with open(self.checkpoint_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass

        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        initial_task_states = {}
        for t in self.tasks:
            initial_task_states[t["id"]] = {
                "name": t.get("name", t["id"]),
                "status": "PENDING",
                "agent": t.get("agent", "Executor"),
                "risk_level": t.get("risk_level", "LOW"),
                "requires_checkpoint": t.get("requires_checkpoint", False),
                "depends_on": t.get("depends_on", []),
                "output_dir": t.get("output_dir", f"task-output/{t['id']}"),
            }

        return {
            "workflow_id": self.plan.get("id", "wf-default"),
            "workflow_name": self.plan.get("name", "Default Workflow"),
            "started_at": now,
            "updated_at": now,
            "status": "IN_PROGRESS",
            "checkpoint_task": None,
            "completed_tasks": [],
            "task_states": initial_task_states,
        }

    def save_checkpoint(self, status: Optional[str] = None, checkpoint_task: Optional[str] = None):
        self.state["updated_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        if status:
            self.state["status"] = status
        if checkpoint_task is not None:
            self.state["checkpoint_task"] = checkpoint_task

        self.checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.checkpoint_path, "w", encoding="utf-8") as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)
            f.write("\n")

    def approve_checkpoint(self, task_id: Optional[str] = None):
        target = task_id or self.state.get("checkpoint_task")
        if not target or target not in self.state["task_states"]:
            return False, f"No suspended checkpoint found for task {target}"

        task_st = self.state["task_states"][target]
        if task_st["status"] != "CHECKPOINT_SUSPENDED":
            return False, f"Task {target} is not in CHECKPOINT_SUSPENDED state (current: {task_st['status']})"

        task_st["status"] = "READY"
        task_st["approved_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        self.state["checkpoint_task"] = None
        self.state["status"] = "IN_PROGRESS"
        self.save_checkpoint()
        return True, f"Checkpoint for {target} approved. Ready to resume."

    def execute_task(self, task: Dict[str, Any]) -> bool:
        tid = task["id"]
        tst = self.state["task_states"][tid]

        # Check for risk-based human gate
        if task.get("requires_checkpoint") and tst.get("status") != "READY" and "approved_at" not in tst:
            tst["status"] = "CHECKPOINT_SUSPENDED"
            tst["suspended_reason"] = (
                f"High-risk task ({task.get('risk_level', 'HIGH')}) requires explicit human approval."
            )
            self.save_checkpoint(status="CHECKPOINT_SUSPENDED", checkpoint_task=tid)
            print(f"[CHECKPOINT] Task {tid} ({task.get('name')}) paused for human approval.")
            return False

        tst["status"] = "RUNNING"
        tst["started_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        self.save_checkpoint()
        print(f"[RUNNING] Task {tid}: {task.get('name')} (Agent: {task.get('agent', 'Executor')})")

        command = task.get("command")
        if self.dry_run or not command:
            exit_code = 0
            output = "[dry-run] simulated execution success"
        else:
            try:
                res = subprocess.run(
                    command,
                    shell=True,
                    cwd=str(self.project_root),
                    capture_output=True,
                    text=True,
                )
                exit_code = res.returncode
                output = (res.stdout + "\n" + res.stderr).strip()
            except Exception as e:
                exit_code = -1
                output = f"Execution failed: {str(e)}"

        tst["exit_code"] = exit_code
        tst["completed_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()

        if exit_code == 0:
            tst["status"] = "COMPLETED"
            if tid not in self.state["completed_tasks"]:
                self.state["completed_tasks"].append(tid)
            print(f"[OK] Task {tid} completed successfully.")
            self.save_checkpoint()
            return True
        else:
            tst["status"] = "FAILED"
            tst["error"] = output
            self.save_checkpoint(status="FAILED")
            print(f"[FAILED] Task {tid} failed with exit code {exit_code}:\n{output}")
            return False

    def run(self) -> str:
        """Runs the workflow DAG until completion or checkpoint suspension."""
        while True:
            # Check completed
            all_done = all(
                self.state["task_states"][t]["status"] == "COMPLETED"
                for t in self.execution_order
            )
            if all_done:
                self.save_checkpoint(status="COMPLETED")
                print(f"[FINISHED] Workflow {self.state['workflow_id']} completed successfully.")
                return "COMPLETED"

            # Find ready tasks
            ready_tasks = []
            for tid in self.execution_order:
                tst = self.state["task_states"][tid]
                if tst["status"] in ("COMPLETED", "RUNNING", "FAILED"):
                    continue
                if tst["status"] == "CHECKPOINT_SUSPENDED":
                    # Currently paused
                    return "CHECKPOINT_SUSPENDED"

                # Check upstream dependencies
                deps = self.task_map[tid].get("depends_on", [])
                deps_satisfied = all(
                    self.state["task_states"][d]["status"] == "COMPLETED" for d in deps
                )

                if deps_satisfied:
                    ready_tasks.append(self.task_map[tid])

            if not ready_tasks:
                # Any failed?
                has_failed = any(
                    self.state["task_states"][t]["status"] == "FAILED"
                    for t in self.execution_order
                )
                if has_failed:
                    self.save_checkpoint(status="FAILED")
                    return "FAILED"
                # Deadlock or unknown condition
                return self.state.get("status", "UNKNOWN")

            # Execute batch within concurrency limit
            batch = ready_tasks[: self.max_concurrency]
            for task in batch:
                success = self.execute_task(task)
                if not success:
                    status = self.state["task_states"][task["id"]]["status"]
                    if status == "CHECKPOINT_SUSPENDED":
                        return "CHECKPOINT_SUSPENDED"
                    elif status == "FAILED":
                        return "FAILED"

        return self.state.get("status", "COMPLETED")


def main() -> int:
    parser = argparse.ArgumentParser(description="Task Commander Dynamic Workflow Engine")
    parser.add_argument("--plan", type=Path, help="Path to workflow plan (.py or .json)")
    parser.add_argument(
        "--checkpoint",
        type=Path,
        default=Path("workflow-checkpoint.json"),
        help="Path to checkpoint file",
    )
    parser.add_argument("--resume-from", type=Path, help="Resume execution from existing checkpoint")
    parser.add_argument("--approve", type=str, help="Approve suspended task ID at checkpoint")
    parser.add_argument("--dry-run", action="store_true", help="Simulate command execution without side effects")
    parser.add_argument("--project-root", type=Path, default=Path("."), help="Project root directory")

    args = parser.parse_args()
    checkpoint_file = args.resume_from or args.checkpoint

    if args.approve:
        if not checkpoint_file.is_file():
            print(f"Error: Checkpoint file {checkpoint_file} not found.", file=sys.stderr)
            return 1
        with open(checkpoint_file, "r", encoding="utf-8") as f:
            ckpt_data = json.load(f)
        orchestrator = WorkflowOrchestrator(
            plan={"id": ckpt_data.get("workflow_id"), "tasks": []},
            checkpoint_path=checkpoint_file,
            project_root=args.project_root,
        )
        ok, msg = orchestrator.approve_checkpoint(args.approve)
        print(msg)
        return 0 if ok else 1

    if not args.plan and not args.resume_from:
        print("Error: Either --plan or --resume-from must be specified.", file=sys.stderr)
        return 1

    if args.resume_from:
        if not args.resume_from.is_file():
            print(f"Error: Checkpoint file {args.resume_from} not found.", file=sys.stderr)
            return 1
        with open(args.resume_from, "r", encoding="utf-8") as f:
            ckpt_data = json.load(f)
        plan_data = {
            "id": ckpt_data.get("workflow_id", "resumed-wf"),
            "name": ckpt_data.get("workflow_name", "Resumed Workflow"),
            "tasks": [
                {
                    "id": tid,
                    "name": tst.get("name", tid),
                    "agent": tst.get("agent", "Executor"),
                    "risk_level": tst.get("risk_level", "LOW"),
                    "requires_checkpoint": tst.get("requires_checkpoint", False),
                    "depends_on": tst.get("depends_on", []),
                    "output_dir": tst.get("output_dir", f"task-output/{tid}"),
                }
                for tid, tst in ckpt_data.get("task_states", {}).items()
            ],
        }
    else:
        plan_data = load_workflow_plan(args.plan)

    orchestrator = WorkflowOrchestrator(
        plan=plan_data,
        checkpoint_path=checkpoint_file,
        project_root=args.project_root,
        dry_run=args.dry_run,
    )

    final_status = orchestrator.run()
    return 0 if final_status in ("COMPLETED", "CHECKPOINT_SUSPENDED") else 1


if __name__ == "__main__":
    sys.exit(main())
