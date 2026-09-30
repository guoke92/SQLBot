"""End-to-End tests for Unified Tool-Agent Runtime."""

from contextlib import contextmanager
from types import SimpleNamespace

from langchain_core.messages import AIMessage

from apps.chat.agent.delivery import finalize_agent_turn_node
from apps.chat.agent.loop import (
    route_after_agent_loop,
    route_after_tools_execution,
)
from apps.chat.agent.workspace import SqlWorkspace
from apps.chat.memory_slots import MemorySlots
from apps.chat.task.agent_prompt import build_agent_system_prompt
from apps.chat.tools.contract import Signals, ToolOutcome
from apps.chat.tools.patch_sql import patch_and_compile_sql


def _result_ds(
    *,
    dataset_id: str,
    sql: str,
    fields: list[str],
    rows: list[dict],
    row_count: int,
    title: str = "",
    required: bool = True,
    truncated: bool = False,
    limit: int | None = None,
):
    return SimpleNamespace(
        dataset_id=dataset_id,
        status="succeeded",
        required=required,
        fields=fields,
        rows=rows,
        row_count=row_count,
        truncated=truncated,
        schema_snapshot={
            "sql": sql,
            "result_title": title,
            "chart_type": "table",
            "limit": limit,
        },
    )


def _workspace(*items: dict) -> dict:
    ws = SqlWorkspace()
    for item in items:
        rev = ws.add_revision(
            item["sql"],
            origin="model",
            status="executed",
            dataset_id=item.get("dataset_id"),
            result_title=item.get("title", ""),
        )
        ws.mark_executed(
            rev.rev,
            dataset_id=item.get("dataset_id"),
            purpose=item.get("purpose", "delivery"),
            result_title=item.get("title", ""),
            truncated=bool(item.get("truncated")),
            display_limit=item.get("limit") or item.get("display_limit"),
        )
    return ws.model_dump(mode="json")


def test_memory_slots_retention_and_baseline_extraction():
    """Session slots persist calibers; SQL truth lives on workspace revs."""
    slots = MemorySlots(
        confirmed_calibers={"amount": "actual_amount", "date": "pay_time"},
        excluded_filters=[{"field": "status", "op": "NOT IN", "value": ["CANCELLED"]}],
        current_rev="r1",
        active_dataset_outline={"fields": ["dept", "sum"], "row_count": 100, "rev": "r1"},
    )
    prompt = build_agent_system_prompt(memory_slots=slots.model_dump())
    assert "<memory_slots>" not in prompt
    assert "<change_baseline>" not in prompt
    assert "硬预算" not in prompt
    assert "current_rev: r1" in prompt


def test_incremental_patch_preserves_confirmed_filters():
    """验证场景3：增量修改在保留已确认口径（如排除项）的同时安全扩展维度."""
    base_sql = "SELECT dept, sum(actual_amount) AS total FROM sales WHERE status NOT IN ('CANCELLED') GROUP BY dept"
    res = patch_and_compile_sql(base_sql, "add_dimension", {"fields": ["month"]})
    assert res["ok"] is True
    patched = res["data"]["sql"].lower()
    assert "month" in patched
    assert "cancelled" in patched and (
        "status not in" in patched or "not status in" in patched
    )
    assert "group by dept, month" in patched


def test_agent_route_after_agent_loop_with_tool_call():
    """验证场景4：Agent 大脑调度工具或完成输出的分流路由."""
    ai_msg_with_call = AIMessage(
        content="I will patch the query to add department.",
        tool_calls=[{"name": "patch_and_compile_sql", "args": {}, "id": "call_1"}],
    )
    state_calling = {"messages": [ai_msg_with_call]}
    assert route_after_agent_loop(state_calling) == "execute_tools"

    ai_msg_final = AIMessage(content="Here is the final result: 850 orders.")
    state_final = {"messages": [ai_msg_final]}
    assert route_after_agent_loop(state_final) == "finalize_turn"


def test_route_after_tools_clarification_interrupt():
    """质疑/歧义时触发澄清卡片中断路由."""
    tool_steps_normal = [
        {
            "name": "patch_and_compile_sql",
            "ok": True,
            "outcome": ToolOutcome(
                ok=True, summary="ok", payload={}, signals=Signals()
            ).model_dump(mode="json"),
        }
    ]
    assert (
        route_after_tools_execution({"tool_steps": tool_steps_normal}) == "agent_loop"
    )

    tool_steps_clarify = [
        {
            "name": "request_clarification",
            "ok": True,
            "outcome": ToolOutcome(
                ok=True,
                summary="card",
                payload={},
                signals=Signals(interrupt=True),
            ).model_dump(mode="json"),
        }
    ]
    assert (
        route_after_tools_execution({"tool_steps": tool_steps_clarify})
        == "await_clarification"
    )

    tool_steps_compare = [
        {
            "ok": True,
            "name": "compare_results",
            "outcome": ToolOutcome(
                ok=True,
                summary="diff",
                payload={"row_count_a": 3, "row_count_b": 5},
                signals=Signals(),
            ).model_dump(mode="json"),
        }
    ]
    assert (
        route_after_tools_execution({"tool_steps": tool_steps_compare}) == "agent_loop"
    )


def _patch_finalize(monkeypatch, datasets):
    @contextmanager
    def _scope():
        yield object()

    monkeypatch.setattr("apps.chat.agent.delivery.session_scope", _scope)
    monkeypatch.setattr(
        "apps.chat.agent.delivery.load_result_datasets",
        lambda *_a, **_k: datasets,
    )
    monkeypatch.setattr(
        "apps.chat.agent.delivery.finalize_run",
        lambda *_a, **_k: None,
    )


def test_finalize_agent_turn_publishes_delivery_datasets_only(monkeypatch):
    """Probe SQL stays out of the answer; multiple delivery datasets are kept."""
    deliveries = [
        _result_ds(
            dataset_id="ds1",
            sql="SELECT code FROM t WHERE identify_style = 'INVITE_AGW'",
            fields=["code"],
            rows=[{"code": "c1"}],
            row_count=1,
            title="企业清单",
        ),
        _result_ds(
            dataset_id="ds2",
            sql="SELECT city, COUNT(*) FROM t GROUP BY city",
            fields=["city", "cnt"],
            rows=[{"city": "SZ", "cnt": 3}],
            row_count=1,
            title="城市分布",
        ),
    ]
    _patch_finalize(monkeypatch, deliveries)
    state = {
        "run_id": "test_run_123",
        "record_id": 999,
        "final_text": "以下为企业清单。",
        "sql_workspace": _workspace(
            {
                "sql": "SELECT identify_style, COUNT(*) FROM t GROUP BY 1",
                "dataset_id": "probe",
                "purpose": "probe",
            },
            {
                "sql": "SELECT code FROM t WHERE identify_style = 'INVITE_AGW'",
                "dataset_id": "ds1",
                "title": "企业清单",
            },
            {
                "sql": "SELECT city, COUNT(*) FROM t GROUP BY city",
                "dataset_id": "ds2",
                "title": "城市分布",
            },
        ),
    }
    out = finalize_agent_turn_node(state)
    ans = out["terminal_answer"]
    assert ans["status"] == "succeeded"
    assert [item["title"] for item in ans["datasets"]] == ["企业清单", "城市分布"]
    assert "COUNT(*) FROM t GROUP BY 1" not in ans["datasets"][0]["sql"]
    assert ans["content"].startswith("以下为企业清单")


def test_finalize_compacts_truncated_copy(monkeypatch):
    _patch_finalize(
        monkeypatch,
        [
            _result_ds(
                dataset_id="ds1",
                sql="SELECT code FROM t LIMIT 1000",
                fields=["code"],
                rows=[{"code": "c1"}],
                row_count=1000,
                title="企业清单",
                truncated=True,
                limit=1000,
            )
        ],
    )
    state = {
        "run_id": "test_run_trunc",
        "record_id": 1001,
        "final_text": (
            "查询已完成，企业清单已生成。以下是本次查询的说明与结果概要：\n\n"
            "口径：认证方式为邀请认证-内管录入。\n\n"
            "本次查询返回 1000 条，符合条件的记录超过 1000 条，结果集有截断。\n"
        ),
        "sql_workspace": _workspace(
            {
                "sql": "SELECT code FROM t LIMIT 1000",
                "dataset_id": "ds1",
                "title": "企业清单",
                "truncated": True,
                "limit": 1000,
            }
        ),
    }
    out = finalize_agent_turn_node(state)
    content = out["terminal_answer"]["content"]
    assert "查询已完成" not in content
    assert "结果概要" not in content
    assert "结果集有截断" not in content
    assert "邀请认证-内管录入" in content
    assert "仅展示前 1000 条。" in content


def test_finalize_empty_stop_is_friendly_failure(monkeypatch):
    _patch_finalize(monkeypatch, [])
    monkeypatch.setattr(
        "apps.chat.graphs.turn_failure.persist_query_terminal_failure",
        lambda payload, **_k: payload.get("outcome")
        or {"status": "failed", "failures": []},
    )
    out = finalize_agent_turn_node(
        {
            "run_id": "empty_run",
            "turn_route": {"task_kind": "query"},
            "tool_steps": [],
        }
    )
    assert out["outcome"]["status"] == "failed"
    assert "error" in out
    assert "换个问法" in out["public_error"] or "synced" in out["public_error"]


def test_query_without_sql_routes_to_fail():
    assert (
        route_after_agent_loop(
            {
                "error": "这次没能查出结果。请换个问法试试，或确认数据源表结构已同步。",
                "messages": [],
            }
        )
        == "fail"
    )


def test_route_after_agent_loop_salvages_sql_on_llm_error():
    state = {
        "error": "RateLimitError 429 TPM",
        "messages": [],
        "sql_workspace": _workspace(
            {
                "sql": "SELECT code FROM t LIMIT 1000",
                "dataset_id": "ds1",
            }
        ),
    }
    assert route_after_agent_loop(state) == "finalize_turn"


def test_finalize_keeps_datasets_when_summary_incomplete(monkeypatch):
    _patch_finalize(
        monkeypatch,
        [
            _result_ds(
                dataset_id="ds1",
                sql="SELECT code FROM t LIMIT 1000",
                fields=["code"],
                rows=[{"code": "c1"}],
                row_count=1000,
                title="企业清单",
                truncated=True,
                limit=1000,
            )
        ],
    )
    state = {
        "run_id": "salvage_run",
        "record_id": 2002,
        "final_text": "",
        "error": "RateLimitError 429 TPM",
        "analysis_incomplete": True,
        "sql_workspace": _workspace(
            {
                "sql": "SELECT code FROM t LIMIT 1000",
                "dataset_id": "ds1",
                "title": "企业清单",
            }
        ),
    }
    out = finalize_agent_turn_node(state)
    assert out.get("error") is None
    ans = out["terminal_answer"]
    assert ans["status"] == "degraded"
    assert [item["title"] for item in ans["datasets"]] == ["企业清单"]
    assert ans["datasets"][0]["sql"]
