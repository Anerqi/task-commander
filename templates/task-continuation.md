# Task Continuation / Recovery Prompt

> Commander fills this for the existing task window. Resolve paths and replace placeholders. For recovery, include the extra fields below. A prompt being emitted is not a delivery acknowledgment.

```text
[Mode] Continue / Recover
[Target window] <human-readable task window label; host session id only if known>
[Task id and round] <original ID; clarification or revision such as 03-R1>
[Role] <existing primary role and absolute role-file path>
[Purpose] Clarification / targeted revision / context synchronization / bounded experiment

[Preserved contract]
Original brief: <absolute path or full original brief if not saved>
Goal, scope, accepted criteria and effective permissions remain unchanged except for the explicit delta below.
Already accepted: <criteria and versioned evidence to reuse>

[Read this delta before proceeding]
Shared context revision: <current revision and absolute authoritative-file pointers>
Changed inputs: <version/hash, location, what changed and why it affects this task>
Issues: <IDs, evidence locations, blocking status and requested fix>
User input: <confirmed answer or pending action; label user observations>
This round's scope and stop condition: <bounded work; no unrelated improvements>
Permissions: <effective network/subagent policy; any explicitly authorized exceptions>
Backup prerequisite: <verified recovery point covering these changes / required backup task / not needed with reason>

[Checks and delivery]
Re-run: <affected checks and necessary regressions, with invalidation reasons>
Reuse: <unchanged checks and evidence>
Output: <existing task directory; preserve prior-round evidence>
Return a receipt per <absolute path to templates/task-receipt.md> with the acknowledged context revision, issue dispositions, evidence, shared-information delta and remaining blockers.
Suggest a legal next state; the Commander remains the status writer.

[Recovery only]
Current state and last durable checkpoint: <paths and versions>
Completed work, attempted approaches, and outstanding items: <receipt pointers>
Working/source locations and write ownership: <absolute paths>
Required role, collaboration, quality and conditional runtime references: <absolute paths>
Reconstruct from those files; ask about missing critical context rather than replaying completed work or trusting unavailable chat history.
```
