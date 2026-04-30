"""Auto-apply configuration: paths, directories, defaults."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
AUTOAPPLY_DIR = REPO_ROOT / "autoapply"
DATA_DIR = AUTOAPPLY_DIR / "data"
DB_PATH = AUTOAPPLY_DIR / "autoapply.db"

PENDING_DIR = DATA_DIR / "pending"
RESULTS_DIR = DATA_DIR / "results"
DRAFTS_DIR = DATA_DIR / "drafts"
RAW_DIR = DATA_DIR / "raw"

USER_ID = 1

DEFAULT_VC_FIRMS = [
    {"name": "a16z", "careers_url": "https://jobs.a16z.com/jobs"},
]


def ensure_dirs() -> None:
    """Create all required directories if they don't exist."""
    for d in [DATA_DIR, PENDING_DIR, RESULTS_DIR, DRAFTS_DIR, RAW_DIR]:
        d.mkdir(parents=True, exist_ok=True)
