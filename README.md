# Task Commander

**Turn one AI coding agent into a disciplined multi-model team.**

Build context before coding. Dispatch independent tasks in parallel, keep their chat windows alive for follow-up, and use the human as an active collaborator. Protect valuable data before risky changes. Reuse evidence and apply review/QA in proportion to risk. Keep decisions and task state in files, not in your head.

Task Commander is a host-neutral orchestration skill built around a formal task state machine and two zero-dependency Python scripts. No server, no API key, no agent runtime — just a structured protocol you can run across Windows, macOS, and Linux.

## Why this exists

Long AI projects usually fail for reasons that have little to do with the model itself:

- Context gets lost across long conversations and separate chat windows.
- One model ends up planning, implementing, and judging its own work.
- Tasks, decisions, blockers, and acceptance criteria disappear into chat history.
- Multi-agent frameworks often require servers, APIs, orchestration infrastructure, or a fully automated runtime.

Task Commander takes a different approach: **keep the intelligence in the models, but put the process under explicit control.**

## What you get

**A lightweight command center for AI-assisted projects:**

`Context Agent → explicit Commander handoff → ready task batches → receipts → acceptance or continuation`

Commander coordinates Executor, Reviewer, QA, Risk Manager, Decision Manager, and Backup Manager. Roles do not automatically switch when a phase ends. The existing [workflow illustration](assets/workflow-section-en.png) shows the original role overview; the protocol below also covers backup, parallel batches, human assistance and persistent windows.

Every task has an explicit owner, scope, dependencies, quality gates, acceptance criteria, and state. The state machine defines what transitions are legal, while the validator script checks the project status instead of trusting the conversation.

The human remains the final decision-maker. Task Commander handles the structure, not the authority.

## Features

- **Explicit handoff:** Context Agent must deliver a filled Commander startup prompt, then remain in its own role.
- **Ready batches:** one independently copyable prompt per task, several prompts per reply when dependencies and read/write scopes allow it. Proposed default: 3 active primary tasks, adjustable to your capacity.
- **Useful tools and human help:** project-authorized public research and focused subagents are encouraged; users can supply domain facts, make decisions, log in locally, demonstrate browser flows, or export missing data. Sensitive transfer and external write actions need specific authorization.
- **Risk-based acceptance:** select Reviewer/QA gates before dispatch, reuse fresh unchanged evidence, and recheck affected scope only. After the default 2 targeted revision rounds, replan rather than loop or automatically pass.
- **Bounded experiments:** compare uncertain approaches in isolation; a well-evidenced negative feasibility result is useful delivery, not production success.
- **Outcome-first prompts:** keep the full contract in a saved brief; send natural instructions in the user's language instead of a rigid field form. Each continuation advances the largest coherent authorized remainder, bundling fixes, integration and relevant validation rather than issuing one prompt per small step. Original user scope and genuine corrections survive generated summaries; a truly narrow request stays narrow.
- **Persistent windows:** startup, continuation and lost-window recovery prompts retain task identity and accepted evidence. Stop issuing instructions when the requested outcome is established; JSON/prompt-only formatting is optional, not the default.
- **Recovery-first work:** proactively dispatch Backup Manager when risky changes lack an adequate verified recovery point. Check coverage, integrity and applicable restore tests; Git alone does not cover dirty/untracked files or live databases.
- **Shared information:** versioned receipts, central sources of truth and targeted synchronization with acknowledgment; no assumption that other windows see updates automatically.
- **Task state machine:** the CLI checks status structure, names and requested transitions; it does not enforce permissions, schedule agents, verify evidence or certify backups.
- **Low-cost discovery and portable core:** frontmatter-only Skill scanning, Python standard library, Windows/macOS/Linux. Codex and OpenCode are the currently supported hosts.

## Installation

Put this directory into the host's skill search path; the location is resolved at runtime via Runtime Discovery, never hard-coded.

- OpenCode: place this directory in a standard skill directory — a user-level `~/.config/opencode/skills/` or a project-level `.opencode/skills/` (or the equivalent position for your setup); it is discovered automatically.
- Codex: place this directory under `$CODEX_HOME/skills/` (`$CODEX_HOME` defaults to `~/.codex`); it is discovered automatically.

The core protocol is host-neutral. Codex and OpenCode are currently supported hosts; other hosts are not officially adapted. `agents/openai.yaml` is an OpenAI/Codex-specific integration descriptor, not part of the core protocol.

The per-host directories are listed as adaptation examples in the "Known host adaptations (examples for adaptation, not the default protocol)" appendix of `references/12-skill-discovery.md`; `scripts/scan-skills.py` locates them at runtime.

The entry document is `SKILL.md`.

## Optional integrations

The context orchestration flow composes the following external skills; use each if present, otherwise use the built-in fallback `references/methodology-fallback.md` (location and composition order in `references/10-context-orchestration.md`):

- `writing-for-agents`
- `grill-with-docs`
- `wait-what`
- `to-questionnaire`

Optional:

- `skill-creator`: validates this skill's structure (using its own structure and content validation flow)

## Directory structure

- `SKILL.md` — skill entry and mandatory rules
- `references/` — role and workflow guidance
  - `00-overview.md` overview and role table
  - `01-context-brief.md` Context Agent prompt
  - `02-commander.md` Commander prompt
  - `03-executor.md` Executor prompt
  - `04-reviewer.md` Reviewer prompt
  - `05-qa.md` QA validation prompt
  - `06-task-template.md` task prompt template
  - `07-verification-guidelines.md` verification rules
  - `08-risk-manager.md` Risk Manager prompt
  - `09-decision-manager.md` Decision Manager prompt
  - `10-context-orchestration.md` context orchestration protocol
  - `11-task-state-machine.md` task state machine
  - `12-skill-discovery.md` skill discovery protocol
  - `14-backup-manager.md` recovery triggers, backup verification and restore boundaries
  - `15-collaboration.md` permissions, ready batches, human help, windows and synchronization
  - `16-quality-gates.md` risk-based gates, evidence reuse, revision budgets and experiments
  - `runtime.md` cross-platform host execution principles
  - `methodology-fallback.md` built-in methodology fallback (zero-dependency distillation used when the composed external skills are absent)
- `templates/` — project status (including optional coordination sections), state specification, agent registry, decision log, task receipt and continuation/recovery templates
- `scripts/` — skill scanning and project status validation scripts
  - `scan-skills.py` scans skill candidates by frontmatter
  - `validate-project-state.py` validates `project-status.md` structure and state transitions
- `agents/openai.yaml` — agent configuration
- `assets/workflow-section-en.png` — workflow overview diagram
- `.github/workflows/ci.yml` — three-platform CI matrix
- `.gitattributes` — line-ending and encoding declarations

## Dependencies

- Python 3.10+ (standard library only, zero third-party dependencies). Use the current runtime interpreter when available; otherwise try `py -3` then `python` on Windows, or `python3` then `python` on macOS/Linux, and verify the reported version.
- Codex or OpenCode with skill support (the core protocol is host-neutral; other hosts are not officially adapted)
- Project files use UTF-8 without BOM

## Triggering

- Explicit call of `task-commander` or `$task-commander`
- Requests expressing context building, task breakdown, multi-model collaboration, review, and QA acceptance

## Typical use

1. Ask Task Commander to clarify the project. Confirm proposed tool/capacity/backup preferences and supply facts only you know.
2. Paste its explicit handoff into a Commander window. Keep this window for project coordination.
3. Open the ready batch's task windows. Required backup work comes before its dependent mutation; unrelated tasks can proceed.
4. Return task receipts to Commander. Paste targeted fixes or context updates back into the original windows, rather than restarting tasks.
5. Accept against evidence, save useful experiment results, and keep non-blocking polish in the backlog.

There is no automatic cross-window message bus or backup daemon. On hosts without dispatch support, you relay prompts/receipts. Protocol checks are agent responsibilities, not guarantees from the Python scripts.

### Existing projects

Keep existing task IDs, phases and history. Add the optional coordination sections from `templates/project-status.md`, establish a context revision and project Collaboration policy, and checkpoint active tasks with `templates/task-receipt.md`. Existing status tables remain compatible; no schema migration is required. New defaults do not override previously agreed task permissions or gates; change an active contract explicitly.

## Script self-check

```text
# Validate a project status file (run from the Task Commander root)
<python> scripts/validate-project-state.py --path <path/to/project-status.md>

# Scan skill candidates (reads only frontmatter)
<python> scripts/scan-skills.py --query-terms <query term1> <query term2>

# Automated unit/regression tests
<python> -m unittest discover -s tests -v
```

CI runs the checks on three operating systems. `tests/behavioral-scenarios.md` defines manual model-level scenarios for handoff, parallelism, continued dialogue, tools, review budgets, synchronization, backups and human help. Static/document tests are regression guards, not proof that every model will obey the protocol.
