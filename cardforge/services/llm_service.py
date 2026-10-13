"""LLM backend wrapper. Drafts card name, flavor, stats, and art prompt."""
from __future__ import annotations

import json

import httpx
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

log = structlog.get_logger(__name__)

DRAFT_SYSTEM_PROMPT = """You are a trading card designer. Given a concept, \
return STRICT JSON with keys: name (<=64 chars), flavor_text (<=280 chars), \
art_prompt (<=512 chars, visual only, no text overlays), stats (object with \
power, toughness, speed, intellect, arcana, charisma; each 0-100). \
No prose outside the JSON."""


class LLMService:
    def __init__(self, backend: str, model: str, api_key: str | None,
                 base_url: str = "https://api.openai.com/v1") -> None:
        self._backend = backend
        self._model = model
        self._base_url = base_url
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(60.0, connect=10.0),
            headers={"Authorization": f"Bearer {api_key}"} if api_key else {},
        )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8))
    async def draft_card(self, prompt: str) -> dict:
        payload = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": DRAFT_SYSTEM_PROMPT},
                {"role": "user", "content": prompt[:4096]},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.9,
        }
        resp = await self._client.post(f"{self._base_url}/chat/completions",
                                       json=payload)
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
        return json.loads(content)

    async def aclose(self) -> None:
        await self._client.aclose()