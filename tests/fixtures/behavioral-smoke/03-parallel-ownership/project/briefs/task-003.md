# Task Brief: TASK-003

- Task ID: TASK-003
- Name: Generate Navigation Placeholders
- Priority: P2
- Role: Executor
- Output directory: `docs/`
- Read scope: `background/01_project_background.md`, `CONTEXT.md`
- Exclusive write scope: `docs/guide/index.md`, `docs/api/index.md`, `docs/index.md`
- Deliverable: Placeholder navigation index files containing predetermined links pointing to `docs/guide/user-guide.md` and `docs/api/reference.md`.
- Product facts: Self-contained placeholder generation; does not read unfinished artifacts from other tasks.
- Acceptance criteria: Navigation files created with valid Markdown link syntax.
- Receipt path: `receipts/task-003.md`
- Gate: Self-check only; no QA gate required.
- Dependencies: None (`-`).
- Concurrency limitation: Exclusive write scope overlaps with `docs/guide/` and `docs/api/`. Must not run concurrently with tasks writing to those directories.
