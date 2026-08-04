"""Pure adapters for result datasets returned to conversation clients."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from common.utils.data_format import DataFormat


def format_json_data(origin_data: dict[str, Any]) -> dict[str, Any]:
    """Normalize row values while preserving dataset metadata."""
    result = dict(origin_data)
    result["fields"] = origin_data.get("fields") or []
    result["fields_info"] = origin_data.get("fields_info") or None
    data = format_json_list_data(origin_data.get("data") or [])
    result["data"] = data
    result["row_count"] = (
        origin_data.get("row_count")
        if origin_data.get("row_count") is not None
        else len(data)
    )
    result["truncated"] = bool(origin_data.get("truncated"))
    if origin_data.get("truncation_reason") is not None:
        result["truncation_reason"] = origin_data["truncation_reason"]
    if origin_data.get("limit") is not None:
        result["limit"] = origin_data["limit"]
    return result


def format_json_list_data(origin_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Normalize database row values for lossless JSON transport."""
    data: list[dict[str, Any]] = []
    for source_row in origin_data:
        row: dict[str, Any] = {}
        for key, raw_value in source_row.items():
            value = raw_value
            if isinstance(value, int) and len(str(abs(value))) > 15:
                value = str(value)
            elif isinstance(value, float):
                decimal_str = str(Decimal(str(value))).rstrip("0").rstrip(".")
                if len(decimal_str) > 15:
                    value = str(value)
            row[key] = value
        data.append(DataFormat.normalize_qualified_sql_column_keys(row))
    return data
