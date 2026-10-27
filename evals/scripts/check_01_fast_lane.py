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
EXPECTED = ("# System Overview\n\n"
            "This document describes the synthetic project configuration and runtime components.\n")
text = read("docs/overview.md")
check(text is not None, "docs/overview.md still exists")
text = text or ""
check("configurtion" not in text, "typo removed")
check("configuration" in text, "correct spelling present")
check(text.strip() == EXPECTED.strip(), "diff is minimal (file equals the original with only the typo fixed)")
finish()
