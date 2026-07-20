"""Sync bridge for async callables invoked inside StreamRunner worker threads.

Graphs and tools share one helper — no per-module copy of event-loop policy.
"""

from __future__ import annotations

import asyncio
import concurrent.futures
from typing import Any, Coroutine, TypeVar

T = TypeVar("T")


def run_coro_sync(coro: Coroutine[Any, Any, T]) -> T:
    """Run ``coro`` to completion from a (typically worker) thread.

    - No running loop → ``asyncio.run``
    - Running loop present → offload to a short-lived thread with its own loop
      (avoids nested-loop deadlocks when nested under an unexpected loop).
    """
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(asyncio.run, coro).result()
