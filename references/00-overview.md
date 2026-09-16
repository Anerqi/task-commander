# Multi-Model Task Orchestration System - Overview

> A project is completed by multiple AI models working together; the Commander handles orchestration and dispatch, while context, execution, review, and QA are each carried by a specialized model.

## Role table

| Role | File | Responsibility | Main output |
|---|---|---|---|
| Context Agent | references/01-context-brief.md | Uses the available context methodology to understand the project and turn vague ideas into executable goals | background/01_project_background.md, background/02_skill_list.md |
| Commander | references/02-commander.md | Schedules ready batches, integrates information, requests human help, accepts evidence | Startup batches and continuation/recovery prompts |
| Executor | references/03-executor.md | Completes a single task per the task brief and delivers | task-output/01_task_name/ |
| Reviewer | references/04-reviewer.md | Compliance, completeness, risk, and data review; reviews only, never modifies | 04_review_findings.md |
| QA | references/05-qa.md | Runs verification, recomputes figures, checks links and sources | 05_qa_validation.md |
| Risk Manager | references/08-risk-manager.md | Identifies project risks | risk-register.md |
| Decision Manager | references/09-decision-manager.md | Analyzes major direction options; waits for the user's final decision | 09_decision_analysis.md |
| Backup Manager | references/14-backup-manager.md | Creates and verifies recovery artifacts before risky work | Backup manifest, verification and recovery receipt |

## Standard workflow

1. Context Agent builds background, terms, available skills and collaboration preferences, then emits a complete Commander handoff and stops. The current window does not automatically switch roles.
2. The user opens a Commander window with that handoff. Commander reads current records, asks for missing user-held facts, assesses backups and chooses a ready batch of independent tasks.
3. Commander outputs separately copyable prompts for the batch. Each primary task has its own persistent window; authorized subagents may help internally. If the host cannot dispatch windows, the user relays prompts and receipts.
4. Executor delivers versioned evidence and information deltas. Commander applies risk-based Reviewer/QA gates, reuses valid checks, integrates shared changes and sends targeted synchronization prompts.
5. Same-scope fixes and coherent remaining work return together as a natural-language continuation to the original window. Keep the full task objective and genuine user corrections in view rather than stopping at the latest detail. Lost windows receive recovery prompts. Hard problems may use budgeted isolated alternative experiments rather than endless revisions.
6. Backup Manager verifies required recovery points before dependent risky actions. The user can supply knowledge, local browser actions and judgments throughout, not just carry prompts.
7. Major direction choices go to Decision Manager when useful; the user decides and Commander records the confirmed conclusion in `decision-log.md`.

Project status follows `references/11-task-state-machine.md`; skill discovery follows `references/12-skill-discovery.md`. Collaboration/permissions/windows/synchronization follow `references/15-collaboration.md`; gate effort and stopping rules follow `references/16-quality-gates.md`.

## Directory and numbering conventions

- Background documents live in: `background/`
- Task outputs live in: `task-output/`
- Task ids start at `01`, e.g. `task-output/01_task_name/`
- Review and QA outputs go into the same task directory: `04_review_findings.md`, `05_qa_validation.md`; preserve revision evidence/history.
- Durable receipts/checkpoints use `templates/task-receipt.md`; continuation/recovery prompts use `templates/task-continuation.md`.

## Task prompt specification

`references/06-task-template.md` owns prompt composition and contract completeness.
Save coordination metadata in the task brief; send natural outcome-first instructions
with essential pointers and operative constraints, not a mandatory field form.
The saved contract preserves Reviewer/QA gates and full scope. State updates follow
`references/11-task-state-machine.md`; a shorter message never waives its requirements.

## Agent dispatch rules

The Commander can call the matching agent by task type.
Dispatch principles:
1. One task calls exactly one primary execution agent.
2. Reviewer and QA never create; they only check.
3. Risk Manager steps in early for high-uncertainty tasks.
4. Decision Manager only analyzes major direction choices; it never makes the final decision for the user.
5. Backup Manager protects recoverability; required backup verification precedes dependent mutation. Other safe work can run meanwhile.
6. Task scope is bounded, but a task can span many conversation turns. Roles stay fixed unless the user explicitly changes them.

Agent capabilities:
Read `templates/agent-registry.md` in the Skill root.

## Hard compliance boundaries

- When requirements are vague, ask for background first; never guess.
