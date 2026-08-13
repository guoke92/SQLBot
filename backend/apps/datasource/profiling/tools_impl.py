"""Concrete mining tool operations (deterministic + probes + writeback)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Any

from sqlmodel import Session, select

from apps.conversation.tooling import tool_failure, tool_success
from apps.datasource.models.datasource import CoreDatasource, CoreField, CoreTable
from apps.datasource.profiling.models import (
    FieldRelation,
    RelationKind,
    RelationSource,
)
from apps.datasource.profiling.relation_candidates import admit_relation_candidate
from apps.datasource.profiling.service import (
    build_profile_brief,
    decide_field_relation,
    get_published_relations,
)
from apps.protocol.registry import get_protocol_for_ds


@dataclass
class MiningContext:
    oid: int
    ds_id: int
    table_id: int | None
    run_mode: str


class MiningOps:
    def __init__(self, ctx: MiningContext) -> None:
        self.ctx = ctx

    def _resolve_table_id(self, table_id: int | None) -> int:
        tid = table_id if table_id is not None else self.ctx.table_id
        if tid is None:
            raise ValueError("table_id is required")
        return int(tid)

    def list_tables_brief(self, session: Session) -> dict[str, Any]:
        brief = build_profile_brief(session, ds_id=self.ctx.ds_id)
        return tool_success("listed tables", brief)

    def get_profile_brief(
        self, session: Session, *, table_id: int | None = None
    ) -> dict[str, Any]:
        tids = None
        if table_id is not None or self.ctx.table_id is not None:
            tids = [self._resolve_table_id(table_id)]
        brief = build_profile_brief(session, ds_id=self.ctx.ds_id, table_ids=tids)
        return tool_success("profile brief", brief)

    def extract_ddl_constraints(
        self, session: Session, *, table_id: int | None = None
    ) -> dict[str, Any]:
        """Read-only PK/FK inspection. CONFIRMED DDL writes belong to facts bootstrap."""
        tid = self._resolve_table_id(table_id)
        ds = session.get(CoreDatasource, self.ctx.ds_id)
        table = session.get(CoreTable, tid)
        if ds is None or table is None:
            return tool_failure("constraints failed", "table not found")
        proto = get_protocol_for_ds(ds)
        table_name = table.table_name
        database_name = table.database_name
        session.expunge(ds)
        session.rollback()
        result = proto.extract_table_constraints(
            ds, resource=table_name, database_name=database_name
        )
        if not result.supported:
            return tool_success("constraints unsupported", result.model_dump())
        return tool_success(
            "constraints extracted (read-only; not published)",
            {
                "primary_keys": result.primary_keys,
                "unique_columns": result.unique_columns,
                "foreign_keys": result.foreign_keys,
                "published": False,
            },
        )

    def name_similarity(
        self,
        session: Session,
        *,
        field_ids: list[int],
        limit: int = 20,
    ) -> dict[str, Any]:
        ids = [int(i) for i in field_ids][:80]
        if len(ids) < 2:
            fields = session.exec(
                select(CoreField).where(
                    CoreField.ds_id == self.ctx.ds_id,
                    CoreField.checked == True,  # noqa: E712
                )
            ).all()
            if self.ctx.table_id is not None:
                fields = [
                    f for f in fields if int(f.table_id) == int(self.ctx.table_id)
                ]
            ids = [int(f.id) for f in fields if f.id is not None][:40]
        rows = session.exec(
            select(CoreField).where(
                CoreField.id.in_(ids),  # type: ignore[arg-type]
                CoreField.ds_id == self.ctx.ds_id,
            )
        ).all()
        by_id = {int(f.id): f for f in rows if f.id is not None}
        pairs: list[tuple[float, int, int, str, str]] = []
        ordered = list(by_id.keys())
        for i, left_id in enumerate(ordered):
            left = by_id[left_id]
            left_norm = _normalize_name(left.field_name)
            for right_id in ordered[i + 1 :]:
                right = by_id[right_id]
                if int(left.table_id) == int(right.table_id):
                    continue
                right_norm = _normalize_name(right.field_name)
                score = SequenceMatcher(None, left_norm, right_norm).ratio()
                if score < 0.72:
                    continue
                pairs.append(
                    (score, left_id, right_id, left.field_name, right.field_name)
                )
        pairs.sort(key=lambda item: item[0], reverse=True)
        payload = [
            {
                "score": round(score, 4),
                "source_field_id": a,
                "target_field_id": b,
                "source_field": an,
                "target_field": bn,
            }
            for score, a, b, an, bn in pairs[: max(1, min(limit, 50))]
        ]
        return tool_success("name similarity ranked", payload)

    def overlap_probe(
        self,
        session: Session,
        *,
        source_field_id: int,
        target_field_id: int,
        sample_size: int = 2000,
    ) -> dict[str, Any]:
        return self._value_probe(
            session,
            source_field_id=source_field_id,
            target_field_id=target_field_id,
            sample_size=sample_size,
            mode="overlap",
        )

    def fanout_probe(
        self,
        session: Session,
        *,
        source_field_id: int,
        target_field_id: int,
        sample_size: int = 2000,
    ) -> dict[str, Any]:
        return self._value_probe(
            session,
            source_field_id=source_field_id,
            target_field_id=target_field_id,
            sample_size=sample_size,
            mode="fanout",
        )

    def _value_probe(
        self,
        session: Session,
        *,
        source_field_id: int,
        target_field_id: int,
        sample_size: int,
        mode: str,
    ) -> dict[str, Any]:
        from apps.db.db import exec_sql

        src = session.get(CoreField, source_field_id)
        dst = session.get(CoreField, target_field_id)
        if src is None or dst is None:
            return tool_failure("probe failed", "field not found")
        if int(src.ds_id) != self.ctx.ds_id or int(dst.ds_id) != self.ctx.ds_id:
            return tool_failure("probe failed", "field outside datasource")
        src_table = session.get(CoreTable, src.table_id)
        dst_table = session.get(CoreTable, dst.table_id)
        ds = session.get(CoreDatasource, self.ctx.ds_id)
        if src_table is None or dst_table is None or ds is None:
            return tool_failure("probe failed", "table/ds missing")
        proto = get_protocol_for_ds(ds)
        bounded = max(100, min(int(sample_size), 5000))
        src_sql = proto.qualify_table(
            ds, src_table.table_name, database_name=src_table.database_name
        )
        dst_sql = proto.qualify_table(
            ds, dst_table.table_name, database_name=dst_table.database_name
        )
        src_col = proto._quote_identifier(src.field_name)
        dst_col = proto._quote_identifier(dst.field_name)

        from apps.datasource.profiling.service import get_active_field_profiles
        from apps.datasource.profiling.soft_signals import (
            inclusion_score,
            key_likelihood,
        )

        src_snap = next(
            (
                p
                for p in get_active_field_profiles(session, table_id=int(src.table_id))
                if int(p.field_id) == int(source_field_id)
            ),
            None,
        )
        dst_snap = next(
            (
                p
                for p in get_active_field_profiles(session, table_id=int(dst.table_id))
                if int(p.field_id) == int(target_field_id)
            ),
            None,
        )
        src_key = key_likelihood(
            distinct_ratio=getattr(src_snap, "distinct_ratio", None),
            null_rate=getattr(src_snap, "null_rate", None),
        )
        dst_key = key_likelihood(
            distinct_ratio=getattr(dst_snap, "distinct_ratio", None),
            null_rate=getattr(dst_snap, "null_rate", None),
        )

        session.expunge(ds)
        session.rollback()

        def _sample(table_sql: str, col_sql: str) -> set[str]:
            if proto.type_key == "sqlServer":
                sql = f"SELECT DISTINCT TOP {bounded} {col_sql} AS v FROM {table_sql} WHERE {col_sql} IS NOT NULL"
            elif proto.type_key == "oracle":
                sql = (
                    f"SELECT DISTINCT {col_sql} AS v FROM {table_sql} "
                    f"WHERE {col_sql} IS NOT NULL FETCH FIRST {bounded} ROWS ONLY"
                )
            else:
                sql = (
                    f"SELECT DISTINCT {col_sql} AS v FROM {table_sql} "
                    f"WHERE {col_sql} IS NOT NULL LIMIT {bounded}"
                )
            raw = exec_sql(ds=ds, sql=sql, origin_column=True)
            values: set[str] = set()
            for row in raw.get("data") or []:
                if not isinstance(row, dict):
                    continue
                value = row.get("v")
                if value is None and row:
                    value = next(iter(row.values()), None)
                if value is not None:
                    values.add(str(value))
            return values

        try:
            left = _sample(src_sql, src_col)
            right = _sample(dst_sql, dst_col)
        except Exception as exc:
            return tool_failure("probe failed", str(exc))

        if not left or not right:
            return tool_success(
                "probe empty",
                {
                    "mode": mode,
                    "source_size": len(left),
                    "target_size": len(right),
                    "intersection": 0,
                    "containment_source_in_target": 0.0,
                    "containment_target_in_source": 0.0,
                    "jaccard": 0.0,
                },
            )
        inter = left & right
        union = left | right
        containment_st = len(inter) / len(left)
        containment_ts = len(inter) / len(right)
        jaccard = len(inter) / len(union) if union else 0.0
        fanout_est = (len(left) / max(len(inter), 1)) if mode == "fanout" else None
        scored = inclusion_score(
            containment_source_in_target=containment_st,
            containment_target_in_source=containment_ts,
            source_key_likelihood=src_key,
            target_key_likelihood=dst_key,
        )
        return tool_success(
            "probe complete",
            {
                "mode": mode,
                "source_field_id": source_field_id,
                "target_field_id": target_field_id,
                "source_size": len(left),
                "target_size": len(right),
                "intersection": len(inter),
                "containment_source_in_target": round(containment_st, 4),
                "containment_target_in_source": round(containment_ts, 4),
                "jaccard": round(jaccard, 4),
                "fanout_estimate": fanout_est,
                "source_key_likelihood": src_key,
                "target_key_likelihood": dst_key,
                **scored,
            },
        )

    def upsert_relation_candidate(
        self,
        session: Session,
        *,
        source_field_id: int,
        target_field_id: int,
        kind: str = "EQUI_JOIN",
        confidence: float | None = None,
        evidence: dict[str, Any] | None = None,
        cardinality: str | None = None,
        source: str | None = None,
    ) -> dict[str, Any]:
        src = session.get(CoreField, source_field_id)
        dst = session.get(CoreField, target_field_id)
        if src is None or dst is None:
            return tool_failure("upsert failed", "field not found")
        if int(src.ds_id) != self.ctx.ds_id or int(dst.ds_id) != self.ctx.ds_id:
            return tool_failure("upsert failed", "field outside datasource")
        kind_value = (kind or RelationKind.EQUI_JOIN.value).upper()
        source_value = (
            source or RelationSource.PROBE.value
        ).strip() or RelationSource.PROBE.value
        # Hard gate (matches agent prompt): EQUI_JOIN must carry probe approval.
        # query_log mining writes FieldRelation directly and does not use this tool.
        if kind_value == RelationKind.EQUI_JOIN.value:
            if (
                not isinstance(evidence, dict)
                or evidence.get("suggest_candidate") is not True
            ):
                return tool_failure(
                    "upsert rejected",
                    "EQUI_JOIN requires evidence.suggest_candidate=true from a probe",
                )
        row, action = admit_relation_candidate(
            session,
            oid=self.ctx.oid,
            ds_id=self.ctx.ds_id,
            source_field_id=int(source_field_id),
            target_field_id=int(target_field_id),
            kind=kind_value,
            confidence=confidence,
            evidence=evidence,
            cardinality=cardinality,
            source=source_value,
        )
        session.commit()
        return tool_success(
            f"relation candidate {action}",
            {"id": row.id, "status": row.status},
        )

    def list_relations(self, session: Session, *, status: str) -> dict[str, Any]:
        rows = get_published_relations(
            session,
            ds_id=self.ctx.ds_id,
            statuses=[status],
        )
        payload = [
            {
                "id": r.id,
                "kind": r.kind,
                "status": r.status,
                "source": r.source,
                "confidence": r.confidence,
                "source_field_id": r.source_field_id,
                "target_field_id": r.target_field_id,
            }
            for r in rows
        ]
        return tool_success(f"listed {status} relations", payload)

    def set_relation_status(
        self, session: Session, relation_id: int, status: str
    ) -> dict[str, Any]:
        row = session.get(FieldRelation, relation_id)
        if row is None or int(row.ds_id) != self.ctx.ds_id:
            return tool_failure("relation update failed", "not found")
        try:
            updated = decide_field_relation(
                session, relation_id=relation_id, status=status
            )
        except ValueError as exc:
            return tool_failure("relation update failed", str(exc))
        except LookupError as exc:
            return tool_failure("relation update failed", str(exc))
        return tool_success(
            f"relation {updated.status}",
            {"id": updated.id, "status": updated.status},
        )

    def get_samples(
        self, session: Session, *, table_id: int | None = None, limit: int = 5
    ) -> dict[str, Any]:
        tid = self._resolve_table_id(table_id)
        ds = session.get(CoreDatasource, self.ctx.ds_id)
        table = session.get(CoreTable, tid)
        if ds is None or table is None:
            return tool_failure("sample failed", "table not found")
        fields = session.exec(
            select(CoreField).where(
                CoreField.table_id == tid,
                CoreField.checked == True,  # noqa: E712
            )
        ).all()
        names = [f.field_name for f in fields if f.field_name][:30]
        if not names:
            return tool_failure("sample failed", "no fields")
        proto = get_protocol_for_ds(ds)
        session.expunge(ds)
        session.rollback()
        try:
            # preview expects a user/session for permissions in some paths; use exec via protocol preview
            from apps.db.db import exec_sql

            cols = ", ".join(proto._quote_identifier(n) for n in names)
            table_sql = proto.qualify_table(
                ds, table.table_name, database_name=table.database_name
            )
            bounded = max(1, min(int(limit), 20))
            if proto.type_key == "sqlServer":
                sql = f"SELECT TOP {bounded} {cols} FROM {table_sql}"
            elif proto.type_key == "oracle":
                sql = f"SELECT {cols} FROM {table_sql} FETCH FIRST {bounded} ROWS ONLY"
            else:
                sql = f"SELECT {cols} FROM {table_sql} LIMIT {bounded}"
            raw = exec_sql(ds=ds, sql=sql, origin_column=True)
            rows = []
            for row in (raw.get("data") or [])[:bounded]:
                if not isinstance(row, dict):
                    continue
                # Redact long values for LLM safety.
                rows.append(
                    {
                        k: (str(v)[:80] if v is not None else None)
                        for k, v in row.items()
                    }
                )
            return tool_success("samples", {"table_id": tid, "rows": rows})
        except Exception as exc:
            return tool_failure("sample failed", str(exc))

    def cooccurrence_probe(
        self,
        session: Session,
        *,
        source_field_id: int,
        target_field_id: int,
        sample_size: int = 2000,
    ) -> dict[str, Any]:
        """Estimate co-non-null rate for intra-table binding hints."""
        src = session.get(CoreField, source_field_id)
        dst = session.get(CoreField, target_field_id)
        if src is None or dst is None:
            return tool_failure("cooccurrence failed", "field not found")
        if int(src.table_id) != int(dst.table_id):
            return tool_failure(
                "cooccurrence failed", "fields must belong to the same table"
            )
        if int(src.ds_id) != self.ctx.ds_id:
            return tool_failure("cooccurrence failed", "field outside datasource")
        table = session.get(CoreTable, src.table_id)
        ds = session.get(CoreDatasource, self.ctx.ds_id)
        if table is None or ds is None:
            return tool_failure("cooccurrence failed", "table/ds missing")
        proto = get_protocol_for_ds(ds)
        bounded = max(100, min(int(sample_size), 5000))
        table_sql = proto.qualify_table(
            ds, table.table_name, database_name=table.database_name
        )
        a = proto._quote_identifier(src.field_name)
        b = proto._quote_identifier(dst.field_name)
        session.expunge(ds)
        session.rollback()
        if proto.type_key == "sqlServer":
            sample = f"(SELECT TOP {bounded} {a} AS a, {b} AS b FROM {table_sql}) s"
        elif proto.type_key == "oracle":
            sample = (
                f"(SELECT {a} AS a, {b} AS b FROM {table_sql} "
                f"FETCH FIRST {bounded} ROWS ONLY) s"
            )
        else:
            sample = f"(SELECT {a} AS a, {b} AS b FROM {table_sql} LIMIT {bounded}) s"
        sql = (
            f"SELECT COUNT(*) AS n, "
            f"SUM(CASE WHEN a IS NOT NULL AND b IS NOT NULL THEN 1 ELSE 0 END) AS both_nn, "
            f"SUM(CASE WHEN a IS NOT NULL THEN 1 ELSE 0 END) AS a_nn, "
            f"SUM(CASE WHEN b IS NOT NULL THEN 1 ELSE 0 END) AS b_nn "
            f"FROM {sample}"
        )
        try:
            from apps.db.db import exec_sql

            raw = exec_sql(ds=ds, sql=sql, origin_column=True)
            row = (raw.get("data") or [{}])[0]
            n = int(row.get("n") or 0)
            both = int(row.get("both_nn") or 0)
            a_nn = int(row.get("a_nn") or 0)
            b_nn = int(row.get("b_nn") or 0)
            return tool_success(
                "cooccurrence",
                {
                    "sample_size": n,
                    "both_non_null": both,
                    "source_non_null": a_nn,
                    "target_non_null": b_nn,
                    "cooccurrence_rate": round(both / n, 4) if n else 0.0,
                },
            )
        except Exception as exc:
            return tool_failure("cooccurrence failed", str(exc))

    def refresh_dictionary_for_table(
        self, session: Session, *, table_id: int | None = None
    ) -> dict[str, Any]:
        tid = self._resolve_table_id(table_id)
        from apps.dictionary.models import DictionaryFieldConfig
        from apps.dictionary.service import refresh_config

        configs = session.exec(
            select(DictionaryFieldConfig).where(
                DictionaryFieldConfig.ds_id == self.ctx.ds_id,
                DictionaryFieldConfig.table_id == tid,
                DictionaryFieldConfig.enabled == True,  # noqa: E712
            )
        ).all()
        refreshed = []
        errors = []
        for cfg in configs:
            if cfg.id is None:
                continue
            try:
                row = refresh_config(session, oid=self.ctx.oid, config_id=int(cfg.id))
                refreshed.append({"config_id": row.id, "status": row.status})
            except Exception as exc:
                errors.append({"config_id": cfg.id, "error": str(exc)[:200]})
        return tool_success(
            "dictionary refresh",
            {"refreshed": refreshed, "errors": errors},
        )

    def compute_ai_priority(
        self, session: Session, *, table_id: int | None = None
    ) -> dict[str, Any]:
        from apps.datasource.profiling.priority import is_high_value_table
        from apps.datasource.profiling.service import get_active_field_profiles
        from apps.datasource.profiling.soft_signals import (
            derive_field_soft_signals,
            infer_table_role,
        )

        tid = self._resolve_table_id(table_id)
        table = session.get(CoreTable, tid)
        if table is None or int(table.ds_id) != self.ctx.ds_id:
            return tool_failure("priority failed", "table not found")
        fields = session.exec(select(CoreField).where(CoreField.table_id == tid)).all()
        field_count = len(fields)
        high = is_high_value_table(table, field_count=field_count)
        profiles = {
            int(p.field_id): p for p in get_active_field_profiles(session, table_id=tid)
        }
        high_keys = 0
        for field in fields:
            if field.id is None:
                continue
            snap = profiles.get(int(field.id))
            signals = derive_field_soft_signals(
                field_name=field.field_name or "",
                field_type=field.field_type,
                null_rate=getattr(snap, "null_rate", None),
                distinct_ratio=getattr(snap, "distinct_ratio", None),
                approx_distinct=getattr(snap, "approx_distinct", None),
                min_value=getattr(snap, "min_value", None),
                max_value=getattr(snap, "max_value", None),
            )
            if signals.get("key_likelihood") == "high":
                high_keys += 1
        role = infer_table_role(
            approx_rows=table.approx_rows,
            field_count=field_count,
            high_key_fields=high_keys,
        )
        return tool_success(
            "priority",
            {
                "table_id": tid,
                "high_value": high,
                "recommend_deep": high,
                "approx_rows": table.approx_rows,
                "field_count": field_count,
                **role,
            },
        )

    def mine_query_log_joins(
        self,
        session: Session,
        *,
        min_count: int = 2,
        sql_limit: int = 200,
    ) -> dict[str, Any]:
        from apps.datasource.profiling.query_log_joins import (
            mine_query_log_join_candidates,
        )

        try:
            result = mine_query_log_join_candidates(
                session,
                ds_id=self.ctx.ds_id,
                oid=self.ctx.oid,
                min_count=min_count,
                sql_limit=sql_limit,
                upsert=True,
            )
        except Exception as exc:
            return tool_failure("query_log mine failed", str(exc))
        return tool_success("query_log joins mined", result)

    def formula_probe(
        self,
        session: Session,
        *,
        result_field_id: int,
        left_field_id: int,
        right_field_id: int | None = None,
        sample_size: int = 200,
    ) -> dict[str, Any]:
        """Heuristic numeric formula checks (sum/product/diff) on sample rows."""
        result = session.get(CoreField, result_field_id)
        left = session.get(CoreField, left_field_id)
        right = session.get(CoreField, right_field_id) if right_field_id else None
        if result is None or left is None:
            return tool_failure("formula probe failed", "field not found")
        if int(result.ds_id) != self.ctx.ds_id or int(left.ds_id) != self.ctx.ds_id:
            return tool_failure("formula probe failed", "field outside datasource")
        if int(result.table_id) != int(left.table_id):
            return tool_failure("formula probe failed", "fields must share a table")
        if right is not None and int(right.table_id) != int(result.table_id):
            return tool_failure("formula probe failed", "fields must share a table")
        table = session.get(CoreTable, result.table_id)
        ds = session.get(CoreDatasource, self.ctx.ds_id)
        if table is None or ds is None:
            return tool_failure("formula probe failed", "table/ds missing")
        proto = get_protocol_for_ds(ds)
        names = [result.field_name, left.field_name]
        if right is not None:
            names.append(right.field_name)
        cols = ", ".join(proto._quote_identifier(n) for n in names if n)
        table_sql = proto.qualify_table(
            ds, table.table_name, database_name=table.database_name
        )
        bounded = max(20, min(int(sample_size), 500))
        session.expunge(ds)
        session.rollback()
        if proto.type_key == "sqlServer":
            sql = f"SELECT TOP {bounded} {cols} FROM {table_sql}"
        elif proto.type_key == "oracle":
            sql = f"SELECT {cols} FROM {table_sql} FETCH FIRST {bounded} ROWS ONLY"
        else:
            sql = f"SELECT {cols} FROM {table_sql} LIMIT {bounded}"
        try:
            from apps.db.db import exec_sql

            raw = exec_sql(ds=ds, sql=sql, origin_column=True)
        except Exception as exc:
            return tool_failure("formula probe failed", str(exc))

        def _num(value: Any) -> float | None:
            if value is None:
                return None
            try:
                return float(value)
            except (TypeError, ValueError):
                return None

        tallies = {"sum": 0, "product": 0, "diff": 0, "ratio": 0, "rows": 0}
        for row in raw.get("data") or []:
            if not isinstance(row, dict):
                continue
            # Column keys may be bare names or aliased.
            vals = list(row.values())
            if len(vals) < 2:
                continue
            r_v = _num(vals[0])
            l_v = _num(vals[1])
            right_v = _num(vals[2]) if right is not None and len(vals) > 2 else None
            if r_v is None or l_v is None:
                continue
            tallies["rows"] += 1
            tol = max(1e-6, abs(r_v) * 0.01)
            if right_v is None:
                if abs(r_v - l_v) <= tol:
                    tallies["ratio"] += 1
                continue
            if abs(r_v - (l_v + right_v)) <= tol:
                tallies["sum"] += 1
            if abs(r_v - (l_v * right_v)) <= tol:
                tallies["product"] += 1
            if abs(r_v - (l_v - right_v)) <= tol:
                tallies["diff"] += 1
            if right_v != 0 and abs(r_v - (l_v / right_v)) <= tol:
                tallies["ratio"] += 1

        n = tallies["rows"] or 1
        rates = {k: round(v / n, 4) for k, v in tallies.items() if k != "rows"}
        best = max(rates.items(), key=lambda item: item[1]) if rates else ("none", 0.0)
        return tool_success(
            "formula probe",
            {
                "result_field_id": result_field_id,
                "left_field_id": left_field_id,
                "right_field_id": right_field_id,
                "sample_rows": tallies["rows"],
                "match_rates": rates,
                "best_op": best[0],
                "best_rate": best[1],
            },
        )

    def hierarchy_probe(
        self,
        session: Session,
        *,
        parent_field_id: int,
        child_field_id: int,
        sample_size: int = 500,
    ) -> dict[str, Any]:
        """Probe path/prefix hierarchy between string-like fields (same table)."""
        parent = session.get(CoreField, parent_field_id)
        child = session.get(CoreField, child_field_id)
        if parent is None or child is None:
            return tool_failure("hierarchy probe failed", "field not found")
        if int(parent.table_id) != int(child.table_id):
            return tool_failure(
                "hierarchy probe failed", "fields must belong to the same table"
            )
        if int(parent.ds_id) != self.ctx.ds_id:
            return tool_failure("hierarchy probe failed", "field outside datasource")
        table = session.get(CoreTable, parent.table_id)
        ds = session.get(CoreDatasource, self.ctx.ds_id)
        if table is None or ds is None:
            return tool_failure("hierarchy probe failed", "table/ds missing")
        proto = get_protocol_for_ds(ds)
        a = proto._quote_identifier(parent.field_name)
        b = proto._quote_identifier(child.field_name)
        table_sql = proto.qualify_table(
            ds, table.table_name, database_name=table.database_name
        )
        bounded = max(50, min(int(sample_size), 2000))
        session.expunge(ds)
        session.rollback()
        if proto.type_key == "sqlServer":
            sql = f"SELECT TOP {bounded} {a} AS p, {b} AS c FROM {table_sql}"
        elif proto.type_key == "oracle":
            sql = (
                f"SELECT {a} AS p, {b} AS c FROM {table_sql} "
                f"FETCH FIRST {bounded} ROWS ONLY"
            )
        else:
            sql = f"SELECT {a} AS p, {b} AS c FROM {table_sql} LIMIT {bounded}"
        try:
            from apps.db.db import exec_sql

            raw = exec_sql(ds=ds, sql=sql, origin_column=True)
        except Exception as exc:
            return tool_failure("hierarchy probe failed", str(exc))

        rows = 0
        prefix_hits = 0
        path_hits = 0
        for row in raw.get("data") or []:
            if not isinstance(row, dict):
                continue
            p = row.get("p")
            c = row.get("c")
            if p is None and c is None and row:
                vals = list(row.values())
                p = vals[0] if vals else None
                c = vals[1] if len(vals) > 1 else None
            if p is None or c is None:
                continue
            ps, cs = str(p).strip(), str(c).strip()
            if not ps or not cs:
                continue
            rows += 1
            if cs.startswith(ps) and cs != ps:
                prefix_hits += 1
            if ps in cs.split("/") or ps in cs.split("."):
                path_hits += 1

        rate_prefix = round(prefix_hits / rows, 4) if rows else 0.0
        rate_path = round(path_hits / rows, 4) if rows else 0.0
        return tool_success(
            "hierarchy probe",
            {
                "parent_field_id": parent_field_id,
                "child_field_id": child_field_id,
                "sample_rows": rows,
                "prefix_rate": rate_prefix,
                "path_segment_rate": rate_path,
                "suggest_candidate": max(rate_prefix, rate_path) >= 0.6,
            },
        )

    def upsert_binding_candidate(
        self,
        session: Session,
        *,
        source_field_id: int,
        target_field_id: int,
        confidence: float | None = None,
        evidence: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return self.upsert_relation_candidate(
            session,
            source_field_id=source_field_id,
            target_field_id=target_field_id,
            kind=RelationKind.BINDING.value,
            confidence=confidence,
            evidence=evidence,
            cardinality="1:1",
        )

    def draft_field_description(
        self,
        session: Session,
        *,
        field_id: int,
        description: str,
        apply: bool = False,
        force: bool = False,
        allow_apply: bool = False,
    ) -> dict[str, Any]:
        field = session.get(CoreField, field_id)
        if field is None or int(field.ds_id) != self.ctx.ds_id:
            return tool_failure("draft field description failed", "field not found")
        text = (description or "").strip()[:500]
        if not text:
            return tool_failure("draft field description failed", "empty description")
        if apply and not allow_apply:
            return tool_success(
                "draft field description (not applied — confirm required)",
                {
                    "field_id": field_id,
                    "description": text,
                    "applied": False,
                    "prior_comment": (field.custom_comment or "")[:120],
                },
            )
        applied = False
        prior = (field.custom_comment or "").strip()
        if apply and allow_apply and (force or not prior):
            field.custom_comment = text
            session.add(field)
            session.commit()
            applied = True
            try:
                from common.utils.embedding_threads import run_save_table_embeddings

                run_save_table_embeddings([int(field.table_id)])
            except Exception:
                pass
        return tool_success(
            "draft field description",
            {
                "field_id": field_id,
                "description": text,
                "applied": applied,
                "prior_comment": prior[:120],
            },
        )

    def draft_table_description(
        self,
        session: Session,
        *,
        description: str,
        table_id: int | None = None,
        apply: bool = False,
        force: bool = False,
        allow_apply: bool = False,
    ) -> dict[str, Any]:
        tid = self._resolve_table_id(table_id)
        table = session.get(CoreTable, tid)
        if table is None or int(table.ds_id) != self.ctx.ds_id:
            return tool_failure("draft table description failed", "table not found")
        text = (description or "").strip()[:500]
        if not text:
            return tool_failure("draft table description failed", "empty description")
        if apply and not allow_apply:
            return tool_success(
                "draft table description (not applied — confirm required)",
                {
                    "table_id": tid,
                    "description": text,
                    "applied": False,
                    "prior_comment": (table.custom_comment or "")[:120],
                },
            )
        applied = False
        prior = (table.custom_comment or "").strip()
        if apply and allow_apply and (force or not prior):
            table.custom_comment = text
            session.add(table)
            session.commit()
            applied = True
            try:
                from common.utils.embedding_threads import run_save_table_embeddings

                run_save_table_embeddings([tid])
            except Exception:
                pass
        return tool_success(
            "draft table description",
            {
                "table_id": tid,
                "description": text,
                "applied": applied,
                "prior_comment": prior[:120],
            },
        )


def _normalize_name(name: str) -> str:
    text = (name or "").strip()
    text = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", text)
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = re.sub(r"_(id|key|code|no|num)$", "", text)
    text = re.sub(r"(id|key|code|no|num)$", "", text)
    return text.strip("_")
