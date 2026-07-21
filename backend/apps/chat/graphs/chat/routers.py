"""Target chat graph routers.

Most NLQ-path routers are re-exported from ``apps.chat.graphs.nodes.nlq``.
Dialogue-path routing is inline in ``nodes_dialogue.route_after_turn``.
This module exists for any future chat-level-only routers.
"""

from apps.chat.graphs.chat.nodes_dialogue import route_after_turn  # noqa: F401
