"""Shared conversation infrastructure with lazy public exports.

Importing a lightweight contract such as ``apps.conversation.outcome`` must
not initialize model providers, graph runtimes or native ML dependencies.
"""

from __future__ import annotations

from importlib import import_module
from typing import Any

_EXPORT_MODULES = {
    "emit": "apps.conversation.events",
    "get_chat_model": "apps.conversation.llm",
    "get_graph": "apps.conversation.registry",
    "register_graph": "apps.conversation.registry",
    "run_coro_sync": "apps.conversation.async_util",
    "StreamRunner": "apps.conversation.runtime",
    "run_graph": "apps.conversation.runtime",
    "submit_graph": "apps.conversation.runtime",
    "StreamSink": "apps.conversation.sink",
    "resolve_sink": "apps.conversation.sink",
}

__all__ = list(_EXPORT_MODULES)


def __getattr__(name: str) -> Any:
    module_name = _EXPORT_MODULES.get(name)
    if module_name is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    value = getattr(import_module(module_name), name)
    globals()[name] = value
    return value
