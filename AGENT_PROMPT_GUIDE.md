# Agent Authoring Guide

This guide explains how to write agents that Claude Code will automatically delegate to, with the full frontmatter schema supported by the current Claude Code subagent system.

## Frontmatter schema

Every marketplace agent is a Markdown file with YAML frontmatter. Only `name` and `description` are required by Claude Code; the rest shape delegation, security, and runtime behavior.

### Fields supported for plugin agents

These work everywhere in this marketplace (all agents live under `plugins/*/agents/` except `plugin-architect`):

| Field | Type | Purpose |
|---|---|---|
| `name` | string | Kebab-case identifier. Must match the filename (minus `.md`). **Required.** |
| `description` | string | When Claude should delegate to this agent. Must follow the "Use PROACTIVELY when…" pattern below. **Required.** |
| `tools` | csv or array | Allowlist of tools the agent may use. Omit to inherit all tools. **Strongly recommended.** |
| `disallowedTools` | csv or array | Denylist applied before `tools` is resolved. Use when you want "everything except X". |
| `model` | `sonnet` \| `opus` \| `haiku` \| full model ID \| `inherit` | Defaults to `inherit`. Use `opus` only when reasoning depth genuinely matters. |
| `skills` | list | Skill names to preload into the agent's context at startup. Subagents **do not inherit** skills from the parent conversation — list them explicitly. |
| `maxTurns` | integer | Hard ceiling on agentic turns. Rarely needed. |
| `effort` | `low` \| `medium` \| `high` \| `xhigh` \| `max` | Overrides session effort. Rarely needed. |
| `isolation` | `worktree` | Runs the agent in a temporary git worktree. Useful for agents that speculatively modify many files. |
| `color` | `red` \| `blue` \| `green` \| `yellow` \| `purple` \| `orange` \| `pink` \| `cyan` | UI color. Keep consistent within a plugin. |
| `memory` | `user` \| `project` \| `local` | Enables a persistent memory directory. Use only for agents that genuinely benefit from cross-session learning (reviewers, auditors). |
| `background` | boolean | Always run as a background task. Usually leave unset. |
| `initialPrompt` | string | Auto-submitted first user turn when the agent runs as the main session (`claude --agent <name>`). |

### Fields that DO NOT work in plugin agents

Claude Code silently ignores these on any agent loaded from a plugin (security restriction):

- `hooks`
- `mcpServers`
- `permissionMode`

If you need them, the agent must live in `.claude/agents/` or `~/.claude/agents/`, not under `plugins/`. The only marketplace agent that qualifies today is `.claude/agents/plugin-architect.md`.

### Custom marketplace fields

- `category` — internal taxonomy only. Claude Code ignores unknown fields, so this is purely for our own organization (and for the README grouping). Not required, not enforced.

## The description field

This is the most important field. Claude Code reads it on every user prompt to decide whether to delegate.

### The pattern

```
description: <What the agent does>. <Expertise areas>. Use PROACTIVELY when <scenario 1>, <scenario 2>, or <scenario 3>.
```

### Required components

1. **The PROACTIVELY keyword** — signals automatic delegation. Acceptable variants: `Use PROACTIVELY when…`, `Use proactively for…`, `Must be used when…`.
2. **A specific WHEN clause** — name concrete scenarios, not vague categories.
3. **Optional phrase triggers** — `If they say "optimize", "N+1", or "slow query", use this agent.`

### Good vs. bad WHEN clauses

**Good** — specific and actionable:
- `when designing Laravel applications, planning architecture, or discussing system design patterns`
- `when optimizing Eloquent queries, fixing N+1 problems, or implementing eager loading`
- `when writing Pest tests, implementing TDD, or creating feature/unit tests`

**Bad** — vague:
- `when needed`
- `for Laravel development`
- `when appropriate`

### Real examples

**Laravel Architect**
```
description: Expert Laravel architect specializing in scalable application design, modular architecture (nwidart/laravel-modules), SOLID principles, and modern PHP patterns. Masters service containers, dependency injection, repository patterns, event-driven architecture, and performance optimization. Use PROACTIVELY when designing Laravel applications, planning architecture, or discussing system design patterns.
```

**Security Engineer**
```
description: Identify security vulnerabilities and ensure compliance with Laravel security standards and best practices. Masters authentication, authorization, CSRF/XSS prevention, SQL injection protection, and rate limiting. Use PROACTIVELY when implementing security features, reviewing code for vulnerabilities, or auditing applications.
```

## The `tools` field: three archetypes

Every agent in this marketplace should declare `tools:`. Leaving it off gives the agent every tool including Write/Edit/Bash, which defeats the point of a specialist. Pick one of three archetypes:

### 1. Read-only analyzer

For reviewers, auditors, planners, and architects that *survey* code without modifying it.

```yaml
tools: Read, Grep, Glob, Bash
```

Examples in this marketplace: `code-reviewer`, `planner`, `scout`, any `security-engineer`, `*-performance` / `performance-expert`, architects whose job is review rather than implementation.

### 2. Implementer

For specialists that write and edit code as their primary job.

```yaml
tools: Read, Edit, Write, Grep, Glob, Bash
```

Examples: `laravel-architect`, `eloquent-expert`, `testing-expert`, `flutter-ui-specialist`, most `*-specialist` agents.

### 3. Full-capability (rare)

For orchestrators that need to spawn other agents or use MCP tools. Omit `tools:` entirely, or use `disallowedTools:` to subtract a few things:

```yaml
disallowedTools: Write, Edit
```

Only use this archetype when there's a concrete reason. Default to archetype 1 or 2.

### When in doubt

Ask: "Does this agent's job description involve producing working code changes?" If yes, archetype 2. If no, archetype 1.

## The `skills` field: preload domain knowledge

Subagents don't inherit skills from the parent conversation. If your plugin ships a skill that's directly relevant to the agent's job, wire it up:

```yaml
skills:
  - laravel-testing-patterns
  - action-driven-design
```

The full skill content is injected into the agent's context at startup. The agent doesn't have to discover or invoke it — it's already loaded.

**Pair agents with skills by name**, e.g.:
- `testing-expert` → `laravel-testing-patterns`
- `laravel-architect` → `laravel-blueprint`, `action-driven-design`
- `filament-specialist` → `filament-blueprint`, `filament-resource-patterns`
- `eloquent-expert` → `eloquent-relationships`

Don't preload every skill in the plugin — only the ones the agent genuinely always needs. Context cost is real.

## The `model` field

- **`sonnet`** (default for most agents) — balances capability and speed.
- **`opus`** — reserve for agents that must reason across architecture, tradeoffs, or ambiguous requirements. Examples: `plugin-architect`, planners for multi-file changes.
- **`haiku`** — fast and cheap, good for narrow lookup/classification agents.
- **`inherit`** (the silent default if you omit `model`) — matches the parent conversation.

## Template

```markdown
---
name: your-agent-name
description: Brief expertise statement. Masters key skills/areas. Use PROACTIVELY when scenario 1, scenario 2, or scenario 3. If they say "keyword1", "keyword2", use this agent.
tools: Read, Edit, Write, Grep, Glob, Bash
model: sonnet
color: blue
skills:
  - relevant-skill-1
category: engineering
---

# Agent Name

## Triggers
- When to invoke (5–7 items)

## Behavioral Mindset
2–3 sentences on philosophy and approach.

## Critical Knowledge
- Version-specific gotchas the agent MUST know.

## Focus Areas
- 8–12 bullet points of competencies.

## Key Actions
- 6–8 primary responsibilities.

## Outputs
- What the agent produces.

## Boundaries
**Will**: capability 1 | capability 2 | capability 3
**Will Not**: constraint 1 | constraint 2 | constraint 3
```

## The information flow

```
User → Claude Code (primary agent) → Your sub-agent → Primary agent → User
```

Sub-agents respond to the primary agent, not the user. The description is what the primary agent reads to decide: (1) whether to call you, (2) how to prompt you, (3) what to expect back.

## Testing a new agent

1. **Explicit invocation** — `Use the <name> agent to review this code`
2. **Proactive triggering** — describe a problem that matches your WHEN clauses and confirm Claude routes to the agent without being told.
3. **Tool constraints** — if you set `tools: Read, Grep, Glob, Bash`, ask the agent to write a file. It should refuse or fail — that's the allowlist working.

## Common trigger vocabulary

**Architecture/Design**: designing applications, planning architecture, discussing system design, evaluating architectural decisions
**Security**: implementing security features, reviewing for vulnerabilities, auditing applications, threat modeling
**Performance**: optimizing performance, fixing slow queries, improving response times, identifying bottlenecks
**Testing**: writing tests, implementing TDD, creating test suites, testing strategies
**Database**: designing schemas, optimizing queries, fixing N+1, implementing relationships

## Summary

```
Correct frontmatter schema
+ Specific WHEN clauses in description
+ Tools allowlist matching the agent's job
+ Skills preloaded where applicable
= An agent Claude Code delegates to reliably, safely, and with the right context.
```

---

**References**
- Claude Code subagents: https://docs.claude.com/en/docs/claude-code/sub-agents
- Plugin subagent restrictions: same page, "Choose the subagent scope" section
