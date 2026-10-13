"""Typed settings loaded from TOML, with sane defaults."""
from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field

try:
    import tomllib
except ModuleNotFoundError:  # py<3.11
    import tomli as tomllib  # type: ignore[no-redef]


class Settings(BaseModel):
    log_level: str = "INFO"
    log_dir: Path = Field(default_factory=lambda: Path.home() / ".cardforge" / "logs")
    pack_paths: list[Path] = Field(
        default_factory=lambda: [
            Path.home() / ".cardforge" / "packs",
            Path("packs"),
        ]
    )
    llm_backend: str = "openai"          # openai | anthropic | local
    llm_model: str = "gpt-4o-mini"
    art_backend: str = "sdxl-local"      # sdxl-local | dall-e | none
    art_model_path: Path | None = None
    card_width_px: int = 750             # 2.5in @ 300dpi
    card_height_px: int = 1050           # 3.5in @ 300dpi
    default_rarity: str = "common"
    max_prompt_chars: int = 4096


def load_settings(path: Path) -> Settings:
    if not path.exists():
        return Settings()
    with path.open("rb") as fh:
        raw = tomllib.load(fh)
    return Settings.model_validate(raw)