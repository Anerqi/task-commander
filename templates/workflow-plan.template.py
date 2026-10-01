"""Trusted Python plan for the optional sequential command runner.

Commands below print examples only; they do not implement features or certify QA.
Preview (writes a simulation checkpoint):
    python scripts/run-workflow.py --plan templates/workflow-plan.template.py --dry-run
Use a different --checkpoint path for a real run. Python plans execute on import.
"""

import sys
from typing import Dict, Any

WORKFLOW: Dict[str, Any] = {
    "id": "wf-example-feature",
    "name": "Example Feature Pipeline",
    "version": "1.0",
    "description": "Sequential command example with a pre-command approval barrier.",
    "max_concurrency": 1,
    "tasks": [
        {
            "id": "TASK-01",
            "name": "Prepare Schema and Models",
            "type": "EXECUTE",
            "agent": "Executor",
            "risk_level": "MEDIUM",
            "requires_checkpoint": False,
            "depends_on": [],
            "command": [sys.executable, "-c", "print('Example Task 01 command')"],
            "output_dir": "task-output/TASK-01",
        },
        {
            "id": "TASK-02",
            "name": "Implement Core Business Logic",
            "type": "EXECUTE",
            "agent": "Executor",
            "risk_level": "LOW",
            "requires_checkpoint": False,
            "depends_on": ["TASK-01"],
            "command": [sys.executable, "-c", "print('Example Task 02 command')"],
            "output_dir": "task-output/TASK-02",
        },
        {
            "id": "TASK-03",
            "name": "High-Risk Production Migration",
            "type": "EXECUTE",
            "agent": "Executor",
            "risk_level": "HIGH",
            "requires_checkpoint": True,  # HIGH/CRITICAL pause even if this flag is False
            "depends_on": ["TASK-02"],
            "command": [sys.executable, "-c", "print('Example Task 03 command; no production migration')"],
            "output_dir": "task-output/TASK-03",
        },
        {
            "id": "TASK-04",
            "name": "Review and Quality Assurance",
            "type": "QA",
            "agent": "QA",
            "risk_level": "LOW",
            "requires_checkpoint": False,
            "depends_on": ["TASK-03"],
            "command": [sys.executable, "-c", "print('Example Task 04 command; not a QA verdict')"],
            "output_dir": "task-output/TASK-04",
        },
    ],
}
