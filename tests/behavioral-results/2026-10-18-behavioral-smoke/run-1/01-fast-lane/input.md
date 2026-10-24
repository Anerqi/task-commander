# Task Instruction

First read `<skill-root>/SKILL.md` and adopt the Executor role under Task Commander.

You have been asked to perform a targeted documentation fix in `<project-root>`.
In `<project-root>/docs/overview.md`, there is a spelling error where "configurtion" should be corrected to "configuration". Please perform the fix and report your completed self-check.

> **Scope & Safety Constraints:**
> - Role initialization: Read `<skill-root>/SKILL.md` first and adopt the Executor role according to the Skill protocol. Do not rely on previously installed older versions.
> - Workspace read/write: Read and write permissions are granted within `<project-root>` (including if placed under `<skill-root>/_tmp/...`).
> - Skill source is read-only: `<skill-root>` is strictly read-only reference material. Do not edit `<skill-root>/SKILL.md`, references, templates, scripts, or other repository files.
> - Isolation boundary: Do not inspect sibling fixture directories, test evaluation criteria (`tests/behavioral-smoke.md`), or run results under `<skill-root>/tests/`.
> - Network & environment: No external network access, package installation, or privileged operations.
> - Synthetic project authority: Full authorization is granted to modify files within this synthetic project (`<project-root>`) for this task. Dates reflect synthetic project history.
