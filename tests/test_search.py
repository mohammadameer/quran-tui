from __future__ import annotations

from quran_tui.models import Ayah
from quran_tui.search import QuranSearchEngine


def _sample_ayahs() -> list[Ayah]:
    return [
        Ayah(
            surah_number=1,
            surah_name_arabic="الفاتحة",
            surah_name_english="Al-Fatihah",
            ayah_number=1,
            text_arabic="بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ",
            text_english="In the name of Allah, The Entirely Merciful, The Especially Merciful.",
        ),
        Ayah(
            surah_number=1,
            surah_name_arabic="الفاتحة",
            surah_name_english="Al-Fatihah",
            ayah_number=2,
            text_arabic="الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ",
            text_english="All praise is for Allah, Lord of all worlds.",
        ),
        Ayah(
            surah_number=2,
            surah_name_arabic="البقرة",
            surah_name_english="Al-Baqarah",
            ayah_number=255,
            text_arabic="اللَّهُ لَا إِلَٰهَ إِلَّا هُوَ الْحَيُّ الْقَيُّومُ",
            text_english="Allah! There is no god worthy of worship except Him, the Ever-Living, All-Sustaining.",
        ),
    ]


def test_search_finds_english_text() -> None:
    engine = QuranSearchEngine(_sample_ayahs())
    results = engine.search("merciful")
    assert results
    assert results[0].ayah.surah_number == 1
    assert results[0].ayah.ayah_number == 1


def test_search_finds_arabic_text() -> None:
    engine = QuranSearchEngine(_sample_ayahs())
    results = engine.search("الْحَمْدُ لِلَّهِ")
    assert results
    assert any(item.ayah.ayah_number == 2 for item in results)


def test_search_empty_query_returns_no_results() -> None:
    engine = QuranSearchEngine(_sample_ayahs())
    assert engine.search("") == []
