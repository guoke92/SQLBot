"""Natural-key normalization for the node store (ADR v3.1 D6/D7).

Keys are stable physical or namespace-scoped identities used for
cross-package deduplication at the decomposer's merge point (M2).
"""

from __future__ import annotations


def norm(value: str) -> str:
    """Casefold and drop all whitespace."""
    return "".join((value or "").casefold().split())


def dataset_key(database: str, name: str) -> str:
    """Physical dataset key: database.table, or bare table when no database.

    Packages may omit the database (single-schema datasources); a bare-table
    key merges with any explicit database key ONLY when the database part is
    absent on both sides. Same table name under different explicit databases
    stays separate and surfaces as a merge conflict at persist time.
    """
    table = norm(name)
    db = norm(database)
    return f"{db}.{table}" if db else table


def field_key(parent_dataset_key: str, field_name: str) -> str:
    return f"{parent_dataset_key}.{norm(field_name)}"


def concept_key(namespace: str, concept_id: str) -> str:
    return f"{norm(namespace)}:{norm(concept_id)}"


def stage_key(unit_key: str, stage_id: str) -> str:
    return f"{unit_key}:{norm(stage_id)}"


def unit_scoped_key(unit_key: str, local_id: str) -> str:
    """Key for unit-owned nodes: caliber/rule/metric/pattern."""
    return f"{unit_key}:{norm(local_id)}"


def unit_key_for(namespace: str, unit_id: str) -> str:
    return f"{norm(namespace)}:{norm(unit_id)}"
