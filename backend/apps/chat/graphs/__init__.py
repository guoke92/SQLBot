"""Chat conversation graphs (analysis, predict, recommend, chat).

Topology is driven by YAML files under ``backend/graphs/``.
Node/router implementations live in ``apps.chat.graphs.nodes.*``.
Registration is handled by ``apps.conversation.graph_loader.bootstrap_graphs``
(called from ``apps.api`` at process start).
"""
