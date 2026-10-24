# 21 - Window and Phase Boundaries

> Read at a phase or milestone boundary, before starting a fresh window, compacting, handing off, or sending a focused subagent. The goal is to preserve useful context at the lowest cost, not to reset windows by habit.

## Boundary, not mid-phase

A **phase** is a coherent chunk of work inside a window: context building, implementation, review, QA, closeout. A **boundary** is the gap between two phases. Decide there, not in the middle of active work.

Mid-phase, the primary window should continue or split a tightly scoped piece into a subagent. Replacing or compacting the primary window mid-phase loses the primary source while it is still needed. A self-contained side piece may be handed off mid-phase while the primary continues. The one exception for replacing the primary window is an actual context limit: save a durable checkpoint and handoff first, state the loss of primary context, and treat it as an emergency recovery, not a habitual reset.

## Decision order

Work top to bottom. The first answer that fits wins.

1. **Continue in this window.**
   Use this when the next phase needs the current phase as a primary source, or when the window still has enough room to reason sharply. Continuing costs nothing and loses nothing. Do not reset merely because a milestone or task completed; completion does not change the window's role.

2. **Start a fresh window.**
   Use this when the current context is genuinely irrelevant to what comes next: the work is independent, the next owner only needs a saved brief and artifacts, and no unresolved reasoning depends on this conversation. The old window may remain resumable. A fresh window is not a fresh project and does not reset task IDs or roles.

3. **Hand off.**
   Use a portable handoff when work must travel: a new host/harness, a new directory or repository, a colleague, or a side task split off mid-phase. A handoff is a fresh window that also travels: add provenance, permissions, accepted evidence and recovery posture so the recipient can act without chat history.

4. **Send a focused subagent.**
   Use this when the next piece is tightly scoped, can run without the user steering, and only needs to return a report or artifact. The primary owner keeps scope, integration and evidence; a subagent does not acquire Commander or gate authority.

5. **Compact or summarize.**
   Use this when the context is still relevant, the host/directory/role stay the same, and the user must stay in the loop, but the window is approaching a real limit. Prefer the host's verified compaction feature; otherwise save a durable checkpoint and open a fresh window with a recovery prompt. If no reliable compaction exists, say so rather than pretending context was preserved.

## How this maps to Task Commander

Task Commander uses manually relayed windows on most hosts. It does not assume automatic `clear`, `compact` or cross-window messaging.

- Keep the task ID, role and accepted evidence stable across any boundary.
- A **handoff packet** should include: task/window identity, original brief and provenance, current artifacts and input versions, accepted evidence, effective permissions and gates, open questions, recovery posture, and the next outcome. Use `templates/task-continuation.md`.
- A **fresh task window** should receive only what its role needs: role rules, brief, relevant inputs, permissions and gates. Do not paste the whole project history.
- A **gate window** stays a gate: review or QA receives the reviewed task ID and version, not implementation ownership. When a gate finishes, return fixes to the original Executor window rather than letting the gate become the implementer.
- A **cold-start Reviewer** boundary overrides generic continuity: stage 1 gets only the neutral packet, not the full project conversation, prior verdicts or background. Follow `references/17-cold-start-review.md`.

## Do not

- Do not compact or replace a window mid-phase for convenience; an actual context limit requires a durable checkpoint and an explicit emergency handoff.
- Do not start a fresh window just to avoid making a difficult decision.
- Do not hand off without durable artifacts and readable pointers.
- Do not claim a replacement window received context merely because a prompt was emitted.
- Do not use a subagent to obtain Commander acceptance or an independent gate verdict by role name alone.

## Completion criteria

The chosen boundary action is justified by the next phase's information needs, not by elapsed time or habit. Durable artifacts are saved, the recipient can act from readable pointers, and role/task identity plus effective permissions survive the move. If the host cannot provide the chosen capability, use the closest safe alternative and state the limitation.
