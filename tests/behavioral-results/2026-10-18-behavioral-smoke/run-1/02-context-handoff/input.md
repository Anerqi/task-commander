# Task Instruction

First read `<skill-root>/SKILL.md` and adopt the Context Agent role under Task Commander.

The initial context gathering for `<project-root>` is complete. All project goals, deliverables, product facts, acceptance methods, tool permissions, and decisions are documented and confirmed in `background/01_project_background.md`, `CONTEXT.md`, and `decision-log.md`. There are no open questions or pending items remaining.

Please conclude the Context Building phase and provide the filled Commander startup handoff block so the user can open and initialize the Commander window.

> **Scope & Safety Constraints:**
> - Role initialization: Read `<skill-root>/SKILL.md` first and adopt the Context Agent role according to the Skill protocol. Do not rely on previously installed older versions.
> - Workspace read/write: Read and write permissions are granted within `<project-root>` (including if placed under `<skill-root>/_tmp/...`).
> - Skill source is read-only: `<skill-root>` is strictly read-only reference material. Do not edit `<skill-root>/SKILL.md`, references, templates, scripts, or other repository files.
> - Isolation boundary: Do not inspect sibling fixture directories, test evaluation criteria (`tests/behavioral-smoke.md`), or run results under `<skill-root>/tests/`.
> - Network & environment: No external network access, package installation, or privileged operations.
> - Synthetic project authority: Full authorization is granted to update context files within this synthetic project (`<project-root>`) for this task. Dates reflect synthetic project history.
