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

- `python -m unittest discover -s tests -q`: **162 tests ran: 158 passed, 4 skipped** on both Python 3.14.0 and 3.13.9. Skips are 2 Windows symlink-privilege cases plus platform-specific validator cases (Windows file lock / POSIX surrogate filename) that run only on their matching OS.
- `python scripts/validate-knowledge.py --project-root .`: optional-layer smoke (absent layer is valid with a warning).
- All five CLI `--help` checks, status-template validation, status rendering and skill scanning pass.
- `git diff --check` is clean; 143 text files are UTF-8/LF without BOM; no temporary artifacts remain.
- Two independent review rounds covered protocol coherence, migration safety, review-axis ownership and validator edge cases. All blocking/high findings were fixed; the remaining items are documented limitations or low-risk test-coverage notes.
- One transient Windows file-lock failure occurred in an unrelated workflow test during a full-suite run; it passed in isolation and in the subsequent full run. This is recorded as an environment flake, not a protocol result.
- Manual behavioral scenarios K1–K5 in `tests/behavioral-scenarios.md` cover knowledge closeout, boundary choice, two-axis review, debug loops and branch closure. They are not a live-model certification.
- A live Commander closeout smoke on an isolated synthetic project passed the knowledge path: valid LOG/topic, status Knowledge update, validator green, graduation candidate flagged, and project `Completed` correctly withheld because the delivery artifact was absent. Evidence: `tests/behavioral-results/2026-10-24-knowledge-closeout/`. This is one host/model observation, not a statistical certification.

## Rollback

Before this iteration, the working tree was archived at:

- `../task-commander-backup-2026-10-24-pre-optimization.zip` (full working tree, excludes `.git`/caches)
- Git branch `backup/pre-optimization-2026-10-24` (HEAD at the time)

To revert, extract the zip over the repository or diff against the backup branch. The knowledge layer is optional, so an existing project can also stop using it without a task-schema rollback.

## Deferred

- External knowledge-base providers (Obsidian/Notion/Lark) and automatic graduation writes.
- Automatic hooks, chat-end triggers and a background maintenance daemon.
- Live model certification across all hosts; token/latency measurement; six-host integration proof.
- Broad protocol pruning beyond the targeted additions in this iteration.
