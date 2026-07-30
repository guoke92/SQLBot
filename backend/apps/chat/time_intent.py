"""Structured time semantics for NLQ planning.

Time range semantics belong to the query plan context.
This module performs a deterministic, side-effect-free interpretation of the
most common time expressions without accessing the datasource.
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta
from typing import Literal, TypedDict

TimeScope = Literal["all", "explicit", "rolling", "default"]
TimeAnchor = Literal["current_time", "data_max"]
TimeComparison = Literal["none", "yoy", "mom"]
TimeGrain = Literal["day", "month", "year"]


class TimeIntent(TypedDict, total=False):
    """Serializable time contract consumed by prompt rendering and probes."""

    scope: TimeScope
    anchor: TimeAnchor
    comparison: TimeComparison
    grain: TimeGrain
    start: str
    end_exclusive: str
    lookback_months: int
    source: str
    confidence: float


_YEAR_RE = re.compile(r"(?<!\d)(20\d{2})(?:年)?(?!\d)")
_YEAR_MONTH_RE = re.compile(r"(?<!\d)(20\d{2})(?:年|[-/])(\d{1,2})(?:月)?(?!\d)")
_DATE_RE = re.compile(r"(?<!\d)(20\d{2})[-/](\d{1,2})[-/](\d{1,2})(?!\d)")
_RECENT_MONTHS_RE = re.compile(r"(?:近|最近|过去)\s*(\d{1,2})\s*个?月")
_ALL_TIME_CUES = ("所有时间", "全部时间", "不限时间", "全量数据", "全部数据")
_TIME_CUES = (
    "今年",
    "本年",
    "本月",
    "近一年",
    "近12个月",
    "最近",
    "月份",
    "每月",
    "趋势",
    "同比",
    "环比",
)


def _month_end_exclusive(now: datetime) -> str:
    year = now.year + (1 if now.month == 12 else 0)
    month = 1 if now.month == 12 else now.month + 1
    return f"{year:04d}-{month:02d}-01"


def _next_month(year: int, month: int) -> tuple[int, int]:
    return (year + 1, 1) if month == 12 else (year, month + 1)


def infer_time_intent(
    question: str,
    *,
    now: datetime | None = None,
) -> TimeIntent | None:
    """Infer deterministic time semantics without touching a datasource.

    ``None`` means the question has no time intent and no default time filter
    should be added. A returned ``default`` scope is deliberately anchored on
    the latest available data rather than wall-clock time, preventing stale
    warehouses from being filtered to an empty current-year window.
    """
    text = (question or "").strip()
    if not text:
        return None
    current = now or datetime.now()

    if any(cue in text for cue in _ALL_TIME_CUES):
        return {
            "scope": "all",
            "comparison": "none",
            "grain": "month",
            "source": "user",
            "confidence": 1.0,
        }

    comparison: TimeComparison = "none"
    if "同比" in text:
        comparison = "yoy"
    elif "环比" in text:
        comparison = "mom"

    date_match = _DATE_RE.search(text)
    if date_match:
        try:
            target = datetime(
                int(date_match.group(1)),
                int(date_match.group(2)),
                int(date_match.group(3)),
            )
        except ValueError:
            target = None
        if target is not None:
            if comparison == "yoy":
                try:
                    start_date = target.replace(year=target.year - 1)
                except ValueError:
                    start_date = target.replace(year=target.year - 1, day=28)
            elif comparison == "mom":
                start_date = target - timedelta(days=1)
            else:
                start_date = target
            return {
                "scope": "explicit",
                "anchor": "current_time",
                "comparison": comparison,
                "grain": "day",
                "start": start_date.strftime("%Y-%m-%d"),
                "end_exclusive": (target + timedelta(days=1)).strftime("%Y-%m-%d"),
                "source": "user",
                "confidence": 1.0,
            }

    year_month_match = _YEAR_MONTH_RE.search(text)
    if year_month_match:
        year = int(year_month_match.group(1))
        month = int(year_month_match.group(2))
        if 1 <= month <= 12:
            if comparison == "yoy":
                start_year, start_month = year - 1, month
            elif comparison == "mom":
                start_month = month - 1 or 12
                start_year = year - (1 if month == 1 else 0)
            else:
                start_year, start_month = year, month
            end_year, end_month = _next_month(year, month)
            return {
                "scope": "explicit",
                "anchor": "current_time",
                "comparison": comparison,
                "grain": "month",
                "start": f"{start_year:04d}-{start_month:02d}-01",
                "end_exclusive": f"{end_year:04d}-{end_month:02d}-01",
                "source": "user",
                "confidence": 1.0,
            }

    year_match = _YEAR_RE.search(text)
    if year_match:
        year = int(year_match.group(1))
        start_year = year - 1 if comparison == "yoy" else year
        return {
            "scope": "explicit",
            "anchor": "current_time",
            "comparison": comparison,
            "grain": "month",
            "start": f"{start_year:04d}-01-01",
            "end_exclusive": f"{year + 1:04d}-01-01",
            "source": "user",
            "confidence": 1.0,
        }

    if "今年" in text or "本年" in text:
        start_year = current.year - 1 if comparison == "yoy" else current.year
        return {
            "scope": "explicit",
            "anchor": "current_time",
            "comparison": comparison,
            "grain": "month",
            "start": f"{start_year:04d}-01-01",
            "end_exclusive": f"{current.year + 1:04d}-01-01",
            "source": "user",
            "confidence": 1.0,
        }

    if "本月" in text:
        if comparison == "yoy":
            start = f"{current.year - 1:04d}-{current.month:02d}-01"
        elif comparison == "mom":
            previous_month = current.month - 1 or 12
            previous_year = current.year - (1 if current.month == 1 else 0)
            start = f"{previous_year:04d}-{previous_month:02d}-01"
        else:
            start = f"{current.year:04d}-{current.month:02d}-01"
        return {
            "scope": "explicit",
            "anchor": "current_time",
            "comparison": comparison,
            "grain": "month",
            "start": start,
            "end_exclusive": _month_end_exclusive(current),
            "source": "user",
            "confidence": 1.0,
        }

    recent_months_match = _RECENT_MONTHS_RE.search(text)
    requested_lookback: int | None = None
    if recent_months_match:
        months = int(recent_months_match.group(1))
        if 1 <= months <= 120:
            requested_lookback = months
    elif "近半年" in text or "最近半年" in text or "过去半年" in text:
        requested_lookback = 6
    elif "过去一年" in text:
        requested_lookback = 12

    if requested_lookback is None and not any(cue in text for cue in _TIME_CUES):
        return None

    # A trend without an explicit wall-clock range should follow the data,
    # otherwise a stale warehouse can be filtered to an empty current window.
    visible_months = requested_lookback or 12
    lookback = visible_months
    if comparison == "yoy":
        lookback += 12
    elif comparison == "mom":
        lookback += 1
    scope: TimeScope = (
        "rolling"
        if requested_lookback is not None
        or any(cue in text for cue in ("近一年", "近12个月", "最近"))
        else "default"
    )
    return {
        "scope": scope,
        "anchor": "data_max",
        "comparison": comparison,
        "grain": "month",
        "lookback_months": lookback,
        "source": "user" if scope == "rolling" else "default_policy",
        "confidence": 0.9 if scope == "rolling" else 0.7,
    }
