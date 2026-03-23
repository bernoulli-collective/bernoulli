---
description: Design the smallest convincing ablation set for an AI research project.
---
Design an ablation plan for: $@

Requirements:
- Identify the exact claims the paper is making.
- For each claim, determine what ablation or control is necessary to support it.
- Prefer the `verifier` subagent when the claim structure is complicated.
- Distinguish:
  - must-have ablations
  - nice-to-have ablations
  - unnecessary experiments
- Call out where benchmark norms imply mandatory controls.
- Optimize for the minimum convincing set, not experiment sprawl.
- If the user wants a durable artifact, save exactly one plan to `outputs/` as markdown.
- End with a `Sources` section containing direct URLs for any external sources used.
