"""Chat-scoped caching: datasource connection + access scope reuse across turns."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.chat.graphs.nodes import nlq  # noqa: E402
from apps.chat.planning import _apply_display_defaults  # noqa: E402
from apps.chat.steps import chat_scope as cs  # noqa: E402
from apps.datasource.access import AccessScope  # noqa: E402

# ── 缓存单元 ──────────────────────────────────────────────────────────────────


def test_connection_cache_ttl_and_invalidate(monkeypatch) -> None:
    cs.clear_chat_scope_cache()
    now = [1000.0]
    monkeypatch.setattr(cs.time, "monotonic", lambda: now[0])

    assert cs.connection_fresh(8) is False
    cs.remember_connection(8)
    assert cs.connection_fresh(8) is True

    now[0] += cs.CONNECTION_TTL_SEC + 1
    assert cs.connection_fresh(8) is False  # TTL 过期

    cs.remember_connection(8)
    cs.invalidate_connection(8)
    assert cs.connection_fresh(8) is False  # 失效即剔除


def test_scope_cache_distinguishes_none_from_missing(monkeypatch) -> None:
    cs.clear_chat_scope_cache()
    now = [1000.0]
    monkeypatch.setattr(cs.time, "monotonic", lambda: now[0])

    assert cs.is_missing(cs.cached_access_scope(1, 8, 5)) is True

    cs.remember_access_scope(1, 8, 5, None)  # 外部/无范围也是有效缓存值
    cached = cs.cached_access_scope(1, 8, 5)
    assert cs.is_missing(cached) is False
    assert cached is None

    scope = AccessScope(resource_names=("d_task",))
    cs.remember_access_scope(1, 8, 5, scope)
    got = cs.cached_access_scope(1, 8, 5)
    assert isinstance(got, AccessScope)
    assert got.resource_names == ("d_task",)

    # 不同 user 不共享
    assert cs.is_missing(cs.cached_access_scope(1, 8, 6)) is True

    now[0] += cs.SCOPE_TTL_SEC + 1
    assert cs.is_missing(cs.cached_access_scope(1, 8, 5)) is True


# ── 节点级：resolve_access_scope 缓存复用 ─────────────────────────────────────


class _FakeSession:
    def __init__(self):
        self.calls: list[str] = []

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def _wire_scope_node(monkeypatch, resolved_scope):
    cs.clear_chat_scope_cache()
    service = SimpleNamespace(
        ds=SimpleNamespace(id=8),
        current_user=SimpleNamespace(id=5),
        record=SimpleNamespace(id=1),
    )
    attached: dict[str, Any] = {}
    resolve_calls: list[int] = []

    monkeypatch.setattr(nlq, "_llm_service", lambda state: service)
    monkeypatch.setattr(
        nlq,
        "resolve_access_scope",
        lambda *a, **k: (resolve_calls.append(1), resolved_scope)[1],
    )
    monkeypatch.setattr(nlq, "attach_runtime", lambda run_id, **kw: attached.update(kw))
    monkeypatch.setattr(nlq, "_ds_scope", lambda svc: (1, 8))
    monkeypatch.setattr(nlq, "session_scope", _FakeSession)
    return service, resolve_calls, attached


def test_access_scope_resolved_once_then_reused(monkeypatch) -> None:
    scope = AccessScope(resource_names=("d_task", "d_project"))
    _service, resolve_calls, attached = _wire_scope_node(monkeypatch, scope)
    state = {"run_id": "r1", "planning_decision": "pending"}

    first = nlq.resolve_access_scope_node(state)
    assert first.get("error") is None
    assert len(resolve_calls) == 1
    assert attached["access_scope"] is scope

    second = nlq.resolve_access_scope_node({**state, "run_id": "r2"})
    assert second.get("error") is None
    assert len(resolve_calls) == 1  # 缓存命中, 不再解析
    assert attached["access_scope"] is scope  # 每个运行仍正确绑定


# ── 节点级：ensure_datasource 连接缓存 ────────────────────────────────────────


def _wire_datasource_node(monkeypatch, *, connected=True):
    cs.clear_chat_scope_cache()
    checks: list[int] = []
    service = SimpleNamespace(
        ds=SimpleNamespace(id=8, name="AIO", type="mysql"),
        record=SimpleNamespace(id=1),
        protocol=SimpleNamespace(
            check_connection=lambda *, ds: (checks.append(1), connected)[1],
        ),
    )
    monkeypatch.setattr(nlq, "_llm_service", lambda state: service)
    monkeypatch.setattr(nlq, "validate_history_ds", lambda *a, **k: None)
    monkeypatch.setattr(nlq.StreamSink, "from_state", classmethod(lambda c, s: None))
    monkeypatch.setattr(nlq, "session_scope", _FakeSession)
    return service, checks


def test_connection_checked_once_then_cached(monkeypatch) -> None:
    service, checks = _wire_datasource_node(monkeypatch)

    first = nlq.ensure_datasource_node({"run_id": "r1"})
    assert first.get("error") is None
    assert len(checks) == 1

    second = nlq.ensure_datasource_node({"run_id": "r2"})
    assert second.get("error") is None
    assert len(checks) == 1  # TTL 内不再打目标库

    assert cs.connection_fresh(8) is True


def test_connection_failure_not_cached(monkeypatch) -> None:
    service, checks = _wire_datasource_node(monkeypatch, connected=False)

    result = nlq.ensure_datasource_node({"run_id": "r1"})
    assert result.get("error") is not None
    assert cs.connection_fresh(8) is False  # 失败不进缓存


def test_execution_connection_failure_invalidates_cache() -> None:
    # 执行期连接失败反哺缓存：由 execute_queries_node 的失效分支保证
    # （kind == "connection" → invalidate_connection）。此处验证缓存语义闭环。
    cs.clear_chat_scope_cache()
    cs.remember_connection(8)
    assert cs.connection_fresh(8) is True
    cs.invalidate_connection(8)  # 执行失败路径调用
    assert cs.connection_fresh(8) is False


# ── 数据集标题：description 必须成为 tab 标题 ────────────────────────────────


def test_display_defaults_use_brief_as_title() -> None:
    plans = [
        {"brief": "问卷星白名单企业完整明细"},
        {"brief": "调研答案完整明细"},
    ]
    _apply_display_defaults(plans, "我想查看问卷调察的完整详细信息")
    assert plans[0]["presentation_title"] == "问卷星白名单企业完整明细（1）"
    assert plans[1]["presentation_title"] == "调研答案完整明细（2）"
    # 回退：无 brief 时才用问题原文
    fallback = [{"brief": ""}]
    _apply_display_defaults(fallback, "用户问题原文")
    assert fallback[0]["presentation_title"] == "用户问题原文"


def test_plans_from_ready_passes_description_as_brief(monkeypatch) -> None:
    from apps.chat.planning import BatchParseResult
    from apps.chat.semantic_planning import QueryDescription, Ready
    from apps.chat.steps import query_agent as qa

    captured: list[dict] = []

    def fake_parse(payload, _llm_service, **_kwargs):
        captured.append(dict(payload))
        # 模拟真实契约：解析层应用显示默认值（brief → 标题 + 序号）
        parsed = [
            {
                "sql": payload.get("sql"),
                "payload": {"sql": payload.get("sql")},
                "brief": payload.get("brief"),
            }
        ]
        _apply_display_defaults(parsed, "用户问题")
        return BatchParseResult(plans=parsed, plan_validated=True)

    monkeypatch.setattr(qa, "parse_query_generation", fake_parse)
    service = SimpleNamespace(
        chat_question=SimpleNamespace(generation_question="用户问题"),
        table_name_list=["t"],
        protocol=SimpleNamespace(
            format_statement_for_display=lambda plan: plan.statement
        ),
    )
    decision = Ready(
        queries=[
            QueryDescription(description="白名单明细", sql="SELECT 1"),
            QueryDescription(description="答题明细", sql="SELECT 2"),
        ]
    )

    plans = qa._plans_from_ready(
        decision, service, schema_fingerprint="fp", max_batch_size=4
    )

    assert [p["brief"] for p in captured] == ["白名单明细", "答题明细"]
    # 标题来自 description, 多计划带序号; 不再回退问题原文
    assert plans[0]["presentation_title"] == "白名单明细（1）"
    assert plans[1]["presentation_title"] == "答题明细（2）"


# ── 执行详情标签完整性 ────────────────────────────────────────────────────────


def test_summarize_label_present_in_all_locales() -> None:
    for loc in ("zh-CN", "en", "zh-TW", "ko-KR"):
        data = json.loads((_ROOT / "frontend/src/i18n" / f"{loc}.json").read_text())
        assert data["chat"]["log"].get("SUMMARIZE"), f"{loc} missing chat.log.SUMMARIZE"


# ── 标题技术注记剥离 ──────────────────────────────────────────────────────────


def test_strip_technical_annotations() -> None:
    from apps.chat.planning import _strip_technical_annotations as strip

    # 修复器式技术注记 → 剥离
    assert (
        strip("按系统维度统计研发二部每月task数、story数（MySQL兼容写法，不使用CTE）")
        == "按系统维度统计研发二部每月task数、story数"
    )
    assert strip("按系统维度统计研发二部每月task数、story数（修复CTE为子查询）") == (
        "按系统维度统计研发二部每月task数、story数"
    )
    # 多层尾部技术括号 → 全部剥离
    assert strip("统计task数（改写为子查询）（兼容5.x版本）") == "统计task数"
    # 半角括号同样处理
    assert strip("统计task数(no CTE)") == "统计task数"
    # 业务括号 → 保留
    assert (
        strip(
            "按系统维度统计研发二部负责人（task/story被分配人机构为研发二部）近一年每月数量"
        )
        == "按系统维度统计研发二部负责人（task/story被分配人机构为研发二部）近一年每月数量"
    )
    # 剥离后剩余文本有效 → 保留剩余部分
    assert strip("统计（兼容写法）") == "统计"
    # 全剥离后为空 → 回退原标题（不留空标题）
    assert strip("（兼容写法）") == "（兼容写法）"


def test_batch_defaults_strip_annotations_in_titles() -> None:
    from apps.chat.planning import apply_batch_display_defaults

    plans = [
        {
            "description": "按系统维度统计研发二部每月task数、story数（MySQL兼容写法，不使用CTE）",
        }
    ]
    apply_batch_display_defaults(plans, "用户问题")
    assert plans[0]["presentation_title"] == "按系统维度统计研发二部每月task数、story数"
