# Agent Capabilities Registry

## Context Agent

Responsibilities:
- Project background collection
- Requirements clarification

## Commander

Responsibilities:
- Project planning
- Task scheduling
- Progress management

## Executor

Capabilities:
- Writing code
- Producing documents
- Data analysis
- Implementing concrete plans

Call when:
The task must produce a concrete deliverable.

## Reviewer

Capabilities:
- Reviewing plans
- Reviewing code
- Reviewing document quality

Call when:
Quality review is needed.

## QA

Capabilities:
- Testing functionality
- Verifying results
- Checking acceptance criteria

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
- Assessing recovery coverage for dirty/untracked files, documents, assets and data stores
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