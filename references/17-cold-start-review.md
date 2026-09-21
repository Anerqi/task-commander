# Cold-Start Review

> Read when Commander selects cold-start review, prepares its packet, or starts/continues/recovers that Reviewer window. This file owns context isolation and staged disclosure. This is a Reviewer mode, not a new role or task state; gate selection and severity remain in `references/16-quality-gates.md`.

## Select a concrete outside perspective

Use a fresh perspective for a significant milestone, changed user journey, or suspected anchoring after repeated revisions. Record the reason, scenario, budget and required coverage in the gate brief. Routine narrow fixes normally retain targeted informed review; cold-start review is not a mandatory extra round on every task.

Assign an observable task, not just an expert title. Examples:

- First-time user: install from the shipped instructions and attempt the first handoff; record every point requiring a guess.
- Incoming maintainer: locate a rule, trace its implementation, and explain how to verify a proposed change, without modifying the deliverable.
- Failure-path tester: exercise a missing input, interrupted operation or conflicting state in an authorized disposable fixture; compare observed and promised behavior.

Cold-start review finds problems without the team's explanation. Informed review checks the full goal, constraints and integration. It complements rather than waives required informed review or QA. The same Reviewer can perform informed reconciliation in stage 2; a separate informed Reviewer is optional when justified by risk. If both run, use the same artifact snapshot and separate report paths; keep their findings separate until both initial records are saved. Both briefs name the reconciliation owner (normally the cold-start Reviewer in stage 2), required combined coverage and report-release point.

## Prepare the stage-1 packet

Commander retains the full execution contract and coordination records. Save a separate, neutral packet, for example `04_cold_start_brief.md`, containing only:

- Reviewed task ID, Reviewer mode, artifact/input versions and concrete scenario with a bounded finish line.
- Applicable original user goals, acceptance criteria and genuine corrections, expressed without the Commander's preferred verdict. Preserve their meaning and coverage; keep source provenance in the full gate contract.
- Essential domain definitions, hard constraints, expected behavior and environment/setup information needed to judge the scenario fairly.
- Explicit allowed input paths: the deliverable, normally available user documentation, relevant source/data and necessary role/runtime rules. Permission to inspect the product is not a request to read every internal project record.
- Effective permissions and their provenance, write limits, isolation/backup prerequisites, budget, and distinct stage-1 and final report paths. Reviewers may write assessment evidence only and use authorized disposable test fixtures; they do not fix deliverables or edit central records.

Keep project narrative, design rationale, execution self-assessment, prior review verdicts, known-issue lists and the Commander's hypotheses outside this packet. Withhold their contents and read-first pointers, including full execution briefs or receipts that contain them; listing them in the same prompt with "read later" is not staged disclosure. Record withheld sources in the Commander's full gate contract, not the stage-1 packet. Neutral extracts are versioned snapshots, not new sources of truth.

Never withhold safety restrictions, authorization limits, necessary acceptance criteria or known hazards needed for safe inspection. Supply these neutrally even if they reduce blindness. If a source mixes essential facts with evaluative narrative, provide a faithful scoped extract. Missing essential context calls for a neutral clarification, not guessing or declaring a defect merely because information was withheld.

User-facing documentation remains available even when it contains product claims: it is part of the deliverable under test. Treat its claims as claims to verify, not as trusted verdicts. Do not sanitize the product to manufacture a better first impression.

## Establish a real context boundary

Start a new session with no inherited project conversation, summaries or execution history. For supported subagents, disable parent-context inheritance and supply only the stage-1 packet. A different model, a role label, or "forget earlier context" in the same conversation does not establish isolation.

Check for host-injected project memory/instructions and report unavoidable exposure. Always obey applicable host instructions and safety rules; never bypass them to claim blindness. If isolation cannot be established, request a genuinely fresh user-opened window or label the assessment informed/partially exposed. A required cold-start gate stays pending until isolation is established or its contract is explicitly changed by the authorized decision-maker; do not silently count an informed assessment as cold-start completion.

During stage 1, synchronization and human answers carry only relevant neutral facts, changed inputs and operative constraints. Defer rationale and other reviewers' findings. Pause unsafe checks immediately when a new hazard is known; isolation never takes priority over safety. Apply the same packet boundary to authorized helper agents.

## Stage 1 — independent discovery

1. Read the packet and allowed inputs, then perform the assigned scenario within its permissions and budget. If additional material is needed, request the specific fact or source instead of broadly loading background, status, decision logs or past reports.
2. Record observations with stable finding IDs, artifact version, location, reproduction steps or reasoning, expected versus observed behavior, affected criterion and uncertainty. Distinguish a demonstrated defect from a question requiring background. No minimum finding count is required.
3. Save the independent record, for example `04_cold_start_initial.md`. Include inputs actually read, any exposure to withheld material, methods, coverage, untested areas and blockers. Even a zero-finding result states its coverage and limits.
4. Return the record and stop for Commander handoff. This is a checkpoint, not a gate Pass or project acceptance. Do not read stage-2 materials in the same turn. Commander verifies the record exists before releasing additional context in a later message.

If evaluative context leaks before the record is saved, disclose its source and timing and retain the observations as partially exposed evidence. Commander applies the isolation fallback above; restarting in the same informed window cannot restore a cold first impression.

## Stage 2 — informed reconciliation

After the independent record is saved, Commander sends a separate continuation with relevant background, full acceptance contract, design rationale, prior evidence and any independently saved informed findings. Reconcile against the full required review scope; the cold scenario alone is not proof that every criterion passed. Identify gaps and perform only the additional checks needed, reusing fresh unchanged evidence under `references/16-quality-gates.md`.

Preserve the stage-1 record unchanged. In the final report, map every initial finding ID to one of: confirmed, refuted by evidence, user-accepted trade-off, or unverified. Cite the evidence and explain every withdrawal or severity change. "Intentional design", an Executor's confidence or a previous Pass alone cannot refute a finding. A trade-off requires traceable user authority and cannot silently waive an essential criterion or safety requirement. Preserve newly discovered issues separately.

Use bounded deciding checks for factual disagreements; ask the user for actual scope/risk decisions. Do not decide by majority vote or ask reviewers to converge merely because another report passed. Apply normal blocking/non-blocking rules and report a final Pass / Conditional pass / Fail with essential gaps explicit. Commander alone accepts the task through the existing state machine. Stage-1 checkpointing and stage-2 reconciliation do not create new task states or consume implementation revision rounds by themselves.

## Gate conclusion and revision timing

When cold-start and informed assessments are combined for one Reviewer gate, label both initial reports provisional, including any provisional Pass/Fail. Keep the task In Review while discovery/reconciliation is active; an initial report alone does not trigger Needs Revision, an implementation revision round, or acceptance. The named reconciliation owner produces the final gate report covering both streams; Commander applies its evidenced conclusion through the normal state rules. Separately required gates, such as QA, retain their own requirements and are not waived by this combination.

Act on credible safety hazards immediately: pause affected operations and use Blocked with its actual pre-block state/resume condition when needed. This pause is not an implementation revision round and does not require disclosing evaluative narrative to the other reviewer. If an actionable gate failure was recorded prematurely and later refuted, preserve that history and the refuting evidence. Resume reassessment using the legal Needs Revision -> In Progress -> In Review route before normal gate/acceptance transitions; do not jump to Completed, erase the transition, invent code changes, or count evidence-only reassessment as an implementation correction. Actual corrective work still follows the normal revision budget.

## Continuation and recovery

After stage 2, reuse the now-informed review window for fixes and affected regressions. Do not call it cold again. A later genuinely new first-impression check needs a fresh isolated window and a reason; do not repeat blind reviews until one passes.

For a lost stage-1 window, recover with only the neutral packet, allowed artifact versions and any stage-1 checkpoint; this is resumed discovery, not a new independent sample. Keep withheld records out of recovery prompts. For a lost stage-2 window, include the preserved initial record and disclosed context, and resume as informed reconciliation. Record mode, stage, exposure, input versions, report paths and disposition evidence in the receipt per `templates/task-receipt.md`; acknowledge only the context actually received.
