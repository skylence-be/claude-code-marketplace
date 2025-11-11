# Agent Prompt Guide: Writing Effective Sub-Agent Descriptions

This guide explains how to write agent descriptions that enable Claude Code to **automatically delegate** tasks to your specialized sub-agents.

## The Pattern

For Claude Code to proactively use your sub-agents, your agent description must follow this pattern:

```markdown
description: [What the agent does]. Use PROACTIVELY when [specific trigger scenarios].
```

## Required Components

### 1. The PROACTIVELY Keyword

This signals to Claude Code that it should use this agent without being explicitly asked.

```markdown
Use PROACTIVELY when...
```

**Alternative phrasing:**
- `Specialist for [task]. Use proactively for...`
- `Use this agent proactively when...`
- `Must be used when...`

### 2. The WHEN Clause

This tells Claude Code **exactly when** to trigger this agent. Be specific!

**Good WHEN clauses:**
```markdown
when designing Laravel applications, planning architecture, or discussing system design patterns
when implementing security features, reviewing code for vulnerabilities, or auditing applications
when optimizing database queries, fixing N+1 problems, or improving performance
when writing tests, implementing TDD, or building test suites
```

**Bad WHEN clauses (too vague):**
```markdown
when needed
when appropriate
for Laravel development
```

## Real Examples from This Marketplace

### Laravel Architect
```markdown
description: Expert Laravel architect specializing in scalable application design, modular architecture (nwidart/laravel-modules), SOLID principles, and modern PHP patterns. Masters service containers, dependency injection, repository patterns, event-driven architecture, and performance optimization. Use PROACTIVELY when designing Laravel applications, planning architecture, or discussing system design patterns.
```

**Why this works:**
- ✅ Clearly states expertise
- ✅ Uses "PROACTIVELY" keyword
- ✅ Specifies concrete scenarios: designing, planning, discussing architecture
- ✅ Claude Code knows to delegate when user asks about architecture

### Security Engineer
```markdown
description: Identify security vulnerabilities and ensure compliance with Laravel security standards and best practices. Masters authentication, authorization, CSRF/XSS prevention, SQL injection protection, and rate limiting. Use PROACTIVELY when implementing security features, reviewing code for vulnerabilities, or auditing applications.
```

**Why this works:**
- ✅ States what it identifies/ensures
- ✅ Lists specific security areas
- ✅ Clear triggers: implementing, reviewing, auditing
- ✅ Claude Code knows to delegate on security-related prompts

## Adding Concrete Trigger Phrases

You can also add explicit keyword triggers:

```markdown
description: Generates completion summaries with text-to-speech output. Use PROACTIVELY when tasks complete. If they say "TTS", "TTS summary", or "text to speech", use this agent.
```

This helps Claude Code match specific user phrases to your agent.

## The Information Flow

Understanding **who talks to whom** is critical:

```
User → Claude Code (primary agent) → Sub-agent → Primary agent → User
```

**Key insight:** Sub-agents respond to the **primary agent**, not to the user. Your description helps the primary agent know:
1. When to call your sub-agent
2. How to prompt your sub-agent
3. What to expect back

## Best Practices

### ✅ DO:

1. **Be specific about triggers**
   ```markdown
   Use PROACTIVELY when optimizing Eloquent queries, fixing N+1 problems, or implementing eager loading
   ```

2. **List concrete scenarios**
   ```markdown
   when writing Pest tests, implementing TDD, or creating feature/unit tests
   ```

3. **Include relevant keywords**
   ```markdown
   Masters authentication, authorization, CSRF/XSS prevention, SQL injection protection
   ```

4. **State the expertise clearly**
   ```markdown
   Expert in Laravel Eloquent ORM, relationships, query optimization, and database patterns
   ```

5. **Add explicit phrase triggers when helpful**
   ```markdown
   If they say "optimize", "performance", or "slow query", use this agent
   ```

### ❌ DON'T:

1. **Be vague**
   ```markdown
   Use when needed for Laravel stuff
   ```

2. **Forget the WHEN clause**
   ```markdown
   Expert Laravel developer. Use PROACTIVELY.
   ```

3. **Overlap too much with other agents**
   - Each agent should have distinct trigger scenarios
   - Avoid ambiguity about which agent to use

4. **Make descriptions too long**
   - Claude Code reads these for every decision
   - Keep focused on key triggers and expertise

## Template

Use this template for new agents:

```markdown
---
name: your-agent-name
description: [Brief expertise statement]. Masters [key skills/areas]. Use PROACTIVELY when [scenario 1], [scenario 2], or [scenario 3]. If they say "[keyword1]", "[keyword2]", use this agent.
category: engineering | quality | architecture | performance
model: sonnet | opus | haiku
color: red | blue | green | yellow | purple | orange | pink | cyan
---

# Agent Name

You are a [role definition].

## Instructions

When invoked, you must:
1. [Step-by-step instructions]
2. [...]

**Best Practices:**
- [Domain-specific best practices]
- [...]

## Report

Provide your response to the **primary agent** (not the user) with:
- [What information to return]
- [Expected format]
```

## Testing Your Agent Descriptions

After creating/updating agent descriptions:

1. **Test explicit invocation:**
   ```
   User: "Use the security-engineer agent to review this code"
   ```

2. **Test proactive triggering:**
   ```
   User: "Review this authentication code for security issues"
   ```
   Claude Code should automatically use security-engineer

3. **Check the logs:**
   - Hooks will log when sub-agents are called
   - Review `logs/subagent_stop.json` to see which agents ran

## Common Trigger Scenarios by Domain

### Architecture/Design
- designing applications
- planning architecture
- discussing system design patterns
- evaluating architectural decisions

### Security
- implementing security features
- reviewing code for vulnerabilities
- auditing applications
- security assessments

### Performance
- optimizing performance
- fixing slow queries
- improving response times
- identifying bottlenecks

### Testing
- writing tests
- implementing TDD
- creating test suites
- testing strategies

### Database
- designing schemas
- optimizing queries
- fixing N+1 problems
- implementing relationships

## Summary

**The magic formula:**
```
What it does + Use PROACTIVELY when + Specific scenarios + Optional keyword triggers
```

When done correctly, Claude Code will automatically route tasks to your specialized agents based on user intent, creating a powerful multi-agent workflow without requiring explicit agent selection.

---

**For more information:**
- Claude Code Sub-Agents Docs: https://docs.anthropic.com/en/docs/claude-code/sub-agents
- Dev Dan's Sub-Agents Video: https://www.youtube.com/watch?v=example
