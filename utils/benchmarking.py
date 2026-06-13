"""
utils/benchmarking.py
----------------------
Runtime and resource benchmarking helpers.

Wraps OCR engine calls with timing, and aggregates results into
a summary structure suitable for display in Colab or Streamlit.
"""

import time
import logging
from typing import Callable, Any

logger = logging.getLogger(__name__)


def timed_run(func: Callable, *args, **kwargs) -> tuple[Any, float]:
    """
    Call a function and measure its wall-clock execution time.

    Args:
        func:   Callable to execute.
        *args:  Positional arguments forwarded to func.
        **kwargs: Keyword arguments forwarded to func.

    Returns:
        Tuple (result, elapsed_seconds).
    """
    t0 = time.perf_counter()
    result = func(*args, **kwargs)
    elapsed = round(time.perf_counter() - t0, 4)
    return result, elapsed


def build_benchmark_table(results: list[dict]) -> list[dict]:
    """
    Convert a list of OCR result dicts into a benchmark-summary table.

    Args:
        results: List of dicts returned by EasyOCREngine.run() or
                 TesseractEngine.run().

    Returns:
        List of dicts, one row per engine:
            engine, lang_code, runtime_s, word_count,
            avg_conf_pct, text_length, status
    """
    rows = []
    for r in results:
        avg_conf = r.get("avg_conf", 0.0)
        # Normalise to a 0–100 percentage for display
        avg_conf_pct = avg_conf * 100 if avg_conf <= 1.0 else avg_conf

        rows.append({
            "Engine": r.get("engine", "?"),
            "Language": r.get("lang_code", "?"),
            "Runtime (s)": r.get("runtime_s", 0.0),
            "Words Detected": len(r.get("words", [])),
            "Avg Confidence (%)": round(avg_conf_pct, 1),
            "Text Length (chars)": len(r.get("text", "")),
            "Status": "✓ OK" if r.get("error") is None else f"✗ {r['error'][:50]}",
        })
    return rows


def speed_winner(results: list[dict]) -> str:
    """
    Return the engine name with the lowest runtime.

    Args:
        results: List of OCR result dicts.

    Returns:
        Engine name string, or "N/A" if results is empty.
    """
    valid = [r for r in results if r.get("error") is None]
    if not valid:
        return "N/A"
    fastest = min(valid, key=lambda r: r.get("runtime_s", float("inf")))
    return fastest.get("engine", "N/A")


def confidence_winner(results: list[dict]) -> str:
    """
    Return the engine name with the highest average confidence.

    Args:
        results: List of OCR result dicts.

    Returns:
        Engine name string, or "N/A".
    """
    valid = [r for r in results if r.get("error") is None]
    if not valid:
        return "N/A"
    best = max(valid, key=lambda r: r.get("avg_conf", 0.0))
    return best.get("engine", "N/A")
