"""Query-conditioned caliber conflicts from Wiki term bridges.

Wiki spec v0 §3.9: concept pages are term bridges; ``adjudication: boundary``
plus ``also_confused_with`` mark competing fields. Enum value labels are user
sayings. The kernel — not the LLM — decides when those bindings conflict.

Detection is query-conditioned (not “any recalled page with also_confused_with”):

1. Attribution: 「A是B」/「A为B」 where A and B bind distinct ``table.field``
2. Alias collision: one query phrase maps to two field_targets
3. Boundary: both sides of a published boundary pair are phrase-matched

``adjudication: synonym`` never conflicts. Independent requested dimensions
(no attribution / collision / boundary) do not conflict — that is why
「查询企业名称和认证方式」 must not open a card.

Conflicts are **evidence** for the agent (``<caliber_conflicts>``), never an
automatic ClarificationCard. The model decides whether to ask and how to word it.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Literal

# Matches plane / prompt budget for conflict evidence — keep in sync.
_MAX_CONFLICTS = 4
_MIN_TERM = 3
_ATTR_CONNECTORS = ("是", "为", "等于")
ConflictKind = Literal["attribution", "alias_collision", "boundary"]


@dataclass(frozen=True)
class TermBinding:
    phrase: str
    page_key: str
    title: str
    table: str
    field: str
    value: str = ""
    value_label: str = ""
    enum_catalog: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class CaliberConflict:
    conflict_id: str
    kind: ConflictKind
    phrase: str
    candidates: tuple[dict[str, Any], ...]
    bindings: tuple[TermBinding, ...] = ()

    def to_evidence(self) -> dict[str, Any]:
        """Evidence for the agent — not a ClarificationCard template."""
        return {
            "conflict_id": self.conflict_id,
            "kind": self.kind,
            "phrase": self.phrase,
            "candidates": [dict(item) for item in self.candidates],
        }

    def page_keys(self) -> tuple[str, ...]:
        return tuple(
            dict.fromkeys(item.page_key for item in self.bindings if item.page_key)
        )


def detect_caliber_conflicts(store: Any, query: str) -> tuple[CaliberConflict, ...]:
    """Return grounded conflicts for this query against the Wiki store."""
    text = str(query or "").strip()
    if store is None or not text:
        return ()
    terms = _term_index(store)
    if not terms:
        return ()
    hits = _phrase_hits(text, terms)
    if not hits:
        return ()
    grouped: dict[frozenset[tuple[str, str]], _Draft] = {}
    _collect_attribution(text, hits, grouped)
    _collect_collisions(hits, grouped)
    _collect_boundary(store, hits, grouped)
    built: list[CaliberConflict] = []
    for draft in sorted(grouped.values(), key=lambda item: item.conflict_id):
        conflict = draft.build()
        if conflict is not None:
            built.append(conflict)
        if len(built) >= _MAX_CONFLICTS:
            break
    return tuple(built)


def conflicts_to_evidence(
    conflicts: tuple[CaliberConflict, ...],
) -> list[dict[str, Any]]:
    return [item.to_evidence() for item in conflicts]


def conflict_page_keys(conflicts: Sequence[CaliberConflict]) -> list[str]:
    keys: list[str] = []
    for item in conflicts:
        for key in item.page_keys():
            if key not in keys:
                keys.append(key)
    return keys


def unresolved_conflicts(
    conflicts: Sequence[Mapping[str, Any]],
    confirmed: Any,
) -> list[dict[str, Any]]:
    """Drop conflicts the user already confirmed this turn / session."""
    confirmed_ids, confirmed_fields = _confirmed_index(confirmed)
    kept: list[dict[str, Any]] = []
    for item in conflicts:
        payload = dict(item)
        qid = str(
            payload.get("conflict_id")
            or payload.get("question_id")
            or ""
        )
        if qid and qid in confirmed_ids:
            continue
        candidate_fields = {
            (str(opt.get("table") or ""), str(opt.get("field") or ""))
            for opt in (
                payload.get("candidates") or payload.get("options") or []
            )
            if isinstance(opt, dict) and opt.get("field")
        }
        if candidate_fields & confirmed_fields:
            continue
        kept.append(payload)
    return kept


@dataclass
class _Draft:
    conflict_id: str
    kind: ConflictKind
    phrase: str
    bindings: list[TermBinding]

    def build(self) -> CaliberConflict | None:
        candidates = _candidates_from_bindings(self.bindings)
        if len(candidates) < 2:
            return None
        return CaliberConflict(
            conflict_id=self.conflict_id,
            kind=self.kind,
            phrase=self.phrase,
            candidates=tuple(candidates),
            bindings=tuple(self.bindings),
        )


def _term_index(store: Any) -> dict[str, list[TermBinding]]:
    index: dict[str, list[TermBinding]] = {}
    pages = getattr(store, "pages", {}) or {}
    catalogs = _enum_catalogs(store)
    for page in pages.values():
        page_type = str(getattr(page, "type", "") or "")
        if page_type not in {"concept", "dict"}:
            continue
        targets = _page_field_targets(store, page)
        if not targets:
            continue
        store_key = str(getattr(page, "store_key", "") or getattr(page, "page_key", ""))
        title = str(getattr(page, "title", "") or store_key)
        for phrase in _page_phrases(page):
            for table, fname in targets:
                _add_term(
                    index,
                    phrase,
                    TermBinding(
                        phrase=phrase,
                        page_key=store_key,
                        title=title,
                        table=table,
                        field=fname,
                        enum_catalog=catalogs.get((table, fname), ()),
                    ),
                )
        if page_type != "dict":
            continue
        for label, value in _enum_labels(page):
            for table, fname in targets:
                _add_term(
                    index,
                    label,
                    TermBinding(
                        phrase=label,
                        page_key=store_key,
                        title=title,
                        table=table,
                        field=fname,
                        value=value,
                        value_label=label,
                        enum_catalog=catalogs.get((table, fname), ()),
                    ),
                )
    return index


def _add_term(
    index: dict[str, list[TermBinding]], phrase: str, binding: TermBinding
) -> None:
    key = phrase.strip()
    if len(key) < _MIN_TERM:
        return
    bucket = index.setdefault(key, [])
    ident = (binding.page_key, binding.table, binding.field, binding.value)
    if any(
        (item.page_key, item.table, item.field, item.value) == ident for item in bucket
    ):
        return
    bucket.append(binding)


def _page_phrases(page: Any) -> list[str]:
    names = [
        str(getattr(page, "title", "") or ""),
        *list(getattr(page, "aliases", ()) or ()),
    ]
    return [name.strip() for name in names if name and name.strip()]


def _page_field_targets(store: Any, page: Any) -> list[tuple[str, str]]:
    """Resolve concept/enum anchors to ``(table, field)`` only — no enum values."""
    refs: list[str] = []
    refs.extend(str(item) for item in (getattr(page, "field_targets", ()) or ()))
    maps_to = str(getattr(page, "maps_to", "") or "").strip()
    if maps_to:
        refs.append(maps_to.split("=", 1)[0].strip())
    if str(getattr(page, "type", "") or "") == "dict":
        for block in getattr(page, "ground_blocks", ()) or ():
            if getattr(block, "kind", "") != "dict":
                continue
            for item in (getattr(block, "data", {}) or {}).get("fields") or []:
                refs.append(str(item))
    seen: set[tuple[str, str]] = set()
    out: list[tuple[str, str]] = []
    for ref in refs:
        resolved = _resolve_field_ref(store, ref)
        if resolved is None or resolved in seen:
            continue
        seen.add(resolved)
        out.append(resolved)
    return out


def _resolve_field_ref(store: Any, raw: str) -> tuple[str, str] | None:
    text = str(raw or "").strip().split("=", 1)[0].strip().strip("'\"")
    if "." not in text:
        return None
    left, _, right = text.partition(".")
    left = left.strip()
    right = right.strip()
    if not left or not right:
        return None
    table_index = getattr(store, "table_index", {}) or {}
    if left in table_index:
        return (left, right)
    enum_page = _resolve_page_name(store, left)
    if enum_page is None or str(getattr(enum_page, "type", "") or "") != "dict":
        return None
    for carrier in _enum_carrier_fields(store, enum_page):
        return carrier
    return None


def _enum_carrier_fields(store: Any, page: Any) -> list[tuple[str, str]]:
    table_index = getattr(store, "table_index", {}) or {}
    refs: list[str] = []
    for item in getattr(page, "field_targets", ()) or ():
        refs.append(str(item))
    for block in getattr(page, "ground_blocks", ()) or ():
        if getattr(block, "kind", "") != "dict":
            continue
        for item in (getattr(block, "data", {}) or {}).get("fields") or []:
            refs.append(str(item))
    out: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for ref in refs:
        text = str(ref or "").strip()
        if "." not in text:
            continue
        table, _, fname = text.partition(".")
        table = table.strip()
        fname = fname.strip()
        if table not in table_index or not fname:
            continue
        key = (table, fname)
        if key in seen:
            continue
        seen.add(key)
        out.append(key)
    return out


def _enum_catalogs(store: Any) -> dict[tuple[str, str], tuple[tuple[str, str], ...]]:
    """table.field → published enum (value, label) pairs."""
    catalogs: dict[tuple[str, str], tuple[tuple[str, str], ...]] = {}
    pages = getattr(store, "pages", {}) or {}
    for page in pages.values():
        if str(getattr(page, "type", "") or "") != "dict":
            continue
        labels = tuple(_enum_labels(page))
        if not labels:
            continue
        for table, fname in _page_field_targets(store, page):
            catalogs[(table, fname)] = labels
    return catalogs


def _enum_labels(page: Any) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for block in getattr(page, "ground_blocks", ()) or ():
        if getattr(block, "kind", "") != "dict":
            continue
        values = (getattr(block, "data", {}) or {}).get("values") or {}
        if not isinstance(values, dict):
            continue
        for value, meta in values.items():
            label = str(value)
            if isinstance(meta, dict):
                label = str(meta.get("label") or value)
            elif meta:
                label = str(meta)
            label = label.strip()
            if label:
                out.append((label, str(value)))
    return out


def _phrase_hits(
    query: str, terms: dict[str, list[TermBinding]]
) -> list[tuple[str, list[TermBinding], int, int]]:
    lowered = query.casefold()
    occupied = [False] * len(lowered)
    hits: list[tuple[str, list[TermBinding], int, int]] = []
    for phrase in sorted(terms, key=len, reverse=True):
        needle = phrase.casefold()
        if len(needle) < _MIN_TERM:
            continue
        start = 0
        while True:
            index = lowered.find(needle, start)
            if index < 0:
                break
            end = index + len(needle)
            if not any(occupied[index:end]):
                occupied[index:end] = [True] * (end - index)
                hits.append((phrase, terms[phrase], index, end))
            start = index + 1
    hits.sort(key=lambda item: item[2])
    return hits


def _collect_attribution(
    query: str,
    hits: list[tuple[str, list[TermBinding], int, int]],
    grouped: dict[frozenset[tuple[str, str]], _Draft],
) -> None:
    for connector in _ATTR_CONNECTORS:
        start = 0
        while True:
            index = query.find(connector, start)
            if index < 0:
                break
            end = index + len(connector)
            left = _nearest_hit(hits, before=index)
            right = _nearest_hit(hits, after=end)
            start = end
            if left is None or right is None:
                continue
            if index - left[3] > 2 or right[2] - end > 2:
                continue
            phrase = query[left[2] : right[3]]
            _register(grouped, "attribution", phrase, [*left[1], *right[1]])


def _collect_collisions(
    hits: list[tuple[str, list[TermBinding], int, int]],
    grouped: dict[frozenset[tuple[str, str]], _Draft],
) -> None:
    for phrase, bindings, _start, _end in hits:
        fields = {(item.table, item.field) for item in bindings}
        if len(fields) < 2:
            continue
        _register(grouped, "alias_collision", phrase, list(bindings))


def _collect_boundary(
    store: Any,
    hits: list[tuple[str, list[TermBinding], int, int]],
    grouped: dict[frozenset[tuple[str, str]], _Draft],
) -> None:
    pages = getattr(store, "pages", {}) or {}
    hit_keys = {
        binding.page_key for _phrase, bindings, _s, _e in hits for binding in bindings
    }
    by_page: dict[str, list[TermBinding]] = {}
    phrases_by_page: dict[str, list[str]] = {}
    for phrase, bindings, _s, _e in hits:
        for binding in bindings:
            by_page.setdefault(binding.page_key, []).append(binding)
            phrases_by_page.setdefault(binding.page_key, []).append(phrase)
    for page in pages.values():
        if (
            str(getattr(page, "adjudication", "") or "").strip().casefold()
            != "boundary"
        ):
            continue
        confused = [
            str(item).strip()
            for item in (getattr(page, "also_confused_with", ()) or ())
            if str(item).strip()
        ]
        store_key = str(getattr(page, "store_key", "") or "")
        if store_key not in hit_keys or not confused:
            continue
        for name in confused:
            other = _resolve_page_name(store, name)
            other_key = (
                str(getattr(other, "store_key", "") or "") if other is not None else ""
            )
            if not other_key or other_key not in hit_keys:
                continue
            left_phrase = (phrases_by_page.get(store_key) or [""])[0]
            right_phrase = (phrases_by_page.get(other_key) or [""])[0]
            phrase = f"{left_phrase} / {right_phrase}".strip(" /")
            _register(
                grouped,
                "boundary",
                phrase,
                [*(by_page.get(store_key) or []), *(by_page.get(other_key) or [])],
            )


def _nearest_hit(
    hits: list[tuple[str, list[TermBinding], int, int]],
    *,
    before: int | None = None,
    after: int | None = None,
) -> tuple[str, list[TermBinding], int, int] | None:
    if before is not None:
        candidates = [item for item in hits if item[3] <= before]
        return max(candidates, key=lambda item: item[3]) if candidates else None
    if after is not None:
        candidates = [item for item in hits if item[2] >= after]
        return min(candidates, key=lambda item: item[2]) if candidates else None
    return None


def _register(
    grouped: dict[frozenset[tuple[str, str]], _Draft],
    kind: ConflictKind,
    phrase: str,
    bindings: list[TermBinding],
) -> None:
    fields = {
        (item.table, item.field) for item in bindings if item.table and item.field
    }
    if len(fields) < 2:
        return
    key = frozenset(fields)
    conflict_id = "caliber:" + "|".join(
        f"{table}.{fname}" for table, fname in sorted(key)
    )
    prior = grouped.get(key)
    if prior is None or (prior.kind != "attribution" and kind == "attribution"):
        grouped[key] = _Draft(
            conflict_id=conflict_id,
            kind=kind,
            phrase=phrase.strip(),
            bindings=list(bindings),
        )
        return
    prior.bindings.extend(bindings)


def _candidates_from_bindings(bindings: Sequence[TermBinding]) -> list[dict[str, Any]]:
    by_field: dict[tuple[str, str], TermBinding] = {}
    for item in bindings:
        if not item.table or not item.field:
            continue
        key = (item.table, item.field)
        prior = by_field.get(key)
        if prior is None or (item.value and not prior.value):
            by_field[key] = item
    candidates: list[dict[str, Any]] = []
    for (_table, _fname), item in sorted(by_field.items()):
        saying = (item.value_label or item.title or item.phrase).strip()
        candidate: dict[str, Any] = {
            "saying": saying,
            "table": item.table,
            "field": item.field,
            "value": item.value,
            "value_label": item.value_label,
        }
        if item.enum_catalog:
            candidate["enum_values"] = [
                {"value": value, "label": label} for label, value in item.enum_catalog
            ]
        candidates.append(candidate)
        if len(candidates) >= 6:
            break
    return candidates


def _resolve_page_name(store: Any, name: str) -> Any | None:
    raw = str(name or "").strip()
    if not raw:
        return None
    cleaned = raw.replace("[[", "").replace("]]", "").split("|", 1)[0].strip()
    getter = getattr(store, "get_page", None)
    if callable(getter):
        page = getter(cleaned)
        if page is not None:
            return page
        folded = cleaned.replace("_", "-")
        page = getter(folded)
        if page is not None:
            return page
    alias_index = getattr(store, "alias_index", {}) or {}
    key = alias_index.get(cleaned.casefold()) or alias_index.get(cleaned)
    pages = getattr(store, "pages", {}) or {}
    if key:
        return pages.get(key)
    for page in pages.values():
        title = str(getattr(page, "title", "") or "").strip()
        slug = str(getattr(page, "page_key", "") or "").strip()
        aliases = [str(item).strip() for item in (getattr(page, "aliases", ()) or ())]
        if cleaned in {title, slug, *aliases}:
            return page
        if cleaned.casefold() in {
            title.casefold(),
            slug.casefold(),
            *(item.casefold() for item in aliases),
        }:
            return page
    return None


def _confirmed_index(confirmed: Any) -> tuple[set[str], set[tuple[str, str]]]:
    ids: set[str] = set()
    fields: set[tuple[str, str]] = set()
    if not isinstance(confirmed, Mapping):
        return ids, fields
    for key, raw in confirmed.items():
        ids.add(str(key))
        if not isinstance(raw, Mapping):
            continue
        qid = str(raw.get("question_id") or "")
        if qid:
            ids.add(qid)
        table = str(raw.get("table") or "")
        fname = str(raw.get("field") or "")
        if fname:
            fields.add((table, fname))
        for item in raw.get("fields") or []:
            if not isinstance(item, Mapping):
                continue
            name = str(item.get("name") or item.get("field") or "")
            if name:
                fields.add((str(item.get("table") or table), name))
    return ids, fields
