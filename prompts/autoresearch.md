---
description: Turn a research idea into a paper-oriented end-to-end run with literature, hypotheses, experiments when possible, and a draft artifact.
---
Run an autoresearch workflow for: $@

Requirements:
- Prefer the project `auto` chain or the `planner` + `researcher` + `verifier` + `writer` subagents when the task is broad enough to benefit from decomposition.
- If the run is likely to take a while, or the user wants it detached, launch the subagent workflow in background with `clarify: false, async: true` and report how to inspect status.
- Start by clarifying the research objective, scope, and target contribution.
- Search for the strongest relevant primary sources first.
- If the topic is current, product-oriented, market-facing, or asks about latest developments, start with `web_search` and `fetch_content`.
- Use `alpha_search` for academic background or paper-centric parts of the topic, but do not rely on it alone for current topics.
- Build a compact evidence table before committing to a paper narrative.
- If experiments are feasible in the current environment, design and run the smallest experiment that materially reduces uncertainty.
- If experiments are not feasible, produce a paper-style draft that is explicit about missing validation and limitations.
- Produce one final durable markdown artifact for the user-facing result.
- If the result is a paper-style draft, save it to `papers/`; otherwise save it to `outputs/`.
- Do not create extra user-facing intermediate markdown files unless the user explicitly asks for them.
- End with a `Sources` section containing direct URLs for every source used.
