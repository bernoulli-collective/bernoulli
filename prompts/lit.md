---
description: Run a literature review on a topic using paper search and primary-source synthesis.
args: <topic>
section: Research Workflows
topLevelCli: true
---
Investigate the following topic as a literature review: $@

Derive a short slug from the topic (lowercase, hyphens, no filler words, ≤5 words). Use this slug for all files in this run.

## Required artifacts

- Plan: `outputs/.plans/<slug>.md`
- Research notes: `notes/<slug>-research-*.md` (one per researcher pass; absent if you searched directly)
- Verification log: `notes/<slug>-verification.md`
- Final review: `outputs/<slug>.md`
- Provenance ledger: `outputs/<slug>.provenance.md`
- Optional figures: `outputs/<slug>-chart-*.{png|svg}`, `outputs/<slug>-diagram.{md|svg}`

`notes/<slug>-verification.md` is the in-process audit trail (task ledger, tool failures, reviewer/verifier verdicts, fix log). `outputs/<slug>.provenance.md` is the user-facing source ledger plus the final verification snapshot.

## Workflow

1. **Plan** — Outline the scope: key questions, source types to search (papers, web, repos), time period, expected sections, and a small task ledger. Write the plan to `outputs/.plans/<slug>.md` and create `notes/<slug>-verification.md` with the same task ledger marked `pending`. Briefly summarize the plan to the user and continue immediately. Do not ask for confirmation or wait for a proceed response unless the user explicitly requested plan review.

2. **Confirm paper-search availability** — Before searching, confirm `alpha` is reachable. If `alpha` returns `Not logged in` or any auth error, attempt `alpha login` once; if it still fails, fall back to `web_search` + `get_content` and record `paper-search: unavailable (<reason>)` at the top of `notes/<slug>-verification.md`. Mention this in the final review's `Review method and scope` section.

3. **Gather** — Use the `researcher` subagent when ≥10 sources are expected or the topic spans multiple subfields; otherwise search directly. Researcher outputs go to `notes/<slug>-research-*.md`; the lead agent never delegates the final synthesis. Update `notes/<slug>-verification.md` for every assigned question with `done`, `blocked`, or `superseded` — never silently skip. If `researcher` fails to spawn, perform the gather pass yourself, log the runtime failure, and proceed. Do not use bold, unless for subtitles.

4. **Synthesize** — Separate consensus, disagreements, and open questions. When useful, propose concrete next experiments or follow-up reading. If the review contains any cross-paper quantitative comparison, produce a `pi-charts` chart (`outputs/<slug>-chart-*.{png|svg}`); if it contains a taxonomy or method pipeline, produce a `pi-mermaid` diagram (`outputs/<slug>-diagram.{md|svg}`). If neither applies, record the omission in `notes/<slug>-verification.md` with a one-line justification. Before finishing the draft, sweep every strong claim against the verification log and downgrade anything that is inferred or single-source critical. Mark every claim as either primary-source (cited inline) or author synthesis (labelled as such — never as a "law").

5. **Cite** — Spawn the `verifier` agent to (i) add inline citations, (ii) verify every source URL resolves, (iii) confirm each numbered citation appears exactly once in the bibliography, and (iv) flag any source whose title or authors do not match the URL's actual page. Verifier writes findings to `notes/<slug>-verification.md`. If `verifier` fails to spawn or returns no findings, perform the same four checks yourself, log the runtime failure, and proceed.

6. **Review** — Spawn the `reviewer` agent to check the cited draft for unsupported claims, logical gaps, zombie sections, scope drift, and single-source critical findings. Fix all FATAL and MAJOR issues before delivering; only MINOR issues may be deferred to Open Questions. After fixes, run one more reviewer pass. Cap the loop at two reviewer passes total — if MAJOR issues remain after the second pass, deliver with them listed verbatim in Open Questions and recorded in `notes/<slug>-verification.md`. If `reviewer` fails to spawn, perform the same checks yourself and log the runtime failure.

7. **Deliver** — Save the final literature review to `outputs/<slug>.md`. Write `outputs/<slug>.provenance.md` listing: date, sources consulted vs. accepted vs. rejected, verification status, and intermediate research/notes files used. Before you stop, verify on disk that `outputs/<slug>.md`, `outputs/<slug>.provenance.md`, and `notes/<slug>-verification.md` all exist; do not stop at an intermediate cited draft alone.

8. **Register in database** — Run the following command (expand `<slug>` to the actual slug):

   ```
   python /Users/harvest/nova/bernoulli-db/log_output.py \
     --slug <slug> --type lit_review \
     --file-path outputs/<slug>.md \
     --note "notes/<slug>-research-*.md" research_sweep \
     --note "notes/<slug>-verification.md" verification
   ```

   If the script is not found or exits with an error, skip silently and append `db-registration: failed` to `outputs/<slug>.provenance.md`.
