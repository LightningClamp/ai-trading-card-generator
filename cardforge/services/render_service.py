"""Card renderer: composes art + stat block + frame via Jinja2 + Pillow."""
from __future__ import annotations

from pathlib import Path

import structlog
from jinja2 import Environment, FileSystemLoader, select_autoescape
from PIL import Image, ImageDraw, ImageFont

from cardforge.config.settings import Settings
from cardforge.core.card import Card
from cardforge.core.pack import CardPackRegistry

log = structlog.get_logger(__name__)

_FRAME_MARGIN = 24
_STAT_BAR_HEIGHT = 18


class RenderService:
    def __init__(self, settings: Settings, registry: CardPackRegistry) -> None:
        self._settings = settings
        self._registry = registry
        self._env = Environment(
            loader=FileSystemLoader("."),
            autoescape=select_autoescape(["html", "xml"]),
        )

    def render(self, card: Card, out_dir: Path) -> Path:
        out_dir.mkdir(parents=True, exist_ok=True)
        canvas = Image.new("RGB",
                           (self._settings.card_width_px, self._settings.card_height_px),
                           (18, 18, 24))
        draw = ImageDraw.Draw(canvas)

        if card.art_path and Path(card.art_path).exists():
            art = Image.open(card.art_path).convert("RGB")
            art = art.resize((self._settings.card_width_px - 2 * _FRAME_MARGIN,
                              int(self._settings.card_height_px * 0.55)))
            canvas.paste(art, (_FRAME_MARGIN, _FRAME_MARGIN))

        font = ImageFont.load_default()
        draw.text((_FRAME_MARGIN, int(self._settings.card_height_px * 0.62)),
                  card.name, fill=(240, 240, 240), font=font)
        draw.text((_FRAME_MARGIN, int(self._settings.card_height_px * 0.66)),
                  card.flavor_text[:120], fill=(180, 180, 190), font=font)

        y = int(self._settings.card_height_px * 0.74)
        for axis in ("power", "toughness", "speed", "intellect", "arcana", "charisma"):
            value = getattr(card.stats, axis)
            draw.text((_FRAME_MARGIN, y), f"{axis[:3].upper()} {value:>3}",
                      fill=(200, 200, 210), font=font)
            draw.rectangle([_FRAME_MARGIN + 80, y,
                            _FRAME_MARGIN + 80 + value * 3, y + _STAT_BAR_HEIGHT],
                           fill=(90, 160, 220))
            y += _STAT_BAR_HEIGHT + 6

        out_path = out_dir / f"{card.card_id}.rendered.png"
        canvas.save(out_path)
        log.info("card_rendered", card_id=card.card_id, path=str(out_path))
        return out_path