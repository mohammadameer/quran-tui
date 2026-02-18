from __future__ import annotations

import argparse
import sys

from . import __version__
from .data import QuranRepository
from .search import QuranSearchEngine
from .state import ReadingStateStore
from .ui import QuranTUIApplication
from .update import check_for_update, run_self_update


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="quran",
        description="Quran terminal app with browse, fuzzy search, and resume.",
    )
    parser.add_argument(
        "--refresh-cache",
        action="store_true",
        help="Download fresh Quran data and overwrite local cache.",
    )
    parser.add_argument(
        "--download-data",
        action="store_true",
        help="Download Quran data and exit (used during install).",
    )
    parser.add_argument(
        "--plain",
        action="store_true",
        help="Disable custom colors for minimal terminals.",
    )
    parser.add_argument(
        "--self-update",
        action="store_true",
        help="Update Quran TUI and exit.",
    )
    parser.add_argument(
        "--no-update-check",
        action="store_true",
        help="Skip startup update check.",
    )
    return parser


def _download_data_only() -> int:
    repository = QuranRepository()
    print("Downloading Quran data...", file=sys.stderr)
    try:
        repository.load(force_refresh=not repository.has_cache())
        print("Quran data ready.", file=sys.stderr)
        return 0
    except Exception as exc:
        print(f"Failed to download: {exc}", file=sys.stderr)
        return 1


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.self_update:
        update_result = run_self_update()
        stream = sys.stdout if update_result.updated else sys.stderr
        print(update_result.message, file=stream)
        return 0 if update_result.updated else 1

    if args.download_data:
        return _download_data_only()

    if not args.no_update_check:
        should_exit = _check_and_prompt_update()
        if should_exit:
            return 0

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

def _check_and_prompt_update() -> bool:
    update_info = check_for_update(__version__)
    if not update_info.update_available or not update_info.latest_version:
        return False

    print(
        f"Update available: {update_info.current_version} -> {update_info.latest_version}",
        file=sys.stderr,
    )

    if not sys.stdin.isatty():
        print("Run: pipx upgrade quran", file=sys.stderr)
        return False

    try:
        user_input = input("Press Enter or y to update now (n to skip): ").strip().lower()
    except EOFError:
        return False

    if user_input not in ("", "y", "yes"):
        print("Skipped update.", file=sys.stderr)
        return False

    update_result = run_self_update()
    stream = sys.stdout if update_result.updated else sys.stderr
    print(update_result.message, file=stream)
    if update_result.updated:
        print("Please run quran again.", file=sys.stderr)
    return update_result.updated


if __name__ == "__main__":
    raise SystemExit(main())
