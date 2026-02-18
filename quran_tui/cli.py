from __future__ import annotations

import argparse
import sys

from .data import QuranRepository
from .search import QuranSearchEngine
from .state import ReadingStateStore
from .ui import QuranTUIApplication


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="quran-tui",
        description="Quran terminal app with browse, fuzzy search, and resume.",
    )
    parser.add_argument(
        "--refresh-cache",
        action="store_true",
        help="Download fresh Quran data and overwrite local cache.",
    )
    parser.add_argument(
        "--plain",
        action="store_true",
        help="Disable custom colors for minimal terminals.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    repository = QuranRepository()
    if args.refresh_cache or not repository.has_cache():
        print("Loading Quran data from API (first run may take a moment)...", file=sys.stderr)

    try:
        quran_data = repository.load(force_refresh=args.refresh_cache)
    except Exception as exc:  # pragma: no cover
        print(f"Failed to load Quran data: {exc}", file=sys.stderr)
        return 1

    search_engine = QuranSearchEngine(quran_data.ayahs_flat)
    state_store = ReadingStateStore()
    app = QuranTUIApplication(
        quran_data=quran_data,
        search_engine=search_engine,
        state_store=state_store,
        enable_color=not args.plain,
    )
    app.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
