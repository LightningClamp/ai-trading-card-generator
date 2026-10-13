"""Sandboxed Jinja2 rendering for untrusted cardpack templates."""
from __future__ import annotations

from jinja2 import Environment, StrictUndefined
from jinja2.sandbox import SandboxedEnvironment

_BANNED_ATTRS = {"__class__", "__globals__", "__subclasses__", "__mro__",
                 "__bases__", "__init__", "__code__"}


class CardTemplateSandbox(SandboxedEnvironment):
    def is_safe_attribute(self, obj, attr, value) -> bool:
        if attr in _BANNED_ATTRS:
            return False
        return super().is_safe_attribute(obj, attr, value)


def make_sandbox() -> Environment:
    env = CardTemplateSandbox(undefined=StrictUndefined, autoescape=True)
    env.globals.clear()
    return env