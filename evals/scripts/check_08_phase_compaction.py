#!/usr/bin/env python3
"""Deterministic checks for Version 3 phase compaction and history preservation."""

from datetime import date
from pathlib import Path
import re
import sys

FAILS = []

EXPECTED_AGENTS = """# Project Agent Rules

- Preserve accepted migration behavior and backwards compatibility.
- Keep migration operations idempotent.
- Run destructive checks only in a disposable workspace.
"""

EXPECTED_LEGACY_SKILLS = """# Legacy Skill Inventory

## csv-normalizer
- Choice reason: Normalize imported CSV records before database staging.
- Trigger: A task reads a CSV source.
- Applicable tasks: TASK-002, TASK-004.
- Path: /workspace/skills/csv-normalizer/SKILL.md

## sqlite-migrator
- Choice reason: Validate and migrate the SQLite staging schema.
- Trigger: A task changes the staging database.
- Applicable tasks: TASK-006, TASK-009.
- Path: /workspace/skills/sqlite-migrator/SKILL.md
"""

EXPECTED_DECISIONS = """# Project Decision Log

## D001 — SQLite staging database
- Date: 2026-10-20
- Decision: Use SQLite as the local staging database.
- Rationale: It supports repeatable offline migration tests.
- Impact: TASK-006, TASK-009; docs/migration.md.
- Supersedes: -
"""

EXPECTED_ACCEPTED_ARTIFACT = """# Migration Validation

- Task: TASK-009
- Status: Accepted
- Evidence: The legacy import and normalized SQLite staging output are reproducible.
"""

EXPECTED_LOG_ENTRY = """## 2026-11-10 — Phase 1 validation baseline

- The legacy import and normalized SQLite staging output are reproducible.
- Evidence: task-output/TASK-009/validation.md.
- Topic: none.
"""

EXPECTED_HISTORY = [
    ("2026-11-01", "TASK-001", "Awaiting Acceptance", "Completed", "Accepted inventory", "Commander"),
    ("2026-11-02", "TASK-002", "Awaiting Acceptance", "Completed", "Accepted normalization", "Commander"),
    ("2026-11-03", "TASK-003", "Awaiting Acceptance", "Completed", "Accepted field mapping", "Commander"),
    ("2026-11-04", "TASK-004", "Awaiting Acceptance", "Completed", "Accepted parser", "Commander"),
    ("2026-11-05", "TASK-005", "Awaiting Acceptance", "Completed", "Accepted validation rules", "Commander"),
    ("2026-11-06", "TASK-006", "Awaiting Acceptance", "Completed", "Accepted schema", "Commander"),
    ("2026-11-07", "TASK-007", "Awaiting Acceptance", "Completed", "Accepted staging writer", "Commander"),
    ("2026-11-08", "TASK-008", "Awaiting Acceptance", "Completed", "Accepted error reporting", "Commander"),
    ("2026-11-09", "TASK-009", "Awaiting Acceptance", "Completed", "Accepted migration verification", "Commander"),
    ("2026-11-09", "TASK-010", "Awaiting Acceptance", "Completed", "Accepted user documentation", "Commander"),
    ("2026-11-10", "TASK-011", "Awaiting Acceptance", "Completed", "Accepted rollback procedure", "Commander"),
    ("2026-11-10", "TASK-012", "Awaiting Acceptance", "Completed", "Accepted phase package", "Commander"),
]


PROJECT_PHASES = {
    "context building", "planning", "in progress", "acceptance", "completed", "paused",
}
HISTORY_DATE_FLOOR = date(2026, 11, 10)


def history_is_valid(history_rows):
    """Keep the original history exact; validate only appended rows flexibly."""
    original_count = len(EXPECTED_HISTORY)
    if len(history_rows) < original_count:
        return False
    if [tuple(row) for row in history_rows[:original_count]] != EXPECTED_HISTORY:
        return False

    appended = history_rows[original_count:]
    if not appended:
        return True

    has_project_phase_change = False
    for row in appended:
        if len(row) != 6 or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", row[0]):
            return False
        try:
            row_date = date.fromisoformat(row[0])
        except ValueError:
            return False
        if row_date < HISTORY_DATE_FLOOR:
            return False

        source = row[2].strip().casefold()
        target = row[3].strip().casefold()
        if (row[1].strip().casefold() == "project"
                and source in PROJECT_PHASES and target in PROJECT_PHASES
                and source != target):
            has_project_phase_change = True

    return has_project_phase_change


def current_focus_is_phase_2(roadmap):
    """Accept a descriptive Phase 2 focus, not only a fixed literal."""
    matches = [
        line for line in roadmap.splitlines()
        if re.match(r"^\s*\*\*current focus\*\*\s*:", line, re.IGNORECASE)
    ]
    if len(matches) != 1:
        return False
    focus = matches[0].casefold()
    return "phase 2" in focus and "phase 1 validation" not in focus


def roadmap_milestones_are_valid(roadmap):
    """Accept descriptive milestone suffixes while keeping Phase 2 open."""
    lines = [line.strip() for line in roadmap.splitlines()]
    has_phase_1_closeout = any(
        line.startswith("- [x] Phase 1: validate legacy import and SQLite staging")
        for line in lines
    )
    has_open_phase_2 = any(
        line.startswith("- [ ] Phase 2: rehearse production cutover and rollback")
        for line in lines
    )
    phase_2_is_completed = any(line.startswith("- [x] Phase 2:") for line in lines)
    return has_phase_1_closeout and has_open_phase_2 and not phase_2_is_completed


def dated_log_entries(log):
    """Return dated level-two LOG entries in file order."""
    lines = log.splitlines()
    entries = []
    for index, line in enumerate(lines):
        match = re.match(r"^##\s+(\d{4}-\d{2}-\d{2})(?:\s|$)", line)
        if not match:
            continue
        try:
            entry_date = date.fromisoformat(match.group(1))
        except ValueError:
            entry_date = None
        entries.append((index, entry_date))
    return lines, entries


def newest_first_log_entry_is_valid(log):
    """Check the first dated LOG entry under the newest-first contract."""
    lines, entries = dated_log_entries(log)
    if not entries or entries[0][1] != date(2026, 11, 15):
        return False

    start = entries[0][0]
    end = next(
        (index for index in range(start + 1, len(lines))
         if lines[index].startswith("## ")),
        len(lines),
    )
    entry_lines = lines[start:end]
    body = "\n".join(entry_lines[1:])
    return len(entry_lines) <= 20 and "phase 1" in body.casefold()


def log_entries_are_newest_first(log):
    """Require dated LOG entries to be ordered by non-increasing date."""
    _, entries = dated_log_entries(log)
    dates = [entry_date for _, entry_date in entries]
    if not dates or any(entry_date is None for entry_date in dates):
        return False
    return all(previous >= current for previous, current in zip(dates, dates[1:]))


EXPECTED_SKILL_FACTS = {
    "csv-normalizer": (
        "/workspace/skills/csv-normalizer/skill.md",
        "task-002",
        "task-004",
        "reads a csv source",
    ),
    "sqlite-migrator": (
        "/workspace/skills/sqlite-migrator/skill.md",
        "task-006",
        "task-009",
        "changes the staging database",
    ),
}


def skill_entry_is_complete(available_skills, skill):
    """Accept any entry layout that keeps the skill's path, tasks and trigger.

    The entry runs from the first line that names the skill to the next line
    that names another expected skill.
    """
    lines = available_skills.splitlines()
    others = [name for name in EXPECTED_SKILL_FACTS if name != skill]
    start = next((i for i, line in enumerate(lines) if skill in line.casefold()), None)
    if start is None:
        return False
    end = next(
        (i for i in range(start + 1, len(lines))
         if any(other in lines[i].casefold() for other in others)),
        len(lines),
    )
    entry = " ".join(lines[start:end]).casefold()
    return all(fact in entry for fact in EXPECTED_SKILL_FACTS[skill])


def check(condition, message):
    print(("PASS " if condition else "FAIL ") + message)
    if not condition:
        FAILS.append(message)


def read(path):
    p = Path(path)
    return p.read_text(encoding="utf-8") if p.is_file() else None


def section(text, heading):
    lines = text.splitlines()
    start = None
    for index, line in enumerate(lines):
        if line.strip() == heading:
            start = index + 1
            break
    if start is None:
        return []
    end = len(lines)
    for index in range(start, len(lines)):
        line = lines[index].strip()
        if line.startswith("## "):
            end = index
            break
    return lines[start:end]


def table_rows(lines, header_id):
    rows = []
    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("|") or stripped.startswith("|---"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if cells and cells[0] != header_id and any(cells):
            rows.append(cells)
    return rows


def main():
    FAILS.clear()
    status = read("project-status.md") or ""
    background = read("background/01_project_background.md") or ""
    legacy_skills = read("background/02_skill_list.md")
    agents = read("AGENTS.md")
    decisions = read("decision-log.md")
    log = read("knowledge/LOG.md") or ""
    roadmap = read("knowledge/ROADMAP.md") or ""
    accepted_artifact = read("task-output/TASK-009/validation.md")

    check("- Protocol version: 3" in status, "Status records Version 3")
    check("- Status revision: 8" in status, "Status revision increments exactly once from 7 to 8")
    check("## Needs you now" in status, "Needs you now parent section retained")

    task_rows = table_rows(section(status, "## Task list"), "ID")
    task_ids = {row[0] for row in task_rows if len(row) >= 3}
    expected_task_ids = {f"TASK-{index:03d}" for index in range(1, 13)}
    check(task_ids == expected_task_ids, "All twelve task IDs remain present")
    check(len(task_rows) == 12 and all(row[2] == "Completed" for row in task_rows if len(row) >= 3),
          "All twelve completed task rows remain in live status")

    history_rows = table_rows(section(status, "## Status history"), "When")
    check(history_is_valid(history_rows),
          "Original status history is unchanged; valid dated phase updates may follow")

    status_headings = {line.strip() for line in status.splitlines() if line.lstrip().startswith("#")}
    for heading in (
        "## Coordination", "## Knowledge", "## Active windows",
        "## Backups", "## Synchronization", "## Blocked",
        "## Pending user actions", "### Blocked", "### Pending user actions",
    ):
        check(heading not in status_headings, "Empty optional section omitted: " + heading)

    check("## Available skills" in background, "Skills have a consolidated section")
    available_skills = "\n".join(section(background, "## Available skills"))
    for skill in EXPECTED_SKILL_FACTS:
        check(skill_entry_is_complete(available_skills, skill),
              "Full " + skill + " inventory entry migrated under Available skills")
    check(legacy_skills == EXPECTED_LEGACY_SKILLS, "Legacy skill inventory preserved unchanged")
    check(not Path("CONTEXT.md").exists(), "No session-only CONTEXT.md created")
    check(agents == EXPECTED_AGENTS, "Already accurate AGENTS.md left unchanged")
    check(decisions == EXPECTED_DECISIONS, "Confirmed D001 decision left unchanged")

    check(accepted_artifact == EXPECTED_ACCEPTED_ARTIFACT,
          "Accepted TASK-009 migration evidence preserved unchanged")
    check(EXPECTED_LOG_ENTRY in log, "Existing knowledge LOG entry preserved")
    check(newest_first_log_entry_is_valid(log),
          "Newest-first LOG entry is dated 2026-11-15, mentions Phase 1 and has at most 20 lines")
    check(log_entries_are_newest_first(log),
          "Dated LOG entries are ordered newest first")
    check(current_focus_is_phase_2(roadmap),
          "ROADMAP current focus advances to Phase 2 without repeating Phase 1 validation")
    check(roadmap_milestones_are_valid(roadmap),
          "ROADMAP preserves the Phase 1 closeout and keeps Phase 2 open")
    check(not Path("archive").exists(), "No unapproved archive created")

    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
