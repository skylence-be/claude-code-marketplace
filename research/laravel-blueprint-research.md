# Laravel Blueprint Best Practices Research

> Compiled from community best practices, official documentation, and developer blog posts (February 2026)

## Table of Contents

1. [Project Planning and Roadmap](#1-project-planning-and-roadmap)
2. [Architecture Patterns and Decision Trees](#2-architecture-patterns-and-decision-trees)
3. [Laravel Blueprint Tool (laravel-shift/blueprint)](#3-laravel-blueprint-tool)
4. [Common Architectural Decisions](#4-common-architectural-decisions)
5. [Project Scaffolding Workflows and Checklists](#5-project-scaffolding-workflows-and-checklists)
6. [Community Leader Best Practices](#6-community-leader-best-practices)
7. [Model Design Patterns and Relationship Planning](#7-model-design-patterns-and-relationship-planning)
8. [API Design and Routing Structure](#8-api-design-and-routing-structure)
9. [Testing Strategy Patterns](#9-testing-strategy-patterns)
10. [Deployment and DevOps Planning](#10-deployment-and-devops-planning)

---

## 1. Project Planning and Roadmap

### Six-Phase Development Roadmap (2025-2026)

**Phase 1 -- Planning and Architecture Design**
- Document business requirements and user stories
- Define and prioritize features using business value criteria
- Create detailed acceptance criteria for each feature
- Establish technical requirements and scalability needs
- Develop user journey maps and technical specification documents
- Select architecture pattern (MVC, DDD, Modular Monolith)
- Create Entity Relationship Diagrams (ERD)
- Plan database migrations with scalability in mind
- Establish naming conventions

**Phase 2 -- Development Environment Setup**
- Use Laravel Sail or Docker for containerized development
- Configure environment variables properly
- Set up Git with branching strategy
- Implement CI/CD pipelines
- Create separate configs for dev/staging/production

**Phase 3 -- Core Development**
- Implement domain logic using Action classes or Service layers
- Set up route management with resourceful routing
- Build API with Resources, proper status codes, and versioning
- Implement authentication (Sanctum/Passport) and authorization

**Phase 4 -- Advanced Features and Optimization**
- Event-driven architecture, CQRS if needed
- Caching strategies (Redis, query caching, HTTP caching)
- Database optimization (indexes, eager loading, connection pooling)
- Consider Laravel Octane for high-performance needs

**Phase 5 -- Testing and Quality Assurance**
- Unit, Feature, API, and Browser testing
- Static analysis with Larastan
- Code formatting with Laravel Pint
- Pre-commit hooks for enforcement

**Phase 6 -- Deployment and Monitoring**
- Zero-downtime deployment (blue-green)
- Monitoring with Telescope, Sentry, New Relic
- Structured logging and alerting

Sources:
- [Comprehensive Laravel Product Development Roadmap 2025-2026 (RCV Technologies)](https://www.rcvtechnologies.com/blog/4538-2/)
- [Laravel Development 2026 Complete Guide (ITMarkerz)](https://itmarkerz.co.in/blog/laravel-development-2026-the-complete-guide-to-building-scaling-enterprise-applications)
- [Laravel Best Practices for 2026 (Smart Logic)](https://smartlogiceg.com/en/post/laravel-best-practices-for-2026)

---

## 2. Architecture Patterns and Decision Trees

### Architecture Decision Framework

| Architecture | When to Choose | Team Size | Complexity |
|---|---|---|---|
| **Standard MVC** | Simple CRUD apps, MVPs, prototypes | 1-3 devs | Low |
| **MVC + Service Layer** | Medium apps with reusable business logic | 2-5 devs | Medium |
| **MVC + Actions** | Medium-large apps wanting SRP compliance | 3-8 devs | Medium |
| **Modular Monolith** | Large apps needing domain separation | 5-15 devs | High |
| **Domain-Driven Design** | Complex business domains, enterprise apps | 5+ devs | High |
| **Microservices** | Very large scale, independent team deployment | 10+ devs | Very High |

### Three Core Architecture Principles (2025)

1. **Keep the default folder structure.** New developers familiar with Laravel can navigate quickly; third-party packages integrate seamlessly. As James Brooks (Laravel core team) states: "Follow the standards laid out by the skeleton and framework."

2. **Organize by domain WITHIN the standard structure.** Create domain folders within standard directories (e.g., `Models/Blog/Category`, `Http/Controllers/Blog/`). Use Artisan commands naturally: `php artisan make:model Blog/Category`.

3. **Avoid unnecessary packages.** When Laravel provides built-in solutions, use them. Don't replace form requests with DTOs without objective justification.

### Service Layer Architecture Pattern

The recommended layered architecture for 2025:

```
Controller -> Service -> Action -> Repository -> Model
```

- **Controller**: Handles HTTP request/response only
- **Service**: Orchestrates multiple actions for a use case
- **Action**: Single-responsibility business operation (e.g., `CreateUserAction`)
- **Repository**: Data access abstraction (optional)
- **Model**: Eloquent entity with relationships and scopes

### DDD Implementation Levels

Four progressive levels of DDD in Laravel:

1. **Subfolder Approach** (Minimal setup): Create `app/Domain/` folder within existing structure
2. **Separate Folder** (Low setup): Place domain outside `app/` at project root, add namespace to `composer.json`
3. **Package/Module Approach** (Medium setup): Domains as separate packages in `packages/` directory
4. **Hexagonal/Three-Layer** (High setup): Application, Domain, and Infrastructure layers with strict separation

Sources:
- [3 Essential Laravel Architecture Best Practices (Benjamin Crozat)](https://benjamincrozat.com/laravel-architecture-best-practices)
- [Laravel DDD Application Structures (JeroenG)](https://jeroeng.dev/blog/laravel-ddd-structures)
- [Clean Service-Action Architecture (Ratheepan Jayakkumar)](https://ratheepan.medium.com/clean-service-action-architecture-a-battle-tested-pattern-for-laravel-applications-dc311ecc5c29)

---

## 3. Laravel Blueprint Tool (laravel-shift/blueprint)

### Overview

Laravel Blueprint is an open-source code generation tool by Jason McCreary (creator of Laravel Shift). It generates multiple Laravel components from a single YAML definition file (`draft.yaml`).

**Requirements**: Laravel 11+
**Installation**: `composer require -W --dev laravel-shift/blueprint`

### YAML Syntax -- Model Definitions

```yaml
models:
  Post:
    title: string:400
    content: longtext
    published_at: nullable timestamp
    author_id: id:user
    softDeletes

  Comment:
    body: text
    post_id: id
    user_id: id
    relationships:
      belongsTo: User, Post
```

### Supported Column Types

All Laravel migration column types are supported. Common ones include:
- `bigIncrements`, `bigInteger`, `binary`, `boolean`
- `char`, `date`, `dateTime`, `decimal`, `double`
- `enum`, `float`, `id`, `integer`, `ipAddress`
- `json`, `jsonb`, `longText`, `morphs`, `string`, `text`
- `timestamp`, `uuid`, `year`

**Type attributes** (appended with colon):
- `string:40` -- string with length 40
- `decimal:8,2` -- precision 8, scale 2
- `enum:pending,successful,failed` -- enum values

### Column Modifiers

`autoIncrement`, `charset`, `collation`, `comment`, `default`, `foreign`, `index`, `nullable`, `onDelete`, `onUpdate`, `primary`, `unsigned`, `unique`, `useCurrent`

Example: `email: string:100 nullable index`

### Relationship Definitions

```yaml
models:
  Post:
    title: string:400
    relationships:
      hasMany: Comment
      belongsToMany: Media, Site
      belongsTo: \Spatie\LaravelPermission\Models\Role
```

Supported types: `belongsTo`, `hasOne`, `hasMany`, `belongsToMany`

### Controller Definitions

```yaml
controllers:
  Post:
    index:
      query: all
      render: post.index with:posts
    store:
      validate: title, content, author_id
      save: post
      send: ReviewPost to:post.author.email with:post
      dispatch: SyncMedia with:post
      fire: NewPost with:post
      flash: post.title
      redirect: posts.index
```

### Generated Components

From a single `draft.yaml`, Blueprint generates:
- Model classes (with fillable, casts, relationships)
- Database migrations
- Model factories
- Controller classes with actions
- Resource routes
- Form request validation classes
- Mailable, Job, and Event classes
- Blade templates
- HTTP tests

Sources:
- [Laravel Blueprint GitHub Repository](https://github.com/laravel-shift/blueprint)
- [Blueprint Documentation](https://blueprint.laravelshift.com/)

---

## 4. Common Architectural Decisions

### Monolith vs. Modular vs. Microservices

**Start monolithic, modularize later.** The 2025 consensus:
- Start with a well-organized Laravel monolith
- Use `nwidart/laravel-modules` or `internachi/modular` to separate domains when complexity grows
- Extract to microservices only when you have independent teams needing independent deployment

| Feature | nwidart/laravel-modules | internachi/modular |
|---|---|---|
| Philosophy | Full-featured module system | Convention-based, minimal tooling |
| File generation | Generates many files with `module:make` | Leverages Laravel package discovery |
| Structure | Custom directory structure | Standard Laravel conventions |
| Best for | Teams wanting opinionated structure | Teams wanting Laravel-native feel |

### Repository Pattern: Use or Skip?

**Use repositories when:**
- You genuinely need to swap data sources
- You need strict separation for unit testing with mocks
- Working on very large, enterprise applications

**Skip repositories when:**
- You are building a typical Laravel application
- You will always use Eloquent/MySQL
- Adding repository interfaces creates unnecessary boilerplate

**Alternative**: Use Action classes instead for testability and separation.

### Frontend Stack Decision (2025-2026)

| Stack | Best For | Adoption |
|---|---|---|
| **Livewire + Filament** | Admin panels, SaaS back-offices, internal tools | 62% |
| **Inertia + Vue/React** | Consumer-facing SPAs, highly interactive UIs | 48% |
| **Blade** | Simple server-rendered pages | Traditional |
| **Decoupled API + SPA** | Separate frontend team, mobile + web clients | Enterprise |

### Service Classes vs. Action Classes

**Service Classes**: Group related methods (e.g., `UserService::create()`, `UserService::update()`)
- Good for grouping related operations
- Can violate SRP as they grow

**Action Classes**: One class, one task (e.g., `CreateUserAction`, `DeactivateUserAction`)
- Strict SRP compliance
- Context-agnostic (reusable across controllers, jobs, commands, listeners)
- Better for medium-to-large projects

**Recommended**: Controller calls Service, Service orchestrates Actions.

Sources:
- [Livewire and Inertia: How We Use Both (Spatie)](https://spatie.be/blog/livewire-and-inertia-how-we-love-and-use-both)
- [Laravel Actions -- One Class One Task](https://www.laravelactions.com/2.x/one-class-one-task.html)

---

## 5. Project Scaffolding Workflows and Checklists

### New Laravel Project Setup Checklist

**1. Installation and Foundation**
- `composer create-project laravel/laravel project-name`
- Configure `.env` file (database, cache, mail, queue)
- Ensure `.env`, `node_modules/`, `vendor/` are in `.gitignore`
- Initialize Git repository with branching strategy

**2. Authentication and Starter Kit**
- Laravel Breeze (simple) or Jetstream (advanced)
- Or Filament for admin panel applications

**3. Core Package Installation**
- `laravel/sanctum` -- API authentication
- `laravel-shift/blueprint` -- code generation (dev)
- `laravel/pint` -- code formatting
- `larastan/larastan` -- static analysis (dev)
- `pestphp/pest` -- testing framework (dev)
- `spatie/laravel-permission` -- roles and permissions (if needed)

**4. Database Design**
- Create ERD using DrawSQL, DrawERD, or Laravel Schema Designer
- Define models, relationships, and indexes
- Write `draft.yaml` for Blueprint or create migrations manually
- Generate factories and seeders

**5. Architecture Setup**
- Create directory structure for chosen pattern
- Set up base classes (BaseController, BaseService, BaseAction)
- Configure route organization
- Set up middleware groups

**6. Development Infrastructure**
- Configure Docker/Sail for local development
- Set up CI/CD pipeline (GitHub Actions)
- Configure pre-commit hooks

**7. API Foundation (if applicable)**
- Set up API versioning (`/api/v1/`)
- Create base API Resource classes
- Configure rate limiting
- Set up API documentation (Scribe)

Sources:
- [Checklist for Setting Up New Laravel App (James Turner)](https://www.jamesturneronline.net/blog/checklist-for-setting-up-a-new-laravel-app.html)
- [Step-by-Step Guide to Laravel 12 Project (Dev-Talk)](https://dev-talk.com/post/step-by-step-guide-to-setting-up-a-laravel-12-project-2025)

---

## 6. Community Leader Best Practices

### Spatie (Freek Van der Herten)

**Core philosophy**: "Laravel provides the most value when you write things the way Laravel intended."

**Key guidelines** (from `spatie.be/guidelines/laravel-php`):
- Follow PSR-1, PSR-2, PSR-12 code standards
- Use typed properties over docblock hints
- Always include `void` return types
- Controllers named as plural + "Controller" suffix
- Use array notation for validation rules (never pipe `|` separated)
- Always use curly brackets in if statements
- Put unhappy path first, happy path last; avoid `else` through early returns
- Use `env()` only in configuration files
- Jobs named as actions (e.g., `CreateUser`)
- Artisan commands use kebab-case

**AI integration**: `spatie/boost-spatie-guidelines` package automatically enforces conventions when AI tools generate code.

### Laravel Daily (Povilas Korop)

- Course: "How to Structure Laravel Projects" -- Services, Actions, Jobs, Observers, Events, Listeners
- Course: "Laravel Modules and DDD" -- compares 3 ways to use Modules
- Advocates analyzing real open-source projects to learn patterns
- Emphasizes practical, real-world patterns over academic theory

### Benjamin Crozat

- Keep default folder structure
- Organize by domain within the standard structure
- Avoid unnecessary packages when Laravel provides built-in solutions

Sources:
- [Spatie Laravel & PHP Guidelines](https://spatie.be/guidelines/laravel-php)
- [How to Structure Laravel Projects (Laravel Daily)](https://laraveldaily.com/course/structure-laravel-projects)
- [3 Laravel Architecture Best Practices (Benjamin Crozat)](https://benjamincrozat.com/laravel-architecture-best-practices)

---

## 7. Model Design Patterns and Relationship Planning

### Eloquent Relationship Planning Guide

| Relationship | When to Use | Example |
|---|---|---|
| `belongsTo` | Child references parent via foreign key | Comment belongs to Post |
| `hasOne` | Parent has exactly one child | User has one Profile |
| `hasMany` | Parent has multiple children | Post has many Comments |
| `belongsToMany` | Many-to-many via pivot table | User belongs to many Roles |
| `hasOneThrough` | Access distant relation through intermediate | Country has one latest Post through User |
| `hasManyThrough` | Access distant relations through intermediate | Country has many Posts through Users |
| `morphOne` | Polymorphic one-to-one | Image morphs to User or Post |
| `morphMany` | Polymorphic one-to-many | Comment morphs to Post or Video |
| `morphToMany` | Polymorphic many-to-many | Tag morphs to many Post, Video |

### Key Design Patterns

- **Fat Models, Skinny Controllers**: Business logic in models (scopes, accessors, mutators)
- **Query Scopes**: Encapsulate common query logic
- **Value Objects / DTOs**: Use `spatie/laravel-data` for complex data transfer
- **Model Factories**: Always create factories alongside models with states for variations

Sources:
- [Eloquent Relationships (Laravel 12.x Official Docs)](https://laravel.com/docs/12.x/eloquent-relationships)
- [Design Patterns Every Laravel Developer Should Know](https://masteryoflaravel.medium.com/design-patterns-every-laravel-developer-should-know-from-theory-to-real-world-implementation-f2856390d986)

---

## 8. API Design and Routing Structure

### RESTful API Best Practices (2025)

**Routing Conventions:**
- Use plural nouns for resources: `/api/v1/users`
- Use nested routes for relationships: `GET /api/v1/users/1/posts`
- Stick to standard HTTP verbs: GET, POST, PUT/PATCH, DELETE
- Use `Route::apiResource()` for CRUD routes

**Versioning**: URI versioning (`/api/v1/`) is the recommended approach.

**API Resources (use from day one):**
```php
class UserResource extends JsonResource {
    public function toArray($request) {
        return [
            'id' => $this->id,
            'name' => $this->name,
            'posts_count' => $this->whenCounted('posts'),
            'posts' => PostResource::collection($this->whenLoaded('posts')),
        ];
    }
}
```

**HTTP Status Codes:**
- 200 OK, 201 Created, 204 No Content
- 401 Unauthorized, 403 Forbidden, 404 Not Found
- 422 Unprocessable Entity (validation), 500 Internal Server Error

**Authentication:**
- **Sanctum** for SPAs and mobile apps
- **Passport** for OAuth2 / third-party authentication

**Always paginate**: Never return unbounded result sets.

**Route Organization:**
```
routes/
  web.php
  api.php
  api/
    v1.php
    v2.php
```

Sources:
- [Laravel API Development RESTful Best Practices 2025 (Hafiz)](https://hafiz.dev/blog/laravel-api-development-restful-best-practices-for-2025)
- [8 Laravel RESTful API Best Practices (Benjamin Crozat)](https://benjamincrozat.com/laravel-restful-api-best-practices)

---

## 9. Testing Strategy Patterns

### Testing Framework: Pest (Recommended for 2025+)

### Nine Best Practices

1. **Use Pest over PHPUnit** for cleaner syntax
2. **Mirror production environment** in tests (MySQL/PostgreSQL, not SQLite)
3. **Prioritize Feature tests** over Unit tests for web applications
4. **Fake remote services** with `Http::fake()`
5. **Implement CI** with GitHub Actions
6. **Enable Continuous Delivery** -- auto-deploy when tests pass
7. **Write tests for bug fixes** to prevent regressions
8. **Avoid over-engineering tests** -- test happy paths and obvious failures
9. **Test outputs, not implementation** -- validate behavior, not internals

### Testing Pyramid for Laravel

```
         /  E2E (Dusk)  \         <- Few, slow, expensive
        /  Feature Tests  \       <- Many, moderate speed
       /    Unit Tests     \      <- Many, fast, focused
      / Static Analysis     \     <- Automated, instant
     / Code Style (Pint)     \    <- Automated, instant
```

Sources:
- [9 Testing Best Practices for Laravel (Benjamin Crozat)](https://benjamincrozat.com/laravel-testing-best-practices)
- [Unit vs Feature Tests in Laravel (d4b)](https://www.d4b.dev/blog/2025-09-15-unit-v-feature-tests)

---

## 10. Deployment and DevOps Planning

### CI/CD Pipeline: 7-Step Checklist

1. **Code Formatting and Linting** -- `./vendor/bin/pint --test`
2. **Static Analysis** -- `./vendor/bin/phpstan analyse --level=5`
3. **Unit + Feature Testing** -- `php artisan test --parallel`
4. **Database Migrations + Seeders** -- Test in staging
5. **Environment Health Check** -- Verify app key, cache, queue, `.env` values
6. **Zero-Downtime Deployment** -- Laravel Deployer, Envoyer, or Ploi
7. **Post-Deploy Monitoring** -- Slack webhooks, Telescope, Sentry

### Deployment Strategy Options

| Strategy | Description | Best For |
|---|---|---|
| **Blue-Green** | Two identical environments, switch traffic | Zero-downtime, instant rollback |
| **Rolling** | Gradual update across instances | Large clusters |
| **Canary** | Route small % to new version | Risk-averse releases |
| **Atomic Symlink** | Symlink switch to new release directory | Standard Laravel deploys |

### Recommended Tools

| Category | Tool |
|---|---|
| CI/CD | GitHub Actions, GitLab CI |
| Deployment | Envoyer, Deployer, Laravel Cloud |
| Monitoring | Laravel Telescope (staging), Sentry/Flare (production) |
| APM | New Relic, Laravel Pulse |
| Queue | Laravel Horizon |
| Code Quality | Laravel Pint, Larastan |
| Security | `composer audit` |

Sources:
- [Laravel CI/CD Pipelines Every App Should Use (SaaSykit)](https://saasykit.com/blog/laravel-ci-cd-pipelines-every-laravel-app-should-use)
- [Laravel CI/CD Checklist (Codecordia)](https://codecordia.com/post/our-laravel-cicd-checklist-7-steps-for-bulletpro)

---

## Blueprint Planning Format Summary

Based on all research, a structured planning format for Laravel projects:

```yaml
# Laravel Project Blueprint
project:
  name: "Project Name"
  laravel_version: 12
  php_version: 8.3

architecture:
  pattern: mvc | service-layer | ddd | modular-monolith
  frontend: blade | livewire | inertia-vue | inertia-react | filament | api-only
  auth: sanctum | passport | jwt
  modules_package: null | nwidart/laravel-modules | internachi/modular

database:
  driver: mysql | postgresql
  cache: redis
  queue: redis
  search: null | meilisearch | algolia

models:
  # Blueprint-compatible YAML definitions
  User:
    name: string
    email: string unique
    password: string
    softDeletes
    relationships:
      hasMany: Post, Comment

controllers:
  Post:
    index:
      query: all
      render: post.index with:posts
    store:
      validate: title, content
      save: post
      redirect: posts.index

api:
  versioning: url  # /api/v1/
  authentication: sanctum
  rate_limit: 60/minute
  pagination: true
  documentation: scribe

testing:
  framework: pest
  strategy:
    feature_tests: priority
    unit_tests: services-and-actions
    browser_tests: critical-flows-only
  ci: github-actions
  static_analysis: larastan:level-6
  formatting: pint

deployment:
  strategy: atomic-symlink | blue-green
  ci_cd: github-actions
  hosting: laravel-cloud | forge | vapor
  monitoring: sentry + pulse
  zero_downtime: true

packages:
  core:
    - laravel/sanctum
    - spatie/laravel-permission
  dev:
    - laravel-shift/blueprint
    - pestphp/pest
    - larastan/larastan
    - laravel/pint
```
