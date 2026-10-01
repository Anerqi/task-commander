#!/usr/bin/env python3
"""render-workflow.py - Visual Dashboard and Diagram Renderer for Task Commander.

Renders project workflow and task state into:
1. Terminal ANSI / ASCII dashboard (--format text)
2. Mermaid flowchart for GitHub / cc-haha / Markdown (--format mermaid)
3. Structured JSON summary (--format json)
"""

from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path
from typing import Any, Dict, List


def split_markdown_row(line: str) -> List[str]:
    """Split unescaped pipe delimiters, retaining escaped pipes inside cells."""
    cells, current, backslashes = [], [], 0
    for character in line:
        if character == "|" and backslashes % 2 == 0:
            cells.append("".join(current).strip())
            current = []
        else:
            current.append(character)
        backslashes = backslashes + 1 if character == "\\" else 0
    cells.append("".join(current).strip())
    return [cell.replace("\\|", "|") for cell in cells[1:-1]]


def load_state_data(source_path: Path) -> Dict[str, Any]:
    """Loads state from checkpoint JSON or project-status.md."""
    if not source_path.is_file():
        raise FileNotFoundError(f"State file not found: {source_path}")

    if source_path.suffix == ".json":
        with open(source_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict) or not isinstance(data.get("task_states"), dict):
            raise ValueError("Checkpoint must contain a task_states object")
        for tid, info in data["task_states"].items():
            if not isinstance(info, dict):
                raise ValueError(f"Invalid checkpoint display entry: {tid}")
            deps = info.get("depends_on", [])
            if not isinstance(deps, list) or any(not isinstance(dep, str) for dep in deps):
                raise ValueError(f"Invalid display dependencies: {tid}")
        data["record_kind"] = "command-progress"
        return data
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
                    parts = split_markdown_row(line_str)
                    if len(parts) >= 6 and parts[0] != "ID" and not all(set(p) <= set("-: ") for p in parts):
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
                    parts = split_markdown_row(line_str)
                    if len(parts) >= 5 and parts[0] != "Task" and not all(set(p) <= set("-: ") for p in parts):
                        blocked.append({
                            "task": parts[0],
                            "reason": parts[2],
                            "owner": parts[3],
                            "done_when": parts[4],
                        })

        return {
            "record_kind": "project-status",
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
    if data.get("record_kind") != "project-status":
        lines.append("  Command progress only; COMPLETED is not project acceptance.")
        if data.get("dry_run"):
            lines.append("  SIMULATION: no task commands executed.")

    task_states = data.get("task_states", {})
    if not task_states:
        lines.append("  (No tasks found in state)")
        return "\n".join(lines)

    lines.append(f"{'TASK ID':<12} | {'STATUS':<20} | {'AGENT':<12} | {'NAME'}")
    lines.append("-" * 70)

    for tid, info in task_states.items():
        st = str(info.get("status") or "UNKNOWN")
        agent = str(info.get("agent") or "Unknown")
        name = str(info.get("name") or tid)

        # Normalize display comparisons without rewriting recorded project states.
        normalized = st.upper().replace(" ", "_")
        if normalized in ("COMPLETED", "DONE", "ACCEPTED"):
            badge = f"[OK] {st}"
        elif normalized == "SIMULATED":
            badge = f"[SIM] {st}"
        elif normalized in ("RUNNING", "IN_PROGRESS"):
            badge = f"[>>] {st}"
        elif normalized in ("CHECKPOINT_SUSPENDED", "BLOCKED", "RECOVERY_REQUIRED"):
            badge = f"[PAUSED] {st}"
        elif normalized == "FAILED":
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
    node_ids = {tid: f"node_{index}" for index, tid in enumerate(task_states)}
    if data.get("record_kind") != "project-status":
        lines.append("    %% Command progress only; completion is not project acceptance")

    for tid, info in task_states.items():
        name = str(info.get("name", tid))
        st = str(info.get("status", "PENDING"))
        normalized = st.upper().replace(" ", "_")
        parts = [html.escape(str(value), quote=True).replace("\n", " ").replace("\\", "&#92;")
                 for value in (tid, name, f"({st})")]
        label = '"' + "<br/>".join(parts) + '"'
        if normalized in ("COMPLETED", "DONE", "ACCEPTED"):
            style = "completed"
        elif normalized in ("RUNNING", "IN_PROGRESS"):
            style = "running"
        elif normalized in ("CHECKPOINT_SUSPENDED", "BLOCKED", "RECOVERY_REQUIRED"):
            style = "suspended"
        elif normalized == "FAILED":
            style = "failed"
        elif normalized == "SIMULATED":
            style = "simulated"
        else:
            style = "pending"
        lines.append(f"    {node_ids[tid]}[{label}]:::{style}")
        for dep in info.get("depends_on", []):
            if dep in task_states:
                lines.append(f"    {node_ids[dep]} --> {node_ids[tid]}")

    lines.append("    classDef completed fill:#d4edda,stroke:#28a745,stroke-width:2px;")
    lines.append("    classDef running fill:#cce5ff,stroke:#004085,stroke-width:2px,stroke-dasharray: 5 5;")
    lines.append("    classDef suspended fill:#fff3cd,stroke:#856404,stroke-width:2px;")
    lines.append("    classDef failed fill:#f8d7da,stroke:#721c24,stroke-width:2px;")
    lines.append("    classDef pending fill:#e2e3e5,stroke:#383d41,stroke-width:1px;")
    lines.append("    classDef simulated fill:#eee,stroke:#666,stroke-dasharray: 3 3;")
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
        if args.format == "text":
            print(render_terminal(data))
        elif args.format == "mermaid":
            print(render_mermaid(data))
        elif args.format == "json":
            print(json.dumps(data, indent=2, ensure_ascii=False))
    except (OSError, ValueError, TypeError, KeyError) as e:
        print(f"Error rendering state: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
