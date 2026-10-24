# Reliability and Onboarding Implementation Plan

> **For agentic workers:** Use the available host's focused subagents for independent tasks and native execution for the shared parser, followed by independent review. The suggested `superpowers:subagent-driven-development` / `superpowers:executing-plans` skills are not available in this session; do not claim to invoke them. Track the steps below with checkboxes.

**Goal:** Make Task Commander easier to verify and try, while making its status validator and renderer agree on Markdown table cells.

**Architecture:** Retain the host-neutral Markdown protocol, existing state specification and standard-library CLIs. Share only table-cell parsing and separator recognition; add CLI regression cases and a small manual/live-model smoke pack rather than an agent runtime or evaluation service.

**Tech Stack:** Python 3.10+ standard library, unittest, UTF-8/LF Markdown, existing three-platform CI.

**Spec:** The user-approved optimization direction in this conversation: establish the test baseline, exercise six core model behaviors, fix parsing consistency, and improve onboarding using evidence. Existing constraints remain authoritative in `README.md`, `SKILL.md`, `references/11-task-state-machine.md`, `references/19-task-routing.md` and `references/runtime.md`.

## Global Constraints

- Python 3.10+; no third-party runtime or test dependencies.
- Keep Windows/macOS/Linux compatibility and UTF-8 without BOM, LF source files.
- Preserve all task states, status-table columns, role boundaries, permissions, backup requirements and acceptance gates.
- Command success, structural validation and model self-reports are not project acceptance.
- This iteration does not change command execution, add roles, initialize this repository as a managed project, or create an issue tracker.
- Work only in this repository and explicitly scoped disposable fixtures; no installation, external writes, commits or pushes.
- Use `Model A` for simple delegated checks/documentation; record actual model/session limitations.

## Review Focus

- Literal escaped pipes and backslash parity must preserve cells identically in both CLIs (Task 2).
- Empty edge cells, optional closing pipes, and aligned separator rows must not shift fields or fabricate tasks (Task 2).
- Malformed rows and stale/duplicate blocked records must remain rejected by the validator (Task 2 plus existing regressions).
- A smoke fixture or illustrative approval must never be treated as real authority or a passing behavioral result (Task 3).
- A newcomer must be able to distinguish the Context/Commander/Executor windows, same-task revision, and actual acceptance in the example (Task 4).

## Agreed verification seams

- Invoke `validate-project-state.py` and `render-workflow.py` as subprocesses from an unrelated working directory. Assert exit codes and JSON fields from known-literal Markdown cases; this covers user-visible parsing and import portability, not full Markdown conformance.
- Exercise model behavior in fresh task-scoped sessions using synthetic fixtures, and independently inspect returned artifacts/transcripts. This covers the six selected interactions for the observed host/model only, not all models or host integrations.
- Keep the existing unittest suite as the regression gate. Do not replace behavioral tests with text-marker assertions.

### Task 1: Establish the baseline

**Files:** Existing `tests/`, status template and four CLIs; no source changes.

- [x] Run `py -3 -m unittest discover -s tests -v` and record passes, failures and skips.
- [x] Run the status-template validator and all four `--help` commands.
- [x] Record Python version and repository revision with the results.

Baseline: revision `588e70e`, Windows / Python 3.14.0, 112 tests: 110 passed and 2 skipped for unavailable symlink privileges. Validator and four help commands exited 0. Evidence: tester session `01a14a42-4384-7692-bb62-bb44e867ce13`.

### Task 2: Align status table parsing

**Files:** Create `scripts/markdown_table.py` and `tests/test_status_table_cli.py`; modify `scripts/validate-project-state.py`, `scripts/render-workflow.py`, the dynamic renderer loader in `tests/test_workflow_engine.py`, and `.github/workflows/ci.yml` as needed.

**Interfaces:** `split_markdown_row(line: str) -> list[str]` returns trimmed cells, decodes an escaped pipe without discarding unrelated backslashes, removes only actual outside borders, and preserves empty cells. `is_separator_row(cells: list[str]) -> bool` recognizes nonempty rows consisting solely of Markdown alignment cells. The renderer retains its existing `split_markdown_row` import surface. The validator retains its JSON/exit-code and strict column-count contracts.

- [x] Write a CLI regression showing a valid task and blocked reason containing `\|`: validator must accept it; renderer must return the literal pipe without shifting status/dependencies/owner.
- [x] Run `py -3 -m unittest discover -s tests -p test_status_table_cli.py -v`; confirm the current validator fails the new case.
- [x] Implement the shared parser and switch both callers to it without broad script restructuring.
- [x] Add vertical regression slices for backslash parity, Unicode, surrounding whitespace, optional closing borders, aligned separators, empty last cells and malformed extra delimiters.
- [x] Keep strict task/blocked column validation; retain existing transition and blocked-metadata regressions.
- [x] Run focused tests and the full suite; include the new helper in CI syntax checks. Do not commit automatically.

Observed red: valid escaped task/blocked cells were counted as 12/8 columns instead of 11/6. Additional red cases covered optional closing borders, alignment/indentation, and a phantom blank-ID display task. After the fixes, 121 tests ran in 34.272s: 119 passed, 2 symlink skips. Also document the cell format in `references/11-task-state-machine.md` and declare `.yml` LF in `.gitattributes` so the edited CI file retains portable line endings.

### Task 3: Make six behavioral checks repeatable

**Files:** Create `tests/behavioral-smoke.md` and narrowly scoped synthetic fixture material where needed; link it from `tests/behavioral-scenarios.md`. Save a concise run report under `tests/behavioral-results/` with evidence/session pointers.

**Interfaces:** Each case has fixed input/setup, an execution prompt separated from evaluator criteria, allowed writes, observable pass/fail conditions and limitations. Cases: Fast Lane, Context handoff/stop, parallel write ownership, objective-preserving continuation, lost-window recovery, and missing-evidence acceptance refusal.

- [x] Define the six cases using existing protocol behavior; do not add new rules merely to satisfy a test.
- [x] Run feasible cases in fresh isolated task contexts with explicit fixture scopes. Record actual sessions and artifacts, failures, skips and unavailable metrics.
- [x] Distinguish an observed live-model result from a static fixture check or illustrative walkthrough; keep unverified cases explicit.
- [x] Use findings to decide whether any small routing-pointer adjustment is justified. Defer broad protocol pruning if the observations do not support it.

Completion note (2026-10-24): run 1 exercised all six cases on Host A / Model A; case 06 was interrupted by a provider error and is archived as INCOMPLETE. The follow-up rerun exercised 04–06 on Host B subagents; all three passed primary behavior and receipt checks. The observed receipt-label defect was addressed by the `templates/task-receipt.md` pointer; no routing-pointer change was justified. Evidence: `tests/behavioral-results/2026-10-18-behavioral-smoke/` and `tests/behavioral-results/2026-10-24-follow-up-rerun/`.

### Task 4: Provide a complete newcomer walkthrough

**Files:** Create `examples/first-project/README.md`; add a short pointer in `README.md`.

- [x] Explain a tiny, disposable two-deliverable project with concrete startup/receipt/continuation examples and window labels.
- [x] Show Context handoff, nonconflicting task ownership, a revision returning to the original task window, and evidence-based Commander acceptance.
- [x] Clearly mark all sample receipts and approvals as illustrations, not executed evidence or permission for a real project.
- [x] Reuse authoritative references instead of copying the protocol into the example; verify paths and narrative consistency.

Completion note (2026-10-24): the walkthrough exists at `examples/first-project/README.md`. All referenced protocol/template paths resolve, and every sample receipt and verdict is explicitly labeled illustrative.

### Task 5: Final verification and review

- [x] Independently review code changes, new behavioral evidence and the walkthrough; fix blocking findings.
- [x] Run the full suite on available Python interpreters, CLI smoke checks and `git diff --check`.
- [x] Verify UTF-8/LF for newly added text, source-tree cleanliness outside the intended diff, and cleanup of owned disposable fixtures.
- [x] Report actual changes, test outcomes, behavioral coverage and untested host/platform limits. List runner timeouts/logging and broader protocol pruning as deferred, not completed.

## Completion record (2026-10-24)

- **Implemented:** shared status-table parser `scripts/markdown_table.py` used by the validator and renderer; CLI regression coverage for escaped pipes, empty cells, optional borders, alignment rows and malformed rows; a receipt-template pointer to the authoritative state labels and gates; the six-scenario behavioral smoke pack with fixtures; the first-project walkthrough; README, CI and `.gitattributes` updates.
- **Verification:** Python 3.14.0 and 3.13.9 each passed 125 tests (2 symlink tests skipped on Windows); all four CLI `--help` checks pass; the status template validates; render and skill-scan smoke checks pass; `git diff --check` is clean; 127 text files are UTF-8/LF without BOM; the temporary behavioral workspaces were removed after their evidence was archived.
- **Behavioral coverage:** run 1 exercised all six scenarios on Host A / Model A (case 06 was INCOMPLETE after a provider error; cases 04/05 had receipt-label failures). The follow-up rerun exercised 04–06 on Host B subagents, with all primary behaviors and receipt checks passing. The parent-side review found no blocking findings; it is not a separate human review.
- **Deferred:** runner timeout/logging improvements, broader protocol pruning, a same-model six-case rerun, and live six-host certification. This iteration does not measure token or latency savings and does not establish host-wide integration.
