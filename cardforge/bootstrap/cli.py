"""Headless CLI entry for batch card generation and pack management."""
from __future__ import annotations

import argparse
from pathlib import Path

DEFAULT_CONFIG = Path.home() / ".cardforge" / "config.toml"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="cardforge",
        description="AI trading card generator — desktop + headless.",
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG,
                        help="Path to config.toml (default: ~/.cardforge/config.toml)")
    parser.add_argument("--version", action="store_true",
                        help="Print version and exit.")
    sub = parser.add_subparsers(dest="command")

    gen = sub.add_parser("generate", help="Generate a card from a prompt.")
    gen.add_argument("prompt", type=str, help="Card concept prompt.")
    gen.add_argument("--template", default="default",
                     help="Template name from the active pack.")
    gen.add_argument("--out", type=Path, default=Path("card_output"),
                     help="Output directory for rendered cards.")

    pack = sub.add_parser("pack", help="Card pack operations.")
    pack.add_argument("action", choices=["list", "inspect", "sign", "verify"])

    return parser.parse_args(argv)