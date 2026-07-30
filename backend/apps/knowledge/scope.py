"""Pure permission scoping for structured knowledge matches."""

from __future__ import annotations

from collections.abc import Collection

from apps.knowledge.models import KnowledgeMatch


def scope_knowledge_matches(
    matches: list[KnowledgeMatch],
    *,
    allowed_targets: Collection[tuple[int, int]],
    row_restricted_tables: Collection[str] = (),
) -> list[KnowledgeMatch]:
    allowed = set(allowed_targets)
    restricted = set(row_restricted_tables)
    scoped: list[KnowledgeMatch] = []
    for match in matches:
        if "entity_binding" not in match.usages:
            scoped.append(match)
            continue
        targets = [
            target
            for target in match.targets
            if (target.table_id, target.field_id) in allowed
            and target.table_name not in restricted
        ]
        if targets:
            scoped.append(match.model_copy(update={"targets": targets}))
    return scoped
