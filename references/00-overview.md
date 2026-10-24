# Multi-Model Task Orchestration System - Overview

> For project coordination, the Commander handles orchestration and dispatch, while context, execution, review, and QA have separate responsibilities. Independent small requests can use the Executor Fast Lane without initializing a project.

## Role table

| Role | File | Responsibility | Main output |
|---|---|---|---|
| Context Agent | references/01-context-brief.md | Uses the available context methodology to understand the project and turn vague ideas into executable goals | background/01_project_background.md, background/02_skill_list.md, AGENTS.md, optional knowledge/LOG.md |
| Commander | references/02-commander.md | Schedules ready batches, integrates information and knowledge deltas, requests human help, accepts evidence | Startup batches, continuation/recovery prompts, knowledge audit/closeout |
| Executor | references/03-executor.md | Completes the assigned contract and delivers | task-output/01_task_name/ or concise inline result for independent Fast Lane |
| Reviewer | references/04-reviewer.md | Spec compliance, completeness, risk and data review; reviews only, never modifies | 04_review_findings.md |
| QA | references/05-qa.md | Standards/behavior verification, recomputes figures, checks links and sources | 05_qa_validation.md |
| Risk Manager | references/08-risk-manager.md | Identifies project risks | risk-register.md |
| Decision Manager | references/09-decision-manager.md | Analyzes major direction options; waits for the user's final decision | 09_decision_analysis.md |
| Backup Manager | references/14-backup-manager.md | Creates and verifies recovery artifacts before risky work | Backup manifest, verification and recovery receipt |

## Execution modes

Use `references/19-task-routing.md` at intake or changed scope/risk. Fast Lane serves independent eligible requests; Lean keeps project records with reduced coordination overhead; Standard follows the project workflow below. Modes preserve roles, permissions and required verification. The directory/brief conventions below apply to project tasks; independent Fast Lane uses its bounded inline contract and result.

## Standard workflow

1. Context Agent builds background, terms, available skills and collaboration preferences, then emits a complete Commander handoff and stops. The current window does not automatically switch roles.
2. The user opens a Commander window with that handoff. Commander reads current records, asks for missing user-held facts, assesses backups and chooses a ready batch of independent tasks.
3. Commander outputs separately copyable prompts for the batch. Each primary task has its own persistent window; authorized subagents may help internally. If the host cannot dispatch windows, the user relays prompts and receipts.
4. Executor delivers versioned evidence and information deltas. Commander applies risk-based Reviewer/QA gates on separate Spec and Standards/behavior axes, reuses valid checks, integrates shared changes and sends targeted synchronization prompts.
5. Same-scope fixes and coherent remaining work return together as a natural-language continuation to the original window. Keep the full task objective and genuine user corrections in view rather than stopping at the latest detail. Lost windows receive recovery prompts. Choose continue/fresh/handoff/subagent/compaction at a phase boundary per `references/21-window-boundaries.md`, not by habit. Hard problems may use budgeted isolated alternative experiments rather than endless revisions.
6. Backup Manager verifies required recovery points before dependent risky actions. The user can supply knowledge, local browser actions and judgments throughout, not just carry prompts.
7. Major direction choices go to Decision Manager when useful; the user decides and Commander records the confirmed conclusion in `decision-log.md`.
8. When the project produces durable conclusions, maintain the optional knowledge layer: short `knowledge/LOG.md` entries, current-truth topic notes, audit at milestones, branch/experiment closure and human-confirmed graduation candidates. After completion, offer an environment-focused retro.

Task status follows `references/11-task-state-machine.md`; skill discovery follows `references/12-skill-discovery.md`. Collaboration/permissions/windows/synchronization follow `references/15-collaboration.md`; gate effort and stopping rules follow `references/16-quality-gates.md`. Context Agent generates or reconciles root `AGENTS.md` from confirmed project-specific rules for all AI agents.

## Directory and numbering conventions

- `background/` — context background documents, skill inventory, and pending questionnaires
- `AGENTS.md` — concise project-level behavioral rules and navigation for all AI agents, generated or reconciled from confirmed constraints during context building
- `knowledge/` — optional durable knowledge layer: `LOG.md` timeline, `topics/` current truth, optional `ROADMAP.md`, `Cited.md` and raw `Reference/`; see `references/20-knowledge-layer.md`
- Task outputs live in: `task-output/`
- Task ids start at `01`, e.g. `task-output/01_task_name/`
- Review and QA outputs go into the same task directory: `04_review_findings.md`, `05_qa_validation.md`; preserve revision evidence/history.
- Project status, decision log, task receipts and knowledge topics have distinct source-of-truth roles; do not duplicate current task state or confirmed decisions in knowledge notes.
- Durable receipts/checkpoints use `templates/task-receipt.md`; continuation/recovery prompts use `templates/task-continuation.md`.

## Task prompt specification

`references/06-task-template.md` owns prompt composition and contract completeness.
For project tasks, save coordination metadata in the task brief; send natural outcome-first instructions
with essential pointers and operative constraints, not a mandatory field form.
Shape each task as a vertical, demoable slice that fits a fresh window and declares its blocking edges; avoid layer-only or per-file microtasks.
The saved contract preserves Reviewer/QA gates and full scope. State updates follow
`references/11-task-state-machine.md`; a shorter message never waives its requirements.

## Agent dispatch rules

The Commander can call the matching agent by task type.
Dispatch principles:
1. One task calls exactly one primary execution agent.
2. Reviewer and QA never create; they only check. Reviewer owns the Spec axis; QA owns the Standards/behavior axis; report them separately.
3. Risk Manager steps in early for high-uncertainty tasks.
4. Decision Manager only analyzes major direction choices; it never makes the final decision for the user.
5. Backup Manager protects recoverability; required backup verification precedes dependent mutation. Other safe work can run meanwhile.
6. Commander integrates shared knowledge deltas after checking evidence; other roles do not write central knowledge records concurrently.
7. Task scope is bounded, but a task can span many conversation turns. Roles stay fixed unless the user explicitly changes them.

Agent capabilities:
Read `templates/agent-registry.md` in the Skill root.

## Hard compliance boundaries

- When requirements are vague, ask for background first; never guess.
