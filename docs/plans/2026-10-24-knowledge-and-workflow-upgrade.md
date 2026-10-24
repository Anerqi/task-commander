# Knowledge and Workflow Upgrade (Protocol v2)

> **Goal:** make Task Commander retain durable project knowledge and make its task, review and context-boundary workflow sharper, borrowing selectively from Project Cairn and the Matt Pocock suite while preserving the host-neutral, documentation-first core.

## Scope

This iteration adds optional capabilities. It does not add a role, task state, required status column, external provider adapter, background hook or agent runtime.

- **Knowledge layer:** `knowledge/LOG.md`, `knowledge/topics/`, optional `ROADMAP.md`, `Cited.md`, `Reference/`; audit, branch/experiment closure and graduation candidates.
- **Window boundaries:** an explicit continue/fresh/handoff/subagent/compaction decision at phase boundaries.
- **Task shaping:** vertical tracer-bullet slices, blocking edges, single-window fit and expand–contract for wide refactors.
- **Review:** Reviewer owns the Spec axis, QA owns the Standards/behavior axis; findings stay separate.
- **Debugging:** a red-capable, deterministic, fast loop before hypotheses for hard bugs and performance regressions.
- **Retro:** optional environment-focused retrospective after completion or a major incident.
- **Versioning:** optional `Protocol version: 2` metadata and incremental adoption for existing projects.

## Key files

- New references: `references/20-knowledge-layer.md` through `references/23-protocol-upgrade.md`.
- New templates: `templates/knowledge-log.md`, `knowledge-topic.md`, `knowledge-roadmap.md`, `knowledge-cited.md`, `project-retro.md`.
- New validator: `scripts/validate-knowledge.py`, with `tests/test_knowledge_validator.py`.
- Integration: `SKILL.md`, `README.md`, `references/01`–`07`, `10`, `11`, `14`–`17`, `19`, `templates/project-status.md`, `templates/task-receipt.md`, `templates/task-continuation.md`, `templates/decision-log.md`, `agents/openai.yaml`.
- Regression guards: `tests/test_document_contracts.py`, CI syntax/help/smoke checks.

## Design boundaries

- `project-status.md` remains the only task-state source; knowledge topics never encode current task state.
- `decision-log.md` remains the authoritative ledger for user-confirmed decisions; topics summarize and point to it.
- Task receipts remain delivery evidence; LOG is a short timeline of progress.
- Engineering assets stay in the code tree; only knowledge about them enters `knowledge/`.
- No empty topic shells; create files on first trigger.
- Commander is the integration owner for shared knowledge; other roles propose deltas.
- Graduation to an external knowledge base requires explicit user confirmation; no provider adapter ships here.
- The knowledge validator checks structure, not truth, evidence or project acceptance.

## Verification

- `python -m unittest discover -s tests -q`: **163 tests ran on Windows: 159 passed, 4 skipped** on both Python 3.14.0 and 3.13.9. An independent Linux review run had 1 platform skip. Skips are platform-specific: 2 Windows symlink-privilege cases plus validator cases that run only on their matching OS (Windows file lock / POSIX surrogate filename).
- `python scripts/validate-knowledge.py --project-root .`: optional-layer smoke (absent layer is valid with a warning).
- All five CLI `--help` checks, status-template validation, status rendering and skill scanning pass.
- `git diff --check` is clean; 164 text files are UTF-8/LF without BOM; no temporary artifacts remain.
- Two independent review rounds covered protocol coherence, migration safety, review-axis ownership and validator edge cases. All blocking/high findings were fixed; the remaining items are documented limitations or low-risk test-coverage notes.
- One transient Windows file-lock failure occurred in an unrelated workflow test during a full-suite run; it passed in isolation and in the subsequent full run. This is recorded as an environment flake, not a protocol result.
- The first v2 CI run failed only on macOS because the new POSIX non-UTF-8 filename test could not create its fixture there. Commit `541784e` makes that test skip when the filesystem rejects the name; the release tag is v2.0.1 after the green CI run.
- Manual behavioral scenarios K1–K5 in `tests/behavioral-scenarios.md` cover knowledge closeout, boundary choice, two-axis review, debug loops and branch closure. They are not a live-model certification.
- A live Commander closeout smoke on an isolated synthetic project passed the knowledge path: valid LOG/topic, status Knowledge update, validator green, graduation candidate flagged, and project `Completed` correctly withheld because the delivery artifact was absent. Evidence: `tests/behavioral-results/2026-10-24-knowledge-closeout/`. This is one host/model observation, not a statistical certification.
- Final six-case behavioral smoke: run 1 (`df1c67e`) passed 5/6; case 05 failed because it modified the already accepted `slugify` and expanded its test rather than only completing the pending `truncate` work. Commit `0eb2914` added the scope-preservation rule. A fresh 05 rerun (`0eb2914`) passed with `slugify` byte-preserved, the round-1 test retained, and 8/8 tests passing. Overall: **6/6 on the final candidate**. Evidence: `tests/behavioral-results/2026-10-24-v2-final-smoke/`.

## Release points and rollback

The public remote has these relevant points:

| Tag | Commit | Meaning |
|---|---|---|
| `v1.0.0` | `588e70e` | Last clean remote baseline before the previously uncommitted reliability/onboarding batch |
| `pre-v2` | `e641299` | Reconstructed snapshot of the pre-v2 working tree (includes reliability/onboarding; excludes v2) |
| `v2.0.1` | the release commit containing this note | Current v2 release; six-case smoke 6/6 and green three-platform CI |

- Review only v2: `git diff pre-v2..v2.0.1`.
- The failed `v2.0.0` candidate tag and the redundant `snapshot/pre-v2` branch were removed after `v2.0.1` passed; commit `6a350e9` remains in `main` history. No product code changed between the candidate and `v2.0.1`; the fix was a test-fixture skip for macOS.
- Roll back to pre-v2: `git switch --detach pre-v2` or create a branch from it.
- Roll back to the last clean remote baseline: `git switch --detach v1.0.0`.
- The pre-v2 snapshot was reconstructed from the backup zip; it is a rollback snapshot, not original commit history. The local zip and `backup/pre-optimization-2026-10-24` branch are extra local safety nets, not required for remote users.
- The knowledge layer is optional, so an existing project can stop using it without a task-schema rollback.

## Deferred

- External knowledge-base providers (Obsidian/Notion/Lark) and automatic graduation writes.
- Automatic hooks, chat-end triggers and a background maintenance daemon.
- Live model certification across all hosts; token/latency measurement; six-host integration proof.
- Receipt-state machine validation (parse a structured suggested-state line rather than guessing free-form prose) as a follow-up.
- Broad protocol pruning beyond the targeted additions in this iteration.
