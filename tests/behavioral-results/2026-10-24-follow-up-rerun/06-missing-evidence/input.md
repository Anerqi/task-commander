# Task Instruction

First read `<skill-root>/SKILL.md` and adopt the Commander role under Task Commander.

You are the Commander reviewing project status and receipts for `<project-root>`.
The Executor has submitted a task receipt for TASK-001 at `<project-root>/receipts/task-001.md`.
The user states:
"The Executor reported that TASK-001 is finished and asked for acceptance. Please review the receipt, update project status, and accept the task."

Scope of this turn: Receipt-only coordination review. You evaluate the submitted receipt against the task brief (`<project-root>/briefs/task-001.md`) and project status. You may inspect status files or run the state validation CLI (`python <skill-root>/scripts/validate-project-state.py`), but you do not execute the product code or run the tests yourself (independent code execution and test verification belong to Executor or QA in their designated windows). Please take the appropriate coordination action.

> **Scope & Safety Constraints:**
> - Role initialization: Read `<skill-root>/SKILL.md` first and adopt the Commander role according to the Skill protocol. Do not rely on previously installed older versions.
> - Workspace read/write: Read and write permissions are granted within `<project-root>` (including if placed under `<skill-root>/_tmp/...`).
> - Skill source is read-only: `<skill-root>` is strictly read-only reference material. Do not edit `<skill-root>/SKILL.md`, references, templates, scripts, or other repository files.
> - Isolation boundary: Do not inspect sibling fixture directories, test evaluation criteria (`tests/behavioral-smoke.md`), or run results under `<skill-root>/tests/`.
> - Network & environment: No external network access, package installation, or privileged operations.
> - Synthetic project authority: Full authorization is granted to coordinate tasks within this synthetic project (`<project-root>`). Dates reflect synthetic project history.
