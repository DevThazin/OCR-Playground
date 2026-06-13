"""
config/languages.py
-------------------
Central language configuration for the OCR Playground.

All OCR engine language code mappings live here.
No engine-specific code should hardcode language strings;
they must always reference this module.

Supported languages: 15
Engines covered: EasyOCR, Tesseract OCR
Future engines: PaddleOCR, TrOCR, DocTR (add keys here when integrating)
"""

from typing import Dict, Any

# ---------------------------------------------------------------------------
# Primary language registry
# ---------------------------------------------------------------------------
# Structure per entry:
#   "Display Name": {
#       "easyocr":    <EasyOCR language code(s) — str or list>,
#       "tesseract":  <Tesseract language code>,
#       "native":     <Name written in that script — for UI display>,
#       "rtl":        <True if right-to-left script>,
#   }
# ---------------------------------------------------------------------------

LANGUAGES: Dict[str, Dict[str, Any]] = {
    "English": {
        "easyocr": "en",
        "tesseract": "eng",
        "native": "English",
        "rtl": False,
    },
    "Hindi": {
        "easyocr": "hi",
        "tesseract": "hin",
        "native": "हिन्दी",
        "rtl": False,
    },
    "Bengali": {
        "easyocr": "bn",
        "tesseract": "ben",
        "native": "বাংলা",
        "rtl": False,
    },
    "Tamil": {
        "easyocr": "ta",
        "tesseract": "tam",
        "native": "தமிழ்",
        "rtl": False,
    },
    "Telugu": {
        "easyocr": "te",
        "tesseract": "tel",
        "native": "తెలుగు",
        "rtl": False,
    },
    "Kannada": {
        "easyocr": "kn",
        "tesseract": "kan",
        "native": "ಕನ್ನಡ",
        "rtl": False,
    },
    "Malayalam": {
        "easyocr": "ml",
        "tesseract": "mal",
        "native": "മലയാളം",
        "rtl": False,
    },
    "Thai": {
        "easyocr": "th",
        "tesseract": "tha",
        "native": "ภาษาไทย",
        "rtl": False,
    },
    "Chinese Simplified": {
        "easyocr": "ch_sim",
        "tesseract": "chi_sim",
        "native": "简体中文",
        "rtl": False,
    },
    "Chinese Traditional": {
        "easyocr": "ch_tra",
        "tesseract": "chi_tra",
        "native": "繁體中文",
        "rtl": False,
    },
    "Japanese": {
        "easyocr": "ja",
        "tesseract": "jpn",
        "native": "日本語",
        "rtl": False,
    },
    "Korean": {
        "easyocr": "ko",
        "tesseract": "kor",
        "native": "한국어",
        "rtl": False,
    },
    "Arabic": {
        "easyocr": "ar",
        "tesseract": "ara",
        "native": "العربية",
        "rtl": True,
    },
    "Russian": {
        "easyocr": "ru",
        "tesseract": "rus",
        "native": "Русский",
        "rtl": False,
    },
    "Vietnamese": {
        "easyocr": "vi",
        "tesseract": "vie",
        "native": "Tiếng Việt",
        "rtl": False,
    },
}
# ---------------------------------------------------------------------------
# Auto-detect configuration
# ---------------------------------------------------------------------------
# When the user selects "Auto Detect", EasyOCR is run in multilingual mode
# using this list of codes. Tesseract will use "eng" as its fallback.

AUTO_DETECT_EASYOCR_LANGS: list = [
    "en", "ch_sim", "ch_tra", "ja", "ko",
    "ar", "ru", "hi", "th", "vi",
]

AUTO_DETECT_TESSERACT_LANG: str = "eng"

# ---------------------------------------------------------------------------
# Convenience helpers
# ---------------------------------------------------------------------------

def get_display_names() -> list:
    """Return sorted list of human-readable language names for UI dropdowns."""
    return sorted(LANGUAGES.keys())


def get_easyocr_code(display_name: str) -> str | list:
    """
    Return the EasyOCR language code(s) for a given display name.

    Args:
        display_name: Key from LANGUAGES (e.g. "Burmese (Myanmar)").

    Returns:
        A string code like "my", or a list for multilingual mode.

    Raises:
        KeyError: If the display name is not found in LANGUAGES.
    """
    return LANGUAGES[display_name]["easyocr"]


def get_tesseract_code(display_name: str) -> str:
    """
    Return the Tesseract language code for a given display name.

    Args:
        display_name: Key from LANGUAGES (e.g. "Burmese (Myanmar)").

    Returns:
        A string code like "mya".

    Raises:
        KeyError: If the display name is not found in LANGUAGES.
    """
    return LANGUAGES[display_name]["tesseract"]


def is_rtl(display_name: str) -> bool:
    """Return True if the language uses a right-to-left script."""
    return LANGUAGES.get(display_name, {}).get("rtl", False)


def language_count() -> int:
    """Return the total number of registered languages."""
    return len(LANGUAGES)
