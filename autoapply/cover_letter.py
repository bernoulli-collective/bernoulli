"""Cover letter generation: builds prompts and writes draft letters for matched jobs."""

from __future__ import annotations

import json
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

from .config import DATA_DIR, DRAFTS_DIR, PENDING_DIR, RESULTS_DIR, USER_ID, ensure_dirs
from .db import get_job, get_user, insert_application, update_job
from .matching import MatchResult
from .models import Application, Job, User

console = Console()


def build_cover_letter_prompt(user: User, job: Job, match: MatchResult) -> str:
    """Build a structured prompt for cover letter generation.

    Modeled after the cold-email skill's four required elements,
    adapted for job applications.
    """
    # Determine pronoun usage for the letter
    pronoun_note = ""
    if user.pronouns:
        pronoun_note = f"\nApplicant uses {user.pronouns} pronouns."

    # Build the context section from matched keywords and roles
    keyword_context = ""
    if match.keyword_overlap:
        keyword_context = f"Relevant skills: {', '.join(match.keyword_overlap[:8])}"

    role_context = ""
    if match.role_match:
        role_context = f"Matching role types: {', '.join(match.role_match)}"

    # Get writing samples for style reference
    style_ref = ""
    if user.private_writing_samples:
        style_ref = (
            "\n\nStyle reference (past cover letters): "
            + ", ".join(user.private_writing_samples[:2])
        )

    prompt = f"""Generate a cover letter for this job application.

## Applicant Profile
- Name: {user.name}
- Email: {user.email or 'not provided'}
- Location: {user.geolocation or 'not provided'}
- Skill level: {user.skill_level}
- Target roles: {', '.join(user.roles) if user.roles else 'general'}
- Key skills: {', '.join(user.keywords[:15]) if user.keywords else 'see resume'}{pronoun_note}

## Job Details
- Title: {job.title}
- Company: {job.company}
- Location: {job.location or 'not specified'}
- Education requirement: {job.education_req or 'not specified'}
- Description: {job.description or 'not available'}

## Match Context
- Match score: {match.score:.0%}
- {keyword_context}
- {role_context}

## Cover Letter Requirements (modeled after cold-email best practices)

The cover letter MUST have these four elements:

1. **Opening** — One sentence: name, current position/affiliation, and purpose.
   ("My name is {user.name}. I am a {user.skill_level}-level candidate studying/working at [affiliation]. I am writing to express my interest in the {job.title} role at {job.company}.")

2. **Connection** — Specific, personal, researched. Name an exact project, product, or initiative at {job.company} and explain WHY it connects to the applicant's work. Generic praise signals a mass application.

3. **Evidence** — 2-3 bullet points of concrete accomplishments that directly map to the job requirements. Use numbers where possible. Draw from the applicant's keywords and background.

4. **Close** — Clear, bounded next step. State availability for interview, attach resume, and express enthusiasm without being sycophantic.

## Pitfalls to avoid
- Generic opening ("I am excited to apply...") — be specific about WHY this company
- Listing skills without context — always connect skill to a concrete project or result
- Being longer than one page — keep it concise, readable in 60 seconds
- Restating the resume — add NEW information about fit and motivation
- Ignoring the company's mission/product — show you researched them

## Format
- Plain text, no markdown formatting in the letter itself
- 3-4 paragraphs maximum
- Professional but not stiff — match the company's tone
- Under 300 words{style_ref}

## Output
Write ONLY the cover letter text. No headers, no metadata, no commentary."""

    return prompt


def generate_cover_letter_draft(
    user: User, job: Job, match: MatchResult
) -> str:
    """Generate a cover letter draft.

    For now, writes a pending request for the Pi agent to fulfill via LLM.
    Returns the path to the pending request file.
    """
    ensure_dirs()

    prompt = build_cover_letter_prompt(user, job, match)

    # Write pending request for Pi agent
    request = {
        "task": "generate_cover_letter",
        "job_id": job.id,
        "job_title": job.title,
        "company": job.company,
        "prompt": prompt,
        "output_file": str(DRAFTS_DIR / f"{job.id}-cover-letter.md"),
    }

    pending_file = PENDING_DIR / f"cover_letter_{job.id}.json"
    pending_file.write_text(json.dumps(request, indent=2))

    return str(pending_file)


def create_draft_application(
    user: User, job: Job, match: MatchResult
) -> int:
    """Create a draft application record and generate cover letter request."""
    ensure_dirs()

    # Generate cover letter request
    pending_path = generate_cover_letter_draft(user, job, match)

    # Check if a cover letter already exists from a prior run
    draft_path = DRAFTS_DIR / f"{job.id}-cover-letter.md"
    cover_letter_text = None
    if draft_path.exists():
        cover_letter_text = draft_path.read_text()

    # Create application record
    app = Application(
        job_id=job.id,
        user_id=user.id or USER_ID,
        cover_letter=cover_letter_text,
        cover_letter_path=str(draft_path),
        submission_mode="draft",
        status="draft",
        preview_md_path=str(DRAFTS_DIR / f"{job.id}-preview.md"),
    )

    app_id = insert_application(app)

    # Update job status
    update_job(job.id, status="drafting")

    console.print(
        f"[green]Draft created for {job.title} @ {job.company} (app_id={app_id})[/green]"
    )

    if cover_letter_text:
        console.print(f"[dim]Cover letter loaded from {draft_path}[/dim]")
    else:
        console.print(
            f"[yellow]Cover letter pending — Pi agent request at {pending_path}[/yellow]"
        )

    return app_id


def process_matches(matches: list[MatchResult]) -> list[int]:
    """Create draft applications for all matched jobs."""
    user = get_user(USER_ID)
    if not user:
        console.print("[red]No user profile found.[/red]")
        return []

    app_ids = []
    for match in matches:
        job = get_job(match.job_id)
        if not job:
            continue
        app_id = create_draft_application(user, job, match)
        app_ids.append(app_id)

    if app_ids:
        console.print(
            Panel(
                f"Created {len(app_ids)} draft applications.\n"
                f"Run 'auto-apply review' to preview drafts.",
                title="Drafts Ready",
                border_style="green",
            )
        )

    return app_ids
