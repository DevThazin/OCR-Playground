"""
ocr_engines/easyocr_engine.py
------------------------------
EasyOCR wrapper for the OCR Playground.

Provides a clean interface for running EasyOCR on an image,
returning structured results (text, confidence, bounding boxes)
in a format compatible with the rest of the platform.

EasyOCR GitHub: https://github.com/JaidedAI/EasyOCR
"""

import time
import logging
from typing import Optional
import numpy as np

logger = logging.getLogger(__name__)


class EasyOCREngine:
    """
    Wrapper around EasyOCR that manages model loading and result formatting.

    EasyOCR downloads language models on first use (~100 MB each).
    The reader is cached per language to avoid reloading across calls.

    Attributes:
        _reader_cache (dict): Maps language code(s) → loaded Reader instance.
        gpu (bool): Whether to use GPU acceleration.
    """

    ENGINE_NAME = "EasyOCR"

    def __init__(self, gpu: bool = False) -> None:
        """
        Initialise the engine.

        Args:
            gpu: Set True to use CUDA GPU. Defaults to False for
                 Streamlit Cloud compatibility (CPU-only environment).
        """
        self.gpu = gpu
        self._reader_cache: dict = {}

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def run(
        self,
        image: np.ndarray,
        lang_code: str | list,
        detail: int = 1,
    ) -> dict:
        """
        Run EasyOCR on a numpy image array.

        Args:
            image:     BGR or RGB numpy array (H × W × 3).
            lang_code: EasyOCR language code, e.g. "en" or ["en", "ch_sim"].
            detail:    1 = return bounding boxes + confidence; 0 = text only.

        Returns:
            dict with keys:
                engine      – "EasyOCR"
                lang_code   – the code(s) used
                text        – full concatenated text
                words       – list of {text, confidence, bbox} dicts
                avg_conf    – float, mean confidence (0–1)
                runtime_s   – wall-clock seconds for the OCR call
                error       – None or an error message string
        """
        result = {
            "engine": self.ENGINE_NAME,
            "lang_code": lang_code,
            "text": "",
            "words": [],
            "avg_conf": 0.0,
            "runtime_s": 0.0,
            "error": None,
        }

        try:
            reader = self._get_reader(lang_code)

            t0 = time.perf_counter()
            raw = reader.readtext(image, detail=detail)
            result["runtime_s"] = round(time.perf_counter() - t0, 4)

            words, lines = self._parse_results(raw)
            result["words"] = words
            result["text"] = "\n".join(lines)

            confs = [w["confidence"] for w in words if w["confidence"] is not None]
            result["avg_conf"] = round(sum(confs) / len(confs), 4) if confs else 0.0

        except Exception as exc:
            logger.error("EasyOCR failed: %s", exc)
            result["error"] = str(exc)

        return result

    def is_available(self) -> bool:
        """
        Check whether the easyocr package is importable.

        Returns:
            True if EasyOCR can be imported, False otherwise.
        """
        try:
            import easyocr  # noqa: F401
            return True
        except ImportError:
            return False

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_reader(self, lang_code: str | list):
        """
        Return a cached EasyOCR Reader, loading it if necessary.

        Args:
            lang_code: Language code string or list of codes.

        Returns:
            easyocr.Reader instance.
        """
        import easyocr

        # Normalise to a hashable key for the cache
        cache_key = tuple(lang_code) if isinstance(lang_code, list) else (lang_code,)
        lang_list = list(cache_key)

        if cache_key not in self._reader_cache:
            logger.info("Loading EasyOCR model for language(s): %s", lang_list)
            self._reader_cache[cache_key] = easyocr.Reader(
                lang_list,
                gpu=self.gpu,
                verbose=False,
            )

        return self._reader_cache[cache_key]

    @staticmethod
    def _parse_results(raw: list) -> tuple[list, list]:
        """
        Convert raw EasyOCR output into structured word records.

        EasyOCR returns each detection as:
            (bbox, text, confidence)
        where bbox = [[x1,y1],[x2,y1],[x2,y2],[x1,y2]]

        Args:
            raw: List of EasyOCR detection tuples.

        Returns:
            Tuple of:
                words – list of dicts {text, confidence, bbox}
                lines – list of text strings (one per detected region)
        """
        words = []
        lines = []

        for detection in raw:
            bbox_raw, text, confidence = detection
            # Convert nested list coords to flat [x1, y1, x2, y2]
            xs = [pt[0] for pt in bbox_raw]
            ys = [pt[1] for pt in bbox_raw]
            bbox = [int(min(xs)), int(min(ys)), int(max(xs)), int(max(ys))]

            words.append({
                "text": text,
                "confidence": round(float(confidence), 4),
                "bbox": bbox,           # [x1, y1, x2, y2]
                "bbox_raw": bbox_raw,   # original quad points for precise drawing
            })
            lines.append(text)

        return words, lines
