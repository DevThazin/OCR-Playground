"""
utils/sidebar.py
-----------------
Streamlit sidebar: language selector, engine toggles, processing options,
engine availability status, and the language dashboard.

Returns a typed config dict consumed by app.py.
"""

from typing import Any
import streamlit as st

from config.languages import (
    LANGUAGES,
    get_display_names,
    language_count,
    AUTO_DETECT_EASYOCR_LANGS,
    AUTO_DETECT_TESSERACT_LANG,
)


def render_sidebar() -> dict[str, Any]:
    """
    Render the full sidebar and return the user's selections.

    Returns:
        dict with keys:
            language         – display name string (or "Auto Detect")
            easyocr_lang     – EasyOCR code(s) to use
            tesseract_lang   – Tesseract code to use
            run_easyocr      – bool
            run_tesseract    – bool
            show_confidence  – bool: draw conf labels on boxes
            enhance_image    – bool: apply contrast/sharpness before OCR
            enhance_contrast – float slider value
            enhance_sharp    – float slider value
    """
    with st.sidebar:
        # ── Brand ─────────────────────────────────────────────────
        st.markdown(
            '<div style="padding:12px 0 4px 0;">'
            '<span style="font-size:1.05rem;font-weight:700;color:#00C9A7;'
            'font-family:monospace;letter-spacing:-0.5px;">OCR Playground</span><br>'
            '<span style="font-size:0.65rem;color:#8B949E;letter-spacing:0.1em;'
            'text-transform:uppercase;">Research Platform</span>'
            '</div>',
            unsafe_allow_html=True,
        )

        st.divider()

        # ── Language section ───────────────────────────────────────
        st.markdown('<div class="sidebar-section">Language</div>', unsafe_allow_html=True)

        # Build dropdown options: languages + Auto Detect at top
        all_names = ["Auto Detect"] + get_display_names()
        english_index = all_names.index("English")

        selected_language: str = st.selectbox(
            "Select language",
            options=all_names,
            index=english_index,
            label_visibility="collapsed",
            help="Applies to both OCR engines simultaneously.",
        )

        # Resolve codes
        if selected_language == "Auto Detect":
            easyocr_lang   = AUTO_DETECT_EASYOCR_LANGS
            tesseract_lang = AUTO_DETECT_TESSERACT_LANG
        else:
            cfg = LANGUAGES[selected_language]
            easyocr_lang   = cfg["easyocr"]
            tesseract_lang = cfg["tesseract"]

        # Language dashboard pill
        ec = easyocr_lang if isinstance(easyocr_lang, str) else "+".join(easyocr_lang)
        st.markdown(
            f'<div class="lang-dashboard">'
            f'<strong>Supported:</strong> {language_count()} languages<br>'
            f'<strong>Selected:</strong> {selected_language}<br>'
            f'<strong>EasyOCR:</strong> <code>{ec}</code><br>'
            f'<strong>Tesseract:</strong> <code>{tesseract_lang}</code>'
            f'</div>',
            unsafe_allow_html=True,
        )

        st.divider()

        # ── OCR Engine selection ───────────────────────────────────
        st.markdown('<div class="sidebar-section">OCR Engines</div>', unsafe_allow_html=True)

        run_easyocr   = st.checkbox("EasyOCR",       value=True,  help="Deep-learning OCR (CRNN + CRAFT detector)")
        run_tesseract = st.checkbox("Tesseract OCR",  value=True,  help="Classical OCR engine by Google")

        if not run_easyocr and not run_tesseract:
            st.warning("Enable at least one engine.", icon="⚠️")

        # Engine availability status
        _show_engine_status()

        st.divider()

        # ── Processing options ─────────────────────────────────────
        st.markdown('<div class="sidebar-section">Processing</div>', unsafe_allow_html=True)

        show_confidence = st.checkbox(
            "Show confidence on boxes",
            value=True,
            help="Draw confidence % above each bounding box.",
        )

        enhance_image = st.checkbox(
            "Pre-process image",
            value=False,
            help="Apply contrast & sharpness before OCR. Can improve accuracy on low-quality scans.",
        )

        enhance_contrast = 1.0
        enhance_sharp    = 1.0
        if enhance_image:
            enhance_contrast = st.slider("Contrast",  0.5, 3.0, 1.5, 0.1)
            enhance_sharp    = st.slider("Sharpness", 0.5, 3.0, 1.5, 0.1)

        st.divider()

        # ── Future engines notice ──────────────────────────────────
        with st.expander("Future engines (coming soon)", expanded=False):
            st.markdown(
                '<div style="font-size:0.75rem;color:#8B949E;line-height:1.6;">'
                '⬡ PaddleOCR<br>'
                '⬡ TrOCR (Microsoft)<br>'
                '⬡ DocTR (mindee)<br>'
                '<br>'
                '<span style="font-size:0.68rem;color:#444D56;">'
                'Architecture supports plug-in addition.</span>'
                '</div>',
                unsafe_allow_html=True,
            )

        # ── Footer ────────────────────────────────────────────────
        st.markdown(
            '<div style="font-size:0.62rem;color:#444D56;text-align:center;'
            'padding-top:20px;letter-spacing:0.06em;">'
            'OCR Playground · PhD Portfolio<br>'
            'Phase 3 · Streamlit'
            '</div>',
            unsafe_allow_html=True,
        )

    return {
        "language":          selected_language,
        "easyocr_lang":      easyocr_lang,
        "tesseract_lang":    tesseract_lang,
        "run_easyocr":       run_easyocr,
        "run_tesseract":     run_tesseract,
        "show_confidence":   show_confidence,
        "enhance_image":     enhance_image,
        "enhance_contrast":  enhance_contrast,
        "enhance_sharp":     enhance_sharp,
    }


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

@st.cache_resource(show_spinner=False)
def _check_easyocr() -> bool:
    """Return True if easyocr is importable."""
    try:
        import easyocr  # noqa: F401
        return True
    except ImportError:
        return False


@st.cache_resource(show_spinner=False)
def _check_tesseract() -> bool:
    """Return True if pytesseract can call the Tesseract binary."""
    try:
        import pytesseract
        pytesseract.get_tesseract_version()
        return True
    except Exception:
        return False


def _show_engine_status() -> None:
    """Display small coloured availability indicators for each engine."""
    easy_ok = _check_easyocr()
    tess_ok = _check_tesseract()

    def dot(ok: bool) -> str:
        color = "#28A745" if ok else "#F85149"
        label = "available" if ok else "not found"
        return (
            f'<span style="display:inline-flex;align-items:center;gap:5px;'
            f'font-size:0.7rem;color:{"#8B949E" if ok else "#F85149"};">'
            f'<span style="width:6px;height:6px;border-radius:50%;background:{color};'
            f'display:inline-block;"></span>{label}</span>'
        )

    st.markdown(
        f'<div style="margin-top:8px;line-height:2;">'
        f'EasyOCR &nbsp;&nbsp; {dot(easy_ok)}<br>'
        f'Tesseract &nbsp;{dot(tess_ok)}'
        f'</div>',
        unsafe_allow_html=True,
    )
