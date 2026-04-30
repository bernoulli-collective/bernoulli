---
description: Find companies that recently raised funding from a given news source and are hiring in california.
args: <source-url-or-name>
section: Auto-Apply Workflows
topLevelCli: true
---
Find recently funded companies from this source: $@

## Sources

If the user provides a URL, navigate directly. If they provide a name, resolve to the default source:

- `techcrunch` or `techcrunch-startups` → `https://techcrunch.com/category/startups/`
- `crunchbase` or `crunchbase-news` → `https://news.crunchbase.com/`
- Any other URL → navigate directly

## Required steps

1. Navigate to the source URL
2. Scan recent articles (last month) for funding announcements
3. While less than 10 companies, for each article mentioning a funding round, extract:
   - **Company name** — exact name
   - **Location** - headquartered locations and include any locations in california. skip company is not in california
   - **Funding amount** — if stated (e.g. "$5M", "undisclosed")
   - **Round** — seed, Series A, B, C, etc.
   - **Company website** — if found in the article
   - **Career page** — Accepting a separte careers page, or welcome to join us message. if found in the article. skip company if not hiring. Try `{company}.com/careers`, `{company}.com/jobs`, greenhouse, ashby, etc.
   - **Article URL** — direct link
   - **Date** — publication date
4. Write results to `autoapply/data/raised_and_hiring.json` as a JSON array
5. Run the ingestion script to load results into SQLite:

```
uv run autoapply/ingest_raised.py autoapply/data/raised_and_hiring.json
```

6. Display a summary table from the script output

## Output format

```json
[
  {
    "company": "Company name",
    "locations": ["San Francisco, CA", "New York, NY"],
    "amount": "$5M",
    "round": "Seed",
    "website": "https://company.com",
    "career_page": "https://company.com/careers",
    "article_url": "https://techcrunch.com/...",
    "date": "2026-04-28"
  }
]
```

## Target

Aim for 5-10 recently funded companies. Do not stop after 1 or 2 — browse multiple pages of results if needed.
