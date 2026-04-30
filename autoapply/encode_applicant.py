"""Applicant encoder: extract structured data from resume, portfolio, and writing samples."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pypdf
from rich.console import Console
from rich.panel import Panel

from .config import DATA_DIR
from .models import User

console = Console()


def extract_keywords_from_text(text: str) -> list[str]:
    """Extract technical keywords from text."""
    # Common technical keywords patterns
    tech_patterns = [
        r'\b(?:python|java|javascript|typescript|c\+\+|c#|rust|go|matlab|r)\b',
        r'\b(?:machine learning|deep learning|neural network|ai|artificial intelligence)\b',
        r'\b(?:nlp|natural language processing|computer vision|llm|large language model)\b',
        r'\b(?:pytorch|tensorflow|keras|scikit-learn|pandas|numpy|scipy)\b',
        r'\b(?:eeg|ecog|emg|neural signal|brain computer interface|bci)\b',
        r'\b(?:signal processing|filtering|fft|wavelet|spectral analysis)\b',
        r'\b(?:reinforcement learning|supervised learning|unsupervised learning)\b',
        r'\b(?:data analysis|data science|statistics|regression|classification)\b',
        r'\b(?:robotics|control system|pid control|kalman filter)\b',
        r'\b(?:version control|git|docker|kubernetes|aws|cloud computing)\b',
    ]

    keywords = set()
    text_lower = text.lower()

    for pattern in tech_patterns:
        matches = re.findall(pattern, text_lower, re.IGNORECASE)
        keywords.update(matches)

    # Also extract capitalized acronyms and technical terms
    acronym_pattern = r'\b[A-Z]{2,}(?:[0-9]+)?\b'
    acronyms = re.findall(acronym_pattern, text)
    keywords.update(acronyms)

    return sorted(list(keywords))


def extract_equation_requirements(text: str) -> str | None:
    """Extract mathematical/equation requirements from text."""
    math_patterns = [
        r'(?:familiarity with|knowledge of|understanding of|experience with)\s+'
        r'(?:differential equations?|partial differential equations?|pde)',
        r'(?:familiarity with|knowledge of|understanding of|experience with)\s+'
        r'(?:linear algebra|matrix|vector|eigenvalue)',
        r'(?:familiarity with|knowledge of|understanding of|experience with)\s+'
        r'(?:probability|statistics|bayesian|markov)',
        r'(?:familiarity with|knowledge of|understanding of|experience with)\s+'
        r'(?:calculus|integration|differentiation|ode)',
        r'(?:must know|required|preferred|advantageous)\s+'
        r'(?:differential equations?|linear algebra|probability|statistics|calculus)',
    ]

    requirements = []
    text_lower = text.lower()

    for pattern in math_patterns:
        matches = re.findall(pattern, text_lower, re.IGNORECASE)
        if matches:
            # Clean up the matches
            for match in matches:
                clean_match = re.sub(
                    r'(?:familiarity with|knowledge of|understanding of|experience with|must know|required|preferred|advantageous)\s+',
                    '',
                    match,
                    flags=re.IGNORECASE,
                ).strip()
                if clean_match:
                    requirements.append(clean_match)

    if requirements:
        # Deduplicate and join
        unique_reqs = list(dict.fromkeys(requirements))
        return ", ".join(unique_reqs).capitalize() + "."

    return None


def extract_roles_from_keywords(keywords: list[str]) -> list[str]:
    """Map keywords to role types."""
    role_mapping = {
        "AI and ML Engineering": [
            "machine learning", "deep learning", "neural network", "ai", "artificial intelligence",
            "nlp", "natural language processing", "computer vision", "llm", "large language model",
            "pytorch", "tensorflow", "keras", "reinforcement learning", "supervised learning",
            "unsupervised learning", "data analysis", "data science", "statistics"
        ],
        "Research Engineering": [
            "research", "experimental", "prototype", "hypothesis", "experiment", "investigation",
            "applied research", "research engineer", "applied scientist"
        ],
        "Neuro Engineering": [
            "eeg", "ecog", "emg", "neural signal", "brain computer interface", "bci",
            "neural decoding", "neural encoding", "spike sorting", "electrophysiology",
            "neurotechnology", "neuroscience", "brain", "neuron"
        ],
    }

    matched_roles = set()
    keywords_lower = [k.lower() for k in keywords]

    for role, role_keywords in role_mapping.items():
        if any(kw in keywords_lower for kw in role_keywords):
            matched_roles.add(role)

    # If no specific roles matched but we have technical keywords, default to Research Engineering
    if not matched_roles and keywords:
        matched_roles.add("Research Engineering")

    return sorted(list(matched_roles))


def process_resume(resume_path: str) -> dict[str, Any]:
    """Extract text and metadata from resume PDF."""
    result = {
        "resume_text": "",
        "keywords": [],
        "equation_requirement": None,
    }

    if not resume_path:
        return result

    path = Path(resume_path).expanduser()
    if not path.exists():
        console.print(f"[yellow]Resume file not found: {path}[/yellow]")
        return result

    try:
        reader = pypdf.PdfReader(str(path))
        text_parts = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)

        full_text = "\n\n".join(text_parts)
        result["resume_text"] = full_text
        result["keywords"] = extract_keywords_from_text(full_text)
        result["equation_requirement"] = extract_equation_requirements(full_text)

        console.print(
            f"[green]Extracted {len(result['keywords'])} keywords from resume[/green]"
        )
        if result["equation_requirement"]:
            console.print(
                f"[dim]Equation requirement: {result['equation_requirement']}[/dim]"
            )

    except Exception as e:
        console.print(f"[red]Error processing resume: {e}[/red]")

    return result


def process_writing_samples(writing_samples: list[str]) -> list[str]:
    """Extract keywords from writing sample descriptions/URLs."""
    keywords = set()

    for sample in writing_samples:
        # Extract keywords from URLs or descriptions
        if isinstance(sample, str):
            # Look for technical terms in the URL/path
            sample_lower = sample.lower()
            tech_terms = [
                "neural", "brain", "eeg", "ai", "ml", "machine learning", "data",
                "algorithm", "model", "analysis", "research", "signal"
            ]
            for term in tech_terms:
                if term in sample_lower:
                    keywords.add(term)

    return sorted(list(keywords))


def encode_applicant(base_json_path: str) -> User:
    """Load base applicant JSON and enrich with extracted data."""
    path = Path(base_json_path).expanduser()
    if not path.exists():
        raise FileNotFoundError(f"Applicant JSON not found: {path}")

    with open(path) as f:
        base_data = json.load(f)

    # Start with base data
    user_data = {
        "id": base_data.get("id", 1),
        "name": base_data.get("name", ""),
        "email": base_data.get("email"),
        "pronouns": base_data.get("pronouns"),
        "geolocation": base_data.get("geolocation"),
        "skill_level": base_data.get("skill_level", "internship"),
        "equation_requirement": None,  # Will be extracted from resume
        "roles": base_data.get("roles", []),
        "keywords": base_data.get("keywords", []),
        "resume_text": base_data.get("resume_text"),
        "resume_path": base_data.get("resume_path"),
        "portfolio_url": base_data.get("portfolio_url"),
        "public_links": base_data.get("public_links", []),
        "writing_samples": base_data.get("writing_samples", []),
        "private_writing_samples": base_data.get("private_writing_samples", []),
    }

    # Process resume if available
    resume_path = user_data.get("resume_path")
    if resume_path:
        resume_data = process_resume(resume_path)
        # Merge resume data, preferring extracted values when base is empty/not set
        if resume_data["resume_text"]:
            user_data["resume_text"] = resume_data["resume_text"]

        # Merge keywords
        resume_keywords = set(resume_data["keywords"])
        existing_keywords = set(user_data["keywords"])
        user_data["keywords"] = sorted(list(existing_keywords | resume_keywords))

        # Set equation requirement if not already set
        if not user_data["equation_requirement"] and resume_data["equation_requirement"]:
            user_data["equation_requirement"] = resume_data["equation_requirement"]

    # Process writing samples for additional keywords
    writing_keywords = process_writing_samples(user_data["writing_samples"])
    if writing_keywords:
        existing_keywords = set(user_data["keywords"])
        user_data["keywords"] = sorted(list(existing_keywords | set(writing_keywords)))

    # Extract roles from all keywords if roles not explicitly set
    if not user_data["roles"] and user_data["keywords"]:
        user_data["roles"] = extract_roles_from_keywords(user_data["keywords"])

    # Ensure we have at least one role if we have keywords
    if not user_data["roles"] and user_data["keywords"]:
        user_data["roles"] = ["Research Engineering"]

    # Create User object
    try:
        user = User(**user_data)
        console.print("[green]Applicant encoding successful[/green]")
        return user
    except Exception as e:
        console.print(f"[red]Error creating User object: {e}[/red]")
        raise


def main() -> None:
    """CLI entrypoint for applicant encoding."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Encode applicant data from JSON and resume/portfolio"
    )
    parser.add_argument(
        "json_path",
        nargs="?",
        default="autoapply/Yoyo.json",
        help="Path to applicant JSON file",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        help="Output path for encoded JSON (defaults to overwriting input)",
    )
    parser.add_argument(
        "--print-only",
        action="store_true",
        help="Print encoded JSON to stdout instead of saving",
    )

    args = parser.parse_args()

    try:
        user = encode_applicant(args.json_path)

        if args.print_only:
            print(user.model_dump_json(indent=2))
        else:
            output_path = Path(args.output) if args.output else Path(args.json_path)
            # Convert to dict for JSON serialization
            user_dict = user.model_dump()
            # Handle None values appropriately for JSON
            user_dict = {k: v for k, v in user_dict.items() if v is not None}
            with open(output_path, "w") as f:
                json.dump(user_dict, f, indent=2, ensure_ascii=False)
            console.print(
                f"[green]Encoded applicant data saved to {output_path}[/green]"
            )

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
