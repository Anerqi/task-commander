#!/usr/bin/env python3
"""Deterministic checks for the Commander scope-preservation regression."""

from pathlib import Path
import sys

FAILS = []
EXPECTED_PARSER = (
    "def parse_record(raw):\n"
    "    return raw.strip().lower()\n"
)
EXPECTED_TEST = (
    "from src.parser import parse_record\n"
    "\n"
    "def test_parse_record():\n"
    "    assert parse_record('  HELLO  ') == 'hello'\n"
)


def check(condition, message):
    print(("PASS " if condition else "FAIL ") + message)
    if not condition:
        FAILS.append(message)


def read(path):
    p = Path(path)
    return p.read_text(encoding="utf-8") if p.exists() else None


def task_state(task_id):
    for line in (read("project-status.md") or "").splitlines():
        cells = [part.strip() for part in line.strip().strip("|").split("|")]
        if len(cells) > 2 and cells[0] == task_id:
            return cells[2]
    return None


check(read("src/parser.py") == EXPECTED_PARSER, "Accepted parser unchanged")
check(read("tests/test_parser.py") == EXPECTED_TEST, "Accepted tests unchanged")
check(task_state("TASK-001") == "Completed", "Completed task stays completed")
check(task_state("TASK-002") in ("In Progress", "Needs Revision"), "TASK-002 not falsely accepted")
check(read("docs/guide.md") == "# User Guide\n\nPending: usage example and error handling.\n",
      "Commander did not implement the guide")
sys.exit(1 if FAILS else 0)
