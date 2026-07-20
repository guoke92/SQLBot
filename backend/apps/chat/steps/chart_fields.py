"""Chart field extraction helpers (domain atom)."""

from __future__ import annotations

from typing import Any, List

from sqlmodel import Session

from apps.chat.curd.chat import format_chart_fields, get_chart_config


def get_fields_from_chart(llm_service: Any, session: Session) -> List[Any]:
    """Resolve axis/value field objects from the record's saved chart config."""
    chart_info = get_chart_config(session, llm_service.record.id)
    return format_chart_fields(chart_info)
