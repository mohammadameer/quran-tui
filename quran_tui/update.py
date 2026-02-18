from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

GITHUB_REPO = "mohammadameer/quran-tui"
LATEST_RELEASE_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
PYPROJECT_RAW_URL = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/pyproject.toml"
INSTALL_SOURCE = f"git+https://github.com/{GITHUB_REPO}.git"
REQUEST_TIMEOUT_SECONDS = 4


@dataclass(slots=True, frozen=True)
class UpdateInfo:
    current_version: str
    latest_version: str | None
    update_available: bool


@dataclass(slots=True, frozen=True)
class UpdateResult:
    updated: bool
    message: str


def check_for_update(current_version: str) -> UpdateInfo:
    latest = fetch_latest_version()
    if not latest:
        return UpdateInfo(
            current_version=current_version,
            latest_version=None,
            update_available=False,
        )

    return UpdateInfo(
        current_version=current_version,
        latest_version=latest,
        update_available=is_newer_version(latest, current_version),
    )


def fetch_latest_version() -> str | None:
    latest_from_release = _fetch_latest_release_version()
    if latest_from_release:
        return latest_from_release
    return _fetch_version_from_pyproject()


def _fetch_latest_release_version() -> str | None:
    payload = _fetch_json(LATEST_RELEASE_URL)
    if not payload:
        return None
    tag_name = payload.get("tag_name")
    if not isinstance(tag_name, str):
        return None
    return _clean_version(tag_name)


def _fetch_version_from_pyproject() -> str | None:
    content = _fetch_text(PYPROJECT_RAW_URL)
    if not content:
        return None
    match = re.search(r'^version\s*=\s*"([^"]+)"\s*$', content, flags=re.MULTILINE)
    if not match:
        return None
    return _clean_version(match.group(1))


def _fetch_json(url: str) -> dict[str, Any] | None:
    try:
        text = _fetch_text(url)
        if not text:
            return None
        data = json.loads(text)
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        return None
    return None


def _fetch_text(url: str) -> str | None:
    request = Request(url, headers={"User-Agent": "quran-tui-update-check/0.1"})
    try:
        with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            return response.read().decode("utf-8")
    except (HTTPError, URLError, TimeoutError, OSError):
        return None


def is_newer_version(candidate: str, current: str) -> bool:
    return _parse_version(candidate) > _parse_version(current)


def _clean_version(version: str) -> str | None:
    cleaned = version.strip()
    if not cleaned:
        return None
    if cleaned.startswith("v"):
        cleaned = cleaned[1:]
    return cleaned if cleaned else None


def _parse_version(version: str) -> tuple[int, int, int]:
    base = version.strip().split("+", 1)[0].split("-", 1)[0]
    parts: list[int] = []
    for token in base.split("."):
        digits = "".join(ch for ch in token if ch.isdigit())
        parts.append(int(digits) if digits else 0)

    while len(parts) < 3:
        parts.append(0)
    return tuple(parts[:3])  # major, minor, patch


def run_self_update() -> UpdateResult:
    commands = _candidate_update_commands()
    for command in commands:
        try:
            result = subprocess.run(command, check=False, capture_output=True, text=True)
        except OSError:
            continue

        if result.returncode == 0:
            return UpdateResult(
                updated=True,
                message=f"Updated successfully using: {' '.join(command)}",
            )

    return UpdateResult(
        updated=False,
        message="Update failed. Please run: pipx upgrade quran-tui",
    )


def _candidate_update_commands() -> list[list[str]]:
    commands: list[list[str]] = []

    if shutil.which("pipx"):
        commands.append(["pipx", "upgrade", "quran-tui"])
        commands.append(["pipx", "install", "--force", INSTALL_SOURCE])

    commands.append([sys.executable, "-m", "pip", "install", "--upgrade", INSTALL_SOURCE])
    return commands
