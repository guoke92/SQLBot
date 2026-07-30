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
        for item in stream_fn(
            input_state,
            config={"recursion_limit": _RECURSION_LIMIT},
            stream_mode="custom",
        ):
            yield item
        return

    if hasattr(runnable, "__iter__") and not isinstance(runnable, (str, bytes, dict)):
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
    runner = StreamRunner()

    def _run() -> Iterator[Any]:
        try:
            yield from run_graph(graph_key, state, **builder_kwargs)
        except Exception as e:
            traceback.print_exc()
            if record_id:
                try:
                    from apps.conversation.turn import persist_turn_failure

                    persist_turn_failure(int(record_id), str(e))
                except Exception:
                    traceback.print_exc()
            yield from sink_error_chunks(state, str(e))

    runner.submit(_run)
    return runner
