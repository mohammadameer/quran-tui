from __future__ import annotations

from pathlib import Path

APP_DIR = Path.home() / ".quran_tui"
CACHE_DIR = APP_DIR / "cache"
STATE_PATH = APP_DIR / "state.json"
CACHE_PATH = CACHE_DIR / "quran_cache_v1.json"

QURAN_ARABIC_URL = "https://api.alquran.cloud/v1/quran/quran-uthmani"
QURAN_ENGLISH_URL = "https://api.alquran.cloud/v1/quran/en.asad"
HTTP_TIMEOUT_SECONDS = 30

MAX_SEARCH_RESULTS = 25


def ensure_app_dirs() -> None:
    """Make sure app folders exist."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
