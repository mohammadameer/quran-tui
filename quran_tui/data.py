from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen

from .config import (
    CACHE_PATH,
    HTTP_TIMEOUT_SECONDS,
    QURAN_CHAPTERS_URL,
    QURAN_VERSES_URL,
    TRANSLATION_ID,
    ensure_app_dirs,
)
from .models import Ayah, QuranData, SurahData


class QuranRepository:
    """Loads Quran data from local cache or quran.com API."""

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

        downloaded_data = self._download_data()
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

    def _download_data(self) -> QuranData:
        chapters = self._fetch_json(QURAN_CHAPTERS_URL)["chapters"]

        surahs: list[SurahData] = []
        ayahs_flat: list[Ayah] = []

        for i, chapter in enumerate(chapters):
            surah_number = int(chapter["id"])
            name_arabic = str(chapter["name_arabic"])
            name_english = str(chapter["name_simple"])

            print(f"Downloading surah {surah_number}/114...", file=sys.stderr, end="\r")

            verses_url = f"{QURAN_VERSES_URL}/{surah_number}?translations={TRANSLATION_ID}&fields=text_uthmani&per_page=300"
            verses_data = self._fetch_json(verses_url)

            surah_ayahs: list[Ayah] = []
            for verse in verses_data["verses"]:
                verse_key = verse["verse_key"]
                ayah_number = int(verse_key.split(":")[1])
                text_arabic = str(verse.get("text_uthmani", "")).strip()
                text_english = ""
                if verse.get("translations"):
                    text_english = str(verse["translations"][0].get("text", "")).strip()

                ayah = Ayah(
                    surah_number=surah_number,
                    surah_name_arabic=name_arabic,
                    surah_name_english=name_english,
                    ayah_number=ayah_number,
                    text_arabic=text_arabic,
                    text_english=text_english,
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

        print(" " * 40, file=sys.stderr, end="\r")
        return QuranData(surahs=surahs, ayahs_flat=ayahs_flat)

    def _fetch_json(self, url: str) -> dict[str, Any]:
        request = Request(url, headers={"User-Agent": "quran-tui/0.1"})
        try:
            with urlopen(request, timeout=HTTP_TIMEOUT_SECONDS) as response:
                payload = response.read().decode("utf-8")
        except (URLError, TimeoutError) as exc:
            raise RuntimeError(f"Could not fetch data from {url}") from exc

        return json.loads(payload)

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
        return {"version": 2, "surahs": serialized_surahs}

    def _deserialize(self, raw: dict[str, Any]) -> QuranData:
        version = raw.get("version", 1)
        if version not in (1, 2):
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
