"""Job-user matching: score how well a user fits a job based on keywords, roles, location, education."""

from __future__ import annotations

import json
from dataclasses import dataclass

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .config import USER_ID
from .db import get_job, get_jobs, get_user, update_job
from .models import Job, User

console = Console()


@dataclass
class MatchResult:
    job_id: int
    job_title: str
    company: str
    score: float  # 0.0 to 1.0
    keyword_overlap: list[str]
    role_match: list[str]
    location_match: bool
    education_match: bool | None  # None = can't determine
    reasons: list[str]


def _keyword_score(user_keywords: list[str], job_text: str) -> tuple[float, list[str]]:
    """Score keyword overlap between user and job description."""
    if not user_keywords or not job_text:
        return 0.0, []

    job_lower = job_text.lower()
    matched = [kw for kw in user_keywords if kw.lower() in job_lower]
    if not user_keywords:
        return 0.0, []
    score = len(matched) / max(len(user_keywords), 1)
    return min(score * 2.0, 1.0), matched  # Scale up, cap at 1.0


def _role_score(user_roles: list[str], job_role_types: list[str]) -> tuple[float, list[str]]:
    """Score role type overlap."""
    if not user_roles or not job_role_types:
        return 0.0, []

    matched = [r for r in user_roles if r in job_role_types]
    score = len(matched) / max(len(user_roles), 1)
    return score, matched


def _location_match(user_geolocation: str | None, job_location: str | None) -> bool:
    """Check if user location is compatible with job location."""
    if not user_geolocation or not job_location:
        return True  # Can't determine, assume compatible

    job_lower = job_location.lower()
    user_lower = user_geolocation.lower()

    # Remote is always compatible
    if "remote" in job_lower:
        return True

    # Check state/city overlap
    # Extract state abbreviation or city name
    user_parts = [p.strip().lower() for p in user_lower.replace(",", " ").split()]
    job_parts = [p.strip().lower() for p in job_lower.replace(",", " ").split()]

    # Check if any user location parts appear in job location
    for part in user_parts:
        if len(part) >= 2 and part in job_parts:
            return True

    # California variants
    ca_variants = {"ca", "california", "bay area", "sf", "san francisco", "berkeley", "palo alto"}
    user_in_ca = any(v in user_lower for v in ca_variants)
    job_in_ca = any(v in job_lower for v in ca_variants)

    if user_in_ca and job_in_ca:
        return True

    return False


def _education_match(user_skill_level: str, job_education_req: str | None) -> bool | None:
    """Check if user education level matches job requirement."""
    if not job_education_req:
        return None

    req_lower = job_education_req.lower()

    # Map skill levels to education compatibility
    level_map = {
        "internship": ["intern", "bachelor", "bs", "ba", "undergraduate", "student"],
        "entry-level": ["bachelor", "bs", "ba", "master", "ms"],
        "mid-level": ["bachelor", "bs", "ba", "master", "ms", "phd"],
        "senior": ["master", "ms", "phd", "doctorate"],
    }

    compatible_terms = level_map.get(user_skill_level, [])

    # If job requires PhD and user is internship level, flag it
    if "phd" in req_lower and user_skill_level in ("internship", "entry-level"):
        return False

    # If job mentions any compatible education level
    if any(term in req_lower for term in compatible_terms):
        return True

    # If "or equivalent" is mentioned, be lenient
    if "equivalent" in req_lower or "or related" in req_lower:
        return True

    return None


def match_job(user: User, job: Job) -> MatchResult:
    """Score how well a user matches a specific job."""
    reasons = []

    # Keyword matching (weight: 0.4)
    job_text = f"{job.title} {job.description or ''} {json.dumps(job.requirements)}"
    kw_score, kw_overlap = _keyword_score(user.keywords, job_text)

    # Role matching (weight: 0.3)
    role_score, role_overlap = _role_score(user.roles, job.role_types)

    # Location matching (weight: 0.15)
    loc_match = _location_match(user.geolocation, job.location)
    loc_score = 1.0 if loc_match else 0.2

    # Education matching (weight: 0.15)
    edu_match = _education_match(user.skill_level, job.education_req)
    if edu_match is True:
        edu_score = 1.0
    elif edu_match is False:
        edu_score = 0.1
        reasons.append(f"Education mismatch: requires {job.education_req}")
    else:
        edu_score = 0.5  # Can't determine

    # Weighted total
    total = (kw_score * 0.4) + (role_score * 0.3) + (loc_score * 0.15) + (edu_score * 0.15)

    # Build reasons
    if kw_overlap:
        reasons.append(f"Keywords matched: {', '.join(kw_overlap[:5])}")
    if role_overlap:
        reasons.append(f"Role match: {', '.join(role_overlap)}")
    if loc_match:
        reasons.append(f"Location compatible: {job.location}")
    if not loc_match:
        reasons.append(f"Location mismatch: {job.location} vs {user.geolocation}")

    return MatchResult(
        job_id=job.id or 0,
        job_title=job.title,
        company=job.company,
        score=round(total, 2),
        keyword_overlap=kw_overlap,
        role_match=role_overlap,
        location_match=loc_match,
        education_match=edu_match,
        reasons=reasons,
    )


def match_all_jobs(min_score: float = 0.2) -> list[MatchResult]:
    """Match user against all new jobs."""
    user = get_user(USER_ID)
    if not user:
        console.print("[red]No user profile found. Run 'auto-apply setup' first.[/red]")
        return []

    jobs = get_jobs(status="new")
    if not jobs:
        console.print("[yellow]No new jobs to match.[/yellow]")
        return []

    results = []
    for job in jobs:
        result = match_job(user, job)
        if result.score >= min_score:
            results.append(result)
            update_job(job.id, status="matched")

    # Sort by score descending
    results.sort(key=lambda r: r.score, reverse=True)

    return results


def display_matches(results: list[MatchResult]) -> None:
    """Display match results in a rich table."""
    if not results:
        console.print("[yellow]No matches found above threshold.[/yellow]")
        return

    table = Table(title=f"Job Matches ({len(results)})")
    table.add_column("ID", style="cyan")
    table.add_column("Score", style="bold green")
    table.add_column("Title")
    table.add_column("Company")
    table.add_column("Roles", style="yellow")
    table.add_column("Keywords Matched")
    table.add_column("Location")

    for r in results:
        score_style = "bold green" if r.score >= 0.6 else "yellow" if r.score >= 0.4 else "dim"
        table.add_row(
            str(r.job_id),
            f"[{score_style}]{r.score:.0%}[/{score_style}]",
            r.job_title,
            r.company,
            ", ".join(r.role_match) if r.role_match else "—",
            ", ".join(r.keyword_overlap[:4]) if r.keyword_overlap else "—",
            "Y" if r.location_match else "N",
        )

    console.print(table)

    # Summary
    avg_score = sum(r.score for r in results) / len(results)
    console.print(
        Panel(
            f"Matched: {len(results)} jobs\n"
            f"Average score: {avg_score:.0%}\n"
            f"Top match: {results[0].job_title} @ {results[0].company} ({results[0].score:.0%})",
            title="Match Summary",
            border_style="green",
        )
    )
