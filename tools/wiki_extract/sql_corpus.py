"""Historical SQL feature corpus.

Extracts equality joins, multi-column join groups, transform joins, and
named formulas from SQL text. Three ingest sources share one store:

- ``init_existing`` — full replace of that source (bootstrap from SQL already on hand)
- ``manual_example`` — incremental upsert (human-added examples)
- ``user_accepted`` — incremental upsert (SQL a user confirmed)

Callers that own those scenarios are not wired yet. They should pass
``SqlRecord`` into ``replace_source`` / ``upsert`` / ``remove``.
Extracted features stay proposed evidence; this module does not write wiki fences.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Mapping, Sequence

import sqlglot
import yaml
from sqlglot import exp
from sqlglot.errors import ParseError

from tools.wiki_extract.join_policy import classify_join_role


class SqlSource(str, Enum):
    """Closed set of corpus sources. New producers must use one of these."""

    INIT_EXISTING = "init_existing"
    MANUAL_EXAMPLE = "manual_example"
    USER_ACCEPTED = "user_accepted"


_SOURCES = frozenset(item.value for item in SqlSource)


@dataclass(frozen=True)
class SqlRecord:
    """One SQL text plus the scenario that produced it."""

    record_id: str
    source: str
    sql: str
    question: str = ""
    dialect: str = "mysql"

    def key(self) -> tuple[str, str]:
        return (self.source, self.record_id)


@dataclass
class CorpusDelta:
    added: int = 0
    updated: int = 0
    removed: int = 0
    parse_errors: list[dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "added": self.added,
            "updated": self.updated,
            "removed": self.removed,
            "parse_errors": list(self.parse_errors),
        }


@dataclass
class _EqJoin:
    left: str
    right: str
    join_role: str

    def identity(self) -> tuple[str, str]:
        pair = tuple(sorted((self.left.lower(), self.right.lower())))
        return pair[0], pair[1]


@dataclass
class _TransformJoin:
    left_sql: str
    right_sql: str
    fields: tuple[str, ...]

    def identity(self) -> tuple[str, str]:
        pair = tuple(sorted((self.left_sql.lower(), self.right_sql.lower())))
        return pair[0], pair[1]


@dataclass
class _JoinGroup:
    tables: tuple[str, str]
    predicates: tuple[tuple[str, str], ...]

    def identity(self) -> tuple[Any, ...]:
        return (self.tables, self.predicates)


@dataclass
class _Formula:
    alias: str
    formula: str
    fields: tuple[str, ...]
    nested: bool

    def identity(self) -> tuple[str, str]:
        return (self.alias.lower(), " ".join(self.formula.lower().split()))


@dataclass
class _RecordFeatures:
    record: SqlRecord
    parse_error: str = ""
    equality_joins: list[_EqJoin] = field(default_factory=list)
    transform_joins: list[_TransformJoin] = field(default_factory=list)
    join_groups: list[_JoinGroup] = field(default_factory=list)
    named_formulas: list[_Formula] = field(default_factory=list)


class SqlFeatureCorpus:
    """In-memory store. ``replace_source`` bootstraps; ``upsert`` increments."""

    def __init__(self) -> None:
        self._items: dict[tuple[str, str], _RecordFeatures] = {}

    def replace_source(self, source: str, records: Sequence[SqlRecord]) -> CorpusDelta:
        """Drop every record of ``source``, then load ``records`` as the new snapshot."""
        source = _require_source(source)
        delta = CorpusDelta()
        incoming = _index_records(source, records)
        old_keys = [key for key in self._items if key[0] == source]
        new_keys = set(incoming)
        for key in old_keys:
            if key not in new_keys:
                del self._items[key]
                delta.removed += 1
        for key, record in incoming.items():
            if key in self._items:
                delta.updated += 1
            else:
                delta.added += 1
            features = extract_sql_features(record)
            self._items[key] = features
            if features.parse_error:
                delta.parse_errors.append(_error_row(features))
        return delta

    def upsert(self, records: Sequence[SqlRecord]) -> CorpusDelta:
        """Insert or replace by ``(source, record_id)``. Other records stay."""
        delta = CorpusDelta()
        for record in records:
            _require_source(record.source)
            _require_record_id(record.record_id)
            key = record.key()
            if key in self._items:
                delta.updated += 1
            else:
                delta.added += 1
            features = extract_sql_features(record)
            self._items[key] = features
            if features.parse_error:
                delta.parse_errors.append(_error_row(features))
        return delta

    def remove(self, source: str, record_ids: Sequence[str]) -> CorpusDelta:
        source = _require_source(source)
        delta = CorpusDelta()
        for record_id in record_ids:
            key = (source, record_id)
            if key in self._items:
                del self._items[key]
                delta.removed += 1
        return delta

    def aggregated(self) -> dict[str, Any]:
        """Features merged across sources. ``support`` counts distinct records."""
        equality: dict[tuple[str, str], dict[str, Any]] = {}
        transforms: dict[tuple[str, str], dict[str, Any]] = {}
        groups: dict[tuple[Any, ...], dict[str, Any]] = {}
        formulas: dict[tuple[str, str], dict[str, Any]] = {}
        errors: list[dict[str, str]] = []

        for features in self._items.values():
            ref = _record_ref(features.record)
            if features.parse_error:
                errors.append(_error_row(features))
                continue
            for join in features.equality_joins:
                _merge_support(
                    equality,
                    join.identity(),
                    {
                        "left": join.left,
                        "right": join.right,
                        "join_role": join.join_role,
                        "kind": "equality",
                    },
                    ref,
                )
            for join in features.transform_joins:
                _merge_support(
                    transforms,
                    join.identity(),
                    {
                        "left_sql": join.left_sql,
                        "right_sql": join.right_sql,
                        "fields": list(join.fields),
                        "kind": "transform",
                    },
                    ref,
                )
            for group in features.join_groups:
                _merge_support(
                    groups,
                    group.identity(),
                    {
                        "tables": list(group.tables),
                        "predicates": [
                            {"left": left, "right": right} for left, right in group.predicates
                        ],
                        "kind": "multi_column",
                    },
                    ref,
                )
            for formula in features.named_formulas:
                _merge_support(
                    formulas,
                    formula.identity(),
                    {
                        "alias": formula.alias,
                        "formula": formula.formula,
                        "fields": list(formula.fields),
                        "nested": formula.nested,
                        "kind": "named_formula",
                    },
                    ref,
                )

        return {
            "records": len(self._items),
            "by_source": _counts_by_source(self._items),
            "equality_joins": _sorted_features(equality),
            "transform_joins": _sorted_features(transforms),
            "join_groups": _sorted_features(groups),
            "named_formulas": _sorted_features(formulas),
            "parse_errors": errors,
        }

    def to_dict(self) -> dict[str, Any]:
        records = []
        for features in self._items.values():
            record = features.record
            records.append(
                {
                    "record_id": record.record_id,
                    "source": record.source,
                    "sql": record.sql,
                    "question": record.question,
                    "dialect": record.dialect,
                }
            )
        records.sort(key=lambda row: (row["source"], row["record_id"]))
        return {"records": records, "aggregated": self.aggregated()}

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> SqlFeatureCorpus:
        corpus = cls()
        records = [
            SqlRecord(
                record_id=str(row["record_id"]),
                source=str(row["source"]),
                sql=str(row.get("sql") or ""),
                question=str(row.get("question") or ""),
                dialect=str(row.get("dialect") or "mysql"),
            )
            for row in payload.get("records") or []
        ]
        if records:
            corpus.upsert(records)
        return corpus

    def save(self, path: Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            yaml.safe_dump(self.to_dict(), allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )

    @classmethod
    def load(cls, path: Path) -> SqlFeatureCorpus:
        payload = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
        if not isinstance(payload, dict):
            raise ValueError(f"sql corpus file is not a mapping: {path}")
        return cls.from_dict(payload)


def extract_sql_features(record: SqlRecord) -> _RecordFeatures:
    """Parse one statement list into join / formula features."""
    features = _RecordFeatures(record=record)
    sql = (record.sql or "").strip()
    if not sql:
        features.parse_error = "empty sql"
        return features
    try:
        trees = sqlglot.parse(sql, dialect=record.dialect or "mysql")
    except ParseError as exc:
        features.parse_error = str(exc).splitlines()[0][:240]
        return features
    for tree in trees:
        if tree is None:
            continue
        for select in tree.find_all(exp.Select):
            _extract_select(select, features, nested=select is not _root_select(tree))
    _dedupe_record(features)
    return features


def _extract_select(select: exp.Select, features: _RecordFeatures, *, nested: bool) -> None:
    base_alias, subquery_outputs = _scope(select)
    for predicate in _predicates(select):
        bare: list[_EqJoin] = []
        for eq in _and_eqs(predicate):
            classified = _classify_eq(eq, base_alias, subquery_outputs)
            if classified is None:
                continue
            if isinstance(classified, _EqJoin):
                features.equality_joins.append(classified)
                bare.append(classified)
            else:
                features.transform_joins.append(classified)
        _add_groups(bare, features)
    if not nested:
        _extract_formulas(select, base_alias, subquery_outputs, features, nested=False)
    else:
        _extract_formulas(select, base_alias, subquery_outputs, features, nested=True)


def _scope(
    select: exp.Select,
) -> tuple[dict[str, str], dict[str, dict[str, list[str]]]]:
    base_alias: dict[str, str] = {}
    subquery_outputs: dict[str, dict[str, list[str]]] = {}
    sources = _from_sources(select)
    for source in sources:
        if isinstance(source, exp.Table):
            base_alias[source.alias_or_name] = source.name
        elif isinstance(source, exp.Subquery):
            alias = source.alias
            inner = source.this
            if alias and isinstance(inner, exp.Select):
                inner_base, inner_subs = _scope(inner)
                subquery_outputs[alias] = _output_map(inner, inner_base, inner_subs)
    return base_alias, subquery_outputs


def _from_sources(select: exp.Select) -> list[exp.Expression]:
    sources: list[exp.Expression] = []
    from_ = select.args.get("from_")
    if isinstance(from_, exp.From) and from_.this is not None:
        sources.append(from_.this)
    for join in select.args.get("joins") or []:
        if isinstance(join, exp.Join) and join.this is not None:
            sources.append(join.this)
    return sources


def _output_map(
    select: exp.Select,
    base_alias: dict[str, str],
    subquery_outputs: dict[str, dict[str, list[str]]],
) -> dict[str, list[str]]:
    outputs: dict[str, list[str]] = {}
    for expression in select.expressions:
        name = _output_name(expression)
        if not name:
            continue
        outputs[name] = _resolved_fields(expression, base_alias, subquery_outputs)
    return outputs


def _output_name(expression: exp.Expression) -> str:
    if isinstance(expression, exp.Alias):
        return expression.alias
    if isinstance(expression, exp.Column):
        return expression.name
    return ""


def _predicates(select: exp.Select) -> list[exp.Expression]:
    found: list[exp.Expression] = []
    for join in select.args.get("joins") or []:
        if isinstance(join, exp.Join):
            on = join.args.get("on")
            if on is not None:
                found.append(on)
    where = select.args.get("where")
    if isinstance(where, exp.Where) and where.this is not None:
        found.append(where.this)
    return found


def _and_eqs(predicate: exp.Expression) -> list[exp.EQ]:
    if isinstance(predicate, exp.And):
        return _and_eqs(predicate.left) + _and_eqs(predicate.right)
    if isinstance(predicate, exp.Paren):
        return _and_eqs(predicate.this)
    if isinstance(predicate, exp.EQ):
        return [predicate]
    return []


def _classify_eq(
    eq: exp.EQ,
    base_alias: dict[str, str],
    subquery_outputs: dict[str, dict[str, list[str]]],
) -> _EqJoin | _TransformJoin | None:
    left_fields = _resolved_fields(eq.left, base_alias, subquery_outputs)
    right_fields = _resolved_fields(eq.right, base_alias, subquery_outputs)
    if not left_fields or not right_fields:
        return None
    # Join = different range variables. Same physical table (self-join) still counts.
    left_quals = {column.table for column in eq.left.find_all(exp.Column) if column.table}
    right_quals = {column.table for column in eq.right.find_all(exp.Column) if column.table}
    if not left_quals or not right_quals or left_quals & right_quals:
        return None
    bare = (
        _is_bare_column(eq.left)
        and _is_bare_column(eq.right)
        and len(left_fields) == 1
        and len(right_fields) == 1
    )
    if bare:
        left, right = left_fields[0], right_fields[0]
        return _EqJoin(
            left=left,
            right=right,
            join_role=classify_join_role(left.split(".", 1)[1], right.split(".", 1)[1]),
        )
    return _TransformJoin(
        left_sql=eq.left.sql(dialect="mysql"),
        right_sql=eq.right.sql(dialect="mysql"),
        fields=tuple(dict.fromkeys([*left_fields, *right_fields])),
    )


def _is_bare_column(expression: exp.Expression) -> bool:
    node = expression
    while isinstance(node, exp.Paren):
        node = node.this
    return isinstance(node, exp.Column)


def _resolved_fields(
    expression: exp.Expression,
    base_alias: dict[str, str],
    subquery_outputs: dict[str, dict[str, list[str]]],
) -> list[str]:
    found: list[str] = []
    for column in expression.find_all(exp.Column):
        resolved = _resolve_column(column, base_alias, subquery_outputs)
        found.extend(resolved)
    return list(dict.fromkeys(found))


def _resolve_column(
    column: exp.Column,
    base_alias: dict[str, str],
    subquery_outputs: dict[str, dict[str, list[str]]],
) -> list[str]:
    qualifier = column.table
    name = column.name
    if not name:
        return []
    if not qualifier:
        # Unqualified column in a select that reads a single physical table.
        if len(base_alias) == 1:
            physical = next(iter(base_alias.values()))
            return [f"{physical}.{name}"]
        return []
    physical = base_alias.get(qualifier)
    if physical:
        return [f"{physical}.{name}"]
    outputs = subquery_outputs.get(qualifier)
    if outputs and name in outputs:
        return list(outputs[name])
    return []


def _add_groups(bare: list[_EqJoin], features: _RecordFeatures) -> None:
    grouped: dict[tuple[str, str], list[_EqJoin]] = defaultdict(list)
    for join in bare:
        tables = tuple(sorted((_table_of(join.left), _table_of(join.right))))
        grouped[tables].append(join)
    for tables, joins in grouped.items():
        if len(joins) < 2:
            continue
        predicates = tuple(
            sorted(
                (join.identity() for join in joins),
                key=lambda item: (item[0], item[1]),
            )
        )
        features.join_groups.append(_JoinGroup(tables=tables, predicates=predicates))


def _extract_formulas(
    select: exp.Select,
    base_alias: dict[str, str],
    subquery_outputs: dict[str, dict[str, list[str]]],
    features: _RecordFeatures,
    *,
    nested: bool,
) -> None:
    for expression in select.expressions:
        if not isinstance(expression, exp.Alias):
            continue
        if _is_bare_column(expression.this):
            continue
        alias = expression.alias
        if not alias:
            continue
        formula = expression.this.sql(dialect="mysql")
        fields = tuple(_resolved_fields(expression.this, base_alias, subquery_outputs))
        features.named_formulas.append(
            _Formula(alias=alias, formula=formula, fields=fields, nested=nested)
        )


def _root_select(tree: exp.Expression) -> exp.Select | None:
    found = tree.find(exp.Select)
    return found if isinstance(found, exp.Select) else None


def _table_of(fq: str) -> str:
    return fq.split(".", 1)[0]


def _dedupe_record(features: _RecordFeatures) -> None:
    features.equality_joins = _unique(features.equality_joins, lambda item: item.identity())
    features.transform_joins = _unique(features.transform_joins, lambda item: item.identity())
    features.join_groups = _unique(features.join_groups, lambda item: item.identity())
    features.named_formulas = _unique(features.named_formulas, lambda item: item.identity())


def _unique(items: list[Any], key_fn: Any) -> list[Any]:
    seen: set[Any] = set()
    kept: list[Any] = []
    for item in items:
        key = key_fn(item)
        if key in seen:
            continue
        seen.add(key)
        kept.append(item)
    return kept


def _require_source(source: str) -> str:
    if source not in _SOURCES:
        allowed = ", ".join(sorted(_SOURCES))
        raise ValueError(f"unknown sql source {source!r}; expected one of {allowed}")
    return source


def _require_record_id(record_id: str) -> None:
    if not str(record_id or "").strip():
        raise ValueError("sql record_id is required")


def _index_records(source: str, records: Sequence[SqlRecord]) -> dict[tuple[str, str], SqlRecord]:
    indexed: dict[tuple[str, str], SqlRecord] = {}
    for record in records:
        if record.source != source:
            raise ValueError(
                f"replace_source({source}) received record source {record.source!r}"
            )
        _require_record_id(record.record_id)
        indexed[record.key()] = record
    return indexed


def _record_ref(record: SqlRecord) -> dict[str, str]:
    return {"source": record.source, "record_id": record.record_id}


def _error_row(features: _RecordFeatures) -> dict[str, str]:
    return {
        "source": features.record.source,
        "record_id": features.record.record_id,
        "error": features.parse_error,
    }


def _merge_support(
    bucket: dict[Any, dict[str, Any]],
    identity: Any,
    payload: dict[str, Any],
    ref: dict[str, str],
) -> None:
    slot = bucket.get(identity)
    if slot is None:
        slot = {**payload, "support": 0, "records": []}
        bucket[identity] = slot
    if ref not in slot["records"]:
        slot["records"].append(ref)
        slot["support"] = len(slot["records"])


def _sorted_features(bucket: dict[Any, dict[str, Any]]) -> list[dict[str, Any]]:
    rows = list(bucket.values())
    rows.sort(key=lambda row: (-int(row["support"]), str(row)))
    return rows


def proposed_edges(aggregated: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Turn aggregated SQL features into proposed join/formula records.

    Does not write wiki pages. Downstream init / manual / user-accepted
    ingest can pass ``corpus.aggregated()`` here.
    """
    edges: list[dict[str, Any]] = []
    for row in aggregated.get("equality_joins") or []:
        edges.append(
            {
                "type": "EQUI_JOIN",
                "left": row.get("left"),
                "right": row.get("right"),
                "trust": "proposed",
                "source": "sql_corpus",
                "join_role": row.get("join_role"),
                "evidence": f"sql_corpus:support={row.get('support')}",
                "records": list(row.get("records") or []),
            }
        )
    for row in aggregated.get("transform_joins") or []:
        edges.append(
            {
                "type": "TRANSFORM_JOIN",
                "left_sql": row.get("left_sql"),
                "right_sql": row.get("right_sql"),
                "fields": list(row.get("fields") or []),
                "trust": "proposed",
                "source": "sql_corpus",
                "evidence": f"sql_corpus:support={row.get('support')}",
                "records": list(row.get("records") or []),
            }
        )
    for row in aggregated.get("join_groups") or []:
        edges.append(
            {
                "type": "MULTI_COLUMN_JOIN",
                "tables": list(row.get("tables") or []),
                "predicates": list(row.get("predicates") or []),
                "trust": "proposed",
                "source": "sql_corpus",
                "evidence": f"sql_corpus:support={row.get('support')}",
                "records": list(row.get("records") or []),
            }
        )
    for row in aggregated.get("named_formulas") or []:
        edges.append(
            {
                "type": "NAMED_FORMULA",
                "alias": row.get("alias"),
                "formula": row.get("formula"),
                "fields": list(row.get("fields") or []),
                "trust": "proposed",
                "source": "sql_corpus",
                "evidence": f"sql_corpus:support={row.get('support')}",
                "records": list(row.get("records") or []),
            }
        )
    return edges


def _counts_by_source(items: dict[tuple[str, str], _RecordFeatures]) -> dict[str, int]:
    counts: dict[str, int] = {source: 0 for source in sorted(_SOURCES)}
    for source, _record_id in items:
        counts[source] = counts.get(source, 0) + 1
    return counts
