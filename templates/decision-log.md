# Project Decision Log Template

> Append-only ledger of user-confirmed consequential decisions. Keep each new entry compact; preserve existing historical entries.

## Purpose

After the user confirms a major decision, the Commander appends one concise record to `<Project Root>/decision-log.md`. This file is the single source of truth for confirmed decisions.

Only record decisions the user has explicitly confirmed. Never copy a Decision Manager recommendation into the ledger as a final decision.

Use a separate analysis artifact for detailed option comparisons. The ledger records the outcome, not the full debate. Keep each new decision to about 3–5 substantive lines.

## Numbering and history

Read the existing file and increment the last number in the format D001, D002, and so on. Start at D001 when the file does not exist.

Append new records. Do not rewrite or delete prior confirmed decisions. When a new decision replaces an earlier one, include a `Supersedes` pointer in the new record; retain the earlier entry and its evidence.

## Record template

```markdown
# Project Decision Log

## DXXX — <short topic>
- Date: YYYY-MM-DD
- Decision: <confirmed choice in one sentence>
- Rationale: <short reason; point to the full analysis if needed>
- Impact: <affected task IDs and paths>
- Supersedes: <decision ID or ->
```

## Boundary

Reversible implementation details do not need a decision record. Stable technical conclusions belong in `knowledge/topics/`. Offer an ADR only when the project already uses ADRs and the choice is hard to reverse, surprising without context, and a real trade-off.
