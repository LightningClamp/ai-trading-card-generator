"""Art backend. Local SDXL via diffusers, or remote DALL-E fallback."""
from __future__ import annotations

from pathlib import Path

import structlog

log = structlog.get_logger(__name__)


class ArtService:
    def __init__(self, backend: str, model_path: Path | None = None,
                 width: int = 750, height: int = 1050) -> None:
        self._backend = backend
        self._model_path = model_path
        self._width = width
        self._height = height
        self._pipe = None

    def _ensure_pipe(self):
        if self._pipe is not None:
            return self._pipe
        if self._backend != "sdxl-local" or self._model_path is None:
            raise RuntimeError("no local art model configured")
        from diffusers import StableDiffusionXLPipeline  # lazy, heavy import
        import torch
        self._pipe = StableDiffusionXLPipeline.from_single_file(
            str(self._model_path),
            torch_dtype=torch.float16,
            use_safetensors=True,
        ).to("cuda")
        return self._pipe

    async def render(self, art_prompt: str, out_path: Path) -> Path:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        if self._backend == "none":
            from PIL import Image
            Image.new("RGB", (self._width, self._height), (24, 24, 32)).save(out_path)
            return out_path
        pipe = self._ensure_pipe()
        image = pipe(prompt=art_prompt, width=self._width, height=self._height,
                     num_inference_steps=30, guidance_scale=7.0).images[0]
        image.save(out_path)
        log.info("art_rendered", path=str(out_path), backend=self._backend)
        return out_path