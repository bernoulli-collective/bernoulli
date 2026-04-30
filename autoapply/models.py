"""Pydantic models for users, jobs, and applications."""

from __future__ import annotations

from pydantic import BaseModel, Field


class User(BaseModel):
    id: int | None = None
    name: str
    email: str | None = None
    pronouns: str | None = None
    geolocation: str | None = None
    skill_level: str = "internship"
    roles: list[str] = Field(default_factory=list)  # e.g., ["AI and ML Engineering", "Research Engineering"]
    keywords: list[str] = Field(default_factory=list)  # extracted from resume, portfolio, writing samples
    resume_text: str | None = None  # optional, may be omitted if keywords are sufficient
    resume_path: str | None = None
    portfolio_url: str | None = None
    public_links: list[str] = Field(default_factory=list)
    writing_samples: list[str] = Field(default_factory=list)
    private_writing_samples: list[str] = Field(default_factory=list)


class Job(BaseModel):
    id: int | None = None
    title: str
    company: str
    url: str
    apply_link: str | None = None
    source: str = "scraped"
    vc_firm_id: int | None = None
    description: str | None = None
    requirements: dict = Field(default_factory=dict)
    role_types: list[str] = Field(default_factory=list)
    education_req: str | None = None
    location: str | None = None
    age_req: str | None = None
    raw_html_path: str | None = None
    status: str = "new"


class Application(BaseModel):
    id: int | None = None
    job_id: int
    user_id: int
    cover_letter: str | None = None
    cover_letter_path: str | None = None
    application_answers: dict = Field(default_factory=dict)
    submission_mode: str = "draft"
    status: str = "draft"
    preview_md_path: str | None = None
    preview_html_path: str | None = None
