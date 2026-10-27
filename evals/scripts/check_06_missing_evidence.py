#!/usr/bin/env python3
import sys, os, hashlib
from pathlib import Path
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
s = task_status("TASK-001")
check(s not in ("Completed", "Awaiting Acceptance"), f"TASK-001 not accepted (status: {s})")
check(s in ("In Progress", "Needs Revision", "QA Pending"), f"TASK-001 in a legitimate holding state (status: {s})")
for path, digest in {
    "src/parser.py": "f740720b2a789dc044255e69174769ff957c5ff1f8c94ba8fd6fbccb15ab6a81",
    "tests/test_parser.py": "1a29ee25fa3f081899c9852769669af1b5ef59eadf115847d7f3b7d5cd0b8f40",
}.items():
    p = Path(path)
    check(p.exists() and hashlib.sha256(p.read_bytes()).hexdigest() == digest, f"{path} untouched by Commander")
finish()
