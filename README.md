# Multi-Framework Development Marketplace

Professional development toolkit with **5 specialized plugins** featuring **24 AI agents** and **56 slash commands** for Laravel, Livewire, Filament, Vue/Nuxt, and Magento 2.

## 📦 Available Plugins

Install only what you need - each plugin is completely isolated with its own agents and commands:

### Backend PHP
- 🚀 **laravel-development** - 9 agents, 21 commands (Laravel 12, Eloquent, testing, security)
- ⚡ **livewire-development** - 1 agent, 4 commands (Livewire 4 reactive components)
- 🎨 **filament-development** - 1 agent, 11 commands (Filament 4 admin panels)
- 🛒 **magento2-development** - 4 agents, 8 commands (Magento 2 / Adobe Commerce)

### Frontend
- 🌐 **vue-nuxt-development** - 8 agents, 12 commands (Vue 3 + Nuxt 4 + TypeScript)

## Quick Install

```bash
# Add the marketplace
/plugin marketplace add skylence-be/multi-framework-dev-marketplace

# Install the plugins you need
/plugin install laravel-development
/plugin install livewire-development
/plugin install filament-development
/plugin install vue-nuxt-development
/plugin install magento2-development
```

## Plugin Details

### 🚀 Laravel Development Plugin

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

**21 commands:** Models, migrations, controllers, jobs, events, listeners, mail, middleware, notifications, observers, policies, requests, resources, rules, seeders, factories, commands, plus utilities

### ⚡ Livewire Development Plugin

**1 specialized agent:**
- livewire-specialist - Livewire 4 reactive components and patterns

**4 commands:** Components, forms, layouts, attributes

### 🎨 Filament Development Plugin

**1 specialized agent:**
- filament-specialist - Filament 4 admin panels, resources, components

**11 commands:** Resources, pages, widgets, relation managers, panels, clusters, custom fields, custom columns, exporters, importers, themes

### 🌐 Vue/Nuxt Development Plugin

**8 specialized agents:**
- vue-architect - Vue 3 architecture and patterns
- nuxt-architect - Nuxt 4 SSR and routing
- typescript-expert - Advanced TypeScript patterns
- state-management - Pinia stores and composables
- testing-specialist - Vitest and component testing
- security-engineer - Frontend security best practices
- ux-engineer - User experience and accessibility
- frontend-performance - Performance optimization

**12 commands:** Components, pages, layouts, composables, stores, plugins, middleware, API clients, plus utilities

### 🛒 Magento 2 Development Plugin

**4 specialized agents:**
- magento-architect - Magento 2 architecture and patterns
- ecommerce-specialist - E-commerce features and workflows
- performance-engineer - Performance optimization
- security-engineer - Security best practices

**8 commands:** Modules, models, controllers, plugins, plus utilities

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
- **Filament 4** - Admin panel framework
- **PHP 8.2+** - Modern PHP features
- **Pest 4** - Testing with type and code coverage
- **Tailwind CSS** - Utility-first styling
- **Alpine.js** - Lightweight JavaScript

## Key Features

### Modular Architecture
For medium-large projects (10+ features, multiple teams):
- Organize code into independent modules
- Module-specific tests, migrations, and routes
- Team scalability with clear boundaries
- Easy module enable/disable

### AI-Assisted Optimization
Using `skylence/laravel-optimize-mcp`:
- Configuration analysis (cache, session, queue drivers)
- Database size monitoring with growth prediction
- Email alerts at 80%/90% disk usage thresholds
- Log file analysis
- Nginx configuration optimization
- Package recommendations

### Testing Excellence
- Pest 4 with modern syntax
- Browser testing with Laravel Dusk
- Type coverage tracking
- Code coverage (90% minimum target)
- Module test detection in phpunit.xml
- Parallel test execution

### Security & Performance
- Security best practices built into all agents
- Laravel Octane awareness for in-memory apps
- Performance optimization recommendations
- Real-time monitoring with Pulse + Optimize MCP

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

### Vue/Nuxt Frontend Development

```bash
# Create Vue 3 + Nuxt 4 application
/frontend:page-new blog/index
/frontend:component-new BlogCard
/frontend:composable-new useBlogPosts
/frontend:store-new blog
/frontend:api-client-new BlogApi
```

### Magento 2 E-Commerce

```bash
# Create custom module
/magento:module-new Vendor_CustomCheckout
/magento:model-new CustomOrder
/magento:controller-new Checkout/Success
/magento:plugin-new OrderProcessor
```

## Architecture Benefits

### Granular Installation
- Install only the plugins you need
- Minimal token usage - each plugin loads only its specific agents and commands
- No unnecessary resources in context

### Composable Workflows
- Mix and match plugins for your stack
- Laravel + Livewire + Filament for full-stack PHP
- Laravel backend + Vue/Nuxt frontend for modern SPA
- Magento 2 for e-commerce projects

### Best Practices Built-In
- Framework-specific conventions and patterns
- SOLID principles and clean architecture
- Security-first approach
- Type safety and static analysis
- Test-driven development
- Performance optimization

## Repository Structure

```
multi-framework-dev-marketplace/
├── .claude-plugin/
│   └── marketplace.json          # 5 plugins definition
├── plugins/
│   ├── laravel-development/
│   │   ├── agents/               # 9 Laravel experts
│   │   └── commands/             # 21 Laravel commands
│   ├── livewire-development/
│   │   ├── agents/               # Livewire specialist
│   │   └── commands/             # 4 Livewire commands
│   ├── filament-development/
│   │   ├── agents/               # Filament specialist
│   │   └── commands/             # 11 Filament commands
│   ├── vue-nuxt-development/
│   │   ├── agents/               # 8 frontend experts
│   │   └── commands/             # 12 frontend commands
│   └── magento2-development/
│       ├── agents/               # 4 Magento experts
│       └── commands/             # 8 Magento commands
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

- **GitHub Issues**: [Report bugs and request features](https://github.com/skylence-be/multi-framework-dev-marketplace/issues)
- **Documentation**: See individual agent files in `plugins/*/agents/`
- **Examples**: Check command files in `plugins/*/commands/`
- **Star the repo**: Help others discover this toolkit!

---

**Built for developers who want AI-assisted development with best practices across Laravel, Livewire, Filament, Vue/Nuxt, and Magento 2.**
