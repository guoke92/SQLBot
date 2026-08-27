"""Chat-scoped caching of datasource connectivity and access scope.

The datasource bound to a chat and the user's AccessScope over it rarely
change mid-conversation, yet every turn re-paid a target-DB roundtrip
(``check_connection``) and a catalog scan (``resolve_access_scope``) and
cluttered the audit timeline with duplicate steps. Entries are process-local
with a TTL — the same trade the value index makes — so permission revocations
apply within the TTL window and connection failures invalidate immediately.

The scope key is ``(oid, ds_id, user_id)``: scope depends on user + datasource,
never on the chat itself, so concurrent chats share entries correctly.
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from typing import Any

from apps.datasource.access import AccessScope

CONNECTION_TTL_SEC = 120.0
SCOPE_TTL_SEC = 300.0

_MISSING: Any = object()


@dataclass(frozen=True)
class _ConnectionEntry:
    expires: float


@dataclass(frozen=True)
class _ScopeEntry:
    scope: AccessScope | None
    expires: float


_CONNECTIONS: dict[int, _ConnectionEntry] = {}
_SCOPES: dict[tuple[int, int, int], _ScopeEntry] = {}
_LOCK = threading.Lock()


def clear_chat_scope_cache() -> None:
    """Test hook: drop all process-local entries."""
    with _LOCK:
        _CONNECTIONS.clear()
        _SCOPES.clear()


def connection_fresh(ds_id: int | None) -> bool:
    if ds_id is None:
        return False
    with _LOCK:
        entry = _CONNECTIONS.get(int(ds_id))
        return entry is not None and entry.expires > time.monotonic()


def remember_connection(ds_id: int | None) -> None:
    if ds_id is None:
        return
    with _LOCK:
        _CONNECTIONS[int(ds_id)] = _ConnectionEntry(
            expires=time.monotonic() + CONNECTION_TTL_SEC
        )


def invalidate_connection(ds_id: int | None) -> None:
    if ds_id is None:
        return
    with _LOCK:
        _CONNECTIONS.pop(int(ds_id), None)


def cached_access_scope(
    oid: int, ds_id: int | None, user_id: int | None
) -> Any:
    """Return the cached AccessScope (may be None) or ``_MISSING``."""
    if ds_id is None:
        return _MISSING
    with _LOCK:
        entry = _SCOPES.get((int(oid), int(ds_id), int(user_id or 0)))
        if entry is None or entry.expires <= time.monotonic():
            return _MISSING
        return entry.scope


def remember_access_scope(
    oid: int, ds_id: int | None, user_id: int | None, scope: AccessScope | None
) -> None:
    if ds_id is None:
        return
    with _LOCK:
        _SCOPES[(int(oid), int(ds_id), int(user_id or 0))] = _ScopeEntry(
            scope=scope, expires=time.monotonic() + SCOPE_TTL_SEC
        )


def is_missing(value: Any) -> bool:
    return value is _MISSING
