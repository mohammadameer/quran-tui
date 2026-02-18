from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class Ayah:
    surah_number: int
    surah_name_arabic: str
    surah_name_english: str
    ayah_number: int
    text_arabic: str
    text_english: str


@dataclass(slots=True)
class SurahData:
    number: int
    name_arabic: str
    name_english: str
    ayahs: list[Ayah]
    bismillah_pre: bool = False


@dataclass(slots=True)
class QuranData:
    surahs: list[SurahData]
    ayahs_flat: list[Ayah]
