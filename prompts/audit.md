---
description: Compare a paper's claims against its public codebase and identify mismatches, omissions, and reproducibility risks.
---
Audit the paper and codebase for: $@

Requirements:
- Prefer the `researcher` subagent for evidence gathering and the `verifier` subagent for the mismatch pass when the audit is non-trivial.
- Identify the canonical paper first with `alpha_search` and `alpha_get_paper`.
- Extract implementation-sensitive claims with `alpha_ask_paper`.
- If a public repo exists, inspect it with `alpha_read_code`.
- Compare claimed methods, defaults, metrics, and data handling against the repository.
- Call out missing code, mismatches, ambiguous defaults, and reproduction risks.
- End with a `Sources` section containing paper and repository URLs.
- Save exactly one audit artifact to `outputs/` as markdown.
