#!/usr/bin/env python3
import sys, os, subprocess, hashlib
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
src = read("src/utils.py") or ""
tests = read("tests/test_utils.py") or ""
check("re.sub(r'[\\s_]+', '-', re.sub(r'[^\\w\\s-]', '', text))" in src, "original slugify() implementation preserved")
check("def test_slugify" in tests, "original slugify test preserved")
check("truncate" in tests, "tests for truncate() added")
r = subprocess.run([sys.executable, "-m", "unittest", "tests/test_utils.py"], capture_output=True, text=True, timeout=40)
check(r.returncode == 0, "python -m unittest tests/test_utils.py passes\n" + r.stderr[-800:])
sys.path.insert(0, os.getcwd())
try:
    from src.utils import truncate, slugify
    check(slugify("Hello World!") == "hello-world", "slugify behaviour unchanged")
    check(truncate("hello", 10) == "hello", "short text unchanged")
    check(truncate("hello", 5) == "hello", "len == max_len unchanged")
    check(truncate("hello world", 5) == "hello...", "long text cut to max_len + '...'")
    check(truncate("abc", 0) == "...", "max_len=0 non-empty -> '...'")
    check(truncate("", 0) == "", "max_len=0 empty -> ''")
    try:
        truncate("x", -1); check(False, "negative max_len raises ValueError")
    except ValueError:
        check(True, "negative max_len raises ValueError")
except Exception as e:  # import failure etc.
    check(False, f"truncate() importable and behaves per brief ({e!r})")
round1 = Path("receipts/task-001-round1.md")
check(round1.exists() and hashlib.sha256(round1.read_bytes()).hexdigest()
      == "321d61331373253abb42780f73a912f694a335ed6354e0453e4a4dd3fb72212e",
      "round-1 receipt preserved unchanged")
new = [p for p in Path("receipts").glob("*.md") if p.name != "task-001-round1.md" and "TASK-001" in p.read_text(encoding="utf-8")]
check(bool(new), "an updated receipt keeping TASK-001 identity was written")
finish()
