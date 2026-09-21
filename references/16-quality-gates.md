# Risk-Based Quality Gates

> Read when choosing acceptance gates, reviewing a delivery, handling a failed check, or launching exploratory alternatives. This file owns review effort, evidence reuse, and stopping rules.

## Choose gates before dispatch

Every task brief states its risk, deliverable version, checkable acceptance criteria, and required Reviewer/QA gates. Choose by impact and reversibility, not by task length.

| Risk / task type | Default evidence and gates |
|---|---|
| Low risk, reversible, narrow scope | Executor self-check plus Commander light acceptance; independent Reviewer/QA may both be waived with a reason |
| Standard delivery | Use Reviewer for reasoning/compliance/design risks, QA for executable or recomputable behavior; use both only when both risks justify it |
| High risk, sensitive data, destructive or hard-to-reverse change | Independent review and relevant QA; verified backup before mutation when data may be lost; critical checks cannot be waived merely to save time |
| Exploration / feasibility spike | Bounded question, time/resource budget, isolated outputs, method, observed result, and next-step recommendation; a negative result can satisfy the exploration criteria |

Even waived gates must be explicit. Use the existing legal route through Awaiting Acceptance; never jump from In Progress to Completed. A passed experiment does not certify a production implementation. Experiment completion means its question was answered with evidence, not that its hypothesis succeeded.

Freeze acceptance scope at dispatch. New polish suggestions become follow-up backlog items, not surprise acceptance requirements. A newly discovered serious safety/correctness issue may block release; identify its evidence and impact and explicitly revise the plan rather than silently moving the goalposts.

## Select review context

Record informed or cold-start mode before dispatch; informed review is the default. Consider cold-start review for significant milestones, changed user journeys, or suspected anchoring after repeated revisions, rather than every small fix. `references/17-cold-start-review.md` owns the neutral packet, real context boundary, independent checkpoint and later informed reconciliation. It is a Reviewer mode, not an additional role or state, and it never replaces required QA or full-scope review coverage.

When using separate cold-start and informed reviewers, preserve both initial assessments before sharing findings. Neither reviewer follows the other's verdict as a premise. Stage 1 alone cannot satisfy the gate: assess the final reconciled report against all required criteria, not just the outside-perspective scenario. For a combined Reviewer gate, both initial reports are provisional; use the named reconciliation owner's final report for the gate decision and revision timing per `references/17-cold-start-review.md`. Pause unsafe work immediately. Do not claim a required cold-start check ran if isolation was unavailable; use that protocol's explicit fallback.

## Divide the checks

- Executor: perform the relevant self-check once for the current delivery; provide commands/results or source evidence.
- Reviewer: inspect reasoning, scope, design, compliance, and material risks. Reference existing valid test evidence instead of rerunning it automatically.
- QA: derive checks from acceptance criteria and realistic success/failure scenarios, then execute or recompute relevant results. An Executor's test list is evidence, not the whole test plan. Do not repeat the entire design review.
- Commander: match criteria to evidence, verify identity/freshness and conclusions, and make the acceptance decision. Do not recreate Reviewer/QA work without an identified evidence gap.

Independent review means an independent assessment of the evidence, not mandatory duplication of every command. If reviewers disagree, identify a falsifiable disputed claim and run a bounded deciding check or ask the user for a scope/risk decision; do not cycle reviewers indefinitely.

## Evidence reuse and invalidation

A reusable check records: check ID/criterion, artifact and relevant input versions, environment/tool or source/date, method, result, evidence path, and checker. Include dirty changes when using Git identifiers. For mutable online sources, define a freshness requirement; missing version or freshness information is a gap, not a presumed pass.

Reuse a passed check when its artifact, relevant dependencies/configuration/environment, and freshness assumptions are unchanged. Invalidate only affected checks plus necessary regression coverage. A shared interface/dependency change can invalidate checks outside the directly edited file; explain the impact boundary. Repeat a check for a concrete reason such as changed inputs, stale sources, flaky output, missing evidence, or a high-risk independent reproduction requirement.

After a targeted fix, check the fixed issue and impacted regressions; previously accepted unaffected criteria stay accepted. Store evidence per revision or preserve history instead of overwriting the only proof of a prior conclusion.

## Findings and stopping

For every assessment, distinguish personally inspected/executed checks, reused evidence and unverified claims. State coverage and limitations even when there are no findings; require no minimum issue count. Project narrative, intentional design and prior passing verdicts alone do not establish correctness or refute a demonstrated issue.

Classify each finding with an ID, evidence location, affected criterion, severity, and requested action:

- **Blocking**: breaks an agreed essential criterion, safety requirement, data integrity, or critical factual validity. Fix, replan, or explicitly narrow the release scope with the user; do not call it passed.
- **Non-blocking**: does not invalidate required acceptance. Record a follow-up owner/risk and proceed where justified.
- **Suggestion**: optional improvement; backlog only.
- **Unverified**: evidence unavailable. If it is essential, acceptance remains blocked; otherwise disclose the limitation and applicable gate decision.

Once all required criteria have valid evidence and blocking findings are resolved, accept and move on. Reopen only for new material evidence, changed scope/inputs, or a reported regression. Completed tasks retain their history; new issues after completion become linked follow-up tasks.

Default to at most 2 targeted revision rounds on the same approach. At the budget limit, change strategy: isolate the unknown, reduce scope with user approval, launch alternative experiments, ask for human help, or record a blocker. This is an escalation budget, never an automatic pass, silent waiver, or permission to leave known critical failures in a released result. The user may approve a justified additional round.

## Parallel experiments

For uncertain work, prefer small competing experiments over a long speculative implementation/review loop. Each experiment states a hypothesis/question, success and stop conditions, resource budget, input snapshot, isolated output, and comparison criteria. Keep risky writes away from original assets and take the required backup first.

Use a new linked task when alternatives can run independently; use continuation within the same task for a small sequential trial. Assign an integration/comparison owner. Compare actual observations against the common criteria, retain useful negative evidence, and stop losing branches. A major route choice goes to the user with options; do not silently replace the accepted project goal. Failed or inconclusive experiments must be labeled accurately; inconclusive evidence does not establish feasibility.
