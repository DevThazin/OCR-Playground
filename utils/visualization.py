"""
utils/visualization.py
-----------------------
Drawing utilities for bounding-box annotations and comparison panels.

All functions accept numpy arrays and return numpy arrays so they
work equally well in Colab (matplotlib) and Streamlit (st.image).
"""

import logging
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)

# Default colours (RGB) used when drawing boxes
COLORS = {
    "EasyOCR": (0, 200, 100),       # green
    "Tesseract OCR": (30, 120, 230), # blue
    "default": (230, 60, 60),        # red fallback
}

BOX_THICKNESS = 2
FONT_SCALE = 0.45
TEXT_PADDING = 2


def draw_bounding_boxes(
    image: np.ndarray,
    words: list,
    engine_name: str = "default",
    show_confidence: bool = True,
) -> np.ndarray:
    """
    Draw bounding boxes and optional confidence labels on a copy of the image.

    Supports both EasyOCR-style bbox (quad points or [x1,y1,x2,y2])
    and Tesseract-style [x1, y1, x2, y2].

    Args:
        image:           RGB numpy array (H × W × 3).
        words:           List of word dicts from an OCR engine result.
                         Each dict must have "bbox" and optionally "confidence".
        engine_name:     Used to pick a colour from COLORS.
        show_confidence: If True, draw confidence score above each box.

    Returns:
        Annotated RGB numpy array (copy, original unchanged).
    """
    try:
        import cv2
    except ImportError:
        logger.warning("opencv-python not installed; returning original image.")
        return image.copy()

    annotated = image.copy()
    # cv2 draws in BGR
    bgr_img = cv2.cvtColor(annotated, cv2.COLOR_RGB2BGR)

    color_rgb = COLORS.get(engine_name, COLORS["default"])
    color_bgr = (color_rgb[2], color_rgb[1], color_rgb[0])

    for word in words:
        bbox = word.get("bbox")
        if bbox is None:
            continue

        # ---- Draw rectangle ----
        x1, y1, x2, y2 = [int(v) for v in bbox]
        cv2.rectangle(bgr_img, (x1, y1), (x2, y2), color_bgr, BOX_THICKNESS)

        # ---- Draw confidence label ----
        if show_confidence:
            conf = word.get("confidence")
            if conf is not None:
                # Normalise to 0–100 display value
                disp_conf = conf * 100 if conf <= 1.0 else conf
                label = f"{disp_conf:.0f}%"
                label_y = max(y1 - TEXT_PADDING, 12)
                cv2.putText(
                    bgr_img, label,
                    (x1, label_y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    FONT_SCALE,
                    color_bgr,
                    1,
                    cv2.LINE_AA,
                )

    # Convert back to RGB for downstream use
    return cv2.cvtColor(bgr_img, cv2.COLOR_BGR2RGB)


def create_comparison_panel(
    original: np.ndarray,
    annotated_easyocr: Optional[np.ndarray],
    annotated_tesseract: Optional[np.ndarray],
) -> np.ndarray:
    """
    Stack the original and annotated images side-by-side for a comparison panel.

    If an annotated image is None, its slot is filled with a gray placeholder.

    Args:
        original:            RGB numpy array.
        annotated_easyocr:   EasyOCR-annotated RGB array or None.
        annotated_tesseract: Tesseract-annotated RGB array or None.

    Returns:
        Horizontally concatenated RGB panel.
    """
    h, w = original.shape[:2]
    placeholder = np.full((h, w, 3), 200, dtype=np.uint8)  # light gray

    easy = annotated_easyocr if annotated_easyocr is not None else placeholder
    tess = annotated_tesseract if annotated_tesseract is not None else placeholder

    # Resize all panels to the same height so hstack works
    easy = _resize_to_height(easy, h)
    tess = _resize_to_height(tess, h)

    return np.hstack([original, easy, tess])


def confidence_bar_image(
    words: list,
    engine_name: str,
    width: int = 400,
    height: int = 200,
) -> np.ndarray:
    """
    Create a simple confidence-distribution bar chart as an RGB numpy array.
    Useful for Colab display without matplotlib.

    Args:
        words:       Word dicts containing "confidence" values.
        engine_name: Label shown in the chart title.
        width:       Output image width.
        height:      Output image height.

    Returns:
        RGB numpy array (height × width × 3).
    """
    try:
        import cv2
    except ImportError:
        return np.full((height, width, 3), 240, dtype=np.uint8)

    canvas = np.full((height, width, 3), 245, dtype=np.uint8)

    confs = [w.get("confidence", 0) for w in words]
    if not confs:
        return canvas

    # Normalise to 0–1
    confs_norm = [c / 100.0 if c > 1.0 else c for c in confs]

    n = len(confs_norm)
    bar_w = max(1, (width - 20) // n)
    color_bgr = (COLORS.get(engine_name, COLORS["default"])[2],
                 COLORS.get(engine_name, COLORS["default"])[1],
                 COLORS.get(engine_name, COLORS["default"])[0])

    for i, c in enumerate(confs_norm):
        bh = int(c * (height - 30))
        x1 = 10 + i * bar_w
        x2 = x1 + bar_w - 1
        y2 = height - 10
        y1 = y2 - bh
        cv2.rectangle(canvas, (x1, y1), (x2, y2), color_bgr, -1)

    cv2.putText(
        canvas, f"{engine_name} confidence",
        (10, 15),
        cv2.FONT_HERSHEY_SIMPLEX, 0.45,
        (50, 50, 50), 1, cv2.LINE_AA,
    )

    return cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _resize_to_height(image: np.ndarray, target_h: int) -> np.ndarray:
    """Scale image to target_h while preserving aspect ratio."""
    try:
        import cv2
        h, w = image.shape[:2]
        if h == target_h:
            return image
        scale = target_h / h
        new_w = int(w * scale)
        return cv2.resize(image, (new_w, target_h), interpolation=cv2.INTER_AREA)
    except ImportError:
        return image
