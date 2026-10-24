# Verification Guidelines

> Apply the task's required criteria, risk tier and evidence reuse rules from `references/16-quality-gates.md`. The lists below are a menu by deliverable type, not a demand to repeat every check for every task/round. Use inherited tools and human assistance per `references/15-collaboration.md`; backup-sensitive tests follow `references/14-backup-manager.md`.

## Verification principles

Any output must answer:

1. Does it exist?
2. Is it correct?
3. Is it reproducible?
4. Does it meet the requirements?

---

## Document verification

Check:

- The file exists
- Encoding is sound
- Structure is complete
- Cited sources are explicit

---

## Data verification

Check:

- Data source
- Time range
- Units
- Calculation formulas

---

## Code verification

Check:

- Environment
- Dependencies
- Inputs and outputs
- Edge cases

---

## Bug-fix and performance tasks: build a feedback loop first

For a hard bug, failing behavior or performance regression, do not start with a theory. Build a feedback loop that reproduces the user's actual symptom and goes **red** on this bug.

The loop should be:

- **Red-capable** — it drives the real failing path and asserts the symptom, not merely "runs without error";
- **Deterministic** — the same verdict every run; for flaky bugs, raise the reproduction rate enough to debug;
- **Fast** — seconds, not minutes;
- **Agent-runnable** — the Executor can run it unattended; if a human must click, make that step explicit and capture the result.

Use the simplest loop that reaches the bug: a failing test, an HTTP/CLI script against a fixture, a headless browser check, a replayed trace, or a minimal harness. Once a loop exists, tighten it (faster, sharper, more deterministic).

Then:

1. Reproduce and confirm it is the user's failure, not a nearby one.
2. Minimize the reproduction until every remaining element is load-bearing.
3. State 3–5 ranked, falsifiable hypotheses before testing any of them.
4. Change one variable at a time. Prefer a debugger/REPL or targeted logs; tag temporary logs so cleanup is mechanical.
5. Write the regression test at a correct seam before the fix. If no correct seam exists, that is an architecture finding, not permission to skip the test.
6. Re-run the original loop after the fix, remove temporary instrumentation, and state the confirmed hypothesis in the receipt/commit message.

If a loop genuinely cannot be built, stop and ask for the missing environment, a redacted artifact or permission to add temporary instrumentation. Do not proceed on vibes. For performance work, establish a baseline measurement before changing code.

## AI-output verification

Forbidden:

- Numbers without sources
- Unsourced capability claims
- Unverified effects
- "Assumed passing" test results presented as execution evidence
- A bug fix without a reproduction or a correctly scoped regression check