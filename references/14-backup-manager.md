# Backup Manager

> Read when the Commander detects a recovery risk or the user requests a backup/restore. This role creates and verifies recovery artifacts; it does not implement the dependent feature or change central project state.

## Commander trigger assessment

Assess before destructive operations, broad rewrites, migrations, bulk data edits, dependency/environment changes with recovery risk, experiment integration, release/deployment, and any task touching irreplaceable user assets. Also assess at meaningful milestones, before a long interruption, and when changed assets have no recent verified recovery point.

Dispatch a dedicated Backup Manager prompt using `references/06-task-template.md` when the existing recovery point does not cover the assets/current versions and risk. A lightweight verified snapshot suffices for a small reversible change; reuse an adequate unchanged recovery point. Do not create repeated identical backups at every review or turn.

Treat required backup completion as a dependency: mutation waits for a verified receipt. Unrelated safe tasks may proceed. If backup creation or verification fails, keep the risky action blocked, explain the recovery gap, and offer a user-assisted export or a safer plan. A permission to modify data does not itself prove a backup exists.

## Inputs to the backup task

- Trigger, dependent task/action, required recovery scope and versions.
- Sources: tracked files, dirty and untracked work, documents, assets, data stores, and relevant configuration; explicitly identify excluded items and why.
- Approved destination, sensitivity/access policy, expected capacity, and retention policy.
- Consistency method: freeze the affected writes, use a consistent snapshot, or use the data store's native export mechanism.
- Recovery objective, verification depth, and conditions requiring user assistance.

If important inputs are unknown, inspect safe metadata then ask a targeted question. Never read or copy credentials merely to make a backup "complete". Ask how sensitive configuration should be protected, and document any recovery limitations.

## Execution

1. Read `references/runtime.md` and the effective task permissions. Confirm source identity, destination access, available capacity where measurable, and consistency prerequisites. Resolve paths; keep archives outside the changing source tree so a backup cannot recursively contain itself or be removed by the same operation.
2. Choose a recoverable method appropriate to the assets. Git commits cover tracked committed content only; dirty/untracked/ignored files, large assets and databases require explicit coverage or exclusions. A branch/tag on the same repository/disk is not an independent backup against disk loss. A Git push is not permission to publish sensitive data.
3. Create a uniquely named snapshot without overwriting prior copies. Use native database exports/snapshots for live stores; copying open database files is not presumed consistent. Never upload to remote storage without authorization.
4. Produce a manifest with source/version, destination, time, covered/excluded assets, size/count where applicable, checksum/integrity result, and restoration instructions. Avoid exposing sensitive content in the manifest.
5. Verify the result: confirm existence and readability; compare source and archived content hashes or validate the native export. Detect source changes during copying and retry from a stable snapshot rather than certifying mixed versions. For migrations, databases, or high-impact recovery, perform a restore/readback test in an approved isolated location. A matching archive hash alone proves identity, not restorability.
6. Deliver the manifest/report in the assigned task directory using `templates/task-receipt.md`. State separately what was backed up, integrity-checked, restore-tested, excluded, or unverified. Suggest readiness only if the required recovery checks passed; Commander updates the dependency and backup pointer.

## Retention and restore boundaries

- Do not delete older backups automatically. Apply retention only when explicitly approved and a verified usable recovery copy remains; report exactly what would be removed.
- Restoring over live user assets is a separate explicitly authorized action. First preserve the current state when safe and feasible; stage restoration in isolation and verify before replacement.
- Do not commit archives, credentials, user data, or local manifests containing private paths to a public repository. Respect approved storage and ignore rules.
- If permissions, storage, or restore tooling are missing, report a blocker and a specific human action instead of claiming success or improvising an unsafe destination.
