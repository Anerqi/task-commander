"""Workflow Plan Template for Task Commander Dynamic Workflow Engine.

Modify this file to define DAG dependencies, risk levels, and execution hooks.
Run with:
    python scripts/run-workflow.py --plan templates/workflow-plan.template.py
"""

from typing import Dict, Any, List

WORKFLOW: Dict[str, Any] = {
    "id": "wf-example-feature",
    "name": "Example Feature Pipeline",
    "version": "1.0",
    "description": "Standard multi-agent workflow with parallel tasks and risk gates.",
    "max_concurrency": 2,
    "tasks": [
        {
            "id": "TASK-01",
            "name": "Prepare Schema and Models",
            "type": "EXECUTE",
            "agent": "Executor",
            "risk_level": "MEDIUM",
            "requires_checkpoint": False,
            "depends_on": [],
            "command": "python -c \"print('Executing Task 01: Models defined')\"",
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
            "command": "python -c \"print('Executing Task 02: Core logic built')\"",
            "output_dir": "task-output/TASK-02",
        },
        {
            "id": "TASK-03",
            "name": "High-Risk Production Migration",
            "type": "EXECUTE",
            "agent": "Executor",
            "risk_level": "HIGH",
            "requires_checkpoint": True,  # Triggers interruption for human sign-off
            "depends_on": ["TASK-02"],
            "command": "python -c \"print('Executing Task 03: Migration executed safely')\"",
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
            "command": "python -c \"print('Executing Task 04: QA test suite passed')\"",
            "output_dir": "task-output/TASK-04",
        },
    ],
}
