"""Job ingestion: scrape VC portfolio career pages, manual job lists."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .config import (
    DEFAULT_VC_FIRMS,
    PENDING_DIR,
    RESULTS_DIR,
    ensure_dirs,
)
from .db import get_vc_firm_id, insert_job, seed_vc_firms, update_job
from .models import Job

console = Console()


def ingest_a16z(limit: int = 3, firm_name: str = "a16z") -> None:
    """Ingest jobs from a VC firm's career page.

    Writes a pending request file for the Pi agent to execute browser scraping,
    then reads any existing results from a prior run.
    """
    ensure_dirs()
    seed_vc_firms()

    firm_careers_url = None
    for firm in DEFAULT_VC_FIRMS:
        if firm["name"] == firm_name:
            firm_careers_url = firm["careers_url"]
            break

    if firm_careers_url is None:
        console.print(f"[red]Unknown VC firm: {firm_name}[/red]")
        return

    vc_firm_id = get_vc_firm_id(firm_name)

    # Write pending request for Pi agent
    pending_file = PENDING_DIR / f"{firm_name}_scrape.json"
    pending_data = {
        "task": "scrape_jobs",
        "firm": firm_name,
        "url": firm_careers_url,
        "limit": limit,
        "output_file": str(RESULTS_DIR / f"{firm_name}_scrape.json"),
        "fields_to_extract": [
            "title",
            "company",
            "url",
            "apply_link",
            "description",
            "location",
            "education_req",
        ],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    pending_file.write_text(json.dumps(pending_data, indent=2))
    console.print(f"[yellow]Pending request written: {pending_file}[/yellow]")
    console.print(
        f"[yellow]Pi agent should navigate to {firm_careers_url} "
        f"and extract up to {limit} jobs[/yellow]"
    )

    # Check if results already exist from a prior run
    results_file = RESULTS_DIR / f"{firm_name}_scrape.json"
    if results_file.exists():
        jobs = _parse_results(results_file, vc_firm_id)
        _insert_jobs(jobs, firm_name)
        return

    console.print(
        Panel(
            f"No results file found at {results_file}\n\n"
            f"Run the Pi agent to scrape jobs, then re-run this command.\n"
            f"The agent should write job data to {results_file}",
            title="Awaiting Pi Agent",
            border_style="yellow",
        )
    )

    # Also show manual fallback
    console.print(
        "\nOr provide a manual job list as JSON:\n"
        "  autoapply/data/results/a16z_scrape.json\n"
        "  Format: [{\"title\": ..., \"company\": ..., \"url\": ..., ...}]"
    )


def ingest_manual(file_path: str) -> None:
    """Ingest jobs from a manual JSON file."""
    from .roles import match_role_type

    path = Path(file_path).expanduser().resolve()
    if not path.exists():
        console.print(f"[red]File not found: {path}[/red]")
        return

    with open(path) as f:
        raw = json.load(f)

    if not isinstance(raw, list):
        console.print("[red]Expected a JSON array of job objects[/red]")
        return

    jobs = []
    for item in raw:
        try:
            title = item.get("title", "")
            company = item.get("company", "")
            description = item.get("description", "")
            role_types = match_role_type(title, description)

            job = Job(
                title=title,
                company=company,
                url=item.get("url", ""),
                apply_link=item.get("apply_link"),
                source="manual",
                role_types=role_types,
                description=description,
                education_req=item.get("education_req"),
                location=item.get("location"),
                age_req=item.get("age_req"),
            )
            jobs.append(job)
        except Exception as e:
            console.print(f"[yellow]Skipping invalid entry: {e}[/yellow]")

    _insert_jobs(jobs, "manual")


def _parse_results(
    results_file: Path, vc_firm_id: int | None
) -> list[Job]:
    """Parse scraped results into Job objects."""
    from .roles import match_role_type

    with open(results_file) as f:
        raw = json.load(f)

    jobs = []
    for item in raw:
        try:
            title = item.get("title", "")
            company = item.get("company", "")
            url = item.get("url", "")
            description = item.get("description", "")
            role_types = match_role_type(title, description)

            job = Job(
                title=title,
                company=company,
                url=url,
                apply_link=item.get("apply_link"),
                source="a16z",
                vc_firm_id=vc_firm_id,
                description=description,
                role_types=role_types,
                education_req=item.get("education_req"),
                location=item.get("location"),
                age_req=item.get("age_req"),
            )
            if not job.title or not job.company or not job.url:
                console.print(f"[yellow]Skipping incomplete entry: {item}[/yellow]")
                continue
            jobs.append(job)
        except Exception as e:
            console.print(f"[yellow]Skipping invalid entry: {e}[/yellow]")

    return jobs


def _insert_jobs(jobs: list[Job], source: str) -> None:
    """Insert jobs into the database, skip duplicates."""
    inserted = 0
    skipped = 0
    new_jobs = []

    for job in jobs:
        if insert_job(job):
            inserted += 1
            new_jobs.append(job)
        else:
            skipped += 1

    console.print(
        Panel(
            f"Inserted: {inserted}\n"
            f"Skipped (duplicate): {skipped}\n"
            f"Total processed: {len(jobs)}",
            title=f"Jobs Ingested ({source})",
            border_style="green",
        )
    )

    if new_jobs:
        table = Table(title=f"New Jobs from {source}")
        table.add_column("ID", style="cyan")
        table.add_column("Title")
        table.add_column("Company")
        table.add_column("Location")
        table.add_column("Education")
        table.add_column("URL", max_width=50)
        for job in new_jobs:
            table.add_row(
                str(job.id or "—"),
                job.title,
                job.company,
                job.location or "—",
                job.education_req or "—",
                job.url[:60],
            )
        console.print(table)
