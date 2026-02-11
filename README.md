# Multi-Framework Development Marketplace

Professional development toolkit with **10 specialized plugins** featuring **37 AI agents**, **64+ slash commands**, and a **self-correcting workflow system** for Laravel, Livewire, Filament, Vue/Nuxt, Magento 2, WordPress, Electron, Flutter, Git worktree management, and Pro-Workflow.

## Available Plugins

Install only what you need — each plugin is completely isolated with its own agents and commands:

### Backend PHP
- **laravel-development** - 9 agents, 21 commands (Laravel 12, Eloquent, testing, security)
- **livewire-development** - 1 agent, 4 commands (Livewire 4 reactive components)
- **filament-development** - 1 agent, 11 commands (Filament 5 admin panels)
- **magento2-development** - 4 agents, 8 commands (Magento 2 / Adobe Commerce)
- **wordpress-development** - 6 agents, 11 commands (WordPress 6.0+, themes, plugins, Gutenberg, WooCommerce)

### Frontend
- **vue-nuxt-development** - 8 agents, 12 commands (Vue 3 + Nuxt 4 + TypeScript)

### Desktop & Mobile
- **electron-development** - 2 agents, 2 commands (Electron + React/TypeScript)
- **flutter-development** - 2 agents, 2 commands (Flutter 3.38+ with Riverpod)

### DevOps & Workflow
- **git-worktree-management** - 1 agent, 5 commands (parallel development workflows)
- **pro-workflow** - 3 agents, 5 commands (self-correcting memory, quality gates, learning capture)

## Quick Install

```bash
# Add the marketplace
/plugin marketplace add https://github.com/skylence-be/claude-code-marketplace

# Install the plugins you need
/plugin install laravel-development
/plugin install livewire-development
/plugin install filament-development
/plugin install vue-nuxt-development
/plugin install magento2-development
/plugin install wordpress-development
/plugin install electron-development
/plugin install flutter-development
/plugin install git-worktree-management
/plugin install pro-workflow
```

## Pro-Workflow Plugin

Self-correcting workflow system that turns the marketplace from a reference library into a learning system. Ported from [rohitg00/claude-code-pro-workflow](https://github.com/rohitg00/claude-code-pro-workflow) with Python hooks and JSON storage.

### Agents
- **planner** - Read-only planning agent that breaks down complex tasks (opus)
- **reviewer** - Code review + security audit agent (opus)
- **scout** - Confidence-gated exploration with 0-100 scoring across 5 dimensions (opus)

### Commands
- `/pro-workflow:commit` - Smart commit with quality gates, multi-language code scan, conventional commits
- `/pro-workflow:wrap-up` - End-of-session checklist: audit changes, verify quality, capture learnings
- `/pro-workflow:handoff` - Generate session handoff document for next session continuity
- `/pro-workflow:learn` - Claude Code best practices guide + save learnings to JSON
- `/pro-workflow:learn-rule` - Capture a correction as a persistent rule

### Context Modes
- **dev** - "Code first, explain after" — working > right > clean
- **research** - "Explore broadly, don't change code yet"
- **review** - "Security > Performance > Style"

### Hook Features (opt-in via flags)
All features are behind argparse flags — backward-compatible if not enabled:

| Hook | Flag | Behavior |
|------|------|----------|
| PreToolUse | `--track-edits` | Count edits, warn at 5/10/every-10 to run quality gates |
| PostToolUse | *(always on)* | Scan edited files for debug statements, TODO/FIXME, hardcoded secrets |
| Stop | `--learn-capture` | Parse `[LEARN]` blocks from responses → append to `learnings.json` |
| Stop | `--session-check` | Periodic wrap-up reminders every 20 responses |
| UserPromptSubmit | `--detect-corrections` | Detect "wrong"/"undo"/"wait"/"actually" → track correction count |
| UserPromptSubmit | `--detect-drift` | Track original intent keywords, warn after 6+ edits if relevance < 20% |
| SessionStart | `--load-learnings` | Display recent project-scoped learnings on startup |

### Storage
- `.claude/data/learnings.json` — persistent learning rules (JSON, no SQLite)
- `.claude/data/sessions/{id}.json` — session state (edit count, corrections, response count)
- `$TMPDIR/pro-workflow/intent-{id}.json` — ephemeral drift detection state
- `.claude/data/handoffs/` — handoff documents (created by `/handoff`)

## Documentation & Guides

### Agent Prompt Guide

**[AGENT_PROMPT_GUIDE.md](./AGENT_PROMPT_GUIDE.md)** - Comprehensive guide on writing effective sub-agent descriptions that enable Claude Code to automatically delegate tasks.

Learn how to:
- Write agent descriptions that trigger automatic delegation
- Use the "PROACTIVELY" keyword correctly
- Define specific trigger scenarios
- Understand the information flow between agents
- Test your agent configurations

**Quick reference:** For Claude Code to automatically use your sub-agents, follow this pattern:
```markdown
description: [What the agent does]. Use PROACTIVELY when [specific trigger scenarios].
```

## Plugin Details

### Laravel Development Plugin

**9 specialized agents:**
- laravel-architect - Architecture, patterns, modular design
- eloquent-expert - ORM, relationships, query optimization
- testing-expert - Pest 4/PHPUnit with browser testing
- security-engineer - Authentication, authorization, security
- optimization-expert - Performance optimization
- laravel-pulse-expert - Performance monitoring
- laravel-reverb-expert - WebSocket real-time communication
- laravel-socialite-expert - OAuth authentication
- laravel-prompts-expert - CLI forms and console commands

**7 specialized skills** (11,416 lines total):
- laravel-coding-standards - Spatie guidelines, PSR compliance, modern PHP 8+ patterns (1,818 lines)
- eloquent-relationships - Relationships, eager loading, N+1 prevention (1,771 lines)
- laravel-queues-jobs - Queue architecture, batching, Horizon (1,812 lines)
- laravel-testing-patterns - Pest 4, feature/unit tests, mocking (1,390 lines)
- laravel-api-design - RESTful APIs, Sanctum, versioning (1,762 lines)
- laravel-caching-strategies - Cache drivers, tags, optimization (1,343 lines)
- laravel-security-patterns - CSRF, XSS, authentication, rate limiting (1,520 lines)

**21 commands:** Models, migrations, controllers, jobs, events, listeners, mail, middleware, notifications, observers, policies, requests, resources, rules, seeders, factories, commands, plus utilities

### Livewire Development Plugin

**1 specialized agent:**
- livewire-specialist - Livewire 4 reactive components and patterns

**3 specialized skills** (5,723 lines total):
- livewire4-reactive-patterns - #[Reactive], #[Computed], #[Locked], wire directives, lifecycle hooks (2,044 lines)
- livewire-forms-validation - Form objects, real-time validation, multi-step wizards (2,065 lines)
- livewire-performance-optimization - Query optimization, lazy loading, computed properties (1,614 lines)

**4 commands:** Components, forms, layouts, attributes

### Filament Development Plugin

**1 specialized agent:**
- filament-specialist - Filament 5 admin panels, resources, components

**4 specialized skills** (7,094 lines total):
- filament-resource-patterns - Resources, forms, tables, filters, actions, relation managers (2,048 lines)
- filament-forms-advanced - Advanced layouts, conditional fields, repeaters, wizards (1,896 lines)
- filament-tables-optimization - Query optimization, bulk actions, exports, summarizers (1,513 lines)
- filament-multi-tenancy - Panel configuration, tenant models, billing, team management (1,637 lines)

**11 commands:** Resources, pages, widgets, relation managers, panels, clusters, custom fields, custom columns, exporters, importers, themes

### Vue/Nuxt Development Plugin

**8 specialized agents:**
- vue-architect - Vue 3 architecture and patterns
- nuxt-architect - Nuxt 4 SSR and routing
- typescript-expert - Advanced TypeScript patterns
- state-management - Pinia stores and composables
- testing-specialist - Vitest and component testing
- security-engineer - Frontend security best practices
- ux-engineer - User experience and accessibility
- frontend-performance - Performance optimization

**6 specialized skills** (7,679 lines total):
- vue3-composition-api-patterns - Composition API, composables, lifecycle, script setup (1,754 lines)
- nuxt4-ssr-optimization - SSR lifecycle, data fetching, server routes, SEO (1,194 lines)
- pinia-state-patterns - Store definition, getters, actions, plugins, SSR hydration (1,232 lines)
- typescript-vue-patterns - Component types, generic components, type-safe routing (1,347 lines)
- vitest-testing-patterns - Component testing, composable testing, mocking, E2E (1,135 lines)
- nuxt-modules-integration - Essential modules, custom modules, plugins, layers (1,017 lines)

**12 commands:** Components, pages, layouts, composables, stores, plugins, middleware, API clients, plus utilities

### Magento 2 Development Plugin

**4 specialized agents:**
- magento-architect - Magento 2 architecture and patterns
- ecommerce-specialist - E-commerce features and workflows
- performance-engineer - Performance optimization
- security-engineer - Security best practices

**8 commands:** Modules, models, controllers, plugins, plus utilities

### WordPress Development Plugin

**6 specialized agents:**
- wordpress-architect - WordPress architecture, hooks, custom post types, REST API
- theme-specialist - Theme development, template hierarchy, block themes
- plugin-specialist - Plugin development, activation hooks, settings API
- gutenberg-expert - Block editor, custom blocks, FSE (Full Site Editing)
- woocommerce-specialist - WooCommerce customization, products, checkout, payments
- wordpress-security - Security hardening, sanitization, nonce verification

**11 commands:** Themes, plugins, Gutenberg blocks, custom post types, taxonomies, widgets, REST API endpoints, shortcodes, plus utilities

### Electron Development Plugin

**2 specialized agents:**
- electron-architect - Electron architecture, secure IPC, system tray, Forge builds
- react-typescript-specialist - React/TypeScript components, Radix UI, Tailwind CSS

**2 commands:** Feature modules and component scaffolding

### Flutter Development Plugin

**2 specialized agents:**
- flutter-architect - Flutter 3.38+ clean architecture, Riverpod, GoRouter
- flutter-ui-specialist - Material 3, responsive layouts, animations, accessibility

**2 commands:** Feature modules and widget scaffolding

### Git Worktree Management Plugin

**1 specialized agent:**
- git-worktree-manager - Worktree creation, environment isolation, database duplication

**5 commands:** Create, setup, cleanup, list worktrees, and database duplication

## Python Hook System

The marketplace includes a Python hook system for automated quality enforcement:

- **PreToolUse** - Block dangerous operations (rm -rf, .env access), track edits
- **PostToolUse** - Scan edited files for debug artifacts and secrets
- **UserPromptSubmit** - Log prompts, detect corrections, detect drift
- **Stop** - Copy transcripts, capture learnings, session reminders
- **SessionStart** - Load context, display learnings
- **PreCompact** - Pre-context compaction handling
- **SubagentStop** - Sub-agent completion notifications

All hooks use `uv run` with inline dependencies — zero installation required.

## Integrated Packages

### Laravel Ecosystem
- **Laravel Octane** - In-memory application server awareness
- **Laravel Pennant** - Feature flags for gradual rollouts
- **Laravel Precognition** - Live validation without duplicating rules
- **Laravel Pulse** - Performance monitoring and insights
- **Laravel Reverb** - Real-time WebSocket communication
- **Laravel Socialite** - OAuth authentication
- **Laravel Prompts** - Beautiful CLI forms

### Development Tools
- **nwidart/laravel-modules** - Modular architecture for medium-large projects
- **skylence/laravel-optimize-mcp** - AI-assisted optimization with MCP tools

### Testing & Quality
- **Pest 4** - Modern testing framework
- **PHPStan/Larastan** - Static analysis for type safety
- **Laravel Pint** - Code style fixer
- **Laravel Dusk** - Browser testing

## Technology Stack

- **Laravel 12** - Latest framework version
- **Livewire 4** - Reactive components with #[Reactive], #[Computed], #[Locked]
- **Filament 5** - Admin panel framework
- **PHP 8.2+** - Modern PHP features
- **Pest 4** - Testing with type and code coverage
- **Vue 3 + Nuxt 4** - Frontend framework with TypeScript
- **Flutter 3.38+** - Cross-platform mobile/desktop
- **Electron** - Desktop applications
- **Tailwind CSS** - Utility-first styling
- **Alpine.js** - Lightweight JavaScript

## Usage Examples

### Laravel Full-Stack Development

```bash
# Create complete backend feature
/laravel:model-new Post
/laravel:migration-new create_posts_table
/laravel:controller-new PostController
/laravel:factory-new PostFactory

# Add reactive frontend
/livewire:component-new PostList
/livewire:form-new PostForm

# Build admin panel
/filament:resource-new PostResource
/filament:widget-new PostStatsWidget
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

### Vue/Nuxt Frontend Development

```bash
# Create Vue 3 + Nuxt 4 application
/frontend:page-new blog/index
/frontend:component-new BlogCard
/frontend:composable-new useBlogPosts
/frontend:store-new blog
/frontend:api-client-new BlogApi
```

### Git Worktree Parallel Development

```bash
# Create isolated worktree for a feature
/git-worktree:worktree-create feature/auth
/git-worktree:db-duplicate feature_auth

# List and manage worktrees
/git-worktree:worktree-list
/git-worktree:worktree-cleanup feature/auth
```

### Magento 2 E-Commerce

```bash
# Create custom module
/magento:module-new Vendor_CustomCheckout
/magento:model-new CustomOrder
/magento:controller-new Checkout/Success
/magento:plugin-new OrderProcessor
```

### WordPress Development

```bash
# Create custom theme and plugin
/wordpress:theme-new PortfolioTheme
/wordpress:plugin-new CustomFunctionality

# Build custom Gutenberg blocks
/wordpress:block-new TestimonialBlock
/wordpress:post-type-new Portfolio
/wordpress:taxonomy-new PortfolioCategory
```

## Repository Structure

```
claude-code-marketplace/
├── .claude/
│   ├── hooks/                       # 7 Python hook scripts
│   ├── output-styles/               # 8 output formatting styles
│   ├── status_lines/                # Custom status line generators
│   └── settings.json                # Hook configuration + permissions
├── .claude-plugin/
│   ├── plugin.json                  # 64+ commands, 37 agents
│   └── marketplace.json             # 10 plugins definition
├── plugins/
│   ├── laravel-development/
│   │   ├── agents/                  # 9 Laravel experts
│   │   ├── commands/                # 21 Laravel commands
│   │   └── skills/                  # 7 Laravel skills (11,416 lines)
│   ├── livewire-development/
│   │   ├── agents/                  # Livewire specialist
│   │   ├── commands/                # 4 Livewire commands
│   │   └── skills/                  # 3 Livewire skills (5,723 lines)
│   ├── filament-development/
│   │   ├── agents/                  # Filament specialist
│   │   ├── commands/                # 11 Filament commands
│   │   └── skills/                  # 4 Filament skills (7,094 lines)
│   ├── vue-nuxt-development/
│   │   ├── agents/                  # 8 frontend experts
│   │   ├── commands/                # 12 frontend commands
│   │   └── skills/                  # 6 Vue/Nuxt skills (7,679 lines)
│   ├── magento2-development/
│   │   ├── agents/                  # 4 Magento experts
│   │   └── commands/                # 8 Magento commands
│   ├── wordpress-development/
│   │   ├── agents/                  # 6 WordPress experts
│   │   └── commands/                # 11 WordPress commands
│   ├── electron-development/
│   │   ├── agents/                  # 2 Electron experts
│   │   └── commands/                # 2 Electron commands
│   ├── flutter-development/
│   │   ├── agents/                  # 2 Flutter experts
│   │   └── commands/                # 2 Flutter commands
│   ├── git-worktree-management/
│   │   ├── agents/                  # Git worktree manager
│   │   ├── commands/                # 5 worktree commands
│   │   └── skills/                  # Worktree patterns
│   └── pro-workflow/
│       ├── agents/                  # 3 workflow agents (planner, reviewer, scout)
│       ├── commands/                # 5 workflow commands
│       ├── contexts/                # 3 context modes (dev, research, review)
│       └── rules/                   # Core quality rules
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
- **Star the repo**: Help others discover this toolkit!

---

**Built for developers who want AI-assisted development with best practices across Laravel, Livewire, Filament, Vue/Nuxt, Magento 2, WordPress, Electron, Flutter, and more.**
