"""Single SSE frame protocol for all chat scenarios.

Front-end types are the product contract — frames always look like:
  data:{json}\\n\\n
with a top-level ``type`` field (and scenario-specific fields).
"""

from __future__ import annotations

from typing import Any, Mapping

import orjson


def emit(payload: Mapping[str, Any]) -> str:
    """Serialize one chat SSE frame.

    ``payload`` must already include ``type`` (and any other fields the FE expects).
    This is the only place that builds ``data:...\\n\\n`` for chat streaming.
    """
    return "data:" + orjson.dumps(dict(payload)).decode() + "\n\n"
