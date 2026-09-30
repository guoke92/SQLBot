"""Column shape, sentinel values, and MinHash sketches for extraction.

MinHash locates value-domain overlap during extract. It does not assign
``fk_like``. Sparse foreign keys stay in the candidate set when the column
names already say so (same name, ``id``/``*_id``, or ``ref_*`` pointing at
the other table's ``id``/``code``). Inclusion
ratios remain the job of ``validate_joins``.
"""

from __future__ import annotations

import hashlib
import os
import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping, Sequence

DEFAULT_K = 64

# Global placeholders. Column-specific high-frequency sentinels are detected
# per value bag and listed on the sketch.
SENTINEL_LITERALS = frozenset(
    {
        "00",
        "000",
        "0000",
        "000000",
        "00000000",
        "0000000000",
        "111111",
        "11111111",
        "1111111111",
        "123456",
        "1234567890",
        "123-456-7890",
        "111-111-1111",
        "000-000-0000",
        "N/A",
        "n/a",
        "NA",
        "na",
        "-",
        "--",
        "无",
        "未知",
        "test",
        "TEST",
    }
)
_REPEAT = re.compile(r"^(.)\1{5,}$")
WEAK_COMMENTS = frozenset({"", "编码", "code", "id", "ID"})


def is_sentinel(value: str) -> bool:
    text = str(value or "").strip()
    if not text:
        return True
    if text in SENTINEL_LITERALS:
        return True
    return bool(_REPEAT.match(text))


def sql_sentinel_exclusions(alias: str, column_sql: str) -> str:
    """Extra AND-clauses for live probes. ``column_sql`` is already quoted.

    Numeric ``0`` is not a global sentinel: flags and ids use it for real.
    """
    quoted = ", ".join(
        "'" + item.replace("'", "''") + "'" for item in sorted(SENTINEL_LITERALS)
    )
    cast = f"CAST({alias}.{column_sql} AS CHAR)"
    return f"{cast} NOT IN ({quoted})"


def summarize_value_counts(
    counts: Mapping[str, int],
    *,
    k: int = DEFAULT_K,
    basis: str = "counts",
) -> dict[str, Any]:
    """Shape + sentinels + MinHash from a value→count map."""
    values = [str(key) for key, count in counts.items() if int(count) > 0]
    weighted = [str(key) for key, count in counts.items() for _ in range(max(int(count), 0))]
    sentinels = sorted({value for value in values if is_sentinel(value)})
    usable = [value for value in values if not is_sentinel(value)]
    return {
        "shape": field_shape(usable),
        "sentinels": sentinels,
        "minhash": {
            "k": k,
            "basis": basis,
            "n": len(usable),
            "values": minhash_sketch(usable, k=k),
        },
        "sentinel_row_ratio": _sentinel_row_ratio(weighted),
    }


def field_shape(values: Sequence[str]) -> dict[str, Any]:
    cleaned = [str(value) for value in values if str(value).strip()]
    if not cleaned:
        return {}
    lengths = [len(value) for value in cleaned]
    mode_len, mode_n = Counter(lengths).most_common(1)[0]
    numeric = sum(1 for value in cleaned if value.isdigit()) / len(cleaned)
    prefix = os.path.commonprefix(cleaned) if len(cleaned) >= 3 else ""
    if len(prefix) > 8:
        prefix = prefix[:8]
    return {
        "n": len(cleaned),
        "len_min": min(lengths),
        "len_max": max(lengths),
        "len_mode": mode_len,
        "len_mode_ratio": round(mode_n / len(cleaned), 4),
        "numeric_ratio": round(numeric, 4),
        "common_prefix": prefix,
    }


def minhash_sketch(values: Iterable[str], *, k: int = DEFAULT_K) -> list[int | None]:
    sketch: list[int | None] = [None] * k
    seen: set[str] = set()
    for raw in values:
        text = str(raw).strip()
        if not text or text in seen or is_sentinel(text):
            continue
        seen.add(text)
        for index in range(k):
            hashed = _hash_token(index, text)
            current = sketch[index]
            if current is None or hashed < current:
                sketch[index] = hashed
    return sketch


def resemblance(left: Sequence[int | None], right: Sequence[int | None]) -> float:
    if not left or len(left) != len(right):
        return 0.0
    matches = 0
    for lhs, rhs in zip(left, right):
        if lhs is not None and lhs == rhs:
            matches += 1
    return matches / len(left)


@dataclass
class FieldSketch:
    fq: str
    table: str
    column: str
    comment: str = ""
    mysql_type: str = ""
    shape: dict[str, Any] = field(default_factory=dict)
    sentinels: list[str] = field(default_factory=list)
    minhash: list[int | None] = field(default_factory=list)
    basis: str = ""

    @property
    def has_comment(self) -> bool:
        return str(self.comment or "").strip() not in WEAK_COMMENTS


def locate_overlaps(
    fields: Sequence[FieldSketch],
    *,
    min_resemblance: float = 0.2,
) -> dict[str, Any]:
    """Pair fields by MinHash. Name-like endpoints stay even when resemblance is low."""
    pairs: list[dict[str, Any]] = []
    imputations: list[dict[str, Any]] = []
    ordered = list(fields)
    for index, left in enumerate(ordered):
        for right in ordered[index + 1 :]:
            if left.table == right.table:
                continue
            if left.mysql_type and right.mysql_type and not _types_compatible(
                left.mysql_type, right.mysql_type
            ):
                continue
            score = resemblance(left.minhash, right.minhash)
            name_keep = _name_keeps_pair(left, right)
            if score < min_resemblance and not name_keep:
                continue
            hint = shape_transform_hint(left.shape, right.shape)
            pairs.append(
                {
                    "left": left.fq,
                    "right": right.fq,
                    "resemblance": round(score, 4),
                    "kept_by": "minhash" if score >= min_resemblance else "name",
                    "transform_hint": hint,
                }
            )
            borrowed = _borrow_comment(left, right, score)
            if borrowed:
                imputations.append(borrowed)
    pairs.sort(key=lambda row: (-float(row["resemblance"]), row["left"], row["right"]))
    return {"pairs": pairs, "imputations": imputations}


def shape_transform_hint(left: Mapping[str, Any], right: Mapping[str, Any]) -> str:
    """Fixed prefix / length-gap hint. Empty when the shapes do not suggest a transform."""
    if not left or not right:
        return ""
    if float(left.get("numeric_ratio") or 0) < 0.9 or float(right.get("numeric_ratio") or 0) < 0.9:
        return ""
    left_len = int(left.get("len_mode") or 0)
    right_len = int(right.get("len_mode") or 0)
    if left_len <= 0 or right_len <= 0 or abs(left_len - right_len) != 1:
        return ""
    left_prefix = str(left.get("common_prefix") or "")
    right_prefix = str(right.get("common_prefix") or "")
    longer, shorter = (right_prefix, left_prefix) if right_len > left_len else (left_prefix, right_prefix)
    if longer and shorter and longer.startswith(shorter) and len(longer) == len(shorter) + 1:
        return f"prefix:{longer[len(shorter):]}"
    if longer and len(longer) == 1 and not shorter:
        return f"prefix:{longer}"
    return ""


def _borrow_comment(left: FieldSketch, right: FieldSketch, score: float) -> dict[str, str] | None:
    if score < 0.8:
        return None
    if left.has_comment and not right.has_comment:
        return {
            "target": right.fq,
            "from": left.fq,
            "comment": left.comment,
            "resemblance": f"{score:.4f}",
            "trust": "proposed",
        }
    if right.has_comment and not left.has_comment:
        return {
            "target": left.fq,
            "from": right.fq,
            "comment": right.comment,
            "resemblance": f"{score:.4f}",
            "trust": "proposed",
        }
    return None


def _name_keeps_pair(left: FieldSketch, right: FieldSketch) -> bool:
    """Keep sparse FK-shaped names even when Jaccard is low.

    ``ref_*`` stays only when the name points at the other table and the
    other column is ``id`` / ``code`` (or named inside the ref token).
    """
    if left.column == right.column:
        return True
    if left.column == "id" and right.column.endswith("_id"):
        return True
    if right.column == "id" and left.column.endswith("_id"):
        return True
    return _ref_points_at(left, right) or _ref_points_at(right, left)


def _ref_points_at(ref: FieldSketch, other: FieldSketch) -> bool:
    if not ref.column.startswith("ref_"):
        return False
    token = ref.column[len("ref_") :]
    if not token or not other.table or other.table not in token:
        return False
    return other.column in {"id", "code"} or other.column in token


def _types_compatible(left: str, right: str) -> bool:
    def family(mysql_type: str) -> str:
        base = mysql_type.split("(", 1)[0].strip().lower()
        if base in {"int", "tinyint", "smallint", "bigint", "mediumint"}:
            return "int"
        if base in {"char", "varchar", "text", "enum"}:
            return "string"
        return base

    return family(left) == family(right)


def _hash_token(index: int, text: str) -> int:
    digest = hashlib.blake2s(f"{index}|{text}".encode(), digest_size=8).digest()
    return int.from_bytes(digest, "big")


def _sentinel_row_ratio(weighted: Sequence[str]) -> float:
    if not weighted:
        return 0.0
    hits = sum(1 for value in weighted if is_sentinel(value))
    return round(hits / len(weighted), 4)


def sketches_from_profile(
    catalog: Mapping[str, Any],
    profile: Mapping[str, Any],
    profile_instance: Mapping[str, Any] | None = None,
) -> list[FieldSketch]:
    """Build sketches from L0 YAML. Distinct counts win over top-k samples."""
    tables = (catalog.get("tables") or {}) if isinstance(catalog, Mapping) else {}
    found: dict[str, FieldSketch] = {}
    _absorb_profile_tables(found, tables, profile, basis="profile")
    if profile_instance:
        _absorb_instance_tables(found, tables, profile_instance)
    return list(found.values())


def _absorb_profile_tables(
    found: dict[str, FieldSketch],
    tables: Mapping[str, Any],
    profile: Mapping[str, Any],
    *,
    basis: str,
) -> None:
    for tname, tmeta in (profile.get("tables") or {}).items():
        columns = ((tables.get(tname) or {}).get("columns") or {}) if isinstance(tables, Mapping) else {}
        for cname, stats in (tmeta.get("column_stats") or {}).items():
            if not isinstance(stats, Mapping):
                continue
            counts = stats.get("values")
            if isinstance(counts, Mapping) and counts:
                summary = summarize_value_counts(counts, basis=basis)
            elif isinstance(stats.get("minhash"), Mapping):
                summary = {
                    "shape": stats.get("shape") or {},
                    "sentinels": list(stats.get("sentinels") or []),
                    "minhash": stats.get("minhash") or {},
                }
            else:
                continue
            info = columns.get(cname) or {}
            sketch = _sketch(str(tname), str(cname), info, summary)
            found[sketch.fq] = sketch


def _absorb_instance_tables(
    found: dict[str, FieldSketch],
    tables: Mapping[str, Any],
    profile_instance: Mapping[str, Any],
) -> None:
    for tname, tmeta in (profile_instance.get("tables") or {}).items():
        columns = ((tables.get(tname) or {}).get("columns") or {}) if isinstance(tables, Mapping) else {}
        for cname, stats in (tmeta.get("column_stats") or {}).items():
            fq = f"{tname}.{cname}"
            if fq in found or not isinstance(stats, Mapping):
                continue
            top_values = stats.get("top_values") or []
            counts = {
                str(item.get("value")): int(item.get("count") or 1)
                for item in top_values
                if isinstance(item, Mapping) and item.get("value") is not None
            }
            if not counts:
                continue
            info = columns.get(cname) or {}
            summary = summarize_value_counts(counts, basis="top_values")
            found[fq] = _sketch(str(tname), str(cname), info, summary)


def _sketch(
    table: str,
    column: str,
    info: Mapping[str, Any],
    summary: Mapping[str, Any],
) -> FieldSketch:
    packed = summary.get("minhash") or {}
    raw_values = packed.get("values") if isinstance(packed, Mapping) else []
    return FieldSketch(
        fq=f"{table}.{column}",
        table=table,
        column=column,
        comment=str(info.get("comment") or ""),
        mysql_type=str(info.get("type") or ""),
        shape=dict(summary.get("shape") or {}),
        sentinels=list(summary.get("sentinels") or []),
        minhash=list(raw_values or []),
        basis=str(packed.get("basis") or "") if isinstance(packed, Mapping) else "",
    )
