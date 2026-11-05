# Authority and Attention Upgrade (Protocol v2, additive)

> **Goal:** close the two weakest seams in the protocol — how a task's authority is recorded and revalidated, and how "does anything need me now" is answered — borrowing selectively from the DeepSeek Harness `dsh-superagent` prototype (Policy/Mandate, record-only start, attention economy) and from its Agent Teams model (compare-and-set status writes, declared write scopes, availability-is-not-outcome).

## Scope

This iteration adds **attributes and rules**, not concepts. It does not add a role, task state, required status column, protocol version bump, external provider adapter or agent runtime. Every new field is optional; existing `project-status.md`, task briefs and receipts stay valid without it.

- **Authority record:** each task brief records grant source, scope, strength and invalidation condition; a resumed task revalidates authority instead of inheriting it silently.
- **Authority strength:** `observe` / `propose` / `act` as an attribute orthogonal to Fast Lane / Lean / Standard, so a first pass at an unfamiliar or irreversible scope can run record-only.
- **Attention block:** the receipt states `outcome`, `attention`, `question`, `resume when` and `dispatch key` in structured form; "waiting for a person" is declared, never inferred from prose.
- **Needs you now:** an optional `project-status.md` section that lists at most five rows of work that genuinely needs a person, and nothing when the project is healthy.
- **Status revision:** an optional monotonic `- Status revision: N` line plus `--expected-revision`, giving the sole-writer rule a compare-and-set check instead of an honour-system read.
- **Design constitution:** three maintenance rules in `SKILL.md` (attribute or prompt text before a new concept; a default before a setting; every output element justifies its attention) plus an attention budget for coordination messages.
- **Team-mode borrows:** availability is not outcome; write scopes are declared and overlap is an advisory warning; a dispatch records its context mode (`fresh` / `inherited` / `recovery`).

## Key files

- Protocol: `references/06-task-template.md`, `references/11-task-state-machine.md`, `references/15-collaboration.md`, `references/19-task-routing.md`.
- Entry and principles: `SKILL.md`, `README.md`.
- Artifacts: `templates/project-status.md`, `templates/task-receipt.md`, `templates/task-state-spec.txt`.
- Validation: `scripts/validate-project-state.py`, new `tests/test_attention_and_revision.py`.
- Regression guards: `tests/test_document_contracts.py`, `tests/test_status_table_cli.py`, CI smoke checks.

## Vocabulary

| Term | Values | Lives in |
| --- | --- | --- |
| Authority strength | `observe` · `propose` · `act` | task brief; inherited from effective policy |
| Outcome | `ready` · `blocked` · `failed` · `waiting` | receipt attention block |
| Attention | `person` · `executor` · `reviewer` · `qa` · `commander` · `none` | receipt attention block |
| Needs you now | `| Task | Question | Resume when |`, max 5 rows | `project-status.md` |
| Status revision | integer, bumped once per status update | `project-status.md` Project section |
| Context mode | `fresh` · `inherited` · `recovery` | task brief; matches `references/21-window-boundaries.md` |

## Design boundaries

- `project-status.md` remains the only task-state source; `Needs you now` is a derived view of it and adds no state.
- The status revision is metadata, not a transition; a mismatch is a concurrency error, not a state error.
- Authority strength never waives a Reviewer/QA gate and never activates a capability the policy does not grant.
- `observe` and `propose` still produce evidence; they are not "no work" and cannot satisfy an acceptance gate by themselves.
- The validator checks structure, not truth: it cannot prove a question is the right question or that a grant source is genuine.
- Existing files without any new field remain valid; adopting a field requires no protocol version bump.

## Verification

- `python -m unittest discover -s tests`: **175 tests, 4 platform skips, OK** on Windows (baseline was 163; +11 in `tests/test_attention_and_revision.py`, +1 document-contract guard).
- `python scripts/validate-project-state.py --path templates/project-status.md`: valid, `status_revision: 1`, `needs_you_count: 0`; the template ships an empty `Needs you now` section so a healthy project takes no space.
- `tests/test_attention_and_revision.py` covers: unknown task in `Needs you now`, terminal task listed, blank or "-" question, more than five rows, wrong column count, `--expected-revision` match / mismatch / missing line, non-numeric revision, and a legacy file with neither field.
- `tests/test_document_contracts.py` now asserts the new markers in `SKILL.md`, `README.md`, the four protocol references, both templates and the spec file, so a later edit cannot quietly drop them.
- `scripts/render-workflow.py` prints a `NEEDS YOU` block before the task table and exposes `needs_you` in `--format json`; the terminal board therefore answers "does anything need me now" before it lists work.
- CI smoke steps stay valid: `py_compile` for every helper, `--help` for all five CLIs, `validate-knowledge.py --project-root .`, and the scan-skills assertions.

## Non-goals

- No new role, task state, phase or required column.
- No automatic acceptance, automatic dispatch or background watcher.
- No provider adapter, web panel or event source; this skill stays host-neutral and file-first.
- No protocol version bump: `Current protocol version: 2` is unchanged.
