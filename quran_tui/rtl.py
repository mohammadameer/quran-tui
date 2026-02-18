"""RTL text processing for Arabic Quran text."""
from __future__ import annotations

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    HAS_RTL_LIBS = True
except ImportError:
    HAS_RTL_LIBS = False


# RTL mode: "auto", "raw", "reshape", "bidi"
_rtl_mode = "auto"


def set_rtl_mode(mode: str) -> None:
    """Set RTL rendering mode: auto, raw, reshape, bidi"""
    global _rtl_mode
    _rtl_mode = mode


def reshape_arabic(text: str) -> str:
    """Reshape Arabic text for proper terminal display."""
    if not HAS_RTL_LIBS or _rtl_mode == "raw":
        return text
    
    if _rtl_mode == "reshape":
        return arabic_reshaper.reshape(text)
    
    # Default: reshape + bidi
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)
