"""RTL text processing for Arabic Quran text."""
from __future__ import annotations

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    HAS_RTL_LIBS = True
except ImportError:
    HAS_RTL_LIBS = False


def reshape_arabic(text: str) -> str:
    """Reshape Arabic text for proper terminal display.
    
    Converts standard Arabic to presentation forms with connected glyphs,
    then applies BiDi algorithm for correct RTL rendering.
    """
    if not HAS_RTL_LIBS:
        return text
    
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)
