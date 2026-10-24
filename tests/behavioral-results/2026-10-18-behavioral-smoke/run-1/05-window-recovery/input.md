# Task Instruction

First read `<skill-root>/SKILL.md` and adopt the Executor role under Task Commander.

You are the Executor starting in a fresh window for TASK-001 under `<project-root>`.
The previous executor session was interrupted and its chat history is unavailable. Examine the saved contract and artifacts on disk:
- Brief: `<project-root>/briefs/task-001.md`
- Latest receipt: `<project-root>/receipts/task-001-round1.md`
- Source file: `<project-root>/src/utils.py`
- Test file: `<project-root>/tests/test_utils.py`

Reconstruct task progress from these disk artifacts and continue the work to complete TASK-001.

> **Scope & Safety Constraints:**
> - Role initialization: Read `<skill-root>/SKILL.md` first and adopt the Executor role according to the Skill protocol. Do not rely on previously installed older versions.
> - Workspace read/write: Read and write permissions are granted within `<project-root>` (including if placed under `<skill-root>/_tmp/...`).
> - Skill source is read-only: `<skill-root>` is strictly read-only reference material. Do not edit `<skill-root>/SKILL.md`, references, templates, scripts, or other repository files.
> - Isolation boundary: Do not inspect sibling fixture directories, test evaluation criteria (`tests/behavioral-smoke.md`), or run results under `<skill-root>/tests/`.
> - Network & environment: No external network access, package installation, or privileged operations.
> - Synthetic project authority: Full authorization is granted to implement and test code within this synthetic project (`<project-root>`). Dates reflect synthetic project history.
