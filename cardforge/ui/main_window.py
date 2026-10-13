"""Main Qt window: prompt box, template picker, preview, export button."""
from __future__ import annotations

import asyncio
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QComboBox, QHBoxLayout, QLabel, QLineEdit,
                               QListWidget, QPushButton, QVBoxLayout, QWidget)

from cardforge.config.settings import Settings
from cardforge.services.render_service import RenderService


class MainWindow(QWidget):
    def __init__(self, render_service: RenderService, settings: Settings) -> None:
        super().__init__()
        self._render = render_service
        self._settings = settings
        self.setWindowTitle("AI Trading Card Generator")
        self.resize(1100, 720)
        self._build_ui()

    def _build_ui(self) -> None:
        root = QHBoxLayout(self)

        left = QVBoxLayout()
        left.addWidget(QLabel("Card concept"))
        self._prompt = QLineEdit()
        self._prompt.setPlaceholderText("e.g. a drowned lighthouse keeper, mythic")
        left.addWidget(self._prompt)

        left.addWidget(QLabel("Template"))
        self._template = QComboBox()
        self._template.addItems(["default", "borderless", "foil"])
        left.addWidget(self._template)

        self._generate = QPushButton("Generate")
        self._generate.clicked.connect(self._on_generate)
        left.addWidget(self._generate)

        left.addWidget(QLabel("Recent cards"))
        self._recent = QListWidget()
        left.addWidget(self._recent)
        left.addStretch(1)

        right = QVBoxLayout()
        self._preview = QLabel("no card yet")
        self._preview.setAlignment(Qt.AlignCenter)
        self._preview.setMinimumSize(500, 700)
        self._preview.setStyleSheet("background:#141420;color:#888;")
        right.addWidget(self._preview)

        root.addLayout(left, 1)
        root.addLayout(right, 2)

    def _on_generate(self) -> None:
        prompt = self._prompt.text().strip()
        if not prompt:
            return
        out_dir = Path("card_output")
        asyncio.get_event_loop().create_task(self._run_generate(prompt, out_dir))

    async def _run_generate(self, prompt: str, out_dir: Path) -> None:
        from cardforge.handlers.generate_card import GenerateCardHandler
        from cardforge.services.art_service import ArtService
        from cardforge.services.llm_service import LLMService

        llm = LLMService(self._settings.llm_backend, self._settings.llm_model, None)
        art = ArtService(self._settings.art_backend, self._settings.art_model_path,
                         self._settings.card_width_px, self._settings.card_height_px)
        handler = GenerateCardHandler(llm, art, self._render)
        card = await handler.run(prompt, self._template.currentText(), out_dir)
        self._recent.addItem(f"{card.name} [{card.rarity.value}]")
        await llm.aclose()