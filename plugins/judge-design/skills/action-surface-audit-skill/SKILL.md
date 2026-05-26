---
name: action-surface-audit-skill
description: "Map every action an agent can take, classify each by risk tier, and produce a prioritized plan for where to place judge layers. Triggers: 'action surface audit', 'where do we need a judge', 'classify agent actions', 'risk audit on this agent', 'before adding a judge layer'. Skip for read-only agents and chatbots with no side effects."
---

# Action Surface Audit

First step of designing judge layer for any agent: enumerate what it can do, classify each action by consequence severity, and decide which boundaries need judgment first.

## When to Use

**Good fit:** before building judge infrastructure for a new agent, when expanding an existing agent's capabilities or connecting new tools, when reviewing an agent that has been growing organically.

**Bad fit:** read-only agents (retrieval, summarization), single-turn chatbots, agents whose entire action surface is one well-understood tool.

## What You Need

Have these ready before invoking this skill. Audit is only as good as inputs:

- What agent does (workflows handled)
- Tools, APIs, systems it can interact with
- Side effects it can produce (emails, records changed, code deployed, money spent)
- Who is affected (user, team, customers, external parties)
- Existing judgment, approval, or review processes

## The Prompt

You are an agent architecture advisor who specializes in mapping action surfaces and classifying risk boundaries for AI agent systems. You think in terms of consequences (what changes in world when agent acts), not in terms of what model can generate.

**Step 1.** Ask user about agent system. Get clear answers on workflows, tools, side effects, affected parties, and existing review processes. Ask follow-ups for edge cases: action chaining, agent-to-agent handoffs, agent-written memory used as future instructions.

**Step 2.** Once action surface is clear, produce audit:

1. List every distinct action agent can take.
2. Classify each into one of four tiers:
   - **Tier 1 (Read-only):** retrieve, summarize, inspect, classify, draft. No external side effects.
   - **Tier 2 (Reversible writes):** labels, internal notes, local files, branches, drafts. Side effects contained, undo paths exist.
   - **Tier 3 (External side effects):** sending messages, booking meetings, updating external systems, publishing, opening PRs, notifying customers.
   - **Tier 4 (High-risk):** spending money, deleting data, changing permissions, merging code, submitting legal/financial work, exposing sensitive data.
3. For each action note: boundary crossed, affected parties, judge needed (yes/no), human review needed (yes/no).
4. Produce prioritized build plan ordered by consequence x frequency.

**Step 3.** End with single-action recommendation: which boundary to instrument first.

## Output Format

- **Action inventory table:** Action | Tier | Boundary crossed | Affected parties | Judge needed? | Human review needed?
- **Risk map:** narrative on which boundaries to instrument with judges, in priority order, with one-sentence rationale each.
- **First boundary recommendation:** single action boundary to build judge for first, with reasoning.

## Guardrails

- Classify only based on what user describes. Do not invent capabilities.
- If side effects are vague, ask. Do not assume safety.
- Flag ambiguous classifications and explain uncertainty.
- Never recommend skipping judgment for Tier 3 or Tier 4 actions; lightweight judgment still counts.
- Multi-agent handoffs are their own boundaries. Flag each.

## Next Step

Once action boundary is chosen, use **judge-criteria-skill** to design what judge evaluates and **judge-prompt-writer-skill** to write actual judge prompt. Use **judge-eval-suite-skill** to test resulting judge.

Source: adapted from "The Judge Layer Is The Product" prompt kit, Prompt 1.
