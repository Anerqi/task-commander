# 18 - Dynamic Workflow Orchestration & Checkpoint Spec

> Dynamic Workflow Orchestration transforms static coordination prompts into executable, code-driven multi-agent pipelines with explicit DAG dependencies, human-in-the-loop checkpoints, and fast checkpoint-resume capabilities.

## 1. Core Principles

1. **Code-as-Orchestrator**: Workflows are declared as inspectable code or structured DAG definitions rather than ambiguous conversational multi-turn text.
2. **Risk-Aware Checkpoints**: High-risk tasks (e.g. database schema mutations, security boundaries, mass deletions) automatically trigger safe interruption (`CHECKPOINT_SUSPENDED`), requiring explicit human sign-off before proceeding.
3. **Resilient Resumption**: Every execution emits an atomic state checkpoint file (`workflow-checkpoint.json`). Interrupted or failed workflows can resume from the exact checkpoint without re-running completed idempotent tasks.
4. **State Machine Alignment**: Dynamic workflows remain strictly synchronized with `templates/task-state-spec.txt` and `templates/project-status.md`. An automated task run produces valid task receipts and updates project status.
5. **Observability First**: Any running or completed workflow must be renderable into both terminal boards (ASCII/ANSI) and visual DAG diagrams (Mermaid).

---

## 2. Workflow Stage & Lifecycle

A Dynamic Workflow is divided into sequential or pipelined **Phases / Stages**:

```
[Phase 1: Discovery & Context] -> [Phase 2: Core Execution (Parallel)] -> [Phase 3: Review & QA] -> [Phase 4: Acceptance]
                                                  |
                                            (@checkpoint) -> [Human Approval]
```

### Task Types in Workflow:
- `EXECUTE`: Standard implementation by Executor Agent.
- `REVIEW`: Non-modifying inspection by Reviewer Agent.
- `QA`: Independent test/verification by QA Agent.
- `GATE`: Decision checkpoint or human confirmation barrier.
- `BACKUP`: Snapshot creation before mutating operations.

### Task Status within Workflow Execution:
- `PENDING`: Awaiting upstream dependencies.
- `READY`: All upstream dependencies satisfied; queued for dispatch.
- `RUNNING`: Dispatched and active in execution slot.
- `CHECKPOINT_SUSPENDED`: Paused at a gate/checkpoint for human sign-off.
- `COMPLETED`: Finished and verified; outputs ready for downstream tasks.
- `FAILED`: Execution or verification failed.
- `SKIPPED`: Safely bypassed due to conditional branch or upstream bypass.

---

## 3. Workflow Definition Contract

A workflow plan (`workflow-plan.py` or JSON configuration) declares:

```python
workflow = {
    "id": "wf-feature-x",
    "name": "Feature Implementation Workflow",
    "version": "1.0",
    "max_concurrency": 3,
    "tasks": [
        {
            "id": "TASK-01",
            "name": "Database Schema Migration",
            "type": "EXECUTE",
            "agent": "Executor",
            "risk_level": "HIGH",           # LOW | MEDIUM | HIGH | CRITICAL
            "requires_checkpoint": True,     # True suspends workflow before or after execution
            "depends_on": [],
            "action": "scripts/tasks/migrate_db.py",
            "output_dir": "task-output/TASK-01"
        },
        {
            "id": "TASK-02",
            "name": "API Service Implementation",
            "type": "EXECUTE",
            "agent": "Executor",
            "risk_level": "LOW",
            "requires_checkpoint": False,
            "depends_on": ["TASK-01"],
            "output_dir": "task-output/TASK-02"
        }
    ]
}
```

---

## 4. Checkpoint State Schema

Execution progress is persisted to `workflow-checkpoint.json` at:
- Every task state transition.
- Explicit checkpoint pauses.
- Graceful shutdown or failure.

```json
{
  "workflow_id": "wf-feature-x",
  "started_at": "2026-10-01T12:00:00Z",
  "updated_at": "2026-10-01T12:05:30Z",
  "status": "SUSPENDED_AT_CHECKPOINT",
  "checkpoint_task": "TASK-01",
  "completed_tasks": ["TASK-PREP"],
  "task_states": {
    "TASK-01": {
      "status": "CHECKPOINT_SUSPENDED",
      "risk_level": "HIGH",
      "reason": "Database migration requires human review of rollback script",
      "artifacts": ["task-output/TASK-01/migration.sql"]
    }
  },
  "context_snapshot": {
    "active_branch": "feature/db-upgrade",
    "git_head": "a1b2c3d"
  }
}
```

---

## 5. Resumption Contract

When calling the orchestrator with `--resume-from <checkpoint_file>`:
1. Validate checkpoint integrity against project files.
2. Load all `COMPLETED` tasks and skip re-execution.
3. If paused at `CHECKPOINT_SUSPENDED`, check whether the user provided `--approve <task_id>` or signed off in `project-status.md`.
4. Re-calculate the DAG ready queue and resume concurrent execution.

---

## 6. Rendering & Monitoring Contract

Every workflow execution can be piped or exported via `scripts/render-workflow.py`:
- `--format text`: Formatted ASCII table with status indicators (`[OK]`, `[RUNNING]`, `[PAUSED]`, `[WAITING]`).
- `--format mermaid`: Visual flowchart suitable for GitHub, cc-haha, or Markdown documents.
- `--format json`: Machine-readable summary for host integration (such as desktop GUI).
