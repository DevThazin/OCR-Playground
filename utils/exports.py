"""
utils/exports.py
-----------------
Generate downloadable artefacts from OCR results:
  - Plain text (.txt)
  - CSV comparison table (.csv)
  - JSON full results (.json)

All functions return bytes ready for st.download_button.
"""

import csv
import io
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def results_to_text(results: list[dict], language: str) -> bytes:
    """
    Build a human-readable text report of all OCR results.

    Args:
        results:  List of OCR result dicts (one per engine).
        language: Selected language display name.

    Returns:
        UTF-8 encoded bytes of the text report.
    """
    lines = []
    ts    = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines.append("=" * 60)
    lines.append("  OCR PLAYGROUND – EXTRACTED TEXT REPORT")
    lines.append(f"  Generated : {ts}")
    lines.append(f"  Language  : {language}")
    lines.append("=" * 60)

    for r in results:
        lines.append("")
        lines.append(f"── {r.get('engine', 'Unknown')} ──")
        lines.append(f"  Language code  : {r.get('lang_code', '?')}")
        lines.append(f"  Runtime        : {r.get('runtime_s', 0):.4f} s")
        lines.append(f"  Words detected : {len(r.get('words', []))}")
        avg = r.get("avg_conf", 0)
        avg_pct = avg * 100 if avg <= 1.0 else avg
        lines.append(f"  Avg confidence : {avg_pct:.1f}%")
        lines.append(f"  Status         : {'OK' if r.get('error') is None else r['error']}")
        lines.append("")
        lines.append("  Extracted text:")
        lines.append("  " + "─" * 40)
        for ln in (r.get("text") or "(no text detected)").splitlines():
            lines.append("  " + ln)
        lines.append("  " + "─" * 40)

    lines.append("")
    lines.append("=" * 60)
    lines.append("  End of report")
    lines.append("=" * 60)

    return "\n".join(lines).encode("utf-8")


def results_to_csv(results: list[dict], language: str) -> bytes:
    """
    Build a CSV comparison table of OCR results.

    Columns: Engine, Language, Runtime_s, Words_Detected,
             Avg_Confidence_pct, Text_Length_chars, Status

    Args:
        results:  List of OCR result dicts.
        language: Selected language display name.

    Returns:
        UTF-8 bytes of the CSV file (with BOM for Excel compatibility).
    """
    buf = io.StringIO()
    writer = csv.DictWriter(
        buf,
        fieldnames=[
            "Engine", "Language", "Lang_Code",
            "Runtime_s", "Words_Detected",
            "Avg_Confidence_pct", "Text_Length_chars",
            "Status", "Extracted_Text",
        ],
    )
    writer.writeheader()

    for r in results:
        avg = r.get("avg_conf", 0)
        avg_pct = round(avg * 100 if avg <= 1.0 else avg, 1)
        writer.writerow({
            "Engine":             r.get("engine", "?"),
            "Language":           language,
            "Lang_Code":          r.get("lang_code", "?"),
            "Runtime_s":          r.get("runtime_s", 0),
            "Words_Detected":     len(r.get("words", [])),
            "Avg_Confidence_pct": avg_pct,
            "Text_Length_chars":  len(r.get("text") or ""),
            "Status":             "OK" if r.get("error") is None else r["error"],
            "Extracted_Text":     (r.get("text") or "").replace("\n", " "),
        })

    # UTF-8 BOM ensures Excel opens it correctly
    return ("\ufeff" + buf.getvalue()).encode("utf-8")


def results_to_json(results: list[dict], language: str, filename: str) -> bytes:
    """
    Serialise full OCR results to JSON (minus non-serialisable numpy arrays).

    Args:
        results:  List of OCR result dicts.
        language: Selected language display name.
        filename: Original uploaded image filename.

    Returns:
        UTF-8 JSON bytes.
    """
    ts = datetime.now().isoformat(timespec="seconds")

    # Strip bbox_raw (list of lists — serialisable but verbose)
    # and keep the flat bbox for each word
    clean_results = []
    for r in results:
        words_clean = []
        for w in r.get("words", []):
            words_clean.append({
                "text":       w.get("text", ""),
                "confidence": w.get("confidence"),
                "bbox":       w.get("bbox"),
            })

        avg = r.get("avg_conf", 0)
        avg_pct = round(avg * 100 if avg <= 1.0 else avg, 1)

        clean_results.append({
            "engine":           r.get("engine"),
            "lang_code":        str(r.get("lang_code", "")),
            "runtime_s":        r.get("runtime_s"),
            "words_detected":   len(r.get("words", [])),
            "avg_confidence_pct": avg_pct,
            "text_length":      len(r.get("text") or ""),
            "status":           "ok" if r.get("error") is None else "error",
            "error":            r.get("error"),
            "text":             r.get("text", ""),
            "words":            words_clean,
        })

    payload = {
        "meta": {
            "generated_at": ts,
            "language":     language,
            "image":        filename,
            "platform":     "OCR Playground v1.0",
        },
        "results": clean_results,
    }

    return json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")


def word_table_to_csv(words: list[dict], engine: str) -> bytes:
    """
    Export per-word detail (text, confidence, bbox) to CSV.

    Args:
        words:  List of word dicts from an engine result.
        engine: Engine name label.

    Returns:
        UTF-8 CSV bytes.
    """
    buf = io.StringIO()
    writer = csv.DictWriter(
        buf,
        fieldnames=["Engine", "Word", "Confidence_pct", "x1", "y1", "x2", "y2"],
    )
    writer.writeheader()

    for w in words:
        conf = w.get("confidence", 0)
        conf_pct = round(conf * 100 if conf <= 1.0 else conf, 1)
        bbox = w.get("bbox", [0, 0, 0, 0])
        writer.writerow({
            "Engine":         engine,
            "Word":           w.get("text", ""),
            "Confidence_pct": conf_pct,
            "x1": bbox[0] if len(bbox) > 0 else "",
            "y1": bbox[1] if len(bbox) > 1 else "",
            "x2": bbox[2] if len(bbox) > 2 else "",
            "y2": bbox[3] if len(bbox) > 3 else "",
        })

    return ("\ufeff" + buf.getvalue()).encode("utf-8")
