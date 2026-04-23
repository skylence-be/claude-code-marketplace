# Multi-Framework Development Marketplace

Professional development toolkit with **15 specialized plugins** featuring **52 AI agents**, **93+ slash commands**, a **self-reflection scoring code review pipeline**, **post-compaction context recovery**, and a **self-correcting workflow system** for Laravel, Livewire, Filament, Vue/Nuxt, Angular, Go, Magento 2, WordPress, Electron, Flutter, NativePHP, Git worktree management, Code Review, Archon Workflows, and Pro-Workflow.

## Available Plugins

Install only what you need — each plugin is completely isolated with its own agents and commands:

### Backend PHP
- **laravel-development** - 9 agents, 18 commands, 13 skills (Laravel 12, Eloquent, testing, security, Tailwind, Pennant, Folio, Wayfinder, PHP 8.4/8.5)
- **livewire-development** - 2 agents, 5 commands, 7 skills (Livewire 4, Blaze optimization, Volt single-file components)
- **filament-development** - 1 agent, 11 commands, 5 skills (Filament 5 admin panels, Blueprint planning)
- **magento2-development** - 4 agents, 8 commands (Magento 2 / Adobe Commerce)
- **wordpress-development** - 6 agents, 11 commands (WordPress 6.0+, themes, plugins, Gutenberg, WooCommerce)

### Frontend
- **vue-nuxt-development** - 8 agents, 12 commands, 7 skills (Vue 3 + Nuxt 4 + TypeScript + Inertia.js v2)
- **angular-development** - 8 agents, 12 commands, 8 skills (Angular 21+, signals, zoneless, SSR)

### Desktop & Mobile
- **electron-development** - 2 agents, 2 commands (Electron + React/TypeScript)
- **flutter-development** - 2 agents, 2 commands (Flutter 3.38+ with Riverpod)
- **nativephp-development** - 3 agents, 4 commands, 3 skills (NativePHP desktop & mobile with Laravel)

### Backend Go
- **golang-development** - 2 agents, 3 commands, 7 skills (idiomatic Go, error handling, concurrency, testing, project structure, interface design, performance)

### Code Quality
- **code-review** - 1 agent, 2 commands, 4 skills, 13 technology contexts (self-reflection scoring, team review, includes Go rules)

### DevOps & Workflow
- **git-worktree-management** - 1 agent, 5 commands (parallel development workflows)
- **pro-workflow** - 2 agents, 5 commands (learning capture, quality gates, post-compaction recovery)

## Quick Install

```bash
# Add the marketplace
/plugin marketplace add https://github.com/skylence-be/claude-code-marketplace

# Install the plugins you need
/plugin install laravel-development
/plugin install livewire-development
/plugin install filament-development
/plugin install vue-nuxt-development
/plugin install angular-development
/plugin install magento2-development
/plugin install wordpress-development
/plugin install electron-development
/plugin install flutter-development
/plugin install nativephp-development
/plugin install golang-development
/plugin install git-worktree-management
/plugin install code-review
/plugin install pro-workflow
```

## Code Review Plugin

Advanced code review with a two-pass self-reflection scoring pipeline inspired by [PR-Agent](https://github.com/qodo-ai/pr-agent) and [Kodus AI](https://github.com/kodustech/kodus-ai):

1. **Generate** — Find all potential issues (universal + technology-specific rules)
2. **Score** — Re-evaluate each finding with confidence 1-10
3. **Filter** — Remove noise below mode threshold
4. **Report** — Severity-grouped output with fix suggestions

### Commands
- `/code-review:code-review` — Single-agent review with `--mode` (quick/thorough/security/pr) and `--threshold`
- `/code-review:team-review` — Spawn parallel reviewers (security, performance, correctness) using agent teams

### Technology Contexts (12)
Auto-detected and loaded based on project files — Laravel, Livewire, Filament, Vue/Nuxt, Angular, Magento 2, WordPress, Electron, Flutter, NativePHP, TypeScript, PHP.

### Confidence Scoring

| Score | Meaning | Adjustments |
|-------|---------|-------------|
| 9-10 | Certain bug or vulnerability | +2 for known anti-pattern |
| 7-8 | Very likely a real issue | +1 for untrusted input |
| 5-6 | Probably an issue | -1 for explanatory comment |
| 3-4 | Might be intentional | -1 for test/fixture code |
| 1-2 | Likely intentional or stylistic | -2 for codebase convention |

### Mode Thresholds

| Mode | Threshold | Use Case |
|------|-----------|----------|
| Quick scan | >= 7 | Small changes, fast feedback |
| Thorough | >= 4 | Large changes, quality gate |
| Security | >= 3 (security) / >= 7 (other) | Security audits |
| PR review | >= 5 | Pull request with verdict |

## Pro-Workflow Plugin

Self-correcting workflow system with persistent learning capture. Ported from [rohitg00/claude-code-pro-workflow](https://github.com/rohitg00/claude-code-pro-workflow).

### Agents
- **planner** — Read-only planning agent for multi-file changes and architecture decisions
- **scout** — Confidence-gated exploration with 0-100 scoring across 5 dimensions

### Commands
- `/pro-workflow:commit` — Smart commit with quality gates and conventional commits
- `/pro-workflow:wrap-up` — End-of-session checklist: audit changes, verify quality, capture learnings
- `/pro-workflow:handoff` — Generate session handoff document for next session continuity
- `/pro-workflow:learn` — Best practices guide + save learnings to JSON
- `/pro-workflow:learn-rule` — Capture a correction as a persistent rule

### Context Modes
- **dev** — "Code first, explain after" — working > right > clean
- **research** — "Explore broadly, don't change code yet"

## Python Hook System

Automated quality enforcement with post-compaction context recovery:

| Hook | Flag | Behavior |
|------|------|----------|
| PreToolUse | `--track-edits` | Count edits, warn at 5/10/every-10 to run quality gates |
| PostToolUse | *(always on)* | Scan edited files for debug statements, TODO/FIXME, hardcoded secrets |
| Stop | `--learn-capture` | Parse `[LEARN]` blocks from responses → append to `learnings.json` |
| Stop | `--session-check` | Periodic wrap-up reminders every 20 responses |
| UserPromptSubmit | `--detect-corrections` | Detect "wrong"/"undo"/"wait" → track correction count |
| UserPromptSubmit | `--detect-drift` | Track original intent, warn after 6+ edits if relevance < 20% |
| SessionStart | `--load-learnings` | Display recent project-scoped learnings on startup |
| SessionStart | `--recover-compact` | Re-inject context after compaction (branch, files, stack, prompts, learnings) |
| PreCompact | `--save-context` | Save context snapshot before compaction for post-compaction recovery |
| SubagentStop | `--notify` | TTS notification when subagent completes |

### Post-Compaction Context Recovery

Addresses the "post-compaction rule amnesia" problem ([7+ GitHub issues](https://github.com/anthropics/claude-code/issues/3537)). Before compaction, `PreCompact` saves a snapshot of:
- Git branch and recent commits
- Modified files list
- Detected technology stack
- Session progress (edit count, responses, agent name)
- Last 3 user prompts (task continuity)
- Top 10 project learnings

After compaction, `SessionStart` detects `source="compact"` and re-injects the snapshot. The snapshot is consumed once (deleted after use) to avoid stale data.

## Laravel Ecosystem Skills

Skills inspired by [Laravel Boost](https://github.com/laravel/boost) analysis, covering gaps Boost doesn't fill:

| Skill | Plugin | What It Covers |
|-------|--------|----------------|
| tailwind-migration | laravel | Tailwind v3→v4: `@import` syntax, `@theme`, deprecated utilities |
| pennant-feature-flags | laravel | Feature flags: define, check, activate, Blade `@feature` |
| folio-routing | laravel | File-based routing: pages, model binding, named routes |
| wayfinder-routes | laravel | TypeScript route generation for Inertia/Vue/React |
| php-modern-features | laravel | PHP 8.4/8.5: `array_find`, pipe operator, `clone()` |
| pest-browser-testing | laravel | Pest 4: `visit/click/fill`, smoke testing, visual regression |
| volt-components | livewire | Volt single-file components: functional + class-based |
| inertia-patterns | vue-nuxt | Inertia v2: deferred props, WhenVisible, usePoll, prefetching |
| /upgrade command | laravel | Systematic framework upgrade with codebase scanning |

## Plugin Details

### Laravel Development Plugin

**9 specialized agents:**
- laravel-architect — Architecture, patterns, modular design
- eloquent-expert — ORM, relationships, query optimization (defers to Boost for core patterns)
- testing-expert — Pest 4/PHPUnit with browser testing (defers to Boost for specific patterns)
- security-engineer — Threat modeling, audit methodology (defers to Boost for OWASP checklist)
- optimization-expert — Performance, infrastructure, capacity planning
- laravel-pulse-expert — Performance monitoring and observability
- laravel-reverb-expert — WebSocket real-time communication
- laravel-socialite-expert — OAuth authentication
- laravel-prompts-expert — CLI forms and console commands

**13 skills:** coding-standards, eloquent-relationships, queues-jobs, testing-patterns (with browser testing), api-design, caching-strategies, security-patterns, blueprint, tailwind-migration, pennant-feature-flags, folio-routing, wayfinder-routes, php-modern-features

**18 commands:** Models, migrations, controllers, jobs, events, listeners, mail, middleware, notifications, observers, policies, requests, resources, rules, seeders, factories, commands, upgrade

### Livewire Development Plugin

**2 specialized agents:**
- livewire-specialist — Livewire 4 reactive components, islands architecture, SFC/MFC
- blaze-specialist — Blade component optimization (91-97% overhead reduction)

**7 skills:** livewire4-reactive-patterns, livewire-forms-validation, livewire-performance-optimization, blaze-optimization, livewire-blueprint, volt-components

**5 commands:** Components, forms, layouts, attributes, blaze-enable

### Filament Development Plugin

**1 specialized agent:**
- filament-specialist — Filament 5 admin panels, Blueprint planning, multi-panel apps

**5 skills:** filament-resource-patterns, filament-forms-advanced, filament-tables-optimization, filament-multi-tenancy, filament-blueprint

**11 commands:** Resources, pages, widgets, relation managers, panels, clusters, custom fields, custom columns, exporters, importers, themes

### Vue/Nuxt Development Plugin

**8 specialized agents:**
- vue-architect, nuxt-architect, typescript-expert, state-management, testing-specialist, security-engineer, ux-engineer, frontend-performance

**7 skills:** vue3-composition-api-patterns, nuxt4-ssr-optimization, pinia-state-patterns, typescript-vue-patterns, vitest-testing-patterns, nuxt-modules-integration, inertia-patterns

**12 commands:** Components, pages, layouts, composables, stores, plugins, middleware, API clients, plus utilities

### Code Review Plugin

**1 specialized agent:**
- code-reviewer — Two-pass self-reflection scoring with technology-aware rule loading

**2 commands:**
- `/code-review:code-review` — Single-agent review (quick/thorough/security/PR modes)
- `/code-review:team-review` — Parallel review team (security + performance + correctness reviewers)

**4 skills:** self-reflection-scoring, review-modes, git-diff-analysis, finding-taxonomy

**12 technology contexts:** Laravel, Livewire, Filament, Vue/Nuxt, Angular, Magento 2, WordPress, Electron, Flutter, NativePHP, TypeScript, PHP

### Other Plugins

- **angular-development** — 8 agents, 12 commands, 8 skills (Angular 21+, signals, zoneless, SSR)
- **magento2-development** — 4 agents, 8 commands (Magento 2 / Adobe Commerce)
- **wordpress-development** — 6 agents, 11 commands (WordPress 6.0+, WooCommerce, Gutenberg)
- **electron-development** — 2 agents, 2 commands (Electron + React/TypeScript)
- **flutter-development** — 2 agents, 2 commands (Flutter 3.38+ with Riverpod)
- **nativephp-development** — 3 agents, 4 commands, 3 skills (NativePHP desktop & mobile)
- **git-worktree-management** — 1 agent, 5 commands (parallel development workflows)

## Usage Examples

### Code Review

```bash
# Review staged changes
/code-review:code-review

# Review a PR with thorough mode
/code-review:code-review --pr 42 --mode thorough

# Spawn parallel review team for a PR
/code-review:team-review --pr 42

# Security-focused team review
/code-review:team-review --pr 42 --reviewers security,security,correctness
```

### Laravel Full-Stack Development

```bash
# Create complete backend feature
/laravel-development:model-new Post
/laravel-development:migration-new create_posts_table
/laravel-development:controller-new PostController

# Upgrade framework
/laravel-development:upgrade --laravel 13

# Add reactive frontend
/livewire-development:component-new PostList
/livewire-development:form-new PostForm

# Build admin panel
/filament-development:resource-new PostResource
```

### Pro-Workflow Session

```bash
# Smart commit with quality gates
/pro-workflow:commit

# End of session
/pro-workflow:wrap-up
/pro-workflow:handoff

# Capture a lesson
/pro-workflow:learn-rule
```

### Vue/Nuxt + Inertia

```bash
/vue-nuxt-development:\frontend:page-new blog/index
/vue-nuxt-development:\frontend:component-new BlogCard
/vue-nuxt-development:\frontend:composable-new useBlogPosts
/vue-nuxt-development:\frontend:store-new blog
```

## Repository Structure

```
claude-code-marketplace/
├── .claude/
│   ├── agents/                      # plugin-architect agent
│   ├── hooks/                       # 7 Python hook scripts + utils
│   ├── output-styles/               # 8 output formatting styles
│   ├── status_lines/                # Custom status line generators
│   └── settings.json                # Hook configuration + permissions
├── .claude-plugin/
│   └── marketplace.json             # 13 plugins definition
├── plugins/
│   ├── laravel-development/         # 9 agents, 18 commands, 13 skills
│   ├── livewire-development/        # 2 agents, 5 commands, 7 skills
│   ├── filament-development/        # 1 agent, 11 commands, 5 skills
│   ├── vue-nuxt-development/        # 8 agents, 12 commands, 7 skills
│   ├── angular-development/         # 8 agents, 12 commands, 8 skills
│   ├── magento2-development/        # 4 agents, 8 commands
│   ├── wordpress-development/       # 6 agents, 11 commands
│   ├── electron-development/        # 2 agents, 2 commands
│   ├── flutter-development/         # 2 agents, 2 commands
│   ├── nativephp-development/       # 3 agents, 4 commands, 3 skills
│   ├── code-review/                 # 1 agent, 2 commands, 4 skills, 12 contexts
│   ├── git-worktree-management/     # 1 agent, 5 commands
│   └── pro-workflow/                # 2 agents, 5 commands, 2 contexts
└── README.md
```

## Contributing

Contributions welcome! This is an open toolkit for the development community.

1. Fork the repository
2. Create your feature branch
3. Add agents or commands to the appropriate plugin
4. Update plugin descriptions in marketplace.json
5. Submit a Pull Request

## License

MIT License - See LICENSE file for details

## Author

**Skylence** - [GitHub Profile](https://github.com/skylence-be)

## Support

- **GitHub Issues**: [Report bugs and request features](https://github.com/skylence-be/claude-code-marketplace/issues)
- **Documentation**: See individual agent files in `plugins/*/agents/`
- **Examples**: Check command files in `plugins/*/commands/`

---

**Built for developers who want AI-assisted development with best practices across Laravel, Livewire, Filament, Vue/Nuxt, Angular, Magento 2, WordPress, Electron, Flutter, NativePHP, and more.**
