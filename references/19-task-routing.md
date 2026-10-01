# Task Routing

> Read at initial task intake, when choosing a lighter execution path, or when scope/risk changes. This file owns execution-mode eligibility and escalation; `references/16-quality-gates.md` owns verification gates. Modes are not roles or task states.

## Route with the smallest sufficient process

1. Preserve the explicitly assigned role, existing task ownership and full user objective. Check whether the request belongs to a registered task or an unfinished broader outcome; the latest small defect is not a new independent request.
2. Check impact, reversibility, effective authorization and resource conflicts. Risk overrides apparent size. File count and keywords are hints, not eligibility rules; one line can change access control or destroy data.
3. Check dependencies, uncertainty and acceptance clarity separately from risk. Use necessary read-only inspection or a focused question to resolve material gaps before mutation, not a speculative score or a full interview by default.
4. Choose a mode below. Explain the choice only when it changes what the user must do. Mode selection never activates permissions, waives an existing gate or changes the window's role.

| Mode | Use | Coordination |
|---|---|---|
| Fast Lane | Independent, unregistered, low-risk, reversible request meeting every condition below | Executor, inline contract and concise self-check result; no project initialization |
| Lean | Registered narrow low-risk work, or low-risk work needing project coordination | Commander plus the task's owner; compact briefs/receipts, existing state machine and risk-based gates |
| Standard | Material dependencies, uncertainty, shared-resource conflicts or elevated risk | Existing project protocol; choose necessary roles and gates rather than every role automatically |

A complex low-risk task may need Standard coordination. Lean does not imply weak verification. Existing task permissions and gates remain effective until explicitly revised through their governing protocol.

## Fast Lane eligibility and contract

All conditions must hold:

- The actual user request is independent and unregistered, not carved out of a broader unfinished assignment or another owner's scope.
- The intended result, write boundary and observable acceptance criteria are clear.
- The change is low-risk and reversible using an adequate recovery method; it has no material cross-task dependency or shared-resource conflict.
- It needs no central-record update, new major decision, sensitive transfer, security/access-control change, destructive operation, deployment, payment or other consequential external write.
- Effective authorization covers the intended actions, and relevant checks can be performed or their material limitations resolved.

When no role has been assigned, a qualifying request may start in Executor. An existing Context or Commander window stays in its role: offer a concise handoff to an Executor window or request an explicit role change when useful. A Commander without project status still cannot dispatch ordinary project work; the independent Fast Lane exception belongs to Executor, not an initialization bypass for Commander.

Use an inline contract stating the requested outcome, allowed scope, checkable finish line and operative constraints. The user's clear request can supply it; clarify only missing essentials. No saved brief, ordinary task ID, background files or `project-status.md` is required. Do not create those artifacts merely to unlock a small task or claim an unsaved brief exists. This exception covers independent delivery only, not project acceptance or coordination.

Use `references/runtime.md` before file/CLI work. Apply effective tool permissions and recovery requirements; consult `references/15-collaboration.md` when delegation, research, human assistance or resource conflicts arise, and `references/14-backup-manager.md` when backup coverage is needed. Use relevant self-check and evidence rules from `references/16-quality-gates.md`; required independent verification means the request no longer qualifies for Fast Lane.

Return a concise result: what changed and where, relevant check/method and actual outcome, and material limitations or remaining work. For a prose correction, inspecting the exact diff may suffice; executable changes need relevant behavioral evidence. Label checks as directly performed, reused or unverified. Say why a relevant check was not run; an exit code alone does not establish the requested result. No mandatory receipt table or extra output file is needed. Executor reports delivery to the user; it does not declare project Completed or accept its own work as a Commander gate.

## Lean and Standard boundaries

For registered tasks, preserve the ID, owner, history and legal transitions in `references/11-task-state-machine.md`. Lean can explicitly waive independent Reviewer/QA gates only under `references/16-quality-gates.md`; keep Commander light acceptance and the route through Awaiting Acceptance. Emitting a prompt is not pickup or execution. Compact records retain the full contract and usable evidence pointers. Low-risk coordinated work without status still requires project initialization before ordinary Commander dispatch.

Reuse authoritative project files rather than rebuilding background; follow `references/10-context-orchestration.md` for sources and inherited context, and `references/17-cold-start-review.md` for staged review disclosure. User-requested stricter checks override a lighter mode. Neither mode introduces automatic acceptance or a new runtime.

## Escalation without losing work

Recheck eligibility when inspection or execution reveals hidden dependencies, increased risk, conflicts, expanded scope or an essential verification gap. Pause the affected action, preserve current artifacts and valid evidence, state the specific gap, and obtain the necessary coordination, authorization, backup or gate before continuing. Continue unaffected authorized work where safe.

If independent work now needs project coordination, request Context initialization or the existing Commander as appropriate; preserve the original objective and record actual prior work without inventing a task-state history. An Executor remains Executor across escalation. Escalation does not authorize broader scope, reset accepted evidence or turn a partial result into completion.
