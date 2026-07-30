"""Chart result parsing helpers."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import orjson

from common.error import SingleMessageError
from common.utils.data_format import DataFormat
from common.utils.json_utils import extract_nested_json


def parse_chart(
    res: str,
    fields: Optional[List[Any]] = None,
) -> Dict[str, Any]:
    """Parse and normalize chart output without writing ChatRecord state."""
    json_str = extract_nested_json(res)
    if json_str is None:
        raise SingleMessageError(
            orjson.dumps(
                {
                    "message": "Cannot parse chart config from answer",
                    "traceback": "Cannot parse chart config from answer:\n" + res,
                }
            ).decode()
        )
    chart: Dict[str, Any] = {}
    message = ""
    error = False
    try:
        data = orjson.loads(json_str)
        if data["type"] and data["type"] != "error":
            chart = data
            DataFormat.align_chart_bindings(chart, fields)
        elif data["type"] == "error":
            message = data["reason"]
            error = True
        else:
            raise Exception("Chart is empty")
    except Exception:
        error = True
        message = orjson.dumps(
            {
                "message": "Cannot parse chart config from answer",
                "traceback": "Cannot parse chart config from answer:\n" + res,
            }
        ).decode()
    if error:
        raise SingleMessageError(message)
    return chart
