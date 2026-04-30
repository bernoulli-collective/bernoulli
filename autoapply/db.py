"""SQLite database operations for auto-apply."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from .config import DB_PATH, ensure_dirs
from .models import Application, Job, User

_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id          INTEGER PRIMARY KEY,
    name        TEXT NOT NULL,
    email       TEXT,
    pronouns    TEXT,
    geolocation TEXT,
    skill_level TEXT DEFAULT 'internship',
    roles       TEXT DEFAULT '[]',
    keywords    TEXT DEFAULT '[]',
    resume_text TEXT,
    resume_path TEXT,
    portfolio_url TEXT,
    public_links TEXT DEFAULT '[]',
    writing_samples TEXT DEFAULT '[]',
    private_writing_samples TEXT DEFAULT '[]',
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS vc_firms (
    id              INTEGER PRIMARY KEY,
    name            TEXT NOT NULL,
    careers_url     TEXT NOT NULL,
    last_scraped_at DATETIME
);

CREATE TABLE IF NOT EXISTS jobs (
    id              INTEGER PRIMARY KEY,
    title           TEXT NOT NULL,
    company         TEXT NOT NULL,
    url             TEXT NOT NULL UNIQUE,
    apply_link      TEXT,
    source          TEXT DEFAULT 'scraped',
    vc_firm_id      INTEGER REFERENCES vc_firms(id),
    description     TEXT,
    requirements    TEXT DEFAULT '{}',
    role_types      TEXT DEFAULT '[]',
    education_req   TEXT,
    location        TEXT,
    age_req         TEXT,
    raw_html_path   TEXT,
    status          TEXT DEFAULT 'new',
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS applications (
    id                  INTEGER PRIMARY KEY,
    job_id              INTEGER REFERENCES jobs(id),
    user_id             INTEGER REFERENCES users(id),
    cover_letter        TEXT,
    cover_letter_path   TEXT,
    application_answers TEXT DEFAULT '{}',
    submission_mode     TEXT DEFAULT 'draft',
    status              TEXT DEFAULT 'draft',
    preview_md_path     TEXT,
    preview_html_path   TEXT,
    submitted_at        DATETIME,
    created_at          DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""


def _row_to_dict(row: sqlite3.Row | tuple, keys: list[str]) -> dict:
    return {k: v for k, v in zip(keys, row)}


def get_connection(db_path: Path | str | None = None) -> sqlite3.Connection:
    """Return a configured SQLite connection."""
    ensure_dirs()
    path = Path(db_path) if db_path else DB_PATH
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db(db_path: Path | str | None = None) -> None:
    """Create all tables if they don't exist."""
    conn = get_connection(db_path)
    try:
        conn.executescript(_SCHEMA)
        conn.commit()
    finally:
        conn.close()


# -- User operations --------------------------------------------------------


def upsert_user(user: User, db_path: Path | str | None = None) -> int:
    """Insert or replace the user record (single-user mode, id=1)."""
    import json

    conn = get_connection(db_path)
    try:
        conn.execute(
            """INSERT OR REPLACE INTO users
               (id, name, email, pronouns, geolocation, skill_level,
                roles, keywords, resume_text, resume_path, portfolio_url,
                public_links, writing_samples, private_writing_samples, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)""",
            (
                user.id or 1,
                user.name,
                user.email,
                user.pronouns,
                user.geolocation,
                user.skill_level,
                json.dumps(user.roles),
                json.dumps(user.keywords),
                user.resume_text,
                user.resume_path,
                user.portfolio_url,
                json.dumps(user.public_links),
                json.dumps(user.writing_samples),
                json.dumps(user.private_writing_samples),
            ),
        )
        conn.commit()
        return user.id or 1
    finally:
        conn.close()


def get_user(user_id: int = 1, db_path: Path | str | None = None) -> User | None:
    """Fetch a user by ID."""
    import json

    conn = get_connection(db_path)
    try:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        if row is None:
            return None
        d = dict(row)
        return User(
            id=d["id"],
            name=d["name"],
            email=d.get("email"),
            pronouns=d.get("pronouns"),
            geolocation=d.get("geolocation"),
            skill_level=d.get("skill_level", "internship"),
            roles=json.loads(d.get("roles") or "[]"),
            keywords=json.loads(d.get("keywords") or "[]"),
            resume_text=d.get("resume_text"),
            resume_path=d.get("resume_path"),
            portfolio_url=d.get("portfolio_url"),
            public_links=json.loads(d.get("public_links") or "[]"),
            writing_samples=json.loads(d.get("writing_samples") or "[]"),
            private_writing_samples=json.loads(d.get("private_writing_samples") or "[]"),
        )
    finally:
        conn.close()


# -- VC firm operations -----------------------------------------------------


def seed_vc_firms(db_path: Path | str | None = None) -> None:
    """Insert default VC firms if not already present."""
    from .config import DEFAULT_VC_FIRMS

    conn = get_connection(db_path)
    try:
        for firm in DEFAULT_VC_FIRMS:
            existing = conn.execute(
                "SELECT id FROM vc_firms WHERE name = ?", (firm["name"],)
            ).fetchone()
            if existing is None:
                conn.execute(
                    "INSERT INTO vc_firms (name, careers_url) VALUES (?, ?)",
                    (firm["name"], firm["careers_url"]),
                )
        conn.commit()
    finally:
        conn.close()


def get_vc_firm_id(name: str, db_path: Path | str | None = None) -> int | None:
    """Return the VC firm ID by name."""
    conn = get_connection(db_path)
    try:
        row = conn.execute(
            "SELECT id FROM vc_firms WHERE name = ?", (name,)
        ).fetchone()
        return row["id"] if row else None
    finally:
        conn.close()


# -- Job operations ---------------------------------------------------------


def insert_job(job: Job, db_path: Path | str | None = None) -> bool:
    """Insert a job; returns True if inserted, False if URL already exists."""
    import json

    conn = get_connection(db_path)
    try:
        conn.execute(
            """INSERT OR IGNORE INTO jobs
               (title, company, url, apply_link, source, vc_firm_id,
                description, requirements, role_types, education_req, location, age_req, raw_html_path)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                job.title,
                job.company,
                job.url,
                job.apply_link,
                job.source,
                job.vc_firm_id,
                job.description,
                json.dumps(job.requirements),
                json.dumps(job.role_types),
                job.education_req,
                job.location,
                job.age_req,
                job.raw_html_path,
            ),
        )
        inserted = conn.total_changes > 0
        conn.commit()
        return inserted
    finally:
        conn.close()


def update_job(job_id: int, db_path: Path | str | None = None, **kwargs) -> None:
    """Update job fields by ID."""
    import json

    if not kwargs:
        return
    set_clauses = []
    values = []
    for k, v in kwargs.items():
        if k in ("requirements",) and isinstance(v, (dict, list)):
            set_clauses.append(f"{k} = ?")
            values.append(json.dumps(v))
        else:
            set_clauses.append(f"{k} = ?")
            values.append(v)
    set_clauses.append("updated_at = CURRENT_TIMESTAMP")
    values.append(job_id)

    conn = get_connection(db_path)
    try:
        conn.execute(
            f"UPDATE jobs SET {', '.join(set_clauses)} WHERE id = ?", values
        )
        conn.commit()
    finally:
        conn.close()


def get_job(job_id: int, db_path: Path | str | None = None) -> Job | None:
    """Fetch a job by ID."""
    import json

    conn = get_connection(db_path)
    try:
        row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
        if row is None:
            return None
        d = dict(row)
        return Job(
            id=d["id"],
            title=d["title"],
            company=d["company"],
            url=d["url"],
            apply_link=d.get("apply_link"),
            source=d.get("source", "scraped"),
            vc_firm_id=d.get("vc_firm_id"),
            description=d.get("description"),
            requirements=json.loads(d.get("requirements") or "{}"),
            role_types=json.loads(d.get("role_types") or "[]"),
            education_req=d.get("education_req"),
            location=d.get("location"),
            age_req=d.get("age_req"),
            raw_html_path=d.get("raw_html_path"),
            status=d.get("status", "new"),
        )
    finally:
        conn.close()


def get_jobs(
    status: str | None = None, db_path: Path | str | None = None
) -> list[Job]:
    """Fetch jobs, optionally filtered by status."""
    import json

    conn = get_connection(db_path)
    try:
        if status:
            rows = conn.execute(
                "SELECT * FROM jobs WHERE status = ? ORDER BY created_at", (status,)
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM jobs ORDER BY created_at").fetchall()
        jobs = []
        for row in rows:
            d = dict(row)
            jobs.append(
                Job(
                    id=d["id"],
                    title=d["title"],
                    company=d["company"],
                    url=d["url"],
                    apply_link=d.get("apply_link"),
                    source=d.get("source", "scraped"),
                    vc_firm_id=d.get("vc_firm_id"),
                    description=d.get("description"),
                    requirements=json.loads(d.get("requirements") or "{}"),
                    role_types=json.loads(d.get("role_types") or "[]"),
                    education_req=d.get("education_req"),
                    location=d.get("location"),
                    age_req=d.get("age_req"),
                    raw_html_path=d.get("raw_html_path"),
                    status=d.get("status", "new"),
                )
            )
        return jobs
    finally:
        conn.close()


# -- Application operations -------------------------------------------------


def insert_application(
    app: Application, db_path: Path | str | None = None
) -> int:
    """Insert an application and return its ID."""
    import json

    conn = get_connection(db_path)
    try:
        cur = conn.execute(
            """INSERT INTO applications
               (job_id, user_id, cover_letter, cover_letter_path,
                application_answers, submission_mode, status,
                preview_md_path, preview_html_path)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                app.job_id,
                app.user_id,
                app.cover_letter,
                app.cover_letter_path,
                json.dumps(app.application_answers),
                app.submission_mode,
                app.status,
                app.preview_md_path,
                app.preview_html_path,
            ),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def update_application(
    app_id: int, db_path: Path | str | None = None, **kwargs
) -> None:
    """Update application fields by ID."""
    import json

    if not kwargs:
        return
    set_clauses = []
    values = []
    for k, v in kwargs.items():
        if k in ("application_answers",) and isinstance(v, (dict, list)):
            set_clauses.append(f"{k} = ?")
            values.append(json.dumps(v))
        elif k == "submitted_at" and v is True:
            set_clauses.append("submitted_at = CURRENT_TIMESTAMP")
        else:
            set_clauses.append(f"{k} = ?")
            values.append(v)
    set_clauses.append("updated_at = CURRENT_TIMESTAMP")
    values.append(app_id)

    conn = get_connection(db_path)
    try:
        conn.execute(
            f"UPDATE applications SET {', '.join(set_clauses)} WHERE id = ?", values
        )
        conn.commit()
    finally:
        conn.close()


def get_application(
    app_id: int, db_path: Path | str | None = None
) -> Application | None:
    """Fetch an application by ID."""
    import json

    conn = get_connection(db_path)
    try:
        row = conn.execute(
            "SELECT * FROM applications WHERE id = ?", (app_id,)
        ).fetchone()
        if row is None:
            return None
        d = dict(row)
        return Application(
            id=d["id"],
            job_id=d["job_id"],
            user_id=d["user_id"],
            cover_letter=d.get("cover_letter"),
            cover_letter_path=d.get("cover_letter_path"),
            application_answers=json.loads(d.get("application_answers") or "{}"),
            submission_mode=d.get("submission_mode", "draft"),
            status=d.get("status", "draft"),
            preview_md_path=d.get("preview_md_path"),
            preview_html_path=d.get("preview_html_path"),
        )
    finally:
        conn.close()


def get_applications(
    status: str | None = None,
    user_id: int | None = None,
    db_path: Path | str | None = None,
) -> list[Application]:
    """Fetch applications with optional filters."""
    import json

    conn = get_connection(db_path)
    try:
        query = "SELECT * FROM applications WHERE 1=1"
        params: list = []
        if status:
            query += " AND status = ?"
            params.append(status)
        if user_id is not None:
            query += " AND user_id = ?"
            params.append(user_id)
        query += " ORDER BY created_at"

        rows = conn.execute(query, params).fetchall()
        apps = []
        for row in rows:
            d = dict(row)
            apps.append(
                Application(
                    id=d["id"],
                    job_id=d["job_id"],
                    user_id=d["user_id"],
                    cover_letter=d.get("cover_letter"),
                    cover_letter_path=d.get("cover_letter_path"),
                    application_answers=json.loads(d.get("application_answers") or "{}"),
                    submission_mode=d.get("submission_mode", "draft"),
                    status=d.get("status", "draft"),
                    preview_md_path=d.get("preview_md_path"),
                    preview_html_path=d.get("preview_html_path"),
                )
            )
        return apps
    finally:
        conn.close()
