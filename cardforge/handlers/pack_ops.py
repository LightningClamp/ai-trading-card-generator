"""Handler: pack list/inspect/sign/verify wired to the CLI subcommand."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from cardforge.core.pack import CardPackRegistry


class PackOpsHandler:
    def __init__(self, registry: CardPackRegistry) -> None:
        self._registry = registry

    def list_packs(self) -> list[str]:
        return self._registry.names()

    def inspect(self, name: str) -> dict:
        pack = self._registry.get(name)
        if pack is None:
            raise KeyError(f"pack not found: {name}")
        return pack.manifest.model_dump()

    def sign(self, name: str, key_path: Path) -> str:
        pack = self._registry.get(name)
        if pack is None:
            raise KeyError(f"pack not found: {name}")
        digest = hashlib.sha256(
            json.dumps(pack.manifest.model_dump(), sort_keys=True).encode()
        ).hexdigest()
        key_path.write_text(digest, encoding="utf-8")
        return digest

    def verify(self, name: str, key_path: Path) -> bool:
        expected = key_path.read_text(encoding="utf-8").strip()
        actual = self.sign(name, key_path)
        return expected == actual