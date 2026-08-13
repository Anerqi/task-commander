# Multi-Model Task Orchestration System - Overview

> A project is completed by multiple AI models working together; the Commander handles orchestration and dispatch, while context, execution, review, and QA are each carried by a specialized model.

## Role table

| Role | File | Responsibility | Main output |
|---|---|---|---|
| Context Agent | references/01-context-brief.md | Uses the available context methodology to understand the project and turn vague ideas into executable goals | background/01_project_background.md, background/02_skill_list.md |
| Commander | references/02-commander.md | Breaks down tasks, writes task prompts, reviews progress lightly, never executes hands-on | One task prompt at a time |
| Executor | references/03-executor.md | Completes a single task per the task brief and delivers | task-output/01_task_name/ |
| Reviewer | references/04-reviewer.md | Compliance, completeness, risk, and data review; reviews only, never modifies | 04_review_findings.md |
| QA | references/05-qa.md | Runs verification, recomputes figures, checks links and sources | 05_qa_validation.md |
| Risk Manager | references/08-risk-manager.md | Identifies project risks | risk-register.md |
| Decision Manager | references/09-decision-manager.md | Analyzes major direction options; waits for the user's final decision | 09_decision_analysis.md |

## Standard workflow

1. Dispatch "01 Context Agent" first: compose the four context skills per `references/10-context-orchestration.md`, interview and understand the project, and output the background documents, `CONTEXT.md`, and the skill list.
2. Then dispatch "02 Commander": the Commander reads the background documents and breaks the goal down into subtasks (01, 02, ...), outputting one task prompt at a time.
3. You copy the task prompt to "03 Executor".
4. After the Executor delivers, the Commander does a light verification; for deep review, sign "04 Reviewer" or "05 QA".
5. Change requests are merged by the Commander into new, small tasks and dispatched separately; never mix changes across tasks.
6. Major direction choices go to "Decision Manager" first; after the user confirms, the Commander appends the final decision to `decision-log.md`.

Project status follows `references/11-task-state-machine.md`; skill discovery follows `references/12-skill-discovery.md`.

## Directory and numbering conventions

- Background documents live in: `background/`
- Task outputs live in: `task-output/`
- Task ids start at `01`, e.g. `task-output/01_task_name/`
- Review and QA outputs go into the same task directory: `04_review_findings.md`, `05_qa_validation.md`

## Task prompt specification

Every generated task prompt must follow `references/06-task-template.md`, which
is the single source of truth for required fields and the pre-dispatch checklist.
Every task must also declare Reviewer and QA quality gates; status updates follow
`references/11-task-state-machine.md`.

## Agent dispatch rules

The Commander can call the matching agent by task type.
Dispatch principles:
1. One task calls exactly one primary execution agent.
2. Reviewer and QA never create; they only check.
3. Risk Manager steps in early for high-uncertainty tasks.
4. Decision Manager only analyzes major direction choices; it never makes the final decision for the user.

Agent capabilities:
Read `templates/agent-registry.md` in the Skill root.

## Hard compliance boundaries

- When requirements are vague, ask for background first; never guess.
