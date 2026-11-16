# 23 - Protocol Version and Upgrade

> Read when opening an existing project after a Task Commander update, when a status file predates the current protocol, or when deciding whether an old project needs migration. This is a pull model: nothing updates an existing project automatically.

**Current protocol version: 3 (2026-11-16).**

## What changed in version 3

Version 3 preserves the roles, task states, transitions and table columns. New templates place `### Needs you now` under `## Coordination`.

- **Attention compatibility:** legacy `## Needs you now` and files without an attention section remain supported. When present, the view still has three columns and at most five rows. Section bodies end at the next ATX heading of any level; fenced-code headings and tables are ignored by the shared parser.
- **Completed-task readability:** count only task rows whose status is `Completed` (case-insensitive). More than 10 produces an advisory archive/readability warning, not a validation failure. `Cancelled` and other states do not count. Archival must preserve task history and evidence pointers; a warning does not authorize deleting records or rewriting terminal states.
- **Shared limits:** `scripts/validation_limits.py` owns `NEEDS_YOU_MAX_ROWS=5`, `COMPLETED_TASK_WARNING_LIMIT=10`, `MAX_FILE_BYTES=2*1024*1024`, `ENTRY_LINE_LIMIT=20` and `SUMMARY_LENGTH_LIMIT=200`. These shared bounds support validation; they do not certify evidence, decisions or permissions.
- **Source ownership:** `grill-with-docs` supplies METHOD only. Task Commander owns output paths and integration rules; `CONTEXT.md` holds only terms/domain relations, `decision-log.md` is the sole decision ledger, and optional `knowledge/ROADMAP.md` holds long-term direction rather than live task state.

Version 2 capabilities and history remain below.

## What changed in version 2

Version 2 keeps the task state machine, status-table columns, role boundaries and CLI contracts. It adds optional capabilities:

- **Knowledge layer** (`references/20-knowledge-layer.md`): durable LOG, topic notes, audit, branch/experiment closure and graduation candidates.
- **Window boundaries** (`references/21-window-boundaries.md`): an explicit continue/fresh/handoff/subagent/compact decision.
- **Task shaping** (`references/06-task-template.md`): tracer-bullet vertical slices, blocking edges and wide-refactor sequencing.
- **Two-axis review** (`references/04-reviewer.md`, `references/05-qa.md`, `references/16-quality-gates.md`): separate Spec and Standards/behavior findings.
- **Debug feedback loop** (`references/07-verification-guidelines.md`): build a red-capable loop before hypothesizing for hard bugs and performance regressions.
- **Project retro** (`references/22-project-retro.md`): improve the environment after completion or a major incident.
- **`Protocol version` metadata** in `project-status.md` (the machine-readable field name is `protocol_version`): optional and backward-compatible.

None of these adds a role, task state or required column. A version-1 project remains readable and valid.

## Compatibility

- Existing `project-status.md` files may omit the `Protocol version` line or the optional coordination sections. The validator does not require them.
- Version 3 does not require an attention section in legacy files; a top-level `## Needs you now` remains valid alongside the new nested convention.
- The knowledge layer is optional and may be absent. Do not create empty topic shells merely to claim adoption.
- Existing task IDs, phases, revisions, receipts and history are preserved across adoption.
- New defaults do not silently widen an active task's permissions or gates. Change active contracts explicitly.
- The command runner and its checkpoint schema are unchanged.

## Upgrade an existing project

1. Read the current `project-status.md`, background, `decision-log.md`, root `AGENTS.md` and any existing knowledge records. Do not reconstruct from chat memory.
2. On the next Commander status write, add `- Protocol version: 3` to the Project section. This is metadata, not a task transition; preserve the status history. Use the nested attention placement for new templates; an existing top-level or absent section need not be migrated.
3. Create `knowledge/LOG.md` only under the trigger in `references/20-knowledge-layer.md`: a new multi-session project may initialize it at setup; an existing project creates it on the first durable conclusion and after user confirmation. If the layer exists or is created under that trigger, add one entry for the adoption; otherwise record the adoption in a receipt or status note. Do not pre-create topics, `Cited.md` or `Reference/`.
4. Apply current defaults, including v2 task shaping and two-axis gates, to **newly dispatched tasks**. An active older task keeps its saved scope, permissions, shape, gates and revision history; if a change is genuinely useful, propose a versioned brief/gate update and obtain user confirmation before altering it. Do not silently redefine active work.
5. At the next relevant dispatch or closeout, bind the new references that apply: knowledge layer for durable conclusions, window boundaries for handoff decisions, task shaping for new decomposition, two-axis review for new gates.
6. When proposing `AGENTS.md` knowledge-navigation rules, show the exact diff and obtain user confirmation. Do not overwrite existing project rules.
7. Record the upgrade and any declined items in `knowledge/LOG.md` (or, before the layer exists, a short note in the next receipt/status update).

## Detect drift

A project is drifted from the current protocol when any of these is true and matters to current work:

- `project-status.md` has no `Protocol version` line, or a version below 3;
- a multi-session project has durable conclusions only in chat or long receipts and no knowledge layer;
- a task was decomposed into layer-only or per-file microtasks without a vertical outcome;
- review and QA do not distinguish Spec compliance from Standards/behavior;
- a hard bug was investigated without a red-capable feedback loop;
- a completed project has no closeout/audit despite reusable lessons.

Missing optional features are not defects by themselves. Drift matters only when it creates a current risk or blocks the next phase.

The upgrade is complete when the status shows `Protocol version: 3`, the adoption or declined items are recorded, and no empty knowledge files were created. Existing task IDs, phases, history, active contracts and accepted evidence remain intact. Neither a legacy attention placement nor an advisory Completed warning blocks adoption.

## Changelog

### 2026-11-16 — protocol version 3

- **Affects**: current template metadata and nested attention placement, shared Markdown section parsing and validation limits, Completed-task readability warnings, and explicit source ownership.
- **Detect**: version absent or below 3 identifies an unreconciled project; legacy or missing attention remains valid. More than 10 `Completed` rows (case-insensitive) triggers only an advisory warning.
- **Fix**: record version 3 at the next Commander write; use nested attention for new templates, retain legacy compatibility, and consider archival with history/evidence pointers preserved. Reconcile source ownership using the authoritative project records.
- **Safety**: `auto` for version metadata only; `confirm` for changes to active contracts, project rules, `AGENTS.md` or external writes. Preserve original scope, user-confirmation protections and all task histories. This adds no roles, states or gate waivers.

### 2026-10-24 — protocol version 2

- **Affects**: `project-status.md` metadata, optional knowledge layer, root `AGENTS.md` navigation, task templates, Reviewer/QA references and existing project adoption.
- **Detect**: `Protocol version` (machine-readable `protocol_version`) absent or below 2; a multi-session project with durable conclusions only in chat/receipts; layer-only task decomposition; Reviewer/QA findings not separated by Spec and Standards/behavior; hard-bug work without a reproduction loop.
- **Fix**: add `Protocol version: 2` on the next Commander write; create `knowledge/LOG.md` only under the knowledge-layer trigger; bind the applicable new references to new tasks; propose (do not silently apply) `AGENTS.md` navigation updates. Active tasks keep their saved contracts unless the user confirms a versioned change. No task-schema migration.
- **Safety**: `auto` for the version metadata only; `confirm` for knowledge-layer creation, `AGENTS.md`, project rules, external knowledge writes or any change that alters an active task's scope or permission.

## Maintaining this file

Every protocol change that affects existing instances must add an entry here and bump the version and date. Skill-internal wording, routing or new optional references that leave existing instances valid do not require an entry. A missed entry means drift is never detected; that discipline is the single point of failure of this mechanism.

Each entry should state: **Affects**, **Detect**, **Fix**, and **Safety** (`auto` for mechanical metadata, `confirm` for meaning, project rules or external writes).
