# 18 - Optional DAG Command Runner and Checkpoints

> Read only when planning to run `scripts/run-workflow.py`, resume its checkpoint, or render command progress. This is an optional sequential command runner, not an agent runtime or a replacement for Commander, receipts, review or QA.

## Capability boundary

The runner executes explicitly authorized local commands in DAG order, one at a time, with pre-command approval barriers and atomic JSON checkpoints. The CLI takes a single-writer lock for its checkpoint. Plans requesting `max_concurrency` other than 1 are rejected: parallel execution is not implemented. Protocol-level ready batches remain available through `references/15-collaboration.md`.

A task type or agent label is metadata only: `REVIEW`, `QA`, `GATE`, `BACKUP` and `EXECUTE` do not dispatch a model, validate role independence, certify backups or collect human judgment. Every node needs an actual command, including in dry-run; a missing command is an error, not simulated success. Use the normal role windows for judgments and approvals that cannot be represented by an authorized command.

`COMPLETED` in a runner checkpoint means only command exit code 0. It is not the project's `Completed` state, a verified deliverable, a gate Pass or acceptance. The runner never writes `project-status.md`, automatically generates protocol task receipts, or implements the project state machine. Commander reads command evidence, checks artifacts, collects required Reviewer/QA reports and integrates real status transitions through `references/11-task-state-machine.md`. Rendered command progress must retain this distinction.

## Plan and authorization

Use `templates/workflow-plan.template.py` as an executable example; its commands only print examples. A trusted Python plan defines `WORKFLOW`; a JSON plan holds the same object. Required fields:

- Workflow `id`, nonempty `tasks`, and optional `max_concurrency` fixed at 1.
- Each task: unique nonblank `id`, a nonempty `command` (argv list preferred, or trusted shell string), optional `depends_on` IDs without duplicates/cycles.
- Optional `risk_level`: `LOW`, `MEDIUM`, `HIGH`, or `CRITICAL`; optional boolean `requires_checkpoint`; name, agent, type and output metadata.

`HIGH` and `CRITICAL` automatically suspend before their command even when `requires_checkpoint` is false. That flag also adds a pre-command barrier for lower-risk tasks. Setting status to READY alone is not approval. `--approve <task-id>` records a timestamp, the current plan hash and the current attempt number; it does not execute or resume the command. Approval is an operator action subject to project authority, not authentication or a substitute for verified recovery prerequisites. There is no automatic approval from text in `project-status.md`.

Python plans execute code when loaded, including during dry-run; shell strings execute with the host shell. Load only trusted, inspected plans under effective authorization. Prefer JSON plus argv lists for portable commands and fewer shell ambiguities. Do not ingest downloaded/agent-generated plans as authorized execution. The runner is not a sandbox or permission enforcer. Review command read/write scope, data transfer, backups and destructive effects before launch. Avoid putting secrets in plans: the entire plan is persisted in the local checkpoint; keep it in approved storage and out of public commits.

## Checkpoint and recovery contract

A new run requires a new checkpoint path. An existing checkpoint is never silently reused or overwritten by a new run. `--resume-from` explicitly loads schema version 2; malformed, old-schema, changed-plan, wrong-project-root and inconsistent task checkpoints fail without reinitialization. Preserve old evidence and reconcile legacy checkpoints manually against actual artifacts; this is not a schema migration that invents completed work.

The checkpoint embeds the complete executable plan, its SHA-256 hash, resolved project root, real/simulation mode, task progress, result lists, attempt history and scoped approvals. Validation requires a successful prefix, at most one active sequential frontier, and pending remaining tasks; workflow-level stops must match that frontier. Unstarted nodes retain no current-attempt result evidence, and prior-attempt approval cannot authorize a retry. Contradictory records fail before approval, retry writes or command execution. Resume can use this saved plan, or `--plan` can supply an identical plan for comparison. The hash identifies the plan object, not external scripts, dirty source files, artifacts, dependencies or environment. Before resuming, Commander/operator must verify those inputs and existing command evidence are still valid. Changed source/environment requires explicit reconciliation/new plan, not assuming the hash certifies freshness. A hash detects mismatch; it is not a signature against malicious edits.

Each task boundary is written to a same-directory temporary file, flushed and fsynced, then replaced with `os.replace`. Failed saves preserve the previous valid checkpoint and report failure; owned temporary files are cleaned up. This avoids truncating the previous JSON, not every possible power-loss failure. The CLI holds `<checkpoint>.lock` for the invocation. If an abnormal process exit leaves a lock, verify the owner is no longer running and reconcile its side effects before removing that stale lock; the CLI never auto-deletes an existing lock. Different checkpoint paths do not isolate shared assets, so prohibit overlapping runs or use genuinely isolated workspaces.

Resume skips only previously recorded successful commands in the same execution mode. It does not promise exactly-once external side effects. An interrupted `RUNNING` task is uncertain: it may have changed data before the result was saved. Resume reports `RECOVERY_REQUIRED` and executes nothing. A recorded `FAILED` task also blocks automatic execution/retry. Inspect artifacts/logs or ask the operator to establish what happened and whether retry is safe. Only then use `--retry <task-id>` as an explicit retry authorization; it preserves attempt evidence, resets that node to PENDING, and clears any earlier approval. High-risk retries must pass a fresh approval barrier. There is no force-complete command or automatic replay. If a command already succeeded but replay is unsafe, reconcile outside this runner under the normal protocol instead of guessing its result.

## Dry-run is not delivery

Dry-run follows ordering/barriers and writes a checkpoint but never invokes task commands. Its terminal state and task results are `SIMULATED`, with `simulated_tasks` separate from `completed_tasks`; no success exit code is fabricated. A simulation checkpoint cannot resume as a real run, or vice versa. Approval/retry record-only operations retain the checkpoint's mode. Use a fresh path to switch from preview to execution. The Python plan import caveat above still applies; dry-run is not a no-file-write sandbox.

## CLI sequence

Run from the verified project root; substitute the verified Python interpreter for `<python>`:

```text
# Preview writes a simulation-only checkpoint and may pause at a high-risk node.
<python> <skill-root>/scripts/run-workflow.py --plan <plan.json> --checkpoint <preview.json> --project-root <project-root> --dry-run
<python> <skill-root>/scripts/run-workflow.py --checkpoint <preview.json> --project-root <project-root> --approve <task-id>
<python> <skill-root>/scripts/run-workflow.py --resume-from <preview.json> --project-root <project-root> --dry-run

# Real execution uses its own checkpoint and effective authorization.
<python> <skill-root>/scripts/run-workflow.py --plan <plan.json> --checkpoint <run.json> --project-root <project-root>
<python> <skill-root>/scripts/run-workflow.py --checkpoint <run.json> --project-root <project-root> --approve <task-id>
<python> <skill-root>/scripts/run-workflow.py --resume-from <run.json> --project-root <project-root>

# Only after reconciling partial effects; this records retry authorization, not execution.
<python> <skill-root>/scripts/run-workflow.py --checkpoint <run.json> --project-root <project-root> --retry <task-id>
<python> <skill-root>/scripts/run-workflow.py --resume-from <run.json> --project-root <project-root>
```

CLI exit 0 can mean commands completed, simulation completed, approval recorded, or suspended awaiting approval; inspect the checkpoint and output, not the exit code alone. Failure and uncertain recovery return nonzero. Required human approval is not completion.

## Rendering and evidence

`scripts/render-workflow.py` renders a checkpoint or `project-status.md` with `--format text`, `mermaid`, or `json`. Checkpoint dashboards show command progress, simulation and pending approval, not an accepted project. Markdown status dashboards display Commander's recorded project task states without changing them. `templates/workflow-checkpoint.json` is a render-only illustrative example, not a resumable execution record.

Store actual command logs/artifact pointers and the reviewed task/input identity in the assigned task result/receipt per `templates/task-receipt.md`. The runner checkpoint records exit codes and failure output; it is not a complete success log or evidence manifest. Keep the normal gates, cold-start isolation and read/write ownership rules in force. Unit tests use synthetic disposable fixtures; they do not certify real migrations, model dispatch or live cross-host integration.
