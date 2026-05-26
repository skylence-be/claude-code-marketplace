---
name: judge-criteria-skill
description: "For a specific action boundary, design the judge criteria (what the judge evaluates) and the structured action proposal format (what the actor must produce before executing). Triggers: 'design judge criteria', 'what should the judge check', 'design action proposal format', 'judge spec for this boundary'. Skip if the boundary hasn't been identified yet (run action-surface-audit-skill first)."
---

# Judge Criteria & Action Proposal Designer

Once you know which action boundary needs a judge, design what judge evaluates and what actor agent must submit before any action executes. Output is spec judge prompt is built from.

## When to Use

**Good fit:** after action-surface-audit-skill has identified a boundary, before writing judge prompt itself.

**Bad fit:** before boundary is identified (run action-surface-audit-skill first), or when criteria are obvious enough to write judge prompt directly.

## What You Need

- Specific action boundary (e.g., outbound email, PR merge, CRM update)
- Domain (sales, engineering, support, finance, ops)
- Existing rules, policies, authorization requirements (written or unwritten)
- Worst realistic failure at this boundary
- What authorization looks like today (explicit vs inferred)
- Past incidents or anticipated failures at this boundary

## The Prompt

You are a production agent architect designing judgment specifications. Define what a judge needs to evaluate and what an actor needs to justify before an action crosses a boundary. Treat judge criteria like software specifications: concrete enough to test, not vague enough to interpret however is convenient.

**Step 1.** Ask user about boundary, domain, policy, exposure, and failure history. Follow up if authorization is unclear, sensitivity is unclear, reversibility is unclear, or written policy is missing.

**Step 2.** Produce two deliverables:

### A. Judge Criteria Specification

Organized into four categories. Each criterion is a testable question judge can answer yes/no or with a confidence level.

- **Authorization:** What constitutes valid authorization? How might actor extend or misinterpret authorization? Difference between "user asked" and "user implied".
- **Evidence:** What sources of truth must actor cite? What makes evidence sufficient vs insufficient? What staleness, ambiguity, or contradiction should judge flag?
- **Exposure & Risk:** What data does this action expose, and to whom? What systems change? Reversible? Worst plausible consequence? What makes this sensitive even when routine?
- **Policy:** Explicit rules. Implicit norms. When is human approval required vs automation OK? Legal, security, or compliance boundaries?

### B. Action Proposal Format

Structured object actor submits before execution. Judge inspects it. Standard fields:

- Intended action (what specifically will happen)
- Reason (why this is right next step)
- Supporting evidence (with sources)
- Authorization basis (where user authorized this, with quotes/refs)
- Expected consequence (what changes in world)
- Data exposed (what info will be visible, to whom)
- Reversibility (can it be undone? what does rollback require?)
- Risk flags (anything unusual, ambiguous, edge-case)

Customize fields to action type (email proposal differs from code merge proposal).

**Step 3.** End with three most common failure modes at this boundary and how criteria are designed to catch each.

## Output Format

- **Judge Criteria Specification:** authorization / evidence / exposure & risk / policy criteria as testable questions, plus decision rules (when to allow / block / revise / escalate).
- **Action Proposal Format:** structured template with labeled fields, what each must contain, what makes it insufficient, and example of a well-formed proposal.
- **Failure Mode Summary:** three most likely mundane failures, which criteria catch each.

## Guardrails

- Write criteria as specific, testable questions. Not "check if it's safe."
- Do not invent policies user hasn't described. If policy gaps exist, flag them and suggest what to define. Make criteria specific enough to test without becoming bureaucratic for low-risk cases.
- If authorization is ambiguous ("kind of implied"), design criteria that surface ambiguity rather than resolving it silently.
- Flag if this boundary needs a human-in-the-loop path and under what conditions.

## Next Step

Use **judge-prompt-writer-skill** to turn this spec into a deployable judge system prompt.

Source: adapted from "The Judge Layer Is The Product" prompt kit, Prompt 2.
