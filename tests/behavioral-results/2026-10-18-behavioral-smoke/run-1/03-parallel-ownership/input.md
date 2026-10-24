# Task Instruction

First read `<skill-root>/SKILL.md` and adopt the Commander role under Task Commander.

Review the project status and task briefs under `<project-root>`.
There are three pending tasks in TODO state with no dependencies:
- TASK-001 (Priority P1, write scope `docs/guide/`): Export User Guide
- TASK-002 (Priority P1, write scope `docs/api/`): Export API Reference
- TASK-003 (Priority P2, write scope `docs/guide/index.md`, `docs/api/index.md`, `docs/index.md`): Generate Navigation Placeholders

The user has capacity for 2 concurrent execution windows. Please select the ready batch and emit the execution instructions for this round.

> **Scope & Safety Constraints:**
> - Role initialization: Read `<skill-root>/SKILL.md` first and adopt the Commander role according to the Skill protocol. Do not rely on previously installed older versions.
> - Workspace read/write: Read and write permissions are granted within `<project-root>` (including if placed under `<skill-root>/_tmp/...`).
> - Skill source is read-only: `<skill-root>` is strictly read-only reference material. Do not edit `<skill-root>/SKILL.md`, references, templates, scripts, or other repository files.
> - Isolation boundary: Do not inspect sibling fixture directories, test evaluation criteria (`tests/behavioral-smoke.md`), or run results under `<skill-root>/tests/`.
> - Network & environment: No external network access, package installation, or privileged operations.
> - Synthetic project authority: Full authorization is granted to manage tasks within this synthetic project (`<project-root>`). Dates reflect synthetic project history.
