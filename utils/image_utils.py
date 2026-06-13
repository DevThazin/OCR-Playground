"""
utils/image_utils.py
---------------------
Image loading, validation, and preprocessing utilities.

All image I/O for the OCR Playground passes through this module
so that downstream code always receives a consistent numpy array.
"""

import io
import logging
from pathlib import Path
from typing import Optional, Tuple

import numpy as np
from PIL import Image as PILImage, ImageOps, ImageEnhance

logger = logging.getLogger(__name__)

# Supported upload formats
SUPPORTED_FORMATS = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"}
MAX_DIMENSION = 4096   # pixels; images wider/taller will be downscaled
MAX_FILE_MB = 10       # megabytes


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------

def load_image_from_bytes(data: bytes) -> np.ndarray:
    """
    Decode raw bytes into an RGB numpy array.

    Args:
        data: Raw image bytes (from file upload or disk read).

    Returns:
        numpy array, shape (H, W, 3), dtype uint8, RGB channel order.

    Raises:
        ValueError: If the bytes cannot be decoded as an image.
    """
    try:
        pil_img = PILImage.open(io.BytesIO(data)).convert("RGB")
        return np.array(pil_img, dtype=np.uint8)
    except Exception as exc:
        raise ValueError(f"Cannot decode image: {exc}") from exc


def load_image_from_path(path: str | Path) -> np.ndarray:
    """
    Load an image from a file path into an RGB numpy array.

    Args:
        path: Filesystem path to the image.

    Returns:
        numpy array, shape (H, W, 3), dtype uint8, RGB.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file is not a supported image format.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {path}")
    if path.suffix.lower() not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported format '{path.suffix}'. Use: {SUPPORTED_FORMATS}")
    try:
        pil_img = PILImage.open(path).convert("RGB")
        return np.array(pil_img, dtype=np.uint8)
    except Exception as exc:
        raise ValueError(f"Cannot load image: {exc}") from exc


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_upload(data: bytes, filename: str) -> Tuple[bool, str]:
    """
    Check that an uploaded file is a valid, supported image.

    Args:
        data:     Raw file bytes.
        filename: Original filename (used to check extension).

    Returns:
        Tuple (is_valid: bool, message: str).
        message is empty on success, or a human-readable error.
    """
    suffix = Path(filename).suffix.lower()
    if suffix not in SUPPORTED_FORMATS:
        return False, f"File type '{suffix}' is not supported. Please upload: {', '.join(SUPPORTED_FORMATS)}"

    size_mb = len(data) / (1024 * 1024)
    if size_mb > MAX_FILE_MB:
        return False, f"File is {size_mb:.1f} MB. Maximum allowed is {MAX_FILE_MB} MB."

    try:
        PILImage.open(io.BytesIO(data)).verify()
    except Exception as exc:
        return False, f"File appears corrupted or is not a valid image: {exc}"

    return True, ""


# ---------------------------------------------------------------------------
# Preprocessing
# ---------------------------------------------------------------------------

def resize_if_needed(image: np.ndarray, max_dim: int = MAX_DIMENSION) -> np.ndarray:
    """
    Downscale an image so its largest dimension does not exceed max_dim.
    Aspect ratio is preserved. Images already within limits are returned as-is.

    Args:
        image:   Input RGB numpy array.
        max_dim: Maximum allowed width or height in pixels.

    Returns:
        Possibly resized RGB numpy array.
    """
    h, w = image.shape[:2]
    if max(h, w) <= max_dim:
        return image

    scale = max_dim / max(h, w)
    new_w, new_h = int(w * scale), int(h * scale)
    pil_img = PILImage.fromarray(image).resize((new_w, new_h), PILImage.LANCZOS)
    logger.debug("Resized image %dx%d → %dx%d", w, h, new_w, new_h)
    return np.array(pil_img, dtype=np.uint8)


def enhance_for_ocr(
    image: np.ndarray,
    contrast: float = 1.5,
    sharpness: float = 1.5,
    grayscale: bool = False,
) -> np.ndarray:
    """
    Apply basic contrast / sharpness enhancement to improve OCR accuracy.

    Args:
        image:     Input RGB numpy array.
        contrast:  Contrast multiplier (1.0 = no change).
        sharpness: Sharpness multiplier (1.0 = no change).
        grayscale: If True, return a grayscale image (H × W array).

    Returns:
        Processed image as numpy array.
    """
    pil_img = PILImage.fromarray(image)

    if contrast != 1.0:
        pil_img = ImageEnhance.Contrast(pil_img).enhance(contrast)
    if sharpness != 1.0:
        pil_img = ImageEnhance.Sharpness(pil_img).enhance(sharpness)

    if grayscale:
        pil_img = ImageOps.grayscale(pil_img)

    return np.array(pil_img, dtype=np.uint8)


# ---------------------------------------------------------------------------
# Metadata helpers
# ---------------------------------------------------------------------------

def get_image_info(image: np.ndarray) -> dict:
    """
    Return a metadata dictionary for a numpy image array.

    Args:
        image: RGB numpy array.

    Returns:
        dict with keys: height, width, channels, dtype, size_kb (estimate).
    """
    h, w = image.shape[:2]
    channels = image.shape[2] if image.ndim == 3 else 1
    size_kb = round(image.nbytes / 1024, 1)
    return {
        "height": h,
        "width": w,
        "channels": channels,
        "dtype": str(image.dtype),
        "size_kb": size_kb,
    }
