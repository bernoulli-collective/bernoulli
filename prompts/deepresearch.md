---
description: Run a thorough, source-heavy investigation on a topic and produce a durable research brief with explicit evidence and source links.
---
Run a deep research workflow for: $@

Requirements:
- Treat `/deepresearch` as one coherent Feynman workflow from the user's perspective. Do not expose internal orchestration primitives unless the user explicitly asks.
- Start as the lead researcher. First make a compact plan: what must be answered, what evidence types are needed, and which sub-questions are worth splitting out.
- Stay single-agent by default for narrow topics. Only use `subagent` when the task is broad enough that separate context windows materially improve breadth or speed.
- If you use subagents, launch them as one worker batch around clearly disjoint sub-questions. Wait for the batch to finish, synthesize the results, and only then decide whether a second batch is needed.
- Prefer breadth-first worker batches for deep research: different market segments, different source types, different time periods, different technical angles, or different competing explanations.
- Use `researcher` workers for evidence gathering, `verifier` workers for adversarial claim-checking, and `writer` only if you already have solid evidence and need help polishing the final artifact.
- Do not make the workflow chain-shaped by default. Hidden worker batches are optional implementation details, not the user-facing model.
- If the user wants it to run unattended, or the sweep will clearly take a while, prefer background execution with `subagent` using `clarify: false, async: true`, then report how to inspect status.
- If the topic is current, product-oriented, market-facing, regulatory, or asks about latest developments, start with `web_search` and `fetch_content`.
- If the topic has an academic literature component, use `alpha_search`, `alpha_get_paper`, and `alpha_ask_paper` for the strongest papers.
- Do not rely on a single source type when the topic spans both current reality and academic background.
- Build a compact evidence table before synthesizing conclusions.
- After synthesis, run a final verification/citation pass. For the strongest claims, independently confirm support and remove anything unsupported, fabricated, or stale.
- Distinguish clearly between established facts, plausible inferences, disagreements, and unresolved questions.
- Produce exactly one durable markdown artifact in `outputs/`.
- The final artifact should read like one deep research memo, not like stitched-together worker transcripts.
- Do not leave extra user-facing intermediate markdown files behind unless the user explicitly asks for them.
- End with a `Sources` section containing direct URLs for every source used.

Default execution shape:
1. Clarify the actual research objective if needed.
2. Make a short plan and identify the key sub-questions.
3. Decide single-agent versus worker-batch execution.
4. Gather evidence across the needed source types.
5. Synthesize findings and identify remaining gaps.
6. If needed, run one more worker batch for unresolved gaps.
7. Perform a verification/citation pass.
8. Write the final brief with a strict `Sources` section.
