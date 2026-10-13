"""The Card domain model — the atom of the whole forge."""
from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum

from pydantic import BaseModel, Field, field_validator


class Rarity(StrEnum):
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    MYTHIC = "mythic"
    LEGENDARY = "legendary"


class StatBlock(BaseModel):
    """Six-axis stat block. Each axis 0-100, sum capped at 420."""
    power: int = Field(ge=0, le=100, default=40)
    toughness: int = Field(ge=0, le=100, default=40)
    speed: int = Field(ge=0, le=100, default=40)
    intellect: int = Field(ge=0, le=100, default=40)
    arcana: int = Field(ge=0, le=100, default=40)
    charisma: int = Field(ge=0, le=100, default=40)

    @field_validator("charisma")
    @classmethod
    def _sum_cap(cls, v: int, info) -> int:
        total = sum(info.data.get(k, 0) for k in
                    ("power", "toughness", "speed", "intellect", "arcana")) + v
        if total > 420:
            raise ValueError(f"stat sum {total} exceeds cap 420")
        return v


class Card(BaseModel):
    card_id: str
    name: str = Field(min_length=1, max_length=64)
    flavor_text: str = Field(default="", max_length=280)
    rarity: Rarity = Rarity.COMMON
    stats: StatBlock = Field(default_factory=StatBlock)
    art_prompt: str = Field(default="", max_length=1024)
    art_path: str | None = None
    template: str = "default"
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    tags: list[str] = Field(default_factory=list)