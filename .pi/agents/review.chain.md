---
name: review
description: Gather evidence, verify claims, and simulate a peer review for an AI research artifact.
---

## researcher
output: research.md

Inspect the target paper, draft, code, cited work, and any linked experimental artifacts for {task}. Gather the strongest primary evidence that matters for a review.

## verifier
reads: research.md
output: verification.md

Audit research.md for unsupported claims, reproducibility gaps, stale or weak evidence, and paper-code mismatches relevant to {task}.

## reviewer
reads: research.md+verification.md
output: review.md
progress: true

Write the final simulated peer review for {task} using research.md and verification.md. Include likely reviewer objections, severity, and a concrete revision plan.
