"""Stream runtime: single chunk queue + sole graph execution entry.

All chat streaming (NLQ process path, analysis, predict, config, …) goes
through StreamRunner. Production callers launch graphs only via ``submit_graph``.
"""

from __future__ import annotations

import concurrent.futures
import os
import queue
import threading
import traceback
from collections.abc import Callable, Generator, Iterable, Iterator, Mapping
from concurrent.futures import Future, ThreadPoolExecutor
from typing import Any

from apps.conversation.registry import get_graph
from apps.conversation.sink import sink_error_chunks
from common.utils.utils import SQLBotLogUtil


def _bounded_setting_int(name: str, default: int, *, minimum: int, maximum: int) -> int:
    try:
        from common.core.config import settings

        configured = settings.model_dump().get(name, default)
        value = int(configured)
        return max(minimum, min(value, maximum))
    except Exception:
        pass
    try:
        value = int(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        value = default
    return max(minimum, min(value, maximum))


# One request occupies a worker while its model/database stream is active.
# Keep this below the aggregate DB connection ceiling by default; deployments
# can tune it explicitly without reintroducing an unbounded executor.
_MAX_WORKERS = _bounded_setting_int(
    "CONVERSATION_MAX_WORKERS",
    32,
    minimum=1,
    maximum=200,
)
_QUEUE_SIZE = _bounded_setting_int(
    "CONVERSATION_STREAM_QUEUE_SIZE",
    256,
    minimum=8,
    maximum=4096,
)
_RECURSION_LIMIT = _bounded_setting_int(
    "CONVERSATION_RECURSION_LIMIT",
    64,
    minimum=16,
    maximum=512,
)
_QUERY_MAX_CONCURRENCY = _bounded_setting_int(
    "CONVERSATION_QUERY_MAX_CONCURRENCY",
    16,
    minimum=1,
    maximum=200,
)
_executor: ThreadPoolExecutor | None = None
_executor_lock = threading.Lock()
_query_executor: ThreadPoolExecutor | None = None
_query_executor_lock = threading.Lock()


def _submit_background(fn: Callable[[], None]) -> Future[None]:
    global _executor
    with _executor_lock:
        if _executor is None:
            _executor = ThreadPoolExecutor(max_workers=_MAX_WORKERS)
        return _executor.submit(fn)


def submit_query(
    fn: Callable[..., Any],
    *args: Any,
    **kwargs: Any,
) -> Future[Any]:
    """Submit datasource work to the process-wide bounded query pool."""
    global _query_executor
    with _query_executor_lock:
        if _query_executor is None:
            _query_executor = ThreadPoolExecutor(
                max_workers=_QUERY_MAX_CONCURRENCY,
                thread_name_prefix="conversation-query",
            )
        return _query_executor.submit(fn, *args, **kwargs)


def shutdown_runtime(*, wait: bool = False) -> None:
    """Release conversation worker resources during application shutdown."""
    global _executor, _query_executor
    with _executor_lock:
        current = _executor
        _executor = None
    with _query_executor_lock:
        current_query = _query_executor
        _query_executor = None
    if current is not None:
        current.shutdown(wait=wait, cancel_futures=True)
    if current_query is not None:
        current_query.shutdown(wait=wait, cancel_futures=True)


class StreamRunner:
    """Background graph execution with an optional streaming consumer.

    The graph owns the business lifecycle.  ``await_result`` is only a live
    transport consumer: closing it detaches SSE delivery but must not cancel or
    finalize the graph run.
    """

    def __init__(self) -> None:
        self._chunks: queue.Queue[Any] = queue.Queue(maxsize=_QUEUE_SIZE)
        self._consumer_detached = threading.Event()
        self.future: Future[None] | None = None

    def is_running(self, timeout: float = 0.5) -> bool:
        if self.future is None:
            return False
        try:
            r = concurrent.futures.wait([self.future], timeout=timeout)
            return len(r.not_done) > 0
        except Exception:
            return True

    def await_result(self) -> Generator[Any, None, None]:
        try:
            while self.is_running(timeout=0) or not self._chunks.empty():
                try:
                    yield self._chunks.get(timeout=0.25)
                except queue.Empty:
                    continue
        finally:
            # StreamingResponse closes this generator on client disconnect.
            self.detach()

    def detach(self) -> None:
        """Detach the stream consumer without changing graph execution state."""
        if self._consumer_detached.is_set():
            return
        self._consumer_detached.set()
        while True:
            try:
                self._chunks.get_nowait()
            except queue.Empty:
                break

    def submit(
        self, fn: Callable[..., Iterable[Any]], *args: Any, **kwargs: Any
    ) -> None:
        """Run ``fn(*args, **kwargs)`` in the pool; each yielded item is enqueued."""

        def _cache() -> None:
            for chunk in fn(*args, **kwargs):
                if self._consumer_detached.is_set():
                    continue
                while not self._consumer_detached.is_set():
                    try:
                        self._chunks.put(chunk, timeout=0.25)
                        break
                    except queue.Full:
                        continue

        self.future = _submit_background(_cache)


def run_graph(graph_key: str, ctx: Any, **builder_kwargs: Any) -> Iterator[Any]:
    """Resolve ``graph_key``, build the runnable, and stream its outputs.

    Builders registered in the registry may return:
    - a generator / iterable of SSE frame strings (or any chunks), or
    - a LangGraph compiled graph that writes SSE via ``get_stream_writer()``.

    Compiled graphs always stream with ``stream_mode=\"custom\"`` so yields are
    exactly the frames writers produced — not intermediate state dumps.
    """
    builder = get_graph(graph_key)
    runnable = builder(ctx, **builder_kwargs)

    # Compiled LangGraph graphs expose stream/invoke
    if hasattr(runnable, "stream") and callable(runnable.stream):
        stream_fn = runnable.stream
        # Prefer a dict-ish input for graph state; plain mapping ctx is fine.
        input_state = ctx if isinstance(ctx, dict) else {}
        run_id = str(input_state.get("run_id") or "")
        checkpointer = getattr(runnable, "checkpointer", None)
        if checkpointer is not None and not run_id:
            raise ValueError("Durable conversation graph requires run_id")
        resume_value = input_state.pop("__resume__", None)
        continue_existing = bool(input_state.pop("__continue__", False))
        graph_input: Any = input_state
        if resume_value is not None:
            from langgraph.types import Command

            graph_input = Command(resume=resume_value)
        elif continue_existing:
            graph_input = None
        config: dict[str, Any] = {"recursion_limit": _RECURSION_LIMIT}
        if run_id:
            config["configurable"] = {"thread_id": run_id}
        for item in stream_fn(graph_input, config=config, stream_mode="custom"):
            yield item
        return

    if hasattr(runnable, "__iter__") and not isinstance(runnable, str | bytes | dict):
        for item in runnable:
            yield item
        return

    yield runnable


def submit_graph(
    graph_key: str, ctx: Mapping[str, Any], **builder_kwargs: Any
) -> StreamRunner:
    """**Sole production entry**: registry → graph stream → StreamRunner queue.

    Callers (chat API, MCP adapters) must use this — not per-scene ``start_*``
    wrappers and not ad-hoc ``StreamRunner().submit(run_graph, ...)``.
    """
    # Materialize a plain dict so workers own a stable snapshot.
    state: dict[str, Any] = dict(ctx)
    record_id = state.get("record_id")
    run_id = str(state.get("run_id") or "")
    runner = StreamRunner()

    def _run() -> Iterator[Any]:
        try:
            if run_id:
                from apps.conversation.models import ConversationRun
                from apps.conversation.run_service import (
                    ConversationRunCancelled,
                    update_run_status,
                )
                from apps.conversation.session import session_scope

                with session_scope() as session:
                    current = session.get(ConversationRun, run_id)
                    if current is not None and current.status == "cancelled":
                        raise ConversationRunCancelled(run_id)
                    update_run_status(session, run_id, "running")
            yield from run_graph(graph_key, state, **builder_kwargs)
            if run_id:
                from apps.conversation.models import ConversationRun
                from apps.conversation.session import session_scope

                with session_scope() as session:
                    completed = session.get(ConversationRun, run_id)
                    status = completed.status if completed is not None else "missing"
                if status in {"queued", "running"}:
                    raise RuntimeError(
                        f"Conversation graph ended without a terminal or interrupt state: {status}"
                    )
                # checkpoint_id is an audit index, not part of the business
                # outcome. A transient read failure must never rewrite an
                # already committed terminal result.
                try:
                    from apps.conversation.checkpoint import get_checkpointer
                    from apps.conversation.run_service import record_checkpoint_id

                    checkpoint = get_checkpointer().get_tuple(
                        {"configurable": {"thread_id": run_id}}
                    )
                    checkpoint_id = str(
                        (
                            (checkpoint.config if checkpoint else {}).get(
                                "configurable"
                            )
                            or {}
                        ).get("checkpoint_id")
                        or ""
                    )
                    with session_scope() as session:
                        record_checkpoint_id(session, run_id, checkpoint_id)
                except Exception as checkpoint_exc:  # noqa: BLE001
                    SQLBotLogUtil.warning(
                        f"checkpoint index update failed for run {run_id}: {checkpoint_exc}"
                    )
        except Exception as e:
            from apps.conversation.run_service import (
                TERMINAL_STATUSES,
                ConversationRunCancelled,
            )

            if isinstance(e, ConversationRunCancelled):
                return
            traceback.print_exc()
            terminal_already_committed = False
            if run_id:
                try:
                    from apps.conversation.models import ConversationRun
                    from apps.conversation.run_service import (
                        append_run_event,
                        finalize_run,
                    )
                    from apps.conversation.session import session_scope

                    with session_scope() as session:
                        current = session.get(ConversationRun, run_id)
                        terminal_already_committed = bool(
                            current is not None and current.status in TERMINAL_STATUSES
                        )
                        if not terminal_already_committed:
                            finalize_run(
                                session,
                                run_id=run_id,
                                status="failed",
                                current_node="runtime",
                                record_snapshot={"terminal": True, "error": str(e)},
                                error_summary=str(e),
                            )
                    if not terminal_already_committed:
                        with session_scope() as session:
                            append_run_event(
                                session,
                                run_id=run_id,
                                payload={"type": "error", "content": str(e)},
                            )
                except Exception:
                    traceback.print_exc()
            elif record_id:
                try:
                    from apps.conversation.turn import persist_turn_failure

                    persist_turn_failure(int(record_id), str(e))
                except Exception:
                    traceback.print_exc()
            if not terminal_already_committed:
                yield from sink_error_chunks(state, str(e))
        finally:
            if run_id:
                # Checkpoints contain only IDs, so paused and completed runs
                # can always rehydrate. Keeping request-scoped models here
                # would leak clients and stale ORM-backed context indefinitely.
                from apps.conversation.runtime_context import detach_runtime

                detach_runtime(run_id)

    runner.submit(_run)
    return runner


def recover_incomplete_runs() -> int:
    """Resume durable checkpoints after process restart.

    ``awaiting_input`` runs intentionally remain paused.  Executed NLQ plans
    are idempotent in ``nlq_run``, so replay cannot query the datasource twice.
    """
    from sqlalchemy import select

    from apps.conversation.checkpoint import get_checkpointer
    from apps.conversation.models import ConversationRun
    from apps.conversation.run_service import update_run_status
    from apps.conversation.session import session_scope

    with session_scope() as session:
        runs = list(
            session.exec(
                select(ConversationRun).where(
                    ConversationRun.status.in_(["queued", "running", "awaiting_input"])
                )
            ).scalars()
        )
        detached = [ConversationRun(**run.model_dump()) for run in runs]

    recovered = 0
    saver = get_checkpointer()
    for run in detached:
        try:
            checkpoint = saver.get_tuple({"configurable": {"thread_id": run.run_id}})
        except Exception as exc:
            SQLBotLogUtil.warning(
                f"checkpoint recovery deferred for run {run.run_id}: {exc}"
            )
            continue
        if run.status == "awaiting_input" and checkpoint is not None:
            continue
        if run.status == "awaiting_input":
            with session_scope() as session:
                update_run_status(session, run.run_id, "running")
        if checkpoint is not None:
            state: dict[str, Any] = {
                "run_id": run.run_id,
                "record_id": run.chat_record_id,
                "graph_key": run.graph_key,
                "sink": "sse",
                "__continue__": True,
            }
        elif run.graph_key == "config":
            from apps.config_assistant.nodes import recover_config_state

            state = recover_config_state(run)
        elif run.graph_key in {"analysis", "predict"}:
            from apps.chat.models.chat_model import ChatRecord

            with session_scope() as session:
                record = session.get(ChatRecord, run.chat_record_id)
                if record is None:
                    continue
                base_record_id = (
                    record.analysis_record_id
                    if run.graph_key == "analysis"
                    else record.predict_record_id
                )
            if base_record_id is None:
                continue
            state = {
                "run_id": run.run_id,
                "record_id": run.chat_record_id,
                "base_record_id": int(base_record_id),
                "graph_key": run.graph_key,
                "sink": "sse",
                "mode": "follow_up",
            }
        else:
            from apps.chat.models.chat_model import ChatFinishStep

            state = {
                "run_id": run.run_id,
                "record_id": run.chat_record_id,
                "graph_key": "chat",
                "sink": "sse",
                "mode": "primary",
                "finish_step": int(ChatFinishStep.GENERATE_CHART.value),
                "return_img": True,
            }
        submit_graph(run.graph_key, state).detach()
        recovered += 1
    return recovered
