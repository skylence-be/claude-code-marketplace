---
name: archon-cli-reference
description: Complete Archon CLI reference — every subcommand, flag, and option with concrete examples. Covers chat, workflow (list/run/status), isolation (list/cleanup), continue, complete, setup, serve, validate (workflows/commands), version, help. Use when invoking Archon from the command line, writing shell scripts that dispatch workflows, debugging setup, or diagnosing isolation/worktree issues.
category: engineering
tags: [archon, cli, commands, workflow, isolation]
related_skills: [archon-dag-workflow-authoring, archon-isolation-and-worktrees]
---

# Archon CLI Reference

Full reference for the `archon` command-line interface in v0.3.5. Based on `archon help` output and source inspection.

## Top-Level Synopsis

```
archon <command> [subcommand] [options] [arguments]
```

## Command Groups

### `chat <message>` — Send a message to the orchestrator

Conversational interaction. The orchestrator decides whether to route to a workflow or respond inline.

```bash
archon chat "What does the orchestrator do?"
archon chat "Plan a refactor to extract payment handling into its own module"
```

### `workflow` — Workflow management

**`workflow list`** — List available workflows in the current directory. Merges bundled defaults with `.archon/workflows/*.yaml`.

```bash
archon workflow list
archon workflow list --json       # machine-readable
```

**`workflow run <name> [message]`** — Run a workflow with an optional user message.

```bash
# Run bundled workflow
archon workflow run archon-fix-github-issue "Fix issue #42"

# Run in isolated worktree (recommended)
archon workflow run archon-fix-github-issue --branch fix/issue-42 "Fix #42"

# Run from a different start-point
archon workflow run archon-feature-development \
  --branch feat/dark-mode \
  --from main \
  "Add dark mode toggle"

# Run in a different repo
archon workflow run archon-plan --cwd /path/to/other/repo "Plan new feature"

# Run without worktree isolation (writes directly to current branch — use sparingly)
archon workflow run quick-fix --no-worktree "Fix typo in README"

# Resume the most recent failed run
archon workflow run archon-fix-github-issue --resume
```

**`workflow status`** — Show status of running workflows.

```bash
archon workflow status
```

Returns `Active workflows (N):` with `ID:`, `Name:`, `Path:`, `Status:`, `Age:` per entry.

### `isolation` — Worktree / environment management

**`isolation list`** — List all active worktrees/environments.

**`isolation cleanup [days]`** — Remove stale environments.

```bash
archon isolation cleanup          # default: 7 days
archon isolation cleanup 14       # remove envs older than 14 days
archon isolation cleanup 0        # remove ALL envs
archon isolation cleanup --merged # only envs with branches merged into main
```

### `continue <branch> [message]` — Continue prior work

Continues work on an existing worktree with its prior conversation context.

```bash
archon continue fix/issue-42 "Address the review feedback"
archon continue fix/issue-42 --workflow archon-smart-pr-review "Review latest push"
archon continue fix/issue-42 --no-context "Start fresh"
```

Default workflow for `continue` is `archon-assist`.

### `complete <branch>` — Branch lifecycle completion

Removes the worktree and associated branches after a PR is merged/closed.

```bash
archon complete fix/issue-42
archon complete review/pr-1
```

### `setup` — Interactive setup wizard

Walks through credentials, config, platform selection.

```bash
archon setup
archon setup --spawn      # open wizard in a new terminal window
```

### `serve` — Web UI server

Starts the full web UI at `http://localhost:3090`. Binary users: downloads a prebuilt web UI tarball on first run, verifies SHA-256, caches locally.

```bash
archon serve
archon serve --port 4000
archon serve --download-only   # cache web UI without starting
```

### `validate` — Static validation

**`validate workflows [name]`** — Validate YAML workflow files.

```bash
archon validate workflows                         # all workflows
archon validate workflows archon-smart-pr-review  # one workflow
archon validate workflows --json                  # machine-readable
```

Checks:
- YAML syntax + required fields
- DAG structure (cycles, missing depends_on, invalid `$nodeId.output` refs)
- All `command:` references exist
- All `mcp:` configs exist with valid JSON
- All `skills:` directories exist

**`validate commands [name]`** — Validate command `.md` files.

```bash
archon validate commands                # all commands
archon validate commands my-command     # one command
```

### `version` — Show version info

```bash
archon version
```

### `help` — Show help

```bash
archon help
archon <command> --help
```

## Global Options

| Flag | Meaning |
|---|---|
| `--cwd <path>` | Override working directory (default: current) |
| `--branch <name>` / `-b <name>` | Create worktree for branch (reuses if exists) |
| `--from <name>` / `--from-branch <name>` | Base branch for new worktree |
| `--no-worktree` | Run directly on current branch without isolation |
| `--resume` | Resume most recent failed run (mutually exclusive with `--branch`) |
| `--workflow <name>` | Used by `continue` to pick a workflow (default: `archon-assist`) |
| `--no-context` | Skip context injection for `continue` |
| `--allow-env-keys` | Grant env-key consent during auto-registration (security gate override) |
| `--spawn` | Used by `setup` to open in a new terminal window |
| `--port <n>` | Used by `serve` to override default 3090 |
| `--download-only` | Used by `serve` to cache web UI without starting |
| `--quiet` / `-q` | Reduce log verbosity to warnings and errors |
| `--verbose` / `-v` | Show debug-level output |
| `--json` | Machine-readable output (for `workflow list`) |

## Common Workflows

### Full PR lifecycle

```bash
# 1. Fix an issue in an isolated worktree
archon workflow run archon-fix-github-issue --branch fix/issue-42 "Fix #42"

# 2. Review the resulting PR
archon workflow run archon-smart-pr-review --branch review/pr-17 "Review PR #17"

# 3. If human feedback lands, continue
archon continue fix/issue-42 --workflow archon-smart-pr-review "Address feedback"

# 4. After merge, complete the lifecycle
archon complete fix/issue-42
```

### Parallel issue fan-out

```bash
archon workflow run archon-fix-github-issue --branch fix/issue-10 "Fix #10" &
archon workflow run archon-fix-github-issue --branch fix/issue-11 "Fix #11" &
archon workflow run archon-fix-github-issue --branch fix/issue-12 "Fix #12" &
wait
```

Each gets its own worktree — they don't conflict.

### Debug a stuck workflow

```bash
# Inspect live state
archon workflow status

# Check the DB directly
sqlite3 ~/.archon/archon.db "
  SELECT workflow_name, status, started_at, completed_at
  FROM remote_agent_workflow_runs
  ORDER BY started_at DESC LIMIT 5
"

# Inspect per-node events
sqlite3 ~/.archon/archon.db "
  SELECT event_type, step_name, substr(data, 1, 200)
  FROM remote_agent_workflow_events
  WHERE workflow_run_id = '<run-id>'
  ORDER BY created_at
"

# Kill a stuck workflow (no archon CLI command exists — kill processes directly)
ps -ef | grep claude-agent-sdk | grep -v grep
kill <pid>
```

## Exit Codes

- `0` — Success
- Non-zero — Various errors; check stderr for details

## Environment

- `~/.archon/.env` — global config (WEBHOOK_SECRET, GITHUB_TOKEN, GH_TOKEN, GITHUB_ALLOWED_USERS, GITHUB_BOT_MENTION, DEFAULT_AI_ASSISTANT, PORT, DATABASE_URL, CLAUDE_USE_GLOBAL_AUTH, MAX_CONCURRENT_CONVERSATIONS)
- `~/.archon/archon.db` — SQLite database for codebases, conversations, workflow runs, isolation environments
- `~/.archon/workspaces/<owner>/<repo>/` — managed worktree workspace root
- `~/.archon/config.yaml` — global user config (assistants, concurrency)
- `<repo>/.archon/config.yaml` — per-repo config (worktree.copyFiles, defaults.loadDefaultWorkflows, etc.)

## Shell Completion

Not shipped by default as of v0.3.5. Track [issue #1011](https://github.com/coleam00/Archon/issues/1011) or similar for updates.
