"""Role type definitions for job matching."""

from __future__ import annotations

from pydantic import BaseModel, Field

DEFAULT_ROLES = [
    {
        "name": "AI and ML Engineering",
        "keywords": [
            "machine learning", "ml engineer", "ai engineer",
            "deep learning", "llm", "large language model",
            "nlp", "natural language processing",
            "computer vision", "generative ai",
            "model training", "inference",
            "ml infrastructure", "mlops",
        ],
        "exclude_keywords": [
            "sales", "marketing", "business development",
        ],
    },
    {
        "name": "Research Engineering",
        "keywords": [
            "research engineer", "applied research",
            "research scientist", "applied scientist",
            "experimental", "prototype",
            "research software engineer", "rse",
        ],
        "exclude_keywords": [
            "product manager", "sales", "marketing",
        ],
    },
    {
        "name": "Neuro Engineering",
        "keywords": [
            "neuro", "neural", "bci", "brain-computer",
            "neuroscience", "neurotechnology",
            "electrophysiology", "neural interface",
            "neuroimaging", "eeg", "ecog", "spike sorting",
            "neuromorphic", "neural decoding", "neural encoding",
        ],
        "exclude_keywords": [
            "sales", "marketing", "business development",
        ],
    },
]


class RoleType(BaseModel):
    name: str
    keywords: list[str] = Field(default_factory=list)
    exclude_keywords: list[str] = Field(default_factory=list)


def get_role_types() -> list[RoleType]:
    """Return the default role type definitions."""
    return [RoleType(**r) for r in DEFAULT_ROLES]


def match_role_type(title: str, description: str) -> list[str]:
    """Return matched role type names for a given job."""
    title_lower = title.lower()
    desc_lower = description.lower()
    combined = f"{title_lower} {desc_lower}"

    matches = []
    for role in get_role_types():
        if any(kw in combined for kw in role.keywords):
            if not any(ex in combined for ex in role.exclude_keywords):
                matches.append(role.name)

    return matches
