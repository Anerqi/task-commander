# Host Adapters and Capability Fallbacks

> Read when installing Task Commander, starting on a new host, changing execution environments, or encountering a missing capability. Host names select documented conventions, not authority or guaranteed tool availability.

## Portable contract

The core is `SKILL.md` plus role references, durable project files and optional Python helpers. It does not require a particular model, slash command, agent SDK or message bus. Copy the complete `task-commander/` directory, not just its entry file; relative references and scripts must stay together.

For a host with native Skills, install in a location that host actually loads and invoke its native skill mechanism. Otherwise ask the agent to read the absolute path to `SKILL.md`, then follow its selected role branch. An `AGENTS.md` or other host instruction file may point to that entry with user approval; do not overwrite existing host instructions or paste all role bodies into them.

A file-readable host without native Skills can run the protocol through manual entry loading. A host without workspace access can only draft instructions from supplied material: ask the user to save and verify the durable files before handing off. Do not claim full file-based orchestration, validated status or completed writes from pasted text alone.

## Installation conventions

Append `task-commander/` to a skill-directory location below. `~` means the current user's home; use the remote/container home when the agent runs there. These are documentation-backed locations, not evidence that the application is installed, trusted, enabled, or tested in this environment.

| Host / scanner profile | Project skill directory | User skill directory | Invocation / caveat |
|---|---|---|---|
| Codex / `codex` | `.agents/skills/` | `~/.agents/skills/` | Native skill selection or `$task-commander`; older `$CODEX_HOME/skills/` remains a scanner compatibility path, not the only installation option |
| OpenCode / `opencode` | `.opencode/skills/` | `~/.config/opencode/skills/` | Ask to load `task-commander` with the native skill mechanism; also recognizes shared `.agents/skills/` and Claude-compatible locations |
| Claude Code / `claude-code` | `.claude/skills/` | `~/.claude/skills/` | `/task-commander` or native description-based selection; project trust and host policy still apply |
| Cursor / `cursor` | `.cursor/skills/` or `.agents/skills/` | `~/.cursor/skills/` or `~/.agents/skills/` | Use native Skills selection; local user skills are not automatically available in remote/cloud execution |
| GitHub Copilot / `copilot` | `.github/skills/` | `~/.copilot/skills/` or `~/.agents/skills/` | Skills-capable agent/CLI surfaces; support and user-directory access depend on the surface/version, not merely a Copilot subscription |
| Pi / `pi` | `.pi/skills/` or `.agents/skills/` | `~/.pi/agent/skills/` or `~/.agents/skills/` | `/skill:task-commander` when skill commands are enabled; `PI_CODING_AGENT_DIR` overrides the Pi user configuration base |
| Other file-readable host | User-selected accessible directory | User-selected accessible directory | Load the absolute entry path manually; pass explicit directories to the scanner |

The installation table is not a complete reproduction of native discovery. Codex, OpenCode, Cursor and Copilot have shared/compatibility paths; Pi also has configured skill files and packages. Hosts may add managed directories, trust gates or version-specific behavior. See `references/12-skill-discovery.md` for what the helper scans and what it does not.

`agents/openai.yaml` is an optional Codex/OpenAI descriptor. Other hosts need neither that file nor an equivalent proprietary descriptor to read the core Skill. Do not turn it into a universal runtime API.

## Capability check, once per environment

Inspect available tools and non-sensitive runtime facts before choosing an execution path. A host name, environment variable or discovered directory is a hint, not proof of a usable capability. Record a concise host/capability snapshot in the project's Collaboration policy: host/version if known, workspace root, selected discovery profile or explicit roots, relevant available tools, limitations, and separate effective authorization sources. Reuse it until the environment changes; do not repeatedly probe on every file operation.

| Capability | If present and authorized | If absent or restricted |
|---|---|---|
| Workspace reads | Read authoritative files and resolve project/Skill roots | Request the specific safe excerpts or local user action; label uninspected facts |
| Workspace writes | Use the host's edit/write tools; preserve other work | Provide proposed text/patches for the user to save; verify returned paths/content before claiming durable state |
| Python 3.10+ and command execution | Run scanner and validator via the verified interpreter | Use frontmatter-only/manual checks or ask the user to run the command; record CLI validation as not run until evidence returns |
| Independent agent dispatch | Use the host's actual tool contract and scoped outputs | Emit separately copyable task prompts for user-opened windows; record pickup only after acknowledgment |
| Parallel/background execution | Use supported isolated tasks within capacity and write boundaries | Run safe work sequentially or let the user relay independent windows; never simulate a background task or invent a session ID |
| Persistent sessions | Continue the actual task window | Reconstruct from saved brief, receipt and evidence using `templates/task-continuation.md` |
| Network/browser tools | Use within effective authorization and data boundaries | Use available local sources or a precise user-assisted action; disclose freshness/coverage limits |
| Structured question UI | Use the host's question tool | Ask the same focused question in ordinary text |

Capability availability never grants permission. Follow `references/15-collaboration.md` (Policy activation); a missing optional tool blocks only the action that needs it. Neither manual operation nor host switching waives required gates, backup prerequisites or user decisions. If a required check cannot be established, keep it unverified rather than calling it passed.

## Discovery is not execution

- Prefer a known host profile when building that host's usable skill list. Use `all` only for cross-host inventory; an inventory entry may not be natively loadable in the current host.
- Follow the host's actual skill restrictions, including explicit-invocation-only metadata, trust and allowlists. The scanner returns metadata; it does not enforce those restrictions or authorize invoking a skill.
- For custom paths, managed installs or package-contained resources, supply approved `--roots` explicitly. Do not scrape arbitrary settings, secrets, plugin caches or the whole home directory to guess capabilities.
- The scanner's first-name-wins deduplication and candidate ordering are its own inventory policy. Native hosts may keep multiple variants or choose different precedence. Verify the selected path before use.
- Switching hosts does not change task identity, project authority or acceptance criteria. Refresh machine-specific absolute pointers and capability/permission snapshots; preserve task IDs, history and still-valid evidence.

## Sources and verification boundary

Installation conventions were checked against the following documentation; a future host/version change should be checked against its current docs before changing an adapter:

- Codex: https://developers.openai.com/codex/skills
- OpenCode: https://opencode.ai/docs/skills/
- Claude Code: https://code.claude.com/docs/en/skills
- Cursor: https://cursor.com/docs/context/skills
- GitHub Copilot: https://docs.github.com/en/copilot/concepts/agents/about-agent-skills
- Pi: the installed host's `README.md`, `docs/skills.md`, `docs/settings.md`, `docs/packages.md` and `docs/environment-variables.md`; resolve these under the host installation, not the target project.

Automated tests exercise Python discovery against synthetic directories and protocol text contracts. They do not certify six live host integrations, native invocation, model compliance, project trust or cloud synchronization. Record actual host/model smoke-test results separately using `tests/behavioral-scenarios.md`.
