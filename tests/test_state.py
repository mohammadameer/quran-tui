from __future__ import annotations

from pathlib import Path

from quran_tui.state import ReadingState, ReadingStateStore


def test_state_round_trip(tmp_path: Path) -> None:
    state_path = tmp_path / "state.json"
    store = ReadingStateStore(state_path=state_path)

    assert store.load() == ReadingState()

    store.save(ReadingState(surah_number=2, ayah_number=255))
    assert store.load() == ReadingState(surah_number=2, ayah_number=255)


def test_state_handles_invalid_json(tmp_path: Path) -> None:
    state_path = tmp_path / "state.json"
    state_path.write_text("{bad json", encoding="utf-8")
    store = ReadingStateStore(state_path=state_path)

    assert store.load() == ReadingState()
