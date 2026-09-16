"""Wiki knowledge search tool for the unified agent."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from apps.chat.agent_knowledge import (
    SEARCH_WIKI_ROUND_LIMIT,
    WIKI_SCHEMA_GAP_SEARCH_LIMIT,
    AgentKnowledgePlane,
    MergeDelta,
    search_wiki_stub,
)
from apps.chat.steps.wiki_recall import retrieve_wiki_context
from apps.chat.tools.base import failure_result, success_result
from apps.conversation.runtime_context import (
    attach_runtime,
    current_worker_identity,
    peek_runtime,
)
from apps.conversation.tooling import ToolResult
from common.utils.utils import SQLBotLogUtil


def _load_plane() -> AgentKnowledgePlane:
    run_id, _token = current_worker_identity()
    if not run_id:
        return AgentKnowledgePlane()
    snap = peek_runtime(run_id) or {}
    return AgentKnowledgePlane.from_dump(snap.get("knowledge_plane"))


def _save_plane(plane: AgentKnowledgePlane) -> None:
    run_id, _token = current_worker_identity()
    if not run_id:
        return
    attach_runtime(run_id, knowledge_plane=plane.to_dump())


def _filter_payload_tables(payload: dict[str, Any], kept: list[str]) -> dict[str, Any]:
    from apps.chat.agent_knowledge import split_schema_text

    data = dict(payload)
    allowed = {str(name) for name in kept}
    data["tables"] = [
        name for name in (data.get("tables") or []) if str(name) in allowed
    ]
    bodies = split_schema_text(str(data.get("schema_text") or ""), tables=list(allowed))
    data["schema_text"] = "\n".join(
        bodies[name] for name in data["tables"] if bodies.get(name)
    )
    evidence = dict(data.get("table_evidence") or {})
    data["table_evidence"] = {name: evidence.get(name) or [] for name in data["tables"]}
    return data


def apply_wiki_search_policy(
    payload: dict[str, Any],
    plane: AgentKnowledgePlane,
) -> tuple[AgentKnowledgePlane, dict[str, Any], Any]:
    """Merge recall into the plane and apply coverage / stop-search policy."""
    plane.search_rounds += 1
    data = dict(payload)
    incoming_pages = [
        str(key)
        for key in (data.get("page_keys") or [])
        if str(key) and str(key) not in plane.page_keys
    ]
    evidence = data.get("table_evidence") or {}
    incoming_tables = [str(name) for name in (data.get("tables") or []) if str(name)]
    stripped = False
    if not incoming_pages and plane.schema_ready:
        kept = [
            name
            for name in incoming_tables
            if name in plane.tables or evidence.get(name)
        ]
        if kept != incoming_tables:
            data = _filter_payload_tables(data, kept)
            stripped = True
    delta = plane.merge_recall(data)
    policy = plane.apply_search_policy(delta)
    if stripped and delta.unchanged:
        policy = {
            **policy,
            "recall_status": "no_new_evidence",
            "stop_search": True,
        }
    return plane, policy, delta


def _search_pace_note(plane: AgentKnowledgePlane) -> str:
    if plane.search_rounds < SEARCH_WIKI_ROUND_LIMIT:
        return ""
    return (
        "已经检索多轮：优先基于当前系统提示写 SQL 或 complete_without_sql；"
        "仅当出现新的缺口概念时再换检索词 search_wiki。"
    )


def _with_pace(message: str, plane: AgentKnowledgePlane) -> str:
    note = _search_pace_note(plane)
    if not note:
        return message
    return f"{message} {note}"


def _continuation_request(plane: AgentKnowledgePlane, query: str) -> Any:
    """Mid-turn search_wiki keeps the plane's tables/pages/queries in the pin set.

    A bare keyword like「城市」would otherwise cold-recall unrelated pages and
    lose the baseline working set that the agent already paid for.
    """
    from apps.chat.steps.recall_request import RecallRequest

    clean = str(query or "").strip()
    if not (plane.tables or plane.page_keys or plane.queries):
        return RecallRequest.simple(clean)
    priors = [str(q).strip() for q in plane.queries[-2:] if str(q).strip()]
    retrieval = "\n".join([*(q for q in priors if q != clean), clean])
    return RecallRequest(
        query=retrieval,
        question=clean,
        pin_tables=tuple(str(name) for name in plane.tables if str(name).strip()),
        pin_pages=tuple(str(key) for key in plane.page_keys if str(key).strip())[:12],
        required_fields={
            str(table): tuple(str(n) for n in names if str(n).strip())
            for table, names in plane.keep_fields.items()
            if names
        },
    )


def _recall_hit_count(payload: Mapping[str, Any]) -> int:
    try:
        n = int(payload.get("hit_count") or 0)
    except (TypeError, ValueError):
        n = 0
    if n > 0:
        return n
    return len(
        [
            str(key).strip()
            for key in (payload.get("page_keys") or [])
            if str(key).strip()
        ]
    )


def search_wiki_knowledge(
    llm_service: Any,
    query: str = "",
    *,
    drop: Sequence[str] | None = None,
    access_scope: Any = None,
    top_k: int | None = None,
) -> ToolResult:
    """Retrieve Wiki/schema into the knowledge plane; return a coverage stub.

    ``drop`` evicts table names / page_keys from later prompt assembly. A
    drop-only call (empty query) does not consume a search round.
    """
    clean_query = str(query or "").strip()
    drop_keys = [str(item).strip() for item in (drop or []) if str(item).strip()]
    if not clean_query and not drop_keys:
        return failure_result("Query cannot be empty for Wiki search", retryable=True)

    try:
        plane = _load_plane()
        dropped: dict[str, list[str]] = {"tables": [], "pages": []}
        if drop_keys:
            dropped = plane.exclude_knowledge(drop_keys)
            _save_plane(plane)
        if not clean_query:
            stub = search_wiki_stub(
                delta=MergeDelta(unchanged=True, schema_ready=plane.schema_ready),
                policy={
                    "schema_ready": plane.schema_ready,
                    "stop_search": False,
                    "recall_status": "dropped",
                    "schema_gap_searches": plane.schema_gap_searches,
                    "dropped_tables": dropped["tables"],
                    "dropped_pages": dropped["pages"],
                },
                plane=plane,
            )
            return success_result(
                (
                    f"已从系统提示淘汰：表 {dropped['tables']}，页 {dropped['pages']}。"
                    "全文见更新后的系统提示；不要淘汰 JOIN 对端或口径仍依赖的表。"
                ),
                data=stub,
            )

        res = retrieve_wiki_context(
            llm_service,
            _continuation_request(plane, clean_query),
            access_scope=access_scope,
            top_k=top_k,
        )
        plane, policy, delta = apply_wiki_search_policy(dict(res), plane)
        if drop_keys:
            policy = {
                **policy,
                "dropped_tables": dropped["tables"],
                "dropped_pages": dropped["pages"],
            }
        _save_plane(plane)

        stub = search_wiki_stub(
            delta=delta,
            policy=policy,
            plane=plane,
            backend=str(res.get("backend") or ""),
            hit_count=_recall_hit_count(res),
        )
        status = str(policy.get("recall_status") or "")
        backend = stub.get("backend") or "none"

        if policy.get("stop_search") and status == "no_new_evidence":
            return success_result(
                _with_pace(
                    (
                        "本次检索没有新的 Wiki 证据（无证据的表未并入）。"
                        "不要用近义词再搜同一批表；出现新缺口再换检索词。"
                        "请基于系统提示写 SQL，或 request_clarification / complete_without_sql。"
                    ),
                    plane,
                ),
                data=stub,
            )
        if policy.get("stop_search") and status == "stagnant" and plane.schema_ready:
            return success_result(
                _with_pace(
                    (
                        "覆盖面未变化：相关表已在系统提示的 schema_catalog 中。"
                        "不要对同一批表再检索；新概念再针对性 search_wiki，"
                        "否则写 SQL 或 request_clarification。"
                    ),
                    plane,
                ),
                data=stub,
            )
        if status == "schema_missing":
            gap = int(stub.get("schema_gap_searches") or 0)
            extra = (
                f"已连续 {gap} 次没有表/枚举结构，换更具体的业务检索词，或 complete_without_sql。"
                if gap >= WIKI_SCHEMA_GAP_SEARCH_LIMIT
                else "换更具体的检索词再 search_wiki，或 complete_without_sql。"
            )
            return success_result(
                _with_pace(
                    (
                        f"已检索到知识（来源 {backend}，新增表 {delta.added_tables}），"
                        f"但没有表/枚举结构。{extra}"
                        "不要查询 information_schema。"
                    ),
                    plane,
                ),
                data=stub,
            )
        if delta.unchanged and not plane.schema_ready:
            return success_result(
                _with_pace(
                    (
                        "没有与该检索词匹配的知识。表/枚举结构仍缺失时，"
                        "换更具体的检索词再 search_wiki，或 complete_without_sql。"
                    ),
                    plane,
                ),
                data=stub,
            )
        return success_result(
            _with_pace(
                (
                    f"已并入系统提示的 schema_catalog / wiki_knowledge（来源 {backend}）："
                    f"新增表 {delta.added_tables}，新增页 {delta.added_pages}，"
                    f"新增可见字段 {stub.get('added_fields') or {}}。"
                    "全文见系统提示；同一对象不要重复检索，新缺口可以再搜。"
                ),
                plane,
            ),
            data=stub,
        )
    except Exception as exc:
        SQLBotLogUtil.error(f"search_wiki_knowledge failed: {exc}")
        return failure_result(f"Failed to search Wiki: {exc}", retryable=True)
