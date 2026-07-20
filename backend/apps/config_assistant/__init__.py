"""Config assistant — primary graph for SQLBot system metadata configuration.

Product surface shares ``/chat/start`` + ``/chat/question``; routing is by
``Chat.chat_type == "config"`` into ``submit_graph("config", ...)``.

Tools wrap existing datasource/table/field CRUD only — never business DML,
never ``execSql``. No independent HTTP service / dual stream path.
"""

from apps.config_assistant import graph as _graph  # noqa: F401 — register_graph("config")

__all__ = ["_graph"]
