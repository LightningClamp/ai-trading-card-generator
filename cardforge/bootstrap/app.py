"""Desktop entrypoint. Boots config, services, then the Qt shell."""
from __future__ import annotations

import sys
from pathlib import Path

import structlog
from PySide6.QtWidgets import QApplication

from cardforge.bootstrap.cli import parse_args
from cardforge.config.settings import load_settings
from cardforge.core.pack import CardPackRegistry
from cardforge.services.render_service import RenderService
from cardforge.ui.main_window import MainWindow
from cardforge.utils.logging import configure_logging

log = structlog.get_logger(__name__)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    settings = load_settings(args.config)
    configure_logging(level=settings.log_level, log_dir=settings.log_dir)
    log.info("boot", version=__import__("cardforge").__version__,
             config=str(args.config))

    registry = CardPackRegistry(search_paths=settings.pack_paths)
    registry.discover()

    render_service = RenderService(settings=settings, registry=registry)

    app = QApplication(sys.argv)
    window = MainWindow(render_service=render_service, settings=settings)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())