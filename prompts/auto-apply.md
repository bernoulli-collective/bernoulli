---
description: Automated job application pipeline. Match jobs to user profile, generate cover letters, autofill Q&A, and preview drafts.
args: <subcommand>
section: Auto-Apply Workflows
topLevelCli: true
---
Run the auto-apply workflow: $@

## Overview

This workflow automates job applications by:
1. Matching ingested jobs against the user's profile (keywords, roles, location)
2. Generating tailored cover letters using the cover-letter skill
3. Auto-filling common application questions
4. Previewing all materials before submission (markdown first, then HTML)

## Subcommands

- `setup` — configure user profile from resume/portfolio
- `ingest` — scrape job listings from a16z or manual sources
- `match` — score jobs against user, create draft applications
- `review` — preview draft applications in terminal
- `list` — list all jobs and their status
- `status` — pipeline dashboard

## Pipeline execution

When the user runs `/auto-apply match`:

1. Load user profile from SQLite (keywords, roles, geolocation, skill level)
2. For each job with status='new':
   a. Score keyword overlap, role match, location, education
   b. If score >= threshold, mark as 'matched'
   c. Generate a cover letter prompt → write to `autoapply/data/pending/`
   d. Generate autofill answers → write to `autoapply/data/drafts/`
3. Process pending cover letter requests:
   - Read each `autoapply/data/pending/cover_letter_*.json`
   - Generate the cover letter using the prompt inside
   - Write result to `autoapply/data/drafts/<job_id>-cover-letter.md`
4. Display match results and draft summary

## Cover letter generation

For each pending cover letter request:
1. Read `autoapply/data/pending/cover_letter_<job_id>.json`
2. The `prompt` field contains the full generation instructions
3. Generate a cover letter following the cover-letter skill guidelines
4. Write ONLY the letter text (no metadata) to the `output_file` path specified in the request
5. Delete the pending file after successful generation

## When running review

For each draft application:
1. Display markdown preview in terminal (cover letter + autofill + links)
2. Save HTML preview to `autoapply/data/drafts/<job_id>-preview.html`
3. Show all files generated per application
4. Show the links that would be submitted (job URL, apply link, resume, portfolio, public links)

## Python CLI

The Python-side pipeline is invoked via:
```
uv run python -m autoapply.cli <subcommand> [options]
```

Available commands:
- `uv run python -m autoapply.cli setup`
- `uv run python -m autoapply.cli ingest [--limit N] [--file PATH]`
- `uv run python -m autoapply.cli match [--id N] [--min-score 0.2]`
- `uv run python -m autoapply.cli review [--id N]`
- `uv run python -m autoapply.cli list [--status STATUS]`
- `uv run python -m autoapply.cli status`
