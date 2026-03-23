---
description: Set up a recurring or deferred research watch on a topic, company, paper area, or product surface.
---
Create a research watch for: $@

Requirements:
- Start with a baseline sweep of the topic using the strongest relevant sources.
- If the watch is about current events, products, markets, regulations, or releases, use `web_search` and `fetch_content` first.
- If the watch has a literature component, add `alpha_search` and inspect the strongest papers directly.
- Summarize what should be monitored, what signals matter, and what counts as a meaningful change.
- Use `schedule_prompt` to create the recurring or delayed follow-up instead of merely promising to check later.
- If the user wants detached execution for the initial sweep, use `subagent` in background mode and report how to inspect status.
- Save exactly one durable baseline artifact to `outputs/`.
- End with a `Sources` section containing direct URLs for every source used.
