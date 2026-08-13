# Built-in Methodology Fallback

> Read this file only when you need to interview and clarify a project and its terms, write or revise agent-facing documents, re-express a misunderstood exchange, or turn an unanswerable decision into a questionnaire. When the work is pure execution without interviews or agent-facing writing, skip loading it.

Distilled from the methods of the four external skills (grill-with-docs, writing-for-agents, wait-what, to-questionnaire); used as the zero-dependency fallback when those skills are not installed.

## Which module for what

| Module | Trigger | Responsibility | Output form |
|---|---|---|---|
| grill-with-docs | Aligning ideas with an existing domain model and documented decisions; context interviews, requirement clarification, term normalization | Deep-dives round by round into goals, scope, terms, scenarios, boundaries, and contradictions, consolidating as it goes | Confirmed and open lists; term table updates; ADRs under the conditions in step 3 |
| writing-for-agents | Creating or editing any agent-facing document (references/, SKILL.md, AGENTS.md, etc.) | Constrains the document's pointer wording, information hierarchy, completion criteria, and single source of truth | A compliant target document |
| wait-what | The user says they do not understand, asks for a redo, or answers off-topic; a question rests on undefined terms and implicit context | Re-expresses the same question as concise language with context, using standard terms | One re-expression + the original question |
| to-questionnaire | Answers or decisions sit with a third party; the current user cannot answer them | Turns a knowledge gap into an asynchronous questionnaire; no guessing forced on the user | A `to-questionnaire-<slug>.md` questionnaire file |

When the four modules are composed, the orchestration order and document sources of truth follow `references/10-context-orchestration.md`; this file is their zero-external-dependency built-in fallback.

## 1. grill-with-docs - structured interview and term clarification

### Trigger

- You need to turn a vague idea into executable goals before doing anything; a plan needs to align with an existing domain model and documented decisions.
- The user's wording conflicts with existing terms, is vague, or domain relations are unverified.

### Steps

1. Understand the current state. Read the project structure and documents first: CONTEXT.md, decision-log.md, existing background documents, and code; when the project already uses ADRs, read them as well. Record facts confirmable from files directly; do not ask the user.
2. Deep-dive question by question. Ask one question at a time; wait for the answer before the next. Every question must:
   - Check the term table: point out conflicts between the user's wording and existing standard terms immediately.
   - Sharpen vague language: when the user is vague or polysemous, propose precise standard-term candidates and ask the user to confirm.
   - Test with concrete scenarios: give bounded scenarios to test whether abstract claims and domain relations hold.
   - Cross-check documents: when the user describes "how it works", verify it against the existing documents.
   - Offer recommended answers: every question comes with a recommended answer or recommended options; never leave the user to answer from scratch.
   - Resolve dependencies that would block later questions first; do not ask what documents can answer.
3. Consolidate as you go. For every answer, judge its category (goal/scope/constraint/term/decision/open) and write it to the matching source of truth:
   - Update the term table immediately once a term is confirmed (CONTEXT.md); record terms and domain relations only, never implementation details.
   - Do not create ADRs by default; record one only when the project already uses ADRs and the decision is simultaneously hard to reverse, surprising without context, and a real trade-off, including background, decision, and reason. `decision-log.md` is the sole ledger of project decisions and keeps the decision id, final conclusion, and ADR path; on conflict it wins.

### Output form

- Confirmed and open lists (goals, scope, terms, decisions, boundaries), each item with status and owning document.
- Updated term table; new ADR files only under the conditions in step 3.

## 2. writing-for-agents - standards for agent-facing documents

### Trigger

- Creating or editing any document an agent consumes: references/, SKILL.md, AGENTS.md, documents reached by a pointer.

### Steps

1. Write the pointers first, then the body. Context pointers (document descriptions, load conditions) do the triggering: state "what the material is + which branches should trigger reaching it"; leave one trigger word per branch and cut identity the body already carries. Pointer wording decides trigger reliability; a must-have behind a weak pointer is a variance bug - sharpen the wording first, and inline the material only if sharpening fails.
2. Arrange content on the information hierarchy, top down: in-file steps (the primary tier; ordered actions) -> in-file reference (definitions and rules to consult on demand) -> disclosed reference (pushed to a separate file, loaded via a pointer on demand). Progressive disclosure: what every branch needs stays in the main file; what only some branches reach goes behind a pointer; especially for step-bearing documents, or reference buries the steps and following them becomes a coin flip.
3. Co-locate related topics. A concept's definitions, rules, and caveats stay under one heading instead of being scattered; grouped material reads like agent-facing documentation, scattered material does not.
4. Give every step a completion criterion. Criteria must be clear (done vs. not-done must be distinguishable, preventing premature completion) and demanding ("every modified model accounted for" beats "produce a change list"). The strongest criteria are checkable and exhaustive. When a criterion cannot be sharpened and premature completion is observed, split the sequence and hide the later steps; that works only across a real context boundary (hand-off, subagent dispatch) - an inline call hides nothing.
5. Anchor behavior with leading words. Prefer compact words already in model pretraining, repeated as tokens rather than coined; collapse multi-site restatements into a single word. Prompt the positive - state the target behavior instead of prohibiting; "do not do X" drags the banned behavior into context and amplifies it.
6. Prune every line. Single source of truth: one authoritative place per meaning; do not restate what the environment can answer (the environment is a source of truth; restating it is a cache - cache only what documents cannot find: unwritten conventions, the reason behind a choice, gotchas no config confesses); check every line for relevance and delete what went stale; delete whole sentences that are no-ops (things the model already does by default).

### Output form

- A compliant target document: a load-condition block, checkable completion criteria, a body organized by the information hierarchy, and single-source-of-truth references.

## 3. wait-what - re-expressing a message that did not land

### Trigger

- The user says they do not understand, asks for a redo, or answers off-topic.
- The current question rests on undefined terms, implicit premises, or cross-file context, and the user cannot understand it on their own.

### Steps

1. Stop the current probing; acknowledge that the current expression did not land.
2. Re-express the same question instead of asking a new one:
   - Add a short necessary context passage, enough for the user to understand on their own; not a page.
   - Use short sentences, take terms from the standard term table, and introduce no new words.
3. Still ask only the original question; never attach a second question to the re-expression.

### Output form

- One context-carrying re-expression in standard terms + the original question.
- Completion criteria: the user can answer the original question, or explicitly states which context passage is still missing.

## 4. to-questionnaire - turning unanswerable decisions into a questionnaire

### Trigger

- The user explicitly says the answer or decision sits with a client, business owner, expert, vendor, or other third party, and the current user cannot answer it.
- At that point stop probing the fact and switch to a questionnaire; a questionnaire is an information-collection vehicle, not a source of truth for facts.

### Steps

1. Interrogate the sending side, not the subject. Confirm only two things with the current user, one exchange round each:
   - Who receives it: role, expertise, relationship with the user - this decides the questionnaire's tone and how much context it must carry. Completion criteria: know who the recipient is and what they have that the user lacks.
   - What to get back: the list of decisions or facts the user cannot resolve alone and must obtain from the other side. Completion criteria: a concrete list of "what the user must be able to decide or do when they leave".
2. Write the questionnaire against the knowledge gap between recipient and user, with this structure:
   - Title and purpose: why the questionnaire exists, what decision sits on it.
   - A one-line sender/recipient/use row: From, To, How your answers will be used.
   - A Context section: enough for an uninvolved recipient to understand the background; enough to answer well, not a page.
   - How to answer: deadline and rough effort; note that partial answers and "I don't know" are equally useful.
   - Topic groups: one `##` per topic, questions ordered by importance descending (an asynchronous questionnaire may only get one round); each question holds one idea, never compounds, with answering blank lines below, and a one-line "why this matters" only where misunderstanding or a flippant reply is likely.
   - Closing safety net: "What else should we know?".
3. Write it to `to-questionnaire-<slug>.md` (slug from the topic) and report the file path. Completion criteria: the file exists and every item in step 1's list is covered by a corresponding question.

### Output form

- The questionnaire file path.
- Until the reply arrives, all questionnaire content is marked open, never written as confirmed facts; after the reply, return to the matching flow and merge the results.
