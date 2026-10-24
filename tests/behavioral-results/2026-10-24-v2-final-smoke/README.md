# V2 Final Six-Case Behavioral Smoke (2026-10-24)

## Environment and method

- Host: Host B (desktop agent tool), one fresh general-purpose subagent per case.
- Model: inherited from the parent session; the exact identifier was not exposed (unmeasured).
- Platform: Windows. Source base for run 1: `df1c67e`; run 2: `0eb2914` after the scope-preservation fix.
- Method: one isolated project copy per case, only that case's `input.md` supplied, evaluator criteria and sibling cases withheld. This is contextual/workspace separation, not an OS sandbox.
- The six cases are the existing `tests/behavioral-smoke.md` pack (Fast Lane, Context handoff, parallel ownership, continuation, window recovery, missing evidence).

## Results

| Case | Run 1 (`df1c67e`) | Run 2 (`0eb2914`) | Note |
|---|---|---|---|
| 01 Fast Lane | PASS | — | Exact one-word fix; no governance files |
| 02 Context handoff | PASS | — | Filled handoff and stop; status validates in Planning |
| 03 Parallel ownership | PASS | — | Two independent prompts; conflicting third task deferred; tasks remain TODO |
| 04 Continuation | PASS | — | All three sections; typo fixed; receipt suggests `Awaiting Acceptance` |
| 05 Window recovery | **FAIL** | **PASS** | Run 1 modified the already accepted `slugify` and expanded its tests; run 2 preserved `slugify`, kept the round-1 test, and passed 8/8 tests |
| 06 Missing evidence | PASS | — | Acceptance refused; `Needs Revision` recorded and status validates |

**Overall:** five of six cases passed in run 1. The single failure was a scope violation, not a broken recovery: the Executor changed accepted code instead of only completing the assigned remainder. Commit `0eb2914` added an explicit "preserve accepted artifacts" rule to the Executor, Commander and task-template guidance. A fresh rerun of case 05 then passed.

## Evidence

- [run-1 observations](run-1/observations.md), [manifest](run-1/manifest.json), [parent verification](run-1/parent-verification.json)
- [run-2 observations](run-2/observations.md), [manifest](run-2/manifest.json), [parent verification](run-2/parent-verification.json)
- Per-case normalized `input.md` and `changes.diff` are under each case directory.

## Limits

- One host/model configuration, one run per case (plus one rerun of 05). This is not a statistical reliability claim.
- No session IDs or full tool transcripts were exposed. Returned summaries and disk artifacts are the evidence; read ordering and uninstrumented actions remain unverified.
- No OS-level network isolation or clipboard relay was independently tested.
- Case 05's run-2 added an empty `tests/__init__.py` to work around a host site-packages `tests` package shadowing the local test module. This is a non-blocking environment adaptation, not part of the deliverable.
- Case 05 run 1 had 16 passing tests but is still a FAIL: passing tests do not cure modifying accepted code outside the assigned scope.
