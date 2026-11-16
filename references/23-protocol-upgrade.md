# 23 - Protocol Version and Upgrade

> Read when opening an existing project after a Task Commander update, when a status file predates the current protocol, or when deciding whether an old project needs migration. This is a pull model: nothing updates an existing project automatically.

**Current protocol version: 3 (2026-11-16).**

## What changed in version 3

Version 3 preserves the task state machine, task-table columns, role boundaries and CLI transition contract. It reduces persistent coordination overhead:

- **Context consolidation:** the selected skill inventory lives in the `Available skills` subsection of `background/01_project_background.md`. Existing `background/02_skill_list.md` files remain readable migration inputs; new projects do not create them.
- **Conditional terminology glossary:** `CONTEXT.md` is created or maintained only when the project already uses grill-with-docs as its persistent glossary, or the user explicitly asks for one. Loading that method for a Context session alone is not a trigger.
- **On-demand knowledge:** a multi-session expectation alone does not create `knowledge/LOG.md`. Create the layer on the first durable conclusion or when the user explicitly requests a persistent timeline. `ROADMAP.md` is only for goals that extend beyond the current session.
- **Compact decisions:** new confirmed decision entries are append-only and normally 3–5 substantive lines. Full option analysis stays in its separate artifact; prior decisions and evidence are not rewritten.
- **Lean status attention view:** Blocked and Pending user actions may appear as nested subsections under `## Needs you now`. Legacy top-level `## Blocked` and `## Pending user actions` remain readable.
- **On-demand coordination sections:** Coordination, Knowledge, Active windows, Backups and Synchronization sections are added only when they carry current information.
- **Phase closeout:** `references/21-window-boundaries.md` defines a closeout checklist that preserves task IDs, evidence and confirmed decisions while reducing stale coordination material.
- **Non-blocking accumulation warning:** `validate-project-state.py` warns when more than 10 tasks are Completed. Warnings do not change validity or the exit code.
- **Central validation limits:** `scripts/validation_limits.py` owns `NEEDS_YOU_MAX_ROWS=5`, `COMPLETED_TASK_WARNING_THRESHOLD=10`, `KNOWLEDGE_FILE_MAX_BYTES=2*1024*1024`, `KNOWLEDGE_LOG_ENTRY_LINE_LIMIT=20` and `KNOWLEDGE_TOPIC_SUMMARY_LENGTH_LIMIT=200`. These shared bounds do not certify evidence, decisions or permissions.
- **Source ownership:** `grill-with-docs` supplies METHOD only. Task Commander owns output paths and integration rules; an existing `CONTEXT.md` holds only terms/domain relations, `decision-log.md` is the sole decision ledger, and optional `knowledge/ROADMAP.md` holds long-term direction rather than live task state.
- **Shared section parsing:** direct bodies end at the next ATX heading of any level; fenced-code headings and tables are ignored. Only level-two task sections are authoritative. Level-three Blocked/Pending records are live only under root Needs you now; legacy level-two records remain valid.
- **Completed-task readability:** count only task rows whose status is Completed (case-insensitive). More than 10 produces an advisory archive/readability warning, not a validation failure. Cancelled and other states do not count. Preserve history and evidence pointers when archiving.

None of these adds a role, task state or required task-table column.

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

- Existing `project-status.md` files may omit the `Protocol version` line or optional coordination sections; protocol metadata remains backward-compatible.
- New templates use root `## Needs you now` with `### Blocked` and on-demand `### Pending user actions`. Prior interim main v3 `### Needs you now` under `## Coordination` with top-level Blocked/Pending is a compatible input, not the canonical v3 output. Legacy `## Needs you now` and files without an attention section remain supported.
- Version 1 and 2 status files remain valid. The validator and renderer recognize both nested `### Blocked` and legacy top-level `## Blocked` sections.
- Legacy top-level `## Pending user actions` remains readable. New records place it under `## Needs you now` when it is needed.
- Existing `background/02_skill_list.md` files are read as migration inputs. Do not delete or rewrite them automatically; new projects put the current inventory in `background/01_project_background.md`.
- Existing `CONTEXT.md` files remain authoritative when the project already maintains them. Do not create one merely because grill-with-docs is loaded for the current session.
- The knowledge layer remains optional. Existing LOGs, topics, roadmaps, citations and history are preserved; no empty files or directories are created.
- Existing task IDs, phases, revisions, receipts, status history and accepted evidence are preserved. No task-schema migration is required.
- New defaults do not silently widen an active task's permissions or gates. Change active contracts explicitly.

## Upgrade an existing project

1. Read the current status, background, decision log, root AGENTS.md and relevant knowledge records. Read legacy skill inventories and CONTEXT.md only when they exist.
2. Wait for the next genuine phase boundary and explicit user confirmation before adopting Version 3. Do not mass-migrate during routine execution.
3. On the first status write after confirmation, add or update `- Protocol version: 3` in the Project section. This is metadata, not a task transition; preserve task IDs, task states and history.
4. When the project background is next updated, merge still-relevant entries from an existing `background/02_skill_list.md` into the `Available skills` subsection of `background/01_project_background.md`. Leave the legacy file intact unless cleanup is separately approved.
5. Preserve an existing CONTEXT.md. If it is absent, create it only when the project already uses grill-with-docs as a persistent glossary or the user explicitly requests it.
6. Do not create a knowledge LOG merely for multi-session work. Apply the creation trigger in `references/20-knowledge-layer.md`; create ROADMAP only for goals that continue beyond this session.
7. Use the nested Needs you now layout for new or deliberately revised status files. The validator continues to read legacy top-level Blocked and Pending user actions sections.
8. Apply compact append-only decision entries to new decisions only. Do not rewrite existing confirmed decisions or analysis records.
9. Add optional coordination sections only when they carry current information. Preserve all active task contracts; obtain user confirmation before altering them with a versioned change.
10. When proposing `AGENTS.md` knowledge-navigation or rule changes, show the exact diff and obtain user confirmation before writing.

## Detect drift

A project may need Version 3 adoption when:

- the skill inventory is maintained only in a new or repeatedly regenerated `background/02_skill_list.md` file;
- CONTEXT.md is being created solely because grill-with-docs was loaded for a one-time session;
- empty knowledge files or a LOG entry for every routine task transition are accumulating;
- AGENTS.md contains volatile task counts, milestone counters or temporary progress notes;
- decision-log entries duplicate full option analysis or prior confirmed decisions are being rewritten;
- the status file carries empty optional coordination sections or has more than 10 Completed task rows.

Missing optional files are not defects. A warning prompts review; it is not permission to delete records or change active task contracts.

The upgrade is complete when the Project section records `Protocol version: 3`, the adoption is confirmed and documented, legacy records remain recoverable, and no unnecessary empty files were created. Existing task IDs, phases, history, active contracts and accepted evidence remain intact.

## Changelog

### 2026-11-16 — protocol version 3

- **Affects**: context background paths, optional CONTEXT.md, knowledge creation/logging, decision records, status attention layout, phase closeout and validation warnings.
- **Detect**: duplicated skill inventory, session-only glossary creation, empty knowledge files, verbose/no-op coordination records, or more than 10 Completed task rows.
- **Fix**: consolidate current skills into background/01; retain 02 as legacy input; create glossary and knowledge files only under their triggers; use nested Needs you now sections; keep decision entries append-only; run the phase closeout checklist.
- **Safety**: `confirm` for project adoption, AGENTS.md rule changes, archive destination/retention, knowledge-layer creation in an existing project, and any change to active task scope or permissions. Mechanical warnings are non-blocking.

### 2026-10-24 — protocol version 2

- **Affects**: `project-status.md` metadata, optional knowledge layer, root `AGENTS.md` navigation, task templates, Reviewer/QA references and existing project adoption.
- **Detect**: `Protocol version` (machine-readable `protocol_version`) absent or below 2; a multi-session project with durable conclusions only in chat/receipts; layer-only task decomposition; Reviewer/QA findings not separated by Spec and Standards/behavior; hard-bug work without a reproduction loop.
- **Fix**: add `Protocol version: 2` on the next Commander write; create `knowledge/LOG.md` only under the knowledge-layer trigger; bind the applicable new references to new tasks; propose (do not silently apply) `AGENTS.md` navigation updates. Active tasks keep their saved contracts unless the user confirms a versioned change. No task-schema migration.
- **Safety**: `auto` for the version metadata only; `confirm` for knowledge-layer creation, `AGENTS.md`, project rules, external knowledge writes or any change that alters an active task's scope or permission.

## Maintaining this file

Every protocol change that affects existing instances must add an entry here and bump the version and date. Skill-internal wording, routing or optional references that leave existing instances valid do not require an entry.

Each entry states: **Affects**, **Detect**, **Fix**, and **Safety**.
