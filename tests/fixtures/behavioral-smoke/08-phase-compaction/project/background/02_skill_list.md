# Legacy Skill Inventory

## csv-normalizer
- Choice reason: Normalize imported CSV records before database staging.
- Trigger: A task reads a CSV source.
- Applicable tasks: TASK-002, TASK-004.
- Path: /workspace/skills/csv-normalizer/SKILL.md

## sqlite-migrator
- Choice reason: Validate and migrate the SQLite staging schema.
- Trigger: A task changes the staging database.
- Applicable tasks: TASK-006, TASK-009.
- Path: /workspace/skills/sqlite-migrator/SKILL.md
