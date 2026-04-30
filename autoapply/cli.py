"""CLI entrypoint for auto-apply workflow."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .config import AUTOAPPLY_DIR, ensure_dirs
from .db import init_db


def _cmd_setup(args: argparse.Namespace) -> None:
    from .setup import setup_user

    ensure_dirs()
    init_db()
    setup_user()


def _cmd_ingest(args: argparse.Namespace) -> None:
    from .ingest import ingest_a16z

    ensure_dirs()
    init_db()
    ingest_a16z(limit=args.limit)


def _cmd_match(args: argparse.Namespace) -> None:
    print("[auto-apply] match — coming in Phase 3")


def _cmd_review(args: argparse.Namespace) -> None:
    print("[auto-apply] review — coming in Phase 3")


def _cmd_list(args: argparse.Namespace) -> None:
    from .db import get_jobs
    from rich.console import Console
    from rich.table import Table

    ensure_dirs()
    init_db()
    jobs = get_jobs(status=args.status if args.status != "all" else None)
    console = Console()
    table = Table(title=f"Jobs ({len(jobs)})")
    table.add_column("ID", style="cyan")
    table.add_column("Title")
    table.add_column("Company")
    table.add_column("Location")
    table.add_column("Status", style="green")
    table.add_column("Source")
    for j in jobs:
        table.add_row(
            str(j.id),
            j.title,
            j.company,
            j.location or "—",
            j.status,
            j.source,
        )
    console.print(table)


def _cmd_status(args: argparse.Namespace) -> None:
    from .db import get_applications, get_jobs
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table

    ensure_dirs()
    init_db()
    console = Console()
    jobs = get_jobs()
    apps = get_applications()

    stats = {
        "total_jobs": len(jobs),
        "new": sum(1 for j in jobs if j.status == "new"),
        "matched": sum(1 for j in jobs if j.status == "matched"),
        "drafting": sum(1 for j in jobs if j.status == "drafting"),
        "ready": sum(1 for j in jobs if j.status == "ready"),
        "submitted": sum(1 for j in jobs if j.status == "submitted"),
        "total_applications": len(apps),
        "draft_apps": sum(1 for a in apps if a.status == "draft"),
        "submitted_apps": sum(1 for a in apps if a.status == "submitted"),
    }

    lines = [
        f"Jobs: {stats['total_jobs']} total",
        f"  new: {stats['new']}, matched: {stats['matched']}, drafting: {stats['drafting']}, ready: {stats['ready']}, submitted: {stats['submitted']}",
        f"Applications: {stats['total_applications']} total",
        f"  draft: {stats['draft_apps']}, submitted: {stats['submitted_apps']}",
    ]
    console.print(Panel("\n".join(lines), title="Auto-Apply Status"))


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="auto-apply",
        description="Automated job application pipeline",
    )
    parser.add_argument(
        "--db",
        type=str,
        default=None,
        help="Path to SQLite database",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # setup
    p_setup = subparsers.add_parser("setup", help="Configure user profile")
    p_setup.set_defaults(func=_cmd_setup)

    # ingest
    p_ingest = subparsers.add_parser("ingest", help="Scrape job listings")
    p_ingest.add_argument(
        "--limit",
        type=int,
        default=3,
        help="Max jobs to scrape (default: 3)",
    )
    p_ingest.set_defaults(func=_cmd_ingest)

    # match
    p_match = subparsers.add_parser("match", help="Match jobs and generate drafts")
    p_match.add_argument("--all", action="store_true", help="Process all new jobs")
    p_match.add_argument("--id", type=int, help="Process specific job ID")
    p_match.set_defaults(func=_cmd_match)

    # review
    p_review = subparsers.add_parser("review", help="Preview draft applications")
    p_review.add_argument("--id", type=int, help="Review specific application ID")
    p_review.set_defaults(func=_cmd_review)

    # list
    p_list = subparsers.add_parser("list", help="List jobs")
    p_list.add_argument(
        "--status",
        type=str,
        default="all",
        choices=["all", "new", "matched", "drafting", "ready", "submitted"],
        help="Filter by status",
    )
    p_list.set_defaults(func=_cmd_list)

    # status
    p_status = subparsers.add_parser("status", help="Show pipeline status")
    p_status.set_defaults(func=_cmd_status)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
