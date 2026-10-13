"""Handler: run a prompt list through the generator, bounded concurrency."""
from __future__ import annotations

import asyncio
from pathlib import Path

import structlog

from cardforge.core.card import Card
from cardforge.handlers.generate_card import GenerateCardHandler

log = structlog.get_logger(__name__)


class BatchGenerateHandler:
    def __init__(self, single: GenerateCardHandler, concurrency: int = 4) -> None:
        self._single = single
        self._sem = asyncio.Semaphore(concurrency)

    async def run(self, prompts: list[str], template: str, out_dir: Path) -> list[Card]:
        async def _one(p: str) -> Card | None:
            async with self._sem:
                try:
                    return await self._single.run(p, template, out_dir)
                except Exception as exc:  # per-card isolation
                    log.error("batch_card_failed", prompt=p[:64], error=str(exc))
                    return None

        results = await asyncio.gather(*(_one(p) for p in prompts))
        return [c for c in results if c is not None]