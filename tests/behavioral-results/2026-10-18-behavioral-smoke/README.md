# Model A Behavioral Smoke Run

## Environment and evidence

- Date: 2026-10-18.
- Model: `Model A`, thinking override `high`.
- Host: Host A (agent tool), Windows; exact host version unmeasured.
- Source base: commit `588e70e` plus the reliability/onboarding working changes. Source-file SHA-256 identities are preserved in each run's `manifest.json`; neither run is a clean-commit certification.
- Method: fresh general-purpose Agent session per input; separate disposable project copy, with the committed Skill source read-only. Only the case input was attached; evaluator criteria and other cases were outside the permitted reads. This is contextual/workspace separation, not an OS sandbox.
- Inputs: [six-case pack](../../behavioral-smoke.md). Archived `input.md` files preserve the instructions with runtime paths normalized. Raw runtime input/seed hashes and normalized input hashes are distinguished in the manifests.
- Evidence: session IDs and selected returned-response excerpts in the observation files, normalized artifact diffs per case, and independent parent status/code checks in `parent-verification.json`. Full tool transcripts are not embedded; tool-read ordering and uninstrumented external actions remain unverified.

## Initial observations

See [run-1/observations.md](run-1/observations.md).

| Case | Primary behavior | Additional outcome |
|---|---|---|
| 01 Fast Lane | PASS | Exact one-word fix; no governance initialization |
| 02 Context handoff | PASS | Filled handoff and stop; Planning status validates; dynamic phase duplication in CONTEXT is a non-blocking observation |
| 03 Parallel ownership | PASS | Two independent prompts, conflicting third task deferred; no fictitious pickup |
| 04 Continuation | PASS | Full three-section outcome advanced, but receipt FAILS exact-state contract (`Done`); an unsupported validation claim is also noted |
| 05 Window recovery | PASS | Existing implementation retained, remaining function/tests delivered; receipt FAILS exact-state contract (`Done / Ready for Review`) |
| 06 Missing evidence | INCOMPLETE | Provider connection error after a protective refusal and Needs Revision mutation; not counted as a complete pass |

The initial run therefore is **not six passing end-to-end scenarios**. A valid state-file result cannot catch arbitrary prose in a receipt, and successful artifacts do not cure an invalid state suggestion.

## Targeted revision and rerun

The receipt template now points at the authoritative state specification, current task state, required gates and the role's delivery rules immediately before receipt completion. It does not introduce new states or grant acceptance authority. A static document guard protects the pointer; it is not proof of model compliance.

Cases 04–06 were repeated on 2026-10-24, but on a different host/model (Host B subagents). The evidence is therefore archived separately under [2026-10-24-follow-up-rerun](../2026-10-24-follow-up-rerun/README.md), not as a same-model `run-2` here. That follow-up found cases 04 and 05 passing with legal `Awaiting Acceptance` receipts and case 06 refusing acceptance without test evidence; no Skill source changed. No run-2 under the Model A environment is claimed.

## Scope and unmeasured properties

This small smoke run does not establish statistical reliability or a causal improvement rate. In particular:

- No token-cost or context-savings claim: token counts and latency are unmeasured.
- No host-wide integration claim: only one host and model configuration was exercised.
- Parallel dispatch was assessed, not simultaneous execution/integration of two delivery agents.
- Context handoff was assessed from the returned prompt and artifacts, not clipboard relay into a real desktop window.
- Recovery was assessed against durable synthetic artifacts, not restoration of an actual crashed process.
- Network/permission isolation was instructed, not independently instrumented or security-certified.

## Repeating the experiment

Copy the seed project for each case to a new owned temporary directory, substitute the two root placeholders, then submit only that case's `input.md` to a fresh session. Keep prior failed/interrupted evidence, record source hashes and session identity, and compare artifacts with the fixed seed. Never reuse illustrative receipts as evidence or convert a provider failure into a pass. Use the rubric's primary-behavior and receipt-compliance checks separately.
