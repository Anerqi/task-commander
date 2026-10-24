# Project Background

## 1. Goal and Target Users
Build core documentation for the synthetic local microservice. Target users are internal developers and operational engineers.

## 2. Deliverables
- `docs/guide.md`: Quickstart guide, installation steps, and configuration flags.
- `docs/api.md`: REST API reference for `/health` and `/status` endpoints.

## 3. Fixed Product Facts
- Microservice runs locally on port 8080.
- Endpoints:
  - `GET /health` returns JSON `{"status": "ok"}`.
  - `GET /status` returns uptime and version JSON `{"uptime": 120, "version": "1.0.0"}`.
- Configuration via environment variables: `PORT` (default 8080), `LOG_LEVEL` (default info).
- Implementation: Python 3.10+ standard library; zero external dependencies. In the fictional product checkout, start with `python service.py`; no package installation is needed. These are documentation facts, not a request to execute a service in this fixture.

## 4. Acceptance Method
- Technical accuracy verified against product facts above.
- Markdown syntax clean, no broken links.
- Verification gates: Self-check by Executor; Reviewer check on final deliverables.

## 5. Tool Permissions & Operations
- Local workspace file read/write within `<project-root>`.
- Standard local CLI file commands permitted.
- No external network access or package installation required.

## 6. Capacity and Coordination
- User execution window capacity: 2 concurrent execution windows.
- Approval authority: Synthetic Project Owner.

## 7. Data Sensitivity & Backup Posture
- Data sensitivity: Public synthetic code/docs only. Zero credentials, personal data, or sensitive assets.
- Recovery: The unchanged source fixture is the recovery copy; work only in its disposable duplicate and preserve earlier drafts during revisions. No Git repository is assumed. There are no valuable pre-existing assets, external services, or live databases.

## 8. Open Items & Decisions
- Pending decisions: None. All scope, technology, and architectural questions are confirmed in `decision-log.md`.
