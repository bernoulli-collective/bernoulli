---
description: Simulate an AI research peer review with likely objections, severity, and a concrete revision plan.
---
Review this AI research artifact: $@

Requirements:
- Prefer the project `review` chain or the `researcher` + `verifier` + `reviewer` subagents when the artifact is large or the review needs to inspect paper, code, and experiments together.
- Inspect the strongest relevant sources directly before making strong review claims.
- If the artifact is a paper or draft, evaluate:
  - novelty and related-work positioning
  - clarity of claims
  - baseline fairness
  - evaluation design
  - missing ablations
  - reproducibility details
  - whether conclusions outrun the evidence
- If code or experiment artifacts exist, compare them against the claimed method and evaluation.
- Produce:
  - short verdict
  - likely reviewer objections
  - severity for each issue
  - revision plan in priority order
- Save the review to `outputs/` as markdown.
- End with a `Sources` section containing direct URLs for every inspected external source.
