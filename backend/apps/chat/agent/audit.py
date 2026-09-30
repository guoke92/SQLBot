"""Chat-agent audit spans. Display titles stay on process_timeline title_key."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from apps.chat.agent_knowledge import KNOWLEDGE_BUDGET_SKIP
from apps.conversation.process_timeline import open_process_span
from apps.conversation.sink import StreamSink


def tool_close_keys(name: str, result: Mapping[str, Any]) -> tuple[str, dict[str, Any]]:
    """Knowledge tools report hit counts; skipped budget is not a failure."""
    from apps.chat.tools.contract import outcome_payload

    signals = result.get("signals") if isinstance(result.get("signals"), Mapping) else {}
    data = outcome_payload(result)
    if (isinstance(signals, Mapping) and signals.get("skipped")) or data.get(
        "reason"
    ) == KNOWLEDGE_BUDGET_SKIP:
        return "chat.summary.tool_skipped", {"tool": name}
    if not result.get("ok"):
        return "chat.summary.tool_failed", {"tool": name}
    if name == "get_table_schema":
        count = len(data.get("tables") or data.get("added_tables") or [])
        return "chat.summary.schema_loaded", {"count": count}
    if name == "get_table_relations":
        count = len(data.get("direct") or []) + len(data.get("bridges") or [])
        return "chat.summary.relations_loaded", {"count": count}
    if name == "search_knowledge":
        count = int(data.get("hit_count") or len(data.get("page_keys") or []) or 0)
        return "chat.summary.wiki_prepared", {"count": count}
    if name == "get_dict_values":
        count = len(data.get("values") or [])
        return "chat.summary.dict_loaded", {"count": count}
    if name == "lookup_values":
        count = len(data.get("candidates") or [])
        return "chat.summary.values_loaded", {"count": count}
    return "chat.summary.tool_ok", {"tool": name}


def emit_compact_span(
    *,
    record_id: Any,
    run_id: str | None,
    sink: StreamSink | None,
    folds: list[Mapping[str, Any]],
    ai_modal_id: Any = None,
    ai_modal_name: str | None = None,
) -> None:
    if not folds or record_id is None:
        return
    span = open_process_span(
        kind="thought",
        record_id=record_id,
        sink=sink,
        run_id=run_id,
        graph_node="agent_loop",
        title_key="chat.timeline.thought",
        thought={"source": "compact", "content": ""},
        meta={"compact": True},
        local_operation=True,
        ai_modal_id=ai_modal_id,
        ai_modal_name=ai_modal_name,
    )
    if span is None:
        return
    span.set_meta({"compact": True})
    span.set_output({"folds": [dict(item) for item in folds], "compact": True})
    span.close(status="completed", summary_key="chat.summary.thought_done")
