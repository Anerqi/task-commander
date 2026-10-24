# First Project Walkthrough: Multi-Window Documentation Sprint

> **Notice:** All sample receipts, state updates, and verdicts below are illustrative walkthrough samples for training, not genuine project authorizations or executed runtime evidence.
> **Operational model:** Task Commander operates across fixed-role windows routed manually by the user. There is no automated message bus, background daemon, or automatic role switching.
> **Authoritative references:** `references/00-overview.md`, `references/01-context-brief.md`, `references/02-commander.md`, `references/06-task-template.md`, `references/11-task-state-machine.md`, `references/16-quality-gates.md`, `references/19-task-routing.md`, `templates/task-receipt.md`, `templates/task-continuation.md`.

## Setup: Disposable Workspace & Fixed Product Facts

Create an empty disposable directory using your file manager, terminal, or PowerShell.
Record its absolute path as `<project-root>`, and record the Task Commander repository path as `<skill-root>`.

This walkthrough builds two non-conflicting documents for a fictional markdown linter, **MiniDoc** v1.0.0 (pure documentation; no installation or execution needed).
**Fixed Product Facts & All Acceptance Criteria:**
- **Product:** MiniDoc v1.0.0. Syntax: `minidoc check <path>` and `minidoc build <dir>`.
- **System Prerequisites:** Python 3.10+ and Git 2.30+.
- **Exit Codes:** 0 = success, 1 = markdown syntax violation, 2 = broken relative link, 3 = configuration error, 4 = file unreadable.
- **Deliverable 1 (`docs/quickstart.md` criteria):** Must contain (1) Prerequisites (Python 3.10+, Git 2.30+), (2) Installation (state that this fictional exercise has no package to install), and (3) First Run (show `minidoc check README.md` as an illustrative command, not an executable instruction).
- **Deliverable 2 (`docs/troubleshooting.md` criteria):** Must contain an Exit Code Reference table defining codes 0 through 4 with concrete remediation steps for each.

---

## Step 1: Context Initialization (Window 1)

Open **Window 1** as the dedicated Context Agent (`references/01-context-brief.md`).

**Copy to Window 1:**
```text
You are the Context Agent. Read <skill-root>/SKILL.md and its Context branch.
Project root: <project-root> (a new, empty disposable directory).
Confirmed facts: MiniDoc v1.0.0 is fictional. Its documented prerequisites are Python 3.10+ and Git 2.30+; illustrative syntax is minidoc check <path> and minidoc build <dir>. There is no package to install or product command to execute.
Exit codes: 0 success; 1 Markdown syntax violation; 2 broken relative link; 3 configuration error; 4 unreadable file.
Audience: first-time users. Write two English documents:
- docs/quickstart.md: prerequisites, a no-installation disclaimer, and illustrative first run minidoc check README.md.
- docs/troubleshooting.md: codes 0-4 with concrete remediation or, for success, the next normal step.
Project acceptance: both documents cover these facts and agree on terminology and commands.
I authorize only local documentation/coordination writes inside this disposable project and read-only access to the Skill. No network, package installation, or real product execution. No valuable existing assets; preserve drafts for any revisions. Capacity: two execution windows. Prefer Lean with documented risk-based gates, up to two targeted revision rounds; ask only about material missing facts.
Produce protocol context files, confirm any additional proposed project rules with me, then emit the filled Commander handoff.
```

- **Expected artifacts:** `<project-root>/background/01_project_background.md`, `<project-root>/background/02_skill_list.md`, `<project-root>/CONTEXT.md`, `<project-root>/decision-log.md`, `<project-root>/AGENTS.md`, `<project-root>/project-status.md` (phase: `Planning`), and handoff text.
- **Stage exit:** Window 1 outputs the Commander handoff prompt. Window 1 remains idle for context queries.

---

## Step 2: Task Planning & Dispatch (Window 2)

Open **Window 2** as the dedicated Commander (`references/02-commander.md`).

**First paste Window 1's actual filled handoff into Window 2, then append:**
```text
Read <skill-root>/SKILL.md, then follow references/02-commander.md.
Project root: <project-root>
Adopt Context handoff from Window 1. Register two tasks in project-status.md while keeping project phase in Planning:
- TASK-001: docs/quickstart.md | Status: TODO | Reviewer: No | QA: No | Exemption reason: Low-risk, reversible static documentation; no code, installation or product execution. Preserve Executor self-check and Commander light acceptance per references/16-quality-gates.md and references/19-task-routing.md.
- TASK-002: docs/troubleshooting.md | Status: TODO | Reviewer: No | QA: No | Exemption reason: Same scoped low-risk documentation exemption.
Save task briefs under <project-root>/briefs/ and compose complete outcome-first dispatch prompts per references/06-task-template.md.
```

- **Protocol rule:** Emitting dispatch prompts leaves tasks in `TODO` and project in `Planning`. A task enters `In Progress` only upon actual pickup confirmation by an Executor.
- **Stage exit:** Commander saves briefs and outputs complete dispatch prompts for Windows 3 and 4.

---

## Step 3: Parallel Execution (Windows 3 & 4)

Open two independent executor windows. Paste each **complete Commander-generated dispatch prompt**, including its saved brief and operative constraints, into the matching window. The excerpts below illustrate essential pointers; do not substitute them for the full assignment. Relay actual pickup confirmations and receipts back to Commander—windows do not see each other's messages.

### Window 3: Executor 1 (`TASK-001`)
**Dispatch excerpt for Window 3:**
```text
Read <skill-root>/SKILL.md, then execute TASK-001.
Project root: <project-root> | Task brief: <project-root>/briefs/task-001.md
Scope: Create docs/quickstart.md for MiniDoc v1.0.0 covering Prerequisites (Python 3.10+, Git 2.30+), Installation, and First Run per brief criteria. Return deliverable and receipt per <skill-root>/templates/task-receipt.md.
```
- **Pickup:** When Executor 1 acknowledges start, Commander updates `TASK-001` to `In Progress` in `project-status.md`; project phase enters `In Progress`.
- **Hypothetical Defect Scenario:** To demonstrate revision flow, assume Executor 1 produces an initial draft omitting prerequisites. Because requirements are unfulfilled, a partial receipt cannot suggest acceptance:
  ```text
  [SAMPLE RECEIPT - ILLUSTRATIVE]
  Task ID: TASK-001 | Round: Initial | Primary role: Executor 1 | Window: Window 3
  Deliverable: docs/quickstart.md
  Self-check: Installation and First Run documented. Omitted: Prerequisites section.
  Suggested state: In Progress (incomplete draft)
  ```

### Window 4: Executor 2 (`TASK-002`)
**Dispatch excerpt for Window 4:**
```text
Read <skill-root>/SKILL.md, then execute TASK-002.
Project root: <project-root> | Task brief: <project-root>/briefs/task-002.md
Scope: Create docs/troubleshooting.md for MiniDoc v1.0.0 covering exit codes 0-4 and concrete remediation per brief criteria. Return deliverable and receipt per <skill-root>/templates/task-receipt.md.
```
- **Pickup:** When Executor 2 acknowledges start, Commander marks `TASK-002` as `In Progress`.
- **Sample Receipt (Illustration only):**
  ```text
  [SAMPLE RECEIPT - ILLUSTRATIVE]
  Task ID: TASK-002 | Round: Initial | Primary role: Executor 2 | Window: Window 4
  Deliverable: docs/troubleshooting.md
  Self-check: Exit codes 0-4 defined with remediation. Criteria satisfied.
  Suggested state: Awaiting Acceptance (waived Reviewer/QA; Commander light acceptance)
  ```
- **Stage exit:** Both deliverables exist on disk; both executors return receipts.

---

## Step 4: Same-Task Revision (Window 2 -> Window 3)

The Commander inspects disk files and receipts against acceptance criteria.
*Note:* If in your actual run Executor 1 already included prerequisites, verify it and skip this revision step—do not reject valid work.

**Copy to Window 2 (Conditional evaluation):**
```text
Inspect <project-root>/docs/troubleshooting.md and <project-root>/docs/quickstart.md on disk:
- If docs/troubleshooting.md satisfies criteria, transition TASK-002: In Progress -> Awaiting Acceptance -> Completed.
- If docs/quickstart.md omits Prerequisites, record TASK-001 as Needs Revision (Finding: Missing Python 3.10+ and Git 2.30+ prerequisites). Compose continuation prompt for round R1 per <skill-root>/templates/task-continuation.md.
Update project-status.md accordingly.
```

**Copy Commander continuation prompt back to existing Window 3 (Executor 1):**
```text
Read <skill-root>/SKILL.md. Continue TASK-001 for round R1.
Task ID remains TASK-001 (Round: R1). Brief: <project-root>/briefs/task-001.md.
Delta: In <project-root>/docs/quickstart.md, add Prerequisites section (Python 3.10+ and Git 2.30+). Preserve existing sections. Return updated receipt per <skill-root>/templates/task-receipt.md.
```

- **Pickup:** When Window 3 resumes work, Commander updates `TASK-001` in `project-status.md`: `Needs Revision` -> `In Progress`.
- Window 3 completes the file and emits revision receipt:
  ```text
  [SAMPLE RECEIPT - ILLUSTRATIVE]
  Task ID: TASK-001 | Round: R1 | Primary role: Executor 1 | Window: Window 3
  Deliverable: docs/quickstart.md
  Self-check: Added Prerequisites section; all criteria satisfied.
  Suggested state: Awaiting Acceptance
  ```
- **Stage exit:** Revision saved; Window 3 emits R1 receipt suggesting `Awaiting Acceptance`.

---

## Step 5: Evidence-Based Acceptance & Project Completion (Window 2)

Per `references/11-task-state-machine.md` and `references/16-quality-gates.md`, Commander verifies actual disk evidence. Transitions cannot skip `Awaiting Acceptance` or project-level acceptance checks.

**Copy to Window 2 (Conditional verification & project completion):**
```text
Inspect <project-root>/docs/quickstart.md on disk:
- Read the latest recorded task state. If all criteria and the actual receipt are verified, record the legal path through Awaiting Acceptance to Completed (normally In Progress -> Awaiting Acceptance -> Completed after R1). Validate each proposed transition before writing, preserve history, and reconcile any unexpected current state instead of inventing a predecessor.
- Check project status: With all delivery tasks Completed, transition project phase: In Progress -> Acceptance.
- Perform project-level acceptance: Check overall consistency between quickstart and troubleshooting.
- If project-level checks pass, transition project phase: Acceptance -> Completed.
Update project-status.md accordingly.
```

- **Sample Commander Verdict (Illustration only):**
  ```text
  [SAMPLE VERDICT - ILLUSTRATIVE]
  Task Checks: docs/quickstart.md and docs/troubleshooting.md verified on disk against all criteria.
  TASK-001: Completed | TASK-002: Completed
  Project Acceptance: Phase In Progress -> Acceptance -> Completed (project criteria passed).
  ```
- **Stage exit:** `<project-root>/project-status.md` reflects terminal phase `Completed`. Walkthrough finished.
