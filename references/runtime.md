# Cross-Platform Host Execution Principles

> Read this file only when the current work will write or delete files, run a CLI or script, or produce a deliverable. When the work is pure interviewing, planning, review explanation, read-only analysis of user-provided content, or generating prompts that do not land on disk, and runs no CLI or script, skip loading it.

## Runtime environment identification

- Before any file or command operation, do runtime discovery (Runtime Discovery) first: confirm the host (Host) environment from environment variables, capability checks, and PATH, without assuming any of them exists by default.
- The principles in this file are platform-neutral: avoid assumptions about a specific operating system, shell, path layout, or CLI implementation.
- Do not presume path separators, line endings, or filesystem case sensitivity; use generic path APIs and explicit encodings instead of guessing fixed filesystem locations.
- When a script needs Python, use the current runtime's interpreter when exposed; otherwise probe Python 3.10+ and verify its version. On Windows try `py -3` then `python`; on macOS and Linux try `python3` then `python`. Reject Microsoft Store aliases or any candidate that cannot execute and report the missing tool clearly; never degrade silently.
- Prefer `--version` or `--help` output when a tool version matters. If the
  version cannot be confirmed, report that limitation.

## Recovery and user-assisted execution

Before potentially destructive or hard-to-reverse work, verify the task's recovery prerequisite per `references/14-backup-manager.md`. If inadequate, ask Commander to dispatch Backup Manager and keep only the risky action blocked. A successful command or Git commit alone does not prove recovery coverage.

Use `references/15-collaboration.md` when missing information, authentication, browser controls or repeated automation failures are better resolved by the user. Ask for a precise safe action/result, not credentials; continue independent work. Tool unavailability is a reason to offer an alternative, not silently prohibit all network or delegation.

## Filesystem operations

- Prefer the host's file-editing capability for modifying existing files; avoid whole-file rewrites.
- Delete only files this task created and confirmed as owned by this task.
- Before deletion, resolve the target's real path and confirm it sits inside the expected workspace; after deletion, verify the target no longer exists.
- Prefer platform-generic search tools for files and content (e.g. rg); when unavailable, fall back to the generic recursive scan method probed at runtime.
- Keep modifications minimal; never revert any change outside the task's scope.

## Shell/CLI selection

- Bind to no specific shell: invoke the verified interpreter directly; adopt no shell-specific syntax in portable commands.
- For cross-platform-consistent text and file processing, prefer the Python standard library over platform-specific command combinations.
- Locate external CLIs via environment variables and PATH; host-agnostic (Host-agnostic): rely only on the generic stdin/stdout and exit-code contract, never match any specific Agent CLI's private interfaces or call details.

## Encoding

- All text deliverables, reports, and scripts are uniformly UTF-8: preferably without BOM, with LF line endings; verify both properties after writing.
- Read text files with an explicit UTF-8 encoding, never relying on the interpreter's or terminal's default encoding.
- Console mojibake is not evidence of file corruption; verify with explicit-encoding reads, file hashes, or actual parse results.
- Write text in a way that produces no BOM (e.g. Python `open(..., encoding='utf-8')`), avoiding BOM or CRLF introduced by older interpreters' default encodings and newline semantics.
- Always use explicit UTF-8 encoding when Python handles non-ASCII text; never pipe script content containing non-ASCII text through an interpreter - when needed, write the script to a workspace temp file as UTF-8 without BOM first, then execute it, and clean it up per the temp-file rules afterward.

## Paths

- Hard-code no absolute paths or host-private directory layouts; resolve base locations such as the user's home directory at runtime via platform-standard environment variables (e.g. HOME, USERPROFILE) or generic path APIs.
- Prefer absolute paths for writes outside the workspace; confirm the current working directory before using relative paths.
- Resolve paths to real paths (resolve/realpath semantics) before operating, avoiding mishaps from symlinks and relative-path ambiguity.
- Doc examples always use platform-agnostic relative paths or placeholders; no machine-specific directories appear.

## Command result verification

- Use more than the exit code to judge success: check the expected stdout, stderr, generated files, and their content as well.
- Some CLIs' help commands may return non-zero exit codes while outputting help normally; follow the task's expectation.
- Repeated stderr notices that are irrelevant and do not affect results can be ignored, but note them in the verification log.
- When output is truncated, write stdout and stderr to a log file prefixed `_tmp` in the workspace, then read it in segments.
- Key numbers, file paths, and cited content must be read and verified directly from the final output file; after modification, re-read to verify the citations match the source file.
- When running verification scripts, record the environment, inputs, outputs, and failure information.

## Temp files

- All temp files and probe artifacts stay in the workspace, prefixed `_tmp`, e.g. `_tmp_analysis.log`.
- Delete every temp file this task produced at task wrap-up; leave none behind in the workspace.
- Do not auto-probe document format conversions (e.g. PDF conversion may hang); deliver source-format files plus manual conversion instructions instead.

## Error recovery

- Console display anomalies never trigger rebuilding a file: first verify with explicit-encoding reads or file hashes, handle it only after confirming real corruption.
- When a command fails, fix the input and the command based on the verification results, then retry; if retries keep failing, stop and report per the task's requirements.
- Conversion operations (e.g. document to PDF) that fail are not retried automatically; instead deliver the source file with manual conversion instructions for the user to complete.
- Recovery never touches files outside the task's scope; on abnormal termination, first ensure already-written file contents are complete and verifiable.
