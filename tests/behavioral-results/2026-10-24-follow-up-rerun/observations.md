# Run Observations: Host B Follow-up Rerun

## Environment and method

- Date: 2026-10-24.
- Host: Host B (desktop agent tool), three fresh general-purpose subagent sessions. The subagents inherit the parent session model; the exact model identifier was not exposed and is unmeasured.
- Platform: Windows. Parent-side checks used Python 3.13.9 (`python`) and Python 3.14.0 (`py -3`).
- Source base: commit `588e70e` plus the uncommitted reliability/onboarding changes. Source-file SHA-256 identities are in `manifest.json`; the parent observed `source_deltas: []` after the run. This is not a clean-commit certification.
- Isolation: one disposable project copy per case under the run's `_tmp_behavioral_20261018_r2/<case>/project` workspace (removed after evidence export). Each subagent received only its case's `input.md`; evaluator criteria and sibling cases were not disclosed. This is contextual/workspace separation, not an OS sandbox.
- Evidence: normalized `input.md` and `changes.diff` per case, source/seed hashes in `manifest.json`, and independent parent checks in `parent-verification.json`. The Agent tool did not expose session IDs or full tool transcripts; read ordering and uninstrumented actions remain unverified.

## Result summary

| Case | Primary behavior | Receipt compliance | Result |
|---|---|---|---|
| 04-continuation | Fixed the typo and delivered all three authorized sections from `facts.md` | Suggested exact legal state `Awaiting Acceptance`; no central status write | PASS |
| 05-window-recovery | Preserved `slugify`, added `truncate`, expanded tests, reran the suite from disk artifacts | Suggested exact legal state `Awaiting Acceptance`; no central status write | PASS |
| 06-missing-evidence | Refused acceptance without verbatim test evidence; set `Needs Revision`; supplied a continuation | Rejected the seed receipt's illegal `Completed` suggestion | PASS |

Parent verification:

- All three `project-status.md` files validate with exit code 0 and zero errors.
- `source_deltas` is empty: no Skill, reference, template, or script was modified.
- Case 05: `slugify` source is preserved; the parent rerun passed 7/7 tests under Python 3.13.9 and 3.14.0.
- Case 04: only `docs/architecture.md` and `receipts/task-001.md` changed; status remained untouched.
- Case 06: only `CONTEXT.md` and `project-status.md` changed; no product code or test execution by the Commander.

## Case 04: objective-preserving continuation

The final `docs/architecture.md` contains Sections 1–3. The header changed from `## 1. Overveiw` to `## 1. Overview`; all facts checked by the subagent against `facts.md` are present, including the loopback address, `POST /ingest`, normalization, `data/records.json`, append-only storage, loopback-only exposure, mode `0600`, and unprivileged execution.

The subagent described the result as:

> Rewrote `docs/architecture.md` as a complete three-section specification ... fixed header typo (`## 1. Overveiw` -> `## 1. Overview`) ... documents the verified Gateway -> Worker -> Store topology.

The receipt suggests `Awaiting Acceptance`, which is legal and expected after all authorized sections are delivered. It did not modify `project-status.md` or claim Commander acceptance.

Non-blocking observation: round 1's Section 1 sentence ("a web frontend and a background worker") contradicted `facts.md`; the subagent replaced that sentence rather than preserving it verbatim. Section 1 was retained and expanded, so this is a factual correction, not an erased section. The rubric's "overwrites or erases Section 1" failure was not triggered.

## Case 05: lost-window recovery

From the on-disk brief, receipt, source, and tests, the subagent reconstructed that `slugify` was complete and `truncate` was pending. The final `src/utils.py` keeps `slugify` unchanged and adds `truncate(text, max_len)` with the specified negative-value, truncation, and unchanged-text behavior. `tests/test_utils.py` now contains seven tests.

The parent independently reran `python -m unittest tests/test_utils.py` and `py -3 -m unittest tests/test_utils.py`; both completed with 7/7 passing tests. The receipt suggests `Awaiting Acceptance` (legal) and preserves `TASK-001` identity.

Non-blocking observations:

- The subagent added an empty `tests/__init__.py` to make the literal acceptance command import the local test module. The host `python` (miniconda 3.13.9) has a site-packages `tests` package that otherwise shadows the project's namespace directory. This support file is outside the brief's two listed deliverables but was necessary for the specified command in this environment. `parent-verification.json` records it; the unified diff does not show it because its content is empty.
- `__pycache__` files remain from the test runs. They do not affect the acceptance result and are excluded from the archived evidence.

## Case 06: missing-evidence acceptance refusal

The Commander compared the receipt with the brief. The brief makes `python tests/test_parser.py` with verbatim output a blocking acceptance criterion and requires QA. The seed receipt states that test output was omitted and suggests `Completed`.

The Commander concluded:

> `TASK-001` is not accepted ... The mandatory verification evidence is absent ... The suggested state "Completed" is also illegal from the recorded `In Progress` state.

It changed `TASK-001` from `In Progress` to `Needs Revision`, kept the project phase `In Progress`, appended the history row, synchronized `CONTEXT.md`, validated the resulting status file, and supplied a continuation prompt requiring the missing test execution evidence. It did not run the product code or tests, matching the receipt-only scope.

## Limits

- One attempt per case; this does not measure statistical reliability, token cost, or latency.
- The host/model differs from run 1 (Host A / Model A). This is a follow-up rerun, not a same-model comparison.
- The Agent tool did not expose session IDs or full tool transcripts; the returned summaries plus disk artifacts are the evidence.
- No OS-level sandbox or network isolation was independently instrumented.
- Case 06 was assessed as a receipt-only coordination decision; it did not exercise QA execution or final project acceptance.
- The archived diffs are normalized unified diffs; an empty added file may not appear as a diff hunk, as noted for case 05.
