"""Apply certified BoundCaliber fragments into the current-turn draft."""

from __future__ import annotations

from typing import Any

from apps.chat.contract.issues import has_user_evidence
from apps.knowledge.compile.bundle import ApplyHit, BoundCaliber, CompiledKnowledge
from apps.knowledge.natural_key import clause_of


def _req_key(req: dict[str, Any]) -> str:
    """Slot identity ignores operation/value so user evidence blocks Bind on same field."""
    field = ""
    ref = req.get("field") or req.get("output") or {}
    if isinstance(ref, dict):
        field = f"{ref.get('resource', '')}.{ref.get('field', '')}"
    return f"{clause_of(req)}:{field}"


def _comparable(value: Any) -> Any:
    if isinstance(value, (list, tuple)):
        return [_comparable(item) for item in value]
    if isinstance(value, dict):
        return {str(k): _comparable(v) for k, v in sorted(value.items())}
    return value


def _slot_values(req: dict[str, Any]) -> Any | None:
    """QueryContract predicates use ``values``; accept legacy ``value`` too."""
    if "values" in req:
        raw = req.get("values")
        if isinstance(raw, (list, tuple)):
            return _comparable(list(raw))
        return _comparable([raw])
    if "value" in req:
        raw = req.get("value")
        if isinstance(raw, (list, tuple)):
            return _comparable(list(raw))
        return _comparable([raw])
    return None


def _conflict(a: dict[str, Any], b: dict[str, Any]) -> bool:
    """Same slot key but different operation/operator/mode/values."""
    for key in ("operation", "operator", "mode"):
        if key in a and key in b and a.get(key) != b.get(key):
            return True
    left = _slot_values(a)
    right = _slot_values(b)
    if left is not None and right is not None and left != right:
        return True
    return False


def _normalize_requirement(req: dict[str, Any]) -> dict[str, Any]:
    """Ensure dumped shape uses ``clause`` (QueryContract field)."""
    out = dict(req)
    if "clause" not in out:
        clause = out.pop("clause_type", None) or out.pop("type", None)
        if clause:
            out["clause"] = clause
    return out


def apply_bound_calibers_to_intent(
    intent_context: dict[str, Any],
    compiled: CompiledKnowledge | None,
) -> tuple[dict[str, Any], list[ApplyHit]]:
    """Prefill **draft** requirements from Bind; user evidence always wins (P0).

    Never writes a frozen ``contract`` while status is evaluating/needs_clarification
    — IntentContext forbids non-null contract outside ready/blocked.
    """
    if compiled is None or not compiled.bound_calibers:
        return intent_context, []

    ctx = dict(intent_context)
    draft = dict(ctx.get("draft") or {})
    existing = list(draft.get("requirements") or [])
    extra_log: list[ApplyHit] = []
    occupied = {_req_key(req): req for req in existing if isinstance(req, dict)}

    for bound in compiled.bound_calibers:
        fragment = bound.fragment or {}
        for req in fragment.get("requirements") or []:
            if not isinstance(req, dict):
                continue
            req = _normalize_requirement(req)
            key = _req_key(req)
            current = occupied.get(key)
            if current is not None and has_user_evidence(
                current.get("evidence_refs") or []
            ):
                extra_log.append(
                    ApplyHit(
                        asset_kind="caliber",
                        asset_id=bound.caliber_id,
                        lineage_id=bound.lineage_id,
                        trust_tier=bound.trust_tier,
                        apply="drop",
                        reason="user_turn_override",
                        meta={"slot_key": key, "label": bound.label},
                    )
                )
                continue
            if current is not None and _conflict(current, req):
                extra_log.append(
                    ApplyHit(
                        asset_kind="caliber",
                        asset_id=bound.caliber_id,
                        lineage_id=bound.lineage_id,
                        trust_tier=bound.trust_tier,
                        apply="clarify",
                        reason="caliber_slot_conflict",
                        meta={"slot_key": key, "label": bound.label},
                    )
                )
                continue
            # Do not silently overwrite a non-empty model inference without conflict
            # when it already has values — only fill empty slots or identical keys.
            merged = dict(req)
            merged["source"] = "knowledge"
            refs = list(merged.get("evidence_refs") or [])
            caliber_ref = f"knowledge:caliber:{bound.caliber_id}"
            if caliber_ref not in refs:
                refs.append(caliber_ref)
            merged["evidence_refs"] = refs
            if current is None:
                existing.append(merged)
                occupied[key] = merged
            else:
                # Prefer knowledge fill only for missing keys; keep current slot_id/label
                filled = {**merged, **{k: v for k, v in current.items() if v not in (None, "", [], {})}}
                # Knowledge still wins source + evidence when we intentionally bind
                filled["source"] = "knowledge"
                filled["evidence_refs"] = merged["evidence_refs"]
                for k, v in merged.items():
                    if k not in ("slot_id", "label") and (
                        k not in current or current.get(k) in (None, "", [], {})
                    ):
                        filled[k] = v
                    elif k in (
                        "operation",
                        "operator",
                        "value",
                        "values",
                        "mode",
                        "field",
                        "output",
                    ):
                        # Same key, no conflict branch → align to certified caliber
                        filled[k] = v
                idx = existing.index(current)
                existing[idx] = filled
                occupied[key] = filled

    draft["requirements"] = existing
    if "version" not in draft:
        draft["version"] = 4
    ctx["draft"] = draft

    # Keep frozen contract only on terminal statuses.
    status = str(ctx.get("status") or "")
    if status not in ("ready", "blocked"):
        ctx["contract"] = None

    if compiled.bound_calibers:
        hints = list(ctx.get("knowledge_bind_labels") or [])
        for bound in compiled.bound_calibers:
            if bound.label and bound.label not in hints:
                hints.append(bound.label)
        ctx["knowledge_bind_labels"] = hints
    return ctx, extra_log


def render_bind_lock_line(bound_calibers: list[BoundCaliber]) -> str:
    if not bound_calibers:
        return ""
    labels = ", ".join(b.label for b in bound_calibers if b.label)
    return f"已锁定业务口径（知识库认证）：{labels}" if labels else ""
