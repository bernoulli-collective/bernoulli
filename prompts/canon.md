---
description: Browse a researcher's or organization's entire publication canon using paper search and primary-source synthesis, characterizing the trajectory of their work.
args: <name-or-url>
section: Research Workflows
topLevelCli: true
---
Map the research canon of this researcher or organization: $@

Determine whether the input is a **lab**, **individual researcher**, or **organization** (company, institute, non-profit). This shapes how you locate publications and how you frame the output.

Derive a short slug from the name (lowercase, hyphens, ≤4 words). Use this slug for all files in this run.

This is an execution request. Go look around. Do not describe the protocol — carry it out.

## Required artifacts

- Plan: `outputs/.plans/<slug>.md`
- Publications log: `notes/<slug>-publications.md`
- Trajectory notes: `notes/<slug>-trajectories.md`
- Verification log: `notes/<slug>-verification.md`
- Canon map: `outputs/<slug>-canon.md`
- Optional concept diagram: `outputs/<slug>-canon-diagram.{png|svg|md}`

## 1. Locate the subject

Accept any of: personal name, lab name, organization name, institution + lab name, or website URL. Retrieval is the lead agent's job — do not delegate this step to a subagent.

**Individual researcher:** try in order until you have a publication list:
1. Personal or lab website (look for Publications, Papers, or Research page)
2. Google Scholar profile
3. arXiv author page
4. Semantic Scholar or OpenReview author search

**Organization (company, institute, non-profit):** try in order:
1. Official research or publications page
2. arXiv org search or institutional author cluster
3. Semantic Scholar institution page
4. Google Scholar search scoped to the org's domain

Log: `[canon] subject=<name> type=<researcher|lab|org> source=<url>`

Collect as many papers as reachable — aim for completeness over speed. Save the raw list (titles, years, venues, URLs/DOIs) to `notes/<slug>-publications.md`. Note any gaps (e.g., paywalled proceedings, pre-2010 work not indexed, blog posts or technical reports outside indexers).

## 2. Situate the subject

As a leading expert in this subject's domain, identify the top 3–5 topics they study. Describe their stance in one sentence.

Spawn the `researcher` subagent with output target `notes/<slug>-trajectories.md`. For each topic, the researcher writes about the TRAJECTORY of the research progress as a story and the RELATIONSHIP of prior art and this subject. Describe what the problem is, why it is challenging, and what people have done in this field to tackle the problem. Connect existing work into a clear research trajectory.

No one likes to read 1–2 pages of dense text. For each topic, add numbered paragraph titles so that it's easy to navigate. The paragraph title should summarize the following paragraph. For 3–5 topics, each 180–300 words.

**Subagent fallback.** If the `researcher` subagent fails to spawn or returns no usable file, complete the trajectory synthesis directly using the publications log, write the synthesis to `notes/<slug>-trajectories.md` yourself, and append a note to `notes/<slug>-verification.md` recording the runtime failure. The final canon map's Coverage gaps section must mention any synthesis that was not produced via subagent. Make sure to follow coding preferences: using python3 and uv.

## 3. Rank by originality

Identify the 3–5 most significant papers or outputs from this subject. List them with title, year, and URL/DOI in `notes/<slug>-trajectories.md` (or appended at the bottom of that file).

No "Author A did blah blah. Author B did blah blah." Focus on the work, not the people. Don't just describe, RELATE it. For each work, find ONE contrastive difference that separates it from others.

Do not trash prior work. Do not bold.

## 4. Diagram the concepts

Create a concept diagram with `pi-mermaid` showing how the subject's topics relate to each other and to anchoring prior art. Save it as `outputs/<slug>-canon-diagram.{png|svg|md}`.

Use `pi-charts` only when there are plottable quantitative comparisons across papers (e.g., citations per topic, sample sizes per study). For a concept map, default to mermaid.

## 5. Cite

Spawn the `verifier` agent to add inline citations and verify every source URL in the trajectory notes and the planned ranked papers list. Verifier output goes to `notes/<slug>-verification.md`. If `verifier` fails, perform the URL/citation pass yourself and record the runtime failure in the verification log.

## 6. Write the canon map

Synthesize `notes/<slug>-trajectories.md`, the ranked papers, and the verification log into the canonical artifact. Do not have any subagent write `outputs/<slug>-canon.md` directly — only the lead agent writes the final map.

Write `outputs/<slug>-canon.md`:

```markdown
# Research Canon: [Name]

**Type:** [Researcher | Lab | Organization]
**Affiliation / Institution:** [if applicable]
**Source:** [URL]
**Date:** [YYYY-MM-DD]

## In one sentence
[Step 2 one-liner]

## Topic trajectories
[3–5 topic sections, each 180–300 words, drawn from `notes/<slug>-trajectories.md`. Numbered paragraph titles.]

## Papers ranked by originality

### 1. [Paper title] ([year])
**Source:** [URL or DOI]
[2–3 sentence assessment, including the ONE contrastive difference]

### 2. ...

### 3. ...

## Coverage gaps
[Any journals, years, or proceedings not reachable, plus any subagent failures that forced lead-agent synthesis — or "none"]
```

## 7. Register in database

Run the following command (expand `<slug>` to the actual slug):

```
python /Users/harvest/nova/bernoulli-db/log_output.py \
  --slug <slug> --type lab_canon \
  --file-path outputs/<slug>-canon.md \
  --lab-slug <slug> \
  --note "notes/<slug>-publications.md" publications \
  --note "notes/<slug>-trajectories.md" trajectories \
  --note "notes/<slug>-verification.md" verification
```

If the script is not found or exits with an error, append `db-registration: failed` to `notes/<slug>-verification.md` and continue.

## 8. Offer next steps

After writing the canon map, list the top 3 papers with their source URLs and ask the user which ones to summarize now. For each confirmed paper, run `/summarize <url>` — the summary will appear at `outputs/<paper-slug>-summary.md` and can feed `/paper-outreach` if the user wants to contact the authors.

Before stopping, verify on disk that `outputs/<slug>-canon.md`, `notes/<slug>-publications.md`, `notes/<slug>-trajectories.md`, and `notes/<slug>-verification.md` exist. Never end with planning-only chat.
