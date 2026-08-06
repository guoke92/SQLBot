"""One canonical model for every expected contract failure.

Contract *model invariants* still raise: they denote invalid program state.
Everything a user or the planner can legitimately hit at runtime is a
``ContractIssue``, so one rule can never produce three different consequences
depending on which caller happened to detect it.

Severity follows the layer of the clauses that caused the issue.  A clause is
confirmed only when its evidence points at something the user actually said;
anything else is a system inference and stays revocable.  An issue caused only
by inferences is therefore ``advisory``: it is resolved by dropping the
inference and stating the assumption, never by blocking the user.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

IssueSeverity = Literal["advisory", "blocking"]

# Only ``user:`` marks a confirmed business choice; the model cannot promote
# its own inference by inventing an unknown namespace.
USER_EVIDENCE_PREFIX = "user:"
QUESTION_EVIDENCE = "user:question"


def answer_evidence(question_id: str) -> str:
    """Return the evidence ref that marks a clause as answered by the user."""
    return f"user:answer:{question_id}"


def has_user_evidence(evidence_refs: Iterable[str]) -> bool:
    """Report whether a clause traces back to something the user said."""
    return any(
        str(ref).strip().casefold().startswith(USER_EVIDENCE_PREFIX)
        for ref in evidence_refs
    )


def is_inferred_evidence(evidence_refs: Iterable[str]) -> bool:
    """Whether provenance is known and cites nothing the user said.

    Absent provenance is deliberately *not* treated as an inference.  Deciding
    on the user's behalf must require positive evidence that the system
    invented the question, so an assessor that ignores the evidence convention
    degrades to asking — never to answering silently.
    """
    refs = [str(ref).strip() for ref in evidence_refs if str(ref).strip()]
    return bool(refs) and not has_user_evidence(refs)


class ContractIssue(BaseModel):
    """A classified, expected contract problem with one routing decision."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    code: str
    severity: IssueSeverity
    slot_ids: tuple[str, ...] = ()
    resources: tuple[str, ...] = ()
    params: dict[str, str] = Field(default_factory=dict)


class ContractAssumption(BaseModel):
    """One inference the system made on the user's behalf, stated openly."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    slot_id: str
    code: str
    label: str
    detail: str = ""


def blocking_issues(issues: Iterable[ContractIssue]) -> list[ContractIssue]:
    return [issue for issue in issues if issue.severity == "blocking"]
