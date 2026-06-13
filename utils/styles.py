"""
utils/styles.py
----------------
All custom CSS for the OCR Playground Streamlit UI.

Design rationale:
  Palette  — Deep GitHub-dark (#0D1117) base, with a single teal accent (#00C9A7)
             that reads like a scanning laser — appropriate for an OCR tool.
  Type     — System monospace for everything: metrics, code, extracted text.
             This makes raw OCR output feel like a terminal readout, not an error.
  Signature— The "scan-line" animated header bar: a single teal line that sweeps
             across the page title, evoking an optical scanner in motion.
             Justified: the app IS a scanner. One risk, rest is quiet.
  Layout   — Card-based sections with 1px teal-tinted borders. No gradients,
             no rounded-pill buttons — precision over friendliness.
"""

CUSTOM_CSS = """
<style>
/* ── Google Font import ─────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;600;700&display=swap');

/* ── Root tokens ────────────────────────────────────────────────── */
:root {
    /* Backgrounds */
    --bg-base:      #0A0F1F;
    --bg-card:      #121A2B;
    --bg-card-alt:  #1B2540;

    /* Main Accent (AI Blue) */
    --accent:       #5B8CFF;
    --accent-dim:   rgba(91, 140, 255, 0.15);
    --accent-mid:   rgba(91, 140, 255, 0.35);

    /* Text */
    --text-primary: #F8FAFC;
    --text-muted:   #94A3B8;
    --text-code:    #8B5CF6;

    /* Borders */
    --border:       rgba(91, 140, 255, 0.18);
    --border-solid: #334155;

    /* Engine Colors */
    --easy-color:   #22C55E;
    --tess-color:   #3B82F6;

    /* Status */
    --danger:       #EF4444;
    --warn:         #F59E0B;

    /* Typography */
    --mono:         'JetBrains Mono', 'Fira Code', 'Courier New', monospace;

    /* Radius */
    --radius:       6px;
}

/* ── Base overrides ─────────────────────────────────────────────── */
html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg-base) !important;
    font-family: var(--mono) !important;
    color: var(--text-primary) !important;
}

[data-testid="stSidebar"] {
    background-color: var(--bg-card) !important;
    border-right: 1px solid var(--border-solid) !important;
}

[data-testid="stSidebar"] * {
    font-family: var(--mono) !important;
}

/* ── Header scan-line animation (signature element) ────────────── */
.ocr-header {
    position: relative;
    padding: 28px 0 20px 0;
    border-bottom: 1px solid var(--border);
    margin-bottom: 28px;
    overflow: hidden;
}

.ocr-header::after {
    content: '';
    position: absolute;
    left: -100%;
    top: 0;
    height: 2px;
    width: 60%;
    background: linear-gradient(90deg, transparent, var(--accent), transparent);
    animation: scan 3s ease-in-out infinite;
}

@keyframes scan {
    0%   { left: -60%; }
    100% { left: 110%; }
}

.ocr-title {
    font-family: var(--mono) !important;
    font-size: 1.75rem !important;
    font-weight: 700 !important;
    color: var(--accent) !important;
    letter-spacing: -0.5px;
    margin: 0 0 4px 0;
}

.ocr-subtitle {
    font-size: 0.78rem;
    color: var(--text-muted);
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

/* ── Cards ──────────────────────────────────────────────────────── */
.ocr-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 20px 22px;
    margin-bottom: 18px;
}

.ocr-card-title {
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--accent);
    border-bottom: 1px solid var(--border);
    padding-bottom: 8px;
    margin-bottom: 14px;
}

/* ── Engine badge ───────────────────────────────────────────────── */
.engine-badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 2px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    margin-right: 8px;
}

.badge-easy    { background: rgba(40,167,69,0.18);  color: #28A745; border: 1px solid rgba(40,167,69,0.35); }
.badge-tess    { background: rgba(26,111,181,0.18); color: #79C0FF; border: 1px solid rgba(26,111,181,0.35); }
.badge-ok      { background: rgba(0,201,167,0.12);  color: var(--accent); border: 1px solid var(--border); }
.badge-error   { background: rgba(248,81,73,0.12);  color: var(--danger); border: 1px solid rgba(248,81,73,0.35); }

/* ── Metrics ────────────────────────────────────────────────────── */
.metric-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
    gap: 12px;
    margin: 16px 0;
}

.metric-box {
    background: var(--bg-card-alt);
    border: 1px solid var(--border-solid);
    border-radius: var(--radius);
    padding: 14px 16px;
    text-align: center;
}

.metric-value {
    font-size: 1.55rem;
    font-weight: 700;
    color: var(--accent);
    line-height: 1.1;
    display: block;
}

.metric-label {
    font-size: 0.68rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-top: 4px;
    display: block;
}

/* ── OCR text output ────────────────────────────────────────────── */
.ocr-text-box {
    background: #010409;
    border: 1px solid var(--border-solid);
    border-radius: var(--radius);
    padding: 14px 16px;
    font-family: var(--mono) !important;
    font-size: 0.82rem;
    line-height: 1.65;
    color: var(--text-code);
    white-space: pre-wrap;
    word-break: break-word;
    max-height: 280px;
    overflow-y: auto;
    margin: 10px 0;
}

.ocr-text-box::-webkit-scrollbar { width: 4px; }
.ocr-text-box::-webkit-scrollbar-track { background: transparent; }
.ocr-text-box::-webkit-scrollbar-thumb { background: var(--accent-mid); border-radius: 2px; }

/* ── Confidence bar ─────────────────────────────────────────────── */
.conf-bar-wrap { margin: 6px 0 12px 0; }
.conf-bar-label {
    font-size: 0.68rem;
    color: var(--text-muted);
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-bottom: 4px;
}

.conf-bar-track {
    height: 6px;
    background: var(--bg-card-alt);
    border-radius: 3px;
    overflow: hidden;
}

.conf-bar-fill {
    height: 100%;
    border-radius: 3px;
    transition: width 0.4s ease;
}

/* ── Table overrides ────────────────────────────────────────────── */
[data-testid="stDataFrame"] table {
    font-family: var(--mono) !important;
    font-size: 0.78rem !important;
}

[data-testid="stDataFrame"] th {
    background: var(--bg-card-alt) !important;
    color: var(--accent) !important;
    font-size: 0.68rem !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    border-bottom: 1px solid var(--border) !important;
}

/* ── Streamlit widget overrides ─────────────────────────────────── */
[data-testid="stSelectbox"] > div,
[data-testid="stMultiSelect"] > div {
    background: var(--bg-card-alt) !important;
    border-color: var(--border-solid) !important;
    font-family: var(--mono) !important;
    font-size: 0.82rem !important;
}

[data-testid="stFileUploader"] {
    background: var(--bg-card) !important;
    border: 1px dashed var(--border) !important;
    border-radius: var(--radius) !important;
}

div.stButton > button {
    background: var(--accent-dim) !important;
    color: var(--accent) !important;
    border: 1px solid var(--accent-mid) !important;
    border-radius: var(--radius) !important;
    font-family: var(--mono) !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.06em !important;
    padding: 0.45rem 1.2rem !important;
    transition: background 0.15s ease, border-color 0.15s ease !important;
}

div.stButton > button:hover {
    background: rgba(0,201,167,0.28) !important;
    border-color: var(--accent) !important;
}

/* Download buttons */
[data-testid="stDownloadButton"] > button {
    background: var(--bg-card-alt) !important;
    color: var(--text-muted) !important;
    border: 1px solid var(--border-solid) !important;
    border-radius: var(--radius) !important;
    font-family: var(--mono) !important;
    font-size: 0.78rem !important;
    transition: color 0.15s ease, border-color 0.15s ease !important;
}

[data-testid="stDownloadButton"] > button:hover {
    color: var(--accent) !important;
    border-color: var(--accent-mid) !important;
}

/* Tabs */
[data-testid="stTabs"] [role="tab"] {
    font-family: var(--mono) !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    color: var(--text-muted) !important;
}

[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom-color: var(--accent) !important;
}

/* Expander */
[data-testid="stExpander"] {
    border: 1px solid var(--border-solid) !important;
    border-radius: var(--radius) !important;
    background: var(--bg-card) !important;
}

/* Status / info boxes */
[data-testid="stAlert"] {
    font-family: var(--mono) !important;
    font-size: 0.8rem !important;
}

/* Divider */
hr {
    border-color: var(--border-solid) !important;
    margin: 20px 0 !important;
}

/* Sidebar section headings */
.sidebar-section {
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--accent);
    margin: 18px 0 8px 0;
    padding-bottom: 4px;
    border-bottom: 1px solid var(--border);
}

/* Language dashboard pill */
.lang-dashboard {
    background: var(--bg-card-alt);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 10px 14px;
    margin: 10px 0;
    font-size: 0.75rem;
}

.lang-dashboard strong { color: var(--accent); }

/* Status indicator dot */
.status-dot {
    display: inline-block;
    width: 7px; height: 7px;
    border-radius: 50%;
    margin-right: 6px;
    vertical-align: middle;
}
.dot-ok    { background: #28A745; box-shadow: 0 0 4px rgba(40,167,69,0.5); }
.dot-error { background: var(--danger); }
.dot-warn  { background: var(--warn); }

/* Empty state */
.empty-state {
    text-align: center;
    padding: 56px 24px;
    color: var(--text-muted);
}
.empty-state-icon { font-size: 3rem; margin-bottom: 16px; }
.empty-state-text { font-size: 0.85rem; line-height: 1.6; }

/* Comparison winner highlight */
.winner-chip {
    display: inline-block;
    background: rgba(0,201,167,0.12);
    color: var(--accent);
    border: 1px solid var(--accent-mid);
    border-radius: 2px;
    padding: 1px 8px;
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    margin-left: 6px;
    vertical-align: middle;
}

/* Scrollbar global */
* { scrollbar-width: thin; scrollbar-color: var(--accent-mid) transparent; }
</style>
"""


def inject_css() -> None:
    """Inject the custom CSS into the Streamlit page."""
    import streamlit as st
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def card(title: str, content: str, unsafe_allow_html: bool = True) -> None:
    """Render a styled card with a small-caps title."""
    import streamlit as st
    st.markdown(
        f'<div class="ocr-card">'
        f'<div class="ocr-card-title">{title}</div>'
        f'{content}'
        f'</div>',
        unsafe_allow_html=True,
    )


def metric_grid(metrics: list[dict]) -> None:
    """
    Render a horizontal grid of metric boxes.

    Args:
        metrics: List of dicts with keys: value, label, (optional) color.
    """
    import streamlit as st
    boxes = ""
    for m in metrics:
        color = m.get("color", "var(--accent)")
        boxes += (
            f'<div class="metric-box">'
            f'<span class="metric-value" style="color:{color}">{m["value"]}</span>'
            f'<span class="metric-label">{m["label"]}</span>'
            f'</div>'
        )
    st.markdown(f'<div class="metric-grid">{boxes}</div>', unsafe_allow_html=True)


def ocr_text_display(text: str) -> None:
    """Display extracted OCR text in a styled monospace scrollable box."""
    import streamlit as st
    import html
    safe = html.escape(text or "(no text detected)")
    st.markdown(f'<div class="ocr-text-box">{safe}</div>', unsafe_allow_html=True)


def confidence_bar(value_pct: float, engine: str) -> None:
    """
    Render a thin horizontal confidence bar.

    Args:
        value_pct: Confidence as 0–100.
        engine:    Engine name for colour selection.
    """
    import streamlit as st
    color = "#28A745" if "Easy" in engine else "#1A6FB5"
    pct   = max(0.0, min(100.0, value_pct))
    st.markdown(
        f'<div class="conf-bar-wrap">'
        f'<div class="conf-bar-label">avg confidence — {pct:.1f}%</div>'
        f'<div class="conf-bar-track">'
        f'<div class="conf-bar-fill" style="width:{pct}%;background:{color}"></div>'
        f'</div></div>',
        unsafe_allow_html=True,
    )


def engine_badge(engine: str) -> str:
    """Return an HTML badge span for an engine name."""
    cls = "badge-easy" if "Easy" in engine else "badge-tess"
    return f'<span class="engine-badge {cls}">{engine}</span>'


def status_badge(ok: bool, label: str = "") -> str:
    """Return a coloured OK / ERROR badge."""
    if ok:
        return f'<span class="engine-badge badge-ok">✓ {label or "OK"}</span>'
    return f'<span class="engine-badge badge-error">✗ {label or "Error"}</span>'


def page_header() -> None:
    """Render the animated scan-line page header."""
    import streamlit as st
    st.markdown(
        '<div class="ocr-header">'
        '<div class="ocr-title">OCR Playground</div>'
        '<div class="ocr-subtitle">multilingual · multi-engine · research platform</div>'
        '</div>',
        unsafe_allow_html=True,
    )


def empty_state(message: str = "Upload an image to begin.") -> None:
    """Render a centred empty-state placeholder."""
    import streamlit as st
    st.markdown(
        f'<div class="empty-state">'
        f'<div class="empty-state-icon">⬡</div>'
        f'<div class="empty-state-text">{message}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
