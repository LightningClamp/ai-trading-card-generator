"""Small Pillow helpers used across renderers and previews."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageOps


def fit_cover(src: Path, size: tuple[int, int]) -> Image.Image:
    img = Image.open(src).convert("RGB")
    return ImageOps.fit(img, size, method=Image.LANCZOS, centering=(0.5, 0.4))


def add_foil