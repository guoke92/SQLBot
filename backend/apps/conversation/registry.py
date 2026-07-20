"""Graph registry — single routing table from graph_key to builder."""

from __future__ import annotations

from typing import Any, Callable, Dict

# builder(ctx) -> compiled graph (or runnable that runtime knows how to execute)
GraphBuilder = Callable[..., Any]

_REGISTRY: Dict[str, GraphBuilder] = {}


def register_graph(graph_key: str, builder: GraphBuilder) -> None:
    """Register (or replace) a graph builder for ``graph_key``."""
    if not graph_key:
        raise ValueError("graph_key must be non-empty")
    if builder is None:
        raise ValueError("builder is required")
    _REGISTRY[graph_key] = builder


def get_graph(graph_key: str) -> GraphBuilder:
    """Return the registered builder; raises KeyError if missing."""
    try:
        return _REGISTRY[graph_key]
    except KeyError as e:
        raise KeyError(f"No graph registered for key={graph_key!r}") from e


def has_graph(graph_key: str) -> bool:
    return graph_key in _REGISTRY


def list_graphs() -> list[str]:
    return sorted(_REGISTRY.keys())


def clear_registry() -> None:
    """Test helper — not for production paths."""
    _REGISTRY.clear()


def unregister_graph(graph_key: str) -> None:
    """Test helper — remove a key if present."""
    _REGISTRY.pop(graph_key, None)
