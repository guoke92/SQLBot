"""In-turn SQL revisions. Delivery truth is ``SqlWorkspace.delivered``."""

from __future__ import annotations

import hashlib
import re
from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from typing import Any, Literal, Self

from pydantic import BaseModel, ConfigDict, Field

Origin = Literal["model", "patch", "inherit"]
RevisionStatus = Literal["draft", "compiled", "executed", "delivered", "failed"]

_REV_RE = re.compile(r"^r(\d+)$")


def normalize_sql(sql: str) -> str:
    return " ".join(str(sql or "").split()).strip()


def hash_sql(sql: str) -> str:
    return hashlib.sha256(normalize_sql(sql).lower().encode("utf-8")).hexdigest()[:16]


def tables_from_sql(sql: str, *, dialect: str | None = None) -> list[str]:
    text = str(sql or "").strip()
    if not text:
        return []
    try:
        import sqlglot
        from sqlglot import exp

        tree = sqlglot.parse_one(text, read=dialect or "mysql")
        names = {
            str(table.name)
            for table in tree.find_all(exp.Table)
            if getattr(table, "name", None)
        }
        return sorted(names)
    except Exception:
        return []


class SqlRevision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rev: str
    ds_id: int | None = None
    sql: str
    sql_hash: str = ""
    tables: list[str] = Field(default_factory=list)
    parent_rev: str | None = None
    origin: Origin = "model"
    status: RevisionStatus = "draft"
    dataset_id: str | None = None
    result_title: str = ""
    row_count: int | None = None
    fields: list[str] = Field(default_factory=list)
    truncated: bool = False
    display_limit: int | None = None
    executed_at: datetime | None = None

    def model_post_init(self, __context: Any) -> None:
        if not self.sql_hash and self.sql:
            object.__setattr__(self, "sql_hash", hash_sql(self.sql))


class SqlWorkspace(BaseModel):
    model_config = ConfigDict(extra="forbid")

    revisions: dict[str, SqlRevision] = Field(default_factory=dict)
    current: str | None = None
    delivered: str | None = None
    seq: int = 0

    @classmethod
    def from_state(cls, state: Mapping[str, Any] | None) -> Self:
        raw = (state or {}).get("sql_workspace") if state is not None else None
        if isinstance(raw, SqlWorkspace):
            return raw
        if isinstance(raw, Mapping):
            try:
                return cls.model_validate(raw)
            except Exception:
                pass
        return cls()

    def next_rev(self) -> str:
        self.seq += 1
        return f"r{self.seq}"

    def get(self, rev: str | None) -> SqlRevision | None:
        key = str(rev or "").strip()
        if not key:
            return None
        return self.revisions.get(key)

    def resolve(self, ref: str | None) -> SqlRevision | None:
        """Resolve ``active`` / ``rN`` / ``dataset_id`` to a revision."""
        token = str(ref or "active").strip() or "active"
        if token in {"active", "*"}:
            if self.current:
                return self.get(self.current)
            if self.delivered:
                return self.get(self.delivered)
            return None
        found = self.get(token)
        if found is not None:
            return found
        for item in self.revisions.values():
            if item.dataset_id and item.dataset_id == token:
                return item
        return None

    def resolve_sql(self, ref: str | None) -> str:
        item = self.resolve(ref)
        return str(item.sql).strip() if item is not None else ""

    def find_by_hash(self, ds_id: int | None, sql_hash: str) -> SqlRevision | None:
        needle = str(sql_hash or "").strip()
        if not needle:
            return None
        for item in self.revisions.values():
            if item.sql_hash == needle and (ds_id is None or item.ds_id == ds_id):
                return item
        return None

    def add_revision(
        self,
        sql: str,
        *,
        origin: Origin = "model",
        status: RevisionStatus = "draft",
        parent_rev: str | None = None,
        dataset_id: str | None = None,
        ds_id: int | None = None,
        result_title: str = "",
        row_count: int | None = None,
        fields: Sequence[str] | None = None,
        truncated: bool = False,
        display_limit: int | None = None,
        rev: str | None = None,
        dialect: str | None = None,
    ) -> SqlRevision:
        text = str(sql or "").strip()
        digest = hash_sql(text)
        existing = self.find_by_hash(ds_id, digest)
        if existing is not None and origin != "patch":
            if dataset_id:
                existing.dataset_id = dataset_id
            if status == "delivered" or (
                status == "executed" and existing.status in {"draft", "compiled"}
            ):
                existing.status = status
            if row_count is not None:
                existing.row_count = row_count
            if fields:
                existing.fields = list(fields)
            if result_title:
                existing.result_title = result_title
            if truncated:
                existing.truncated = True
            if display_limit is not None:
                existing.display_limit = display_limit
            self.current = existing.rev
            return existing
        key = str(rev or "").strip() or self.next_rev()
        if key in self.revisions:
            key = self.next_rev()
        item = SqlRevision(
            rev=key,
            ds_id=ds_id,
            sql=text,
            sql_hash=digest,
            tables=tables_from_sql(text, dialect=dialect),
            parent_rev=parent_rev,
            origin=origin,
            status=status,
            dataset_id=dataset_id,
            result_title=result_title,
            row_count=row_count,
            fields=list(fields or []),
            truncated=truncated,
            display_limit=display_limit,
            executed_at=datetime.now(timezone.utc)
            if status in {"executed", "delivered"}
            else None,
        )
        self.revisions[key] = item
        self.current = key
        return item

    def apply_patch(
        self,
        base_ref: str,
        new_sql: str,
        *,
        ds_id: int | None = None,
        dialect: str | None = None,
    ) -> SqlRevision:
        parent = self.resolve(base_ref)
        parent_rev = parent.rev if parent is not None else None
        return self.add_revision(
            new_sql,
            origin="patch",
            status="compiled",
            parent_rev=parent_rev,
            ds_id=ds_id if ds_id is not None else (parent.ds_id if parent else None),
            dialect=dialect,
        )

    def mark_executed(
        self,
        rev: str,
        *,
        dataset_id: str | None = None,
        row_count: int | None = None,
        fields: Sequence[str] | None = None,
        result_title: str = "",
        purpose: Literal["probe", "delivery"] = "delivery",
        truncated: bool = False,
        display_limit: int | None = None,
    ) -> SqlRevision | None:
        item = self.get(rev)
        if item is None:
            return None
        item.status = "delivered" if purpose == "delivery" else "executed"
        item.executed_at = datetime.now(timezone.utc)
        if dataset_id:
            item.dataset_id = dataset_id
        if row_count is not None:
            item.row_count = row_count
        if fields:
            item.fields = list(fields)
        if result_title:
            item.result_title = result_title
        if truncated:
            item.truncated = True
        if display_limit is not None:
            item.display_limit = display_limit
        self.current = item.rev
        if purpose == "delivery":
            self.delivered = item.rev
        return item

    def inherit_dataset(
        self,
        dataset: Mapping[str, Any],
        *,
        ds_id: int | None = None,
        dialect: str | None = None,
    ) -> SqlRevision | None:
        sql = str(dataset.get("sql") or "").strip()
        if not sql:
            return None
        rev = str(dataset.get("rev") or "").strip() or None
        raw_limit = dataset.get("limit")
        if raw_limit is None:
            raw_limit = dataset.get("display_limit")
        try:
            display_limit = int(raw_limit) if raw_limit is not None else None
        except (TypeError, ValueError):
            display_limit = None
        item = self.add_revision(
            sql,
            origin="inherit",
            status="executed",
            dataset_id=str(dataset.get("dataset_id") or "") or None,
            ds_id=ds_id,
            result_title=str(dataset.get("title") or dataset.get("brief") or ""),
            row_count=dataset.get("row_count")
            if isinstance(dataset.get("row_count"), int)
            else None,
            fields=[str(f) for f in (dataset.get("fields") or [])],
            truncated=bool(dataset.get("truncated")),
            display_limit=display_limit,
            rev=rev,
            dialect=dialect,
        )
        self.current = item.rev
        return item

    def render_index(self) -> str:
        if not self.revisions:
            return ""
        lines: list[str] = []
        order = sorted(
            self.revisions.values(),
            key=lambda item: _rev_order(item.rev),
        )
        for item in order:
            marks: list[str] = []
            if item.rev == self.delivered:
                marks.append("已交付")
            elif item.status == "executed":
                marks.append("已执行")
            elif item.status == "compiled":
                marks.append("草稿")
            elif item.status == "failed":
                marks.append("失败")
            else:
                marks.append(item.status)
            tag = " ".join(f"[{m}]" for m in marks)
            bits = [f"{item.rev} {tag}"]
            if item.result_title:
                bits.append(item.result_title)
            if item.tables:
                bits.append(f"{len(item.tables)} 表")
            if item.row_count is not None:
                bits.append(f"{item.row_count} 行")
            if item.truncated:
                if item.display_limit is not None:
                    bits.append(f"截断前 {item.display_limit}")
                else:
                    bits.append("已截断")
            if item.fields:
                bits.append("fields=" + ",".join(item.fields[:8]))
            if item.dataset_id:
                bits.append(f"dataset={item.dataset_id}")
            if item.parent_rev:
                bits.append(f"← {item.origin}({item.parent_rev})")
            lines.append(" · ".join(bits))
        return "\n".join(lines)

    def truncation(self) -> tuple[bool, int | None]:
        """Display-window truncation of the sealed delivery revision."""
        if not self.delivered:
            return False, None
        item = self.get(self.delivered)
        if item is None or not item.truncated:
            return False, None
        return True, item.display_limit


def _rev_order(rev: str) -> int:
    match = _REV_RE.match(rev)
    return int(match.group(1)) if match else 0
