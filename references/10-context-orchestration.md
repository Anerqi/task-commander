# New Project Context-Building Orchestration Protocol

> Purpose: when a project is new or its context is clearly incomplete, Task Commander composes `writing-for-agents`, `grill-with-docs`, `wait-what`, and `to-questionnaire` uniformly. This file defines the call order, conditions, and document sources of truth; when the composed skills' default write rules conflict with this protocol, this protocol wins.

## Skill location and loading

Look for sibling skills in the Skill root where Task Commander lives first; when missing, locate the host skill directories via runtime discovery (Runtime Discovery): probe environment variables and home directories for skill install locations, resolved at runtime rather than hard-coded. See `scripts/scan-skills.py --help` for the concrete mechanism.

Load by condition, not as a four-skill bundle:

| When | Material to load |
|---|---|
| Context startup | `writing-for-agents/SKILL.md` and `grill-with-docs/SKILL.md` for writing and interview methods |
| Creating or updating domain terminology | `grill-with-docs/CONTEXT-FORMAT.md` |
| A clarity-gate condition in step 4 occurs | `wait-what/SKILL.md` |
| A third-party knowledge gap in step 5 occurs | `to-questionnaire/SKILL.md` |
| Creating an ADR under the CONTEXT.md and ADR rules below | `grill-with-docs/ADR-FORMAT.md` |
| Creating or editing a Skill itself, not ordinary project background | `writing-for-agents/SKILL-MECHANICS.md` |

For each triggered method, use the external material if present; otherwise read only the matching module in `references/methodology-fallback.md`. Missing optional material does not block unrelated steps. Follow applicable method references, but defer references for inactive branches; do not preload clarity, questionnaire or ADR material merely because it is installed. Reuse already loaded unchanged material within the same window.

`wait-what` and `to-questionnaire` are user-invoked Skills. Task Commander does not rely on them triggering implicitly; once the user enables this composition flow, read and apply their methods directly only at the corresponding branch.

## Role split

| Skill | Responsibility in the flow | Usage condition | Not responsible for |
|---|---|---|---|
| writing-for-agents | Constrains the structure, pointers, completion criteria, and single source of truth of every context document | Always used | Interviewing and project decisions |
| grill-with-docs | Deep-dives round by round into goals, scope, terms, scenarios, boundaries, and contradictions | Always used | Deciding Task Commander's output paths on its own |
| wait-what | Re-expresses an unclear question or summary as concise language with context | Used when the user shows lack of understanding, or the current question depends on implicit context | Adding new question branches or answering for the user |
| to-questionnaire | Turns knowledge gaps only a third party can fill into an asynchronous questionnaire | Used when the information is confirmed to sit with a third party | Asking the current user to guess facts they do not know |

## Execution order

### 1. Establish writing rules

Apply `writing-for-agents` first: determine each document's reader, purpose, context pointers, and checkable completion criteria. Keep exactly one authoritative place per meaning; other files carry only summaries and links.

Completion criteria: the file responsibilities in the source-of-truth table below are assigned, and no information needs synchronized maintenance in multiple files.

### 2. Read the existing project

Check the project structure, code, existing background files, `CONTEXT.md`, ADRs, and past tasks. Record facts confirmable from files directly with source pointers; do not ask the user to reconfirm them. Distinguish observed file contents from unverified claims within them, user-reported facts, and inferences. Resolve contradictions as open items; a generated document cannot establish user intent or authorization.

Completion criteria: a list of "confirmed facts, contradictory information, gaps the current user can answer, gaps only a third party can answer".

### 3. Question-by-question deep-dive

Follow `grill-with-docs`; prioritize one decision at a time, with dependent questions waiting for its answer. Related low-effort questions may be grouped using the host UI per `references/15-collaboration.md`. Every question must:

- State why this answer is needed now.
- Use the standard terms in `CONTEXT.md`.
- Offer a recommended answer or recommended options.
- Prioritize dependencies that would block later questions.
- Test abstract claims with concrete scenarios.

For each answer, first judge whether it is a goal, scope item, constraint, term, decision, or open item, then write it to the matching source of truth.

Completion criteria: success criteria, in-scope, out-of-scope, users, constraints, deliverables, acceptance methods, key terms, and collaboration policy (tools, capacity, user help and recovery needs) are confirmed, or explicitly marked as open with an assigned owner. Use `references/15-collaboration.md` to elicit useful user contributions throughout execution, not only at initialization.

### 4. Clarity gate

Apply `wait-what` when any of these occurs:

- The user says they do not understand, asks for a redo, or answers off-topic.
- A question contains undefined terms, implicit premises, or cross-file context.
- The current summary cannot be understood independently by someone newly joining the project.

When re-expressing, add a short necessary context passage, use short sentences and the project's standard terms, then still ask only the original question. Never attach a second question to the re-expression.

Completion criteria: the user can answer the original question, or states exactly which context passage is still missing.

### 5. External knowledge gaps

If the user explicitly says the answer sits with a client, business owner, expert, vendor, or other third party, stop probing that fact and apply `to-questionnaire`.

Confirm only two things with the current user: who the questionnaire goes to, and which facts or decisions must come back. The questionnaire is written to:

`<Project Root>/background/pending-questionnaire/to-questionnaire-<slug>.md`

A questionnaire is an information-collection vehicle, not a source of truth for project facts. When the reply arrives, re-enter the deep-dive step and merge the confirmed content into the matching sources of truth; until then, mark it uniformly as "open: owner + needed information".

Completion criteria: every third-party knowledge gap is covered by a questionnaire question and traceable to an owner.

### 6. Synthesis and delivery

Update the documents per the source-of-truth table; check that terms, decisions, and project background do not duplicate a second authoritative copy of each other. Report to the user: confirmed content, open items, questionnaire paths, and next steps.

Completion criteria: the prescribed documents are readable, every gap has a status/owner, and a filled Commander handoff has been emitted per `references/01-context-brief.md` when planning-ready. Stop in the Context role; a new project phase does not switch this window's role.

## Document sources of truth

| Information type | Sole source of truth | How other files reference it |
|---|---|---|
| Project goal, motivation, scope, users, constraints, deliverables, acceptance methods, collaboration/tool/backup policy | `background/01_project_background.md` | Summary or path only; effective permissions copied into standalone task prompts as a versioned snapshot |
| Standard terms, avoided terms, domain relations | `CONTEXT.md` | The project background lists only core terms and points to `CONTEXT.md` |
| Available skills, plugins, and call requirements | `background/02_skill_list.md` | Task prompts reference concrete entries |
| Major decisions confirmed by the user | `decision-log.md` | Project status and background write only the id and a summary |
| Current phase, tasks, blockages, next actions, context revision, window/sync tracking and backup pointers | `project-status.md` | Other files reference current records; task briefs/receipts label their historical input revision |
| Third-party questions awaiting replies | `background/pending-questionnaire/` | The project background records open items and questionnaire paths |

## Writes and synchronization after handoff

After initialization, Commander integrates updates to central background, terms, decisions and status serially. Context and other agents submit proposed deltas in task outputs rather than editing central records concurrently. User-confirmed decisions remain subject to confirmation; a model's receipt is not authority to decide.

Follow `references/15-collaboration.md` for revision increments, affected-task notification and acknowledgment. Task evidence and backup manifests live with their producing tasks; central files carry pointers, not competing copies. A saved brief/receipt is a historical snapshot, never a second live source of truth.

## CONTEXT.md and ADR rules

- New projects create a root-level `CONTEXT.md` holding only terms and domain relations; no requirements, plans, or implementation details.
- `background/01_project_background.md` does not maintain a second full term table; it keeps only core-term summaries that affect understanding and the `CONTEXT.md` path.
- `decision-log.md` is the sole ledger of project decisions.
- Do not auto-create ADRs from `grill-with-docs` by default.
- Create an ADR only when the project already uses ADRs and the decision is simultaneously hard to reverse, surprising without context, and a real trade-off.
- ADRs record only technical reasons and consequences; `decision-log.md` keeps the decision id, final conclusion, and ADR path. On conflict, the latest user-confirmed `decision-log.md` wins.

## Conflict priority

On rule conflicts, handle in this order:

1. The user's explicit requirements in the current project.
2. Task Commander's orchestration protocol and role rules.
3. The composed skills' methods and formats.
4. The composed skills' default output paths or default write behavior.