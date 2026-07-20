"""Domain atoms for chat scenarios.

Import submodules directly preferred
(``from apps.chat.steps.terminology import match_terminology``).
Package-level re-exports stay lazy so surfaces do not force sqlbot_xpack I/O.
"""

from __future__ import annotations

from typing import Any

__all__ = [
    "match_scope",
    "match_terminology",
    "match_training",
    "match_custom_prompts",
    "match_table_schema",
    "build_prompt_messages",
    "get_last_conversation_rounds",
    "process_stream",
    "generate_sql",
    "generate_chart",
    "generate_analysis",
    "generate_predict",
    "generate_recommend_questions",
    "select_datasource",
    "validate_history_ds",
    "check_save_sql",
    "check_save_chart",
    "check_save_predict_data",
    "save_sql_data",
    "generate_filter",
    "generate_assistant_dynamic_sql",
]


def __getattr__(name: str) -> Any:
    mapping = {
        "match_scope": ("apps.chat.steps.scope", "match_scope"),
        "match_terminology": ("apps.chat.steps.terminology", "match_terminology"),
        "match_training": ("apps.chat.steps.training", "match_training"),
        "match_custom_prompts": ("apps.chat.steps.custom_prompt", "match_custom_prompts"),
        "match_table_schema": ("apps.chat.steps.schema", "match_table_schema"),
        "build_prompt_messages": ("apps.chat.steps.messages", "build_prompt_messages"),
        "get_last_conversation_rounds": (
            "apps.chat.steps.history",
            "get_last_conversation_rounds",
        ),
        "process_stream": ("apps.chat.steps.stream", "process_stream"),
        "generate_sql": ("apps.chat.steps.sql", "generate_sql"),
        "generate_chart": ("apps.chat.steps.chart", "generate_chart"),
        "generate_analysis": ("apps.chat.steps.analysis", "generate_analysis"),
        "generate_predict": ("apps.chat.steps.predict", "generate_predict"),
        "generate_recommend_questions": (
            "apps.chat.steps.recommend",
            "generate_recommend_questions",
        ),
        "select_datasource": ("apps.chat.steps.datasource", "select_datasource"),
        "validate_history_ds": ("apps.chat.steps.datasource", "validate_history_ds"),
        "check_save_sql": ("apps.chat.steps.persist", "check_save_sql"),
        "check_save_chart": ("apps.chat.steps.persist", "check_save_chart"),
        "check_save_predict_data": ("apps.chat.steps.predict", "check_save_predict_data"),
        "save_sql_data": ("apps.chat.steps.persist", "save_sql_data"),
        "generate_filter": ("apps.chat.steps.permissions", "generate_filter"),
        "generate_assistant_dynamic_sql": (
            "apps.chat.steps.permissions",
            "generate_assistant_dynamic_sql",
        ),
    }
    if name not in mapping:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    mod_name, attr = mapping[name]
    import importlib

    mod = importlib.import_module(mod_name)
    return getattr(mod, attr)
