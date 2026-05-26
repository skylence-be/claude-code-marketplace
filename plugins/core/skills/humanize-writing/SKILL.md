---
name: humanize-writing-skill
description: "Humanize text that sounds too AI or too ChatGPT. Triggers: 'humanize this', 'make it less AI', 'sounds too ChatGPT', 'remove em dashes', 'de-AI writing'. Skip for technical docs, READMEs, code comments, commit messages, formal/academic tone."
license: MIT
---

# Humanize Writing

Make text sound like a specific human wrote it. Read `references/ai-patterns-dictionary.md` first — it's the banned word list, structural tells, and examples.

## Pick a voice first

1. User specified → use it.
2. User provided a sample → mirror it (sentence length, word choice, punctuation habits, transitions). Disliked samples are equally useful.
3. Neither → ask:
   > "What voice?
   > - **Clear thinker** — direct, no decoration, smart person working through an idea
   > - **Casual** — like telling a friend. Warm, loose, real.
   > - **Sharp** — strong takes, punchy sentences, zero hedging
   > - **Warm professional** — credible and polished but still sounds like a person
   > - **Your voice** — paste a sample and I'll match it"
4. User says "just do it" → default to **clear thinker** and go.

## Three passes

**Pass 1 — Kill AI vocabulary.** Replace every Tier 1 word. Replace Tier 2 where clustered. Delete Tier 3 transition clusters (>2 in a short section) — good writing rarely needs explicit connectors. Don't just swap synonyms; restructure when the fancy word isn't needed.

**Pass 2 — Break AI structures.** These are stronger tells than vocabulary:
- Em dashes: never. Replace every one with a comma, period, or parentheses.
- Parallel negation ("Not X, but Y") → state the positive directly.
- Rule of three → pick the one or two that matter.
- Rhetorical Q + answer ("What does this mean? It means...") → just say it.
- Mirror structures (consecutive sentences with identical shapes) → break the symmetry.
- Neat paragraph endings → let ≥30% just stop without a tidy conclusion.
- Inflation of importance ("pivotal", "testament to") → delete. Content speaks for itself.
- Signposting ("Let's dive in") → drop the announcement, start with the substance.
- Secondary convergence → when you stop using one AI pattern, don't replace it with another. Vary approaches; sometimes no transition at all.

**Pass 3 — Add human texture.** Apply the selected voice, then: vary sentence length aggressively (short, long, fragment); start some sentences with "And" or "But"; have opinions (remove "it could be argued"); use specific numbers/names/dates over vague claims; leave some thoughts unresolved.

## Anti-AI audit

After rewriting: ask "What still makes this obviously AI-generated?" — note 2–4 remaining tells, fix them, then present the final version.

## Checklist

- [ ] Zero Tier 1 words
- [ ] Tier 2 words max once each
- [ ] ≤2 formal transition words total
- [ ] No parallel negation / tricolons / mirror structures
- [ ] Zero em dashes
- [ ] No rhetorical Q+A / inflation of importance / signposting
- [ ] Sentence length varies; at least one starts with "And" or "But"
- [ ] Author's opinion is visible; reads like a person, not a press release
- [ ] Output matches the selected voice

Keep meaning and facts intact. Don't dumb it down — "human" isn't "simplistic." Don't over-correct into a different kind of artificiality — forced casualness is just as obvious. Return the rewrite only; don't explain changes unless asked.

---
*Based on [Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing), [brandonwise/humanizer](https://github.com/brandonwise/humanizer), [blader/humanizer](https://github.com/blader/humanizer), [lguz/humanize-writing-skill](https://github.com/lguz/humanize-writing-skill). MIT.*
