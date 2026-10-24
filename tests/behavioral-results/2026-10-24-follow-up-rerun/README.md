# Host B Follow-up Rerun: Cases 04–06

This directory archives a follow-up rerun of the three behavioral cases that were incomplete or had receipt-compliance failures in the 2026-10-18 Model A run. It covers `04-continuation`, `05-window-recovery`, and `06-missing-evidence`.

## Environment

- Date: 2026-10-24.
- Host: Host B (desktop agent tool), three fresh general-purpose subagent sessions.
- Model: inherited from the parent session; the exact identifier was not exposed (unmeasured).
- Source base: commit `588e70e` plus the uncommitted reliability/onboarding changes. Source hashes are recorded in [manifest.json](manifest.json).
- Isolation: one disposable project copy per case; only that case's input was disclosed. This is not an OS sandbox.

## Results

| Case | Primary behavior | Receipt compliance | Result |
|---|---|---|---|
| 04-continuation | PASS: typo fixed, all three sections delivered from `facts.md` | PASS: exact legal `Awaiting Acceptance`; no status write | PASS |
| 05-window-recovery | PASS: `slugify` preserved, `truncate` added, 7/7 tests pass in parent rerun | PASS: exact legal `Awaiting Acceptance`; no status write | PASS |
| 06-missing-evidence | PASS: acceptance refused; `Needs Revision` recorded and validated | PASS: seed receipt's illegal `Completed` rejected | PASS |

See [observations.md](observations.md) for the per-case evidence, non-blocking observations, and limitations.

## Evidence files

- `manifest.json` — source/seed hashes and normalized case metadata.
- `parent-verification.json` — independently observed file deltas, status validation, source preservation, and test rerun.
- `<case>/input.md` — normalized prompt supplied to the subagent.
- `<case>/changes.diff` — normalized artifact diff against the seed.

## Scope

This is a follow-up rerun on a different host/model from the 2026-10-18 Model A run. It does not establish a same-model improvement rate, token savings, latency, multi-host compatibility, or OS-level isolation. Case 06 was a receipt-only Commander review; it did not execute QA or project-level acceptance.
