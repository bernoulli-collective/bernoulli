"""Ingest raised-and-hiring JSON into SQLite database."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from .config import ensure_dirs
from .db import get_vc_firm_id, insert_job, seed_vc_firms
from .models import Job

FUNDING_VC_NAME = "Funding Source"


def ingest_raised_and_hiring(json_path: str) -> None:
    """Read raised_and_hiring.json and insert career page URLs as jobs to watch."""
    from rich.console import Console

    console = Console()
    path = Path(json_path).expanduser().resolve()
    if not path.exists():
        console.print(f"[red]File not found: {path}[/red]")
        return

    with open(path) as f:
        raw = json.load(f)

    if not isinstance(raw, list):
        console.print("[red]Expected a JSON array[/red]")
        return

    ensure_dirs()
    seed_vc_firms()

    # Register the funding source as a pseudo-VC firm
    conn = None
    vc_firm_id = None
    try:
        from .db import get_connection

        conn = get_connection()
        existing = conn.execute(
            "SELECT id FROM vc_firms WHERE name = ?", (FUNDING_VC_NAME,)
        ).fetchone()
        if existing is None:
            conn.execute(
                "INSERT INTO vc_firms (name, careers_url) VALUES (?, ?)",
                (FUNDING_VC_NAME, "n/a"),
            )
            conn.commit()
        row = conn.execute(
            "SELECT id FROM vc_firms WHERE name = ?", (FUNDING_VC_NAME,)
        ).fetchone()
        vc_firm_id = row["id"] if row else None
    finally:
        if conn:
            conn.close()

    inserted = 0
    for item in raw:
        company = item.get("company", "")
        career_page = item.get("career_page")
        if not company or not career_page:
            console.print(f"[yellow]Skipping {company}: no career page[/yellow]")
            continue

        url = career_page
        locations = item.get("locations", [])
        description = (
            f"Recently funded: {item.get('amount', 'undisclosed')} {item.get('round', '')} "
            f"on {item.get('date', 'unknown')}. "
            f"Source: {item.get('article_url', '')}"
        )

        job = Job(
            title=f"Career Page — {company}",
            company=company,
            url=url,
            apply_link=None,
            source="raised_and_hiring",
            vc_firm_id=vc_firm_id,
            description=description,
            location=", ".join(locations) if locations else None,
            role_types=[],
        )

        if insert_job(job):
            inserted += 1
            console.print(f"[green]+ {company}: {url}[/green]")
        else:
            console.print(f"[dim]~ {company}: already tracked[/dim]")

    console.print(f"\n[dark_sea_green3]Ingested {inserted} new career pages[/dark_sea_green3]")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Ingest raised-and-hiring companies into SQLite"
    )
    parser.add_argument(
        "json_path",
        nargs="?",
        default="autoapply/data/raised_and_hiring.json",
        help="Path to raised_and_hiring.json",
    )
    args = parser.parse_args()
    ingest_raised_and_hiring(args.json_path)


if __name__ == "__main__":
    main()
