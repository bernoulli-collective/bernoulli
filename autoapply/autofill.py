"""Application Q&A auto-fill: generate answers to common application questions."""

from __future__ import annotations

import json
from pathlib import Path

from rich.console import Console

from .config import DRAFTS_DIR, PENDING_DIR, ensure_dirs
from .models import Job, User

console = Console()

# Common application questions and how to answer them from user data
COMMON_QUESTIONS = [
    {
        "question": "Why are you interested in this role?",
        "strategy": "Connect user's roles/keywords to job description. Reference specific company work.",
    },
    {
        "question": "What relevant experience do you have?",
        "strategy": "List top 3 keyword overlaps with concrete project examples from resume.",
    },
    {
        "question": "Why do you want to work at this company?",
        "strategy": "Reference company mission, recent news, specific product/research that connects to user's work.",
    },
    {
        "question": "What is your availability?",
        "strategy": "Based on skill_level: internship = summer/semester dates, entry = immediately, etc.",
    },
    {
        "question": "Are you authorized to work in the US?",
        "strategy": "Flag for user to answer manually — sensitive legal question.",
    },
    {
        "question": "What are your salary expectations?",
        "strategy": "Flag for user to answer manually — varies by role and location.",
    },
    {
        "question": "Tell us about a project you're proud of.",
        "strategy": "Select the most relevant project from user keywords that matches job description.",
    },
    {
        "question": "How did you hear about this position?",
        "strategy": "Based on job source: a16z portfolio, raised_and_hiring, etc.",
    },
]


def generate_autofill(user: User, job: Job, keyword_overlap: list[str]) -> dict:
    """Generate auto-fill answers for common application questions.

    Returns a dict mapping question → answer (or 'MANUAL' for sensitive questions).
    """
    answers = {}

    for q_template in COMMON_QUESTIONS:
        question = q_template["question"]
        strategy = q_template["strategy"]

        if "Flag for user" in strategy:
            answers[question] = "[MANUAL] — Please answer this question yourself."
            continue

        # Generate contextual answers based on user data and job
        if "interested in this role" in question.lower():
            role_text = ", ".join(user.roles[:2]) if user.roles else "research and engineering"
            answers[question] = (
                f"I am drawn to the {job.title} role because it aligns with my focus on {role_text}. "
                f"My experience with {', '.join(keyword_overlap[:3]) if keyword_overlap else 'relevant technologies'} "
                f"directly applies to the work at {job.company}."
            )

        elif "relevant experience" in question.lower():
            skills = keyword_overlap[:5] if keyword_overlap else user.keywords[:5]
            answers[question] = (
                f"I have hands-on experience with {', '.join(skills)}. "
                f"As a {user.skill_level}-level candidate, I have worked on projects spanning "
                f"{', '.join(user.roles[:2]) if user.roles else 'multiple technical domains'}."
            )

        elif "want to work at this company" in question.lower():
            source_note = ""
            if job.source == "raised_and_hiring":
                source_note = f" I noticed {job.company}'s recent funding round and growth trajectory."
            answers[question] = (
                f"I want to work at {job.company} because the {job.title} position "
                f"connects directly to my background in "
                f"{', '.join(user.roles[:2]) if user.roles else 'this domain'}.{source_note}"
            )

        elif "availability" in question.lower():
            availability_map = {
                "internship": "Available for summer 2026 or flexible semester-based schedule.",
                "entry-level": "Available to start immediately or within 2 weeks notice.",
                "mid-level": "Available with standard 2-4 weeks notice period.",
                "senior": "Available to discuss timeline based on project needs.",
            }
            answers[question] = availability_map.get(
                user.skill_level, "Available to discuss timing."
            )

        elif "project you're proud of" in question.lower():
            if keyword_overlap:
                answers[question] = (
                    f"[DRAFT] A project involving {keyword_overlap[0]} — "
                    f"please expand with specific details from your portfolio."
                )
            else:
                answers[question] = "[DRAFT] Please describe a relevant project."

        elif "hear about" in question.lower():
            source_map = {
                "a16z": "I found this position through the a16z portfolio jobs board.",
                "raised_and_hiring": f"I discovered {job.company} through recent funding news coverage.",
                "manual": "I found this position through my job search.",
                "scraped": "I found this position through an online job board.",
            }
            answers[question] = source_map.get(job.source, "Through my job search.")

    return answers


def save_autofill(job_id: int, answers: dict) -> Path:
    """Save autofill answers to a JSON file."""
    ensure_dirs()
    output_path = DRAFTS_DIR / f"{job_id}-autofill.json"
    output_path.write_text(json.dumps(answers, indent=2, ensure_ascii=False))
    return output_path
