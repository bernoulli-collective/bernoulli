---
description: Turn reviewer comments into a structured rebuttal and revision plan for an AI research paper.
---
Prepare a rebuttal workflow for: $@

Requirements:
- If reviewer comments are provided, organize them into a response matrix.
- If reviewer comments are not yet provided, infer the likely strongest objections from the current draft and review them before drafting responses.
- Prefer the `reviewer` subagent or the project `review` chain when fresh critical review is still needed.
- For each issue, produce:
  - reviewer concern
  - whether it is valid
  - evidence available now
  - paper changes needed
  - rebuttal language
- Do not overclaim fixes that have not been implemented.
- Save exactly one rebuttal matrix to `outputs/` as markdown.
- End with a `Sources` section containing direct URLs for all inspected external sources.
