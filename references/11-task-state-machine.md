# Formal Task State Machine

> Purpose: defines the structure of `project-status.md`, legal task states, state transitions, evidence requirements, and parallel write rules. The Context Agent initializes the file; after initialization, the Commander is the sole status writer.

Machine validation uses `templates/task-state-spec.txt`; it must stay consistent with this file's phases, states, and transition table.

## Sole writer

- The sole writer of `project-status.md` is the Commander.
- The Context Agent creates the file from `templates/project-status.md` only when initializing a new project, and sets the project phase to `Planning` after delivering the background documents.
- Executor, Reviewer, QA, Risk Manager, and Decision Manager never modify `project-status.md`; they only give evidence and suggested states in their delivery reports.
- When parallel tasks complete, the Commander reads the results one by one and updates the status file serially; multiple agents must never write at the same time.

## Project phases

| Phase | Meaning | Entry condition |
|---|---|---|
| Context Building | Confirming goals, scope, terms, and constraints | New project initialized |
| Planning | Context meets the breakdown bar; building tasks | Context Agent completed delivery |
| In Progress | At least one task is in a non-terminal state and dispatch has begun | First task entered In Progress |
| Acceptance | All required deliverables done; project-level acceptance in progress | No In Progress, In Review, Needs Revision, or QA Pending tasks |
| Completed | Project-level acceptance passed | Final acceptance defined by the user or the project passed |
| Paused | The project as a whole is temporarily stopped | User explicitly paused, or a project-level blockage exists |

When a project resumes from `Paused`, the pre-pause phase must be recorded and restored. `Completed` is terminal; new requirements create new tasks or new phases, never erase history.

## Required task fields

Every task in `project-status.md` must record:

- Task id and name
- Current status
- Priority
- Primary agent
- Prerequisites
- Parallel-safe or not
- Reviewer required or not
- QA required or not
- Output directory
- Last updated time

A task id, once used, must never be reassigned to another task. Revision rounds use `<task id>-R1`, `<task id>-R2`, belonging to the original task; never create a new top-level id.

## Task states

| State | Meaning | Entry evidence |
|---|---|---|
| TODO | The brief is complete and dependencies are satisfied, but not yet dispatched | Full task prompt and output directory |
| In Progress | The Executor or another primary agent has picked up the task | Dispatched task prompt |
| In Review | The delivery exists, waiting for or undergoing Reviewer review | Delivery file paths and self-check results |
| Needs Revision | Reviewer, QA, or Commander found issues that must be fixed | Concrete issue list with evidence locations |
| QA Pending | The delivery or revision passed the required review; waiting for or undergoing QA | Review conclusion or exemption basis |
| Awaiting Acceptance | Both required Reviewer and QA gates passed; waiting for Commander's light acceptance | Review and QA reports, or an explicit exemption basis |
| Completed | All acceptance criteria satisfied | Commander's acceptance conclusion and delivery path |
| Blocked | The current state cannot proceed | Block reason, owner, relief condition, pre-block state |
| Cancelled | Explicitly cancelled by the user, or confirmed abandoned after a direction change | Cancellation decision and its record location |

## Legal transitions

| Current state | May enter |
|---|---|
| TODO | In Progress, Blocked, Cancelled |
| In Progress | In Review, QA Pending, Awaiting Acceptance, Needs Revision, Blocked, Cancelled |
| In Review | Needs Revision, QA Pending, Awaiting Acceptance, Blocked, Cancelled |
| Needs Revision | In Progress, Blocked, Cancelled |
| QA Pending | Needs Revision, Awaiting Acceptance, Blocked, Cancelled |
| Awaiting Acceptance | Completed, Needs Revision, Blocked, Cancelled |
| Blocked | <blocked-before>, Cancelled |
| Completed | None |
| Cancelled | None |

A gate may be skipped only when the task brief explicitly states that Reviewer or QA is not required. Never go directly from `In Progress` to `Completed`.

## Status update transaction

Every Commander status update must complete in order:

1. Read the latest `project-status.md` and confirm the current state was not changed by another update.
2. Check whether the target state is in the legal transition table.
3. Check that the required evidence files really exist, and read their key conclusions.
4. Update the current status, time, and next actions in the task list.
5. Append one row to the status history: old state, new state, basis, and operator.
6. Sync the current blockage, current focus, and project phase.
7. Re-read the file as UTF-8 and confirm the tables, states, and evidence paths are consistent.

If any step fails, keep the original state and record it as an issue to handle; never write the target state first and add evidence later.

## Review and QA gates

- Reviewer requirements are decided by risk, impact scope, compliance requirements, or the task brief.
- QA requirements are decided by runnability, recomputability, data truthfulness, or user acceptance requirements.
- When the Reviewer fails the delivery or QA fails, the task enters `Needs Revision` and a new revision round is created.
- A conditional pass may proceed only when every condition has been turned into an explicit revision item or a remaining risk, and the Commander judges it does not block acceptance.

## Blocking and recovery

Entering `Blocked` must record:

- Pre-block state
- Block reason
- Owner
- Relief condition
- Next check condition or date

After the blockage is relieved, the task may return only to the recorded pre-block state and continue with normal transitions; recovery must never skip review or QA.
To validate a recovery transition, run `<python> scripts/validate-project-state.py --path <path/to/project-status.md> --from-state Blocked --to-state <pre-block state> --task-id <task id>`; the script enforces validation against the current blocked table.

## Parallel tasks

A task may be marked parallel-safe only when all hold:

- All prerequisites are satisfied.
- Output directories do not overlap.
- No shared deliverable files are modified.
- One task's output does not change another task's input.
- No executing agent writes `project-status.md`.

Parallelism only changes dispatch order; it never changes a single task's state machine.