from __future__ import annotations

from pathlib import Path
import shutil

APP_DIR = Path.home() / ".quran-tui"
LEGACY_APP_DIR = Path.home() / ".quran_tui"
CACHE_DIR = APP_DIR / "cache"
STATE_PATH = APP_DIR / "state.json"
CACHE_PATH = CACHE_DIR / "quran-tui-cache-v1.json"

QURAN_API_BASE = "https://api.quran.com/api/v4"
QURAN_CHAPTERS_URL = f"{QURAN_API_BASE}/chapters"
QURAN_VERSES_URL = f"{QURAN_API_BASE}/quran/verses/uthmani"
QURAN_TRANSLATIONS_URL = f"{QURAN_API_BASE}/quran/translations/85"
TRANSLATION_ID = 85  # M.A.S. Abdel Haleem (English)
HTTP_TIMEOUT_SECONDS = 30

MAX_SEARCH_RESULTS = 25


def ensure_app_dirs() -> None:
    """Make sure app folders exist and legacy path is migrated."""
    _migrate_legacy_data_dir()
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _migrate_legacy_data_dir() -> None:
    if APP_DIR.exists() or not LEGACY_APP_DIR.exists():
        return

    try:
        LEGACY_APP_DIR.rename(APP_DIR)
        return
    except OSError:
        # Rename can fail on locked files or cross-device moves.
        pass

    APP_DIR.mkdir(parents=True, exist_ok=True)
    for child in LEGACY_APP_DIR.iterdir():
        destination = APP_DIR / child.name
        if child.is_dir():
            shutil.copytree(child, destination, dirs_exist_ok=True)
        else:
            shutil.copy2(child, destination)
