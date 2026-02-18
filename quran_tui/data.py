from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen

from .config import (
    CACHE_PATH,
    HTTP_TIMEOUT_SECONDS,
    QURAN_ARABIC_URL,
    QURAN_ENGLISH_URL,
    ensure_app_dirs,
)
from .models import Ayah, QuranData, SurahData


class QuranRepository:
    """Loads Quran data from local cache or remote API."""

    def __init__(self, cache_path: Path | None = None) -> None:
        self.cache_path = cache_path or CACHE_PATH

    def has_cache(self) -> bool:
        return self.cache_path.exists()

    def load(self, force_refresh: bool = False) -> QuranData:
        ensure_app_dirs()
        if not force_refresh:
            cached_data = self._load_from_cache()
            if cached_data is not None:
                return cached_data

        downloaded_data = self._download_and_merge()
        self._save_to_cache(downloaded_data)
        return downloaded_data

    def _load_from_cache(self) -> QuranData | None:
        if not self.cache_path.exists():
            return None

        try:
            raw = json.loads(self.cache_path.read_text(encoding="utf-8"))
            return self._deserialize(raw)
        except (OSError, json.JSONDecodeError, KeyError, ValueError, TypeError):
            return None

    def _save_to_cache(self, quran_data: QuranData) -> None:
        serialized = self._serialize(quran_data)
        tmp_path = self.cache_path.with_suffix(".tmp")
        tmp_path.write_text(
            json.dumps(serialized, ensure_ascii=False, separators=(",", ":")),
            encoding="utf-8",
        )
        tmp_path.replace(self.cache_path)

    def _download_and_merge(self) -> QuranData:
        arabic_payload = self._download_json(QURAN_ARABIC_URL)
        english_payload = self._download_json(QURAN_ENGLISH_URL)

        arabic_surahs = arabic_payload["surahs"]
        english_surahs = english_payload["surahs"]

        if len(arabic_surahs) != len(english_surahs):
            raise RuntimeError("Quran API returned inconsistent surah counts.")

        surahs: list[SurahData] = []
        ayahs_flat: list[Ayah] = []

        for arabic_surah, english_surah in zip(arabic_surahs, english_surahs):
            surah_number = int(arabic_surah["number"])
            name_arabic = str(arabic_surah["name"])
            name_english = str(arabic_surah.get("englishName", english_surah.get("englishName", "")))

            arabic_ayahs = arabic_surah["ayahs"]
            english_ayahs = english_surah["ayahs"]
            ayah_count = min(len(arabic_ayahs), len(english_ayahs))

            surah_ayahs: list[Ayah] = []
            for idx in range(ayah_count):
                ar_ayah = arabic_ayahs[idx]
                en_ayah = english_ayahs[idx]
                ayah_number = int(ar_ayah["numberInSurah"])
                ayah = Ayah(
                    surah_number=surah_number,
                    surah_name_arabic=name_arabic,
                    surah_name_english=name_english,
                    ayah_number=ayah_number,
                    text_arabic=str(ar_ayah["text"]).strip(),
                    text_english=str(en_ayah["text"]).strip(),
                )
                surah_ayahs.append(ayah)
                ayahs_flat.append(ayah)

            surahs.append(
                SurahData(
                    number=surah_number,
                    name_arabic=name_arabic,
                    name_english=name_english,
                    ayahs=surah_ayahs,
                )
            )

        return QuranData(surahs=surahs, ayahs_flat=ayahs_flat)

    def _download_json(self, url: str) -> dict[str, Any]:
        request = Request(url, headers={"User-Agent": "quran-tui/0.1"})
        try:
            with urlopen(request, timeout=HTTP_TIMEOUT_SECONDS) as response:
                payload = response.read().decode("utf-8")
        except (URLError, TimeoutError) as exc:
            raise RuntimeError(f"Could not fetch Quran data from {url}") from exc

        body = json.loads(payload)
        if body.get("status") != "OK":
            raise RuntimeError(f"Quran API returned error for {url}")
        return body["data"]

    def _serialize(self, quran_data: QuranData) -> dict[str, Any]:
        serialized_surahs: list[dict[str, Any]] = []
        for surah in quran_data.surahs:
            serialized_surahs.append(
                {
                    "number": surah.number,
                    "name_arabic": surah.name_arabic,
                    "name_english": surah.name_english,
                    "ayahs": [
                        {
                            "ayah_number": ayah.ayah_number,
                            "text_arabic": ayah.text_arabic,
                            "text_english": ayah.text_english,
                        }
                        for ayah in surah.ayahs
                    ],
                }
            )
        return {"version": 1, "surahs": serialized_surahs}

    def _deserialize(self, raw: dict[str, Any]) -> QuranData:
        if raw.get("version") != 1:
            raise ValueError("Unsupported cache format.")

        surahs: list[SurahData] = []
        ayahs_flat: list[Ayah] = []
        for surah_raw in raw["surahs"]:
            surah_number = int(surah_raw["number"])
            name_arabic = str(surah_raw["name_arabic"])
            name_english = str(surah_raw["name_english"])
            surah_ayahs: list[Ayah] = []
            for ayah_raw in surah_raw["ayahs"]:
                ayah = Ayah(
                    surah_number=surah_number,
                    surah_name_arabic=name_arabic,
                    surah_name_english=name_english,
                    ayah_number=int(ayah_raw["ayah_number"]),
                    text_arabic=str(ayah_raw["text_arabic"]),
                    text_english=str(ayah_raw["text_english"]),
                )
                surah_ayahs.append(ayah)
                ayahs_flat.append(ayah)

            surahs.append(
                SurahData(
                    number=surah_number,
                    name_arabic=name_arabic,
                    name_english=name_english,
                    ayahs=surah_ayahs,
                )
            )

        return QuranData(surahs=surahs, ayahs_flat=ayahs_flat)
