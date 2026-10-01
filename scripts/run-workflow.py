#!/usr/bin/env python3
"""Optional sequential command runner; command success is not project acceptance.

DAG ordering, pre-command approval barriers and versioned atomic checkpoints only.
No agent dispatch, project-status writes, receipt certification or parallel execution.
Python plans and shell command strings are trusted executable code, not a sandbox.
"""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any


SCHEMA_VERSION = 2
TASK_STATES = {"PENDING", "READY", "RUNNING", "CHECKPOINT_SUSPENDED", "COMPLETED", "SIMULATED", "FAILED"}
WORKFLOW_STATES = {"IN_PROGRESS", "CHECKPOINT_SUSPENDED", "COMPLETED", "SIMULATED", "FAILED", "RECOVERY_REQUIRED"}


def now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def load_workflow_plan(plan_path: Path) -> dict[str, Any]:
    """Python plans execute on import, even in dry-run: load only trusted files."""
    if plan_path.suffix == ".py":
        spec = importlib.util.spec_from_file_location("dynamic_plan", plan_path)
        if spec is None or spec.loader is None:
            raise ValueError(f"Cannot load plan: {plan_path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if not hasattr(module, "WORKFLOW"):
            raise ValueError("Python plan must define WORKFLOW")
        return module.WORKFLOW
    if plan_path.suffix == ".json":
        return json.loads(plan_path.read_text(encoding="utf-8"))
    raise ValueError("Plan must be .py or .json")


def validate_dag(tasks: list[dict[str, Any]]) -> list[str]:
    if not isinstance(tasks, list) or not tasks:
        raise ValueError("Plan must contain a nonempty tasks list")
    task_map = {}
    for task in tasks:
        if not isinstance(task, dict) or not isinstance(task.get("id"), str) or not task["id"].strip():
            raise ValueError("Every task needs a nonblank string ID")
        if task["id"] in task_map:
            raise ValueError(f"Duplicate task ID: {task['id']}")
        task_map[task["id"]] = task
    degree = dict.fromkeys(task_map, 0)
    adjacency = {tid: [] for tid in task_map}
    for task in tasks:
        deps = task.get("depends_on", [])
        if not isinstance(deps, list) or any(not isinstance(dep, str) for dep in deps):
            raise ValueError(f"Invalid dependencies: {task['id']}")
        if len(deps) != len(set(deps)):
            raise ValueError(f"Duplicate dependency: {task['id']}")
        for dep in deps:
            if dep not in task_map:
                raise ValueError(f"Task {task['id']} depends on nonexistent task {dep}")
            adjacency[dep].append(task["id"])
            degree[task["id"]] += 1
    queue = [tid for tid, count in degree.items() if count == 0]
    order = []
    while queue:
        tid = queue.pop(0)
        order.append(tid)
        for successor in adjacency[tid]:
            degree[successor] -= 1
            if degree[successor] == 0:
                queue.append(successor)
    if len(order) != len(tasks):
        raise ValueError("Cyclic dependency detected in workflow DAG")
    return order


def validate_plan(plan: dict[str, Any]) -> list[str]:
    if not isinstance(plan, dict) or not isinstance(plan.get("id"), str) or not plan["id"].strip():
        raise ValueError("Plan needs a nonblank workflow ID")
    # This runner is intentionally sequential; old plans must not imply parallelism.
    concurrency = plan.get("max_concurrency", 1)
    if type(concurrency) is not int or concurrency != 1:
        raise ValueError("Sequential runner supports max_concurrency=1 only")
    order = validate_dag(plan.get("tasks"))
    for task in plan["tasks"]:
        command = task.get("command")
        valid = isinstance(command, str) and bool(command.strip())
        valid = valid or (isinstance(command, list) and bool(command)
                          and all(isinstance(arg, str) and bool(arg) for arg in command))
        if not valid:
            raise ValueError(f"Task {task['id']} requires a nonempty command (string or argv list)")
        for field in ("name", "agent", "type", "output_dir"):
            if field in task and (not isinstance(task[field], str) or not task[field].strip()):
                raise ValueError(f"Task {task['id']} metadata {field} must be a nonblank string")
        if task.get("risk_level", "LOW") not in {"LOW", "MEDIUM", "HIGH", "CRITICAL"}:
            raise ValueError(f"Invalid risk level: {task['id']}")
        if type(task.get("requires_checkpoint", False)) is not bool:
            raise ValueError(f"requires_checkpoint must be boolean: {task['id']}")
    return order


def plan_hash(plan: dict[str, Any]) -> str:
    serialized = json.dumps(plan, sort_keys=True, ensure_ascii=False, allow_nan=False)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def requires_approval(task: dict[str, Any]) -> bool:
    return task.get("requires_checkpoint", False) or task.get("risk_level", "LOW") in {"HIGH", "CRITICAL"}


def read_checkpoint(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("Unsupported checkpoint schema; preserve old evidence and reconcile manually")
    if data.get("example_only"):
        raise ValueError("Render-only checkpoint example cannot be resumed")
    if not isinstance(data.get("plan"), dict):
        raise ValueError("Checkpoint is missing its executable plan snapshot")
    validate_plan(data["plan"])
    if data.get("plan_hash") != plan_hash(data["plan"]):
        raise ValueError("Checkpoint plan hash mismatch")
    return data


@contextmanager
def checkpoint_lock(path: Path):
    """Single CLI writer. A stale lock requires human reconciliation, never auto-deletion."""
    lock_path = path.with_name(path.name + ".lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise ValueError(f"Checkpoint locked: {lock_path}; reconcile the owning process before removing a stale lock") from exc
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(f"pid={os.getpid()}\n")
        yield
    finally:
        lock_path.unlink()


class WorkflowOrchestrator:
    def __init__(self, plan: dict[str, Any], checkpoint_path: Path,
                 project_root: Path, dry_run: bool = False, resume: bool = False):
        self.execution_order = validate_plan(plan)
        # Snapshot mutable caller input using the same JSON representation used on disk.
        self.plan = json.loads(json.dumps(plan, ensure_ascii=False, allow_nan=False))
        self.digest = plan_hash(self.plan)
        self.tasks = self.plan["tasks"]
        self.task_map = {task["id"]: task for task in self.tasks}
        self.checkpoint_path = checkpoint_path.resolve()
        self.project_root = project_root.resolve(strict=True)
        if not self.project_root.is_dir():
            raise ValueError("Project root must be a directory")
        self.dry_run = dry_run
        self.success_state = "SIMULATED" if dry_run else "COMPLETED"
        if resume:
            self.state = read_checkpoint(self.checkpoint_path)
            self._validate_state()
        else:
            if self.checkpoint_path.exists():
                raise ValueError("Checkpoint already exists; use --resume-from or a new checkpoint path")
            states = {}
            for task in self.tasks:
                states[task["id"]] = {
                    "name": task.get("name", task["id"]), "status": "PENDING",
                    "attempt": 1, "attempt_history": [],
                    "agent": task.get("agent", "Executor"),
                    "risk_level": task.get("risk_level", "LOW"),
                    "requires_checkpoint": requires_approval(task),
                    "depends_on": task.get("depends_on", []),
                    "output_dir": task.get("output_dir", f"task-output/{task['id']}"),
                }
            stamp = now()
            self.state = {
                "schema_version": SCHEMA_VERSION, "workflow_id": self.plan["id"],
                "workflow_name": self.plan.get("name", self.plan["id"]),
                "plan": self.plan, "plan_hash": self.digest,
                "project_root": str(self.project_root), "dry_run": dry_run,
                "started_at": stamp, "updated_at": stamp, "status": "IN_PROGRESS",
                "checkpoint_task": None, "completed_tasks": [], "simulated_tasks": [],
                "task_states": states,
            }

    def _validate_state(self):
        data = self.state
        if data.get("workflow_id") != self.plan["id"] or data.get("plan_hash") != self.digest:
            raise ValueError("Checkpoint belongs to a different or changed plan")
        if data.get("project_root") != str(self.project_root):
            raise ValueError("Checkpoint project root changed; reconcile before resuming")
        if type(data.get("dry_run")) is not bool or data["dry_run"] != self.dry_run:
            raise ValueError("Dry-run and real checkpoints cannot be interchanged")
        states = data.get("task_states")
        if not isinstance(states, dict) or set(states) != set(self.task_map):
            raise ValueError("Checkpoint task set does not match plan")
        for tid, info in states.items():
            if not isinstance(info, dict) or info.get("status") not in TASK_STATES:
                raise ValueError(f"Invalid checkpoint task state: {tid}")
        completed, simulated, suspended = [], [], []
        for tid, info in states.items():
            status = info["status"]
            if status in {"SIMULATED", "COMPLETED"} and status != self.success_state:
                raise ValueError(f"Task {tid} has an incompatible simulation/result state")
            if status == "COMPLETED":
                if type(info.get("exit_code")) is not int or info["exit_code"] != 0:
                    raise ValueError(f"Task {tid} lacks a successful command result")
                completed.append(tid)
            if status == "SIMULATED":
                simulated.append(tid)
            if status == "CHECKPOINT_SUSPENDED":
                suspended.append(tid)
            task = self.task_map[tid]
            expected_metadata = {
                "name": task.get("name", tid), "agent": task.get("agent", "Executor"),
                "risk_level": task.get("risk_level", "LOW"),
                "requires_checkpoint": requires_approval(task),
                "depends_on": task.get("depends_on", []),
                "output_dir": task.get("output_dir", f"task-output/{tid}"),
            }
            if any(info.get(key) != value for key, value in expected_metadata.items()):
                raise ValueError(f"Checkpoint task metadata differs from plan: {tid}")
            if status == "CHECKPOINT_SUSPENDED" and not requires_approval(task):
                raise ValueError(f"Unexpected approval barrier: {tid}")
            if status != "PENDING" and any(states[dep].get("status") != self.success_state
                                           for dep in task.get("depends_on", [])):
                raise ValueError(f"Checkpoint has unsatisfied dependencies for {tid}")
            attempt = info.get("attempt")
            history = info.get("attempt_history")
            if (type(attempt) is not int or attempt < 1 or not isinstance(history, list)
                    or len(history) != attempt - 1 or any(
                        not isinstance(entry, dict) or entry.get("attempt") != index
                        or entry.get("status") not in {"RUNNING", "FAILED"}
                        for index, entry in enumerate(history, start=1))):
                raise ValueError(f"Invalid attempt history for {tid}")
            result_fields = {"started_at", "completed_at", "exit_code", "error"}
            approval_fields = {"approved_at", "approval_plan_hash", "approval_attempt"}
            if status in {"PENDING", "READY", "CHECKPOINT_SUSPENDED"} and result_fields.intersection(info):
                raise ValueError(f"Unstarted task {tid} retains current-attempt evidence")
            if status in {"PENDING", "CHECKPOINT_SUSPENDED"} and approval_fields.intersection(info):
                raise ValueError(f"Unapproved task {tid} retains approval")
            if status in {"RUNNING", "FAILED", self.success_state} and not isinstance(info.get("started_at"), str):
                raise ValueError(f"Task {tid} lacks a recorded start")
            if status in {"FAILED", self.success_state} and not isinstance(info.get("completed_at"), str):
                raise ValueError(f"Task {tid} lacks a recorded finish")
            if status == "RUNNING" and {"completed_at", "exit_code", "error"}.intersection(info):
                raise ValueError(f"Running task {tid} retains result evidence")
            if status == "FAILED" and (type(info.get("exit_code")) is not int or info["exit_code"] == 0):
                raise ValueError(f"Failed task {tid} lacks a failure exit code")
            if status == "SIMULATED" and {"exit_code", "error"}.intersection(info):
                raise ValueError(f"Simulated task {tid} contains real command results")
            approved = (info.get("approval_plan_hash") == self.digest
                        and info.get("approval_attempt") == attempt
                        and isinstance(info.get("approved_at"), str) and bool(info["approved_at"]))
            if requires_approval(task) and status in {"READY", "RUNNING", "FAILED", self.success_state} and not approved:
                raise ValueError(f"Checkpoint lacks scoped approval for {tid}")
        for key, expected in (("completed_tasks", completed), ("simulated_tasks", simulated)):
            values = data.get(key)
            if (not isinstance(values, list) or any(not isinstance(tid, str) for tid in values)
                    or len(values) != len(set(values)) or set(values) != set(expected)):
                raise ValueError(f"Inconsistent checkpoint {key}")
        if len(suspended) > 1 or data.get("checkpoint_task") != (suspended[0] if suspended else None):
            raise ValueError("Inconsistent suspended checkpoint pointer")
        if data.get("status") not in WORKFLOW_STATES:
            raise ValueError("Invalid workflow status")
        # A sequential run has a successful prefix, at most one active frontier,
        # then only PENDING tasks. Reject impossible combinations before writes.
        frontier = None
        for tid in self.execution_order:
            status = states[tid]["status"]
            if frontier is None and status == self.success_state:
                continue
            if frontier is None:
                frontier = status
            elif status != "PENDING":
                raise ValueError("Checkpoint has inconsistent sequential execution frontier")
        allowed_workflow_states = {
            None: {"IN_PROGRESS", self.success_state},
            "PENDING": {"IN_PROGRESS"}, "READY": {"IN_PROGRESS"},
            "RUNNING": {"IN_PROGRESS", "RECOVERY_REQUIRED"},
            "FAILED": {"FAILED"}, "CHECKPOINT_SUSPENDED": {"CHECKPOINT_SUSPENDED"},
        }
        if data["status"] not in allowed_workflow_states.get(frontier, set()):
            raise ValueError("Workflow status is inconsistent with task frontier")

    def save_checkpoint(self, status: str | None = None, checkpoint_task: str | None = None):
        if status is not None:
            self.state["status"] = status
        # Only suspension carries a pointer. Approval/retry clear it explicitly.
        if checkpoint_task is not None:
            self.state["checkpoint_task"] = checkpoint_task
        self.state["updated_at"] = now()
        self.checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n",
                                             dir=self.checkpoint_path.parent,
                                             prefix="_tmp_workflow_", suffix=".json", delete=False) as handle:
                temporary = Path(handle.name)
                json.dump(self.state, handle, indent=2, ensure_ascii=False, allow_nan=False)
                handle.write("\n")
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, self.checkpoint_path)
        finally:
            if temporary is not None and temporary.exists():
                temporary.unlink()

    def approve_checkpoint(self, task_id: str):
        info = self.state["task_states"].get(task_id)
        if not info or info["status"] != "CHECKPOINT_SUSPENDED":
            raise ValueError(f"Task {task_id} is not suspended")
        info.update(status="READY", approved_at=now(), approval_plan_hash=self.digest,
                    approval_attempt=info["attempt"])
        info.pop("suspended_reason", None)
        self.state["checkpoint_task"] = None
        self.save_checkpoint(status="IN_PROGRESS")
        print(f"[APPROVED] {task_id}; command execution still requires resume")

    def retry_task(self, task_id: str):
        info = self.state["task_states"].get(task_id)
        if not info or info["status"] not in {"RUNNING", "FAILED"}:
            raise ValueError(f"Task {task_id} is not interrupted or failed")
        history = info.setdefault("attempt_history", [])
        history.append({key: info[key] for key in (
            "attempt", "status", "started_at", "completed_at", "exit_code", "error",
            "approved_at", "approval_plan_hash", "approval_attempt"
        ) if key in info})
        for key in ("started_at", "completed_at", "exit_code", "error", "approved_at", "approval_plan_hash",
                    "approval_attempt", "suspended_reason"):
            info.pop(key, None)
        info["attempt"] += 1
        info["status"] = "PENDING"
        info["retry_authorized_at"] = now()
        self.state["checkpoint_task"] = None
        self.save_checkpoint(status="IN_PROGRESS")
        print(f"[RETRY AUTHORIZED] {task_id}; reconcile side effects first; high-risk approval must be renewed")

    def execute_task(self, task: dict[str, Any]) -> bool:
        tid = task["id"]
        info = self.state["task_states"][tid]
        approved = (info.get("approval_plan_hash") == self.digest
                    and info.get("approval_attempt") == info["attempt"] and bool(info.get("approved_at")))
        if requires_approval(task) and not approved:
            info["status"] = "CHECKPOINT_SUSPENDED"
            info["suspended_reason"] = "Explicit approval required before command execution"
            self.save_checkpoint(status="CHECKPOINT_SUSPENDED", checkpoint_task=tid)
            print(f"[CHECKPOINT] {tid}: approval required")
            return False
        info.update(status="RUNNING", started_at=now())
        self.save_checkpoint(status="IN_PROGRESS")
        print(f"[RUNNING] {tid}: {task.get('name', tid)}")
        if self.dry_run:
            info.update(status="SIMULATED", completed_at=now())
            self.state["simulated_tasks"].append(tid)
            self.save_checkpoint()
            print(f"[SIMULATED] {tid}; no command executed")
            return True
        command = task["command"]  # Plan validation prevents missing-action success.
        try:
            result = subprocess.run(command, shell=isinstance(command, str), cwd=self.project_root,
                                    capture_output=True, text=True, encoding="utf-8", errors="replace")
            exit_code = result.returncode
            output = (result.stdout + "\n" + result.stderr).strip()
        except KeyboardInterrupt:
            self.save_checkpoint(status="RECOVERY_REQUIRED")
            raise
        except OSError as exc:
            exit_code, output = -1, str(exc)
        info.update(exit_code=exit_code, completed_at=now())
        if exit_code != 0:
            info.update(status="FAILED", error=output)
            self.save_checkpoint(status="FAILED")
            print(f"[FAILED] {tid}: exit {exit_code}\n{output}")
            return False
        info["status"] = "COMPLETED"
        self.state["completed_tasks"].append(tid)
        self.save_checkpoint()
        print(f"[OK] {tid}: command exit 0 (not acceptance)")
        return True

    def run(self) -> str:
        # A previously RUNNING command may already have committed side effects.
        # Never infer failure or rerun it just because the runner was interrupted.
        states = self.state["task_states"]
        if any(info["status"] == "RUNNING" for info in states.values()):
            self.save_checkpoint(status="RECOVERY_REQUIRED")
            print("[RECOVERY REQUIRED] Reconcile interrupted commands before an explicit --retry")
            return "RECOVERY_REQUIRED"
        if any(info["status"] == "FAILED" for info in states.values()):
            return "FAILED"
        for tid in self.execution_order:
            info = states[tid]
            if info["status"] == self.success_state:
                continue
            if info["status"] == "CHECKPOINT_SUSPENDED":
                return "CHECKPOINT_SUSPENDED"
            if not self.execute_task(self.task_map[tid]):
                return info["status"]
        self.save_checkpoint(status=self.success_state)
        print(f"[FINISHED] {self.plan['id']}: {self.success_state}; project gates remain separate")
        return self.success_state


def main() -> int:
    parser = argparse.ArgumentParser(description="Optional sequential DAG command runner (not project acceptance)")
    parser.add_argument("--plan", type=Path, help="Trusted plan (.py executes on load, or .json)")
    parser.add_argument("--checkpoint", type=Path, default=Path("workflow-checkpoint.json"))
    parser.add_argument("--resume-from", type=Path, help="Explicitly resume a schema-2 checkpoint")
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument("--approve", help="Record scoped approval only; does not execute")
    actions.add_argument("--retry", help="Authorize retry of failed/interrupted task after side-effect reconciliation")
    parser.add_argument("--dry-run", action="store_true", help="Simulate commands in a separate checkpoint; still writes checkpoint files")
    parser.add_argument("--project-root", type=Path, default=Path("."))
    args = parser.parse_args()
    checkpoint = (args.resume_from or args.checkpoint).resolve()
    resume = bool(args.resume_from or args.approve or args.retry)
    try:
        with checkpoint_lock(checkpoint):
            if resume:
                saved = read_checkpoint(checkpoint)
                plan = load_workflow_plan(args.plan) if args.plan else saved["plan"]
                # An approval/retry is a record-only operation, preserving the saved mode.
                dry_run = saved.get("dry_run") if (args.approve or args.retry) else args.dry_run
            else:
                if args.plan is None:
                    raise ValueError("--plan is required for a new run")
                plan, dry_run = load_workflow_plan(args.plan), args.dry_run
            engine = WorkflowOrchestrator(plan, checkpoint, args.project_root, dry_run=dry_run, resume=resume)
            if args.approve:
                engine.approve_checkpoint(args.approve)
                return 0
            if args.retry:
                engine.retry_task(args.retry)
                return 0
            status = engine.run()
            return 0 if status in {"COMPLETED", "SIMULATED", "CHECKPOINT_SUSPENDED"} else 1
    except KeyboardInterrupt:
        print("Interrupted; reconcile the last checkpoint before retrying", file=sys.stderr)
        return 130
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
