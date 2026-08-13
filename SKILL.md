---
name: task-commander
description: Multi-model task orchestration system. Use when the user needs context building, task breakdown, cross-conversation dispatch, execution, review, QA, risk analysis, or major decision collaboration; also used to generate single-task prompts that can be copied into other chat windows.
---

# Task Commander

## Core flow

1. Read `references/00-overview.md` to learn the roles, directories, and numbering conventions.
2. Decide the execution type:
   - When you will write or delete files, run a CLI or script, or produce a deliverable, read `references/runtime.md` first.
   - When a file write, CLI, or verification command errors, produces no output, times out, or is uncertain, verify and retry per the "Command result verification" and "Error recovery" sections of `references/runtime.md`.
   - When the work is pure interviewing, planning, review explanation, read-only analysis of user-provided content, or generating prompts that do not land on disk, and runs no CLI or script, skip that reference.
3. Determine the project root: prefer the directory the user specifies; otherwise use the current workspace root; when several candidate projects exist and it cannot be determined, confirm first.
4. Read or initialize `<Project Root>/project-status.md`:
   - First read `references/11-task-state-machine.md`; validate an existing status file with `scripts/validate-project-state.py`, and initialize from `templates/project-status.md`.
   - After context building, set the project phase to `Planning`. After initialization, only the Commander writes the status file; other roles submit evidence and suggested states only.
5. When the project lacks background documents, read `references/10-context-orchestration.md` and `references/01-context-brief.md`, and compose `writing-for-agents`, `grill-with-docs`, `wait-what`, and `to-questionnaire` (use each if present; otherwise use the built-in fallback `references/methodology-fallback.md`).
6. Once the context meets the breakdown bar, read `references/02-commander.md`, `references/06-task-template.md`, and `references/11-task-state-machine.md`, then break down and dispatch tasks:
   - Every prompt must include the task id, must-read files as absolute paths, the output directory, network requirements, Skill/plugin and subagent permissions, Reviewer/QA gates, acceptance criteria, and compliance prerequisites.
   - When subagents are allowed, note they inherit the parent model and must not switch models.
   - Output one task prompt at a time; only when a task is explicitly marked parallel-safe and the user asks for more, output the next one, still a single task per reply.
7. When a task enters execution, review, QA, risk, or decision analysis, read the matching role entry as needed: `references/03-executor.md`, `references/04-reviewer.md`, `references/05-qa.md`, `references/08-risk-manager.md`, or `references/09-decision-manager.md`.
8. When a task involves acceptance or comparison scripts, additionally read `references/07-verification-guidelines.md`.
9. When generating a skill list, read `references/12-skill-discovery.md`, run `scripts/scan-skills.py` to scan only frontmatter, dedupe, and filter candidates, then read the candidate Skill bodies.
10. Throughout, obey the source-of-truth boundaries in `references/10-context-orchestration.md` and the state transitions in `references/11-task-state-machine.md`; never fabricate data, context, or decisions; for anything unconfirmed, record the owner, the gap, and the next step.
11. This Skill is offline by default. When external information, network access, plugins, Skills, or subagents are needed, declare them explicitly in the task prompt; time-sensitive information also notes its source and date.

## Entry navigation

- Overview and workflow: `references/00-overview.md`
- Context orchestration: `references/10-context-orchestration.md`
- Context interview: `references/01-context-brief.md`
- Commander: `references/02-commander.md`
- Execution: `references/03-executor.md`
- Review: `references/04-reviewer.md`
- QA: `references/05-qa.md`
- Task template: `references/06-task-template.md`
- Verification rules: `references/07-verification-guidelines.md`
- Risk management: `references/08-risk-manager.md`
- Decision management: `references/09-decision-manager.md`
- Task state machine: `references/11-task-state-machine.md`
- Skill discovery: `references/12-skill-discovery.md`
- Cross-platform host execution principles; read only before writing files or running CLIs: `references/runtime.md`
- Built-in methodology fallback (when the composed skills are absent): `references/methodology-fallback.md`
- Project status template: `templates/project-status.md`
- Agent registry: `templates/agent-registry.md`
- Decision log template: `templates/decision-log.md`
- State specification: `templates/task-state-spec.txt`
- State validation: `scripts/validate-project-state.py`
- Skill scanning: `scripts/scan-skills.py`