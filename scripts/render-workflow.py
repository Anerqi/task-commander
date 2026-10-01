#!/usr/bin/env python3
"""render-workflow.py - Visual Dashboard and Diagram Renderer for Task Commander.

Renders project workflow and task state into:
1. Terminal ANSI / ASCII dashboard (--format text)
2. Mermaid flowchart for GitHub / cc-haha / Markdown (--format mermaid)
3. Structured JSON summary (--format json)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List


def load_state_data(source_path: Path) -> Dict[str, Any]:
    """Loads state from checkpoint JSON or project-status.md."""
    if not source_path.is_file():
        raise FileNotFoundError(f"State file not found: {source_path}")

    if source_path.suffix == ".json":
        with open(source_path, "r", encoding="utf-8") as f:
            return json.load(f)
    elif source_path.suffix == ".md":
        # Parse task list from project-status.md
        tasks: Dict[str, Any] = {}
        blocked: List[Dict[str, str]] = []
        current_section = None

        with open(source_path, "r", encoding="utf-8") as f:
            for line in f:
                line_str = line.strip()
                if line_str.startswith("## "):
                    current_section = line_str[3:].strip()
                    continue

                if current_section == "Task list" and line_str.startswith("|") and not line_str.startswith("|---"):
                    parts = [p.strip() for p in line_str.split("|")[1:-1]]
                    if len(parts) >= 6 and parts[0] != "ID":
                        tid, name, status, priority, agent = parts[0], parts[1], parts[2], parts[3], parts[4]
                        deps = [d.strip() for d in parts[5].split(",") if d.strip() and d.strip() != "-"]
                        tasks[tid] = {
                            "name": name,
                            "status": status,
                            "priority": priority,
                            "agent": agent,
                            "depends_on": deps,
                        }

                elif current_section == "Blocked" and line_str.startswith("|") and not line_str.startswith("|---"):
                    parts = [p.strip() for p in line_str.split("|")[1:-1]]
                    if len(parts) >= 5 and parts[0] != "Task":
                        blocked.append({
                            "task": parts[0],
                            "reason": parts[2],
                            "owner": parts[3],
                            "done_when": parts[4],
                        })

        return {
            "workflow_id": "project-status",
            "workflow_name": "Project Tasks",
            "status": "TRACKED",
            "task_states": tasks,
            "blocked_items": blocked,
        }
    else:
        raise ValueError(f"Unsupported source format: {source_path.suffix}. Expected .json or .md")


def render_terminal(data: Dict[str, Any]) -> str:
    lines = []
    wf_name = data.get("workflow_name", data.get("workflow_id", "Workflow"))
    status = data.get("status", "UNKNOWN")

    status_tag = f"[{status}]"
    lines.append("=" * 70)
    lines.append(f"  TASK COMMANDER WORKFLOW BOARD :: {wf_name}  {status_tag}")
    lines.append("=" * 70)

    task_states = data.get("task_states", {})
    if not task_states:
        lines.append("  (No tasks found in state)")
        return "\n".join(lines)

    lines.append(f"{'TASK ID':<12} | {'STATUS':<20} | {'AGENT':<12} | {'NAME'}")
    lines.append("-" * 70)

    for tid, info in task_states.items():
        st = info.get("status", "PENDING")
        agent = info.get("agent", "Unknown")
        name = info.get("name", "")

        # Status badge
        if st in ("COMPLETED", "DONE", "ACCEPTED"):
            badge = f"[OK] {st}"
        elif st in ("RUNNING", "IN_PROGRESS"):
            badge = f"[>>] {st}"
        elif st in ("CHECKPOINT_SUSPENDED", "BLOCKED"):
            badge = f"[PAUSED] {st}"
        elif st == "FAILED":
            badge = f"[ERR] {st}"
        else:
            badge = f"[ ] {st}"

        lines.append(f"{tid:<12} | {badge:<20} | {agent:<12} | {name}")

    blocked = data.get("blocked_items", [])
    if blocked:
        lines.append("-" * 70)
        lines.append("  BLOCKED ITEMS / BOTTLENECKS:")
        for b in blocked:
            lines.append(f"  * Task {b['task']} - Reason: {b['reason']} (Owner: {b['owner']})")

    lines.append("=" * 70)
    return "\n".join(lines)


def render_mermaid(data: Dict[str, Any]) -> str:
    lines = ["```mermaid", "graph TD"]
    task_states = data.get("task_states", {})

    for tid, info in task_states.items():
        name = info.get("name", tid).replace('"', "'")
        st = info.get("status", "PENDING")
        label = f'"{tid}<br/>{name}<br/>({st})"'

        # Shape formatting by status
        if st in ("COMPLETED", "DONE", "ACCEPTED"):
            lines.append(f"    {tid}[{label}]:::completed")
        elif st in ("RUNNING", "IN_PROGRESS"):
            lines.append(f"    {tid}[{label}]:::running")
        elif st in ("CHECKPOINT_SUSPENDED", "BLOCKED"):
            lines.append(f"    {tid}[{label}]:::suspended")
        elif st == "FAILED":
            lines.append(f"    {tid}[{label}]:::failed")
        else:
            lines.append(f"    {tid}[{label}]:::pending")

        for dep in info.get("depends_on", []):
            if dep in task_states:
                lines.append(f"    {dep} --> {tid}")

    lines.append("    classDef completed fill:#d4edda,stroke:#28a745,stroke-width:2px;")
    lines.append("    classDef running fill:#cce5ff,stroke:#004085,stroke-width:2px,stroke-dasharray: 5 5;")
    lines.append("    classDef suspended fill:#fff3cd,stroke:#856404,stroke-width:2px;")
    lines.append("    classDef failed fill:#f8d7da,stroke:#721c24,stroke-width:2px;")
    lines.append("    classDef pending fill:#e2e3e5,stroke:#383d41,stroke-width:1px;")
    lines.append("```")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Render Task Commander workflow board and diagrams")
    parser.add_argument("source", type=Path, help="Path to checkpoint.json or project-status.md")
    parser.add_argument(
        "--format",
        choices=["text", "mermaid", "json"],
        default="text",
        help="Output display format (default: text)",
    )

    args = parser.parse_args()

    try:
        data = load_state_data(args.source)
    except Exception as e:
        print(f"Error loading state: {e}", file=sys.stderr)
        return 1

    if args.format == "text":
        print(render_terminal(data))
    elif args.format == "mermaid":
        print(render_mermaid(data))
    elif args.format == "json":
        print(json.dumps(data, indent=2, ensure_ascii=False))

    return 0


if __name__ == "__main__":
    sys.exit(main())
