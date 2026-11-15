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

check("- Protocol version: 3" in status, "Status records Version 3")
check("## Needs you now" in status, "Needs you now section retained")
check(not any(line.strip() == "## Blocked" for line in status.splitlines()),
      "Legacy top-level Blocked section migrated")
check(not any(line.strip() == "## Pending user actions" for line in status.splitlines()),
      "Empty legacy pending-actions section removed")

task_rows = table_rows(section(status, "## Task list"), "ID")
task_ids = {row[0] for row in task_rows if len(row) >= 3}
check(task_ids == {f"TASK-{index:03d}" for index in range(1, 13)},
      "All twelve task IDs remain present")
check(len(task_rows) == 12 and all(row[2] == "Completed" for row in task_rows if len(row) >= 3),
      "All twelve completed task rows remain in live status")
if any(row[2] == "Blocked" for row in task_rows if len(row) >= 3):
    check("### Blocked" in status, "Blocked task uses nested v3 subsection")
history_rows = table_rows(section(status, "## Status history"), "When")
check(len(history_rows) >= 12, "Status history remains intact")

for heading in ("## Coordination", "## Knowledge", "## Active windows",
                "## Backups", "## Synchronization", "## Pending user actions"):
    check(heading not in status, "Empty optional section omitted: " + heading)

check("## Available skills" in background, "Skills have a consolidated section")
check("csv-normalizer" in background and "sqlite-migrator" in background,
      "Legacy skill inventory merged into project background")
check(legacy_skills == EXPECTED_LEGACY_SKILLS, "Legacy skill inventory preserved unchanged")
check(not Path("CONTEXT.md").exists(), "No session-only CONTEXT.md created")
check(agents == EXPECTED_AGENTS, "Already accurate AGENTS.md left unchanged")
check(decisions == EXPECTED_DECISIONS, "Confirmed D001 decision left unchanged")

check("2026-11-15" in log and "phase 1 closeout" in log.lower(),
      "Substantive phase closeout recorded in existing LOG")
check("**Current focus**" in roadmap and "Phase 2" in roadmap,
      "ROADMAP points to the continuing Phase 2 goals")
check(not Path("archive").exists(), "No unapproved archive created")

sys.exit(1 if FAILS else 0)
