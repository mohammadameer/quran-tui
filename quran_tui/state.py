from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .config import STATE_PATH, ensure_app_dirs


@dataclass(slots=True, frozen=True)
class ReadingState:
    surah_number: int = 1
    ayah_number: int = 1


class ReadingStateStore:
    """Saves and loads the last reading position."""

    def __init__(self, state_path: Path | None = None) -> None:
        self.state_path = state_path or STATE_PATH

    def load(self) -> ReadingState:
        ensure_app_dirs()
        if not self.state_path.exists():
            return ReadingState()

        try:
            raw = json.loads(self.state_path.read_text(encoding="utf-8"))
            return ReadingState(
                surah_number=max(1, int(raw.get("surah_number", 1))),
                ayah_number=max(1, int(raw.get("ayah_number", 1))),
            )
        except (OSError, ValueError, json.JSONDecodeError, TypeError):
            return ReadingState()

    def save(self, state: ReadingState) -> None:
        ensure_app_dirs()
        payload = {
            "surah_number": max(1, int(state.surah_number)),
            "ayah_number": max(1, int(state.ayah_number)),
        }
        tmp_path = self.state_path.with_suffix(".tmp")
        tmp_path.write_text(json.dumps(payload), encoding="utf-8")
        tmp_path.replace(self.state_path)
