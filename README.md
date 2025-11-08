# Laravel + Livewire 4 + Filament 4 Development Kit

Complete development toolkit for Laravel 12, Livewire 4, and Filament 4 with **35 slash commands** and **11 specialized AI agents**.

## Features

- 🚀 **Laravel 12** - Latest Laravel framework support
- ⚡ **Livewire 4** - Reactive components with new attributes system
- 🎨 **Filament 4** - Admin panel builder integration
- 🧩 **Modular Architecture** - nwidart/laravel-modules support for large projects
- 📊 **Optimization Tools** - skylence/laravel-optimize-mcp integration
- ✅ **Pest 4** - Modern testing with browser tests, type coverage, code coverage
- 🔒 **Security First** - Best practices built-in

## Quick Install

```bash
# Clone or download to your Claude Code plugins directory
git clone https://github.com/YOUR_USERNAME/skylence-claude-code-laravel-livewire4.git

# Or install via Claude Code marketplace
/plugin install skylence-laravel-livewire4-kit
```

## What's Inside

### 📦 Slash Commands (35 Total)

#### Laravel Commands (17)
- `/laravel:model-new` - Eloquent model with migration
- `/laravel:controller-new` - Resource/API controllers
- `/laravel:migration-new` - Database migrations
- `/laravel:factory-new` - Model factories for testing
- `/laravel:seeder-new` - Database seeders
- `/laravel:request-new` - Form requests with validation
- `/laravel:policy-new` - Authorization policies
- `/laravel:resource-new` - API resources
- `/laravel:middleware-new` - HTTP middleware
- `/laravel:job-new` - Queue jobs
- `/laravel:event-new` - Events
- `/laravel:listener-new` - Event listeners
- `/laravel:mail-new` - Mailable classes
- `/laravel:notification-new` - Multi-channel notifications
- `/laravel:observer-new` - Model observers
- `/laravel:rule-new` - Custom validation rules
- `/laravel:command-new` - Artisan console commands

#### Livewire Commands (4)
- `/livewire:component-new` - Livewire 4 components with reactive properties
- `/livewire:form-new` - Livewire forms with validation
- `/livewire:attribute-new` - Custom Livewire attributes
- `/livewire:layout-new` - Livewire layout templates

#### Filament Commands (11)
- `/filament:resource-new` - CRUD resources with pages
- `/filament:page-new` - Custom pages
- `/filament:widget-new` - Dashboard widgets (stats, charts, tables)
- `/filament:relation-manager-new` - Relation managers
- `/filament:panel-new` - Multi-panel applications
- `/filament:cluster-new` - Resource organization clusters
- `/filament:custom-field-new` - Custom form fields
- `/filament:custom-column-new` - Custom table columns
- `/filament:exporter-new` - Data exporters
- `/filament:importer-new` - Data importers
- `/filament:theme-new` - Custom panel themes

#### Utility Commands (3)
- `/new-task` - Analyze task complexity and create implementation plan
- `/misc:code-cleanup` - Clean up code following best practices
- `/misc:code-optimize` - Optimize code for performance
- `/misc:feature-plan` - Plan feature implementation

### 🤖 Specialized AI Agents (11)

1. **eloquent-expert** - Eloquent ORM, relationships, query optimization
2. **laravel-architect** - Architecture, patterns, modular design with nwidart/laravel-modules
3. **livewire-specialist** - Livewire 4 reactive components and patterns
4. **filament-specialist** - Filament 4 admin panels, resources, components
5. **testing-expert** - Pest 4/PHPUnit with browser testing, code coverage
6. **security-engineer** - Authentication, authorization, CSRF, SQL injection prevention
7. **optimization-expert** - Performance optimization with skylence/laravel-optimize-mcp
8. **laravel-prompts-expert** - CLI forms and console commands
9. **laravel-pulse-expert** - Performance monitoring and bottleneck identification
10. **laravel-reverb-expert** - WebSocket server and real-time communication
11. **laravel-socialite-expert** - OAuth authentication and social login

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

### Create a Complete Feature

```bash
# Plan the feature
/new-task "Create a blog system with posts, categories, and comments"

# Generate components
/laravel:model-new Post
/laravel:migration-new create_posts_table
/laravel:controller-new PostController
/livewire:component-new PostList
/filament:resource-new PostResource

# Set up testing
/laravel:factory-new PostFactory
php artisan test --coverage
```

### Optimize Your Application

```
"Analyze my Laravel project and help me optimize it"
```

The optimization-expert will use MCP tools to:
- Check configuration for performance issues
- Monitor database size and growth
- Recommend package improvements
- Analyze nginx configuration
- Review project structure

### Set Up Modular Architecture

For projects with 10+ features:
```bash
composer require nwidart/laravel-modules
php artisan module:make Blog
php artisan module:make Shop
```

Agents will guide you on:
- Module structure and organization
- Testing configuration for modules
- Inter-module communication
- Livewire/Filament in modules

## Best Practices Built-In

All commands and agents follow:
- ✅ Laravel best practices and conventions
- ✅ SOLID principles
- ✅ Security-first approach (CSRF, SQL injection prevention)
- ✅ Type safety with PHPStan
- ✅ Test-driven development
- ✅ Performance optimization
- ✅ Modular architecture for scalability

## Configuration

See `plugin.json` for complete feature configuration including:
- All 35 slash commands
- 11 specialized agents
- Integrated package settings
- Testing and quality tool configurations

## Contributing

Contributions welcome! This is an open toolkit for the Laravel community.

## License

MIT License - See LICENSE file for details

## Author

Skylence - [Your GitHub Profile]

## Support

- GitHub Issues: Report bugs and request features
- Documentation: See individual agent files in `.claude/agents/`
- Examples: Check command files in `.claude/commands/`

---

**Built for Laravel developers who want AI-assisted development with best practices, comprehensive testing, and production-ready code.**
