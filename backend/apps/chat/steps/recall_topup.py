"""Evidence-driven recall top-up: deterministic resolver + fulfiller.

Four trigger sources share one resolver: pre-recall question text, planner
``missing_concepts``, clarification answers (structured field refs + custom
text), and SQL identifier-validation failures (tables outside the working
set). The resolver only consults local indexes — value index, catalog lexicon,
relation graph, knowledge unit index — never an LLM. The fulfiller expands the
working set through the protocol's exact projection and appends a value
evidence block to the schema text (same convention as confirmed relations).
"""

from __future__ import annotations

import datetime
import threading
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, ConfigDict
from sqlmodel import Session, select

from apps.chat.models.chat_model import OperationEnum
from apps.chat.steps.observability import log_span
from apps.datasource.access import AccessScope
from apps.datasource.models.datasource import CoreTable
from apps.datasource.profiling.models import RelationKind, RelationStatus
from apps.datasource.profiling.service import get_published_relations
from apps.datasource.recall.value_index import match_values
from apps.dictionary.matching import normalize_dictionary_value
from apps.knowledge.compile import active_published_units
from common.core.config import settings
from common.utils.utils import SQLBotLogUtil

_EVIDENCE_TABLE_KINDS = frozenset({"clarification_option", "user_correction"})
_EVIDENCE_TEXT_KINDS = frozenset({"clarification_custom", "user_correction"})
_MIN_TERM_LENGTH = 2
_MAX_CATALOG_HITS = 4
_MAX_KNOWLEDGE_HITS = 3
_MAX_RELATION_NEIGHBORS = 3
_CANDIDATE_RELATION_CONFIDENCE = 0.85

_ALLOWLIST_LOCK = threading.Lock()
_ALLOWLIST_CACHE: tuple[str, frozenset[int]] = ("", frozenset())


@dataclass(frozen=True)
class TopupSignals:
    """Gap signals from one trigger source (all optional)."""

    question_text: str = ""
    evidence_texts: tuple[str, ...] = ()
    evidence_tables: tuple[str, ...] = ()
    unauthorized_tables: tuple[str, ...] = ()
    missing_concepts: tuple[str, ...] = ()


class TopupManifest(BaseModel):
    """What the resolver believes the working set is missing, and why."""

    model_config = ConfigDict(frozen=True)

    tables: tuple[str, ...] = ()
    advisory_tables: tuple[dict[str, Any], ...] = ()
    value_hits: tuple[dict[str, Any], ...] = ()
    knowledge_units: tuple[dict[str, Any], ...] = ()
    misses: tuple[str, ...] = ()

    @property
    def has_additions(self) -> bool:
        return bool(self.tables or self.advisory_tables or self.knowledge_units)


class TopupResult(BaseModel):
    """Fulfiller outcome; ``changed`` False means a no-op short-circuit."""

    model_config = ConfigDict(frozen=True)

    changed: bool = False
    added_tables: tuple[str, ...] = ()
    resources: tuple[str, ...] = ()


@dataclass(frozen=True)
class _CatalogTable:
    table_id: int
    name: str
    comment: str


def topup_enabled_for(ds_id: int | None) -> bool:
    """Master gate: feature flag + datasource allowlist (empty = all)."""
    if not settings.RECALL_TOUP_ENABLED:
        return False
    raw = (settings.RECALL_TOUP_DS_ALLOWLIST or "").strip()
    if not raw:
        return True
    global _ALLOWLIST_CACHE
    with _ALLOWLIST_LOCK:
        if _ALLOWLIST_CACHE[0] != raw:
            ids = frozenset(
                int(item.strip()) for item in raw.split(",") if item.strip().isdigit()
            )
            _ALLOWLIST_CACHE = (raw, ids)
        ids = _ALLOWLIST_CACHE[1]
    return ds_id is None or int(ds_id) in ids


def signals_from_evidence(items: list[Any]) -> TopupSignals:
    """Project clarification evidence into gap signals (pure, test-friendly).

    Option/correction answers carry structured field refs (``fields[].table``);
    custom/correction answers contribute their free text for value matching.
    """
    tables: list[str] = []
    texts: list[str] = []
    for item in items:
        kind = str(getattr(item, "kind", "") or "")
        structured = getattr(item, "structured_value", None)
        structured = structured if isinstance(structured, dict) else {}
        if kind in _EVIDENCE_TABLE_KINDS:
            name = str(structured.get("table") or "").strip()
            if name:
                tables.append(name)
            tables.extend(_table_refs(structured))
        if kind in _EVIDENCE_TEXT_KINDS:
            content = str(getattr(item, "content", "") or "").strip()
            if content:
                texts.append(content)
    return TopupSignals(
        evidence_tables=tuple(dict.fromkeys(tables)),
        evidence_texts=tuple(dict.fromkeys(texts)),
    )


def _table_refs(structured: Mapping[str, Any]) -> list[str]:
    """Table names from a structure carrying ``fields: [{table, ...}]`` refs."""
    names: list[str] = []
    for ref in structured.get("fields") or []:
        if isinstance(ref, Mapping):
            name = str(ref.get("table") or "").strip()
            if name:
                names.append(name)
    return names


def tables_from_clarify_card(card: Mapping[str, Any] | None) -> tuple[str, ...]:
    """Tables named by clarify option field refs (structured, no parsing).

    Consumed by the plan gate: an option that names a table outside the
    working set means the recall window — not the user — lacks information.
    """
    tables: list[str] = []
    if not isinstance(card, Mapping):
        return ()
    for question in card.get("questions") or []:
        if not isinstance(question, Mapping):
            continue
        for option in question.get("options") or []:
            if not isinstance(option, Mapping):
                continue
            name = str(option.get("table") or "").strip()
            if name:
                tables.append(name)
            tables.extend(_table_refs(option))
    return tuple(dict.fromkeys(tables))


def apply_knowledge_topup(
    session: Session,
    llm_service: Any,
    manifest: TopupManifest,
    *,
    oid: int,
) -> bool:
    """Recompile the bundle with one extra unit (+1 beyond the limit-2 cap).

    Returns True when ``llm_service.compiled_knowledge`` was replaced — the
    caller treats that as a working-set change (snapshot write-back / bounce)
    even when no tables were added.
    """
    if not manifest.knowledge_units:
        return False
    try:
        from apps.knowledge.compile import compile_business_data_bundle

        ds_id = getattr(llm_service.ds, "id", None)
        llm_service.compiled_knowledge = compile_business_data_bundle(
            session,
            stage="generate",
            question=str(llm_service.retrieval_question or ""),
            oid=int(oid),
            ds_id=int(ds_id) if ds_id else None,
            include_matches=False,
            extra_revision_ids=tuple(
                int(item["revision_id"])
                for item in manifest.knowledge_units
                if item.get("revision_id")
            ),
        )
        return True
    except Exception as exc:  # noqa: BLE001
        SQLBotLogUtil.warning("knowledge top-up recompile failed: %s", exc)
        return False


def _catalog(session: Session, *, ds_id: int) -> dict[str, _CatalogTable]:
    rows = session.exec(
        select(CoreTable).where(
            CoreTable.ds_id == ds_id,
            CoreTable.checked == True,  # noqa: E712
        )
    ).all()
    catalog: dict[str, _CatalogTable] = {}
    for table in rows:
        if table.id is None:
            continue
        catalog[table.table_name] = _CatalogTable(
            table_id=int(table.id),
            name=table.table_name,
            comment=str(table.custom_comment or "").strip(),
        )
    return catalog


def _match_catalog(
    terms: tuple[str, ...], catalog: dict[str, _CatalogTable]
) -> list[tuple[str, str]]:
    """Bidirectional containment between terms and table name/comment."""
    hits: list[tuple[str, str]] = []
    for raw_term in terms:
        term = normalize_dictionary_value(raw_term)
        if len(term) < _MIN_TERM_LENGTH:
            continue
        for entry in catalog.values():
            name = normalize_dictionary_value(entry.name)
            comment = normalize_dictionary_value(entry.comment)
            if (len(name) >= _MIN_TERM_LENGTH and (term in name or name in term)) or (
                len(comment) >= _MIN_TERM_LENGTH
                and (term in comment or comment in term)
            ):
                hits.append((entry.name, raw_term))
                if len(hits) >= _MAX_CATALOG_HITS:
                    return hits
    return hits


def _match_knowledge_units(
    session: Session,
    *,
    oid: int,
    ds_id: int,
    terms: tuple[str, ...],
) -> list[dict[str, Any]]:
    """Lexical match between missing concepts and active unit identity."""
    normalized_terms = [
        normalize_dictionary_value(term)
        for term in terms
        if len(normalize_dictionary_value(term)) >= _MIN_TERM_LENGTH
    ]
    if not normalized_terms:
        return []
    hits: list[dict[str, Any]] = []
    for unit, revision in active_published_units(session, oid=oid, datasource_id=ds_id):
        identity = normalize_dictionary_value(
            " ".join(part for part in (unit.title, unit.domain, unit.unit_key) if part)
        )
        if not identity:
            continue
        for term in normalized_terms:
            if term in identity:
                hits.append(
                    {
                        "unit_key": unit.unit_key,
                        "title": unit.title,
                        "domain": unit.domain,
                        "revision_id": int(revision.id or 0),
                        "matched_concept": term,
                    }
                )
                break
        if len(hits) >= _MAX_KNOWLEDGE_HITS:
            break
    return hits


def _relation_neighbors(
    session: Session,
    *,
    ds_id: int,
    anchor_table_ids: list[int],
    catalog: dict[str, _CatalogTable],
    working_set: set[str],
) -> list[dict[str, Any]]:
    """One-hop joinable endpoints of the anchor tables (advisory, capped)."""
    if not anchor_table_ids:
        return []
    id_to_name = {entry.table_id: entry.name for entry in catalog.values()}
    rows = get_published_relations(
        session,
        ds_id=ds_id,
        table_ids=anchor_table_ids,
        statuses=[RelationStatus.CONFIRMED.value, RelationStatus.CANDIDATE.value],
    )
    neighbors: list[dict[str, Any]] = []
    seen: set[int] = set()
    for relation in rows:
        if relation.kind not in (
            RelationKind.EQUI_JOIN.value,
            RelationKind.HIERARCHY.value,
        ):
            continue
        if relation.status != RelationStatus.CONFIRMED.value and (
            relation.confidence is None
            or float(relation.confidence) < _CANDIDATE_RELATION_CONFIDENCE
        ):
            continue
        for endpoint in (relation.source_table_id, relation.target_table_id):
            endpoint_id = int(endpoint or 0)
            name = id_to_name.get(endpoint_id)
            if (
                not name
                or endpoint_id in seen
                or endpoint_id in anchor_table_ids
                or name in working_set
            ):
                continue
            seen.add(endpoint_id)
            neighbors.append(
                {
                    "table": name,
                    "table_id": endpoint_id,
                    "reason": "relation-neighbor",
                    "status": relation.status,
                }
            )
            if len(neighbors) >= _MAX_RELATION_NEIGHBORS:
                return neighbors
    return neighbors


def resolve_recall_topup(
    session: Session,
    llm_service: Any,
    signals: TopupSignals,
    *,
    oid: int,
    access_scope: AccessScope | None = None,
) -> TopupManifest:
    """Turn gap signals into a manifest via local indexes only (no LLM)."""
    ds_id = int(getattr(llm_service.ds, "id", 0) or 0)
    catalog = _catalog(session, ds_id=ds_id)
    allowed = set(access_scope.resource_names) if access_scope is not None else None

    def _admissible(name: str) -> bool:
        return name in catalog and (allowed is None or name in allowed)

    working_set = {str(name) for name in (llm_service.table_name_list or [])}

    tables: list[str] = []

    def _claim(name: str) -> None:
        if name in working_set or name in tables or not _admissible(name):
            return
        tables.append(name)

    for name in (*signals.evidence_tables, *signals.unauthorized_tables):
        _claim(str(name).strip())

    value_hits: list[dict[str, Any]] = []
    texts = [signals.question_text, *signals.evidence_texts]
    for text in texts:
        if not str(text or "").strip():
            continue
        allowed_tables = frozenset(allowed) if allowed is not None else None
        for hit in match_values(
            session, str(text), oid=oid, ds_id=ds_id, allowed_tables=allowed_tables
        ):
            _claim(hit.table_name)
            value_hits.append(
                {
                    "table": hit.table_name,
                    "field": hit.field_name,
                    "value": hit.value,
                    "source": hit.source,
                    "in_text": hit.matched_text,
                }
            )
    unique_value_hits: list[dict[str, Any]] = []
    seen_hits: set[tuple[str, str, str]] = set()
    for item in value_hits:
        key = (item["table"], item["field"], item["in_text"])
        if key not in seen_hits:
            seen_hits.add(key)
            unique_value_hits.append(item)

    for table_name, _term in _match_catalog(signals.missing_concepts, catalog):
        if table_name not in working_set:
            _claim(table_name)

    knowledge_hits = _match_knowledge_units(
        session, oid=oid, ds_id=ds_id, terms=signals.missing_concepts
    )

    anchor_ids = [
        catalog[name].table_id
        for name in (*tables, *(hit["table"] for hit in unique_value_hits))
        if name in catalog
    ]
    neighbors = _relation_neighbors(
        session,
        ds_id=ds_id,
        anchor_table_ids=list(dict.fromkeys(anchor_ids)),
        catalog=catalog,
        working_set=working_set,
    )
    advisory_tables: list[dict[str, Any]] = []
    for neighbor in neighbors:
        if neighbor["table"] not in tables:
            advisory_tables.append(neighbor)

    resolved_terms = {
        normalize_dictionary_value(term)
        for term in signals.missing_concepts
        if any(
            normalize_dictionary_value(term) in normalize_dictionary_value(material)
            for material in (
                *(
                    f"{item['table']}.{item['field']} {item['value']}"
                    for item in unique_value_hits
                ),
                *(
                    f"{name} {catalog[name].comment}"
                    for name in tables
                    if name in catalog
                ),
                *(f"{item['title']} {item['domain']}" for item in knowledge_hits),
            )
        )
    }
    misses = tuple(
        term
        for term in signals.missing_concepts
        if normalize_dictionary_value(term) not in resolved_terms
    )

    return TopupManifest(
        tables=tuple(tables),
        advisory_tables=tuple(advisory_tables),
        value_hits=tuple(unique_value_hits),
        knowledge_units=tuple(knowledge_hits),
        misses=misses,
    )


def value_evidence_block(
    hits: list[dict[str, Any]] | tuple[dict[str, Any], ...],
) -> str:
    """Render value evidence in the schema text (confirmed-relations style)."""
    if not hits:
        return ""
    lines = ["【Value evidence】"]
    for item in hits:
        lines.append(
            f"{item.get('value')} ≈ {item.get('table')}.{item.get('field')} "
            f"({item.get('source')})"
        )
    return "\n".join(lines) + "\n"


def fulfill_recall_topup(
    session: Session,
    llm_service: Any,
    manifest: TopupManifest,
    *,
    access_scope: AccessScope | None = None,
    graph_node: str = "recall_topup",
    audit: bool = True,
) -> TopupResult:
    """Expand the working set via exact projection; short-circuit no-ops.

    ``audit=False`` suppresses the span when the caller's graph node already
    emitted its CHOOSE_TABLE span for this execution (same-retrieve rule);
    telemetry via ``record_topup_event`` is independent of this flag.
    """
    current = [str(name) for name in (llm_service.table_name_list or [])]
    present = set(current)
    additions = [
        name
        for name in (
            *manifest.tables,
            *(str(item["table"]) for item in manifest.advisory_tables),
        )
        if name and name not in present
    ]
    if not additions:
        evidence_ready = all(
            str(item.get("table")) in present for item in manifest.value_hits
        )
        if manifest.value_hits and evidence_ready:
            # Tables already present: only attach the evidence block.
            block = value_evidence_block(list(manifest.value_hits))
            if block and block not in (llm_service.chat_question.db_schema or ""):
                llm_service.chat_question.db_schema = (
                    str(llm_service.chat_question.db_schema or "") + block
                )
                return TopupResult(changed=True, resources=tuple(current))
        return TopupResult(changed=False, resources=tuple(current))

    union = list(dict.fromkeys([*current, *additions]))

    def _apply() -> list[str]:
        snapshot = llm_service.protocol.retrieve_schema(
            session=session,
            current_user=llm_service.current_user,
            ds=llm_service.ds,
            question=llm_service.retrieval_question,
            out_ds_instance=llm_service.out_ds_instance,
            resource_names=union,
            required_resource_names=(),
            access_scope=access_scope,
        )
        llm_service.chat_question.db_schema = snapshot.schema_text
        llm_service.chat_question.sample_data = snapshot.sample_data
        llm_service.table_name_list = list(snapshot.resource_names)
        block = value_evidence_block(list(manifest.value_hits))
        if block:
            llm_service.chat_question.db_schema = (
                str(llm_service.chat_question.db_schema or "") + block
            )
        return list(snapshot.resource_names)

    if not audit:
        try:
            resources = _apply()
        except Exception as exc:  # noqa: BLE001
            SQLBotLogUtil.warning("recall top-up fulfill failed: %s", exc)
            return TopupResult(changed=False, resources=tuple(current))
        return TopupResult(
            changed=True, added_tables=tuple(additions), resources=tuple(resources)
        )

    with log_span(
        operate=OperationEnum.CHOOSE_TABLE,
        record_id=getattr(llm_service.record, "id", None),
        local_operation=True,
        graph_node=graph_node,
        brief="补召回扩展工作集",
        title_key="chat.log.CHOOSE_TABLE",
    ) as span:
        try:
            resources = _apply()
        except Exception as exc:  # noqa: BLE001
            SQLBotLogUtil.warning("recall top-up fulfill failed: %s", exc)
            span.mark_degraded(f"recall top-up fulfill failed: {exc}")
            return TopupResult(changed=False, resources=tuple(current))
        span.set_detail(
            {
                "added_tables": additions,
                "resources": resources,
                "value_hits": [dict(item) for item in manifest.value_hits],
                "advisory_tables": [dict(item) for item in manifest.advisory_tables],
                "knowledge_units": [dict(item) for item in manifest.knowledge_units],
            }
        )
        span.set_summary("chat.audit.schema_ready", count=len(resources))
    return TopupResult(
        changed=True,
        added_tables=tuple(additions),
        resources=tuple(resources),
    )


def record_topup_event(session: Session, run_id: str, event: dict[str, Any]) -> None:
    """Append one top-up telemetry event under ``query_run.agent_decision``."""
    try:
        from apps.conversation.models import QueryRun

        run = session.get(QueryRun, run_id)
        if run is None:
            return
        decision = dict(run.agent_decision or {})
        history = list(decision.get("topup") or [])
        history.append({"ts": datetime.datetime.now().isoformat(), **event})
        decision["topup"] = history
        run.agent_decision = decision
        session.add(run)
        session.commit()
    except Exception as exc:  # noqa: BLE001
        SQLBotLogUtil.warning("recall top-up telemetry write failed: %s", exc)
        session.rollback()
