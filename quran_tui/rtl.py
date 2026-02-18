"""RTL text processing for Arabic Quran text."""
from __future__ import annotations

try:
    import arabic_reshaper
    HAS_RESHAPER = True
except ImportError:
    HAS_RESHAPER = False


def reshape_arabic(text: str) -> str:
    """Reshape Arabic text for proper terminal display.
    
    Converts standard Arabic to presentation forms with connected glyphs.
    """
    if not HAS_RESHAPER:
        return text
    
    return arabic_reshaper.reshape(text)
