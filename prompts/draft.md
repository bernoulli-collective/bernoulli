---
description: Turn research findings into a polished paper-style draft with equations, sections, and explicit claims.
---
Write a paper-style draft for: $@

Requirements:
- Prefer the `writer` subagent when the draft should be produced from already-collected notes, and use `verifier` first if the evidence still looks shaky.
- Ground every claim in inspected sources, experiments, or explicit inference.
- Use clean Markdown structure with LaTeX where equations materially help.
- Include at minimum:
  - title
  - abstract
  - problem statement
  - related work
  - method or synthesis
  - evidence or experiments
  - limitations
  - conclusion
- If citations are available, include citation placeholders or references clearly enough to convert later.
- Add a `Sources` appendix with direct URLs for all primary references used while drafting.
- Save exactly one draft to `papers/` as markdown.
