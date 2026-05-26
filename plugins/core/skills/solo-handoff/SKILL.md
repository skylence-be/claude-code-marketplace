---
name: solo-handoff
description: Use PROACTIVELY when the user needs to share state across Claude sessions, hand off work to another agent, or coordinate across Solo projects. Triggers: 'hand off to another agent', 'save this for next session', 'shared todo', 'transfer to other project', 'scratchpad', 'lock to prevent race', 'cross-project', 'another agent needs this'. For in-conversation work only, use TaskCreate instead.
---

# Solo Handoff

Coordination primitives for cross-session and cross-agent state via the Solo MCP server.

## When to use what

| Need | Tool |
|---|---|
| Persist structured notes for next session | `scratchpad_write` |
| Append ongoing observations | `scratchpad_append` / `scratchpad_append_section` |
| Update a specific passage | `scratchpad_edit` |
| Shared task list across agents | `todo_create` / `todo_list` |
| Mark a task done | `todo_complete` |
| Prevent concurrent writes to a shared resource | `lock_acquire` / `lock_release` |
| Move state to a different Solo project | `scratchpad_transfer` / `todo_transfer` |
| In-conversation work only | TaskCreate (built-in, not Solo) |
| Permanent user-level preferences | `~/.claude/memory/` |

---

## SoloTerm workflow

When the user is working inside SoloTerm (a Solo-managed terminal session), follow this pattern:

**Session start**: check for an existing scratchpad before doing anything else:
```
scratchpad_list()               # look for a scratchpad named after the project or task
scratchpad_read(id)             # load context if one exists
todo_list()                     # check open todos before starting
```

**During work**: keep the scratchpad current:
```
scratchpad_append(id, content)                             # running notes, discoveries
scratchpad_append_section(id, "## Decisions", content)    # named section for a topic
scratchpad_edit(id, target, new_content, revision)        # replace a specific block
todo_create(title, body)                                   # track a new work item
todo_update(todo_id, body=new_body)                       # revise a todo
```

**Session end / handoff**: leave a clean state for the next agent:
```
scratchpad_append_section(id, "## Handoff", handoff_text) # add pick-up notes; include suggested skills
todo_complete(todo_id)                                     # close finished items
scratchpad_archive(id)                                     # archive if the work is done
```

The handoff section should include a "Suggested skills" list naming any skills the next agent should invoke, and references (absolute paths or URLs) to existing plans, PRDs, or diffs rather than restating them inline.

---

## Scratchpad CRUD reference

### Create
```
scratchpad_write(name, content)
```
A leading `# H1` in `content` becomes the scratchpad's display title. Scope is the current project unless you pass `project_id`.

### Read
```
scratchpad_read(id)             # full content
scratchpad_tail(id, lines=50)   # last N lines; faster for long pads
scratchpad_find(id, query)      # search text *within* one scratchpad
scratchpad_list()               # browse all scratchpads in the project
```

### Update
```
scratchpad_append(id, content)                              # add lines at the end
scratchpad_append_section(id, heading, content)             # add a named ## section
scratchpad_edit(id, target, content, expected_revision)     # replace a block in-place
scratchpad_clear(id)                                        # wipe content, keep metadata
scratchpad_rename(id, name)                                 # rename
scratchpad_add_tags(id, tags)                               # tag for filtering
scratchpad_remove_tags(id, tags)
```

`expected_revision` on `scratchpad_edit` is a concurrency guard; pass the revision from the last read. The call fails if the pad has changed since, so you don't silently overwrite concurrent writes.

### Move / export
```
scratchpad_transfer(id, target_project_id)   # move to another Solo project
scratchpad_save_to_file(id, path)            # dump to a local file
scratchpad_load_from_file(name, path)        # create a scratchpad from a file
```

### Delete
```
scratchpad_archive(id)                       # soft-delete; recoverable
scratchpad_delete(id, expected_revision)     # permanent; pass revision as safety check
```

---

## Todo lifecycle

### Create and read
```
todo_create(title, body?, tags?)    # body accepts markdown
todo_get(todo_id)                   # full detail including blockers and comments
todo_list()                         # all todos in project; filter by tag or status
```

### Update
```
todo_update(todo_id, title?, body?, ...)    # patch any field
todo_add_tag(todo_id, tag)
todo_remove_tag(todo_id, tag)
todo_comment_create(todo_id, body)          # threaded notes
todo_comment_update(comment_id, body)
todo_comment_delete(comment_id)
```

### Dependencies
```
todo_add_blocker(todo_id, blocker_todo_id)       # this todo is blocked by another
todo_remove_blocker(todo_id, blocker_todo_id)
todo_set_blockers(todo_id, [ids])                # replace full blocker set
```

Pass `response_mode: "rich"` on write ops (`todo_create`, `todo_update`, etc.) to get fully hydrated state back in the response without a separate `todo_get`.

### Complete or remove
```
todo_complete(todo_id)               # mark done; stays visible in history
todo_delete(todo_id)                 # hard delete
todo_lock(todo_id)                   # exclusive write lock (multi-agent)
todo_unlock(todo_id)
```

### Cross-project
```
todo_transfer(todo_id, target_project_id)   # move to another Solo project
```

---

## Locks

Use locks when multiple agents may write to the same scratchpad or shared resource concurrently.

```
lock_acquire(key)       # block until acquired
lock_release(key)       # always release in the same session that acquired
lock_status(key)        # inspect current holder and TTL
```

Always release in the same session that acquired. A lock left unreleased persists until TTL expiry.

---

## Cross-project transfer

Resolve `target_project_id` with `list_projects` before transferring:
```
list_projects()
scratchpad_transfer(id, target_project_id)
todo_transfer(todo_id, target_project_id)
```

---

## Scratchpad content rules

1. Redact API keys, passwords, and PII; write `[REDACTED]` in place.
2. Don't re-state content already captured in plans, PRDs, ADRs, issues, or diffs; reference by absolute path or URL instead.
3. Include a "Suggested skills" section in handoff notes naming skills the next agent should invoke.

---

## Handoff chain

If handing off to a freshly spawned agent, use `xve:solo-spawn` first to get the agent's process ID, then pass scratchpad IDs in the initial prompt so the agent can `scratchpad_read` immediately without `scratchpad_list` guesswork.
