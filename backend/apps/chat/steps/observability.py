"""Graph-span observability via ChatLog (single audit channel for ExecutionDetails).

Nodes/steps call ``log_span`` instead of inventing parallel timelines.
Messages use a stable envelope so the UI can show batch/attempt/unit labels.

Envelope (when structured)::

    {
      "sqlbot_span": true,
      "graph_node": "execute_queries",
      "step_index": 0,
      "gen_attempts": 0,
      "unit_index": 1,
      "brief": "...",
      "payload": { ... domain summary ... }
    }

Legacy step logs keep list-of-chat-messages or bare dicts; history API still works.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Dict, Iterator, List, Optional, Union

import orjson

from apps.chat.curd.chat import end_log, start_log, trigger_log_error
from apps.chat.models.chat_model import ChatLog, OperationEnum
from apps.conversation.session import session_scope

SPAN_FLAG = "sqlbot_span"


def make_span_message(
    *,
    graph_node: str = "",
    step_index: Optional[int] = None,
    gen_attempts: Optional[int] = None,
    unit_index: Optional[int] = None,
    brief: str = "",
    payload: Optional[Dict[str, Any]] = None,
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    msg: Dict[str, Any] = {SPAN_FLAG: True}
    if graph_node:
        msg["graph_node"] = graph_node
    if step_index is not None:
        msg["step_index"] = int(step_index)
    if gen_attempts is not None:
        msg["gen_attempts"] = int(gen_attempts)
    if unit_index is not None:
        msg["unit_index"] = int(unit_index)
    if brief:
        msg["brief"] = brief
    if payload is not None:
        msg["payload"] = payload
    if extra:
        for k, v in extra.items():
            if k not in msg and v is not None:
                msg[k] = v
    return msg


def inject_span_meta(
    messages: Union[List[Any], Dict[str, Any], str, None],
    *,
    graph_node: str = "",
    step_index: Optional[int] = None,
    gen_attempts: Optional[int] = None,
    unit_index: Optional[int] = None,
    brief: str = "",
    payload: Optional[Dict[str, Any]] = None,
) -> Union[List[Any], Dict[str, Any]]:
    """Merge span meta into step message payloads (list or dict)."""
    meta = make_span_message(
        graph_node=graph_node,
        step_index=step_index,
        gen_attempts=gen_attempts,
        unit_index=unit_index,
        brief=brief,
        payload=payload,
    )
    if messages is None:
        return meta
    if isinstance(messages, dict):
        if messages.get(SPAN_FLAG):
            merged = dict(messages)
            for k, v in meta.items():
                if k == "payload" and isinstance(v, dict) and isinstance(merged.get("payload"), dict):
                    merged["payload"] = {**merged["payload"], **v}
                elif k not in merged or merged.get(k) in (None, "", []):
                    merged[k] = v
            return merged
        return {**meta, "payload": messages}
    if isinstance(messages, list):
        # Chat-style message list: prepend a system meta marker the UI can skip/show.
        head = {
            "type": "system",
            "sqlbot_system": True,
            "sqlbot_span_meta": True,
            "content": orjson.dumps(meta).decode(),
        }
        return [head, *messages]
    if isinstance(messages, str):
        return {**meta, "payload": {"text": messages}}
    return meta


def _messages_for_storage(messages: Union[List[Any], Dict[str, Any], str, None]) -> Any:
    if messages is None:
        return None
    if isinstance(messages, (dict, list)):
        return messages
    return messages


@contextmanager
def log_span(
    *,
    operate: OperationEnum,
    record_id: Optional[int],
    ai_modal_id: Optional[int] = None,
    ai_modal_name: Optional[str] = None,
    local_operation: bool = True,
    graph_node: str = "",
    step_index: Optional[int] = None,
    gen_attempts: Optional[int] = None,
    unit_index: Optional[int] = None,
    brief: str = "",
    initial_payload: Optional[Dict[str, Any]] = None,
) -> Iterator[Dict[str, Any]]:
    """Context manager: one ChatLog row covering a graph unit of work.

    Usage::

        with log_span(operate=..., record_id=..., graph_node="ground_entities") as span:
            ...
            span["payload"] = {...}
            span["error"] = True  # optional
    """
    span: Dict[str, Any] = {
        "payload": dict(initial_payload or {}),
        "error": False,
        "token_usage": None,
        "reasoning_content": None,
        "log": None,
    }
    if not record_id:
        yield span
        return

    initial_msg = make_span_message(
        graph_node=graph_node,
        step_index=step_index,
        gen_attempts=gen_attempts,
        unit_index=unit_index,
        brief=brief,
        payload=span["payload"] or None,
    )
    log: Optional[ChatLog] = None
    try:
        with session_scope() as session:
            log = start_log(
                session=session,
                ai_modal_id=ai_modal_id,
                ai_modal_name=ai_modal_name,
                operate=operate,
                record_id=record_id,
                full_message=_messages_for_storage(initial_msg),
                local_operation=local_operation,
            )
            span["log"] = log
        yield span
    except Exception:
        span["error"] = True
        raise
    finally:
        if log is None:
            return
        try:
            final_msg = make_span_message(
                graph_node=graph_node,
                step_index=step_index,
                gen_attempts=gen_attempts,
                unit_index=unit_index,
                brief=brief,
                payload=span.get("payload") or None,
            )
            with session_scope() as session:
                if span.get("error"):
                    try:
                        trigger_log_error(session, log)
                    except Exception:
                        pass
                end_log(
                    session=session,
                    log=log,
                    full_message=_messages_for_storage(final_msg),
                    reasoning_content=span.get("reasoning_content"),
                    token_usage=span.get("token_usage") or {},
                )
        except Exception:
            # Observability must not break the main graph.
            pass
