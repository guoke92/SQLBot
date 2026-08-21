"""Shared in-memory SQLModel store for node-plane tests.

Replaces the per-file FakeStore / _ExecResult / _row_predicate copies so the
where-clause predicate and entity dispatch are defined once.  Test files keep
their own entity -> attribute mapping and subclass FakeStore.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock


class ExecResult:
    def __init__(self, items: list[Any]) -> None:
        self._items = items

    def all(self) -> list[Any]:
        return list(self._items)

    def first(self) -> Any:
        return self._items[0] if self._items else None

    def one_or_none(self) -> Any:
        return self._items[0] if self._items else None


def row_predicate(crit: Any) -> Any:
    """Compile simple eq / ne / in_ / and_ / or_ criteria into a row predicate."""
    if crit.__class__.__name__ == "BooleanClauseList":
        parts = [row_predicate(c) for c in crit.clauses]
        name = getattr(crit.operator, "__name__", "")
        if name == "and_":
            return lambda row: all(p(row) for p in parts)
        if name == "or_":
            return lambda row: any(p(row) for p in parts)
        return lambda row: False
    key = getattr(crit.left, "key", None)
    value = getattr(crit.right, "value", crit.right)
    op_name = getattr(crit.operator, "__name__", "")
    if key is None:
        return lambda row: True
    if op_name == "eq":
        return lambda row: getattr(row, key, None) == value
    if op_name == "ne":
        return lambda row: getattr(row, key, None) != value
    if op_name == "in_":
        return lambda row: getattr(row, key, None) in (value or [])
    return lambda row: True


class FakeStore:
    """Dispatch exec() by selected entity, keeping per-entity row lists."""

    def __init__(self, entities: dict[Any, str]) -> None:
        self._entities = entities
        for attr in entities.values():
            setattr(self, attr, [])
        self._next_id = 100

    def session(self) -> MagicMock:
        session = MagicMock()
        store = self

        def _exec(stmt: Any) -> ExecResult:
            entity = (
                stmt.column_descriptions[0]["entity"]
                if stmt.column_descriptions
                else None
            )
            rows = (
                list(getattr(store, store._entities.get(entity, "")))
                if entity in store._entities
                else []
            )
            clause = None
            try:
                clause = stmt.whereclause
            except Exception:  # noqa: BLE001
                clause = None
            if clause is not None and clause.__class__.__name__ != "True_":
                try:
                    predicate = row_predicate(clause)
                    rows = [row for row in rows if predicate(row)]
                except Exception:  # noqa: BLE001 - fall back to unfiltered
                    pass
            return ExecResult(rows)

        session.exec.side_effect = _exec
        session.get.side_effect = lambda model, pk: next(
            (
                row
                for row in getattr(store, store._entities.get(model, ""))
                if getattr(row, "id", None) == pk
            ),
            None,
        )
        session.add.side_effect = self._add
        session.flush.side_effect = self._flush
        session.commit.side_effect = lambda: None
        session.refresh.side_effect = lambda obj: None
        session.rollback.side_effect = lambda: None
        return session

    def _add(self, obj: Any) -> None:
        attr = self._entities.get(type(obj))
        if attr is None:
            return
        rows = getattr(self, attr)
        if obj not in rows:
            rows.append(obj)

    def _flush(self) -> None:
        for rows in (getattr(self, a) for a in set(self._entities.values())):
            for row in rows:
                if getattr(row, "id", None) is None:
                    self._next_id += 1
                    try:
                        row.id = self._next_id
                    except Exception:  # noqa: BLE001
                        pass
