# Task Startup Prompt

> Commander fills one independently copyable prompt per ready task. A reply may contain a batch of these prompts; each retains one primary owner and a bounded objective. For an existing task window, use `templates/task-continuation.md` instead. Resolve all path placeholders before sending.

```text
[Mode] Start
[Task id / target window] <01_task_name / human-readable window label>
[Priority / kind / risk] <P0-P3 / delivery or exploration / low, standard or high>
[Primary role] <Executor / Reviewer / QA / Risk Manager / Decision Manager / Backup Manager>
[Why this task] <value and why it is ready now>

[Contract and context]
Project root: <absolute path>
Original brief location: <absolute task-local path; save this contract there before execution>
Shared context revision and relevant input versions: <revision plus precise input pointers>
Must read:
- <absolute primary-role file path in this Skill>
- <absolute Skill root>/references/15-collaboration.md
- <absolute Skill root>/references/11-task-state-machine.md
- <absolute project root>/background/01_project_background.md
- <absolute project root>/background/02_skill_list.md
- <absolute project root>/project-status.md
- <only relevant terms, decisions, upstream artifacts and acceptance evidence>
Conditional reads:
- Before file/CLI work: <absolute Skill root>/references/runtime.md; follow its recovery rules on error/uncertainty.
- When selecting or applying acceptance checks/experiments: <absolute Skill root>/references/16-quality-gates.md.
- When recovery risk or backup work applies: <absolute Skill root>/references/14-backup-manager.md.

[Dependencies and parallel contract]
Prerequisites: <satisfied tasks and evidence, or none>
Parallel-safe: <yes/no and reason; batch companions if any>
Read scope: <files/data/services/browser sessions and stable input versions>
Write scope: <exclusive files/directories/resources; central records remain Commander-owned>
Isolation and integration owner: <workspace/snapshot and owner, or not applicable>
Backup prerequisite: <verified recovery artifact covering current inputs / required task / not needed with reason>
User contribution: <question/action and expected return, or none; identify what waits>

[Effective tools and budget]
Policy source: <absolute project background path and section>
Network: <public read-only research allowed / restriction and concrete reason>
Sources/freshness: <source requirements and cutoff if relevant>
Skills/plugins: <available selected names and absolute entry paths>
Subagents: <allowed with bounded scope/count / restriction and concrete reason>
Model policy: parent model by default; changes require explicit authorization and host support.
Resource/time budget and stop condition: <task-appropriate bounds>
Sensitive transfer, payment, publishing, deployment and destructive actions need applicable explicit authorization; inherited research permission does not authorize them.

[Work]
<Goal, scope, expected deliverable; 2-5 sentences. For exploration include the question/hypothesis, comparison criteria and isolated experiment plan.>

[Quality gates]
Reviewer: <required/not required and risk-based reason>
QA: <required/not required and risk-based reason>
Acceptance criteria: <small numbered list of observable requirements, no unrelated polish>
Evidence: <checks, source or runtime requirements, version identity and paths>
Revision budget: <inherit project policy or justified exception; exhaustion means replan, not pass>
Compliance: <specific security/privacy/copyright/domain boundaries or relevant background section>

[Output and handback]
Task directory: <absolute project root>/task-output/<task id_task name>/
Deliverable: <concrete files, commonly 01_result.md>
Gate briefs use distinct names (04_review_brief.md, 05_qa_brief.md) so they never overwrite the execution brief or deliverable; details in `references/15-collaboration.md`.
Review/QA reports when required: 04_review_findings.md / 05_qa_validation.md (preserve revision evidence)
Return a concise receipt using <absolute Skill root>/templates/task-receipt.md, including context acknowledgment, evidence, shared-information delta and pending human actions.
Suggested next state: <legal state matching gates, never self-assign Completed>
Remain available in this task window for clarification and targeted revision. Do not switch roles or edit project-status.md.
```

## Pre-dispatch checklist

1. Each prompt has its own ID, target window, primary role, goal, absolute paths, and saved brief location.
2. Prerequisites are actually satisfied; writes, input mutations, browser/services and integration ownership are conflict-checked against active tasks.
3. Required recovery point is verified before risky mutation. A pending backup means dispatch the backup task first, not runnable dependent work.
4. Effective tools inherit the project policy; restrictions have a reason, capability is real, and human help is requested where useful.
5. Acceptance criteria, required gates, budgets, and evidence are risk-proportionate; exploration failure is distinguished from implementation failure.
6. Input revision and receipt/continuation conventions are supplied. A new prompt does not imply confirmed pickup by another window.
7. Reviewer/QA tasks name the reviewed task ID and artifact version, keep gate briefs in separate files, and record the gate window without creating a duplicate deliverable row.
