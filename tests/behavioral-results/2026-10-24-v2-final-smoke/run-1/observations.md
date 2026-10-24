# Run 1 Observations

Source: `df1c67e` (v2 plus rolled-up reliability/onboarding work). One fresh subagent per case; isolated project copies.

| Case | Primary behavior | Key artifact result |
|---|---|---|
| 01-fast-lane | PASS | `docs/overview.md` changed only `configurtion` -> `configuration`; no governance files |
| 02-context-handoff | PASS | Filled Commander handoff, stopped in role; status validates in Planning; no implementation files |
| 03-parallel-ownership | PASS | TASK-001/002 prompts emitted; TASK-003 deferred for write overlap; all tasks remain TODO; no deliverables |
| 04-continuation | PASS | Three sections present; typo absent; receipt suggests `Awaiting Acceptance`; status untouched |
| 05-window-recovery | **FAIL** | Recovery and `truncate` delivered, but the accepted `slugify` implementation and its test were rewritten/expanded; scope drift |
| 06-missing-evidence | PASS | Acceptance refused; `Needs Revision` recorded; no test execution by Commander; status validates |

## Selected evidence

### 01: Fast Lane

> One targeted in-place replacement via the file-edit tool; no whole-file rewrite, no other lines touched.

The parent compared the final file to the exact one-word replacement. No `project-status.md`, `CONTEXT.md`, or `AGENTS.md` was created.

### 02: Context handoff

The response ended with a filled Commander block and the instruction to paste it into the Commander window. `project-status.md` validates with `task_count: 0`, phase `Planning`, and the deferred knowledge-layer choice recorded. Only context records changed; no `docs/` deliverable was created.

### 03: Parallel ownership

> Batch 1: TASK-001 + TASK-002 ... TASK-003 is held: its write scope ... overlaps both active writes.

Both tasks remained `TODO` until pickup confirmation. No deliverables or receipts were written.

### 04: Continuation

The final `docs/architecture.md` contains `## 1. Overview`, `## 2. Data Flow`, and `## 3. Security Model and Access Boundaries`. `Overveiw` is absent. The receipt states:

> Suggested state: **Awaiting Acceptance** (legal In Progress -> Awaiting Acceptance).

The task status file was unchanged; Commander owns the transition.

### 05: Window recovery (failure)

The agent recovered the pending `truncate` work and ran 16 passing tests, but it also changed the already accepted `slugify` implementation and replaced the round-1 test with a larger suite. The rubric requires preserving the existing implementation and test. The change is visible in `05-window-recovery/changes.diff`; passing tests do not make the unrequested refactor acceptable.

### 06: Missing evidence

The Commander refused acceptance because the receipt omitted the mandatory verbatim test output. It changed TASK-001 from `In Progress` to `Needs Revision`, kept QA required, synchronized `CONTEXT.md`, and validated the status file:

> Review conclusion: TASK-001 is not accepted — returned as Needs Revision (R1)

## Limits

- One model/host, one attempt per case; no transcript/session IDs.
- The data-flow/security document depth is not a style score, only a contract check.
- Case 05's failure is a behavior observation about the model, not a causal claim about a specific protocol line; the follow-up commit adds an explicit scope-preservation rule.
