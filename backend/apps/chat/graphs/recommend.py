"""Recommend nodes — backward-compatible re-exports.

Canonical implementations live in ``apps.chat.graphs.nodes.recommend``.
Topology is driven by ``backend/graphs/current/recommend.yaml``.
"""

from apps.chat.graphs.nodes.recommend import (  # noqa: F401
    RecommendState,
    generate_node,
)
