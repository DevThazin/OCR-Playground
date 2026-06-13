"""
ocr_engines/tesseract_engine.py
--------------------------------
Tesseract OCR wrapper for the OCR Playground.

Uses pytesseract (Python binding) to call the Tesseract binary.
Returns structured results compatible with the EasyOCR engine interface.

Tesseract: https://github.com/tesseract-ocr/tesseract
pytesseract: https://github.com/madmaze/pytesseract
"""

import time
import logging
from typing import Optional
import numpy as np

logger = logging.getLogger(__name__)

# Tesseract page-segmentation modes (psm) used in this project:
#   PSM_AUTO  = 3  (fully automatic page segmentation, no OSD)
#   PSM_BLOCK = 6  (assume a single uniform block of text)
PSM_AUTO = 3


class TesseractEngine:
    """
    Wrapper around pytesseract / Tesseract OCR.

    Extracts text with per-word bounding boxes and confidence scores
    using Tesseract's TSV output format.

    Attributes:
        custom_config (str): Extra Tesseract CLI flags.
    """

    ENGINE_NAME = "Tesseract OCR"

    def __init__(self, psm: int = PSM_AUTO, oem: int = 3) -> None:
        """
        Initialise the engine.

        Args:
            psm: Page Segmentation Mode (default 3 = auto).
            oem: OCR Engine Mode (default 3 = default, based on available engines).
        """
        self.custom_config = f"--oem {oem} --psm {psm}"

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def run(
        self,
        image: np.ndarray,
        lang_code: str,
    ) -> dict:
        """
        Run Tesseract OCR on a numpy image array.

        Args:
            image:     BGR or RGB numpy array (H × W × 3).
            lang_code: Tesseract language code, e.g. "eng" or "mya".

        Returns:
            dict with keys:
                engine      – "Tesseract OCR"
                lang_code   – the code used
                text        – full extracted text string
                words       – list of {text, confidence, bbox} dicts
                avg_conf    – float, mean confidence (0–100 scale → normalised 0–1)
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
            import pytesseract
            from PIL import Image as PILImage

            # pytesseract expects a PIL Image
            pil_img = self._to_pil(image)

            t0 = time.perf_counter()

            # Get plain text (fast)
            plain_text: str = pytesseract.image_to_string(
                pil_img,
                lang=lang_code,
                config=self.custom_config,
            )

            # Get per-word data with confidence + bounding boxes (TSV)
            tsv_data = pytesseract.image_to_data(
                pil_img,
                lang=lang_code,
                config=self.custom_config,
                output_type=pytesseract.Output.DICT,
            )

            result["runtime_s"] = round(time.perf_counter() - t0, 4)
            result["text"] = plain_text.strip()

            words = self._parse_tsv(tsv_data)
            result["words"] = words

            confs = [w["confidence"] for w in words if w["confidence"] is not None]
            # Tesseract confidence is 0–100; normalise to 0–1
            result["avg_conf"] = round((sum(confs) / len(confs)) / 100.0, 4) if confs else 0.0

        except Exception as exc:
            logger.error("Tesseract failed: %s", exc)
            result["error"] = str(exc)

        return result

    def is_available(self) -> bool:
        """
        Check whether pytesseract and the Tesseract binary are both reachable.

        Returns:
            True if Tesseract can be invoked, False otherwise.
        """
        try:
            import pytesseract
            pytesseract.get_tesseract_version()
            return True
        except Exception:
            return False

    def get_version(self) -> str:
        """
        Return the installed Tesseract version string.

        Returns:
            Version string like "5.3.0" or "unavailable".
        """
        try:
            import pytesseract
            return str(pytesseract.get_tesseract_version())
        except Exception:
            return "unavailable"

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _to_pil(image: np.ndarray):
        """
        Convert a numpy array to a PIL Image for pytesseract.

        Handles both RGB and BGR arrays (OpenCV default is BGR).

        Args:
            image: numpy array (H × W × 3).

        Returns:
            PIL.Image.Image
        """
        from PIL import Image as PILImage
        # If the array looks like it came from OpenCV (BGR), convert to RGB
        if image.ndim == 3 and image.shape[2] == 3:
            # We assume RGB from the image_utils pipeline; no conversion needed.
            return PILImage.fromarray(image.astype(np.uint8))
        return PILImage.fromarray(image.astype(np.uint8))

    @staticmethod
    def _parse_tsv(tsv: dict) -> list:
        """
        Convert pytesseract's TSV dict into structured word records.

        pytesseract.image_to_data returns a dict where each key maps
        to a list. Rows with conf == -1 are block/line delimiters —
        skip them. Only keep rows with actual word text.

        Args:
            tsv: Dict from pytesseract.image_to_data(output_type=DICT).

        Returns:
            List of dicts {text, confidence, bbox}.
        """
        words = []
        n = len(tsv["text"])

        for i in range(n):
            text = tsv["text"][i].strip()
            conf = int(tsv["conf"][i])

            # Skip empty text or delimiter rows (conf == -1)
            if not text or conf < 0:
                continue

            x = int(tsv["left"][i])
            y = int(tsv["top"][i])
            w = int(tsv["width"][i])
            h = int(tsv["height"][i])

            words.append({
                "text": text,
                "confidence": conf,           # 0–100 scale (raw Tesseract)
                "confidence_norm": round(conf / 100.0, 4),  # 0–1
                "bbox": [x, y, x + w, y + h],               # [x1, y1, x2, y2]
            })

        return words
