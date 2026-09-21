# Formal Task State Machine

> Purpose: defines the structure of `project-status.md`, legal task states, state transitions, evidence requirements, and parallel write rules. The Context Agent initializes the file; after initialization, the Commander is the sole status writer.

Machine validation uses `templates/task-state-spec.txt`; it must stay consistent with this file's phases, states, and transition table.

## Sole writer

- The sole writer of `project-status.md` is the Commander.
- The Context Agent creates the file from `templates/project-status.md` only when initializing a new project, and sets the project phase to `Planning` after delivering the background documents.
- Executor, Reviewer, QA, Risk Manager, Decision Manager, and Backup Manager never modify `project-status.md`; they only give evidence and suggested states in their delivery reports.
- When parallel tasks complete, the Commander reads the results one by one and updates the status file serially; multiple agents must never write at the same time.

## Project phases

| Phase | Meaning | Entry condition |
|---|---|---|
| Context Building | Confirming goals, scope, terms, and constraints | New project initialized |
| Planning | Context meets the breakdown bar; building tasks | Context Agent completed delivery |
| In Progress | At least one task is in a non-terminal state and dispatch has begun | First task entered In Progress |
| Acceptance | All required deliveries accepted; only project-level acceptance remains | All required delivery tasks are Completed; no required delivery task remains TODO, Blocked, In Progress, In Review, Needs Revision, QA Pending, or Awaiting Acceptance |
| Completed | Project-level acceptance passed | Final acceptance defined by the user or the project passed |
| Paused | The project as a whole is temporarily stopped | User explicitly paused, or a project-level blockage exists |

Check Acceptance readiness against the original required outcomes and confirmed scope changes, not just the rows already scheduled. Unscheduled required work also prevents entry. Deferring or cancelling a required outcome needs explicit user confirmation recorded in `decision-log.md`; a Cancelled task alone does not remove the requirement. Optional backlog may remain only when it is outside the confirmed required delivery scope. Project-level acceptance checks themselves may run in Acceptance; if they reveal more required delivery work, return to In Progress before dispatching that work. The CLI checks phase names, not this evidence-based readiness judgment.

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

A task id, once used, must never be reassigned to another task. Revision rounds use `<task id>-R1`, `<task id>-R2`, belonging to the original task; never create a new top-level id solely for a same-scope correction. Record rounds in receipts/history, not as duplicate task rows. A new objective or independent experiment may be a linked top-level task.

## Task states

| State | Meaning | Entry evidence |
|---|---|---|
| TODO | The brief is complete and dependencies are satisfied, but not yet dispatched | Full task prompt and output directory |
| In Progress | The Executor or another primary agent has picked up the task | User or host confirmation of dispatch/pickup; emitting a copyable prompt alone leaves TODO |
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
2. Before writing, validate the proposed transition against the current file: `<python> scripts/validate-project-state.py --path <status path> --task-id <task id> --from-state "<current state>" --to-state "<target state>"`. Both states and a nonblank task ID are required; the source must match that task's recorded current state.
3. Check that the required evidence files really exist, and read their key conclusions.
4. Update the current status, time, and next actions in the task list.
5. Append one row to the status history: old state, new state, basis, and operator.
6. Sync the current blockage, current focus, and project phase. Add a blocked record on entry; remove it on recovery/cancellation, retaining its reason and pre-block state in history. Change the task and active blocked table together before validation.
7. Run structural validation with `--path` only on the updated file, then re-read it as UTF-8 and confirm the tables, states, and evidence paths. Do not replay the old `--from-state` transition check after the state has already changed.

If any step fails, keep the original state and record it as an issue to handle; never write the target state first and add evidence later.

## Review and QA gates

Use `references/16-quality-gates.md` for risk-based selection, evidence reuse/invalidation, finding severity, revision budgets and exploration acceptance. The state machine is unchanged by a batch, continuation, or experiment: waived gates still pass through Awaiting Acceptance; a negative experiment result may satisfy its stated question but is not implementation success.

- Reviewer requirements are decided by risk, impact scope, compliance requirements, or the task brief.
- QA requirements are decided by runnability, recomputability, data truthfulness, or user acceptance requirements.
- When a required Reviewer or QA gate fails, the task enters `Needs Revision`; record the required remediation and start a revision round when corrective work is dispatched. For a combined cold-start/informed gate, initial reports are provisional until reconciliation under `references/17-cold-start-review.md` (Gate conclusion and revision timing); they are not actionable gate failures by themselves. Pause unsafe operations immediately without waiting for reconciliation. Evidence-only reassessment does not consume an implementation correction round.
- A conditional pass may proceed only when every condition has been turned into an explicit revision item or a remaining risk, and the Commander judges it does not block acceptance.

## Blocking and recovery

Entering `Blocked` must record:

- Pre-block state
- Block reason
- Owner
- Relief condition
- Next check condition or date

Each currently Blocked task must have exactly one active blocked record. The record must reference an existing Blocked task, and its pre-block state must be a declared non-Blocked state with a legal transition into Blocked. In the default graph, Completed, Cancelled, Blocked and unknown values cannot be pre-block states. Duplicate, orphan, stale or missing records fail structural validation; repair them from actual history/evidence rather than guessing or deleting inconvenient evidence.

After the blockage is relieved, the task may return only to its recorded legal pre-block state and continue with normal transitions; recovery must never skip review or QA. Validate against the still-blocked file with `<python> scripts/validate-project-state.py --path <path/to/project-status.md> --task-id <task id> --from-state Blocked --to-state "<pre-block state>"`. Cancellation remains an explicit legal alternative, with the same task-ID and structural consistency requirements, not a recovery to the pre-block state.

## Parallel tasks

A task may be marked parallel-safe only when all hold:

- All prerequisites are satisfied.
- Output directories do not overlap.
- No shared deliverable files are modified.
- One task's output does not change another task's input.
- No executing agent writes `project-status.md`.

- Shared source files, data stores, browser sessions, ports and other resources are also checked for conflicts; use isolated snapshots/workspaces and an integration owner when needed.
- A required backup is a prerequisite and must have verified evidence before the dependent mutation is dispatched as ready. A snapshot may be reused only while its coverage/version remains adequate.

Parallelism only changes dispatch order; it never changes a single task's state machine. Use the ready-batch policy in `references/15-collaboration.md` rather than limiting each reply to a single prompt.

## Optional coordination metadata

The optional Coordination, Active windows, Pending user actions, Backups, and Synchronization sections in `templates/project-status.md` track context revisions, task/window mappings, input versions, ownership and acknowledgment. They do not add states or alter the required task/history columns. Existing projects may add them incrementally.

Commander checks these optional fields manually; `scripts/validate-project-state.py` validates structure/state names, active blocked-record consistency and task-bound requested transitions, not evidence truth, project-phase readiness, backup restorability, read/write conflicts, acknowledgment, Reviewer/QA evidence or permission enforcement, or full history consistency. A successful CLI result does not replace those checks.