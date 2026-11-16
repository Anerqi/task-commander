#!/usr/bin/env python3
"""Deterministic checks for Version 3 phase compaction and history preservation."""

from pathlib import Path
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
        if cells and cells[0] != header_id and cells[0]:
            rows.append(cells)
    return rows


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
check([tuple(row) for row in history_rows] == EXPECTED_HISTORY,
      "All twelve original status-history rows remain unchanged and in order")

status_headings = {line.strip() for line in status.splitlines() if line.lstrip().startswith("#")}
for heading in (
    "## Coordination", "## Knowledge", "## Active windows",
    "## Backups", "## Synchronization", "## Blocked",
    "## Pending user actions", "### Blocked", "### Pending user actions",
):
    check(heading not in status_headings, "Empty optional section omitted: " + heading)

check("## Available skills" in background, "Skills have a consolidated section")
available_skills = "\\n".join(section(background, "## Available skills"))
for skill, details in {
    "csv-normalizer": (
        "Choice reason: Normalize imported CSV records before database staging.",
        "Trigger: A task reads a CSV source.",
        "Applicable tasks: TASK-002, TASK-004.",
        "Path: /workspace/skills/csv-normalizer/SKILL.md",
    ),
    "sqlite-migrator": (
        "Choice reason: Validate and migrate the SQLite staging schema.",
        "Trigger: A task changes the staging database.",
        "Applicable tasks: TASK-006, TASK-009.",
        "Path: /workspace/skills/sqlite-migrator/SKILL.md",
    ),
}.items():
    check(skill in available_skills and all(detail in available_skills for detail in details),
          "Full " + skill + " inventory entry migrated under Available skills")
check(legacy_skills == EXPECTED_LEGACY_SKILLS, "Legacy skill inventory preserved unchanged")
check(not Path("CONTEXT.md").exists(), "No session-only CONTEXT.md created")
check(agents == EXPECTED_AGENTS, "Already accurate AGENTS.md left unchanged")
check(decisions == EXPECTED_DECISIONS, "Confirmed D001 decision left unchanged")

check(accepted_artifact == EXPECTED_ACCEPTED_ARTIFACT,
      "Accepted TASK-009 migration evidence preserved unchanged")
check(EXPECTED_LOG_ENTRY in log, "Existing knowledge LOG entry preserved")
check("2026-11-15" in log and "phase 1 closeout" in log.lower(),
      "Substantive phase closeout recorded in existing LOG")
check("**Current focus**: Phase 2" in roadmap,
      "ROADMAP current focus advances to Phase 2")
check("- [x] Phase 1: validate legacy import and SQLite staging." in roadmap
      and "- [ ] Phase 2: rehearse production cutover and rollback." in roadmap,
      "ROADMAP preserves Phase 1 and Phase 2 milestones")
check(not Path("archive").exists(), "No unapproved archive created")

sys.exit(1 if FAILS else 0)
