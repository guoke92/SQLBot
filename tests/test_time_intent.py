"""Unit tests for deterministic NLQ time semantics."""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.chat.time_intent import infer_time_intent  # noqa: E402


_NOW = datetime(2026, 7, 24, 12, 0, 0)


def test_no_time_language_does_not_add_default_filter() -> None:
    assert infer_time_intent("统计各部门任务数量", now=_NOW) is None


def test_all_time_disables_default_range() -> None:
    intent = infer_time_intent("查看所有时间的每月趋势", now=_NOW)
    assert intent is not None
    assert intent["scope"] == "all"
    assert intent["bucket"] == "month"


def test_default_trend_anchors_on_latest_data() -> None:
    intent = infer_time_intent("按月份查看任务趋势", now=_NOW)
    assert intent is not None
    assert intent["scope"] == "default"
    assert intent["anchor"] == "data_max"
    assert intent["lookback_months"] == 12
    assert intent["range_unit"] == "month"
    assert intent["bucket"] == "month"
    assert "start" not in intent


def test_explicit_year_bucket_is_not_treated_as_monthly_trend() -> None:
    intent = infer_time_intent("按年度查看销售趋势", now=_NOW)

    assert intent is not None
    assert intent["scope"] == "default"
    assert intent["bucket"] == "year"


def test_bucket_only_time_phrases_are_recognized() -> None:
    yearly = infer_time_intent("按年度统计销售额", now=_NOW)
    daily = infer_time_intent("按日统计订单量", now=_NOW)

    assert yearly is not None
    assert yearly["scope"] == "unspecified"
    assert yearly["bucket"] == "year"
    assert daily is not None
    assert daily["scope"] == "unspecified"
    assert daily["bucket"] == "day"


def test_yoy_keeps_two_years() -> None:
    intent = infer_time_intent("按月份查看同比趋势", now=_NOW)
    assert intent is not None
    assert intent["comparison"] == "yoy"
    assert intent["lookback_months"] == 24


def test_mom_keeps_previous_period() -> None:
    intent = infer_time_intent("最近每月环比", now=_NOW)
    assert intent is not None
    assert intent["comparison"] == "mom"
    assert intent["lookback_months"] == 13


def test_custom_rolling_months_preserve_requested_window() -> None:
    intent = infer_time_intent("查看最近 6 个月的趋势", now=_NOW)
    assert intent is not None
    assert intent["scope"] == "rolling"
    assert intent["lookback_months"] == 6


def test_rolling_range_does_not_imply_monthly_grouping() -> None:
    intent = infer_time_intent("统计最近 6 个月的总额", now=_NOW)
    assert intent is not None
    assert intent["scope"] == "rolling"
    assert intent["range_unit"] == "month"
    assert "bucket" not in intent


def test_rolling_year_range_does_not_imply_monthly_grouping() -> None:
    intent = infer_time_intent("统计近一年签收额", now=_NOW)
    assert intent is not None
    assert intent["scope"] == "rolling"
    assert intent["range_unit"] == "month"
    assert "bucket" not in intent


def test_custom_rolling_yoy_adds_previous_year_window() -> None:
    intent = infer_time_intent("查看近3个月同比", now=_NOW)
    assert intent is not None
    assert intent["lookback_months"] == 15


def test_explicit_year_is_not_replaced_by_default() -> None:
    intent = infer_time_intent("统计 2025 年每月数量", now=_NOW)
    assert intent is not None
    assert intent["scope"] == "explicit"
    assert intent["start"] == "2025-01-01"
    assert intent["end_exclusive"] == "2026-01-01"
    assert intent["range_unit"] == "year"
    assert intent["bucket"] == "month"


def test_year_filter_does_not_force_month_grouping() -> None:
    intent = infer_time_intent("统计 2025 年总额", now=_NOW)
    assert intent is not None
    assert intent["range_unit"] == "year"
    assert "bucket" not in intent


def test_explicit_year_yoy_includes_previous_year() -> None:
    intent = infer_time_intent("统计 2025 年同比", now=_NOW)
    assert intent is not None
    assert intent["start"] == "2024-01-01"
    assert intent["end_exclusive"] == "2026-01-01"


def test_explicit_month_is_calendar_bounded() -> None:
    intent = infer_time_intent("查看 2025年12月 数据", now=_NOW)
    assert intent is not None
    assert intent["start"] == "2025-12-01"
    assert intent["end_exclusive"] == "2026-01-01"


def test_explicit_month_mom_includes_previous_month() -> None:
    intent = infer_time_intent("查看 2025-01 环比", now=_NOW)
    assert intent is not None
    assert intent["start"] == "2024-12-01"
    assert intent["end_exclusive"] == "2025-02-01"


def test_explicit_date_is_not_widened_to_full_month() -> None:
    intent = infer_time_intent("查看 2025-01-31 的数据", now=_NOW)
    assert intent is not None
    assert intent["range_unit"] == "day"
    assert intent["start"] == "2025-01-31"
    assert intent["end_exclusive"] == "2025-02-01"
