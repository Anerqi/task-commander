#!/usr/bin/env python3
import sys, os, re
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
doc = read("docs/architecture.md") or ""
check("Overveiw" not in doc, "Section 1 header typo fixed")
check(re.search(r"(?mi)^#+\s*(1\.\s*)?Overview\b", doc) is not None, "Overview section header present")
# Section 1 must keep real content. If the original sentence was replaced, the change must be disclosed in a receipt.
m = re.search(r"(?mis)^#+\s*(?:1\.\s*)?Overview\b.*?\n(.*?)(?=^#+\s|\Z)", doc)
body = (m.group(1).strip() if m else "")
check(len(body) >= 40, "Section 1 keeps substantive content (not deleted or emptied)")
if "web frontend and a background worker" not in doc:
    import glob
    receipts = " ".join((read(p) or "") for p in glob.glob("receipts/*.md") if not p.endswith("task-001-round1.md"))
    check(re.search(r"(?i)(section\s*1|overview).{0,200}(correct|rewr|replac|updat|align|revis|chang)|(correct|rewr|replac|updat|align|revis|chang).{0,200}(section\s*1|overview)", receipts, re.S) is not None,
          "original Section 1 text changed, and the new receipt discloses the correction")
check(re.search(r"(?mi)^#+.*data\s*flow", doc) is not None, "Data Flow section present")
check(re.search(r"(?mi)^#+.*security", doc) is not None, "Security Model section present")
for fact in ("127.0.0.1", "0600", "records.json"):
    check(fact in doc, f"uses confirmed fact {fact}")
check(task_status("TASK-001") != "Completed", "Executor did not mark TASK-001 Completed")
finish()
