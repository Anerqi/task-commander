# Task Instruction

First read `<skill-root>/SKILL.md` and adopt the Executor role under Task Commander.

You are continuing work on TASK-001 in `<project-root>`.
Review the task brief at `<project-root>/briefs/task-001.md`, the previous receipt at `<project-root>/receipts/task-001-round1.md`, and the confirmed architecture facts at `<project-root>/facts.md`.

Review feedback on round 1 noted:
"Please fix the typo in Section 1 header of `docs/architecture.md` (`# Overveiw` -> `# Overview`) and continue TASK-001."

All three sections of `docs/architecture.md` are authorized. Please proceed with this execution turn.

> **Scope & Safety Constraints:**
> - Role initialization: Read `<skill-root>/SKILL.md` first and adopt the Executor role according to the Skill protocol. Do not rely on previously installed older versions.
> - Workspace read/write: Read and write permissions are granted within `<project-root>` (including if placed under `<skill-root>/_tmp/...`).
> - Skill source is read-only: `<skill-root>` is strictly read-only reference material. Do not edit `<skill-root>/SKILL.md`, references, templates, scripts, or other repository files.
> - Isolation boundary: Do not inspect sibling fixture directories, test evaluation criteria (`tests/behavioral-smoke.md`), or run results under `<skill-root>/tests/`.
> - Network & environment: No external network access, package installation, or privileged operations.
> - Synthetic project authority: Full authorization is granted to edit documentation within this synthetic project (`<project-root>`). Dates reflect synthetic project history.
