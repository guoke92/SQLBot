"""Shared chat constants (no I/O, safe for curd/steps/graphs imports)."""

from __future__ import annotations

# Assistant types that bind datasources via external/dynamic APIs (outAPI, …).
# Single source of truth — import this; do not redeclare (1, 3) inline.
DYNAMIC_DS_TYPES: list[int] = [1, 3]
