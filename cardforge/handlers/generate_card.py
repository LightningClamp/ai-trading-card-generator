"""Handler: prompt -> card. Orchestrates LLM copy, art, stats, render."""
from __future__ import annotations

import uuid
from pathlib import Path

import structlog

from cardforge.core.balancer import clamp_to_budget, suggest_rarity
from cardforge.core.card import Card, StatBlock
from cardforge.services.art_service import ArtService
from cardforge.services.llm_service import LLMService
from cardforge.services.render_service import RenderService

log = structlog.get_logger(__name__)


class GenerateCardHandler:
    def __init__(self, llm: LLMService, art: ArtService, render: RenderService) -> None:
        self._llm = llm
        self._art = art
        self._render = render

    async def run(self, prompt: str, template: str, out_dir: Path) -> Card:
        draft = await self._llm.draft_card(prompt)
        stats = StatBlock(**draft["stats"])
        rarity = suggest_rarity(stats)
        stats = clamp_to_budget(stats, rarity)

        card = Card(
            card_id=str(uuid.uuid4()),
            name=draft["name"],
            flavor_text=draft.get("flavor_text", ""),
            rarity=rarity,
            stats=stats,
            art_prompt=draft.get("art_prompt", prompt),
            template=template,
        )
        art_path = await self._art.render(card.art_prompt, out_dir / f"{card.card_id}.png")
        card = card.model_copy(update={"art_path": str(art_path)})
        rendered = self._render.render(card, out_dir)
        log.info("card_generated", card_id=card.card_id, rarity=rarity.value,
                 out=str(rendered))
        return card