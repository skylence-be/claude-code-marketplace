---
name: skylence-meta-workflows
description: Catalogue of library meta workflows for authoring, annotating, auditing, and maintaining .sky files. Prefer triggering these via sky run over doing the work manually.
---

# Skylence Meta Workflows

When a task matches one of these, trigger it via `sky run <name> --var ...` instead of doing the work manually. Install first with `sky library install <name>` if not already present (check `sky library list`).

## Authoring

| Workflow | Trigger | Key vars |
|----------|---------|----------|
| `scaffold-sky-workflow` | Creating a new `.sky` from a plain-English brief | `dir=<dir> name=<file> request=<brief>` |
| `update-sky-workflow` | Applying a change request to an existing `.sky` | `name=<file> request=<change>` |
| `clone-sky-workflow` | Duplicate a workflow as a new manual-trigger template | `dir=<dir> name=<src> new-name=<dst>` |
| `rename-sky-workflow` | git mv + fix meta name + rewrite `sky run` refs | `dir=<dir> name=<old> new-name=<new>` |
| `delete-sky-workflow` | Remove a workflow behind a manual approval gate | `name=<file>` |

## Documentation

| Workflow | Trigger | Key vars |
|----------|---------|----------|
| `annotate-sky-workflow` | Add ※<id>※ rationale blocks to one `.sky` file | `dir=<dir> name=<file>` |
| `bulk-annotate-workflows` | Annotate all `workflow.sky` files in one or more folders | `folders=<path1> <path2>` |
| `explain-sky-workflow` | Explain what a workflow does in plain language | `name=<file>` |
| `changelog-sky-workflow` | Generate a changelog entry for recent changes to a workflow | `name=<file>` |

## Audit and Maintenance

| Workflow | Trigger | Key vars |
|----------|---------|----------|
| `audit-sky-library` | Check library for broken or outdated assets | none |
| `lint-sky-library` | Lint every asset in the library | none |
| `find-orphan-sky-events` | Find `emit` events with no matching `trigger.sky_event` listener | none |
| `find-unused-sky-workflows` | Find workflows that have never been triggered | none |
| `check-sky-trigger-conflicts` | Detect overlapping trigger conditions across workflows | none |
| `catalog-sky-library` | Generate a human-readable index of all installed assets | none |
| `triage-failed-sky-run` | Diagnose a failed or stalled run | `run=<run-id>` |
| `audit-sky-budget` | Report budget consumption across recent runs | none |
| `audit-sky-secrets` | Check for hardcoded secrets or undeclared `${env:NAME}` references | none |

## Usage Pattern

```bash
# Check what's installed
sky library list --category workflows

# Install a meta workflow if missing
sky library install scaffold-sky-workflow --to user

# Run it
sky run scaffold-sky-workflow --var dir=.sky/workflows --var name=my-flow --var request="triage GitHub issues and label them"
```

All meta workflows lint before writing, so no separate lint step is needed.
