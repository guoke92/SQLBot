"""K4 VQR — Verified Query Reuse short-circuit."""

from __future__ import annotations

import re
from typing import Any

from pydantic import BaseModel, Field

from apps.knowledge.compile.bundle import ApplyHit
from apps.knowledge.policy import KnowledgePolicy


class ReuseResult(BaseModel):
    exemplar_id: int | None = None
    lineage_id: str | None = None
    original_sql: str
    rebound_sql: str
    skeleton: str
    rebind_map: dict[str, str] = Field(default_factory=dict)
    confidence: float


_LITERAL_RE = re.compile(r"'(?:[^'\\]|\\.)*'|\"(?:[^\"\\]|\\.)*\"|\b\d+(?:\.\d+)?\b")


def _sql_skeleton(sql: str) -> tuple[str, list[str]]:
    """Replace string/numeric literals with ``?`` and return (skeleton, literals)."""
    literals: list[str] = []

    def _replace(m: re.Match[str]) -> str:
        literals.append(m.group(0))
        return "?"

    skeleton = _LITERAL_RE.sub(_replace, sql)
    return skeleton, literals


def try_reuse(
    *,
    question: str,
    examples: list[dict[str, Any]],
    policy: KnowledgePolicy,
) -> ReuseResult | None:
    """Attempt SQL reuse from a certified exemplar.

    A hit requires: certified tier, similarity above the policy threshold, and
    every SQL literal present verbatim in the current question (no guessing —
    an unmatched literal means the value context changed, so we fall through
    to normal LLM generation with the exemplar as an Exemplify hint instead).
    """
    if not policy.reuse_enabled:
        return None

    threshold = policy.reuse_similarity_threshold
    question_tokens = set(re.findall(r"\w+", question))

    for ex in examples:
        if (ex.get("trust_tier") or "") != "certified" or not ex.get("sql"):
            continue
        similarity = float(ex.get("similarity") or 0)
        if similarity < threshold:
            continue

        exemplar_sql: str = ex["sql"]
        skeleton, literals = _sql_skeleton(exemplar_sql)
        if any(lit.strip("'\"") not in question_tokens for lit in literals):
            continue

        return ReuseResult(
            exemplar_id=ex.get("id"),
            lineage_id=(ex.get("knowledge_meta") or {}).get("lineage_id"),
            original_sql=exemplar_sql,
            rebound_sql=exemplar_sql,
            skeleton=skeleton,
            confidence=similarity,
        )

    return None


def build_reuse_apply_hit(result: ReuseResult) -> ApplyHit:
    return ApplyHit(
        asset_kind="example",
        asset_id=result.exemplar_id,
        lineage_id=result.lineage_id,
        trust_tier="certified",
        apply="reuse",
        reason="vqr_short_circuit",
        meta={
            "skeleton": result.skeleton,
            "rebind_map": result.rebind_map,
            "confidence": result.confidence,
        },
    )
