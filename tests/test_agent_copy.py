"""Compact unified-agent final copy (openers, sample tables, truncation note)."""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from langchain_core.messages import AIMessage  # noqa: E402

from apps.chat.agent.workspace import SqlWorkspace  # noqa: E402
from apps.chat.agent_copy import (  # noqa: E402
    compact_agent_final_text,
    recover_analysis_report,
    truncated_display_note,
)

_CHAT_217_TEXT = """查询已完成，企业清单已生成。以下是本次查询的说明与结果概要：

口径：认证方式为邀请认证-内管录入（identify_style = INVITE_AGW），建档时间早于 2025-06-01。

本次查询返回 1000 条企业建档记录（已按建档时间倒序展示在结果集中），说明截至当前采样符合条件的记录超过 1000 条，结果集有截断。
如需完整清单（全部行数）请告诉我。

## 样本示例

| 企业名称 | 认证方式 | 客户状态 |
| --- | --- | --- |
| 某某科技 | INVITE_AGW | EFFECT |

> 提示：结果已挂在下方表格。

**几点说明：**
1. 未按客户状态过滤。
2. 数据类型均为主数据。
"""


def test_compact_agent_final_text_drops_opener_and_sample_table() -> None:
    out = compact_agent_final_text(_CHAT_217_TEXT, truncated=True, limit=1000)
    assert "查询已完成" not in out
    assert "企业清单已生成" not in out
    assert "结果概要" not in out
    assert "样本示例" not in out
    assert "几点说明" not in out
    assert "完整清单" not in out
    assert "结果集有截断" not in out
    assert "|" not in out
    assert "INVITE_AGW" in out
    assert "仅展示前 1000 条。" in out


def test_compact_agent_final_text_is_idempotent() -> None:
    once = compact_agent_final_text(_CHAT_217_TEXT, truncated=True, limit=1000)
    twice = compact_agent_final_text(once, truncated=True, limit=1000)
    assert twice == once


def test_compact_keeps_analyze_evidence_tables() -> None:
    report = """### 核心发现
开通率 12.4%。

### 证据

| 渠道 | 开通率 |
| --- | --- |
| A | 18% |
| B | 9% |
"""
    kept = compact_agent_final_text(report, keep_tables=True)
    assert "核心发现" not in kept
    assert "开通率 12.4%。" in kept
    assert "| 渠道 | 开通率 |" in kept
    assert "12.4%" in kept
    stripped = compact_agent_final_text(report, keep_tables=False)
    assert "|" not in stripped
    assert "12.4%" in stripped
    assert "核心发现" in stripped


def test_recover_analysis_report_after_empty_stop() -> None:
    report = "## 核心发现\n1956 家企业存在空缺。\n\n## 证据\n\n| 角色 | 企业 |\n| --- | --- |\n| 核心企业 | 1292 |\n"
    kept = recover_analysis_report(
        [AIMessage(content=report), AIMessage(content="")],
        "",
    )
    assert kept == report.strip()
    compacted = compact_agent_final_text(
        kept, truncated=True, limit=1000, keep_tables=True
    )
    assert "1956 家企业存在空缺。" in compacted
    assert "核心发现" not in compacted
    assert "| 核心企业 | 1292 |" in compacted
    assert "仅展示前 1000 条。" not in compacted
    assert compact_agent_final_text(kept, keep_tables=True) == compacted


def test_analyze_report_skips_query_footnote_even_without_a_window_mention() -> None:
    report = """### 核心发现
4115 家企业完全没有运营人。清单为 4,232 家中的前 1,000 行。
"""
    compacted = compact_agent_final_text(
        report, truncated=True, limit=1000, keep_tables=True
    )
    assert "前 1,000 行" in compacted
    assert "仅展示前 1000 条。" not in compacted
    query = compact_agent_final_text(
        "已按确认口径筛选。", truncated=True, limit=1000, keep_tables=False
    )
    assert query.endswith("仅展示前 1000 条。")


def test_truncated_display_note_fallback() -> None:
    assert truncated_display_note(1000) == "仅展示前 1000 条。"
    assert truncated_display_note(None) == ""


def test_truncation_from_delivered_revision() -> None:
    workspace = SqlWorkspace()
    probe = workspace.add_revision("SELECT 1", status="executed")
    workspace.mark_executed(
        probe.rev, purpose="probe", truncated=True, display_limit=50
    )
    assert workspace.truncation() == (False, None)
    delivery = workspace.add_revision("SELECT * FROM t LIMIT 1000", status="executed")
    workspace.mark_executed(
        delivery.rev, purpose="delivery", truncated=True, display_limit=1000
    )
    assert workspace.truncation() == (True, 1000)
