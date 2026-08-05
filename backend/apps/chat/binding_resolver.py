"""Resolve structured entity bindings from unified knowledge matches."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable
from typing import Any

from apps.chat.query_contract import PredicateRequirement, parse_requirement
from apps.knowledge.models import KnowledgeMatch


def resolve_entity_bindings(
    matches: Iterable[KnowledgeMatch | dict[str, Any]],
) -> dict[str, Any]:
    grouped: dict[str, list[KnowledgeMatch]] = defaultdict(list)
    for item in matches:
        match = (
            item
            if isinstance(item, KnowledgeMatch)
            else KnowledgeMatch.model_validate(item)
        )
        if "entity_binding" in match.usages and match.targets:
            grouped[match.query].append(match)

    resolved: dict[str, Any] = {}
    ambiguous: dict[str, Any] = {}
    for phrase, options in grouped.items():
        ordered = sorted(options, key=lambda item: item.score, reverse=True)
        winner = ordered[0]
        competing_scores = [
            item.score for item in ordered[1:] if item.canonical != winner.canonical
        ]
        margin = (
            winner.score - max(competing_scores) if competing_scores else winner.score
        )
        targets: list[dict[str, Any]] = []
        seen_targets: set[tuple[int, int]] = set()
        for option in ordered:
            if option.canonical != winner.canonical:
                continue
            for target in option.targets:
                key = (target.table_id, target.field_id)
                if key not in seen_targets:
                    seen_targets.add(key)
                    targets.append(target.model_dump())
        alternatives: list[str] = []
        for value in [*winner.alternatives, *(item.canonical for item in ordered[1:])]:
            if value != winner.canonical and value not in alternatives:
                alternatives.append(value)
        binding = {
            "canonical": winner.canonical,
            "description": winner.description,
            "alternatives": alternatives[:8],
            "targets": targets,
            "resolution": winner.match_type,
            "confidence": winner.score,
            "margin": round(margin, 4),
        }
        is_confident = (
            winner.match_type in {"exact", "suffix"}
            and winner.score >= 0.9
            and margin >= 0.05
        )
        if is_confident:
            binding["match"] = "eq"
            resolved[phrase] = binding
        else:
            ambiguous[phrase] = {
                **binding,
                "match": "candidate",
                "options": [
                    {
                        "canonical": item.canonical,
                        "description": item.description,
                        "score": item.score,
                        "targets": [target.model_dump() for target in item.targets],
                    }
                    for item in ordered[:8]
                ],
            }
    return {
        "candidates": list(grouped),
        "resolved": resolved,
        "ambiguous": ambiguous,
        "match_count": sum(len(items) for items in grouped.values()),
    }


def binding_resource_names(bindings: dict[str, Any]) -> list[str]:
    """Return every table needed to evaluate or apply an entity binding."""
    names: list[str] = []

    def append_targets(targets: Iterable[dict[str, Any]]) -> None:
        for target in targets:
            name = target.get("table_name")
            if name and name not in names:
                names.append(name)

    for info in (bindings.get("resolved") or {}).values():
        append_targets(info.get("targets") or [])
    for info in (bindings.get("ambiguous") or {}).values():
        for option in info.get("options") or []:
            append_targets(option.get("targets") or [])
    return names


def retain_binding_resources(
    bindings: dict[str, Any],
    allowed_resource_names: Iterable[str],
) -> dict[str, Any]:
    """Drop targets that schema/permission retrieval did not admit."""
    allowed = set(allowed_resource_names)
    resolved: dict[str, Any] = {}
    for phrase, raw_info in (bindings.get("resolved") or {}).items():
        info = dict(raw_info)
        targets = [
            target
            for target in info.get("targets") or []
            if target.get("table_name") in allowed
        ]
        if targets:
            info["targets"] = targets
            resolved[phrase] = info
    ambiguous: dict[str, Any] = {}
    for phrase, raw_info in (bindings.get("ambiguous") or {}).items():
        info = dict(raw_info)
        options: list[dict[str, Any]] = []
        for raw_option in info.get("options") or []:
            option = dict(raw_option)
            targets = [
                target
                for target in option.get("targets") or []
                if target.get("table_name") in allowed
            ]
            if targets:
                option["targets"] = targets
                options.append(option)
        if options:
            info["options"] = options
            ambiguous[phrase] = info
    return {
        **bindings,
        "candidates": list(dict.fromkeys([*resolved, *ambiguous])),
        "resolved": resolved,
        "ambiguous": ambiguous,
    }


def apply_confirmed_entity_bindings(
    bindings: dict[str, Any],
    intent_context: dict[str, Any] | None,
) -> dict[str, Any]:
    """Promote user-confirmed entity choices into normal resolved bindings."""
    if not intent_context:
        return bindings
    requirements = (
        (intent_context.get("contract") or {}).get("requirements")
        or (intent_context.get("draft") or {}).get("requirements")
        or []
    )
    selected_by_phrase: dict[str, str] = {}
    for raw in requirements:
        if not isinstance(raw, dict) or raw.get("clause") != "predicate":
            continue
        requirement = parse_requirement(raw)
        if not isinstance(requirement, PredicateRequirement):
            continue
        phrase = requirement.label.strip()
        selected = str(requirement.values[0]).strip() if requirement.values else ""
        if phrase and selected and phrase in (bindings.get("ambiguous") or {}):
            selected_by_phrase[phrase] = selected

    if not selected_by_phrase:
        return bindings
    resolved = dict(bindings.get("resolved") or {})
    ambiguous = dict(bindings.get("ambiguous") or {})
    for phrase, selected in selected_by_phrase.items():
        source = ambiguous.get(phrase)
        # A confirmed binding is meaningful only against the deterministic
        # candidate set that produced its clarification question.
        if not source:
            continue
        matching = next(
            (
                option
                for option in source.get("options") or []
                if str(option.get("canonical") or "") == selected
            ),
            None,
        )
        if matching is None:
            continue
        targets = list((matching or {}).get("targets") or source.get("targets") or [])
        resolved[phrase] = {
            "canonical": selected,
            "alternatives": [],
            "targets": targets,
            "resolution": "user_confirmed",
            "confidence": 1.0,
            "margin": 1.0,
            "match": "eq",
        }
        ambiguous.pop(phrase, None)
    return {
        **bindings,
        "candidates": list(dict.fromkeys([*resolved, *ambiguous])),
        "resolved": resolved,
        "ambiguous": ambiguous,
    }
