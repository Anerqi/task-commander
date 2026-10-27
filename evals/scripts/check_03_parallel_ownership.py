#!/usr/bin/env python3
import sys, os
# --- helpers (inlined: skill-up uploads only the script file) ---
from pathlib import Path

FAILS = []

def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)

def read(path):
    p = Path(path)
    return p.read_text(encoding="utf-8") if p.exists() else None

def task_status(task_id, path="project-status.md"):
    """Status column of a task row in the project-status task table, or None."""
    text = read(path) or ""
    for line in text.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if cells and cells[0] == task_id and len(cells) > 2:
            return cells[2]
    return None

def files_under(d):
    p = Path(d)
    return [f for f in p.rglob("*") if f.is_file()] if p.exists() else []

def finish():
    sys.exit(1 if FAILS else 0)
# --- checks ---
check(not files_under("docs"), "Commander did not write any docs/ deliverables")
s3 = task_status("TASK-003")
check(s3 in ("TODO", "Blocked", None), f"TASK-003 not started this round (status: {s3})")
started = [t for t in ("TASK-001", "TASK-002", "TASK-003") if task_status(t) == "In Progress"]
check(len(started) <= 2, f"at most 2 tasks moved to In Progress ({started})")
finish()
