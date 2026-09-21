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
- **Cold-start review:** at selected milestones, give a fresh Reviewer a concrete user/maintainer scenario and neutral facts, not internal rationale or prior verdicts. Save independent findings first, then disclose context in a later message and reconcile every finding with evidence. This complements informed review and QA; it is not an extra role or a guarantee of bias-free judgment.
- **Bounded experiments:** compare uncertain approaches in isolation; a well-evidenced negative feasibility result is useful delivery, not production success.
- **Outcome-first prompts:** keep the full contract in a saved brief; send natural instructions in the user's language instead of a rigid field form. Each continuation advances the largest coherent authorized remainder, bundling fixes, integration and relevant validation rather than issuing one prompt per small step. Original user scope and genuine corrections survive generated summaries; a truly narrow request stays narrow.
- **Persistent windows:** startup, continuation and lost-window recovery prompts retain task identity and accepted evidence. Stop issuing instructions when the requested outcome is established; JSON/prompt-only formatting is optional, not the default.
- **Recovery-first work:** proactively dispatch Backup Manager when risky changes lack an adequate verified recovery point. Before status/background initialization, Context may provide a standalone protective backup prompt without becoming Commander. Check coverage, integrity and applicable restore tests; Git alone does not cover dirty/untracked files or live databases.
- **Shared information:** versioned receipts, central sources of truth and targeted synchronization with acknowledgment; no assumption that other windows see updates automatically.
- **Task state machine:** the CLI checks status structure, active blocked-record consistency and task-bound transitions against the actual recorded source state. It does not decide project-phase readiness, enforce permissions/QA gates, schedule agents, verify evidence or certify backups. Project Acceptance requires completed required deliveries, not merely the absence of actively running tasks.
- **Low-cost discovery and portable core:** frontmatter-only Skill scanning, Python standard library, Windows/macOS/Linux. The protocol is host-neutral; documented adapters cover Pi, Claude Code, Cursor, GitHub Copilot, Codex, OpenCode, and any other host that can read the files.

## Installation

Put this directory into a skill location the host loads, or point the agent at it manually; the exact location is resolved at runtime via Runtime Discovery, never hard-coded. `references/host-adapters.md` owns the per-host table, capability fallbacks and verification boundary.

- Pi: project `.pi/skills/` or `.agents/skills/`, user `~/.pi/agent/skills/` or `~/.agents/skills/` (`PI_CODING_AGENT_DIR` overrides `~/.pi/agent`).
- Claude Code: project `.claude/skills/`, user `~/.claude/skills/`.
- Cursor: project `.cursor/skills/` or `.agents/skills/`, user `~/.cursor/skills/` or `~/.agents/skills/`.
- GitHub Copilot: project `.github/skills/`, user `~/.copilot/skills/` or `~/.agents/skills/`.
- Codex: project or user `.agents/skills/`; the older `$CODEX_HOME/skills/` location remains a scanner compatibility path.
- OpenCode: project `.opencode/skills/`, user `~/.config/opencode/skills/`.
- Other hosts: load the absolute `SKILL.md` path manually and, if needed, pass `--roots` explicitly to the scanner.

The core protocol is host-neutral and does not require a proprietary descriptor or a specific agent runtime: an `AGENTS.md`-style pointer, a manual read of the entry file, or native Skill discovery all work. `agents/openai.yaml` is an optional OpenAI/Codex integration descriptor, not part of the core protocol. Host names select documented conventions, not authorization or proof that a capability is present; confirm the actual environment per `references/host-adapters.md`.

The per-host directories are listed as an adaptation table in `references/host-adapters.md` and as runtime adaptation examples in the appendix of `references/12-skill-discovery.md`; `scripts/scan-skills.py` locates them at runtime, filtered by `--host` (default `all`).

The entry document is `SKILL.md`.

## Optional integrations

The context orchestration flow composes the following external skills when their branches apply; use available methods or the matching module of `references/methodology-fallback.md` (loading conditions and composition order in `references/10-context-orchestration.md`):

- `writing-for-agents` — startup writing rules
- `grill-with-docs` — startup interview method; terminology/ADR formats when needed
- `wait-what` — only when clarification is needed
- `to-questionnaire` — only for third-party knowledge gaps

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
  - `17-cold-start-review.md` neutral review packets, context isolation, independent discovery and later informed reconciliation
  - `host-adapters.md` host installation conventions, capability fallbacks and discovery caveats
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
- A host that can read and write the project files and, for the automated checks, run Python. Native Skill support is convenient but not required; see `references/host-adapters.md`.
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

There is no automatic cross-window message bus or backup daemon, and installing this Skill adds no agent runtime: you relay prompts/receipts on hosts without dispatch support, and each capability is used only when the host really provides it. Protocol checks are agent responsibilities, not guarantees from the Python scripts.

### Request a fresh perspective

Ask: "Before this milestone is accepted, have a fresh Reviewer try the first-use flow using only the deliverable, user docs and necessary criteria/constraints. Save its observations before sharing project rationale or past review results, then reconcile them against the full acceptance contract."

Commander prepares the staged packets; the fresh window does not inherit the implementation conversation. Ordinary user documentation remains available and safety/permission limits always apply. If the host cannot isolate context, use a genuinely fresh user-opened window or disclose the limitation instead of claiming a blind check. Follow-up fixes can return to the now-informed review window; routine minor edits need not trigger another cold review. See `references/17-cold-start-review.md`.

### Existing projects

Keep existing task IDs, phases and history. Add the optional coordination sections from `templates/project-status.md`, establish a context revision and project Collaboration policy, and checkpoint active tasks with `templates/task-receipt.md`. Existing status tables remain compatible; no schema migration is required. New defaults do not override previously agreed task permissions or gates; change an active contract explicitly.

### Stricter transition validation

Status table columns are unchanged. Structural checks still use `--path` alone. Transition checks now require all of `--task-id`, `--from-state`, and `--to-state`; a missing/unknown task or a source state different from the recorded state fails. A lone `--task-id` is an error, not an ignored option.

Run a transition check **before** updating the state. After changing the task and its active blocked record together, validate the resulting file with `--path` only. Every Blocked task needs exactly one matching record with a legal pre-block state; duplicate, missing, orphan and stale records now fail. Preserve actual history when correcting old inconsistent files; do not invent a predecessor or bypass required gates.

## Script self-check

```text
# Validate a project status file (run from the Task Commander root)
<python> scripts/validate-project-state.py --path <path/to/project-status.md>

# Check a proposed transition against the current, pre-update task state
<python> scripts/validate-project-state.py --path <path/to/project-status.md> --task-id 01 --from-state "In Progress" --to-state "QA Pending"

# Scan skill candidates (reads only frontmatter); --host picks the path profile
<python> <path/to/task-commander>/scripts/scan-skills.py --project-root <project root> --host all --query-terms <query term1> <query term2>

# Automated unit/regression tests
<python> -m unittest discover -s tests -v
```

CI runs the checks on three operating systems. `tests/behavioral-scenarios.md` defines manual model-level scenarios for handoff, parallelism, continued dialogue, tools, review budgets, synchronization, backups, human help and host adaptation. Static/document tests are regression guards, not proof that every model will obey the protocol; host scenarios are documentation-checked, not live six-host certification.
