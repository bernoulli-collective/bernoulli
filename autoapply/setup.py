"""User profile setup: resume parsing, portfolio, links, writing samples."""

from __future__ import annotations

import json
from pathlib import Path

from pypdf import PdfReader
from rich.console import Console
from rich.panel import Panel

from .config import USER_ID, ensure_dirs
from .db import get_user, upsert_user
from .models import User

console = Console()


def _extract_resume_text(pdf_path: str) -> str:
    """Extract text from a PDF resume."""
    reader = PdfReader(pdf_path)
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text)
    return "\n\n".join(pages)


def _prompt_path(prompt: str) -> Path | None:
    """Prompt for a file path and validate it exists."""
    path = input(prompt).strip()
    if not path:
        return None
    p = Path(path).expanduser().resolve()
    if not p.exists():
        console.print(f"[red]File not found: {p}[/red]")
        return None
    return p


def _prompt_url(prompt: str) -> str | None:
    """Prompt for a URL."""
    url = input(prompt).strip()
    if not url:
        return None
    return url


def _prompt_list(prompt: str) -> list[str]:
    """Prompt for a comma-separated list."""
    raw = input(prompt).strip()
    if not raw:
        return []
    return [item.strip() for item in raw.split(",") if item.strip()]


def setup_user() -> None:
    """Interactive user profile setup."""
    ensure_dirs()

    existing = get_user(USER_ID)
    if existing:
        console.print(
            Panel(
                f"Existing profile found: [bold]{existing.name}[/bold]\n"
                f"Skill level: {existing.skill_level}\n"
                f"Resume: {existing.resume_path or 'not set'}\n"
                f"Portfolio: {existing.portfolio_url or 'not set'}\n"
                f"Public links: {len(existing.public_links)}\n"
                f"Writing samples: {len(existing.writing_samples)}\n"
                f"Private samples: {len(existing.private_writing_samples)}",
                title="Current Profile",
                border_style="yellow",
            )
        )
        overwrite = input("\nOverwrite? [y/N] ").strip().lower()
        if overwrite != "y":
            console.print("[dim]Keeping existing profile.[/dim]")
            return

    console.print(Panel("User Profile Setup", border_style="blue"))

    # Name
    name = input("Name: ").strip()
    if not name:
        console.print("[red]Name is required.[/red]")
        return

    # Email
    email = input("Email: ").strip() or None

    # Skill level
    console.print("\nTarget skill level:")
    console.print("[dim]  internship, entry-level, mid-level, senior[/dim]")
    skill_level = input("  Level (default: internship): ").strip().lower()
    if not skill_level:
        skill_level = "internship"

    # Resume
    resume_path: Path | None = None
    resume_text: str | None = None
    console.print("\nResume (PDF):")
    while True:
        rp = _prompt_path("  Path to resume PDF (or Enter to skip): ")
        if rp is None:
            break
        if not rp.suffix.lower() == ".pdf":
            console.print("[red]Please provide a PDF file.[/red]")
            continue
        resume_path = rp
        try:
            resume_text = _extract_resume_text(str(rp))
            word_count = len(resume_text.split())
            console.print(f"[green]Extracted {word_count} words from resume.[/green]")
            break
        except Exception as e:
            console.print(f"[red]Failed to parse PDF: {e}[/red]")
            resume_path = None
            resume_text = None

    # Portfolio URL
    portfolio_url = _prompt_url("Portfolio URL (or Enter to skip): ")

    # Public links
    console.print("\nPublic links (comma-separated):")
    console.print("[dim]  e.g. GitHub, LinkedIn, blog, Twitter[/dim]")
    public_links = _prompt_list("  URLs: ")

    # Writing samples
    console.print("\nPublic writing samples (file paths, comma-separated):")
    console.print("[dim]  e.g. blog posts, essays, published articles[/dim]")
    writing_raw = input("  Paths: ").strip()
    writing_samples = []
    if writing_raw:
        for p in writing_raw.split(","):
            p = p.strip()
            if p:
                fp = Path(p).expanduser().resolve()
                if fp.exists():
                    writing_samples.append(str(fp))
                else:
                    console.print(f"[yellow]Skipping missing file: {fp}[/yellow]")

    # Private writing samples
    console.print("\nPrivate writing samples (for zero-shot cover letters):")
    console.print("[dim]  e.g. past cover letters, application essays[/dim]")
    private_raw = input("  Paths: ").strip()
    private_writing_samples = []
    if private_raw:
        for p in private_raw.split(","):
            p = p.strip()
            if p:
                fp = Path(p).expanduser().resolve()
                if fp.exists():
                    private_writing_samples.append(str(fp))
                else:
                    console.print(f"[yellow]Skipping missing file: {fp}[/yellow]")

    user = User(
        id=USER_ID,
        name=name,
        email=email,
        skill_level=skill_level,
        resume_text=resume_text,
        resume_path=str(resume_path) if resume_path else None,
        portfolio_url=portfolio_url,
        public_links=public_links,
        writing_samples=writing_samples,
        private_writing_samples=private_writing_samples,
    )

    uid = upsert_user(user)
    console.print(
        Panel(
            f"Profile saved (user id={uid})\n"
            f"Skill level: {user.skill_level}\n"
            f"Resume: {user.resume_path or 'not set'}\n"
            f"Portfolio: {user.portfolio_url or 'not set'}\n"
            f"Public links: {len(public_links)}\n"
            f"Writing samples: {len(writing_samples)}\n"
            f"Private samples: {len(private_writing_samples)}",
            title="Setup Complete",
            border_style="green",
        )
    )
