# 20 - Project Knowledge Layer

> Optional durable knowledge for projects that outlive one task or one window. It stores stable conclusions, not task state. Read when initializing a multi-session project, recording a conclusion or lesson, auditing accumulated knowledge, closing an experiment, or considering graduation.

## Why this layer exists

Task Commander already records current task state, delivery evidence and user-confirmed decisions. Those records answer "what is happening now?" They do not reliably answer "what have we learned, and which conclusion is still true?" Without a separate layer, that knowledge is repeatedly reconstructed from chat history or buried in long receipts.

The knowledge layer is **optional**. A one-shot or purely local task may need none of it. For a project that spans sessions, windows or contributors, create it on the first durable conclusion; do not pre-build empty topic files.

## What belongs where

| Information | Sole source of truth | Other files |
|---|---|---|
| Current task state, phase, blockers, coordination | `project-status.md` | Knowledge notes may point to it; do not duplicate current status |
| User-confirmed major decisions | `decision-log.md` | Topics summarize and point to the decision ID |
| Stable technical conclusions, lessons, procedures | `knowledge/topics/<topic>.md` | LOG and task receipts point to the topic |
| Chronological progress summary | `knowledge/LOG.md` | Short entries with pointers; no long conclusions |
| Delivery evidence | Task result files and receipts | Topics cite artifact versions and receipt paths |
| Project context, scope, constraints, collaboration policy | `background/01_project_background.md` | Other files point to it |
| Project-wide behavioral rules | root `AGENTS.md` | Knowledge notes do not replace project rules |
| External knowledge actually used | `knowledge/Cited.md` | Pointers only; never copy the external body |

Do not create a second competing summary. If a topic needs the full reasoning, it points to the artifact, decision or receipt that owns it.

**Engineering assets stay in the code tree.** A schema, configuration, source file or executable specification is not knowledge about the project; it is a project asset. Only the reasoning, pitfalls, decisions and reusable lessons about such assets belong in `knowledge/`.

## Layout and creation triggers

```text
knowledge/
  LOG.md                  # created at initialization for a multi-session project
  ROADMAP.md              # optional; only when goals outlast one session
  topics/<topic>.md       # created on the first stable conclusion or lesson
  Cited.md                # created on first external adoption
  Reference/              # optional raw external inputs; append-only
```

**Creation trigger:**

- **New project:** Context may create `knowledge/LOG.md` at initialization when the project is expected to span multiple sessions or the user wants durable knowledge; it may also initialize a short `ROADMAP.md` when goals outlast the current session.
- **Existing project:** do not create a layer during a routine context refresh. Start with `knowledge/LOG.md` on the first durable conclusion and after user confirmation; preserve all existing records and history. No task-schema migration is required.
- In both cases, do not pre-create topic files, `Cited.md` or `Reference/`; create each on its first real trigger.
- Before creating the directory, check for an existing `knowledge/` that already serves another purpose. If it is unrelated, ask the user and choose a different directory or explicitly confirm adoption; do not overwrite it.
- `knowledge/Reference/` holds raw external inputs the project owns but did not author. It is not for copied knowledge-base bodies or generated summaries.

Templates live in `templates/knowledge-log.md`, `templates/knowledge-topic.md`, `templates/knowledge-roadmap.md` and `templates/knowledge-cited.md`.

## Write ownership

After initialization, the **Commander is the integration owner** for shared knowledge records, consistent with its ownership of status, decisions and shared background.

- Executor, Reviewer, QA, Risk Manager and other roles propose knowledge deltas in their receipts or task output. They do not concurrently rewrite shared topics or LOG.
- A task explicitly assigned as knowledge maintenance may draft or update a topic within its brief, but Commander still reconciles conflicts and records the integration.
- `AGENTS.md` remains project-owned: any role may propose a rule change, but new or changed rules require user confirmation before writing.

## Maintain the layer

### LOG entries

After a substantive milestone, decision, experiment result or incident, add one entry **at the top** of `knowledge/LOG.md` (newest first):

- What changed, was decided, or was learned.
- Evidence, receipt or artifact pointer.
- Affected task/topic pointer.

Keep an entry under about 20 lines. LOG is a timeline, not a place for full conclusions.

### Topic notes

When a stable conclusion, lesson, procedure or reusable pattern appears, create or update `knowledge/topics/<topic>.md`:

- Use the frontmatter required by `templates/knowledge-topic.md`.
- Keep `summary` as a one-line conclusion for retrieval.
- Use `contains` for the kinds of knowledge present: `decision`, `experience`, `lesson`, `procedure`, `reference` or `open_question`.
- Keep only body sections with real content. Include `Background` and `Current conclusion` when they carry content; evidence, practice, boundaries and open questions are added only when useful. A topic must still contain a real conclusion somewhere; a title-only or heading-only shell is not valid.
- Correct an old conclusion in place and add a LOG pointer to the revision. Do not silently overwrite history.
- A topic may point to a decision ID, artifact, receipt or source; it must not become a second decision ledger.

### External knowledge

When an external note or source actually shaped a conclusion or output, add a pointer row to `knowledge/Cited.md`: source, adopted/adapted conclusion, where it applies and a link. Reading a source without adopting it does not earn a citation.

## Conflicts and source priority

Handle conflicts in this order:

1. A user-confirmed decision in `decision-log.md` wins over a topic summary. Record the conflict, preserve the verified evidence that led to the earlier conclusion, mark the topic as superseded or point it to the decision, and do not erase the evidence.
2. A current stable conclusion in `knowledge/topics/` wins over an older LOG entry; flag the stale LOG entry.
3. `AGENTS.md` wins for project behavior and hard constraints; record the conflict and ask the user rather than silently changing a rule.
4. Verified artifact/evidence wins over prose claims.
5. `project-status.md` wins for current task state; never infer task completion from a topic or LOG.
6. Receipts and briefs are historical snapshots; cite their artifact/version rather than treating them as current truth.
7. If two topics conflict and neither is clearly newer, record an explicit open question and ask the user rather than silently choosing.

## Audit

Run a knowledge audit at a milestone and before project Acceptance when the layer exists. Use `scripts/validate-knowledge.py` for structure, then apply judgment:

```text
<python> <skill-root>/scripts/validate-knowledge.py --project-root <project-root>
```

The validator checks layout, frontmatter fields, enum values, LOG ordering and basic shell/empty-file warnings. It does not judge truth, contradicting conclusions or whether a topic is worth keeping.

Human/Commander audit checklist:

- LOG entries are short, newest-first, and contain pointers rather than long conclusions.
- Topics have useful summaries and frontmatter; no empty topic shells.
- Contradictions between topics, decisions and older LOG entries are resolved or recorded as open questions.
- Repeated decisions or solved pitfalls have a topic instead of existing only in chat or receipts.
- Pointers to receipts, artifacts and external notes are readable and current.
- Graduation candidates are recorded but not silently promoted.
- Closed experiments or branches have a knowledge disposition.
- The audit itself gets one short LOG entry.

A knowledge audit is not a new task state and does not replace Reviewer/QA evidence. It is a project-level closeout check; if it finds required work, create a linked task instead of inventing a transition.

## Branch and experiment closure

Before merging, abandoning or rolling back an exploration branch or experiment, classify each knowledge-bearing change:

- **discard** — dead end or superseded noise; do not bring it into the main knowledge.
- **merge-to-knowledge** — a validated negative result, decision or lesson still worth keeping; distill it into a topic and add a LOG pointer.
- **graduation candidate** — reusable outside this project; flag it for human confirmation.
- **archive pointer** — a process artifact worth keeping; record its path instead of copying its body.

`main` receives distilled current truth, not the branch's whole exploration history. A reverted branch does not erase a validated lesson.

## Graduation candidates

A topic may be a graduation candidate when it is:

- verified in the project, not merely guessed;
- reusable outside this project;
- abstracted from local implementation details;
- safe to move to the target knowledge base;
- traceable to its source.

Mark `graduation_status: candidate` only after that judgment. Commander proposes the candidate to the user; the user confirms before any external write. This Skill does **not** include a knowledge-base provider adapter or automatic external write. The project topic remains the local current truth; a future external note, if created, becomes the cross-project copy.

## AGENTS.md navigation

When the layer exists, the root `AGENTS.md` should state the reading order and boundaries, not duplicate the protocol:

```text
Read AGENTS.md -> knowledge/ROADMAP.md (if present) -> recent knowledge/LOG.md entries -> relevant knowledge/topics/ -> task brief.
```

Also state that topics are stable current truth, LOG is summary/pointer history, `decision-log.md` owns confirmed decisions, and engineering assets stay outside `knowledge/`. Keep the file concise and point to this reference instead of pasting it.

## Completion criteria

- The layer is either intentionally absent or has a readable LOG and any topics have valid frontmatter using the documented enums.
- No empty topic shells, copied external bodies or duplicated current task status exist.
- Stable conclusions have a current location and a named integration owner (Commander); conflicts are resolved or explicit.
- A milestone/Acceptance audit has run when the layer exists, with its result recorded.
- Any graduation candidate is awaiting explicit user confirmation, not silently published.

## Iron rules

- Never fabricate a conclusion, source or human confirmation.
- Never let `knowledge/` become a second task-status file.
- Never silently overwrite a confirmed decision or a prior conclusion.
- Never copy a whole external knowledge note into the project; link to it.
- Never auto-publish to an external knowledge base.
