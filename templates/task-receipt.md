# Task Receipt / Checkpoint

> Use as a concise section of the existing task result, or a separate receipt if useful. Omit irrelevant optional sections rather than filling pages with empty fields. Retain prior-round evidence. All roles submit evidence and suggested states; only Commander updates central status.

## Identity and progress

- Task ID / round / primary role / window label:
- Original brief path:
- Acknowledged shared context revision and relevant input versions:
- Deliverables and current versions (include dirty-file identity when relevant):
- Completed / remaining / suggested legal next state:

Before sending a registered-task receipt, read the current recorded state and required gates. Use a verbatim state label from `templates/task-state-spec.txt` and check it against the role's delivery rules and `references/11-task-state-machine.md`. Keep completion of your delivery separate from Commander acceptance; if a next state cannot yet be justified, report the missing work or evidence instead of inventing a label.

## In-phase progress (optional)

Use when a checkpoint supports the coordination checks in `references/02-commander.md` (In-phase progress checks), not as a periodic reporting requirement.

- Active stage and comparison checkpoint / relevant input versions:
- Substantive delta and evidence path (artifact advance, new evidence, eliminated hypothesis or reduced unknown); otherwise what remains unchanged:
- Consecutive no-progress checks / agreed diagnostic threshold, if supplied by Commander:
- Suspected cause, changed check/experiment or help request; blocker owner and resume condition if genuinely unable to proceed:

## Acceptance evidence

| Check / criterion | Artifact + relevant input versions | Method / environment or source date | Result + provenance (direct / reused / unverified) | Evidence path / checker |
|---|---|---|---|---|

- Reused checks and why still valid:
- Changed inputs, invalidated checks and regression scope:
- Findings: ID, blocking / non-blocking / suggestion / unverified, location, disposition:

## Review context (when relevant)

- Mode / stage / concrete scenario / assigned coverage:
- Packet version and inputs actually read; inherited or accidental context exposure and timing:
- Preserved independent record path; stage-2 context release and final report paths:
- Initial finding ID -> confirmed / refuted by evidence / user-accepted trade-off / unverified; evidence and reason for each disposition or severity change:
- Checked criteria, untested areas and remaining coverage gaps (including zero-finding reports):
- Stage 1 is a checkpoint, not a gate pass; acknowledge only context actually received. Follow `references/17-cold-start-review.md` for isolation and reconciliation.

## Shared-information delta

- New facts with evidence; disproved assumptions; interface/constraint changes:
- Label each as verified fact, user report, hypothesis, or proposal:
- Authoritative file to update and affected task IDs:
- Decision requiring user confirmation (not a final decision until confirmed):
- Write conflicts, user actions, blockers, owner and resume condition:

## Knowledge delta (when relevant)

- Stable conclusion / lesson / procedure produced (or "none"):
- Proposed topic path and one-line summary:
- Evidence / artifact / decision pointer:
- Scope: project-local / reusable graduation candidate:
- Conflict with an existing topic or LOG entry:
- Commander integration required; do not edit shared knowledge records concurrently.

## Recovery checkpoint (when relevant)

- Recovery artifact and manifest path / source version / creation time:
- Coverage and exclusions; integrity check; isolated restore/readback result:
- Restoration instructions and remaining limitations:
- Last durable work checkpoint, tried approaches, and next action if this window is lost:

## Exploration (when relevant)

- Question/hypothesis, input snapshot, budget and stop condition:
- Method and observed positive / negative / inconclusive result:
- Comparison criteria, useful failed approaches, and recommended next experiment:
