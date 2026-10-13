"""Stat balancing — keeps generated stat blocks inside rarity budgets."""
from __future__ import annotations

from cardforge.core.card import Card, Rarity, StatBlock

RARITY_BUDGET: dict[Rarity, int] = {
    Rarity.COMMON: 180,
    Rarity.UNCOMMON: 240,
    Rarity.RARE: 300,
    Rarity.MYTHIC: 360,
    Rarity.LEGENDARY: 420,
}

_AXES = ("power", "toughness", "speed", "intellect", "arcana", "charisma")


def clamp_to_budget(stats: StatBlock, rarity: Rarity) -> StatBlock:
    """Scale all axes proportionally so the sum fits the rarity budget."""
    budget = RARITY_BUDGET[rarity]
    total = sum(getattr(stats, axis) for axis in _AXES)
    if total <= budget:
        return stats
    scale = budget / total
    scaled = {axis: max(0, min(100, round(getattr(stats, axis) * scale)))
              for axis in _AXES}
    return StatBlock(**scaled)


def suggest_rarity(stats: StatBlock) -> Rarity:
    total = sum(getattr(stats, axis) for axis in _AXES)
    for rarity, budget in sorted(RARITY_BUDGET.items(), key=lambda kv: kv[1]):
        if total <= budget:
            return rarity
    return Rarity.LEGENDARY


def rebalance(card: Card) -> Card:
    return card.model_copy(update={"stats": clamp_to_budget(card.stats, card.rarity)})