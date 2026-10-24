# Agent Capabilities Registry

## Context Agent

Responsibilities:
- Project background collection
- Requirements clarification
- Optional knowledge-layer initialization and concise AGENTS.md navigation

## Commander

Responsibilities:
- Project planning
- Task scheduling
- Progress management
- Knowledge integration, milestone audit and optional project retro

## Executor

Capabilities:
- Writing code
- Producing documents
- Data analysis
- Implementing concrete plans
- Building a red-capable feedback loop for hard bugs and performance work

Call when:
The task must produce a concrete vertical slice with observable acceptance criteria.

## Reviewer

Capabilities:
- Spec-axis review: original goal, full task scope, genuine user corrections and scope expansion
- Reviewing plans
- Reviewing code
- Reviewing document quality
- Cold-start scenario assessment followed by informed reconciliation, when selected

Call when:
Quality review is needed. Reviewer owns the Spec axis; QA owns Standards/behavior. For a fresh outside perspective at a milestone or suspected anchoring, use the cold-start mode in `references/17-cold-start-review.md`; it retains the Reviewer role.

## QA

Capabilities:
- Standards/behavior-axis verification: runnability, observable behavior, recomputation and project rules
- Testing functionality
- Verifying results
- Checking acceptance criteria
- Requiring a red-capable reproduction for bug/perf work

Call when:
The task is done and needs verification.

## Risk Manager

Capabilities:
- Risk analysis
- Feasibility assessment

Call when:
Technical uncertainty exists.

## Backup Manager

Capabilities:
- Assessing recovery coverage for dirty/untracked files, documents, assets, data stores and durable knowledge records
- Creating consistent recovery snapshots and manifests in approved storage
- Verifying integrity and performing approved isolated restore/readback checks
- Reporting retention, privacy, consistency and restoration limitations

Call when:
Risky mutation, migration, integration, release, or changed irreplaceable assets lack an adequate verified recovery point. Required backup verification precedes dependent work.
Role file: `references/14-backup-manager.md`

## Decision Manager

Capabilities:
- Analyzing candidate options for major directions
- Comparing benefits, costs, risks, and reversibility
- Recommending without making the final decision for the user

Call when:
The project direction changes.
