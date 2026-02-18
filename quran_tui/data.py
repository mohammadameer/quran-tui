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
    QURAN_TRANSLATIONS_URL,
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
        print("Fetching chapters...", file=sys.stderr)
        chapters = self._fetch_json(QURAN_CHAPTERS_URL)["chapters"]

        print("Fetching Arabic text...", file=sys.stderr)
        all_verses = self._fetch_json(QURAN_VERSES_URL)["verses"]

        print("Fetching translations...", file=sys.stderr)
        all_translations = self._fetch_json(QURAN_TRANSLATIONS_URL)["translations"]

        chapter_map = {int(ch["id"]): ch for ch in chapters}
        verses_by_surah: dict[int, list[tuple[int, str]]] = {}
        for verse in all_verses:
            key = verse["verse_key"]
            surah_num, ayah_num = map(int, key.split(":"))
            if surah_num not in verses_by_surah:
                verses_by_surah[surah_num] = []
            verses_by_surah[surah_num].append((ayah_num, verse.get("text_uthmani", "")))

        translations_list: list[str] = [t.get("text", "") for t in all_translations]

        surahs: list[SurahData] = []
        ayahs_flat: list[Ayah] = []
        translation_idx = 0

        for surah_number in sorted(verses_by_surah.keys()):
            chapter = chapter_map[surah_number]
            name_arabic = str(chapter["name_arabic"])
            name_english = str(chapter["name_simple"])
            bismillah_pre = bool(chapter.get("bismillah_pre", False))

            surah_ayahs: list[Ayah] = []
            verses = sorted(verses_by_surah[surah_number], key=lambda x: x[0])

            for ayah_number, text_arabic in verses:
                text_english = translations_list[translation_idx] if translation_idx < len(translations_list) else ""
                translation_idx += 1

                ayah = Ayah(
                    surah_number=surah_number,
                    surah_name_arabic=name_arabic,
                    surah_name_english=name_english,
                    ayah_number=ayah_number,
                    text_arabic=str(text_arabic).strip(),
                    text_english=str(text_english).strip(),
                )
                surah_ayahs.append(ayah)
                ayahs_flat.append(ayah)

            surahs.append(
                SurahData(
                    number=surah_number,
                    name_arabic=name_arabic,
                    name_english=name_english,
                    ayahs=surah_ayahs,
                    bismillah_pre=bismillah_pre,
                )
            )

        print("Done!", file=sys.stderr)
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
                    "bismillah_pre": surah.bismillah_pre,
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
        return {"version": 3, "surahs": serialized_surahs}

    def _deserialize(self, raw: dict[str, Any]) -> QuranData:
        version = raw.get("version", 1)
        if version < 3:
            raise ValueError("Cache outdated, needs refresh.")

        surahs: list[SurahData] = []
        ayahs_flat: list[Ayah] = []
        for surah_raw in raw["surahs"]:
            surah_number = int(surah_raw["number"])
            name_arabic = str(surah_raw["name_arabic"])
            name_english = str(surah_raw["name_english"])
            bismillah_pre = bool(surah_raw.get("bismillah_pre", surah_number != 1 and surah_number != 9))
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
                    bismillah_pre=bismillah_pre,
                )
            )

        return QuranData(surahs=surahs, ayahs_flat=ayahs_flat)
