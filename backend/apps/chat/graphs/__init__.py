"""Chat conversation graphs (recommend, chat).

Topology is driven by YAML files under ``backend/graphs/``.
Chat node bodies live in ``apps.chat.agent``; recommend nodes remain in
``apps.chat.graphs.nodes.recommend``. Registration is handled by
``apps.conversation.graph_loader.bootstrap_graphs`` (called from ``apps.api``
at process start).
"""
