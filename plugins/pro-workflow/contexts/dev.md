# Development Mode

Switch to this context when actively building features.

## Mindset
- Code first, explain after
- Working > right > clean
- Iterate quickly, test frequently

## Priorities
1. **Get it working** — make it functional first
2. **Get it right** — fix edge cases and correctness
3. **Get it clean** — refactor only after it works

## Behavior
- Run tests after every meaningful change
- Keep commits atomic and focused
- Use plan mode for changes touching >3 files
- Quality gates before every commit (`/pro-workflow:commit`)
- Check for debug artifacts before committing

## Anti-Patterns
- Don't over-engineer before it works
- Don't refactor while debugging
- Don't skip tests "just this once"
- Don't commit debug statements

## Trigger
Say: "Switch to dev mode" or "Let's build"
