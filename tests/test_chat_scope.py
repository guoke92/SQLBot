"""Chat-scoped caching: datasource connection + access scope reuse across turns."""

from __future__ import annotations

import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

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
