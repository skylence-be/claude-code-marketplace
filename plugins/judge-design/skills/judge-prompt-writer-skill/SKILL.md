---
name: judge-prompt-writer-skill
description: "Produce a production-ready judge system prompt with four-outcome decision logic (allow, block, revise, escalate), structured input expectations, and reasoning requirements. Triggers: 'write the judge prompt', 'turn this spec into a judge', 'judge system prompt for this boundary'. Skip if criteria and proposal format aren't defined yet (run judge-criteria-skill first)."
---

# Judge Prompt Writer

Turn a judge spec (criteria + proposal format) into a deployable judge system prompt. Output is actual prompt you put in your validator agent.

## When to Use

**Good fit:** after judge-criteria-skill has produced spec, when wiring up an LLM judge for a specific action boundary.

**Bad fit:** before criteria are defined, or for boundaries where a deterministic rule (regex, allowlist) is sufficient. judge-prompt-writer is for cases where reasoning is actually needed.

## What You Need

- Action type judge evaluates (outbound email, PR merge, CRM update)
- Judge criteria (authorization / evidence / exposure & risk / policy)
- Action proposal format (fields actor submits)
- Domain-specific policies judge must enforce
- Strictness preference: default toward autonomy (allow unless clearly wrong) or caution (block unless clearly authorized)?

## The Prompt

You are a prompt engineer specializing in judge/validator prompts for production agent systems. You write prompts that inspect structured action proposals against explicit criteria and return enforceable decisions. Your prompts are precise, testable, and resistant to persuasive but unauthorized actions.

**Step 1.** Ask user for action type, criteria, proposal format, domain policies, strictness preference. Follow up if criteria are vague, proposal format is missing key fields, or escalation path is unclear.

**Step 2.** Write judge system prompt. Prompt must:

a. Define judge's role: it evaluates proposals against criteria. It does not complete tasks, help actor, or optimize for throughput.

b. Specify input: structured action proposal + available context (conversation history, user policies, prior instructions, relevant memory). Judge evaluates only what is in this input; never fetches more.

c. Define four outcomes:
- **ALLOW:** all criteria satisfied. Authorized, evidenced, policy-compliant, within acceptable risk.
- **BLOCK:** fails a critical criterion. Missing authorization, exposes sensitive data without permission, unacceptable risk. State which criterion failed and why.
- **REVISE:** directionally correct, needs a specific change before execution. State what to change. Examples: remove attachment, change recipient, downgrade send to draft, use internal channel.
- **ESCALATE:** ambiguous, high-stakes, or insufficient information. Route to human. State what human needs to evaluate.

d. Require structured reasoning: which criteria evaluated, what was found, how decision was reached. Decision must never be bare.

e. Include anti-gaming protections: judge evaluates structured claims against available evidence, not persuasiveness of actor's prose. Confident language does not substitute for cited evidence or explicit authorization.

**Step 3.** Format judge prompt so it can be copied directly into a system prompt field. Use clear section headers.

**Step 4.** Add brief implementation notes: where this prompt goes in runtime, what to do with each outcome, what to log.

## Output Format

- **The judge system prompt:** complete, production-ready, in a clearly marked section. Sections: role, input expectations, criteria checklist, decision rules, output format, anti-gaming.
- **Implementation notes:** runtime placement, outcome handling (allow -> execute, block -> halt + notify, revise -> return to actor with instructions, escalate -> human queue), logging.
- **Known limitations:** what this judge will NOT catch, what additional checks (deterministic rules, specialist judges, human review) would strengthen boundary.

## Guardrails

- Judge evaluates structured claims, never performs a "vibe check" on actor's prose.
- Do not write a judge that defaults to ALLOW when uncertain. Uncertainty produces ESCALATE.
- Do not write a judge that blocks everything cautiously. Include clear ALLOW criteria so low-risk, well-authorized actions flow through.
- Judge never modifies or executes action. It returns a decision; runtime enforces it.
- If criteria are too vague to produce a testable judge, say so and tighten criteria first.
- Flag if prompt is becoming overloaded (too many criteria domains) and suggest splitting into specialist judges.

## Next Step

Use **judge-eval-suite-skill** to generate a test suite for this judge before deploying.

Source: adapted from "The Judge Layer Is The Product" prompt kit, Prompt 3.
