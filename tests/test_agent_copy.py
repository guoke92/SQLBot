"""Compact unified-agent final copy (openers, sample tables, truncation note)."""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.chat.agent_copy import (  # noqa: E402
    compact_agent_final_text,
    truncated_display_note,
    truncation_from_delivery_steps,
    truncation_from_tool_steps,
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


def test_truncated_display_note_fallback() -> None:
    assert truncated_display_note(1000) == "仅展示前 1000 条。"
    assert truncated_display_note(None) == ""


def test_truncation_from_tool_steps_skips_probe() -> None:
    truncated, limit = truncation_from_tool_steps(
        [
            {
                "ok": True,
                "result": {
                    "data": {
                        "sql": "SELECT 1",
                        "truncated": True,
                        "limit": 50,
                        "required": False,
                    }
                },
            },
            {
                "ok": True,
                "result": {
                    "data": {
                        "sql": "SELECT * FROM t LIMIT 1000",
                        "truncated": True,
                        "limit": 1000,
                        "required": True,
                    }
                },
            },
        ]
    )
    assert truncated is True
    assert limit == 1000


def test_truncation_from_delivery_steps() -> None:
    truncated, limit = truncation_from_delivery_steps(
        [
            {"required": False, "data": {"truncated": True, "limit": 10, "sql": "x"}},
            {"required": True, "data": {"truncated": True, "limit": 1000, "sql": "y"}},
        ]
    )
    assert truncated is True
    assert limit == 1000
