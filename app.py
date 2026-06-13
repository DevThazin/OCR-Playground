"""
app.py
-------
OCR Playground – Streamlit Application (Phase 3)
=================================================

Entry point for the web application. Run with:
    streamlit run app.py

Architecture:
  ┌─ sidebar.py     → user config (language, engines, options)
  ├─ image_utils.py → upload validation & preprocessing
  ├─ easyocr_engine.py / tesseract_engine.py → OCR
  ├─ visualization.py → annotated images
  ├─ benchmarking.py  → runtime tables
  ├─ metrics.py       → confidence stats, text stats
  ├─ exports.py       → txt / csv / json download
  └─ styles.py        → injected CSS
"""

from __future__ import annotations

import io
import logging
from datetime import datetime
from typing import Optional

import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from PIL import Image as PILImage

# ── Internal modules ─────────────────────────────────────────────
from config.languages import language_count
from ocr_engines.easyocr_engine import EasyOCREngine
from ocr_engines.tesseract_engine import TesseractEngine
from utils.image_utils import (
    load_image_from_bytes,
    validate_upload,
    enhance_for_ocr,
    get_image_info,
)
from utils.visualization import draw_bounding_boxes, create_comparison_panel
from utils.benchmarking import build_benchmark_table, speed_winner, confidence_winner
from utils.metrics import confidence_stats, text_stats
from utils.exports import results_to_text, results_to_csv, results_to_json, word_table_to_csv
from utils.styles import inject_css, metric_grid, ocr_text_display, confidence_bar, page_header, engine_badge, status_badge, empty_state
from utils.sidebar import render_sidebar

# ── Logging ──────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Page config (must be FIRST Streamlit call) ───────────────────
st.set_page_config(
    page_title="OCR Playground",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get help": "https://github.com/YOUR_USERNAME/OCR-Playground",
        "Report a bug": "https://github.com/YOUR_USERNAME/OCR-Playground/issues",
        "About": "OCR Playground – Multilingual Multi-Engine OCR Research Platform",
    },
)

# ── Inject custom CSS ────────────────────────────────────────────
inject_css()

# ═══════════════════════════════════════════════════════════════════
# Engine instances (cached across reruns)
# ═══════════════════════════════════════════════════════════════════

@st.cache_resource(show_spinner=False)
def get_easy_engine() -> EasyOCREngine:
    """Return a cached EasyOCR engine instance (GPU=False for Streamlit Cloud)."""
    return EasyOCREngine(gpu=False)


@st.cache_resource(show_spinner=False)
def get_tess_engine() -> TesseractEngine:
    """Return a cached Tesseract engine instance."""
    return TesseractEngine()


# ═══════════════════════════════════════════════════════════════════
# Core OCR runner
# ═══════════════════════════════════════════════════════════════════

def run_ocr(
    image: np.ndarray,
    cfg: dict,
) -> dict[str, Optional[dict]]:
    """
    Run the selected OCR engines on the preprocessed image.

    Args:
        image: RGB numpy array.
        cfg:   Sidebar config dict.

    Returns:
        dict with keys "easyocr" and "tesseract", values are result dicts or None.
    """
    results: dict[str, Optional[dict]] = {"easyocr": None, "tesseract": None}

    if cfg["run_easyocr"]:
        with st.spinner("Running EasyOCR …"):
            try:
                engine = get_easy_engine()
                results["easyocr"] = engine.run(image, cfg["easyocr_lang"])
            except Exception as exc:
                logger.error("EasyOCR runtime error: %s", exc)
                results["easyocr"] = {
                    "engine": "EasyOCR", "lang_code": cfg["easyocr_lang"],
                    "text": "", "words": [], "avg_conf": 0.0,
                    "runtime_s": 0.0, "error": str(exc),
                }

    if cfg["run_tesseract"]:
        with st.spinner("Running Tesseract OCR …"):
            try:
                engine = get_tess_engine()
                results["tesseract"] = engine.run(image, cfg["tesseract_lang"])
            except Exception as exc:
                logger.error("Tesseract runtime error: %s", exc)
                results["tesseract"] = {
                    "engine": "Tesseract OCR", "lang_code": cfg["tesseract_lang"],
                    "text": "", "words": [], "avg_conf": 0.0,
                    "runtime_s": 0.0, "error": str(exc),
                }

    return results


# ═══════════════════════════════════════════════════════════════════
# Section renderers
# ═══════════════════════════════════════════════════════════════════

def render_image_info(image: np.ndarray, filename: str) -> None:
    """Display image metadata below the viewer."""
    info = get_image_info(image)
    st.markdown(
        f'<div style="font-size:0.72rem;color:#8B949E;margin-top:6px;font-family:monospace;">'
        f'<strong style="color:#00C9A7;">{filename}</strong> &nbsp;·&nbsp; '
        f'{info["width"]} × {info["height"]} px &nbsp;·&nbsp; '
        f'{info["channels"]}ch &nbsp;·&nbsp; {info["size_kb"]} KB'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_metrics_dashboard(results: dict, cfg: dict) -> None:
    """Render the top-level metrics dashboard cards."""
    st.markdown(
        '<div style="font-size:0.65rem;font-weight:600;letter-spacing:0.14em;'
        'text-transform:uppercase;color:#00C9A7;margin-bottom:12px;">'
        'Metrics Dashboard</div>',
        unsafe_allow_html=True,
    )

    easy = results.get("easyocr")
    tess = results.get("tesseract")

    # Aggregate totals
    total_words = 0
    total_conf  = []
    total_rt    = []

    for r in [easy, tess]:
        if r and r.get("error") is None:
            total_words += len(r.get("words", []))
            avg = r.get("avg_conf", 0)
            total_conf.append(avg * 100 if avg <= 1.0 else avg)
            total_rt.append(r.get("runtime_s", 0))

    avg_conf_disp = f"{sum(total_conf)/len(total_conf):.1f}%" if total_conf else "—"
    total_rt_disp = f"{sum(total_rt):.2f}s" if total_rt else "—"

    engines_run = sum([1 for r in [easy, tess] if r is not None])

    metric_grid([
    {"value": cfg["language"],       "label": "Language"},
    {"value": avg_conf_disp,         "label": "Avg Confidence"},
    {"value": total_rt_disp,         "label": "OCR Runtime"},
    {"value": str(engines_run),      "label": "Engines Run",         "color": "#8B949E"},
    {"value": str(language_count()), "label": "Languages Supported", "color": "#8B949E"},
])


def render_engine_result(result: dict, image: np.ndarray, show_confidence: bool) -> None:
    """
    Render a full result panel for one OCR engine inside a tab.

    Shows: status, text output, confidence bar, word table, annotated image.
    """
    engine_name = result.get("engine", "Engine")
    error       = result.get("error")
    words       = result.get("words", [])
    text        = result.get("text", "")
    avg_conf    = result.get("avg_conf", 0)
    runtime_s   = result.get("runtime_s", 0)

    avg_pct = avg_conf * 100 if avg_conf <= 1.0 else avg_conf

    # ── Status row ──────────────────────────────────────────────
    st.markdown(
        f'{engine_badge(engine_name)}'
        f'{status_badge(error is None)}',
        unsafe_allow_html=True,
    )

    if error:
        st.error(f"OCR failed: {error}", icon="🚨")
        return

    # ── Quick stats ──────────────────────────────────────────────
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Words detected", len(words))
    with c2:
        st.metric("Avg confidence", f"{avg_pct:.1f}%")
    with c3:
        st.metric("Runtime", f"{runtime_s:.3f}s")

    # ── Confidence bar ───────────────────────────────────────────
    confidence_bar(avg_pct, engine_name)

    # ── Extracted text ───────────────────────────────────────────
    st.markdown(
        '<div style="font-size:0.68rem;color:#8B949E;letter-spacing:0.08em;'
        'text-transform:uppercase;margin-top:14px;margin-bottom:4px;">Extracted text</div>',
        unsafe_allow_html=True,
    )
    ocr_text_display(text)

    # ── Annotated image ──────────────────────────────────────────
    if words:
        annotated = draw_bounding_boxes(image, words, engine_name, show_confidence)
        st.markdown(
            '<div style="font-size:0.68rem;color:#8B949E;letter-spacing:0.08em;'
            'text-transform:uppercase;margin:14px 0 6px 0;">Bounding boxes</div>',
            unsafe_allow_html=True,
        )
        st.image(annotated, use_container_width=True)

    # ── Per-word table (collapsible) ─────────────────────────────
    if words:
        with st.expander(f"Per-word detail ({len(words)} words)", expanded=False):
            df = _words_to_dataframe(words, engine_name)
            st.dataframe(df, use_container_width=True, hide_index=True)

            # Download per-word CSV
            word_csv = word_table_to_csv(words, engine_name)
            st.download_button(
                label="⬇  Download word table (.csv)",
                data=word_csv,
                file_name=f"words_{engine_name.replace(' ', '_').lower()}.csv",
                mime="text/csv",
                key=f"dl_words_{engine_name}",
            )


def render_comparison_tab(results: dict, image: np.ndarray) -> None:
    """Render the side-by-side comparison table and visualisation panel."""
    easy = results.get("easyocr")
    tess = results.get("tesseract")

    active = [r for r in [easy, tess] if r is not None and r.get("error") is None]
    if not active:
        st.info("No successful OCR results to compare.", icon="ℹ️")
        return

    # ── Comparison table ─────────────────────────────────────────
    bench_rows = build_benchmark_table(active)
    df_bench   = pd.DataFrame(bench_rows)
    st.dataframe(df_bench, use_container_width=True, hide_index=True)

    # ── Winner callouts ──────────────────────────────────────────
    spd  = speed_winner(active)
    conf = confidence_winner(active)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            f'<div class="ocr-card" style="text-align:center;padding:16px;">'
            f'<div class="ocr-card-title">⚡ Fastest engine</div>'
            f'<div style="font-size:1.1rem;color:#00C9A7;font-weight:700;">{spd}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f'<div class="ocr-card" style="text-align:center;padding:16px;">'
            f'<div class="ocr-card-title">🎯 Best confidence</div>'
            f'<div style="font-size:1.1rem;color:#00C9A7;font-weight:700;">{conf}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # ── Visual comparison chart ───────────────────────────────────
    st.markdown("---")
    _render_comparison_chart(active)

    # ── Side-by-side image panel ─────────────────────────────────
    st.markdown(
        '<div style="font-size:0.68rem;color:#8B949E;letter-spacing:0.08em;'
        'text-transform:uppercase;margin:18px 0 8px 0;">Bounding box comparison</div>',
        unsafe_allow_html=True,
    )

    easy_ann  = draw_bounding_boxes(image, easy["words"], "EasyOCR", False) if easy and not easy.get("error") else None
    tess_ann  = draw_bounding_boxes(image, tess["words"], "Tesseract OCR", False) if tess and not tess.get("error") else None
    panel     = create_comparison_panel(image, easy_ann, tess_ann)
    st.image(panel, caption="Original · EasyOCR (green) · Tesseract (blue)", use_container_width=True)


def render_visualisation_tab(results: dict, image: np.ndarray) -> None:
    """Detailed visualisation panel: per-engine annotated images + confidence histograms."""
    cols = st.columns([1, 1])

    for idx, (key, label) in enumerate([("easyocr", "EasyOCR"), ("tesseract", "Tesseract OCR")]):
        r = results.get(key)
        with cols[idx]:
            st.markdown(
                f'<div style="font-size:0.72rem;color:#8B949E;letter-spacing:0.08em;'
                f'text-transform:uppercase;margin-bottom:8px;">{label}</div>',
                unsafe_allow_html=True,
            )

            if r is None:
                st.markdown('<div style="color:#444D56;font-size:0.78rem;">Not run.</div>', unsafe_allow_html=True)
                continue
            if r.get("error"):
                st.error(r["error"])
                continue

            # Annotated image
            ann = draw_bounding_boxes(image, r["words"], r["engine"], True)
            st.image(ann, use_container_width=True)

            # Confidence histogram
            confs = [w.get("confidence", 0) for w in r["words"]]
            if confs:
                confs_pct = [c * 100 if c <= 1.0 else c for c in confs]
                color     = "#28A745" if "Easy" in label else "#1A6FB5"
                fig, ax   = plt.subplots(figsize=(5, 2.5))
                fig.patch.set_facecolor("#161B22")
                ax.set_facecolor("#0D1117")
                ax.hist(confs_pct, bins=20, color=color, edgecolor="none", alpha=0.85)
                mean = sum(confs_pct) / len(confs_pct)
                ax.axvline(mean, color="#00C9A7", lw=1.5, ls="--", label=f"Mean {mean:.1f}%")
                ax.legend(fontsize=7, facecolor="#161B22", labelcolor="#E6EDF3", edgecolor="none")
                ax.set_xlabel("Confidence (%)", fontsize=7.5, color="#8B949E")
                ax.set_ylabel("Words", fontsize=7.5, color="#8B949E")
                ax.tick_params(colors="#8B949E", labelsize=7)
                for sp in ax.spines.values():
                    sp.set_edgecolor("#30363D")
                plt.tight_layout()
                st.pyplot(fig, use_container_width=True)
                plt.close(fig)


def render_download_section(
    results: dict,
    language: str,
    filename: str,
) -> None:
    """Render the Download section with text, CSV, and JSON options."""
    st.markdown(
        '<div class="ocr-card-title" style="margin-bottom:16px;">Download results</div>',
        unsafe_allow_html=True,
    )

    active = [r for r in results.values() if r is not None]
    if not active:
        st.info("Run OCR first to enable downloads.", icon="ℹ️")
        return

    txt_data  = results_to_text(active, language)
    csv_data  = results_to_csv(active, language)
    json_data = results_to_json(active, language, filename)

    ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
    stem = filename.rsplit(".", 1)[0] if "." in filename else filename

    c1, c2, c3 = st.columns(3)
    with c1:
        st.download_button(
            label="⬇  Text report (.txt)",
            data=txt_data,
            file_name=f"ocr_{stem}_{ts}.txt",
            mime="text/plain",
            use_container_width=True,
        )
    with c2:
        st.download_button(
            label="⬇  CSV results (.csv)",
            data=csv_data,
            file_name=f"ocr_{stem}_{ts}.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with c3:
        st.download_button(
            label="⬇  Full JSON (.json)",
            data=json_data,
            file_name=f"ocr_{stem}_{ts}.json",
            mime="application/json",
            use_container_width=True,
        )

    # Extracted-text downloads per engine
    for r in active:
        if r.get("text") and not r.get("error"):
            eng_label = r["engine"].replace(" ", "_").lower()
            st.download_button(
                label=f"⬇  {r['engine']} text only (.txt)",
                data=(r["text"] or "").encode("utf-8"),
                file_name=f"text_{eng_label}_{stem}_{ts}.txt",
                mime="text/plain",
                key=f"dl_txt_{eng_label}",
            )


# ═══════════════════════════════════════════════════════════════════
# Internal helpers
# ═══════════════════════════════════════════════════════════════════

def _words_to_dataframe(words: list[dict], engine: str) -> pd.DataFrame:
    """Convert a words list to a display-ready DataFrame."""
    rows = []
    for w in words:
        conf = w.get("confidence", 0)
        conf_pct = round(conf * 100 if conf <= 1.0 else conf, 1)
        bbox = w.get("bbox", [0, 0, 0, 0])
        rows.append({
            "Word":       w.get("text", ""),
            "Conf (%)":   conf_pct,
            "x1": bbox[0] if len(bbox) > 0 else 0,
            "y1": bbox[1] if len(bbox) > 1 else 0,
            "x2": bbox[2] if len(bbox) > 2 else 0,
            "y2": bbox[3] if len(bbox) > 3 else 0,
        })
    return pd.DataFrame(rows)


def _render_comparison_chart(active: list[dict]) -> None:
    """Bar chart comparing runtime and confidence side-by-side."""
    names     = [r["engine"] for r in active]
    runtimes  = [r.get("runtime_s", 0) for r in active]
    avg_confs = [r.get("avg_conf", 0) for r in active]
    avg_pcts  = [c * 100 if c <= 1.0 else c for c in avg_confs]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 3.5))
    fig.patch.set_facecolor("#161B22")

    colors = ["#28A745", "#1A6FB5"]

    for ax in (ax1, ax2):
        ax.set_facecolor("#0D1117")
        ax.tick_params(colors="#8B949E", labelsize=8)
        for sp in ax.spines.values():
            sp.set_edgecolor("#30363D")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    # Runtime bars
    bars1 = ax1.bar(names, runtimes, color=colors[:len(names)], width=0.4, edgecolor="none")
    for bar, val in zip(bars1, runtimes):
        ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                 f"{val:.3f}s", ha="center", va="bottom", fontsize=8, color="#E6EDF3")
    ax1.set_title("Runtime (s)", color="#E6EDF3", fontsize=9, pad=8)
    ax1.set_ylabel("seconds", fontsize=8, color="#8B949E")
    ax1.set_ylim(0, max(runtimes) * 1.4 if runtimes else 1)
    ax1.tick_params(axis="x", colors="#E6EDF3")

    # Confidence bars
    bars2 = ax2.bar(names, avg_pcts, color=colors[:len(names)], width=0.4, edgecolor="none")
    for bar, val in zip(bars2, avg_pcts):
        ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                 f"{val:.1f}%", ha="center", va="bottom", fontsize=8, color="#E6EDF3")
    ax2.set_title("Avg Confidence (%)", color="#E6EDF3", fontsize=9, pad=8)
    ax2.set_ylabel("percent", fontsize=8, color="#8B949E")
    ax2.set_ylim(0, 115)
    ax2.tick_params(axis="x", colors="#E6EDF3")

    plt.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)


# ═══════════════════════════════════════════════════════════════════
# Main application
# ═══════════════════════════════════════════════════════════════════

def main() -> None:
    """
    Main Streamlit application entry point.

    Layout:
      Left sidebar  – language, engine, processing options
      Main area     – upload → image viewer → Run → tabbed results
    """

    # ── Sidebar ──────────────────────────────────────────────────
    cfg = render_sidebar()

    # ── Page header ───────────────────────────────────────────────
    page_header()

    # ═══════════════════════════════════
    # IMAGE UPLOAD
    # ═══════════════════════════════════
    st.markdown(
        '<div class="ocr-card-title">Upload image</div>',
        unsafe_allow_html=True,
    )
    uploaded_file = st.file_uploader(
        "Choose an image",
        type=["png", "jpg", "jpeg", "bmp", "tiff", "webp"],
        label_visibility="collapsed",
        help="Supported: PNG, JPG, JPEG, BMP, TIFF, WebP · Max 10 MB",
    )

    # ───────────────────────────────────
    # Guard: no upload → empty state
    # ───────────────────────────────────
    if uploaded_file is None:
        st.markdown("---")
        empty_state(
            "Upload an image above to begin OCR analysis.<br>"
            "Supports PNG · JPG · JPEG · BMP · TIFF · WebP · Max 10 MB"
        )
        return

    # ───────────────────────────────────
    # Validate upload
    # ───────────────────────────────────
    raw_bytes = uploaded_file.read()
    valid, err_msg = validate_upload(raw_bytes, uploaded_file.name)
    if not valid:
        st.error(f"Invalid file: {err_msg}", icon="🚨")
        return

    # ───────────────────────────────────
    # Decode image
    # ───────────────────────────────────
    try:
        image_rgb = load_image_from_bytes(raw_bytes)
    except ValueError as exc:
        st.error(str(exc), icon="🚨")
        return

    # ───────────────────────────────────
    # Pre-process (optional)
    # ───────────────────────────────────
    ocr_image = image_rgb
    if cfg["enhance_image"]:
        with st.spinner("Pre-processing image …"):
            ocr_image = enhance_for_ocr(
                image_rgb,
                contrast=cfg["enhance_contrast"],
                sharpness=cfg["enhance_sharp"],
            )

    # ═══════════════════════════════════
    # IMAGE VIEWER
    # ═══════════════════════════════════
    st.markdown("---")
    col_img, col_run = st.columns([3, 1])

    with col_img:
        st.markdown(
            '<div class="ocr-card-title">Image preview</div>',
            unsafe_allow_html=True,
        )
        display_image = ocr_image if cfg["enhance_image"] else image_rgb
        st.image(display_image, use_container_width=True)
        render_image_info(image_rgb, uploaded_file.name)

    with col_run:
        st.markdown(
            '<div class="ocr-card-title">Run OCR</div>',
            unsafe_allow_html=True,
        )
        if not cfg["run_easyocr"] and not cfg["run_tesseract"]:
            st.warning("Select at least one engine in the sidebar.", icon="⚠️")
            return

        # Engine selection summary
        engines_selected = []
        if cfg["run_easyocr"]:   engines_selected.append("EasyOCR")
        if cfg["run_tesseract"]: engines_selected.append("Tesseract")
        st.markdown(
            '<div style="font-size:0.72rem;color:#8B949E;margin-bottom:10px;">'
            f'Engines: <strong style="color:#E6EDF3;">{" · ".join(engines_selected)}</strong><br>'
            f'Language: <strong style="color:#E6EDF3;">{cfg["language"]}</strong>'
            '</div>',
            unsafe_allow_html=True,
        )

        run_pressed = st.button(
            "▶  Run OCR",
            use_container_width=True,
            type="primary",
        )

        if cfg["enhance_image"]:
            st.markdown(
                f'<div style="font-size:0.68rem;color:#D29922;margin-top:8px;">'
                f'⚙ Pre-processing active<br>'
                f'Contrast ×{cfg["enhance_contrast"]:.1f} · Sharp ×{cfg["enhance_sharp"]:.1f}'
                f'</div>',
                unsafe_allow_html=True,
            )

    # ───────────────────────────────────
    # Guard: button not pressed
    # ───────────────────────────────────
    if not run_pressed:
        # Check session state for previous results
        if "ocr_results" not in st.session_state:
            st.markdown("---")
            st.markdown(
                '<div style="font-size:0.78rem;color:#8B949E;text-align:center;padding:24px 0;">'
                'Press <strong style="color:#00C9A7;">▶ Run OCR</strong> to start analysis.'
                '</div>',
                unsafe_allow_html=True,
            )
            return
        # Use cached results from previous run
        results      = st.session_state["ocr_results"]
        last_file    = st.session_state.get("ocr_filename", uploaded_file.name)
        last_image   = st.session_state.get("ocr_image", image_rgb)
    else:
        # ─────────────────────────────
        # Run OCR
        # ─────────────────────────────
        results = run_ocr(ocr_image, cfg)

        # Persist to session state so results survive widget interactions
        st.session_state["ocr_results"]  = results
        st.session_state["ocr_filename"] = uploaded_file.name
        st.session_state["ocr_image"]    = ocr_image
        last_file  = uploaded_file.name
        last_image = ocr_image

    # ───────────────────────────────────
    # Guard: no results at all
    # ───────────────────────────────────
    all_results = [r for r in results.values() if r is not None]
    if not all_results:
        st.warning("No OCR results available. Enable at least one engine.", icon="⚠️")
        return

    # ═══════════════════════════════════
    # METRICS DASHBOARD
    # ═══════════════════════════════════
    st.markdown("---")
    render_metrics_dashboard(results, cfg)

    # ═══════════════════════════════════
    # TABBED RESULTS
    # ═══════════════════════════════════
    st.markdown("---")

    tab_labels = []
    if results.get("easyocr"):    tab_labels.append("EasyOCR")
    if results.get("tesseract"):  tab_labels.append("Tesseract OCR")
    if len(tab_labels) > 1:
        tab_labels += ["Comparison", "Visualisation"]
    tab_labels.append("Download")

    tabs = st.tabs(tab_labels)
    tab_idx = 0

    if results.get("easyocr"):
        with tabs[tab_idx]:
            render_engine_result(
                results["easyocr"], last_image, cfg["show_confidence"]
            )
        tab_idx += 1

    if results.get("tesseract"):
        with tabs[tab_idx]:
            render_engine_result(
                results["tesseract"], last_image, cfg["show_confidence"]
            )
        tab_idx += 1

    if len([r for r in results.values() if r]) > 1:
        with tabs[tab_idx]:
            render_comparison_tab(results, last_image)
        tab_idx += 1

        with tabs[tab_idx]:
            render_visualisation_tab(results, last_image)
        tab_idx += 1

    # Download tab is always last
    with tabs[tab_idx]:
        render_download_section(results, cfg["language"], last_file)


# ── Entry point ───────────────────────────────────────────────────
if __name__ == "__main__":
    main()
