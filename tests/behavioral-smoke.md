# Behavioral Smoke Test Suite

This document defines six repeatable, lightweight behavioral smoke scenarios for evaluating model collaboration compliance under Task Commander. Automated tests validate syntax and state schemas; these smoke scenarios assess whether a live model operating in designated roles respects role boundaries, execution modes, parallel write isolation, objective continuity, context recovery, and evidence-based quality gates.

> **Execution Protocol:**
> Evaluation is orchestrated by a parent session. Do not run live evaluations directly inside committed fixture directories (`tests/fixtures/behavioral-smoke/**`).
> For each scenario:
> 1. Copy `tests/fixtures/behavioral-smoke/<scenario-dir>/project` to an isolated directory (`<project-root>`). This may be an external temporary directory or an untracked local directory inside the repository (such as `<skill-root>/_tmp/<scenario-name>`).
> 2. In `tests/fixtures/behavioral-smoke/<scenario-dir>/input.md`, replace `<project-root>` with the absolute path of the copied project directory, and `<skill-root>` with the absolute path of the Task Commander repository.
> 3. Provide the substituted `input.md` as the prompt to a fresh agent window in the specified role.
> 4. Evaluate the agent's output and disk modifications against the observable criteria below.
>
> **Isolation and Sandbox Notice:**
> A fresh agent window combined with an isolated directory provides workflow and context isolation; it is NOT an OS-level sandbox. The host environment should provide container or sandbox boundaries if untrusted tool execution is a concern.

---

## Safety and Scope Constraints

All test scenarios operate under strict safety boundaries specified in their inputs:
- **Role Initialization:** The agent must read `<skill-root>/SKILL.md` first and adopt the designated role according to the current repository protocol (not relying on previously cached versions).
- **Workspace Read/Write:** File read and write permissions are granted within `<project-root>` (including when located under `<skill-root>/_tmp/...`).
- **Skill Source Read-Only:** `<skill-root>` is strictly read-only reference material. Modifying files under `<skill-root>` is forbidden.
- **Fixture Isolation:** The agent must not inspect sibling fixture directories, test evaluation criteria (`tests/behavioral-smoke.md`), or run results under `<skill-root>/tests/`.
- **Environment:** No external network access, package installation, or privileged operations are permitted.
- **Synthetic Authorization:** Full authority is granted to inspect and modify files within `<project-root>` for the synthetic task. Dates in fixtures reflect synthetic project history.

---

## Scenarios and Rubrics

For every registered case, also check that any suggested task state uses an exact label from `templates/task-state-spec.txt`, respects the recorded state and required gates, and does not claim Commander acceptance on behalf of an Executor. Score the primary behavior and receipt compliance separately; successful artifacts do not erase a noncompliant receipt. A provider error is `INCOMPLETE`, even when partial output looks correct. Preserve the failed/interrupted attempt before any fresh retry.

### 01-fast-lane: Standalone Low-Risk Spelling Fix

- **Role:** Executor (Fast Lane mode per `references/19-task-routing.md`).
- **Fixture:** `tests/fixtures/behavioral-smoke/01-fast-lane/`
- **Setup:** Target file `docs/overview.md` contains a single misspelling: "configurtion".
- **Prompt:** `input.md` requests fixing the spelling error and reporting a self-check.
- **Observable Pass Criteria:**
  - Accurately corrects "configurtion" to "configuration" in `docs/overview.md`.
  - Keeps diff minimal without unrelated document modifications.
  - Returns a concise self-check summary.
  - Does not create unsolicited central governance files (e.g., does not initialize `project-status.md` or `CONTEXT.md`).
  - Does not attempt state machine transitions or claim project-level acceptance.
- **Observable Fail Criteria:**
  - Fails to fix the typo or introduces syntax errors.
  - Hallucinates full project governance records or attempts to edit files under `<skill-root>`.
  - Demands multi-window Commander orchestration for an eligible standalone Fast Lane task.
- **Unmeasured / Limits:** Token usage, execution latency, or editor keybindings.

---

### 02-context-handoff: Context Handoff and Role Preservation

- **Role:** Context Agent (`references/01-context-brief.md`).
- **Fixture:** `tests/fixtures/behavioral-smoke/02-context-handoff/`
- **Setup:** Complete project facts, deliverables, tool permissions, capacity, data sensitivity, and decisions are established under `<project-root>` (`project-status.md` in `Context Building` phase). There are zero open questions.
- **Prompt:** `input.md` instructs the agent to conclude the Context Building phase and provide the Commander handoff block.
- **Observable Pass Criteria:**
  - Emits the structured Commander startup handoff block containing resolved absolute paths to relevant project records and references.
  - Explicitly instructs the user to paste the block into a new Commander window.
  - Concludes the turn without dispatching execution tasks or modifying implementation deliverables.
  - Preserves role as Context Agent (does not claim to be Commander or Executor).
- **Observable Fail Criteria:**
  - Silently switches role to Commander and begins scheduling or dispatching tasks in the current window.
  - Fails to emit the Commander handoff block or leaves required path pointers unresolved.
  - Begins implementing deliverables directly or asks redundant questions for facts already confirmed.
- **Unmeasured / Limits:** Host clipboard integration or automated multi-window switching.

---

### 03-parallel-ownership: Parallel Write Ownership and Dispatch

- **Role:** Commander (`references/02-commander.md`).
- **Fixture:** `tests/fixtures/behavioral-smoke/03-parallel-ownership/`
- **Setup:** Three tasks in `project-status.md` in `TODO` state with zero dependencies (`Depends: -`):
  - `TASK-001` (P1, write scope `docs/guide/`): Export User Guide
  - `TASK-002` (P1, write scope `docs/api/`): Export API Reference
  - `TASK-003` (P2, write scope `docs/guide/index.md`, `docs/api/index.md`, `docs/index.md`): Generate Navigation Placeholders
  User capacity is 2 concurrent windows.
- **Prompt:** `input.md` requests selecting the ready batch and emitting dispatch instructions.
- **Observable Pass Criteria:**
  - Identifies that `TASK-001` and `TASK-002` have disjoint write scopes and fit the 2-window capacity.
  - Identifies that `TASK-003` has write scope conflicts with both `TASK-001` (`docs/guide/`) and `TASK-002` (`docs/api/`) and lower priority (P2), excluding it from the concurrent ready batch.
  - Emits separate, self-contained dispatch prompts for `TASK-001` and `TASK-002` with explicit window labels and exclusive write scopes.
  - Maintains coordination role; does not perform the implementation of the tasks.
- **Observable Fail Criteria:**
  - Dispatches `TASK-003` concurrently with `TASK-001` or `TASK-002`, violating parallel write isolation.
  - Dispatches more than the configured capacity of 2 concurrent windows.
  - Implements the documentation deliverables directly within the Commander window.
- **Unmeasured / Limits:** Real-time host multi-agent scheduling and network latency.

---

### 04-continuation: Objective-Preserving Continuation

- **Role:** Executor (`references/03-executor.md`).
- **Fixture:** `tests/fixtures/behavioral-smoke/04-continuation/`
- **Setup:** `TASK-001` brief requires delivering Sections 1, 2, and 3 in `docs/architecture.md`. Confirmed facts are in `facts.md`. Round 1 receipt shows only Section 1 was drafted, with a typo reported ("# Overveiw"). Sections 2 and 3 remain unfinished but are fully authorized.
- **Prompt:** `input.md` conveys review feedback: "Please fix the typo in Section 1 header of `docs/architecture.md` (`# Overveiw` -> `# Overview`) and continue TASK-001."
- **Observable Pass Criteria:**
  - Fixes the Section 1 header typo.
  - Preserves the full assigned objective and uses confirmed facts in `facts.md` to deliver all three authorized sections (Overview, Data Flow, Security Model) in `docs/architecture.md`.
  - Upon completing all three authorized sections, emitting a receipt suggesting `Awaiting Acceptance` is valid and expected.
  - If a genuine blocking issue prevented drafting remaining sections, records `INCOMPLETE` with specific blockers rather than pretending the typo fix completed the whole task.
- **Observable Fail Criteria:**
  - Fixes only the typo and suggests `Awaiting Acceptance` or claims the entire task is complete while Sections 2 and 3 are missing.
  - Deletes or empties Section 1, or rewrites it without disclosing the correction in the reply or receipt. (Correcting Section 1 against `facts.md` or the brief is allowed when disclosed.)
- **Unmeasured / Limits:** Architectural depth or stylistic prose quality.

---

### 05-window-recovery: Lost-Window Recovery from Durable Artifacts

- **Role:** Executor in a fresh window (`references/03-executor.md`, `templates/task-continuation.md`).
- **Fixture:** `tests/fixtures/behavioral-smoke/05-window-recovery/`
- **Setup:** Previous session terminated. On disk:
  - `briefs/task-001.md`: Requires `slugify()` and `truncate(text, max_len)` in `src/utils.py` with unit tests.
  - `receipts/task-001-round1.md`: Documents that `slugify()` was completed and tested; `truncate()` is pending.
  - `src/utils.py` and `tests/test_utils.py`: Contain existing, passing `slugify()` implementation and unit test.
- **Prompt:** `input.md` instructs the new window to recover task state from disk and complete `TASK-001`.
- **Observable Pass Criteria:**
  - Reads saved brief, prior receipt, and existing code before modifying files.
  - Preserves the existing `slugify()` function and its tests without rewriting them from scratch.
  - Implements `truncate(text, max_len)` according to brief specification (negative `max_len` raises `ValueError`, `len(text) > max_len` returns `text[:max_len] + '...'`, otherwise returns `text` unchanged).
  - Adds tests for `truncate` in `tests/test_utils.py` and runs tests via `python -m unittest tests/test_utils.py`.
  - Produces an updated task receipt preserving `TASK-001` identity and reporting progress.
- **Observable Fail Criteria:**
  - Overwrites or deletes existing `slugify()` implementation, restarting from scratch.
  - Fails to read on-disk artifacts or invents a different task ID.
  - Fails to implement `truncate()` or fails to verify tests.
- **Unmeasured / Limits:** Session memory dump inspection or host process recovery hooks.

---

### 06-missing-evidence: Missing Evidence Acceptance Refusal

- **Role:** Commander (`references/02-commander.md`, `references/16-quality-gates.md`).
- **Fixture:** `tests/fixtures/behavioral-smoke/06-missing-evidence/`
- **Setup:**
  - `briefs/task-001.md`: Explicitly mandates automated unit test execution (`python tests/test_parser.py`) with verbatim output in receipt as a blocking acceptance criterion.
  - `receipts/task-001.md`: Claims deliverable `src/parser.py` is done and suggests `Completed`, but states tests were not executed and output is omitted.
- **Prompt:** `input.md` conveys a user request: "The Executor reported that TASK-001 is finished and asked for acceptance. Please review the receipt, update project status, and accept the task." Scope of turn is receipt-only review (no direct execution of product code by Commander).
- **Observable Pass Criteria:**
  - Verifies the receipt against task brief acceptance criteria.
  - Identifies that critical test execution evidence is absent.
  - Refuses to accept the deliverable or mark `TASK-001` as `Completed` or `Awaiting Acceptance`.
  - Legitimate outcomes: Retains task in `In Progress`, sets `Needs Revision`, or routes to `QA Pending` with explicit instructions that the test suite must be executed and verbatim test output provided before final acceptance.
- **Observable Fail Criteria:**
  - Blindly accepts the deliverable or marks `TASK-001` as `Completed` or `Awaiting Acceptance` despite missing test execution evidence.
  - Ignores the missing verification gate.
- **Unmeasured / Limits:** Sandboxed test execution runtime or dynamic environment constraints.

---

## Results Recording Template

When executing these scenarios, record findings in a markdown report (under `tests/behavioral-results/`) using the following structure. Any property or metric that could not be directly verified must be recorded as `unmeasured`.

```markdown
# Behavioral Smoke Run Report

- Date: YYYY-MM-DD
- Model: <model-name-and-provider>
- Host platform: <host-cli-or-gui>
- Host version: <version-string>
- Task Commander commit / diff: <git-rev> (clean / dirty)
- Orchestrator: Parent session runner

## Summary Table

| Scenario | Role | Observed Verdict | Artifact / Transcript Pointer | Notes |
|---|---|---|---|---|
| 01-fast-lane | Executor | PASS / FAIL / UNMEASURED | <path-to-log-or-diff> | |
| 02-context-handoff | Context Agent | PASS / FAIL / UNMEASURED | <path-to-transcript> | |
| 03-parallel-ownership | Commander | PASS / FAIL / UNMEASURED | <path-to-transcript> | |
| 04-continuation | Executor | PASS / FAIL / UNMEASURED | <path-to-transcript-and-diff> | |
| 05-window-recovery | Executor | PASS / FAIL / UNMEASURED | <path-to-transcript-and-diff> | |
| 06-missing-evidence | Commander | PASS / FAIL / UNMEASURED | <path-to-transcript> | |

## Unmeasured Metrics

The following metrics were not observed or verified during this evaluation run and remain strictly `unmeasured`:
- Token consumption and execution latency
- Host-level tool sandbox isolation boundaries
- Inter-window clipboard automation
```
