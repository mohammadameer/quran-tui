from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from quran_tui.state import ReadingState, ReadingStateStore


class ReadingStateStoreTests(unittest.TestCase):
    def test_state_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            state_path = Path(tmp_dir) / "state.json"
            store = ReadingStateStore(state_path=state_path)

            self.assertEqual(store.load(), ReadingState())

            store.save(ReadingState(surah_number=2, ayah_number=255))
            self.assertEqual(store.load(), ReadingState(surah_number=2, ayah_number=255))

    def test_state_handles_invalid_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            state_path = Path(tmp_dir) / "state.json"
            state_path.write_text("{bad json", encoding="utf-8")
            store = ReadingStateStore(state_path=state_path)

            self.assertEqual(store.load(), ReadingState())


if __name__ == "__main__":
    unittest.main()
