"""Config assistant — primary graph for AI智能问数 system metadata configuration.

Product surface shares ``/chat/start`` + ``/chat/question``; routing is by
``Chat.chat_type == "config"`` into ``submit_graph("config", ...)``.

Tools adapt existing domain services only — never business DML or free-form SQL.
The model/tool loop, event stream and record lifecycle use conversation core.

Topology is driven by ``backend/graphs/current/config.yaml``.
Only scene preparation lives in ``apps.config_assistant.nodes``.
"""
