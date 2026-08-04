"""Executable query contract compiled from confirmed semantic intent.

Clarification owns user-facing decisions. SQL planning and validation consume
this smaller, deterministic projection instead of reinterpreting labels or
free-form values independently.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Literal

from apps.chat.semantic_intent import (
    Aggregation,
    BindingRole,
    IntentBinding,
    decision_selected_values,
    validate_binding_requirements,
)


@dataclass(frozen=True)
class ContractBinding:
    """One physical identifier and its unambiguous SQL clause role."""

    identifier: str
    role: BindingRole
    aggregation: Aggregation = "none"


@dataclass(frozen=True)
class ContractRequirement:
    """One confirmed contract slot and its machine-checkable SQL requirement."""

    key: str
    kind: str
    label: str
    bindings: tuple[ContractBinding, ...]
    expected_values: tuple[str, ...] = ()
    match_any_identifier: bool = False

    @property
    def preserves_grain(self) -> bool:
        return any(binding.role == "group" for binding in self.bindings)

    @property
    def identifiers(self) -> tuple[str, ...]:
        return tuple(binding.identifier for binding in self.bindings)

    def bindings_for(
        self,
        *roles: Literal["group", "measure", "attribute", "filter", "join"],
    ) -> tuple[ContractBinding, ...]:
        accepted = set(roles)
        return tuple(binding for binding in self.bindings if binding.role in accepted)


@dataclass(frozen=True)
class QueryContract:
    """Canonical planning/validation projection of a resolved intent."""

    requirements: tuple[ContractRequirement, ...] = ()
    time_intent: Mapping[str, Any] | None = None


def _compile_bindings(values: Any, *, key: str) -> tuple[ContractBinding, ...]:
    if not isinstance(values, Sequence) or isinstance(values, (str, bytes)):
        return ()
    bindings: list[ContractBinding] = []
    seen: set[ContractBinding] = set()
    for value in values:
        if not isinstance(value, Mapping):
            raise ValueError(f"Query contract binding in {key} must be an object")
        try:
            parsed = IntentBinding.model_validate(value)
        except ValueError as exc:
            raise ValueError(f"Invalid query contract binding in {key}: {exc}") from exc
        binding = ContractBinding(
            identifier=parsed.identifier,
            role=parsed.role,
            aggregation=parsed.aggregation,
        )
        if binding not in seen:
            seen.add(binding)
            bindings.append(binding)
    return tuple(bindings)


def compile_query_contract(
    decisions: Sequence[Mapping[str, Any]],
    *,
    time_intent: Mapping[str, Any] | None = None,
) -> QueryContract:
    """Compile locked decisions once without guessing from display text."""
    requirements: list[ContractRequirement] = []
    seen_keys: set[str] = set()
    for decision in decisions:
        if not decision.get("locked"):
            continue
        key = str(decision.get("key") or "").strip()
        if not key or key in seen_keys:
            continue
        kind = str(decision.get("kind") or "").strip()
        effect = str(decision.get("effect") or "include").strip().lower()
        if effect not in {"include", "omit"}:
            raise ValueError(f"Unsupported intent effect in query contract: {effect}")
        if effect == "omit":
            seen_keys.add(key)
            continue
        bindings = _compile_bindings(decision.get("bindings") or [], key=key)
        binding_phrase = str(decision.get("binding_phrase") or "").strip()
        validate_binding_requirements(
            kind=kind,
            effect=effect,
            bindings=bindings,
            binding_phrase=binding_phrase,
            context=f"Executable {kind} decision {key}",
        )
        expected_values: tuple[str, ...] = ()
        if kind == "entity" and binding_phrase:
            expected_values = tuple(decision_selected_values(decision.get("value")))
            if not expected_values:
                raise ValueError(
                    f"Confirmed entity decision {key} requires selected value(s)"
                )
        requirements.append(
            ContractRequirement(
                key=key,
                kind=kind,
                label=str(decision.get("label") or decision.get("key") or "").strip(),
                bindings=bindings,
                expected_values=expected_values,
                match_any_identifier=kind == "entity",
            )
        )
        seen_keys.add(key)
    return QueryContract(
        requirements=tuple(requirements),
        time_intent=dict(time_intent) if time_intent else None,
    )
