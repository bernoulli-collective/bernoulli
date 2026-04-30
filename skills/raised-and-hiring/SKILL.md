---
name: funded-companies
description: Find companies that recently raised funding from a given news source. Use when the user wants to discover startups who just raised and may be hiring.
---

# Funded Companies

Browse the given news source URL to find recent funding announcements, extract company names, funding amounts, and links.

## Workflow

1. Navigate to the source URL (e.g. `https://techcrunch.com/category/startups/`)
2. Browse recent articles (last 7 days) looking for funding announcements
3. For each article that mentions a funding round, extract:
   - Company name
   - Funding amount (if stated)
   - Funding round (seed, Series A, B, etc.)
   - Company website URL (if found)
   - Article URL
   - Date
4. Write results to `autoapply/data/funded_companies.json`
5. Display a summary table in the terminal

## Output format

Write a JSON array to `autoapply/data/funded_companies.json`:

```json
[
  {
    "company": "Company name",
    "amount": "$5M",
    "round": "Seed",
    "website": "https://company.com",
    "article_url": "https://techcrunch.com/...",
    "date": "2026-04-28"
  }
]
```

## Default sources

- TechCrunch Startups: `https://techcrunch.com/category/startups/`
- Crunchbase News: `https://news.crunchbase.com/`

If the user does not specify a source, default to TechCrunch Startups.
