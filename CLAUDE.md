# CLAUDE.md

## Development Rules

1. **TDD First** — Write tests before implementation, even for markdown files. See `tests/unit/test_skill_structure.py` for examples.

2. **Run Tests** — `uv run pytest` before committing.

## Project Structure

```
rhdh-skill/
├── commands/                    # Slash commands for Claude Code
├── skills/
│   ├── rhdh/                    # Orchestrator skill (Python CLI + routing)
│   │   ├── rhdh/                # Python CLI package (stdlib only)
│   │   ├── scripts/             # Entry point (./scripts/rhdh)
│   │   ├── references/          # Tool refs (GitHub, JIRA, repos, versions)
│   │   └── SKILL.md             # Main intake + routing to sub-skills
│   ├── overlay/                 # Overlay skill (markdown only)
│   │   ├── workflows/           # Plugin workflows (onboard, update, fix, triage)
│   │   ├── references/          # Overlay-specific refs (CI, labels, metadata)
│   │   ├── templates/           # Workspace file templates
│   │   └── SKILL.md             # Overlay workflow routing
│   ├── rhdh-local/              # Local testing skill (Python CLI + workflows)
│   │   ├── rhdh_local/          # Python CLI package (compose, health, sync)
│   │   ├── scripts/             # Entry point (./scripts/rhdh-local)
│   │   ├── workflows/           # Local workflows (enable, disable, test, switch)
│   │   ├── references/          # Customization, env, troubleshooting refs
│   │   └── SKILL.md             # Local testing intake
│   ├── create-backend-plugin/   # Bootstrap backend dynamic plugins
│   ├── create-frontend-plugin/  # Bootstrap frontend dynamic plugins
│   ├── export-and-package/      # Export & package as OCI/tgz/npm
│   └── generate-frontend-wiring/ # Configure mount points, routes, tabs
├── .claude-plugin/              # Plugin manifest + marketplace listing
├── .planning/                   # Planning docs for future features
├── tests/                       # pytest test suite (dev only)
└── pyproject.toml               # Dev dependencies (pytest, ruff)
```

## CLIs

Two stdlib-only Python CLIs (Python 3.9+), auto-detecting output format (**TTY** → human-readable, **Piped** → JSON):

### `rhdh` — Orchestrator CLI

```bash
./skills/rhdh/scripts/rhdh                   # Status (orientation)
./skills/rhdh/scripts/rhdh doctor            # Full environment check
./skills/rhdh/scripts/rhdh config init       # Create config with auto-detection
./skills/rhdh/scripts/rhdh config show       # Show resolved paths
./skills/rhdh/scripts/rhdh config set <k> <v> # Set config value
./skills/rhdh/scripts/rhdh setup submodule list  # List available repos
./skills/rhdh/scripts/rhdh setup submodule add --all  # Add all required repos
./skills/rhdh/scripts/rhdh workspace list    # List plugin workspaces
./skills/rhdh/scripts/rhdh workspace status <name>
./skills/rhdh/scripts/rhdh log add "msg" --tag x  # Activity worklog
./skills/rhdh/scripts/rhdh log show / search
./skills/rhdh/scripts/rhdh todo add / list / done / note / show
./skills/rhdh/scripts/rhdh local up / down / status / apply / health  # Delegates to rhdh-local
```

### `rhdh-local` — Local Testing CLI

```bash
./skills/rhdh-local/scripts/rhdh-local       # Standalone local testing CLI
```

Both CLIs follow [agentic CLI design patterns](https://github.com/durandom/dotfiles/blob/main/skills/recipes/references/agentic-cli.md) (`/recipes agentic-cli`).

## Key Patterns

- `OutputFormatter` handles JSON/human rendering — commands build data dicts
- Workflows live in `skills/overlay/workflows/` and `skills/rhdh-local/workflows/`
- Config discovery: env vars → project config → user config → auto-detection
- `commands/` dir provides slash commands that Claude Code auto-discovers
- `rhdh` CLI delegates `local` subcommands to `rhdh_local.cli` module

## Versioning

Single version (`0.2.0`) kept in sync across three files:

- `pyproject.toml` — Python package version
- `.claude-plugin/plugin.json` — plugin manifest
- `.claude-plugin/marketplace.json` — marketplace listing (2 occurrences)

Bump all three when releasing.
