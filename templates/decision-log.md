# Project Decision Log Template

## Purpose

After the user confirms a major decision, the Commander appends the decision to `<Project Root>/decision-log.md` using this template. That file is the single source of truth; do not create a directory with the same name.
Only record decisions the user has explicitly confirmed; do not write Decision Manager recommendations directly as final decisions.

Decision-log entries are for consequential choices, not every reversible implementation detail. If the project uses ADRs, offer one only when the choice is hard to reverse, surprising without context, and the result of a real trade-off; otherwise the decision-log entry is enough. A stable conclusion that is not a decision belongs in `knowledge/topics/`, not here.

## Numbering rules

Read the existing `decision-log.md` and increment the last number, in the format D001, D002...; start at D001 when the file does not exist.

## Input information (required / reference)

- Decision topic and background
- Options considered and their pros and cons (usually from discussion records or comparison tables)
- The chosen option and the reason
- The tasks and files the decision affects
- Whether a re-evaluation is needed later (optional)

## Record template

The `# Project Decision Log` H1 appears only once when the file is initialized; later records append only the `## DXXX` sections.

```markdown
# Project Decision Log

## DXXX
Date: YYYY-MM-DD
Decision: (summarize the decision in one sentence)
Chosen option: (name of the chosen option)

---

## Background
Why this decision was needed:

---

## Options considered
### Option A
Pros:
Cons:

### Option B
Pros:
Cons:

(Add more options as needed)

---

## Final choice
Choice: (Option A / Option B / ...)
Reason:

---

## Impact
Affected tasks:
- (task id)
Affected files:
- (file path)
Knowledge topic / ADR pointer (if any):
- (path)

---

## Follow-up review
Re-evaluation needed: yes / no
(If yes, state the trigger condition or date for the re-evaluation)
```