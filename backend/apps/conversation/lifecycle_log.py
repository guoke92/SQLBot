"""Compact structured lifecycle logs for runtime fault diagnosis.

Run events remain the transport timeline and ``chat_log`` remains the business
audit trail.  This module only emits operational facts to the application log.
"""

from __future__ import annotations

from typing import Any

import orjson

from common.utils.utils import SQLBotLogUtil

_ALLOWED_FIELDS = frozenset(
    {
        "run_id",
        "record_id",
        "chat_id",
        "graph_key",
        "node",
        "phase",
        "status",
        "dispatch_attempt",
        "intent_revision",
        "plan_id",
        "elapsed_ms",
        "error_type",
        "error_code",
        "asset_id",
        "asset_kind",
        "reason",
        "count",
    }
)


def log_lifecycle(event: str, *, level: str = "info", **fields: Any) -> None:
    payload = {"event": event}
    payload.update(
        {
            key: value
            for key, value in fields.items()
            if key in _ALLOWED_FIELDS and value is not None
        }
    )
    message = orjson.dumps(payload, default=str).decode()
    logger = getattr(SQLBotLogUtil, level, SQLBotLogUtil.info)
    logger(message)
