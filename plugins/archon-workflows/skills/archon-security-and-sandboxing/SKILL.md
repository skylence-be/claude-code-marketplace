---
name: archon-security-and-sandboxing
description: Master Archon's three layered security systems — (1) the env-leak gate (v0.3.0+) that scans target repo .env files for sensitive keys and blocks subprocess spawn unless the codebase has allow_env_keys=true or is launched with --allow-env-keys, (2) the SUBPROCESS_ENV_ALLOWLIST that filters which process.env vars reach Claude/Codex subprocesses, and (3) the SandboxSettings schema (sandbox field on DAG nodes) that passes Claude Agent SDK OS-level filesystem/network restrictions (allowedDomains, allowWrite/denyWrite, allowLocalBinding, proxy ports). Use when debugging env-leak errors, configuring per-codebase consent, writing workflows that need network restrictions, or understanding why a legitimate env var isn't reaching a subprocess.
category: engineering
tags: [archon, security, env-leak, sandbox, allowlist, consent]
related_skills: [archon-dag-workflow-authoring, archon-architecture-deep-dive, archon-isolation-and-worktrees]
---

# Archon Security and Sandboxing

Archon has three layered security systems that protect against credential leakage and malicious code execution:

1. **Env-leak gate** — scans target repo `.env` files for sensitive keys and blocks subprocess spawn unless explicit consent is given
2. **Subprocess env allowlist** — filters which `process.env` vars reach Claude/Codex subprocesses
3. **Sandbox settings** — per-node OS-level filesystem and network restrictions passed to the Claude Agent SDK

All three work together to prevent a malicious or poorly-configured workflow from exfiltrating credentials or attacking the host.

## When to Use This Skill

- Debugging "Cannot run workflow — contains keys that will leak" errors
- Configuring per-codebase consent for env keys
- Writing workflows that need restricted network access (HTTPS allowlist, no DNS)
- Understanding why a legitimate env var isn't reaching your subprocess
- Adding a new repo with a `.env` file that has credentials
- Auditing the security posture of Archon in a multi-team setup

## System 1: The Env-Leak Gate (v0.3.0+)

### The Problem

Bun (the JS runtime Archon uses) **auto-loads `.env` from the current working directory** when any subprocess starts. If a workflow spawns Claude Code with `cwd = /path/to/target-repo`, and that target repo has a `.env` file containing `ANTHROPIC_API_KEY=...` or `OPENAI_API_KEY=...`, Bun silently injects those vars into Claude's environment. **Archon cleans its own env before spawning subprocesses, but Bun's auto-load happens anyway.**

Consequences:
- API calls billed to the wrong account (the repo owner's, not Archon's)
- Keys visible to any Claude tool call that logs environment
- Silent — no error, no warning by default

### The Gate

`packages/core/src/utils/env-leak-scanner.ts` implements a pre-spawn scanner that runs before Archon spawns any Claude/Codex subprocess:

1. **Scan** the target repo's `.env`, `.env.local`, `.env.*` files
2. **Extract** all keys matching a sensitive-keys set (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `CLAUDE_CODE_OAUTH_TOKEN`, `GITHUB_TOKEN`, `OPENROUTER_API_KEY`, etc.)
3. **If any found** → **block** the spawn with a detailed `EnvLeakError`:

```
Cannot run workflow — /path/to/repo contains keys that will leak into AI subprocesses

Found:
    .env — ANTHROPIC_API_KEY, OPENAI_API_KEY

Why this matters:
Bun subprocesses auto-load .env from their working directory. Archon cleans
its own environment, but Claude/Codex subprocesses running with cwd=<this repo>
will re-inject these keys at their own startup, bypassing archon's allowlist.
This can bill the wrong API account silently.

Choose one:
    1. Remove the key from this repo's .env (recommended):
         grep -v '^ANTHROPIC_API_KEY=' .env > .env.tmp && mv .env.tmp .env

    2. Rename to a non-auto-loaded file:
         mv .env .env.secrets
         # update your app to load it explicitly

    3. Acknowledge the risk — see "Consent Paths" below
```

### Consent Paths

Three ways to grant explicit consent so the gate lets the workflow proceed:

#### 1. Per-codebase consent (CLI)

When **registering a new codebase** via CLI, add the `--allow-env-keys` flag:

```bash
archon workflow run my-workflow --branch fix/xyz --allow-env-keys "Fix xyz"
```

This sets `allow_env_keys = 1` on the `remote_agent_codebases` row for this project. Persists across runs — you won't need to re-flag.

**What it does**: Archon still scans the `.env` at spawn time (scan always runs). When keys are found AND the codebase has `allow_env_keys: true`, the error is downgraded to a warning log (`env_leak_gate.consented_codebase_spawn`) and the spawn proceeds.

#### 2. Per-codebase consent (UI)

Via the Archon Web UI: Settings → Projects → find the project → toggle **"Allow env keys"**. Same effect as the CLI flag, but persisted per-codebase in the DB.

#### 3. Global bypass (DANGEROUS)

`~/.archon/config.yaml`:

```yaml
# WARNING: disables the env-leak gate for ALL codebases
allow_target_repo_keys: true
```

This weakens the gate globally — every codebase's env keys will leak into subprocesses. Use only in trusted single-developer setups where you fully understand the consequences.

**Per-repo override**: `<repo>/.archon/config.yaml` can override the global setting:

```yaml
# Repo-local override — wins over global
allow_target_repo_keys: true          # or false to force re-enable
```

### Consent Audit Trail

Every time the gate is bypassed, Archon emits a structured warning log:

```json
{
  "level": "warn",
  "source": "env_leak_gate_disabled",
  "codebasePath": "/Users/jv/webdev/tastytrade.skylence.be",
  "reason": "allow_env_keys consent"
}
```

Also logged: the first time a user bypasses the gate for a given source (global config vs repo config vs per-codebase), a one-time warning is emitted so it shows up in ops review.

### Gate Behavior in Compiled Binaries

In `v0.3.4+`, the binary distribution changed how `~/.archon/.env` is loaded (`override: true` for all keys, not just `DATABASE_URL`). **The gate still runs regardless** — binary mode doesn't auto-bypass anything. Consent paths are unchanged.

## System 2: Subprocess Env Allowlist

### The Problem

Even with the env-leak gate catching `.env`-loaded keys, the Archon **server process** has access to everything in its own environment (which includes Archon's legitimate credentials, system PATH, shell config, etc.). If Archon spreads `process.env` into a Claude subprocess, all of that leaks too.

### The Allowlist

`packages/core/src/utils/env-allowlist.ts` defines `SUBPROCESS_ENV_ALLOWLIST` — a canonical set of env vars that Claude/Codex subprocesses legitimately need:

**System essentials** (needed by tools, git, shell ops):
- `PATH`, `HOME`, `USER`, `LOGNAME`, `SHELL`, `TERM`, `TMPDIR`, `TEMP`, `TMP`, `LANG`, `LC_ALL`, `LC_CTYPE`, `TZ`, `SSH_AUTH_SOCK`

**Claude auth and config**:
- `CLAUDE_USE_GLOBAL_AUTH`, `CLAUDE_API_KEY`, `CLAUDE_CODE_OAUTH_TOKEN`
- `CLAUDE_CODE_USE_BEDROCK`, `CLAUDE_CODE_USE_VERTEX`
- `ANTHROPIC_BASE_URL`, `ANTHROPIC_BEDROCK_BASE_URL`, `ANTHROPIC_VERTEX_PROJECT_ID`, `ANTHROPIC_VERTEX_REGION`

**Archon runtime config**:
- `ARCHON_HOME`, `ARCHON_DOCKER`, `IS_SANDBOX`, `WORKSPACE_PATH`, `LOG_LEVEL`

**Git identity** (used by git commits inside workflows):
- `GIT_AUTHOR_NAME`, `GIT_AUTHOR_EMAIL`, `GIT_COMMITTER_NAME`, `GIT_COMMITTER_EMAIL`, `GIT_SSH_COMMAND`

**GitHub CLI** (used by Claude tools):
- `GITHUB_TOKEN`, `GH_TOKEN`

**Anything else is dropped** — Archon builds a clean subprocess env from `process.env` filtered through this allowlist.

### Per-Codebase Env Additions

Workflows can declare additional env vars per codebase via the `codebase_env_vars` table (written by `.archon/config.yaml` `env:` key):

```yaml
# <repo>/.archon/config.yaml
env:
  STRIPE_API_KEY: sk_test_xxx         # plain value
  DB_URL: ${LOCAL_DB_URL}             # reads from Archon server's env
```

These are **merged on top** of the allowlist by the workflow executor via `requestOptions.env`. Subprocesses see them in addition to the allowlist vars. **They bypass the gate entirely** — once you've declared them in repo config, you've implicitly consented.

### Auth Filtering

`buildSubprocessEnv()` in `claude.ts` applies one additional filter: when `CLAUDE_USE_GLOBAL_AUTH` is set, it **strips** `CLAUDE_CODE_OAUTH_TOKEN` and `CLAUDE_API_KEY` from the allowlist. This prevents the subprocess from using explicit creds when the user wants it to fall back to Claude's global auth store.

## System 3: Sandbox Settings (per-node)

### The `sandbox:` Field on DAG Nodes

`packages/workflows/src/schemas/dag-node.ts:71` — `sandboxSettingsSchema` passes OS-level restrictions directly to the Claude Agent SDK. Applies to command and prompt nodes only (Claude-exclusive feature).

```yaml
- id: run-tests
  command: archon-run-tests
  sandbox:
    enabled: true
    autoAllowBashIfSandboxed: true
    allowUnsandboxedCommands: false
    filesystem:
      allowWrite:
        - ./tmp
        - ./test-results
      denyWrite:
        - .env
        - secrets/
      denyRead:
        - .env.secrets
    network:
      allowedDomains:
        - api.github.com
        - registry.npmjs.org
      allowManagedDomainsOnly: true
      allowLocalBinding: true          # allow binding to localhost
      httpProxyPort: 3128              # route HTTP through a proxy
    excludedCommands:
      - rm
      - rsync
```

### Top-Level Sandbox Fields

| Field | Type | Purpose |
|---|---|---|
| `enabled` | boolean | Master switch for sandboxing (default: SDK default) |
| `autoAllowBashIfSandboxed` | boolean | Auto-permit Bash tool when sandbox is active (usually blocked) |
| `allowUnsandboxedCommands` | boolean | Allow specific commands to run outside the sandbox |
| `enableWeakerNestedSandbox` | boolean | Loosen nested process isolation (for workflows that shell out heavily) |
| `enableWeakerNetworkIsolation` | boolean | Loosen network isolation (useful for DNS-needy operations) |
| `excludedCommands` | string[] | Commands that are always blocked, even if sandbox allows them |
| `ignoreViolations` | Record<string, string[]> | Suppress specific violation types |

### Filesystem Sub-Object

```yaml
sandbox:
  filesystem:
    allowWrite:          # paths the subprocess CAN write to
      - ./tmp
      - ./build
    denyWrite:           # paths the subprocess CANNOT write to (overrides allowWrite)
      - .env
      - .git/config
    denyRead:            # paths the subprocess CANNOT read at all
      - secrets/
```

**Semantics**: `allowWrite` is the permission base; `denyWrite` is an override that takes precedence. `denyRead` is absolute — even the AI can't see the file contents.

### Network Sub-Object

```yaml
sandbox:
  network:
    allowedDomains:                   # HTTPS allowlist
      - api.github.com
      - registry.npmjs.org
    allowManagedDomainsOnly: true     # DENY everything not in allowedDomains
    allowUnixSockets:                 # allow specific unix sockets
      - /var/run/docker.sock
    allowAllUnixSockets: false
    allowLocalBinding: true           # allow binding to 127.0.0.1 ports
    httpProxyPort: 3128               # route HTTP through localhost:3128
    socksProxyPort: 1080              # route SOCKS through localhost:1080
```

**Security hardening recipe**:

```yaml
sandbox:
  enabled: true
  network:
    allowManagedDomainsOnly: true
    allowedDomains:
      - api.github.com
      - registry.npmjs.org
    allowLocalBinding: false         # no localhost binds
  filesystem:
    denyWrite: [.env, .env.*, secrets/, .git/config]
    denyRead: [.env.secrets]
```

This limits the node to package installs and GitHub API only, no other network, no writing to sensitive config.

### Ripgrep Command Override

```yaml
sandbox:
  ripgrep:
    command: /opt/homebrew/bin/rg
    args: ["--max-filesize", "1M"]
```

If your sandbox denies access to the default `rg` location, you can point at a custom binary. Rare — only needed for unusual sandbox configurations.

### Sandbox Limitations

- **Claude only**: sandbox config is silently ignored on Codex nodes
- **Platform-dependent**: macOS uses different sandbox primitives than Linux; some fields are no-ops on certain platforms
- **Not a security boundary for malicious AI**: sandbox prevents accidental harm; a sufficiently clever AI can still try to exfiltrate via allowed channels (GitHub comments, npm publish, etc.). For hard isolation, use container-level sandboxing (Docker, Firejail) around Archon itself.

## Putting It All Together

A workflow that handles sensitive credentials safely:

```yaml
name: sensitive-deploy
description: |
  Use when: deploying to production with credentials that must not leak.
  Triggers: "deploy production", "release to prod".
  NOT for: dev deploys, local testing.

  Suggested branch: deploy/prod-YYYY-MM-DD

provider: claude
model: sonnet

nodes:
  - id: preflight
    bash: |
      set -e
      if [ ! -d node_modules ]; then pnpm install --frozen-lockfile; fi
      if [ ! -f .nuxt/eslint.config.mjs ]; then pnpm nuxi prepare; fi
    timeout: 600000

  - id: confirm-deploy
    approval:
      message: "⚠️ Deploying to production. Approve?"
      capture_response: true
    depends_on: [preflight]

  - id: deploy
    command: archon-deploy
    depends_on: [confirm-deploy]
    sandbox:
      enabled: true
      filesystem:
        allowWrite:
          - ./build
          - ./dist
        denyWrite:
          - .env
          - .env.*
          - secrets/
        denyRead:
          - .env.secrets
      network:
        allowManagedDomainsOnly: true
        allowedDomains:
          - api.github.com
          - api.vercel.com
          - registry.npmjs.org
    hooks:
      PreToolUse:
        - matcher: "Bash"
          response:
            permissionDecision: "ask"
            systemPromptAddition: |
              About to run a Bash command during production deploy.
              Double-check it's not destructive before proceeding.
    timeout: 1200000
```

Layers in effect:
1. **Env-leak gate** — scanned at spawn, will block unless repo has `allow_env_keys` consent
2. **Subprocess allowlist** — only allowed env vars reach the deploy subprocess
3. **Sandbox** — filesystem denies `.env` writes, network limited to GitHub + Vercel + npm
4. **Hooks** — every Bash call goes through a permission gate with AI self-review
5. **Approval** — human gate before the deploy node runs at all

## Diagnostic Commands

### Check a repo's env-leak status

```bash
# Look for sensitive keys in a repo's .env files
for f in /path/to/repo/.env*; do
  [ -f "$f" ] && grep -iE '^(ANTHROPIC|OPENAI|CLAUDE|GITHUB|OPENROUTER)_' "$f" 2>/dev/null
done
```

### Check allow_env_keys consent for a codebase

```bash
sqlite3 ~/.archon/archon.db "
  SELECT id, name, default_cwd, allow_env_keys, created_at
  FROM remote_agent_codebases
  WHERE name = '<owner>/<repo>'
"
```

### Set per-codebase consent manually

```bash
sqlite3 ~/.archon/archon.db "
  UPDATE remote_agent_codebases
  SET allow_env_keys = 1
  WHERE id = '<codebase-id>'
"
```

### Inspect what env vars a subprocess would see

Run with verbose logging to capture the `buildSubprocessEnv` output:

```bash
LOG_LEVEL=debug archon workflow run my-workflow --branch test "test"
```

Then grep the logs for `subprocess_env_built` — shows the allowlist-filtered env that Archon actually passed to Claude.

## Source of Truth

| Concern | File |
|---|---|
| Env-leak scanner | `packages/core/src/utils/env-leak-scanner.ts` |
| Sensitive keys set | `packages/core/src/utils/env-leak-scanner.ts` (`SENSITIVE_KEYS`) |
| Subprocess allowlist | `packages/core/src/utils/env-allowlist.ts` (`SUBPROCESS_ENV_ALLOWLIST`) |
| Pre-spawn gate check (Claude) | `packages/core/src/clients/claude.ts:273-290` |
| Pre-spawn gate check (Codex) | `packages/core/src/clients/codex.ts:181-200` |
| `allow_env_keys` DB column | `packages/core/src/types/index.ts:60` |
| Global bypass config | `packages/core/src/config/config-types.ts:92` (`allow_target_repo_keys`) |
| Repo-level bypass | `packages/core/src/config/config-types.ts:179` |
| Config loader merge | `packages/core/src/config/config-loader.ts:403` |
| Sandbox schema | `packages/workflows/src/schemas/dag-node.ts:71` (`sandboxSettingsSchema`) |
| CLI `--allow-env-keys` flag | Global options in `archon --help` |
| Env-leak introduction | CHANGELOG `## [0.3.0]` ("Env-leak gate hardening") |
| Config fix for binaries | CHANGELOG `## [0.3.2]` ("env-leak gate false-positive for unregistered cwd") |
