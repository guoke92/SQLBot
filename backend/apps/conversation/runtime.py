"""Stream runtime: single chunk queue + sole graph execution entry.

All chat streaming (NLQ process path, analysis, predict, config, …) goes
through StreamRunner. Production callers launch graphs only via ``submit_graph``.
"""

from __future__ import annotations

import collections
import concurrent.futures
import threading
import traceback
from concurrent.futures import Future, ThreadPoolExecutor
from typing import Any, Callable, Generator, Iterable, Iterator, List, Mapping, Optional

from apps.conversation.registry import get_graph
from apps.conversation.sink import sink_error_chunks

# Shared pool for background streaming work (same capacity as historic llm executor).
executor = ThreadPoolExecutor(max_workers=200)


class StreamRunner:
    """Background generator → chunk queue → FE consumer via ``await_result``."""

    def __init__(self) -> None:
        self._chunks: collections.deque[Any] = collections.deque()
        self._event = threading.Event()
        self.future: Optional[Future[None]] = None

    def is_running(self, timeout: float = 0.5) -> bool:
        if self.future is None:
            return False
        try:
            r = concurrent.futures.wait([self.future], timeout=timeout)
            return len(r.not_done) > 0
        except Exception:
            return True

    def pop_chunk(self) -> Any | None:
        try:
            return self._chunks.popleft()
        except IndexError:
            return None

    def await_result(self) -> Generator[Any, None, None]:
        while self.is_running():
            while True:
                chunk = self.pop_chunk()
                if chunk is not None:
                    yield chunk
                else:
                    break
        while True:
            chunk = self.pop_chunk()
            if chunk is None:
                break
            yield chunk

    def submit(self, fn: Callable[..., Iterable[Any]], *args: Any, **kwargs: Any) -> None:
        """Run ``fn(*args, **kwargs)`` in the pool; each yielded item is enqueued."""

        def _cache() -> None:
            for chunk in fn(*args, **kwargs):
                self._chunks.append(chunk)
                self._event.set()

        self.future = executor.submit(_cache)


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
    if hasattr(runnable, "stream") and callable(getattr(runnable, "stream")):
        stream_fn = getattr(runnable, "stream")
        # Prefer a dict-ish input for graph state; plain mapping ctx is fine.
        input_state = ctx if isinstance(ctx, dict) else {}
        for item in stream_fn(input_state, stream_mode="custom"):
            yield item
        return

    if hasattr(runnable, "__iter__") and not isinstance(runnable, (str, bytes, dict)):
        for item in runnable:
            yield item
        return

    yield runnable


def submit_graph(graph_key: str, ctx: Mapping[str, Any], **builder_kwargs: Any) -> StreamRunner:
    """**Sole production entry**: registry → graph stream → StreamRunner queue.

    Callers (chat API, MCP adapters) must use this — not per-scene ``start_*``
    wrappers and not ad-hoc ``StreamRunner().submit(run_graph, ...)``.
    """
    runner = StreamRunner()
    # Materialize a plain dict so workers own a stable snapshot.
    state: dict[str, Any] = dict(ctx)

    def _run() -> Iterator[Any]:
        try:
            yield from run_graph(graph_key, state, **builder_kwargs)
        except Exception as e:
            traceback.print_exc()
            yield from sink_error_chunks(state, str(e))

    runner.submit(_run)
    return runner
