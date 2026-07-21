"""Config assistant — primary graph for SQLBot system metadata configuration.

Product surface shares ``/chat/start`` + ``/chat/question``; routing is by
``Chat.chat_type == "config"`` into ``submit_graph("config", ...)``.

Tools wrap existing datasource/table/field CRUD only — never business DML,
never ``execSql``. No independent HTTP service / dual stream path.

Topology is driven by ``backend/graphs/current/config.yaml``.
Node/router implementations live in ``apps.config_assistant.nodes``.
"""
