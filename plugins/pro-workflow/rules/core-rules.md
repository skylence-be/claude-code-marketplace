# Core Rules

Universal rules for any project. Add to CLAUDE.md or use as reference.

## Quality
- Run lint/typecheck before commit
- Test affected code after changes
- No `console.log` / `dd()` / `dump()` / `var_dump()` / `debugger` in production code
- No hardcoded secrets, API keys, or credentials
- No TODO/FIXME without ticket references in committed code

## Git
- Atomic commits — one logical change per commit
- Conventional commit messages: `type(scope): summary`
- Feature branches, never commit directly to main
- Review changes before push (`/pro-workflow:commit`)

## Context
- Read before edit — understand existing code first
- Plan before multi-file changes (use plan mode for >3 files)
- Compact context at task boundaries (`/compact`)
- Keep <10 MCPs enabled, <80 tools total

## Learning
- Capture corrections: `[LEARN] Category: Rule`
- Review learnings at session start
- Patterns compound over time — the more you capture, the fewer mistakes

## Communication
- Concise > verbose
- Action > explanation
- Ask when unclear — don't assume
- Acknowledge mistakes immediately

## Performance (Model Selection)
- Haiku for quick tasks (simple edits, lookups)
- Sonnet for features (standard implementation)
- Opus for architecture (complex design, multi-system)

## Claude Code Mastery
- Use plan mode for multi-file changes
- Write CLAUDE.md with structure, conventions, rules
- Manage context: `/compact` at task boundaries, `/context` to check usage
- Prompts need: scope + context + constraints + acceptance criteria
- Build skills for repeated workflows (>3 repetitions)
- Delegate to subagents for parallel exploration
- Use hooks for automated quality gates
- Review security model before handling sensitive data

## PHP-Specific
- No `ray()` calls in committed code
- No `dd()` or `dump()` in committed code
- Run `./vendor/bin/pint` before committing PHP files
- Run `php artisan test` after changes to Laravel code

## JavaScript/TypeScript-Specific
- No `console.log` or `debugger` in committed code
- Run linter and type checker before committing

## Python-Specific
- No `print()` debug statements or `breakpoint()` in committed code
- No `pdb` imports in committed code
