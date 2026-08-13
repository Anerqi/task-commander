# Task Prompt Template (filled in by the Commander)

> Every dispatch uses this template to generate the complete prompt; do not drop any required field except "fill-in" items.
> Before dispatching, replace the Skill-root placeholder paths in [Conditional must-read] with resolved absolute paths; never load them as ordinary must-read files, never keep placeholder text in the final prompt, and do not copy this filling note.

---

## Single-task prompt (copy everything below to the target agent)

```text
You are the target agent assigned to this task. First read the files in [Role rules] below, then execute strictly per the task brief; if [Execution agent] contradicts the role rules, stop immediately and report.

[Task id] 01_task_name

[Task priority]
P0/P1/P2/P3

[Task dependency]
Prerequisites:
- None
Or:
- task 01

[Parallel-safe]
Yes / No

[Quality gates]
- Reviewer: required / not required; reason:
- QA: required / not required; reason:

[Execution agent]
Executor / Reviewer / QA / Risk Manager / Decision Manager

[Call reason]
Why this agent was chosen

[Role rules]
- Fill in the absolute path of the role file matching the target agent in the task-commander Skill
- Executor: references/03-executor.md
- Reviewer: references/04-reviewer.md
- QA: references/05-qa.md
- Risk Manager: references/08-risk-manager.md
- Decision Manager: references/09-decision-manager.md

[Must-read files]
- Task Commander Skill root/references/11-task-state-machine.md
- Project root/background/01_project_background.md
- Project root/background/02_skill_list.md
- Project root/project-status.md
- (other task-related files, per the Commander's fill-in)

[Conditional must-read]
- Before writing or deleting files, running a CLI or script, or producing a deliverable: Task Commander Skill root/references/runtime.md
- When a file write, CLI, or verification command errors, produces no output, times out, or is uncertain: verify and retry per the "Command result verification" and "Error recovery" sections of Task Commander Skill root/references/runtime.md
- When the work is pure interviewing, planning, review explanation, read-only analysis of user-provided content, or generating prompts that do not land on disk, and runs no CLI or script: do not load Task Commander Skill root/references/runtime.md.

[Output location]
- Project root/task-output/01_task_name/
- Deliverable file: 01_result.md
- Review file (if needed): 04_review_findings.md
- QA file (if needed): 05_qa_validation.md

[Network and tools]
- Network: required / not required
- Data source requirement: name the sites and the cutoff time
- Plugins/Skills: list by skill name (e.g. writing-for-agents; path info in `background/02_skill_list.md`)
- Subagent: allowed / not allowed; when allowed, must note "the subagent must inherit the parent model and must not switch models"

[Task content]
<The Commander writes 2-5 sentences here: goal, scope, output.>

[Compliance prerequisites]
<State the security, privacy, copyright, industry, or decision boundaries this task must obey; when there are no special requirements, write "obey all constraints in the background documents and role rules".>

[Acceptance criteria]
1. <verifiable criterion 1>
2. <verifiable criterion 2>
3. <verifiable criterion 3>

[Suggested state after completion]
<In Review / QA Pending / Awaiting Acceptance; must match the quality gates; never write Completed>

```

## Pre-dispatch checklist

1. Do the task id and output directory carry 01/02 numbering?
2. Are all must-read files absolute paths?
3. Do the role rules match the execution agent, with absolute paths?
4. Is network required/not required stated explicitly?
5. Are skills/plugins/subagent stated explicitly?
6. Are there 3-5 verifiable acceptance criteria?
7. Is the compliance prerequisites section present?
8. Do the Reviewer/QA gates and the suggested completion state match?
9. Is the host-execution reference (runtime.md) in conditional must-read as an absolute path, and kept on-demand?

## Task dependency

This task depends on:
- None
Or:
- Runs after task 01 completes