"""Wiki knowledge search tool for the unified agent."""

from __future__ import annotations

from typing import Any

from apps.chat.agent_knowledge import (
    WIKI_SCHEMA_GAP_SEARCH_LIMIT,
    AgentKnowledgePlane,
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
    data["tables"] = [name for name in (data.get("tables") or []) if str(name) in allowed]
    bodies = split_schema_text(str(data.get("schema_text") or ""), tables=list(allowed))
    data["schema_text"] = "\n".join(
        bodies[name] for name in data["tables"] if bodies.get(name)
    )
    evidence = dict(data.get("table_evidence") or {})
    data["table_evidence"] = {
        name: evidence.get(name) or [] for name in data["tables"]
    }
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


def search_wiki_knowledge(
    llm_service: Any,
    query: str,
    *,
    access_scope: Any = None,
    top_k: int | None = None,
) -> ToolResult:
    """Retrieve Wiki/schema into the knowledge plane; return a coverage stub."""
    clean_query = str(query or "").strip()
    if not clean_query:
        return failure_result("Query cannot be empty for Wiki search", retryable=True)

    try:
        res = retrieve_wiki_context(
            llm_service,
            clean_query,
            access_scope=access_scope,
            top_k=top_k,
        )
        plane = _load_plane()
        plane, policy, delta = apply_wiki_search_policy(dict(res), plane)
        _save_plane(plane)

        stub = search_wiki_stub(
            delta=delta,
            policy=policy,
            plane=plane,
            backend=str(res.get("backend") or ""),
        )
        status = str(policy.get("recall_status") or "")
        backend = stub.get("backend") or "none"

        if policy.get("stop_search") and status == "no_new_evidence":
            return success_result(
                (
                    "No new Wiki evidence: extra tables were not merged. "
                    "stop_search is set. Do not call search_wiki again. "
                    "Write SQL from the system schema_catalog or request_clarification."
                ),
                data=stub,
            )
        if policy.get("stop_search") and status in {"round_limit", "budget_exhausted"}:
            return success_result(
                (
                    "Wiki search budget reached. stop_search is set. "
                    "Do not call search_wiki again. Write SQL or tell the user "
                    "the knowledge base cannot cover this yet."
                ),
                data=stub,
            )
        if policy.get("stop_search") and status == "stagnant" and plane.schema_ready:
            return success_result(
                (
                    "Coverage unchanged: tables already in the system schema_catalog. "
                    "Do not call search_wiki again for the same tables. "
                    "Write SQL or request_clarification."
                ),
                data=stub,
            )
        if policy.get("stop_search"):
            return success_result(
                (
                    "Wiki recall stalled: no published table/enum schema after "
                    f"{stub.get('schema_gap_searches') or WIKI_SCHEMA_GAP_SEARCH_LIMIT} "
                    "attempts. Do not call search_wiki again. Do not query "
                    "information_schema / SHOW COLUMNS. Stop tool use and tell "
                    "the user the knowledge base cannot answer this yet."
                ),
                data=stub,
            )
        if status == "schema_missing":
            return success_result(
                (
                    f"Retrieved knowledge (source: {backend}, "
                    f"added_tables: {delta.added_tables}) "
                    "but no table/enum schema. One more targeted search_wiki is "
                    "allowed; do not query information_schema."
                ),
                data=stub,
            )
        if delta.unchanged and not plane.schema_ready:
            return success_result(
                (
                    "No matching knowledge for this query. "
                    "One more targeted search_wiki is allowed if table/enum schema "
                    "is still missing; otherwise stop."
                ),
                data=stub,
            )
        return success_result(
            (
                f"Merged into system catalog (source: {backend}, "
                f"added_tables: {delta.added_tables}, "
                f"added_pages: {delta.added_pages})."
            ),
            data=stub,
        )
    except Exception as exc:
        SQLBotLogUtil.error(f"search_wiki_knowledge failed: {exc}")
        return failure_result(f"Failed to search Wiki: {exc}", retryable=True)
