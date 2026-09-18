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
    scores = dict(data.get("table_scores") or {})
    if scores:
        data["table_scores"] = {
            name: scores.get(name, 0.0) for name in data["tables"] if name in scores
        }
    return data


def _admit_payload(
    data: dict[str, Any],
    plane: AgentKnowledgePlane,
    *,
    query: str,
    named_query: str = "",
) -> tuple[dict[str, Any], list[str], list[str]]:
    """Strip peripheral pages and long-tail tables before they merge into RAM."""
    from apps.chat.steps.wiki_focus import admit_pages, admit_tables

    incoming_pages = [str(key) for key in (data.get("page_keys") or []) if str(key)]
    incoming_tables = [str(name) for name in (data.get("tables") or []) if str(name)]
    evidence = data.get("table_evidence") or {}
    scores = data.get("table_scores") or {}
    admitted, rejected_tables = admit_tables(
        incoming_tables,
        plane=plane,
        evidence=evidence if isinstance(evidence, Mapping) else {},
        scores=scores if isinstance(scores, Mapping) else {},
        query=query,
        schema_text=str(data.get("schema_text") or ""),
    )
    working = list(dict.fromkeys([*plane.tables, *admitted]))
    page_query = named_query or query
    kept_pages = admit_pages(incoming_pages, working_tables=working, query=page_query)
    allowed_pages = {str(key) for key in plane.page_keys} | set(kept_pages)
    rejected_pages = [
        key
        for key in incoming_pages
        if key not in plane.page_keys and key not in kept_pages
    ]
    data["page_keys"] = [
        key for key in (data.get("page_keys") or []) if str(key) in allowed_pages
    ]
    passages = dict(data.get("wiki_passages") or {})
    if passages:
        data["wiki_passages"] = {
            key: text for key, text in passages.items() if str(key) in allowed_pages
        }
    if rejected_pages and not kept_pages:
        data["knowledge_text"] = ""
    if admitted != incoming_tables:
        data = _filter_payload_tables(data, admitted)
    return data, rejected_tables, rejected_pages


def apply_wiki_search_policy(
    payload: dict[str, Any],
    plane: AgentKnowledgePlane,
    *,
    focus: str = "all",
    query: str = "",
) -> tuple[AgentKnowledgePlane, dict[str, Any], Any]:
    """Merge recall into the plane and apply coverage / stop-search policy."""
    from apps.chat.steps.wiki_focus import (
        LOCAL_FOCUS,
        binding_pages,
        expanded_tables,
        normalize_focus,
    )

    kind = normalize_focus(focus)
    if kind not in LOCAL_FOCUS:
        plane.search_rounds += 1
    data = dict(payload)
    catalog_query = str(
        data.get("question")
        or getattr(plane, "question", "")
        or query
        or data.get("query")
        or ""
    ).strip()
    named_query = str(query or data.get("query") or "").strip()
    rejected_tables: list[str] = []
    rejected_pages: list[str] = []
    if kind not in LOCAL_FOCUS:
        data, rejected_tables, rejected_pages = _admit_payload(
            data, plane, query=catalog_query, named_query=named_query
        )
    delta = plane.merge_recall(data)
    policy = plane.apply_search_policy(delta, focus=kind)
    if kind in LOCAL_FOCUS:
        found = bool((data.get("focus_facts") or {}).get("found"))
        policy = {
            **policy,
            "recall_status": "hit" if found else "not_found",
            "stop_search": not found,
        }
    if kind not in LOCAL_FOCUS and policy.get("recall_status") == "hit":
        if not delta.added_tables and not binding_pages(
            delta.added_pages, plane.tables
        ):
            policy = {
                **policy,
                "recall_status": "diminishing_returns",
                "stop_search": True,
            }
    folded = [name for name in plane.tables if name not in set(expanded_tables(plane))]
    policy = {
        **policy,
        "focus": kind,
        "focus_facts": dict(data.get("focus_facts") or {}),
        "rejected_tables": rejected_tables,
        "rejected_pages": rejected_pages,
        "folded_tables": folded,
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


def _lookup_message(
    kind: str, payload: Mapping[str, Any], policy: Mapping[str, Any]
) -> str:
    facts = dict(payload.get("focus_facts") or {})
    found = list(facts.get("found") or [])
    missing = list(facts.get("missing") or [])
    needle = str(facts.get("query") or (missing[0] if missing else "") or "")
    if policy.get("recall_status") == "not_found" or not found:
        return (
            f"在当前表中未找到名为 {needle or '该对象'} 的{kind}。"
            "该列大概率无需查询或属于自定义扩展，请勿反复搜索，"
            "可直接编写 SQL、complete_without_sql 或向用户澄清。"
        )
    if kind == "dict":
        mappings = [
            f"{item.get('table')}.{item.get('field')}={item.get('enums') or {}}"
            for item in found
            if isinstance(item, Mapping)
        ]
        return (
            f"已核对枚举（未注入 Wiki 正文）：{mappings}。"
            "取值以本次核对为准；不要再综合搜索同一字段。"
        )
    if kind == "relation":
        pairs = [
            f"{item.get('left')}↔{item.get('right')}"
            for item in found
            if isinstance(item, Mapping)
        ]
        return f"已核验表关联（未注入 Wiki 正文）：{pairs}。可据此写 JOIN。"
    if kind == "term":
        keys = [
            str(item.get("page_key") or item.get("title") or "")
            for item in found
            if isinstance(item, Mapping)
        ]
        return f"已核对术语别名（未注入 Wiki 正文）：{keys}。"
    rows = [
        f"{item.get('table')}.{item.get('field')}（{item.get('comment') or ''}）"
        for item in found
        if isinstance(item, Mapping)
    ]
    return (
        f"已核对字段并点亮投影（未注入 Wiki 正文）：{rows}。"
        "下一轮系统提示会展开这些列；不要再用 focus=all 确认同一列。"
    )


def _comprehensive_message(
    plane: AgentKnowledgePlane,
    policy: Mapping[str, Any],
    delta: Any,
    stub: Mapping[str, Any],
) -> str:
    status = str(policy.get("recall_status") or "")
    backend = stub.get("backend") or "none"
    rejected = list(stub.get("rejected_tables") or []) + list(
        stub.get("rejected_pages") or []
    )
    rejected_note = (
        f"未准入 {rejected}（点名 search_wiki 可并入）。" if rejected else ""
    )
    if policy.get("stop_search") and status == "no_new_evidence":
        return _with_pace(
            (
                "本次检索没有新的 Wiki 证据（无证据的表未并入）。"
                "不要用近义词再搜同一批表；出现新缺口再换检索词。"
                "请基于系统提示写 SQL，或 request_clarification / complete_without_sql。"
            ),
            plane,
        )
    if status == "diminishing_returns":
        return _with_pace(
            (
                "当前业务主表已齐备，综合搜索未发现更多结构。"
                f"{rejected_note}"
                "如需核对具体列或字典，请指定 focus=field|dict|term|relation 进行核查；"
                "若口径已大致清晰，请直接编写 SQL 或发起澄清。"
                "stop_search 仅为软提示，新业务线索仍可再搜。"
            ),
            plane,
        )
    if status == "schema_missing":
        gap = int(stub.get("schema_gap_searches") or 0)
        extra = (
            f"已连续 {gap} 次没有表/枚举结构，换更具体的业务检索词，或 complete_without_sql。"
            if gap >= WIKI_SCHEMA_GAP_SEARCH_LIMIT
            else "换更具体的检索词再 search_wiki，或 complete_without_sql。"
        )
        return _with_pace(
            (
                f"已检索到知识（来源 {backend}，新增表 {delta.added_tables}），"
                f"但没有表/枚举结构。{extra}"
                "不要查询 information_schema。"
            ),
            plane,
        )
    if delta.unchanged and not plane.schema_ready:
        return _with_pace(
            (
                "没有与该检索词匹配的知识。表/枚举结构仍缺失时，"
                "换更具体的检索词再 search_wiki，或 complete_without_sql。"
            ),
            plane,
        )
    folded = list(stub.get("folded_tables") or [])
    folded_note = f"折叠为索引的表 {folded}。" if folded else ""
    return _with_pace(
        (
            f"已并入系统提示的 schema_catalog / wiki_knowledge（来源 {backend}）："
            f"新增表 {delta.added_tables}，新增页 {delta.added_pages}，"
            f"新增可见字段 {stub.get('added_fields') or {}}。"
            f"{rejected_note}{folded_note}"
            "全文见系统提示；同一对象不要重复检索，新缺口可以再搜。"
        ),
        plane,
    )


def _human_question(llm_service: Any, plane: AgentKnowledgePlane, fallback: str) -> str:
    chat_q = getattr(getattr(llm_service, "chat_question", None), "question", None)
    return (
        str(getattr(plane, "question", "") or "").strip()
        or str(chat_q or "").strip()
        or (str(plane.queries[0]).strip() if plane.queries else "")
        or str(fallback or "").strip()
    )


def _continuation_request(
    plane: AgentKnowledgePlane,
    query: str,
    *,
    focus: str = "all",
    question: str = "",
) -> Any:
    """Mid-turn search_wiki pins the working set; never concatenates old tool queries.

    Named page keys open by identity without a second RRF pass, so a rule slug
    cannot expand tables. New needles stay this sentence only.
    """
    from apps.chat.steps.recall_request import RecallRequest
    from apps.chat.steps.wiki_focus import named_wiki_keys

    clean = str(query or "").strip()
    human = str(question or getattr(plane, "question", "") or "").strip()
    if plane.queries and not human:
        human = str(plane.queries[0] or "").strip()
    named = named_wiki_keys(clean)
    if not (plane.tables or plane.page_keys or plane.queries):
        text = human or clean
        return RecallRequest.simple(text, focus=focus)
    pin_tables = tuple(str(name) for name in plane.tables if str(name).strip())
    pin_pages = list(
        dict.fromkeys(
            [
                *(str(key) for key in plane.page_keys if str(key).strip()),
                *named,
            ]
        )
    )[:12]
    required = {
        str(table): tuple(str(n) for n in names if str(n).strip())
        for table, names in plane.keep_fields.items()
        if names
    }
    if named:
        return RecallRequest(
            query="",
            question=human or clean,
            pin_tables=pin_tables,
            pin_pages=tuple(pin_pages),
            required_fields=required,
            focus=focus,
        )
    return RecallRequest(
        query=clean,
        question=human or clean,
        pin_tables=pin_tables,
        pin_pages=tuple(pin_pages),
        required_fields=required,
        focus=focus,
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
    focus: str = "all",
    access_scope: Any = None,
    top_k: int | None = None,
) -> ToolResult:
    """Retrieve Wiki/schema into the knowledge plane; return a coverage stub.

    ``drop`` evicts table names / page_keys from later prompt assembly. A
    drop-only call (empty query) does not consume a search round.
    ``focus`` other than ``all`` looks up facts on the current plane.
    """
    from apps.chat.steps.wiki_focus import (
        LOCAL_FOCUS,
        infer_focus,
        lookup_payload,
        normalize_focus,
    )

    clean_query = str(query or "").strip()
    drop_keys = [str(item).strip() for item in (drop or []) if str(item).strip()]
    if not clean_query and not drop_keys:
        return failure_result("Query cannot be empty for Wiki search", retryable=True)

    try:
        plane = _load_plane()
        human = _human_question(llm_service, plane, clean_query)
        if human and not plane.question:
            plane.question = human
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
                    "focus": "all",
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

        kind = infer_focus(clean_query, plane, declared=normalize_focus(focus))
        if kind in LOCAL_FOCUS:
            payload = lookup_payload(
                plane, clean_query, focus=kind, llm_service=llm_service
            )
            plane, policy, delta = apply_wiki_search_policy(payload, plane, focus=kind)
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
                backend="lookup",
                hit_count=int(payload.get("hit_count") or 0),
            )
            return success_result(
                _lookup_message(kind, payload, policy),
                data=stub,
            )

        res = retrieve_wiki_context(
            llm_service,
            _continuation_request(
                plane, clean_query, focus=kind, question=plane.question or human
            ),
            access_scope=access_scope,
            top_k=top_k,
        )
        plane, policy, delta = apply_wiki_search_policy(
            dict(res), plane, focus=kind, query=clean_query
        )
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
        return success_result(
            _comprehensive_message(plane, policy, delta, stub),
            data=stub,
        )
    except Exception as exc:
        SQLBotLogUtil.error(f"search_wiki_knowledge failed: {exc}")
        return failure_result(f"Failed to search Wiki: {exc}", retryable=True)
