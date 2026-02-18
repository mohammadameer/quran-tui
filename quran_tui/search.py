from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Callable, Sequence

from .config import MAX_SEARCH_RESULTS
from .models import Ayah

try:
    from rapidfuzz import fuzz  # type: ignore
except ImportError:  # pragma: no cover
    fuzz = None


def _normalize(text: str) -> str:
    return " ".join(text.casefold().split())


def _fallback_ratio(left: str, right: str) -> float:
    return SequenceMatcher(None, left, right).ratio() * 100


def _rapidfuzz_ratio(left: str, right: str) -> float:
    assert fuzz is not None
    return float(fuzz.WRatio(left, right))


def _score_func() -> Callable[[str, str], float]:
    return _rapidfuzz_ratio if fuzz is not None else _fallback_ratio


@dataclass(slots=True, frozen=True)
class SearchResult:
    ayah: Ayah
    score: float
    preview: str


class QuranSearchEngine:
    """Fuzzy verse search with direct-match boost."""

    def __init__(self, ayahs: Sequence[Ayah]) -> None:
        self.ayahs = list(ayahs)
        self._ratio = _score_func()

    def search(self, query: str, limit: int = MAX_SEARCH_RESULTS) -> list[SearchResult]:
        normalized_query = _normalize(query)
        if not normalized_query:
            return []

        results: list[SearchResult] = []
        for ayah in self.ayahs:
            normalized_en = _normalize(ayah.text_english)
            normalized_ar = _normalize(ayah.text_arabic)

            english_score = self._ratio(normalized_query, normalized_en)
            arabic_score = self._ratio(normalized_query, normalized_ar)

            contains_bonus = 35 if normalized_query in normalized_en or normalized_query in normalized_ar else 0
            best_score = max(english_score, arabic_score) + contains_bonus
            if best_score < 45:
                continue

            results.append(
                SearchResult(
                    ayah=ayah,
                    score=best_score,
                    preview=_build_preview(ayah.text_english),
                )
            )

        results.sort(key=lambda item: item.score, reverse=True)
        return results[:limit]


def _build_preview(text: str, max_length: int = 110) -> str:
    compact = " ".join(text.split())
    if len(compact) <= max_length:
        return compact
    return compact[: max_length - 3].rstrip() + "..."
