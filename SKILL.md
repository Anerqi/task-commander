---
name: task-commander
description: Multi-model task orchestration. Use for context building, durable project knowledge, parallel task dispatch, persistent task-window collaboration, window/phase boundaries, risk-based two-axis review and QA, backup planning, human-assisted work, project retro, and information synchronization; generates copyable start, continuation, and recovery prompts.
---

# Task Commander

## Route once, keep the role

1. Determine the project root from the user's path or current workspace; ask only when ambiguous. For project coordination or unfamiliar role boundaries, read `references/00-overview.md`. On an unfamiliar host, before installation, or when a needed capability may be missing, read `references/host-adapters.md`.
2. Preserve the role explicitly requested by the user or assigned in the incoming task prompt. At intake, lighter-path selection or changed scope/risk, use `references/19-task-routing.md`: Fast Lane is independent unregistered delivery, Lean reduces project coordination overhead, and Standard uses the existing project protocol. Modes do not change roles or task states. If no role is assigned, a qualifying Fast Lane request starts in Executor; otherwise use Context Agent when background is missing, or propose Commander. Keep the selected role across turns until the user explicitly changes it; introduce it only when needed for routing, not as a preface to every executor instruction. Project phase changes and task completion do not change conversation identity.
3. Load only the selected role's branch below. A Fast Lane Executor uses its inline contract and the routing reference instead of project initialization. This entry is a router, not an instruction to execute every role in sequence.
4. Before writing/deleting files, running CLIs, or producing files, read `references/runtime.md`. Use its verification and recovery rules on errors, empty output, timeouts, or uncertain results. Pure conversation/read-only explanation needs no runtime reference.

## Role branches and completion

- **Context Agent**: read `references/01-context-brief.md` and `references/10-context-orchestration.md`; for an existing project, also `references/23-protocol-upgrade.md`. Clarify gaps, create or reconcile background, generate root `AGENTS.md`, initialize and validate status, and create the optional knowledge layer only under the trigger in `references/20-knowledge-layer.md`. Handle the Pre-initialization protection handoff in `references/14-backup-manager.md` when a recovery point is needed. Emit the filled Commander handoff, name its target window, and stop in role.
- **Commander**: read `references/02-commander.md`, `references/15-collaboration.md`, and `references/11-task-state-machine.md`. Read/validate status and the relevant knowledge layer; if status is absent, request Context. Dispatch vertical slices, attach two-axis gates, integrate receipts and knowledge deltas, run the milestone knowledge audit when applicable, and use `references/21-window-boundaries.md` at a phase boundary. Do not implement tasks yourself or shrink broad work to the last detail.
- **Executor**: read `references/03-executor.md`; deliver the assigned vertical slice, build a red-capable loop for hard bugs/performance work per `references/07-verification-guidelines.md`, and propose knowledge deltas in the receipt. Fast Lane follows `references/19-task-routing.md`; registered tasks keep their contract, state machine and Commander acceptance.
- **Reviewer / QA**: read `references/04-reviewer.md` or `references/05-qa.md` plus `references/16-quality-gates.md`; report without editing. Reviewer owns Spec; QA owns Standards/behavior; keep the axes separate. Cold-start review follows `references/17-cold-start-review.md` before loading project context.
- **Risk / Decision / Backup**: read `references/08-risk-manager.md`, `references/09-decision-manager.md`, or `references/14-backup-manager.md`; analyze or protect, never make the user's final decision or claim an untested restore.

## Shared execution rules

- **Project rules**: read the target project's root `AGENTS.md` when present; cold-start stage 1 gets only its neutral packet.
- **Collaboration**: `references/15-collaboration.md` owns batches, permissions, windows and synchronization. Public research and focused subagents are allowed within effective authorization.
- **Quality**: `references/16-quality-gates.md` owns gates. Reviewer=Spec, QA=Standards/behavior; no budget or one axis becomes an automatic pass.
- **Recovery**: `references/14-backup-manager.md` owns recovery. Knowledge records are durable assets; a required verified backup gates dependent mutation.
- **State**: `references/11-task-state-machine.md` owns status. Commander is the sole status writer after Context initialization and integrates shared records; only user-confirmed decisions are final. The optional knowledge layer never replaces task state.
- **Knowledge**: `references/20-knowledge-layer.md` owns the durable layer. Stable conclusions go to topics, short progress to LOG; no empty shells or external copies. Graduation requires user confirmation.
- **Boundaries**: `references/21-window-boundaries.md` owns phase/window choices; `references/22-project-retro.md` is the optional environment retro after completion, a major incident, or repeated review/QA friction. Do not reset or auto-edit project rules by habit.
- **Prompts**: `references/06-task-template.md` owns vertical slices and outcome-first instructions. Save the contract, reference paths, bundle coherent work, and stop when the outcome is established.
- **Discovery**: `references/12-skill-discovery.md` plus `scripts/scan-skills.py`; filter frontmatter, then read only candidate bodies.
- **Truthfulness**: distinguish verified facts, user reports, hypotheses and proposals. Tool availability, emitted prompts and successful checks are different facts; never claim execution from intent.

## Artifact navigation

- Execution modes, independent Fast Lane eligibility and escalation: `references/19-task-routing.md`
- Host installation conventions and capability fallbacks: `references/host-adapters.md`
- Context sources and optional methodology composition: `references/10-context-orchestration.md`
- Context Agent deliverables and AGENTS.md generation/merge rules: `references/01-context-brief.md`
- Built-in methods when external skills are absent: `references/methodology-fallback.md`
- Task prompt, vertical slicing and pre-dispatch checklist: `references/06-task-template.md`
- Domain-specific verification details, including bug/perf feedback loops: `references/07-verification-guidelines.md`
- Cold-start review packets, isolation and informed reconciliation: `references/17-cold-start-review.md`
- Durable project knowledge, audit, branch closure and graduation candidates: `references/20-knowledge-layer.md`
- Window/phase boundary choices: `references/21-window-boundaries.md`
- Optional project retro and environment improvement: `references/22-project-retro.md`
- Existing-project protocol version and upgrade: `references/23-protocol-upgrade.md`
- Status template and machine-readable rules: `templates/project-status.md`, `templates/task-state-spec.txt`
- Agent capabilities and decision ledger: `templates/agent-registry.md`, `templates/decision-log.md`
- Knowledge templates: `templates/knowledge-log.md`, `templates/knowledge-topic.md`, `templates/knowledge-roadmap.md`, `templates/knowledge-cited.md`
- Durable delivery/checkpoint: `templates/task-receipt.md`
- Continuation, boundary and lost-window recovery: `templates/task-continuation.md`
- Optional project retro record: `templates/project-retro.md`
- Before optional command execution, checkpoint resume or rendering: `references/18-dynamic-workflow.md`, `templates/workflow-plan.template.py`, `templates/workflow-checkpoint.json`. The runner is sequential command progress, not agent dispatch or project acceptance.
- Structural/status validation: `scripts/validate-project-state.py`; knowledge-layer structure: `scripts/validate-knowledge.py` (neither proves evidence, permissions, or actual agent behavior)
