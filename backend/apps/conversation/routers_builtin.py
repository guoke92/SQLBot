"""Built-in topology routers — no business logic.

Used by graph YAML via::

    router:
      type: ok_or_fail
      next: ensure_datasource
"""

from __future__ import annotations

from typing import Any, Callable, Mapping


def ok_or_fail(next_name: str) -> Callable[[Mapping[str, Any]], str]:
    """Return ``fail`` when ``state["error"]`` is set, otherwise ``next_name``."""

    if not next_name:
        raise ValueError("ok_or_fail requires a non-empty next node name")

    def _route(state: Mapping[str, Any]) -> str:
        return "fail" if state.get("error") else next_name

    _route.__name__ = f"ok_or_fail__{next_name}"
    _route.__qualname__ = _route.__name__
    return _route
