---
description: Turn research findings into a polished paper-style draft with equations, sections, and explicit claims.
args: <topic>
section: Research Workflows
topLevelCli: true
---
Write a paper-style draft for: $@

Derive a short slug from the topic (lowercase, hyphens, no filler words, ≤5 words). Use this slug for all files in this run.

Requirements:
- Before writing, outline the draft structure: proposed title, sections, key claims to make, source material to draw from, and a verification log for the critical claims, figures, and calculations. Write the outline to `outputs/.plans/<slug>.md`. Present the outline to the user. If this is an unattended or one-shot run, continue automatically. If the user is actively interacting, give them a brief chance to request changes before proceeding.
- Use the `writer` subagent when the draft should be produced from already-collected notes, then use the `verifier` subagent to add inline citations and verify sources.
- Include at minimum: title, abstract, problem statement, related work, method or synthesis, evidence or experiments, limitations, conclusion.
- **Never invent experimental results, scores, figures, images, charts, tables, datasets, or benchmarks.** If no raw artifact, cited source, or prior research note provides the value, write a clearly labeled placeholder such as `TODO: run experiment` or `No experimental results are available yet` instead of fabricating plausible numbers.
- The `evidence or experiments` section must contain only one of:
  - cited results from primary sources,
  - results computed from explicit raw artifacts/scripts already present in the workspace,
  - a proposed experimental plan with no claimed outcomes.
- Every figure, chart, image, or table must have provenance in its caption: source URL, research-file reference, raw artifact path, or script path. If provenance is missing, omit the figure.
- Use clean Markdown with LaTeX where equations materially help.
- Generate charts with `pi-charts` only for quantitative data, benchmarks, and comparisons that already exist in the source material or raw artifacts. Use Mermaid for architectures and pipelines only when the structure is supported by sources. Every figure needs a provenance-bearing caption.
- Before delivery, sweep the draft for any claim that sounds stronger than its support. Mark tentative results as tentative and remove unsupported numerics instead of letting the verifier discover them later.
- Save exactly one draft to `papers/<slug>.md`.
- End with a `Sources` appendix with direct URLs for all primary references.
