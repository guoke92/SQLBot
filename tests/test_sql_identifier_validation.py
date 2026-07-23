"""Regression tests for scope-aware physical SQL identifier extraction."""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

_apps_module = sys.modules.get("apps")
if _apps_module is not None and not getattr(_apps_module, "__path__", None):
    for _module_name in list(sys.modules):
        if _module_name == "apps" or _module_name.startswith("apps."):
            sys.modules.pop(_module_name, None)

from apps.protocol.sql.identifier_validation import (  # noqa: E402
    PhysicalColumnRef,
    collect_sql_identifier_usage,
)


def _usage(sql: str):
    return collect_sql_identifier_usage(sql, "mysql")


def test_cte_names_are_not_physical_tables() -> None:
    usage = _usage(
        """
        WITH task_stats AS (
            SELECT t.project_id AS system_id, COUNT(*) AS task_count
            FROM d_task t
            GROUP BY t.project_id
        )
        SELECT stats.system_id, stats.task_count
        FROM task_stats stats
        """
    )

    assert usage.physical_tables == frozenset({"d_task"})
    assert usage.physical_columns == (
        PhysicalColumnRef(table_name="d_task", column_name="project_id"),
    )


def test_derived_alias_outputs_do_not_collide_with_inner_table_alias() -> None:
    usage = _usage(
        """
        SELECT t.month, t.task_count
        FROM (
            SELECT DATE_FORMAT(t.create_time, '%Y-%m') AS month,
                   COUNT(*) AS task_count
            FROM d_task t
            GROUP BY month
        ) t
        """
    )

    assert usage.physical_tables == frozenset({"d_task"})
    assert usage.physical_columns == (
        PhysicalColumnRef(table_name="d_task", column_name="create_time"),
    )


def test_unknown_physical_column_is_still_collected() -> None:
    usage = _usage("SELECT t.not_exists FROM d_task t")

    assert usage.physical_columns == (
        PhysicalColumnRef(table_name="d_task", column_name="not_exists"),
    )


def test_physical_table_hidden_in_cte_still_hits_allow_list() -> None:
    usage = _usage(
        """
        WITH hidden AS (SELECT s.id FROM secret_story s)
        SELECT h.id FROM hidden h
        """
    )

    assert usage.physical_tables == frozenset({"secret_story"})


def test_unqualified_group_alias_is_not_a_physical_column() -> None:
    usage = _usage(
        """
        SELECT DATE_FORMAT(create_time, '%Y-%m') AS month, COUNT(*) AS total
        FROM d_task
        GROUP BY month
        ORDER BY month
        """
    )

    assert usage.physical_columns == (
        PhysicalColumnRef(
            column_name="create_time",
            candidate_tables=("d_task",),
        ),
    )
