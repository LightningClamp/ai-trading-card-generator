"""Card pack discovery and loading. Packs are zip archives of templates+assets."""
from __future__ import annotations

import json
import zipfile
from pathlib import Path

import structlog
from pydantic import BaseModel, ValidationError

from cardforge.core.card import Card

log = structlog.get_logger(__name__)

CARD_PACK_VERSION = 3


class PackManifest(BaseModel):
    name: str
    version: int = CARD_PACK_VERSION
    author: str = "unknown"
    description: str = ""
    templates: list[str] = []
    signature: str | None = None


class CardPack(BaseModel):
    manifest: PackManifest
    root: Path

    def template_path(self, name: str) -> Path:
        return self.root / "templates" / f"{name}.j2"


class CardPackRegistry:
    """Discovers .cardpack files and exploded pack directories."""

    def __init__(self, search_paths: list[Path]) -> None:
        self._search_paths = search_paths
        self._packs: dict[str, CardPack] = {}

    def discover(self) -> int:
        found = 0
        for base in self._search_paths:
            if not base.exists():
                continue
            for entry in base.iterdir():
                if entry.suffix == ".cardpack":
                    self._load_archive(entry)
                    found += 1
                elif entry.is_dir() and (entry / "manifest.json").exists():
                    self._load_dir(entry)
                    found += 1
        log.info("pack_discovery", count=found)
        return found

    def _load_archive(self, path: Path) -> None:
        try:
            with zipfile.ZipFile(path) as zf:
                manifest_raw = json.loads(zf.read("manifest.json"))
            manifest = PackManifest.model_validate(manifest_raw)
            self._packs[manifest.name] = CardPack(manifest=manifest, root=path)
        except (zipfile.BadZipFile, KeyError, ValidationError) as exc:
            log.warning("pack_load_failed", path=str(path), error=str(exc))

    def _load_dir(self, path: Path) -> None:
        try:
            manifest = PackManifest.model_validate(
                json.loads((path / "manifest.json").read_text("utf-8"))
            )
            self._packs[manifest.name] = CardPack(manifest=manifest, root=path)
        except (OSError, ValidationError) as exc:
            log.warning("pack_load_failed", path=str(path), error=str(exc))

    def get(self, name: str) -> CardPack | None:
        return self._packs.get(name)

    def names(self) -> list[str]:
        return sorted(self._packs)