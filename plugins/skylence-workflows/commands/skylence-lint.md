---
description: Lint Skylence .sky files and explain each error code with the exact fix
---

# Lint Skylence Workflows

Run `./bin/sky lint` on `.sky/workflows/` (or a single file), report every error with its lint code, and propose a concrete fix for each one.

## Specification

$ARGUMENTS

## Process

1. **Determine scope**: a specific file from `$ARGUMENTS` or the full `.sky/workflows/` directory
2. **Run the lint**: `./bin/sky lint [path]`
3. **For each error**, identify the lint code (e.g., `SKY-WF-040`) and look it up in the table below
4. **Propose a fix** with the exact line edit and the rationale
5. **Re-lint after fixes** to confirm zero remaining errors

## Examples

### Full lint

```bash
./bin/sky lint
```

### Single file

```bash
./bin/sky lint .sky/workflows/triage-issue.sky
```

## Common Lint Codes

| Code | Meaning | Fix |
|------|---------|-----|
| `SKY-WF-040` | `chain_from` target missing from `depends_on` | Add the chain target to `depends_on` |
| `SKY-WF-047` | Bare `{{var}}` in `http.body` JSON literal | Use `{{var|json}}` to JSON-escape the value |
| `SKY-WF-055` | Undeclared `${env:NAME}` reference | Add `NAME` to the `secrets` array in `⊕meta⊕` |
| `SKY-WF-060` | Invalid `output_format` JSON schema | Fix schema; verify required fields and types |
| `SKY-WF-...` (general) | Trigger missing, duplicate node id, unknown key | Read the lint message; the daemon prints the line |

## Tips

- Lint runs as a pre-commit hook via lefthook in the Skylence repo. If lint fails, the commit is blocked. Fix every error first.
- The lint is fast; run it every time a `.sky` file is touched.
- A `when` condition with a bareword RHS does not lint-fail (it parses) but silently skips the node forever. Always quote the RHS: `"$x.output == 'value'"`.

After fixing, re-run `./bin/sky lint` to confirm a clean exit.
