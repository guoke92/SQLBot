"""Process timeline writer, projector helpers, and truncation contract."""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.conversation.process_timeline import (  # noqa: E402
    _compact_item,
    _emit_process_event,
    _item_from_log,
    _process_payload,
    localize_process_event,
    localize_process_item,
    preview_rows,
    project_thought_for_view,
    tool_title_key,
)
from apps.chat.graphs.nodes.agent_finalize import infer_chart_for_presentation  # noqa: E402
from apps.chat.tools.execute_sql import execute_sql_sandbox  # noqa: E402


def test_markdown_sink_does_not_emit_events() -> None:
    sink = SimpleNamespace(mode="markdown", event=MagicMock())
    _emit_process_event(
        sink, event_type="process_upsert", item={"id": 1, "kind": "thought"}
    )
    sink.event.assert_not_called()


def test_sse_sink_emits_compact_item_without_detail() -> None:
    sink = SimpleNamespace(mode="sse", event=MagicMock())
    item = {
        "id": 7,
        "kind": "tool",
        "detail": {"input": "secret-prompt"},
        "title_key": "k",
    }
    _emit_process_event(sink, event_type="process_upsert", item=item)
    payload = sink.event.call_args.args[0]
    assert payload["type"] == "process_upsert"
    assert payload["item"]["id"] == 7
    assert "detail" not in payload["item"]


def test_sse_delta_keeps_full_thought() -> None:
    sink = SimpleNamespace(mode="sse", event=MagicMock())
    body = "字" * 1400
    _emit_process_event(
        sink,
        event_type="process_delta",
        item={
            "id": 3,
            "kind": "thought",
            "thought": {"content": body, "source": "model_reasoning"},
            "detail": {"input": "hidden"},
        },
    )
    payload = sink.event.call_args.args[0]
    thought = payload["item"]["thought"]
    assert payload["type"] == "process_delta"
    assert "truncated" not in thought
    assert thought["content"] == body
    assert "detail" not in payload["item"]


def test_compact_item_strips_detail() -> None:
    compact = _compact_item({"id": 1, "detail": {"x": 1}, "kind": "thought"})
    assert compact == {"id": 1, "kind": "thought"}


def test_project_thought_for_view_keeps_full_body() -> None:
    body = "字" * 1400
    thought = {"source": "model_reasoning", "content": body}
    compact = project_thought_for_view(thought, "compact")
    assert compact is not None
    assert "truncated" not in compact
    assert compact["content"] == body
    detail = project_thought_for_view(thought, "detail")
    assert detail is not None
    assert "truncated" not in detail
    assert detail["content"] == body
    emitted = _compact_item({"id": 1, "kind": "thought", "thought": thought})
    assert "truncated" not in emitted["thought"]
    assert emitted["thought"]["content"] == body


def test_item_from_log_keeps_full_thought_on_compact_and_detail() -> None:
    from apps.chat.steps.observability import make_span_message

    body = "字" * 1400
    envelope = make_span_message(
        graph_node="agent_loop",
        title_key="chat.timeline.thought",
        payload=_process_payload(
            kind="thought",
            thought={"content": body, "source": "model_reasoning"},
        ),
    )
    log = SimpleNamespace(
        id=11,
        run_id="r1",
        pid=9,
        messages=envelope,
        reasoning_content=None,
        finish_time=None,
        start_time=None,
        error=False,
        token_usage={},
        operate=None,
    )
    compact = _item_from_log(log, view="compact")  # type: ignore[arg-type]
    assert compact is not None
    assert "truncated" not in compact["thought"]
    assert compact["thought"]["content"] == body
    assert "detail" not in compact
    detail = _item_from_log(log, view="detail")  # type: ignore[arg-type]
    assert detail is not None
    assert "truncated" not in detail["thought"]
    assert detail["thought"]["content"] == body
    assert "detail" in detail


def test_localize_process_item_and_event() -> None:
    def trans(key: str, **params) -> str:
        if key == "chat.timeline.tool.execute_sql_sandbox":
            return f"SQL {params.get('n', '')}".strip()
        return key

    item = localize_process_item(
        {
            "id": 1,
            "kind": "tool",
            "title_key": "chat.timeline.tool.execute_sql_sandbox",
            "title_params": {"n": 2},
            "summary_key": "chat.summary.query_rows",
            "summary_params": {"count": 3},
        },
        trans,
    )
    assert item["title"] == "SQL 2"
    event = localize_process_event(
        {
            "type": "process_upsert",
            "item": {
                "id": 1,
                "title_key": "chat.timeline.tool.execute_sql_sandbox",
                "title_params": {},
            },
        },
        trans,
    )
    assert event["item"]["title"] == "SQL"


def test_tool_title_key_and_preview_rows() -> None:
    assert (
        tool_title_key("execute_sql_sandbox")
        == "chat.timeline.tool.execute_sql_sandbox"
    )
    assert tool_title_key("") == "chat.timeline.tool.generic"
    rows = preview_rows([{"a": 1}, {"a": 2}, {"a": 3}, {"a": 4}], limit=3)
    assert len(rows) == 3
    assert rows[0]["a"] == 1


def test_chart_inference_uses_value_kinds_not_column_names() -> None:
    presentation = {
        "title": "t",
        "columns": [
            {"field": "month_label", "label": "month_label", "display": "month_label"},
            {"field": "qty", "label": "qty", "display": "qty"},
        ],
    }
    chart = infer_chart_for_presentation(
        presentation,  # type: ignore[arg-type]
        ["month_label", "qty"],
        [{"month_label": "alpha", "qty": 1}, {"month_label": "beta", "qty": 2}],
    )
    assert chart["type"] in {"bar", "table"}
    assert "series" not in (chart.get("axis") or {})
    temporal = infer_chart_for_presentation(
        presentation,  # type: ignore[arg-type]
        ["month_label", "qty"],
        [
            {"month_label": "2024-01-01", "qty": 1},
            {"month_label": "2024-02-01", "qty": 2},
        ],
    )
    assert temporal["type"] == "line"
    assert "series" not in (temporal.get("axis") or {})


def test_chart_inference_rejects_identifier_as_measure() -> None:
    """Entity listings with snowflake id + create_time must stay tables."""
    fields = [
        "id",
        "name",
        "cust_no",
        "identify_style",
        "create_time",
    ]
    presentation = {
        "title": "企业清单",
        "columns": [{"field": f, "label": f, "display": f} for f in fields],
    }
    rows = [
        {
            "id": 1946025846161575938,
            "name": "甲",
            "cust_no": "C1",
            "identify_style": "INVITE_AGW",
            "create_time": "2025-03-05 15:34:30",
        },
        {
            "id": 2100000000000000000,
            "name": "乙",
            "cust_no": "C2",
            "identify_style": "INVITE_AGW",
            "create_time": "2025-05-29 18:21:04",
        },
        {
            "id": 1750000000000000000,
            "name": "丙",
            "cust_no": "C3",
            "identify_style": "INVITE",
            "create_time": "2024-07-25 10:05:12",
        },
    ]
    chart = infer_chart_for_presentation(
        presentation,  # type: ignore[arg-type]
        fields,
        rows,
    )
    assert chart["type"] == "table"

    credit = infer_chart_for_presentation(
        {
            "title": "t",
            "columns": [
                {"field": "建档创建时间", "label": "", "display": "建档创建时间"},
                {"field": "统一信用代码", "label": "", "display": "统一信用代码"},
            ],
        },  # type: ignore[arg-type]
        ["建档创建时间", "统一信用代码"],
        [
            {"建档创建时间": "2024-01-01", "统一信用代码": "911100000123456789"},
            {"建档创建时间": "2024-02-01", "统一信用代码": "911100000765432109"},
            {"建档创建时间": "2024-03-01", "统一信用代码": "911100000987654321"},
        ],
    )
    assert credit["type"] == "table"


def test_select_delivery_datasets_skips_probes_untitled_replace() -> None:
    from apps.chat.graphs.nodes.agent_finalize import select_delivery_datasets

    probe = SimpleNamespace(
        dataset_id="p", required=False, status="succeeded", row_count=2
    )
    first = SimpleNamespace(
        dataset_id="a", required=True, status="succeeded", row_count=10
    )
    second = SimpleNamespace(
        dataset_id="b", required=True, status="succeeded", row_count=8
    )
    failed = SimpleNamespace(
        dataset_id="f", required=True, status="failed", row_count=0
    )
    picked = select_delivery_datasets([probe, first, failed, second])
    assert [item.dataset_id for item in picked] == ["b"]

    only_probe = select_delivery_datasets([probe])
    assert only_probe == []


def test_execute_sql_truncation_uses_protocol_max_rows(monkeypatch) -> None:
    fake_service = MagicMock()
    fake_service.protocol.parse_candidate_payload.return_value = MagicMock(
        success=True,
        statement="SELECT 1",
        message="",
    )
    fake_service.protocol.validate_plan.return_value = MagicMock(
        success=True, message=""
    )
    fake_service.protocol.execute.return_value = MagicMock(
        data=[{"id": i} for i in range(5)],
        fields=["id"],
        truncated=False,
    )
    stored: dict = {}

    def _upsert(**kwargs):
        stored.update(kwargs)

    monkeypatch.setattr("apps.chat.tools.execute_sql.upsert_result_dataset", _upsert)
    monkeypatch.setattr(
        "apps.chat.tools.execute_sql.current_worker_identity",
        lambda: ("run-1", "tok"),
    )
    monkeypatch.setattr(
        "apps.chat.tools.execute_sql.current_tool_call_id", lambda: "call-9"
    )
    monkeypatch.setattr(
        "apps.chat.tools.execute_sql.apply_wiki_enum_labels",
        lambda **_k: ([{"id": i} for i in range(5)], {"id": {"0": "zero"}}),
    )
    res = execute_sql_sandbox(fake_service, "SELECT 1", limit=5)
    assert res["ok"] is True
    assert stored["required"] is True
    assert stored["result_title"] == ""
    assert res["data"]["truncated"] is True
    assert res["data"]["row_count"] == 5
    assert res["data"]["limit"] == 5
    assert res["data"]["plan_id"] == "call-9"
    assert stored["truncated"] is True
    assert stored["row_count"] == 5
    assert stored["plan_id"] == "call-9"
    assert stored["value_labels"] == {"id": {"0": "zero"}}
    assert res["data"]["value_labels"] == {"id": {"0": "zero"}}
    fake_service.protocol.execute.assert_called()
    assert fake_service.protocol.execute.call_args.kwargs.get("max_rows") == 5


def test_execute_sql_probe_marks_not_required(monkeypatch) -> None:
    fake_service = MagicMock()
    fake_service.protocol.parse_candidate_payload.return_value = MagicMock(
        success=True,
        statement="SELECT 1",
        message="",
    )
    fake_service.protocol.validate_plan.return_value = MagicMock(
        success=True, message=""
    )
    fake_service.protocol.execute.return_value = MagicMock(
        data=[{"id": 1}],
        fields=["id"],
        truncated=False,
    )
    stored: dict = {}
    monkeypatch.setattr(
        "apps.chat.tools.execute_sql.upsert_result_dataset",
        lambda **kwargs: stored.update(kwargs),
    )
    monkeypatch.setattr(
        "apps.chat.tools.execute_sql.current_worker_identity",
        lambda: ("run-1", "tok"),
    )
    monkeypatch.setattr(
        "apps.chat.tools.execute_sql.current_tool_call_id", lambda: "call-1"
    )
    monkeypatch.setattr(
        "apps.chat.tools.execute_sql.apply_wiki_enum_labels",
        lambda **kwargs: (list(kwargs["rows"]), {}),
    )
    res = execute_sql_sandbox(
        fake_service,
        "SELECT 1",
        required=False,
        result_title="探查",
    )
    assert res["ok"] is True
    assert res["data"]["required"] is False
    assert stored["required"] is False
    assert stored["result_title"] == "探查"


def test_execute_sql_respects_sql_limit_above_default(monkeypatch) -> None:
    fake_service = MagicMock()
    fake_service.ds = MagicMock()
    fake_service.ds.type = "mysql"
    fake_service.table_name_list = None
    fake_service.protocol.parse_candidate_payload.return_value = MagicMock(
        success=True,
        statement="SELECT * FROM t LIMIT 2000",
        message="",
    )
    fake_service.protocol.validate_plan.return_value = MagicMock(
        success=True, message=""
    )
    fake_service.protocol.execute.return_value = MagicMock(
        data=[{"id": i} for i in range(2000)],
        fields=["id"],
        truncated=False,
    )
    monkeypatch.setattr(
        "apps.chat.tools.execute_sql.upsert_result_dataset", lambda **_k: None
    )
    monkeypatch.setattr(
        "apps.chat.tools.execute_sql.current_worker_identity",
        lambda: ("", None),
    )
    monkeypatch.setattr(
        "apps.chat.tools.execute_sql.apply_wiki_enum_labels",
        lambda **kwargs: (list(kwargs["rows"]), {}),
    )
    res = execute_sql_sandbox(
        fake_service,
        "SELECT * FROM t LIMIT 2000",
        limit=1000,
    )
    assert res["ok"] is True
    assert res["data"]["row_count"] == 2000
    assert res["data"]["truncated"] is True
    assert res["data"]["limit"] == 2000
    assert fake_service.protocol.execute.call_args.kwargs.get("max_rows") == 2000


def test_fold_clarification_flow_merges_tool_and_wait_into_one_card() -> None:
    from apps.conversation.process_timeline import fold_clarification_flow

    folded = fold_clarification_flow(
        [
            {
                "id": 1,
                "kind": "tool",
                "status": "completed",
                "tool": {"name": "request_clarification", "call_id": "c1"},
                "started_at": "2026-09-07T03:00:00",
                "finished_at": "2026-09-07T03:00:01",
                "summary_key": "chat.summary.tool_ok",
            },
            {
                "id": 2,
                "kind": "clarification",
                "status": "interrupted",
                "started_at": "2026-09-07T03:00:01",
                "finished_at": "2026-09-07T03:00:40",
                "summary_key": "chat.audit.step_interrupted",
                "meta": {
                    "interrupt_id": "intr-1",
                    "version": 1,
                    "clarification_card": {"questions": []},
                },
            },
            {
                "id": 3,
                "kind": "clarification",
                "status": "completed",
                "started_at": "2026-09-07T03:00:40",
                "finished_at": "2026-09-07T03:00:40",
                "summary_key": "chat.summary.tool_ok",
            },
            {"id": 4, "kind": "thought", "status": "completed"},
        ]
    )
    assert len(folded) == 2
    assert folded[0]["kind"] == "clarification"
    assert folded[0]["status"] == "completed"
    assert folded[0]["summary_key"] == "chat.summary.clarification_confirmed"
    assert folded[0]["started_at"] == "2026-09-07T03:00:00"
    assert folded[0]["meta"]["interrupt_id"] == "intr-1"
    assert folded[1]["kind"] == "thought"


def test_fold_clarification_flow_keeps_rounds_separate() -> None:
    from apps.conversation.process_timeline import fold_clarification_flow

    folded = fold_clarification_flow(
        [
            {
                "id": 1,
                "kind": "tool",
                "status": "completed",
                "tool": {"name": "request_clarification", "call_id": "c1"},
                "summary_key": "chat.summary.tool_ok",
            },
            {
                "id": 2,
                "kind": "clarification",
                "status": "completed",
                "summary_key": "chat.summary.clarification_confirmed",
                "meta": {
                    "interrupt_id": "intr-1",
                    "version": 1,
                    "clarification_card": {"questions": [{"question_id": "q1"}]},
                },
            },
            {"id": 3, "kind": "thought", "status": "completed"},
            {
                "id": 4,
                "kind": "tool",
                "status": "completed",
                "tool": {"name": "request_clarification", "call_id": "c2"},
                "summary_key": "chat.summary.tool_ok",
            },
            {
                "id": 5,
                "kind": "clarification",
                "status": "running",
                "summary_key": "chat.summary.clarification_waiting",
                "meta": {
                    "interrupt_id": "intr-2",
                    "version": 2,
                    "clarification_card": {"questions": [{"question_id": "q2"}]},
                },
            },
        ]
    )
    assert [item["kind"] for item in folded] == [
        "clarification",
        "thought",
        "clarification",
    ]
    assert folded[0]["meta"]["interrupt_id"] == "intr-1"
    assert folded[0]["summary_key"] == "chat.summary.clarification_confirmed"
    assert folded[2]["meta"]["interrupt_id"] == "intr-2"
    assert folded[2]["status"] == "running"
    assert folded[2]["summary_key"] == "chat.summary.clarification_waiting"


def test_fold_clarification_flow_leaves_orphan_tool_as_tool() -> None:
    from apps.conversation.process_timeline import fold_clarification_flow

    folded = fold_clarification_flow(
        [
            {"id": 1, "kind": "thought", "status": "completed"},
            {
                "id": 2,
                "kind": "tool",
                "status": "completed",
                "tool": {"name": "request_clarification", "call_id": "c2"},
                "summary_key": "chat.summary.tool_ok",
            },
        ]
    )
    assert len(folded) == 2
    assert folded[1]["kind"] == "tool"
    assert folded[1]["summary_key"] == "chat.summary.tool_ok"


def test_create_interrupt_keeps_worker_token_for_inline_span(monkeypatch) -> None:
    """Parked clarify must still emit process events under the same worker."""
    from datetime import datetime
    from types import SimpleNamespace
    from unittest.mock import MagicMock

    from apps.conversation import run_service
    from apps.conversation.models import ConversationInterrupt

    run = SimpleNamespace(
        run_id="run-1",
        status="running",
        worker_token="tok-alive",
        lease_expires_at=datetime.now(),
        active_interrupt_id=None,
        update_time=datetime.now(),
        chat_record_id=1,
        graph_key="chat",
        event_cursor=0,
    )
    session = MagicMock()
    session.refresh = MagicMock()
    monkeypatch.setattr(run_service, "_entity_one", lambda *_a, **_k: run)
    monkeypatch.setattr(run_service, "_assert_worker_ownership", lambda *_a, **_k: None)
    monkeypatch.setattr(run_service, "_assert_transition", lambda *_a, **_k: None)
    monkeypatch.setattr(
        run_service,
        "public_interrupt_payload",
        lambda payload: {
            "questions": [
                {
                    "question_id": "q1",
                    "question": "?",
                    "options": [{"option_id": "a", "label": "A", "meaning": "A"}],
                }
            ]
        },
    )
    monkeypatch.setattr(run_service, "_entity_one_or_none", lambda *_a, **_k: None)
    monkeypatch.setattr(run_service, "_append_run_event_locked", lambda *_a, **_k: 1)
    monkeypatch.setattr(run_service, "log_lifecycle", lambda *_a, **_k: None)

    pending = run_service.create_interrupt(
        session,
        run_id="run-1",
        payload={"questions": [{"question_id": "q1", "question": "?", "options": []}]},
    )
    assert isinstance(pending, ConversationInterrupt)
    assert pending.interrupt_id
    assert run.status == "awaiting_input"
    assert run.worker_token == "tok-alive"
    assert run.lease_expires_at is None
    assert run.active_interrupt_id == pending.interrupt_id
    session.commit.assert_called()
    session.add.assert_called()


def test_caliber_surface_splits_confirmed_from_assumptions() -> None:
    from apps.chat.caliber_surface import project_caliber_surface

    surface = project_caliber_surface(
        {
            "confirmed_calibers": {
                "q1": {
                    "question": "「认证方式是平台录入」应如何理解？",
                    "label": "按录入方式：平台录入",
                    "meaning": "按录入方式：平台录入",
                    "option_id": "q1_b",
                }
            },
            "assumptions": [
                {
                    "question": "默认时间口径",
                    "label": "按创建时间",
                    "meaning": "按创建时间",
                    "source": "declared",
                },
                {
                    "question": "旧澄清残留",
                    "label": "不应出现在假设",
                    "meaning": "不应出现在假设",
                    "source": "clarification",
                },
            ],
        }
    )
    confirmed = surface["confirmed_calibers"]
    assumptions = surface["assumptions"]
    assert len(confirmed) == 2
    assert confirmed[0]["question"].startswith("「认证方式是平台录入」")
    assert confirmed[0]["value"] == "按录入方式：平台录入"
    assert "q1_b" not in confirmed[0]["value"]
    assert any(item["value"] == "不应出现在假设" for item in confirmed)
    assert len(assumptions) == 1
    assert assumptions[0]["value"] == "按创建时间"
    assert assumptions[0]["source"] == "declared"


def test_assumptions_from_slots_are_human_readable() -> None:
    from apps.chat.graphs.nodes.agent_finalize import _assumptions_from_slots

    items = _assumptions_from_slots(
        {
            "confirmed_calibers": {
                "q1": {
                    "question": "「认证方式是平台录入」应如何理解？",
                    "label": "按录入方式：平台录入",
                    "meaning": "按录入方式：平台录入",
                    "option_id": "q1_b",
                }
            }
        }
    )
    assert len(items) == 1
    assert items[0]["question"].startswith("「认证方式是平台录入」")
    assert items[0]["value"] == "按录入方式：平台录入"
    assert "q1_b" not in items[0]["value"]
    assert items[0].get("field") is None


def test_bound_llm_io_keeps_small_payloads_and_caps_large() -> None:
    from apps.conversation.process_timeline import LLM_IO_MAX_CHARS, bound_llm_io

    small = [{"type": "human", "content": "hello"}]
    assert bound_llm_io(small) == small
    huge = "x" * (LLM_IO_MAX_CHARS + 10_000)
    capped = bound_llm_io({"prompt": huge})
    assert isinstance(capped, dict)
    assert capped.get("truncated") is True
    assert capped.get("truncation_reason") == "llm_io_max_chars"


def test_langgraph_preserves_open_tool_spans_on_nlq_state() -> None:
    from langgraph.graph import StateGraph

    from apps.chat.graphs.nodes.nlq.state import NlqState

    builder = StateGraph(NlqState)

    def n1(_state):
        return {"open_tool_spans": {"c1": 3700}}

    seen: dict = {}

    def n2(state):
        seen["open_tool_spans"] = state.get("open_tool_spans")
        return {}

    builder.add_node("n1", n1)
    builder.add_node("n2", n2)
    builder.set_entry_point("n1")
    builder.add_edge("n1", "n2")
    builder.set_finish_point("n2")
    builder.compile().invoke({})
    assert seen["open_tool_spans"] == {"c1": 3700}
