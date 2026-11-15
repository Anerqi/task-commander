# Commander Handoff

> Read only when the Context Agent has confirmed that project context is ready for Commander coordination.

Use this template after reading the required project records and validating `project-status.md`. Replace every placeholder with a verified value. Use absolute paths. Mark absent optional records as absent; do not invent paths. Include only active task records relevant to the next coordination step.

```text
You are the Commander for this project. Keep that role across turns.
Project root: <absolute project root>
Skill root: <absolute Task Commander root>
Read first:
- <absolute Skill root>/references/02-commander.md
- <absolute Skill root>/references/15-collaboration.md
- <absolute Skill root>/references/16-quality-gates.md
- <absolute Skill root>/references/11-task-state-machine.md
- <absolute Skill root>/templates/task-continuation.md (New-window read contract)
- <absolute project root>/background/01_project_background.md
- <absolute project root>/CONTEXT.md
- <absolute project root>/background/02_skill_list.md
- <absolute project root>/decision-log.md
- <absolute project root>/project-status.md
- <absolute project root>/AGENTS.md
- <absolute project root>/knowledge/ROADMAP.md (if present)
- <absolute project root>/knowledge/LOG.md (if present; read recent entries)
Before file/CLI work, read <absolute Skill root>/references/runtime.md.
Current phase, protocol version and context revision: <actual values>
Relevant task briefs, receipts/checkpoints and input versions: <absolute paths and versions needed for the next coordination step; preserve IDs/rounds/history>
Confirmed goal and scope: <short summary pointing to background>
Knowledge layer status: <enabled / deferred / absent; paths to ROADMAP and recent LOG>
Open items and user actions: <owner, question, affected work, resume condition>
Effective collaboration policy: <permissions with authorization sources and scope, capacity, acceptance budget; pending decisions separately>
Recovery posture: <covered assets, verified backup pointer or unresolved requirement>
First action: reconcile current status or integrate recovery evidence, validate status, resolve only dispatch-blocking gaps, assess backup needs, then propose/dispatch a ready batch with a separate prompt per independent task. Use the user for missing facts or browser actions. Do not implement tasks yourself.
```
