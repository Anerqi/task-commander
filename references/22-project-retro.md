# 22 - Project Retrospective and Environment Improvement

> Optional after project completion, a major incident, or a milestone with unexpected friction. The goal is to improve the environment for the next run, not to grade people or rewrite the deliverable.

## Trigger

Run a lightweight retro when:

- the project reaches `Completed` and the user wants to capture lessons;
- the same review/QA failure repeats across tasks or rounds;
- a serious incident, data scare or recovery event occurred;
- a milestone took far more coordination than expected and the cause is likely environmental.

Do not run a full retro after every small task. A short LOG entry may be enough.

## Steps

1. **Read primary sources.** Use current status, `decision-log.md`, `knowledge/LOG.md`, relevant topics, receipts, review/QA findings, and the actual artifacts. Do not rely on memory of the conversation.
2. **Find environment candidates.** Look for:
   - **Navigation**: the agent took too long to find a file, rule or decision; a pointer or index would help.
   - **Automated checks**: a mistake could have been caught by a lint, type check, test, schema check or CI gate. Prefer a deterministic check over another prose rule.
   - **Coding/project standards**: a reviewer missed a judgment call; should a rule be added, clarified or removed?
   - **AGENTS.md**: is it too long, stale, or full of no-ops? Move navigation to pointers; move mechanical rules to checks.
   - **Tool economy**: an expensive or repeated tool call could be replaced by a script, cached artifact or better pointer.
   - **Information access**: a missing log, read-only service, test database or browser capability blocked good work.
3. **Classify the fix.** A mechanical mistake (a fixed pattern, forbidden API, import shape, file-location rule) should become a deterministic check. A judgment call belongs in `AGENTS.md`, a coding-standards document or a reviewer rule.
4. **Propose, do not silently change.** Present concrete candidates with observation, evidence, proposed change, owner and expected effect. The user confirms rule changes and external writes.
5. **Record and follow through.** Add a short `knowledge/LOG.md` entry when the layer exists; otherwise record the retro in a receipt or the next status note. Create a linked task or successor phase for accepted changes. If the project is already `Completed`, keep that terminal history and start new work as a new phase/task; do not rewrite the completed record. Re-run the retro only for new evidence, not to restate the same findings.

Use `templates/project-retro.md` for the working record. The retro is not a new task state and does not replace project Acceptance; it happens after the triggered milestone or completion.

## Boundaries

- Improve the environment, not the person. Avoid blame and vague advice.
- Do not turn every finding into another rule. A rule that does not change behavior is a no-op; delete it or make it a check.
- Do not edit `AGENTS.md`, templates or shared records without confirmation.
- Do not claim a change improved outcomes without evidence. Record it as a proposal, then observe subsequent work.
- Do not silently graduate project knowledge to an external knowledge base; that is a separate human-confirmed action under `references/20-knowledge-layer.md`.

## Completion criteria

The retro produces a small set of concrete environment candidates, each classified as mechanical or judgment, with an owner and disposition. Accepted changes are recorded; deferred or rejected candidates retain a reason. When the knowledge layer exists, it has one short retro entry; otherwise the result is recorded in a receipt or status note. Any follow-up work has a linked task, successor phase or named owner.
