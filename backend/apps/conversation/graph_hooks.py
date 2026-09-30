"""Graph-key hooks so Host does not import product-agent modules.

Product graphs register hydrate (resume runtime) and recover (terminal salvage).
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

RecoverFn = Callable[[str, Mapping[str, Any] | None], bool]
HydrateFn = Callable[[Any, Any], dict[str, Any]]

_RECOVER: dict[str, RecoverFn] = {}
_HYDRATE: dict[str, HydrateFn] = {}


def register_recover(graph_key: str, fn: RecoverFn) -> None:
    if graph_key:
        _RECOVER[graph_key] = fn


def register_hydrate(graph_key: str, fn: HydrateFn) -> None:
    if graph_key:
        _HYDRATE[graph_key] = fn


def try_recover(
    graph_key: str, run_id: str, state: Mapping[str, Any] | None = None
) -> bool:
    fn = _RECOVER.get(str(graph_key or ""))
    if fn is None:
        return False
    return bool(fn(run_id, state))


def try_hydrate(graph_key: str, run: Any, service: Any) -> dict[str, Any]:
    fn = _HYDRATE.get(str(graph_key or ""))
    if fn is None:
        return {}
    extras = fn(run, service)
    return dict(extras) if extras else {}
