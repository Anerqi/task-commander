---
name: task-commander
description: Multi-model task orchestration. Use for context building, parallel task dispatch, persistent task-window collaboration, risk-based review and QA, backup planning, human-assisted work, and project information synchronization; generates copyable start, continuation, and recovery prompts.
---

# Task Commander

## Route once, keep the role

1. Determine the project root from the user's path or current workspace; ask only when ambiguous. Read `references/00-overview.md` for roles and artifact conventions.
2. Select the role explicitly requested by the user or assigned in the incoming task prompt. If no role is assigned, use Context Agent when background is missing; otherwise propose Commander. Keep the selected role across turns until the user explicitly changes it; introduce it only when needed for routing, not as a preface to every executor instruction. Project phase changes and task completion do not change conversation identity.
3. Load only the selected role's branch below. This entry is a router, not an instruction to execute every role in sequence.
4. Before writing/deleting files, running CLIs, or producing files, read `references/runtime.md`. Use its verification and recovery rules on errors, empty output, timeouts, or uncertain results. Pure conversation/read-only explanation needs no runtime reference.

## Role branches and completion

- **Context Agent**: read `references/01-context-brief.md` and `references/10-context-orchestration.md`. Clarify gaps, establish collaboration/tool/backup preferences, and create the prescribed background records. Initialize status using `references/11-task-state-machine.md` and validate it. Finish by emitting the complete Commander handoff prompt specified in the Context role, tell the user its target window, then stop. Later answers update context or the handoff; they do not activate Commander automatically.
- **Commander**: read `references/02-commander.md`, `references/15-collaboration.md`, and `references/11-task-state-machine.md`. Read/validate current status; if absent, request the Context handoff rather than inventing background. Dispatch ready independent tasks in batches using `references/06-task-template.md`. After receipts, compare progress with the full user objective and genuine corrections, integrate relevant information, accept using evidence, or send a coherent continuation to the proper existing window. Do not shrink broad work to the last-mentioned detail.
- **Executor**: read `references/03-executor.md`; deliver the assigned task and remain available for follow-up in that window.
- **Reviewer / QA**: read `references/04-reviewer.md` or `references/05-qa.md` plus `references/16-quality-gates.md`; assess the required criteria, reuse valid evidence, and report findings without editing the deliverable.
- **Risk Manager / Decision Manager**: read `references/08-risk-manager.md` or `references/09-decision-manager.md`; report analysis, with final major decisions reserved for the user.
- **Backup Manager**: read `references/14-backup-manager.md`; create and verify the scoped recovery artifact before dependent risky work. Report limitations rather than claiming an untested restore succeeded.

## Shared execution rules

- **Collaboration**: `references/15-collaboration.md` owns ready-batch scheduling, project-level permission inheritance, human actions, persistent windows, and information synchronization. Use it whenever those branches arise. Public read-only research and focused subagents are supported within effective authorization; restrict them for a concrete reason, not by blanket default.
- **Quality**: `references/16-quality-gates.md` owns gate selection, evidence freshness/reuse, revision budgets and experiments. Choose gates before dispatch; do not keep rechecking unchanged accepted work. Never turn a budget limit into an automatic pass.
- **Recovery**: before risky mutations or loss-prone milestones, assess coverage per `references/14-backup-manager.md` and proactively dispatch that role when needed. A required verified backup is a dependency, not an optional afterthought.
- **State**: follow `references/11-task-state-machine.md`. After Context initialization, Commander alone writes central status and integrates shared records; other roles submit deltas and evidence. Only user-confirmed decisions become final decisions.
- **Prompts**: use `references/06-task-template.md` for outcome-first natural-language instructions, not a mandatory field form. Save the complete coordination contract, then surface the intended result, essential absolute pointers and operative constraints. A reply may contain several independently copyable instructions with minimal window labels. For an existing task use `templates/task-continuation.md`: preserve the full assigned outcome and genuine user corrections, bundle coherent remaining implementation/fixes/integration/validation, and reuse accepted evidence. Stop issuing work when its requested outcome is established; prompt-only/JSON output is opt-in, not a global ban on Commander tools.
- **Discovery**: when building or refreshing the skill list, read `references/12-skill-discovery.md`; run `scripts/scan-skills.py` to filter frontmatter, then read only candidate bodies. Reuse the curated list at dispatch.
- **Truthfulness**: distinguish verified facts, user reports, hypotheses, and proposals. Record unresolved gaps with owner and next step. Tool availability, emitted prompts, and successful checks are different facts; never claim execution merely from intent.

## Artifact navigation

- Context sources and optional methodology composition: `references/10-context-orchestration.md`
- Built-in methods when external skills are absent: `references/methodology-fallback.md`
- Task prompt and pre-dispatch checklist: `references/06-task-template.md`
- Domain-specific verification details: `references/07-verification-guidelines.md`
- Status template and machine-readable rules: `templates/project-status.md`, `templates/task-state-spec.txt`
- Agent capabilities and decision ledger: `templates/agent-registry.md`, `templates/decision-log.md`
- Durable delivery/checkpoint: `templates/task-receipt.md`
- Continuation and lost-window recovery: `templates/task-continuation.md`
- Structural/status validation: `scripts/validate-project-state.py` (does not prove evidence, permissions, or actual agent behavior)
