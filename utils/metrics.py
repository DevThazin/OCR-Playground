"""
utils/metrics.py
-----------------
OCR quality metrics: confidence statistics, text statistics,
and (where ground truth is available) CER / WER.

Phase 1 implements confidence and text statistics.
CER / WER stubs are included, ready for Phase 5.
"""

import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Confidence statistics
# ---------------------------------------------------------------------------

def confidence_stats(words: list) -> dict:
    """
    Compute confidence statistics over a list of word dicts.

    Args:
        words: List of dicts, each containing a "confidence" key.
               Values may be in 0–1 or 0–100 range; the function
               normalises to 0–100 for all returned values.

    Returns:
        dict with keys:
            count, mean_pct, min_pct, max_pct, high_conf_ratio
        All percentage values are rounded to 1 decimal place.
        Returns all-zero dict if words is empty.
    """
    confs = [w.get("confidence") for w in words if w.get("confidence") is not None]
    if not confs:
        return {"count": 0, "mean_pct": 0.0, "min_pct": 0.0, "max_pct": 0.0, "high_conf_ratio": 0.0}

    # Normalise to 0–100
    confs_pct = [c * 100 if c <= 1.0 else c for c in confs]

    high_threshold = 80.0
    high_conf_ratio = sum(1 for c in confs_pct if c >= high_threshold) / len(confs_pct)

    return {
        "count": len(confs_pct),
        "mean_pct": round(sum(confs_pct) / len(confs_pct), 1),
        "min_pct": round(min(confs_pct), 1),
        "max_pct": round(max(confs_pct), 1),
        "high_conf_ratio": round(high_conf_ratio, 3),
    }


# ---------------------------------------------------------------------------
# Text statistics
# ---------------------------------------------------------------------------

def text_stats(text: str) -> dict:
    """
    Compute basic statistics about an OCR output string.

    Args:
        text: Raw text string from an OCR engine.

    Returns:
        dict with keys:
            char_count, word_count, line_count,
            unique_words, avg_word_length
    """
    if not text or not text.strip():
        return {
            "char_count": 0,
            "word_count": 0,
            "line_count": 0,
            "unique_words": 0,
            "avg_word_length": 0.0,
        }

    words = re.findall(r"\S+", text)
    lines = [ln for ln in text.splitlines() if ln.strip()]
    avg_wl = sum(len(w) for w in words) / len(words) if words else 0.0

    return {
        "char_count": len(text),
        "word_count": len(words),
        "line_count": len(lines),
        "unique_words": len(set(w.lower() for w in words)),
        "avg_word_length": round(avg_wl, 2),
    }


# ---------------------------------------------------------------------------
# CER / WER  (Phase 5 stubs)
# ---------------------------------------------------------------------------

def character_error_rate(hypothesis: str, reference: str) -> float:
    """
    Compute Character Error Rate (CER) between hypothesis and reference.

    CER = edit_distance(hyp_chars, ref_chars) / len(ref_chars)

    Args:
        hypothesis: OCR-produced text.
        reference:  Ground-truth text.

    Returns:
        Float in [0, ∞). 0.0 = perfect. Capped display at 1.0 recommended.
    """
    if not reference:
        return 0.0 if not hypothesis else 1.0

    hyp_chars = list(hypothesis)
    ref_chars = list(reference)
    dist = _levenshtein(hyp_chars, ref_chars)
    return round(dist / len(ref_chars), 4)


def word_error_rate(hypothesis: str, reference: str) -> float:
    """
    Compute Word Error Rate (WER) between hypothesis and reference.

    WER = edit_distance(hyp_words, ref_words) / len(ref_words)

    Args:
        hypothesis: OCR-produced text.
        reference:  Ground-truth text.

    Returns:
        Float in [0, ∞). 0.0 = perfect.
    """
    hyp_words = hypothesis.split()
    ref_words = reference.split()
    if not ref_words:
        return 0.0 if not hyp_words else 1.0
    dist = _levenshtein(hyp_words, ref_words)
    return round(dist / len(ref_words), 4)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _levenshtein(seq1: list, seq2: list) -> int:
    """
    Compute Levenshtein edit distance between two sequences.

    Args:
        seq1: List of characters or words (hypothesis).
        seq2: List of characters or words (reference).

    Returns:
        Integer edit distance.
    """
    m, n = len(seq1), len(seq2)
    # Use a rolling 1D DP array to keep memory O(n)
    dp = list(range(n + 1))

    for i in range(1, m + 1):
        prev = dp[0]
        dp[0] = i
        for j in range(1, n + 1):
            temp = dp[j]
            if seq1[i - 1] == seq2[j - 1]:
                dp[j] = prev
            else:
                dp[j] = 1 + min(prev, dp[j], dp[j - 1])
            prev = temp

    return dp[n]
