# Task Commander

**Turn one AI coding agent into a disciplined multi-model team.**

Build context before coding. Dispatch independent tasks in parallel, keep their chat windows alive for follow-up, and use the human as an active collaborator. Protect valuable data before risky changes. Reuse evidence and apply review/QA in proportion to risk. Keep decisions and task state in files, not in your head.

Task Commander is a host-neutral orchestration skill built around a formal task state machine and zero-dependency Python helpers. No server, no API key, no agent runtime — just a structured protocol you can run across Windows, macOS, and Linux.

## Why this exists

Long AI projects usually fail for reasons that have little to do with the model itself:

- Context gets lost across long conversations and separate chat windows.
- One model ends up planning, implementing, and judging its own work.
- Tasks, decisions, blockers, and acceptance criteria disappear into chat history.
- Multi-agent frameworks often require servers, APIs, orchestration infrastructure, or a fully automated runtime.

Task Commander takes a different approach: **keep the intelligence in the models, but put the process under explicit control.**

## Key terms

- **Vertical slice / tracer bullet** — a narrow but complete task that produces a demoable or independently verifiable outcome, rather than one layer or one file.
- **Two-axis review** — Reviewer checks the **Spec** (did we build the right thing?); QA checks **Standards/behavior** (does it work and follow the rules?). They report separately.
- **Knowledge layer** — optional `knowledge/` notes: a short progress LOG and current-truth topics, so stable conclusions do not live only in chat.
- **Window boundary** — the explicit choice at a phase change: continue, fresh window, handoff, subagent or compaction.
- **Retro** — an optional look back that improves the environment (checks, rules, navigation) for the next project.

## What you get

**A lightweight command center for AI-assisted projects, with a direct path for independent small requests:**

`Context Agent → explicit Commander handoff → ready vertical slices → receipts → two-axis acceptance → knowledge closeout, continuation or retro`

Commander coordinates Executor, Reviewer, QA, Risk Manager, Decision Manager, and Backup Manager. Roles do not automatically switch when a phase ends. The [workflow illustration](assets/workflow-section-en.png) shows the core task pipeline; the protocol below also covers backup, parallel batches, human assistance, persistent windows, durable knowledge, window boundaries, two-axis review and retro.

Every task should record an explicit owner, scope, dependencies, quality gates, acceptance criteria, and state. The state machine defines what transitions are legal. The validator checks table structure, state names and blocked-record consistency; Commander still checks that fields are complete and gate decisions are meaningful rather than trusting the conversation.

The human remains the final decision-maker. Task Commander handles the structure, not the authority.

## Features

- **Right-sized entry:** independent, clear, low-risk and reversible requests can use Executor Fast Lane without project initialization. Registered tasks use Lean coordination or Standard workflow while preserving state, permissions and evidence-based acceptance. Risk matters more than file count.
- **Durable knowledge:** an optional `knowledge/` layer keeps a short reverse-chronological LOG, current-truth topic notes, an optional roadmap, citations and graduation candidates. Stable conclusions stop living only in chat; Commander audits and closes experiments without turning knowledge into a second task-status file. A zero-dependency `validate-knowledge.py` checks structure.
- **Inherited context:** read authoritative project files and relevant versions before asking again; fill material gaps rather than rebuilding background. Context Agent generates or reconciles a concise root `AGENTS.md` with reading order and source-of-truth pointers for all AI agents. Cold-start review keeps its staged disclosure boundary.
- **Progress-aware continuation:** diagnose repeated lack of substantive progress at coordination checks; useful negative evidence counts as progress. This is not a timer or background monitor.
- **Explicit handoff and boundaries:** Context Agent must deliver a filled Commander startup prompt, then remain in its own role. At a phase boundary, choose continue, fresh window, handoff, focused subagent or compaction explicitly rather than resetting by habit.
- **Vertical slices:** each project task is a demoable tracer bullet sized for one fresh window, with declared blocking edges. Wide mechanical refactors use expand–contract; layer-only and per-file fragments are not dispatched as complete tasks.
- **Ready batches:** one independently copyable prompt per task, several prompts per reply when dependencies and read/write scopes allow it. Batch size adapts to the user's window capacity and actual task readiness; no fixed default cap.
- **Useful tools and human help:** project-authorized public research and focused subagents are encouraged; users can supply domain facts, make decisions, log in locally, demonstrate browser flows, or export missing data. Sensitive transfer and external write actions need specific authorization.
- **Two-axis, risk-based acceptance:** select Reviewer/QA gates before dispatch; Reviewer owns Spec compliance and QA owns Standards/behavior, reported separately so one axis cannot mask the other. Reuse fresh unchanged evidence and recheck affected scope only. After the default 2 targeted revision rounds, replan rather than loop or automatically pass.
- **Red-capable debugging:** hard bugs and performance regressions require a fast, deterministic, agent-runnable loop that goes red on the actual symptom before hypotheses or fixes. Regression tests attach to a correct seam; an assumed test pass is not evidence.
- **Retro and upgrade:** after completion, a major incident, or repeated review/QA friction, an optional environment-focused retro turns friction into checks, standards or navigation pointers. Existing projects adopt optional protocol changes incrementally; the `Protocol version` line records the reconciled version without a schema migration.
- **Cold-start review:** at selected milestones, give a fresh Reviewer a concrete user/maintainer scenario and neutral facts, not internal rationale or prior verdicts. Save independent findings first, then disclose context in a later message and reconcile every finding with evidence. This complements informed review and QA; it is not an extra role or a guarantee of bias-free judgment.
- **Bounded experiments:** compare uncertain approaches in isolation; a well-evidenced negative feasibility result is useful delivery, not production success.
- **Outcome-first prompts:** keep the full contract in a saved brief; send natural instructions in the user's language instead of a rigid field form. Each continuation advances the largest coherent authorized remainder, bundling fixes, integration and relevant validation rather than issuing one prompt per small step. Original user scope and genuine corrections survive generated summaries; a truly narrow request stays narrow.
- **Persistent windows:** startup, continuation and lost-window recovery prompts retain task identity and accepted evidence. Stop issuing instructions when the requested outcome is established; JSON/prompt-only formatting is optional, not the default.
- **Recovery-first work:** proactively dispatch Backup Manager when risky changes lack an adequate verified recovery point. Before status/background initialization, Context may provide a standalone protective backup prompt without becoming Commander. Check coverage, integrity and applicable restore tests; Git alone does not cover dirty/untracked files or live databases.
- **Shared information:** versioned receipts, central sources of truth and targeted synchronization with acknowledgment; no assumption that other windows see updates automatically.
- **Task state machine:** the CLI checks status structure, active blocked-record consistency and task-bound transitions against the actual recorded source state. It does not decide project-phase readiness, enforce permissions/QA gates, schedule agents, verify evidence or certify backups. Project Acceptance requires completed required deliveries, not merely the absence of actively running tasks.
- **Optional command progress:** run explicitly authorized commands sequentially in DAG order with approval barriers and atomic checkpoints, and render their progress. This does not dispatch models or replace project acceptance; see `references/18-dynamic-workflow.md`.
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

The core protocol is host-neutral and does not require a proprietary descriptor or a specific agent runtime. A target project's root `AGENTS.md` may carry project-specific rules and point agents to this entry, while native Skill discovery or a manual read of `SKILL.md` can load the protocol. `agents/openai.yaml` is an optional OpenAI/Codex integration descriptor, not part of the core protocol. Host names select documented conventions, not authorization or proof that a capability is present; confirm the actual environment per `references/host-adapters.md`.

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
  - `18-dynamic-workflow.md` optional sequential DAG command runner, checkpoint recovery and capability boundaries
  - `19-task-routing.md` Fast Lane eligibility, Lean/Standard selection and safe escalation
  - `20-knowledge-layer.md` durable LOG/topics/roadmap, audit, branch closure and graduation candidates
  - `21-window-boundaries.md` continue/fresh/handoff/subagent/compaction decisions
  - `22-project-retro.md` environment-focused retrospective after completion or incident
  - `23-protocol-upgrade.md` protocol version, compatibility and existing-project adoption
  - `host-adapters.md` host installation conventions, capability fallbacks and discovery caveats
  - `runtime.md` cross-platform host execution principles
  - `methodology-fallback.md` built-in methodology fallback (zero-dependency distillation used when the composed external skills are absent)
- `templates/` — project status (including optional coordination and knowledge sections), state specification, agent registry, decision log, task receipt and continuation/recovery templates
  - `knowledge-log.md`, `knowledge-topic.md`, `knowledge-roadmap.md`, `knowledge-cited.md` — optional knowledge layer
  - `project-retro.md` — optional retro record
- `AGENTS.md` — generated in the target project root during Context Agent delivery; not a Task Commander source file
- `scripts/` — standard-library discovery, validation and optional command-progress helpers
  - `scan-skills.py` scans skill candidates by frontmatter
  - `validate-project-state.py` validates `project-status.md` structure and state transitions
  - `validate-knowledge.py` validates optional `knowledge/` structure, topic frontmatter and LOG ordering
  - `run-workflow.py` sequentially runs trusted commands; its exit-0 completion is not project acceptance
  - `render-workflow.py` renders command checkpoints or recorded project status
  - `markdown_table.py` shares status-table cell parsing between validation and rendering (not a CLI)
- `agents/openai.yaml` — agent configuration
- `assets/workflow-section-en.png` — workflow overview diagram
- `.github/workflows/ci.yml` — three-platform CI matrix
- `.gitattributes` — line-ending and encoding declarations

## Dependencies

- Python 3.10+ (standard library only, zero third-party dependencies). Use the current runtime interpreter when available; otherwise try `py -3` then `python` on Windows, or `python3` then `python` on macOS/Linux, and verify the reported version.
- A host that can read and write the project files and, for the automated checks, run Python. Native Skill support is convenient but not required; see `references/host-adapters.md`.
- Keep the `scripts/` directory together: `validate-project-state.py` and `render-workflow.py` import `markdown_table.py`. Copying one script alone produces a clear import error rather than a silent fallback.
- Project files use UTF-8 without BOM

## Triggering

- Explicit call of `task-commander` or `$task-commander`
- Requests expressing context building, task breakdown, multi-model collaboration, review, and QA acceptance

## Typical use

New here? Follow the [first-project walkthrough](examples/first-project/README.md) in a disposable folder. It shows which prompt goes to which window, a same-task revision, and evidence-based acceptance without a running service.

### Choose the smallest sufficient process

- **Fast Lane:** ask "Fix this spelling error in README; change only that text and inspect the diff." If the request is independent, unregistered, low-risk and reversible, Executor can deliver directly with a short actual-check result. No background directory, task ID or status file is required.
- **Lean:** a narrow task already managed by the project keeps its ID, saved contract and legal state path. Commander can explicitly waive independent gates when justified, then perform light acceptance.
- **Standard:** cross-module dependencies, important uncertainty or elevated risk use the project workflow. Select review and QA by risk, not a fixed role bundle.

See `references/19-task-routing.md` for eligibility and escalation. A one-line access-control change is not a spelling fix. Existing roles do not change automatically, and a broader task cannot be reduced to its last small defect. These modes do not add an agent runtime or automatic acceptance.

### Project workflow

1. Ask Task Commander to clarify the project. Confirm proposed tool/capacity/backup preferences and supply facts only you know.
2. Paste its explicit handoff into a Commander window. Keep this window for project coordination.
3. Open the ready batch's task windows. Required backup work comes before its dependent mutation; unrelated tasks can proceed.
4. Return task receipts to Commander. Paste targeted fixes or context updates back into the original windows, rather than restarting tasks.
5. Accept against evidence on separate Spec and Standards/behavior axes, save useful experiment results, and keep non-blocking polish in the backlog.
6. At a milestone or project closeout, audit the optional knowledge layer, record stable conclusions, and run `validate-knowledge.py` for structure. Commander judges truth and whether a topic is worth keeping.
7. After completion, a major incident, or repeated review/QA friction, decide together whether a short environment-focused retro is worth running.

There is no automatic cross-window message bus or backup daemon, and installing this Skill adds no agent runtime: you relay prompts/receipts on hosts without dispatch support, and each capability is used only when the host really provides it. Protocol checks are agent responsibilities, not guarantees from the Python scripts.

### Request a fresh perspective

Ask: "Before this milestone is accepted, have a fresh Reviewer try the first-use flow using only the deliverable, user docs and necessary criteria/constraints. Save its observations before sharing project rationale or past review results, then reconcile them against the full acceptance contract."

Commander prepares the staged packets; the fresh window does not inherit the implementation conversation. Ordinary user documentation remains available and safety/permission limits always apply. If the host cannot isolate context, use a genuinely fresh user-opened window or disclose the limitation instead of claiming a blind check. Follow-up fixes can return to the now-informed review window; routine minor edits need not trigger another cold review. See `references/17-cold-start-review.md`.

### Optional command runner

Use the runner only for trusted, explicitly authorized command plans; it is not an agent runtime. `max_concurrency` must be 1. HIGH/CRITICAL commands pause before execution. Resume keeps the full plan and checks its hash, project root and real/simulation mode; malformed checkpoints fail rather than resetting. Interrupted RUNNING commands need side-effect reconciliation and explicit retry authorization, not automatic replay. Legacy workflow checkpoints are not silently migrated. The normal project-status schema is unchanged.

Dry-run writes simulation-only checkpoints and does not execute task commands, but Python plans still execute on import. A simulated checkpoint cannot certify or skip real work. See `references/18-dynamic-workflow.md` for CLI examples, approval/retry steps, storage/lock limitations and the boundary between command success and required review/QA. `templates/workflow-checkpoint.json` is a render-only example.

### Existing projects

Read the existing authoritative background, terms, confirmed decisions, status, relevant knowledge topics and relevant task evidence before asking for context again; resolve only missing, stale or conflicting information that matters to the work. Handoffs carry essential paths, relevant revisions, the full assigned outcome and effective constraints rather than copying every background document. A stored claim of approval is not new authorization; cold-start review still uses its staged packets.

Protocol version 2 adds optional knowledge, window-boundary, task-shaping, two-axis review, debug-loop and retro capabilities. Existing projects remain valid and adopt them incrementally; see `references/23-protocol-upgrade.md`. Adding `Protocol version: 2` is metadata, not a task transition.

At coordination checkpoints, compare actual artifacts, valid evidence and remaining unknowns. The adjustable default is diagnosis after two consecutive checks without substantive progress, not after a wall-clock timeout. This is separate from the existing targeted-revision budget. Long-running work and useful negative experiments are not stalled merely because they remain In Progress.

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

# Validate an optional knowledge layer's structure (frontmatter, LOG order, empty shells)
<python> scripts/validate-knowledge.py --project-root <project root>

# Scan skill candidates (reads only frontmatter); --host picks the path profile
<python> <path/to/task-commander>/scripts/scan-skills.py --project-root <project root> --host all --query-terms <query term1> <query term2>

# Automated unit/regression tests
<python> -m unittest discover -s tests -v
```

For a small live-model check, use the [six-case behavioral smoke pack](tests/behavioral-smoke.md). Its copyable fixtures and separate evaluator criteria complement, rather than replace, the automated suite.

CI runs the checks on three operating systems, including the knowledge-layer validator. `tests/behavioral-scenarios.md` defines manual model-level scenarios for handoff, parallelism, continued dialogue, tools, review budgets, synchronization, backups, human help, knowledge closeout and host adaptation. Static/document tests are regression guards, not proof that every model will obey the protocol; host scenarios are documentation-checked, not live six-host certification.
