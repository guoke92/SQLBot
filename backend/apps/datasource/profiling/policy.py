"""Resolve DS/table mining policies into EffectivePolicy."""

from __future__ import annotations

from typing import Any, Mapping

from apps.datasource.profiling.capability_catalog import (
    EffectivePolicy,
    agent_capabilities,
    expand_capabilities,
    facts_capabilities,
    preset_capabilities,
)


def _as_mapping(raw: Any) -> dict[str, Any] | None:
    if raw is None:
        return None
    if isinstance(raw, Mapping):
        return dict(raw)
    return None


def _policy_from_doc(doc: Mapping[str, Any] | None, *, source: str) -> EffectivePolicy | None:
    if not doc:
        return None
    if doc.get("inherit") is True:
        return None
    preset = str(doc.get("preset") or "lite").strip().lower()
    caps_raw = doc.get("capabilities")
    if preset == "custom":
        if not isinstance(caps_raw, (list, tuple, set)):
            raise ValueError("custom mining_policy requires capabilities list")
        selected = [str(x) for x in caps_raw]
        closed = expand_capabilities(selected)
        return EffectivePolicy(
            preset="custom",
            capabilities=closed,
            facts_caps=facts_capabilities(closed),
            agent_caps=agent_capabilities(closed),
            source=source,
        )
    base = set(preset_capabilities(preset))
    if isinstance(caps_raw, (list, tuple, set)):
        base |= {str(x) for x in caps_raw}
    closed = expand_capabilities(base)
    return EffectivePolicy(
        preset=preset if preset in {"lite", "standard", "deep"} else "lite",
        capabilities=closed,
        facts_caps=facts_capabilities(closed),
        agent_caps=agent_capabilities(closed),
        source=source,
    )


def resolve_mining_policy(
    *,
    ds_policy: Any = None,
    table_policy: Any = None,
    default_preset: str = "lite",
) -> EffectivePolicy:
    """Table override > DS default > system preset (default lite = facts only)."""
    table_doc = _as_mapping(table_policy)
    resolved = _policy_from_doc(table_doc, source="table")
    if resolved is not None:
        return resolved
    ds_doc = _as_mapping(ds_policy)
    resolved = _policy_from_doc(ds_doc, source="ds")
    if resolved is not None:
        return resolved
    closed = expand_capabilities(preset_capabilities(default_preset))
    return EffectivePolicy(
        preset=default_preset if default_preset in {"lite", "standard", "deep"} else "lite",
        capabilities=closed,
        facts_caps=facts_capabilities(closed),
        agent_caps=agent_capabilities(closed),
        source="default",
    )


def policy_to_public_dict(policy: EffectivePolicy) -> dict[str, Any]:
    return {
        "preset": policy.preset,
        "source": policy.source,
        "capabilities": sorted(policy.capabilities),
        "facts_caps": sorted(policy.facts_caps),
        "agent_caps": sorted(policy.agent_caps),
        "has_agent_work": policy.has_agent_work(),
    }
