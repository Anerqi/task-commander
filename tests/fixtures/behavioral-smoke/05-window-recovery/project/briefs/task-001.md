# Task Brief: TASK-001

- Task ID: TASK-001
- Role: Executor
- Deliverables:
  1. `src/utils.py`:
     - Function `slugify(text: str) -> str`: Converts text to lowercase hyphenated slug, removing non-alphanumeric characters.
     - Function `truncate(text: str, max_len: int) -> str`:
       - If `max_len < 0`: raises `ValueError`.
       - If `len(text) > max_len`: returns `text[:max_len] + '...'` (the resulting string length will be `max_len + 3`).
       - If `len(text) <= max_len`: returns `text` unchanged.
       - Specifically, for `max_len = 0`: returns `'...'` for any non-empty string, and returns `""` for an empty string.
  2. `tests/test_utils.py`: Unit tests covering both functions.
- Acceptance criteria: Unit tests pass via `python -m unittest tests/test_utils.py`.
- Output receipt: `receipts/task-001.md`
