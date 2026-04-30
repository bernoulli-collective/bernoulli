"""Preview system: render draft applications as markdown and HTML for review."""

from __future__ import annotations

import json
from pathlib import Path

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from .config import DRAFTS_DIR, USER_ID, ensure_dirs
from .db import get_application, get_applications, get_job, get_user, update_application
from .models import Application, Job, User

console = Console()


def _render_draft_markdown(app: Application, job: Job, user: User) -> str:
    """Render a draft application as markdown."""
    lines = []

    lines.append(f"# Draft Application: {job.title} @ {job.company}")
    lines.append("")
    lines.append(f"**Applicant:** {user.name} ({user.pronouns or ''})")
    lines.append(f"**Job URL:** {job.url}")
    if job.apply_link:
        lines.append(f"**Apply Link:** {job.apply_link}")
    lines.append(f"**Location:** {job.location or 'Not specified'}")
    lines.append(f"**Education:** {job.education_req or 'Not specified'}")
    lines.append(f"**Status:** {app.status}")
    lines.append("")

    # Cover letter section
    lines.append("---")
    lines.append("")
    lines.append("## Cover Letter")
    lines.append("")
    if app.cover_letter:
        lines.append(app.cover_letter)
    else:
        lines.append("*Pending generation by Pi agent.*")
        cover_letter_path = Path(app.cover_letter_path) if app.cover_letter_path else None
        if cover_letter_path and cover_letter_path.exists():
            lines.append("")
            lines.append(cover_letter_path.read_text())
        else:
            lines.append("")
            lines.append(f"*Expected at: {app.cover_letter_path}*")
    lines.append("")

    # Autofill answers section
    lines.append("---")
    lines.append("")
    lines.append("## Application Answers")
    lines.append("")
    if app.application_answers:
        for question, answer in app.application_answers.items():
            lines.append(f"**Q: {question}**")
            lines.append(f"A: {answer}")
            lines.append("")
    else:
        autofill_path = DRAFTS_DIR / f"{job.id}-autofill.json"
        if autofill_path.exists():
            answers = json.loads(autofill_path.read_text())
            for question, answer in answers.items():
                lines.append(f"**Q: {question}**")
                lines.append(f"A: {answer}")
                lines.append("")
        else:
            lines.append("*No autofill answers generated yet.*")
    lines.append("")

    # Files generated
    lines.append("---")
    lines.append("")
    lines.append("## Generated Files")
    lines.append("")
    files = [
        (f"{job.id}-cover-letter.md", app.cover_letter_path),
        (f"{job.id}-autofill.json", str(DRAFTS_DIR / f"{job.id}-autofill.json")),
        (f"{job.id}-preview.md", app.preview_md_path),
    ]
    for label, path in files:
        exists = Path(path).exists() if path else False
        status = "exists" if exists else "pending"
        lines.append(f"- `{label}` — {status}")
    lines.append("")

    # Links to submit
    lines.append("---")
    lines.append("")
    lines.append("## Links for Submission")
    lines.append("")
    lines.append(f"- Job posting: {job.url}")
    if job.apply_link:
        lines.append(f"- Direct apply: {job.apply_link}")
    if user.resume_path:
        lines.append(f"- Resume: {user.resume_path}")
    if user.portfolio_url:
        lines.append(f"- Portfolio: {user.portfolio_url}")
    if user.public_links:
        for link in user.public_links:
            lines.append(f"- Public link: {link}")
    lines.append("")

    return "\n".join(lines)


def _render_html(markdown_content: str, job: Job) -> str:
    """Convert markdown to simple HTML for browser preview."""
    # Basic markdown to HTML conversion (no external dep needed)
    html_lines = [
        "<!DOCTYPE html>",
        "<html><head>",
        f"<title>Draft: {job.title} @ {job.company}</title>",
        "<style>",
        "body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; line-height: 1.6; }",
        "h1 { color: #1a1a1a; border-bottom: 2px solid #e0e0e0; padding-bottom: 8px; }",
        "h2 { color: #333; margin-top: 2em; }",
        "hr { border: none; border-top: 1px solid #e0e0e0; margin: 2em 0; }",
        "a { color: #0066cc; }",
        "code { background: #f5f5f5; padding: 2px 6px; border-radius: 3px; font-size: 0.9em; }",
        "strong { color: #1a1a1a; }",
        ".status-draft { color: #cc7700; font-weight: bold; }",
        ".status-pending { color: #666; font-style: italic; }",
        "</style>",
        "</head><body>",
    ]

    # Simple line-by-line conversion
    for line in markdown_content.split("\n"):
        if line.startswith("# "):
            html_lines.append(f"<h1>{line[2:]}</h1>")
        elif line.startswith("## "):
            html_lines.append(f"<h2>{line[3:]}</h2>")
        elif line.startswith("---"):
            html_lines.append("<hr>")
        elif line.startswith("- "):
            content = line[2:]
            # Convert markdown links
            import re
            content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', content)
            html_lines.append(f"<li>{content}</li>")
        elif line.startswith("**Q:"):
            html_lines.append(f"<p><strong>{line.strip('*')}</strong></p>")
        elif line.startswith("**"):
            content = line.strip("*")
            html_lines.append(f"<p><strong>{content}</strong></p>")
        elif line.startswith("*") and line.endswith("*"):
            content = line.strip("*")
            html_lines.append(f"<p><em class='status-pending'>{content}</em></p>")
        elif line.strip():
            html_lines.append(f"<p>{line}</p>")

    html_lines.append("</body></html>")
    return "\n".join(html_lines)


def preview_draft(app_id: int) -> None:
    """Preview a single draft application in the terminal."""
    app = get_application(app_id)
    if not app:
        console.print(f"[red]Application {app_id} not found.[/red]")
        return

    job = get_job(app.job_id)
    user = get_user(app.user_id)
    if not job or not user:
        console.print("[red]Job or user data missing.[/red]")
        return

    # Render markdown
    md_content = _render_draft_markdown(app, job, user)

    # Save markdown preview
    ensure_dirs()
    md_path = DRAFTS_DIR / f"{job.id}-preview.md"
    md_path.write_text(md_content)
    update_application(app_id, preview_md_path=str(md_path))

    # Display in terminal
    console.print(Markdown(md_content))
    console.print(f"\n[dim]Markdown saved: {md_path}[/dim]")

    # Save HTML preview
    html_content = _render_html(md_content, job)
    html_path = DRAFTS_DIR / f"{job.id}-preview.html"
    html_path.write_text(html_content)
    update_application(app_id, preview_html_path=str(html_path))
    console.print(f"[dim]HTML saved: {html_path}[/dim]")


def preview_all_drafts() -> None:
    """Preview all pending draft applications."""
    apps = get_applications(status="draft")
    if not apps:
        console.print("[yellow]No draft applications to review.[/yellow]")
        return

    user = get_user(USER_ID)
    if not user:
        console.print("[red]No user profile found.[/red]")
        return

    console.print(
        Panel(
            f"Draft Applications: {len(apps)} pending review",
            border_style="blue",
        )
    )

    # Summary table
    table = Table(title="Pending Drafts")
    table.add_column("App ID", style="cyan")
    table.add_column("Job Title")
    table.add_column("Company")
    table.add_column("Cover Letter")
    table.add_column("Autofill")
    table.add_column("Files")

    for app in apps:
        job = get_job(app.job_id)
        if not job:
            continue

        cl_status = "ready" if app.cover_letter else "pending"
        autofill_path = DRAFTS_DIR / f"{job.id}-autofill.json"
        af_status = "ready" if autofill_path.exists() else "pending"

        files = []
        for fname in [
            f"{job.id}-cover-letter.md",
            f"{job.id}-autofill.json",
            f"{job.id}-preview.md",
            f"{job.id}-preview.html",
        ]:
            if (DRAFTS_DIR / fname).exists():
                files.append(fname)

        table.add_row(
            str(app.id),
            job.title,
            job.company,
            f"[green]{cl_status}[/green]" if cl_status == "ready" else f"[yellow]{cl_status}[/yellow]",
            f"[green]{af_status}[/green]" if af_status == "ready" else f"[yellow]{af_status}[/yellow]",
            "\n".join(files) if files else "—",
        )

    console.print(table)

    # Show each draft
    for app in apps:
        console.print("")
        preview_draft(app.id)
        console.print("")
