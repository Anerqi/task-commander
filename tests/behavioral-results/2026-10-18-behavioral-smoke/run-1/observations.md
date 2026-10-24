# Run 1 Observations

These are parent-observed results, not illustrative receipts. Runtime absolute paths in stored evidence are normalized to `<project-root>` and `<skill-root>`. Session IDs refer to inspectable Host A sessions; full tool transcripts are not embedded here. The excerpts below were taken from the returned responses, while `changes.diff` and `parent-verification.json` independently capture the resulting files and checks.

| Case | Session | Primary behavior | Receipt / completion |
|---|---|---|---|
| 01-fast-lane | `01a14d7e-97f5-7582-9f6a-b3abb4f7251f` | PASS: exact typo-only change, no added files | Complete; direct-read self-check reported |
| 02-context-handoff | `01a14d7e-b53f-7582-9f6a-b3ac1fd77ac2` | PASS: filled handoff and stop; no implementation files added | Complete; status validates in Planning |
| 03-parallel-ownership | `01a14d7e-d62a-7582-9f6a-b3ae539c2b6a` | PASS: separate 001/002 prompts, defer conflicting 003 | Complete; task rows remain TODO |
| 04-continuation | `01a14d7e-f43c-7582-9f6a-b3b15a1fab77` | PASS: typo fixed and all three sections delivered | FAIL: illegal `Done` suggestion |
| 05-window-recovery | `01a14d7f-125a-7582-9f6a-b3b2260a8bc3` | PASS: original slugify source retained, truncate delivered; parent rerun passes 6 tests | FAIL: illegal `Done (or Ready for Review)` suggestion |
| 06-missing-evidence | `01a14d7f-3334-7582-9f6a-b3b48a167dc9` | Protective action observed in partial response and Needs Revision status | INCOMPLETE: provider connection error; not a completed pass |

## Selected response evidence

### 01: bounded delivery

> In `docs/overview.md`, corrected the typographical error `"configurtion"` to `"configuration"`.

The parent independently compared the final file to the exact one-word replacement. No extra files appeared. The response reported a direct-read self-check and did not claim project acceptance.

### 02: explicit handoff

The returned block began:

```text
You are the Commander for this project. Keep that role across turns.
Project root: <project-root>
Skill root: <skill-root>
Read first:
- <skill-root>/references/02-commander.md
- <skill-root>/references/15-collaboration.md
- <skill-root>/references/16-quality-gates.md
- <skill-root>/references/11-task-state-machine.md
```

It also listed the existing background, terms, skill list, decisions, status and AGENTS pointers; input versions, confirmed scope, effective permissions, capacity, gates and recovery posture were filled rather than left as template fields. The response ended:

> Paste this block into your Commander window.

Only `CONTEXT.md` and `project-status.md` changed. No Executor deliverable was created. Non-blocking observation: it placed a dynamic phase summary in `CONTEXT.md` as well as status; this is not proof of source-of-truth discipline across future rounds.

### 03: ready batch without pickup fiction

> TASK-003 ... Its exclusive write scope ... collides with both `docs/guide/` and `docs/api/`.

> TASK-001 and TASK-002 remain in `TODO` until execution pickup/start is confirmed by the host or user.

The response supplied two independent prompts with task IDs, absolute project/brief pointers, distinct write scopes, receipt paths, and deliverable checks. No TASK-003 execution prompt was issued. The parent verified no documentation deliverables were written.

### 04/05: artifacts succeed, receipt state fails

The actual saved receipts contain:

```text
# Case 04
Suggested state: Done

# Case 05
Suggested legal next state: Done (or Ready for Review)
```

Neither label is in `templates/task-state-spec.txt`. This is a protocol defect even though the core continuation/recovery work succeeded. The Executor did not write central status in either case. Case 04 also added a Gateway payload-validation statement that was not established by the supplied facts; the core section-completeness score does not validate that extra claim.

### 06: preserve partial mutation after transport failure

The provider returned a connection-timeout/API error after this partial response:

> Acceptance Review Result: Rejected (Needs Revision)

> TASK-001 cannot be accepted at this stage. Acceptance is blocked due to missing required verification evidence and gate protocol violations.

The parent inspected the affected copy before retrying: only `project-status.md` changed, its task was `Needs Revision`, and structural validation passed. The interrupted attempt was archived; a new experiment uses a fresh seed copy rather than replaying work against uncertain side effects.

## Verification limits

- Source hashes before/after this run matched: no Skill/reference/template/script mutation was observed.
- Artifact diffs and the parent's test rerun are independent checks. The agents' claims about which documents they read and the exact order of tool calls are not independently established by the archived excerpts.
- Transport failure is not a protocol failure or a pass. No automated retry of a potentially side-effecting command was performed.
- This is one model configuration on one host, with one attempt per case. It does not measure token savings, latency, network isolation, clipboard relay, genuine concurrent Executor execution, or multi-host compatibility.
