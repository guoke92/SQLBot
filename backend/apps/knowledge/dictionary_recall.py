"""Local dictionary-value recall.

No datasource access is allowed here. Chat-time grounding consumes only the
last successfully published local snapshot in ``READY`` status (STALE /
DISABLED generations are never bound).
"""

from __future__ import annotations

from collections import defaultdict

from sqlalchemy import and_, desc, func, or_
from sqlmodel import Session, select

from apps.datasource.models.datasource import CoreField, CoreTable
from apps.dictionary.matching import best_matching_span, normalize_dictionary_value
from apps.dictionary.models import (
    DictionaryFieldConfig,
    DictionaryStatus,
    DictionaryValue,
)
from apps.knowledge.models import FieldTarget, KnowledgeMatch


def _rank(query: str, value: str) -> tuple[int, int, int, int]:
    return (
        0 if query == value else 1,
        0 if value.endswith(query) else 1,
        0 if query in value else 1,
        len(value),
    )


def recall_dictionary(
    session: Session,
    *,
    question: str,
    oid: int,
    ds_id: int,
    max_matches: int = 12,
) -> list[KnowledgeMatch]:
    normalized_question = normalize_dictionary_value(question)
    if not normalized_question:
        return []
    direct_match = DictionaryValue.normalized_value == normalized_question
    similarity = func.word_similarity(
        DictionaryValue.normalized_value,
        normalized_question,
    )
    fuzzy_match = and_(
        func.length(DictionaryValue.normalized_value) >= 3,
        DictionaryValue.normalized_value.op("<%")(normalized_question),
    )
    rows = session.exec(
        select(
            DictionaryValue,
            DictionaryFieldConfig,
            CoreTable,
            CoreField,
            similarity.label("similarity"),
        )
        .join(
            DictionaryFieldConfig,
            DictionaryFieldConfig.id == DictionaryValue.config_id,
        )
        .join(CoreTable, CoreTable.id == DictionaryFieldConfig.table_id)
        .join(CoreField, CoreField.id == DictionaryFieldConfig.field_id)
        .where(
            and_(
                DictionaryFieldConfig.oid == oid,
                DictionaryFieldConfig.ds_id == ds_id,
                DictionaryFieldConfig.enabled == True,  # noqa: E712
                DictionaryFieldConfig.status == DictionaryStatus.READY,
                DictionaryFieldConfig.published_generation > 0,
                DictionaryValue.generation
                == DictionaryFieldConfig.published_generation,
                or_(direct_match, fuzzy_match),
            )
        )
        .order_by(
            desc(direct_match),
            desc(similarity),
            func.length(DictionaryValue.normalized_value),
            DictionaryFieldConfig.id,
            DictionaryValue.id,
        )
        .limit(max_matches * 32)
    ).all()
    if not rows:
        return []

    grouped: dict[tuple[str, int], list[tuple[DictionaryValue, DictionaryFieldConfig, CoreTable, CoreField]]] = defaultdict(list)
    for value, config, table, field, _similarity in rows:
        matched_phrase = best_matching_span(
            normalized_question,
            value.normalized_value,
        )
        if matched_phrase:
            grouped[(matched_phrase, int(config.id))].append(
                (value, config, table, field)
            )

    matches: list[KnowledgeMatch] = []
    for (query, _config_id), candidates in grouped.items():
        ranked = sorted(
            candidates,
            key=lambda row: _rank(query, row[0].normalized_value),
        )
        for value, _config, table, field in ranked:
            rank = _rank(query, value.normalized_value)
            match_type = (
                "exact"
                if rank[0] == 0
                else "suffix"
                if rank[1] == 0
                else "contains"
            )
            score = (
                1.0
                if match_type == "exact"
                else 0.9
                if match_type == "suffix"
                else 0.75
            )
            matches.append(
                KnowledgeMatch(
                    source="dictionary",
                    usages=["entity_binding"],
                    query=query,
                    canonical=value.value,
                    description=field.custom_comment or field.field_comment or "",
                    match_type=match_type,
                    score=score,
                    targets=[
                        FieldTarget(
                            ds_id=ds_id,
                            table_id=int(table.id),
                            table_name=table.table_name,
                            field_id=int(field.id),
                            field_name=field.field_name,
                        )
                    ],
                )
            )
    consolidated: dict[tuple[str, str], KnowledgeMatch] = {}
    for match in sorted(matches, key=lambda item: item.score, reverse=True):
        key = (match.query, match.canonical)
        existing = consolidated.get(key)
        if existing is None:
            consolidated[key] = match
            continue
        seen_targets = {
            (target.table_id, target.field_id) for target in existing.targets
        }
        for target in match.targets:
            target_key = (target.table_id, target.field_id)
            if target_key not in seen_targets:
                existing.targets.append(target)
                seen_targets.add(target_key)
    return list(consolidated.values())[:max_matches]
