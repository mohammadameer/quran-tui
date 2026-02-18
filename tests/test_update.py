from __future__ import annotations

import unittest
from unittest.mock import patch

from quran_tui.update import check_for_update, is_newer_version


class UpdateTests(unittest.TestCase):
    def test_is_newer_version_true(self) -> None:
        self.assertTrue(is_newer_version("0.2.0", "0.1.9"))
        self.assertTrue(is_newer_version("1.0.0", "0.99.9"))

    def test_is_newer_version_false(self) -> None:
        self.assertFalse(is_newer_version("0.1.0", "0.1.0"))
        self.assertFalse(is_newer_version("0.1.0", "0.2.0"))

    @patch("quran_tui.update.fetch_latest_version", return_value="0.9.0")
    def test_check_for_update_available(self, _mock_fetch) -> None:
        info = check_for_update("0.1.0")
        self.assertEqual(info.latest_version, "0.9.0")
        self.assertTrue(info.update_available)

    @patch("quran_tui.update.fetch_latest_version", return_value=None)
    def test_check_for_update_no_remote(self, _mock_fetch) -> None:
        info = check_for_update("0.1.0")
        self.assertIsNone(info.latest_version)
        self.assertFalse(info.update_available)


if __name__ == "__main__":
    unittest.main()
