---
name: cover-letter
description: Generate a tailored cover letter for a job application. Reads the pending request from autoapply/data/pending/, uses the applicant's profile and job context to produce a concise, specific letter. Modeled on cold-email best practices.
---

# Cover Letter

Generate a cover letter for a job application from a pending request file.

## Four required elements

Every cover letter must have all four (adapted from cold-email principles):

1. **Opening** — one sentence: name, current position/affiliation, and what you want. Direct, no filler.
   - Good: "My name is Yoyo Yuan. I am a physics student at Minerva University with research experience in neural interfaces. I am writing to apply for the [Role] at [Company]."
   - Bad: "I am excited to submit my application for..." (generic, says nothing)

2. **Connection** — specific, personal, researched. Name an exact project, paper, product, or initiative at the company and explain WHY it connects to your work.
   - Good: "Your team's work on low-latency neural decoding aligns with my experience building sub-$10 microelectrode arrays at Frontier Tower Neurotech."
   - Bad: "I am fascinated by your company's innovative work." (mass-application signal)

3. **Evidence** — 2-3 concrete accomplishments that map to the job requirements.
   - Use numbers (secured $30k+ funding, built 128-channel electrode patterns, coordinated with 3 engineers)
   - Connect each to a job requirement, not just a skill dump
   - Draw from the keyword overlap provided in the prompt

4. **Close** — clear next step. State what you're attaching, your availability, and one sentence of genuine (not sycophantic) enthusiasm.

## Pitfalls to flag and fix

- Generic opening → rewrite to be role-specific
- Listing skills without projects → always ground in a concrete experience
- Longer than 300 words → trim, the letter is a writing sample not a memoir
- Restating the resume → add motivation, fit reasoning, or new context
- Ignoring company mission → show you know what they do and why you care
- Wrong pronouns → check the applicant's stated pronouns

## Process

1. Read the pending request file from `autoapply/data/pending/cover_letter_<job_id>.json`
2. Extract the prompt, applicant profile, and job context
3. Generate the cover letter following the four elements above
4. Write the letter to `autoapply/data/drafts/<job_id>-cover-letter.md`
5. The letter should be plain text (no markdown headers), 3-4 paragraphs, under 300 words

## Output

Write only the cover letter text to the output file. No headers, no metadata, no review section in the file itself.
