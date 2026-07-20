"""Workspace / datasource scope for RAG-style match steps."""

from __future__ import annotations

from typing import Any, Optional, Tuple


def match_scope(
    llm_service: Any,
    oid: Optional[int] = None,
    ds_id: Optional[int] = None,
) -> Tuple[Optional[int], Optional[int], Optional[int]]:
    """Return ``(oid, ds_id, assistant_id)`` used by terminology/training/prompts.

    Assistant type=1 (out-of-band dynamic DS) drops ds scoping and passes assistant id.
    Assistant type=4 keeps chat workspace oid.
    """
    calculate_oid = oid
    calculate_ds_id = ds_id
    assistant_id: Optional[int] = None
    current_assistant = getattr(llm_service, "current_assistant", None)
    if current_assistant:
        calculate_oid = (
            current_assistant.oid
            if current_assistant.type != 4
            else getattr(llm_service, "oid", None)
        )
        if current_assistant.type == 1:
            calculate_ds_id = None
            assistant_id = current_assistant.id
    return calculate_oid, calculate_ds_id, assistant_id
