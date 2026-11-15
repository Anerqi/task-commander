# 23 - Protocol Version and Upgrade

> Read when opening an existing project after a Task Commander update, when a status file predates the current protocol, or when deciding whether an old project needs migration. This is a pull model: nothing updates an existing project automatically.

**Current protocol version: 3 (2026-11-15).**

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
- **Central validation limits:** existing knowledge-file limits and the completed-task warning threshold are defined in `scripts/validation_limits.py`.

None of these adds a role, task state or required task-table column.

## Compatibility

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
9. Add optional coordination sections only when they carry current information. Preserve all active task contracts unless the user confirms a versioned change.

## Detect drift

A project may need Version 3 adoption when:

- the skill inventory is maintained only in a new or repeatedly regenerated `background/02_skill_list.md` file;
- CONTEXT.md is being created solely because grill-with-docs was loaded for a one-time session;
- empty knowledge files or a LOG entry for every routine task transition are accumulating;
- AGENTS.md contains volatile task counts, milestone counters or temporary progress notes;
- decision-log entries duplicate full option analysis or prior confirmed decisions are being rewritten;
- the status file carries empty optional coordination sections or has more than 10 Completed task rows.

Missing optional files are not defects. A warning prompts review; it is not permission to delete records or change active task contracts.

The upgrade is complete when the Project section records `Protocol version: 3`, the adoption is confirmed and documented, legacy records remain recoverable, and no unnecessary empty files were created.

## Changelog

### 2026-11-15 — protocol version 3

- **Affects**: context background paths, optional CONTEXT.md, knowledge creation/logging, decision records, status attention layout, phase closeout and validation warnings.
- **Detect**: duplicated skill inventory, session-only glossary creation, empty knowledge files, verbose/no-op coordination records, or more than 10 Completed task rows.
- **Fix**: consolidate current skills into background/01; retain 02 as legacy input; create glossary and knowledge files only under their triggers; use nested Needs you now sections; keep decision entries append-only; run the phase closeout checklist.
- **Safety**: `confirm` for project adoption, AGENTS.md rule changes, archive destination/retention, knowledge-layer creation in an existing project, and any change to active task scope or permissions. Mechanical warnings are non-blocking.

### 2026-10-24 — protocol version 2

- **Affects**: optional knowledge layer, window-boundary choices, task shaping, two-axis review, debug feedback loop, retro and protocol metadata.
- **Detect**: optional v2 capabilities absent where they create current risk.
- **Fix**: adopt relevant v2 capabilities incrementally; preserve task IDs, phases, history and accepted evidence.
- **Safety**: `confirm` for project rules, active task contract changes, external writes and knowledge-layer creation in existing projects.

## Maintaining this file

Every protocol change that affects existing instances must add an entry here and bump the version and date. Skill-internal wording, routing or optional references that leave existing instances valid do not require an entry.

Each entry states: **Affects**, **Detect**, **Fix**, and **Safety**.
