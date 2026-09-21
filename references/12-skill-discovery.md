# Host-Neutral Skill Discovery Protocol

> Purpose: when generating `background/02_skill_list.md`, avoid reading every Skill body. First read only the YAML frontmatter with the script, dedupe and filter; read the full body only for candidate Skills. Host installation conventions and capability fallbacks live in `references/host-adapters.md`.

## When to run

Confirm the project goal, scope, deliverables, constraints, and key terms first; then scan Skills. Do not traverse all skill directories early while the context is still vague.

## Scan entry

Use the absolute path to the Task Commander Skill root; the script may be installed somewhere unrelated to the project being analyzed:

`<absolute Task Commander root>/scripts/scan-skills.py`

Anchor discovery on the project, not on the installed Skill:

```text
# Run from the project root, or pass --project-root
<python> <absolute Skill root>/scripts/scan-skills.py --project-root <project root> --host <profile> --query-terms <query term 1> <query term 2> --max-results 30
```

Discovery is driven by an explicit profile, not by the current host's identity:

- `--host` selects the candidate path profile: `all` (default), `codex`, `opencode`, `claude-code`, `cursor`, `copilot`, or `pi`. A profile is a list of documented candidate paths, not evidence that the host is installed, trusted or enabled.
- `--project-root` sets the starting directory for project-level discovery (default: the current working directory): nearest directories first, walking upward to the Git worktree top when Git reports one, otherwise to the filesystem root.
- User-level paths come from the current user's home directory. `CODEX_HOME` overrides the Codex base; `PI_CODING_AGENT_DIR` overrides the Pi user configuration base.
- Nonempty `--roots` replaces discovery entirely, for custom, managed or package-contained locations.
- Only existing directories are scanned, each real path once. Directory symlinks are followed with cycle protection so a symlinked installation is not missed.

The exact candidate paths, ordering and limits are in `scripts/scan-skills.py --help`, its module docstring, and the adaptation table in `references/host-adapters.md`.

Root order is also duplicate priority. When the same skill name appears more than once, the first occurrence is kept and the remaining paths are recorded in `duplicate_paths`. This is the scanner's own inventory policy: a native host may keep multiple variants or resolve conflicts differently, so verify which path was actually selected before relying on it. Use `--host all` only for cross-host inventory; a skill found in another host's directory may not be loadable here.

## Two-phase discovery

### Phase one: metadata filtering

1. Extract 5-15 query terms from `01_project_background.md` and `CONTEXT.md`, covering domain, deliverables, technology stack, and task types.
2. Run the scan script; it reads only the YAML frontmatter at the top of each `SKILL.md`, never the body.
3. Match query terms against names and descriptions and score them.
4. Keep at most 30 candidates by default; when results are short, supplement with same-domain skills or skills the user explicitly specified.

### Phase two: candidate verification

Run only on phase-one candidates:

- Read the full `SKILL.md`.
- Confirm the real trigger and applicable scenarios.
- Confirm whether network, plugins, or subagents are needed.
- Drop skills that are irrelevant to the project, functionally duplicate, or missing dependencies.

Do not keep reading unselected Skills' bodies "just in case".

## Output requirements

`background/02_skill_list.md` records, for every final inclusion:

- Skill name
- Choice reason
- Trigger
- Applicable tasks
- Absolute path
- Network required or not
- Plugin required or not
- Subagent required or not
- Duplicate install paths (if any)

Absolute paths are resolved for the active workspace and current session. They
are not portable artifacts that can be reused unchanged on another machine.

The scan result is a candidate list, not the final checklist. The final judgment must combine the project background and the candidate bodies.

## Fallback rules

When the script cannot run:

1. Still read only the frontmatter of each `SKILL.md`.
2. Dedupe by name using the profile's directory priority.
3. Filter candidates first, then read the candidate bodies.
4. Record the script failure reason and the fallback method used in the delivery notes.

## Adaptation examples (examples for adaptation, not the default protocol)

The directories below are the documented values the discovery profiles take on currently known hosts. Treat them as adaptation examples, not as proof that this host is installed, trusted or enabled. When the host or version changes, trust the runtime discovery results and its current documentation.

| Host / profile | Project skill directory | User skill directory |
|---|---|---|
| Codex / `codex` | `.agents/skills/` | `~/.agents/skills/`; `$CODEX_HOME/skills/` and the plugin caches are compatibility paths |
| OpenCode / `opencode` | `.opencode/skills/`; also `.agents/skills/`, `.claude/skills/` | `~/.config/opencode/skills/`; also `~/.agents/skills/`, `~/.claude/skills/` |
| Claude Code / `claude-code` | `.claude/skills/` | `~/.claude/skills/` |
| Cursor / `cursor` | `.cursor/skills/`, `.agents/skills/`; also `.claude/skills/`, `.codex/skills/` | `~/.cursor/skills/`, `~/.agents/skills/`; also `~/.claude/skills/`, `~/.codex/skills/` |
| GitHub Copilot / `copilot` | `.github/skills/`; also `.claude/skills/`, `.agents/skills/` | `~/.copilot/skills/`, `~/.agents/skills/` |
| Pi / `pi` | `.pi/skills/` (local to the project start) and `.agents/skills/` (ancestor-walked) | `~/.pi/agent/skills/` and `~/.agents/skills/`; `PI_CODING_AGENT_DIR` overrides the Pi base |

Host-specific caveats the scanner deliberately does not reproduce:

- Pi loads project resources only when the project is trusted; in non-interactive mode an unsaved trust decision can mean the files are found but not loaded.
- Pi also discovers configured skill paths, packages and some standalone `.md` files. The scanner reads neither host configuration files nor packages; pass `--roots` for those locations.
- Native hosts decide description-based versus explicit-only invocation, name conflicts and managed/enterprise directories themselves. The scanner reports metadata; it does not enforce host policy or authorize invoking a skill.
- Installing this Skill adds instructions, not agent runtimes: subagent dispatch, parallel windows and background execution exist only when the host really provides them, per `references/host-adapters.md`.

Sources for these conventions are recorded in `references/host-adapters.md`, together with the verification boundary: automated tests cover synthetic directories and protocol text, not live host integrations.
