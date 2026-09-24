"""Person combo mapping: user_id / wx_id + multi-form names, conflict discard."""

from __future__ import annotations

import re
from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any

from apps.datasource.instance_index.cells import tokenize_cell
from apps.datasource.models.datasource import CoreDatasource, CoreField, CoreTable
from common.utils.utils import SQLBotLogUtil

VAL_PERSON_ALIAS = "person_alias"
PERSON_TABLE = "__person__"
PERSON_FIELD = "identity"
PERSON_SAMPLE_LIMIT = 400

_CJK_RE = re.compile(r"[\u4e00-\u9fff]")
_LATIN_RE = re.compile(r"[A-Za-z]")
_USER_NAME_RE = re.compile(r"^(.+_user)_name$")
_WXID_RE = re.compile(r"^(.+)_wxid$")

# First-batch paired id/name columns (zip on the same row).
EXPLICIT_PAIRS: tuple[tuple[str, str, str, str], ...] = (
    (
        "tenant_project_approval",
        "solution_manager_id",
        "solution_manager_name",
        "user_id",
    ),
    (
        "tenant_project_approval",
        "initiator_user_id",
        "initiator_user_name",
        "user_id",
    ),
    (
        "tenant_project_approval",
        "wf_last_operator_id",
        "wf_last_operator",
        "user_id",
    ),
    (
        "wechat_project_approval_apply",
        "solution_manager_wxid",
        "solution_manager",
        "wx_id",
    ),
    (
        "tenant_project_approval_flow",
        "approver_user_id",
        "approver_user_name",
        "user_id",
    ),
    (
        "tenant_project_approval_flow_node",
        "operator_user_id",
        "operator_user_name",
        "user_id",
    ),
    (
        "tenant_project_approval_flow_node",
        "transfer_to_user_id",
        "transfer_to_user_name",
        "user_id",
    ),
)

OPERATOR_HUB = "cust_person_info"


def person_source_table_names() -> frozenset[str]:
    return frozenset(
        {OPERATOR_HUB} | {table for table, _id, _name, _kind in EXPLICIT_PAIRS}
    )


@dataclass(frozen=True)
class PersonPairSpec:
    table: str
    id_field: str
    name_field: str
    id_kind: str  # user_id | wx_id


@dataclass
class PersonEvidence:
    table: str
    name_field: str
    id_field: str
    id_kind: str = "user_id"
    user_id: str | None = None
    wx_id: str | None = None
    name_zh: str | None = None
    name_en_raw: str | None = None
    extra_anchors: list[dict[str, str]] = field(default_factory=list)


@dataclass
class PersonRecord:
    user_id: str | None = None
    wx_id: str | None = None
    name_zh: str | None = None
    name_en_fold: str | None = None
    name_en_raw: str | None = None
    anchored_fields: list[dict[str, str]] = field(default_factory=list)

    def person_key(self) -> str:
        return (
            self.user_id
            or self.wx_id
            or self.name_zh
            or self.name_en_fold
            or self.name_en_raw
            or ""
        )

    def aliases(self) -> list[str]:
        values = [
            self.name_zh,
            self.name_en_raw,
            self.name_en_fold,
            self.user_id,
            self.wx_id,
        ]
        out: list[str] = []
        seen: set[str] = set()
        for item in values:
            text = str(item or "").strip()
            if not text or text in seen:
                continue
            seen.add(text)
            out.append(text)
        return out

    def form_count(self) -> int:
        n = 0
        if self.user_id:
            n += 1
        if self.wx_id:
            n += 1
        if self.name_zh:
            n += 1
        if self.name_en_raw or self.name_en_fold:
            n += 1
        return n

    def snapshot(self) -> dict[str, Any]:
        aliases = self.aliases()
        return {
            "person_key": self.person_key(),
            "user_id": self.user_id,
            "wx_id": self.wx_id,
            "name_zh": self.name_zh,
            "name_en_fold": self.name_en_fold,
            "name_en_raw": self.name_en_raw,
            "aliases": aliases,
            "anchored_fields": list(self.anchored_fields),
        }


def pair_specs_for_table(
    table_name: str, field_names: Sequence[str]
) -> list[PersonPairSpec]:
    names = {str(item).strip() for item in field_names if str(item).strip()}
    specs: list[PersonPairSpec] = []
    seen: set[tuple[str, str]] = set()
    for table, id_field, name_field, kind in EXPLICIT_PAIRS:
        if table != table_name:
            continue
        if id_field not in names or name_field not in names:
            continue
        key = (id_field, name_field)
        if key in seen:
            continue
        seen.add(key)
        specs.append(
            PersonPairSpec(
                table=table, id_field=id_field, name_field=name_field, id_kind=kind
            )
        )
    for field_name in sorted(names):
        match = _USER_NAME_RE.match(field_name)
        if match:
            id_field = f"{match.group(1)}_id"
            if id_field in names and (id_field, field_name) not in seen:
                seen.add((id_field, field_name))
                specs.append(
                    PersonPairSpec(
                        table=table_name,
                        id_field=id_field,
                        name_field=field_name,
                        id_kind="user_id",
                    )
                )
            continue
        wx = _WXID_RE.match(field_name)
        if wx:
            stem = wx.group(1)
            name_field = stem if stem in names else f"{stem}_name"
            if name_field in names and (field_name, name_field) not in seen:
                seen.add((field_name, name_field))
                specs.append(
                    PersonPairSpec(
                        table=table_name,
                        id_field=field_name,
                        name_field=name_field,
                        id_kind="wx_id",
                    )
                )
    return specs


def classify_person_name(raw: str) -> tuple[str | None, str | None]:
    """Return (name_zh, name_en_raw)."""
    text = str(raw or "").strip()
    if not text:
        return None, None
    has_cjk = bool(_CJK_RE.search(text))
    has_latin = bool(_LATIN_RE.search(text))
    if has_cjk and not has_latin:
        return text, None
    if has_latin and not has_cjk:
        return None, text
    if has_cjk:
        return text, None
    return None, text


def fold_en_name(raw: str | None) -> str | None:
    text = str(raw or "").strip()
    if not text:
        return None
    return text.casefold()


def evidence_from_row(
    spec: PersonPairSpec, id_cell: str, name_cell: str
) -> list[PersonEvidence]:
    """Zip id/name tokens from one row. Length mismatch → skip and log."""
    ids = tokenize_cell(id_cell) if str(id_cell or "").strip() else []
    names = tokenize_cell(name_cell) if str(name_cell or "").strip() else []
    if ids and names and len(ids) != len(names):
        SQLBotLogUtil.info(
            "person-map zip skip %s.%s/%s lens id=%s name=%s",
            spec.table,
            spec.id_field,
            spec.name_field,
            len(ids),
            len(names),
        )
        return []
    count = max(len(ids), len(names), 1 if (id_cell or name_cell) else 0)
    if not ids and not names:
        if str(name_cell or "").strip():
            names = [str(name_cell).strip()]
        elif str(id_cell or "").strip():
            ids = [str(id_cell).strip()]
        else:
            return []
        count = 1
    rows: list[PersonEvidence] = []
    for index in range(count):
        ident = ids[index] if index < len(ids) else ""
        name = names[index] if index < len(names) else ""
        name_zh, name_en = classify_person_name(name)
        user_id = ident.strip() if spec.id_kind == "user_id" and ident else None
        wx_id = ident.strip() if spec.id_kind == "wx_id" and ident else None
        if not (user_id or wx_id or name_zh or name_en):
            continue
        rows.append(
            PersonEvidence(
                table=spec.table,
                name_field=spec.name_field,
                id_field=spec.id_field,
                id_kind=spec.id_kind,
                user_id=user_id or None,
                wx_id=wx_id or None,
                name_zh=name_zh,
                name_en_raw=name_en,
            )
        )
    return rows


def _name_keys(ev: PersonEvidence) -> list[str]:
    keys: list[str] = []
    if ev.name_zh:
        keys.append(f"zh:{ev.name_zh}")
    folded = fold_en_name(ev.name_en_raw)
    if folded:
        keys.append(f"en:{folded}")
    return keys


def merge_person_records(evidence: Sequence[PersonEvidence]) -> list[PersonRecord]:
    """Drop names that map to ≥2 user_id or ≥2 wx_id; keep combos with ≥2 forms."""
    user_by_name: dict[str, set[str]] = defaultdict(set)
    wx_by_name: dict[str, set[str]] = defaultdict(set)
    for ev in evidence:
        for key in _name_keys(ev):
            if ev.user_id:
                user_by_name[key].add(ev.user_id)
            if ev.wx_id:
                wx_by_name[key].add(ev.wx_id)
    dropped = {key for key, values in user_by_name.items() if len(values) >= 2} | {
        key for key, values in wx_by_name.items() if len(values) >= 2
    }
    kept = [ev for ev in evidence if not (set(_name_keys(ev)) & dropped)]

    clusters: list[PersonRecord] = []

    def _compatible(record: PersonRecord, ev: PersonEvidence) -> bool:
        if ev.user_id and record.user_id and ev.user_id != record.user_id:
            return False
        if ev.wx_id and record.wx_id and ev.wx_id != record.wx_id:
            return False
        if (
            ev.name_zh
            and record.name_zh
            and ev.name_zh != record.name_zh
            and (ev.user_id or record.user_id or ev.wx_id or record.wx_id)
            and not (ev.user_id and record.user_id and ev.user_id == record.user_id)
            and not (ev.wx_id and record.wx_id and ev.wx_id == record.wx_id)
        ):
            if not (ev.user_id == record.user_id or ev.wx_id == record.wx_id):
                return False
        return True

    def _same_cluster(record: PersonRecord, ev: PersonEvidence) -> bool:
        if ev.user_id and record.user_id == ev.user_id:
            return True
        if ev.wx_id and record.wx_id == ev.wx_id:
            return True
        if ev.name_zh and record.name_zh == ev.name_zh:
            return True
        if fold_en_name(ev.name_en_raw) and record.name_en_fold == fold_en_name(
            ev.name_en_raw
        ):
            return True
        return False

    def _apply(record: PersonRecord, ev: PersonEvidence) -> None:
        if ev.user_id and not record.user_id:
            record.user_id = ev.user_id
        if ev.wx_id and not record.wx_id:
            record.wx_id = ev.wx_id
        if ev.name_zh and not record.name_zh:
            record.name_zh = ev.name_zh
        if ev.name_en_raw:
            if not record.name_en_raw:
                record.name_en_raw = ev.name_en_raw
            if not record.name_en_fold:
                record.name_en_fold = fold_en_name(ev.name_en_raw)
        id_role = "wx" if ev.id_kind == "wx_id" else "id"
        anchors = list(ev.extra_anchors) or [
            {"table": ev.table, "field": ev.name_field, "value_role": "name"},
            {"table": ev.table, "field": ev.id_field, "value_role": id_role},
        ]
        for item in anchors:
            key = (item.get("table"), item.get("field"), item.get("value_role"))
            existing = {
                (a.get("table"), a.get("field"), a.get("value_role"))
                for a in record.anchored_fields
            }
            if key not in existing:
                record.anchored_fields.append(item)

    for ev in kept:
        matched: PersonRecord | None = None
        for record in clusters:
            if _same_cluster(record, ev) and _compatible(record, ev):
                matched = record
                break
        if matched is None:
            matched = PersonRecord()
            clusters.append(matched)
        _apply(matched, ev)

    return [item for item in clusters if item.person_key() and item.form_count() >= 2]


def person_records_to_payloads(
    records: Sequence[PersonRecord],
) -> list[tuple[str, str, str, str, dict[str, Any] | None]]:
    payloads: list[tuple[str, str, str, str, dict[str, Any] | None]] = []
    for record in records:
        extra = record.snapshot()
        for alias in record.aliases():
            payloads.append(
                (PERSON_TABLE, PERSON_FIELD, VAL_PERSON_ALIAS, alias, extra)
            )
    return payloads


def sample_pair_rows(
    proto: Any,
    ds: CoreDatasource,
    table: CoreTable,
    columns: Sequence[str],
    *,
    limit: int = PERSON_SAMPLE_LIMIT,
) -> list[dict[str, Any]]:
    """Row-wise sample so id/name arrays can zip. Tests may stub ``sample_rows``."""
    names = [str(item).strip() for item in columns if str(item).strip()]
    if not names:
        return []
    sampler = getattr(proto, "sample_rows", None)
    if callable(sampler):
        try:
            rows = sampler(
                ds,
                resource=str(table.table_name or ""),
                columns=names,
                database_name=getattr(table, "database_name", None),
                limit=limit,
            )
        except Exception as exc:
            SQLBotLogUtil.warning(
                "person-map sample_rows %s failed: %s", table.table_name, exc
            )
            return []
        return [row for row in (rows or []) if isinstance(row, dict)]
    execute = getattr(proto, "execute", None)
    qualify = getattr(proto, "qualify_table", None)
    quote = getattr(proto, "_quote_identifier", None)
    if not callable(execute) or not callable(qualify):
        return []
    try:
        from apps.protocol.base import QueryPlan

        table_sql = qualify(
            ds,
            str(table.table_name or ""),
            database_name=getattr(table, "database_name", None),
        )
        quoted = [quote(name) if callable(quote) else name for name in names]
        sql = f"SELECT {', '.join(quoted)} FROM {table_sql} LIMIT {max(1, int(limit))}"
        result = execute(ds, QueryPlan(statement=sql, payload={"sql": sql}))
        data = list(getattr(result, "data", None) or [])
        out: list[dict[str, Any]] = []
        for row in data:
            if isinstance(row, dict):
                out.append(row)
            elif isinstance(row, list | tuple):
                out.append(
                    {names[idx]: row[idx] for idx in range(min(len(names), len(row)))}
                )
        return out
    except Exception as exc:
        SQLBotLogUtil.warning(
            "person-map sample sql %s failed: %s", table.table_name, exc
        )
        return []


def collect_hub_evidence(
    proto: Any,
    ds: CoreDatasource,
    table: CoreTable,
    fields: Sequence[CoreField],
) -> list[PersonEvidence]:
    """cust_person_info: sys user_id ↔ name / en_name on the same row."""
    table_name = str(table.table_name or "")
    if table_name != OPERATOR_HUB:
        return []
    present = {str(item.field_name or "").strip() for item in fields}
    if "user_id" not in present or "name" not in present:
        return []
    needed = [col for col in ("user_id", "name", "en_name", "id") if col in present]
    rows = sample_pair_rows(proto, ds, table, needed)
    evidence: list[PersonEvidence] = []
    for row in rows:
        user_id = str(row.get("user_id") or "").strip() or None
        name_zh, name_from_zh_col = classify_person_name(str(row.get("name") or ""))
        en_zh, name_en = classify_person_name(str(row.get("en_name") or ""))
        name_zh = name_zh or en_zh
        name_en = name_en or name_from_zh_col
        if not ((user_id and (name_zh or name_en)) or (name_zh and name_en)):
            continue
        anchors = [
            {"table": table_name, "field": "user_id", "value_role": "id"},
            {"table": table_name, "field": "name", "value_role": "name"},
        ]
        if "en_name" in present:
            anchors.append(
                {"table": table_name, "field": "en_name", "value_role": "name"}
            )
        if "id" in present:
            anchors.append({"table": table_name, "field": "id", "value_role": "hub_pk"})
        evidence.append(
            PersonEvidence(
                table=table_name,
                name_field="name",
                id_field="user_id",
                id_kind="user_id",
                user_id=user_id,
                name_zh=name_zh,
                name_en_raw=name_en,
                extra_anchors=anchors,
            )
        )
    return evidence


def collect_person_evidence(
    proto: Any,
    ds: CoreDatasource,
    table: CoreTable,
    fields: Sequence[CoreField],
) -> list[PersonEvidence]:
    table_name = str(table.table_name or "")
    field_names = [str(item.field_name or "").strip() for item in fields]
    evidence: list[PersonEvidence] = []
    evidence.extend(collect_hub_evidence(proto, ds, table, fields))
    specs = pair_specs_for_table(table_name, field_names)
    if not specs:
        return evidence
    needed: list[str] = []
    seen_cols: set[str] = set()
    for spec in specs:
        for col in (spec.id_field, spec.name_field):
            if col not in seen_cols:
                seen_cols.add(col)
                needed.append(col)
    rows = sample_pair_rows(proto, ds, table, needed)
    for row in rows:
        for spec in specs:
            id_cell = str(row.get(spec.id_field) or "")
            name_cell = str(row.get(spec.name_field) or "")
            evidence.extend(evidence_from_row(spec, id_cell, name_cell))
    return evidence


def extra_instance_hits_for_people(
    person_hits: Sequence[Any],
    instance_rows: Sequence[Any],
    *,
    scope_tables: set[str] | None = None,
    scope_fields: set[tuple[str, str]] | None = None,
) -> list[Any]:
    """Expand person_alias hits onto instance rows on anchored fields."""
    from apps.datasource.instance_index.service import ValueAnchor
    from apps.dictionary.matching import normalize_dictionary_value

    wanted: list[tuple[set[str], set[tuple[str, str]], dict[str, Any]]] = []
    for hit in person_hits:
        extra = hit.extra if isinstance(getattr(hit, "extra", None), dict) else {}
        if not extra:
            continue
        alias_values = list(extra.get("aliases") or []) + [
            extra.get("name_zh"),
            extra.get("name_en_raw"),
            extra.get("name_en_fold"),
            extra.get("user_id"),
            extra.get("sso_id"),
            extra.get("wx_id"),
        ]
        aliases = {
            normalize_dictionary_value(str(item))
            for item in alias_values
            if str(item or "").strip()
        }
        fields = {
            (str(item.get("table") or ""), str(item.get("field") or ""))
            for item in (extra.get("anchored_fields") or [])
            if isinstance(item, dict) and item.get("table") and item.get("field")
        }
        if scope_fields or scope_tables:
            fields = {
                pair
                for pair in fields
                if pair in (scope_fields or set()) or pair[0] in (scope_tables or set())
            }
        if aliases and fields:
            wanted.append((aliases, fields, extra))
    if not wanted:
        return []
    out: list[ValueAnchor] = []
    seen: set[tuple[str, str, str]] = set()
    for row in instance_rows:
        table = str(getattr(row, "table_name", "") or "")
        field_name = str(getattr(row, "field_name", "") or "")
        raw = str(getattr(row, "raw_value", "") or "")
        norm = str(getattr(row, "normalized_value", "") or "")
        val_type = str(getattr(row, "val_type", "") or "")
        if val_type == VAL_PERSON_ALIAS:
            continue
        key = (table, field_name, raw)
        if key in seen:
            continue
        for aliases, fields, extra in wanted:
            if (table, field_name) not in fields:
                continue
            if not any(alias and (alias in norm or norm in alias) for alias in aliases):
                continue
            seen.add(key)
            row_extra = (
                getattr(row, "extra", None)
                if isinstance(getattr(row, "extra", None), dict)
                else {}
            )
            merged = dict(extra)
            merged.update(row_extra or {})
            for keep in (
                "person_key",
                "user_id",
                "wx_id",
                "name_zh",
                "name_en_fold",
                "name_en_raw",
                "aliases",
                "anchored_fields",
            ):
                if extra.get(keep) is not None:
                    merged[keep] = extra[keep]
            out.append(
                ValueAnchor(
                    table_name=table,
                    field_name=field_name,
                    raw_value=raw,
                    val_type=val_type or "instance",
                    matched_text=norm or raw,
                    extra=merged,
                )
            )
            break
    return out


def synthetic_id_hits_for_people(person_hits: Sequence[Any], scope: Any) -> list[Any]:
    """Emit id/wx column candidates from the combo snapshot when instance rows are missing."""
    from apps.datasource.instance_index.service import ValueAnchor

    allows = getattr(scope, "allows", None)
    out: list[ValueAnchor] = []
    seen: set[tuple[str, str, str]] = set()
    for hit in person_hits:
        extra = hit.extra if isinstance(getattr(hit, "extra", None), dict) else {}
        if not extra:
            continue
        user_id = str(extra.get("user_id") or extra.get("sso_id") or "").strip()
        wx_id = str(extra.get("wx_id") or "").strip()
        for item in extra.get("anchored_fields") or []:
            if not isinstance(item, dict):
                continue
            table = str(item.get("table") or "")
            field_name = str(item.get("field") or "")
            role = str(item.get("value_role") or "")
            if not table or not field_name:
                continue
            if callable(allows) and not allows(table, field_name):
                continue
            raw = ""
            if role == "id" and user_id:
                raw = user_id
            elif role == "wx" and wx_id:
                raw = wx_id
            if not raw:
                continue
            key = (table, field_name, raw)
            if key in seen:
                continue
            seen.add(key)
            out.append(
                ValueAnchor(
                    table_name=table,
                    field_name=field_name,
                    raw_value=raw,
                    val_type="instance",
                    matched_text=raw,
                    extra=dict(extra),
                )
            )
    return out
