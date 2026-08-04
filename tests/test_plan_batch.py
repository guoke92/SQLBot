"""Atomic generated plan batch contract tests."""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import orjson

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.chat.planning import parse_query_generation  # noqa: E402
from apps.protocol import QueryPlan  # noqa: E402
from apps.protocol.rest.protocol import RestProtocol  # noqa: E402
from apps.protocol.sql.protocol import SqlProtocol  # noqa: E402
from common.utils.json_utils import extract_nested_json  # noqa: E402


class FakeProtocol:
    def supports(self, _capability: str) -> bool:
        return True

    def parse_llm_output(self, text: str) -> QueryPlan:
        data = orjson.loads(text)
        if not data.get("success"):
            return QueryPlan(success=False, message=data.get("message") or "invalid")
        sql = data.get("sql") or ""
        return QueryPlan(
            success=True,
            statement=sql,
            payload={"sql": sql},
            resources=data.get("tables") or [],
            chart_type=data.get("chart-type"),
            brief=data.get("brief"),
        )

    def validate_plan(
        self,
        _ds: object,
        plan: QueryPlan,
        _allowed_resources: list[str],
    ) -> QueryPlan:
        if "bad_column" in plan.statement:
            return plan.model_copy(
                update={"success": False, "message": "unknown column bad_column"}
            )
        return plan.model_copy(update={"resources": ["physical_table"]})

    def format_statement_for_display(self, plan: QueryPlan) -> str:
        return plan.statement


def service() -> SimpleNamespace:
    return SimpleNamespace(
        protocol=FakeProtocol(),
        ds=object(),
        table_name_list=["physical_table"],
        chat_question=SimpleNamespace(
            question="汇总今年签收额和融资额",
            intent_context=None,
        ),
    )


def test_mixed_valid_invalid_batch_is_rejected_atomically() -> None:
    raw = orjson.dumps(
        [
            {"success": True, "sql": "SELECT 1", "tables": ["claimed"]},
            {
                "success": True,
                "sql": "SELECT bad_column FROM physical_table",
                "tables": ["physical_table"],
            },
        ]
    ).decode()
    result = parse_query_generation(raw, service(), max_batch_size=3)

    assert result.success is False
    assert result.plans == []
    assert result.plan_validated is False
    assert result.contract_satisfied is False
    assert "计划 2" in (result.error_message or "")


def test_validated_physical_resources_replace_model_claim() -> None:
    raw = orjson.dumps(
        {"success": True, "sql": "SELECT 1", "tables": ["claimed"]}
    ).decode()
    result = parse_query_generation(raw, service(), max_batch_size=3)

    assert result.success is True
    assert result.plan_validated is True
    assert result.contract_satisfied is True
    assert result.plans[0]["tables"] == ["physical_table"]
    assert result.plans[0]["brief"] == "汇总今年签收额和融资额"


def test_current_plan_brief_is_not_inherited_from_rejected_attempt() -> None:
    raw = orjson.dumps(
        {
            "success": True,
            "sql": "SELECT 1",
            "brief": "",
        }
    ).decode()

    result = parse_query_generation(raw, service(), max_batch_size=3)

    assert result.plans[0]["brief"] == "汇总今年签收额和融资额"


def test_clarification_text_is_not_used_as_result_title() -> None:
    llm_service = service()
    llm_service.chat_question.question = "已确认查询口径：请确认签收额和融资额"
    llm_service.chat_question.generation_question = "汇总今年签收额和融资额"
    raw = orjson.dumps(
        {
            "success": True,
            "sql": "SELECT 1",
            "brief": "模型生成的临时标题",
        }
    ).decode()

    result = parse_query_generation(raw, llm_service, max_batch_size=3)

    assert result.plans[0]["brief"] == "汇总今年签收额和融资额"


def test_result_title_is_derived_from_confirmed_business_contract() -> None:
    llm_service = service()
    llm_service.chat_question.intent_context = {
        "decisions": [
            {
                "key": "dimension.company",
                "kind": "dimension",
                "label": "企业",
                "locked": True,
                "bindings": [
                    {
                        "identifier": "company_name",
                        "role": "group",
                        "aggregation": "none",
                    }
                ],
                "value": "按企业",
            },
            {
                "key": "metric.signed_amount",
                "kind": "metric",
                "label": "累计签收额",
                "locked": True,
                "bindings": [
                    {"identifier": "amount", "role": "measure", "aggregation": "sum"}
                ],
                "value": "合计",
            },
        ]
    }

    result = parse_query_generation(
        orjson.dumps(
            {
                "success": True,
                "sql": "SELECT company_name, SUM(amount) FROM asset",
                "brief": "模型临时标题",
            }
        ).decode(),
        llm_service,
        max_batch_size=3,
    )

    assert result.plans[0]["brief"] == "按企业统计累计签收额"
    assert result.plans[0]["presentation_title"] == "按企业统计累计签收额"


def test_result_title_excludes_display_attributes_from_grouping() -> None:
    llm_service = service()
    llm_service.chat_question.intent_context = {
        "decisions": [
            {
                "key": "grain.enterprise",
                "kind": "grain",
                "label": "企业主体",
                "locked": True,
                "bindings": [
                    {
                        "identifier": "company_name",
                        "role": "group",
                        "aggregation": "none",
                    }
                ],
            },
            {
                "key": "dimension.supplier_level",
                "kind": "dimension",
                "label": "供应商层级",
                "locked": True,
                "bindings": [
                    {
                        "identifier": "apply_level",
                        "role": "attribute",
                        "aggregation": "min",
                    }
                ],
            },
            {
                "key": "metric.signed_amount",
                "kind": "metric",
                "label": "累计签收额",
                "locked": True,
                "bindings": [
                    {
                        "identifier": "orig_asset_amt",
                        "role": "measure",
                        "aggregation": "sum",
                    }
                ],
            },
        ]
    }

    result = parse_query_generation(
        (
            '{"success":true,"sql":"SELECT company_name, '
            "MIN(apply_level), SUM(orig_asset_amt) FROM asset "
            'GROUP BY company_name"}'
        ),
        llm_service,
        max_batch_size=3,
    )

    assert result.plans[0]["presentation_title"] == "按企业主体统计累计签收额"
    assert "供应商层级" not in result.plans[0]["presentation_title"]


def test_batch_over_limit_is_rejected_instead_of_truncated() -> None:
    raw = orjson.dumps(
        [{"success": True, "sql": f"SELECT {index}"} for index in range(4)]
    ).decode()
    result = parse_query_generation(raw, service(), max_batch_size=3)

    assert result.success is False
    assert "超过单批上限" in (result.error_message or "")


def test_batch_must_implement_required_contract_identifiers() -> None:
    llm_service = service()
    llm_service.chat_question.intent_context = {
        "decisions": [
            {
                "key": "relation.finance_asset.keys",
                "kind": "relation",
                "label": "关联字段",
                "locked": True,
                "bindings": [
                    {
                        "identifier": "company_name",
                        "role": "join",
                        "aggregation": "none",
                    },
                    {
                        "identifier": "core_company_id",
                        "role": "join",
                        "aggregation": "none",
                    },
                ],
                "value": "company_name + core_company_id",
            }
        ]
    }

    rejected = parse_query_generation(
        orjson.dumps(
            {
                "success": True,
                "sql": (
                    "SELECT * FROM finance f JOIN asset a "
                    "ON f.company_name = a.company_name"
                ),
            }
        ).decode(),
        llm_service,
        max_batch_size=3,
    )

    assert rejected.success is False
    assert "core_company_id" in (rejected.error_message or "")

    accepted = parse_query_generation(
        orjson.dumps(
            {
                "success": True,
                "sql": (
                    "SELECT * FROM finance f JOIN asset a "
                    "ON f.company_name = a.company_name "
                    "AND f.core_company_id = a.core_company_id"
                ),
            }
        ).decode(),
        llm_service,
        max_batch_size=3,
    )

    assert accepted.success is True


def test_contract_identifier_must_appear_in_its_business_clause() -> None:
    llm_service = service()
    llm_service.chat_question.intent_context = {
        "decisions": [
            {
                "key": "scope.department",
                "kind": "scope",
                "label": "部门范围",
                "locked": True,
                "bindings": [
                    {
                        "identifier": "department_name",
                        "role": "filter",
                        "aggregation": "none",
                    }
                ],
                "value": "研发二部",
            }
        ]
    }

    rejected = parse_query_generation(
        orjson.dumps(
            {
                "success": True,
                "sql": "SELECT department_name, COUNT(*) FROM task",
            }
        ).decode(),
        llm_service,
        max_batch_size=3,
    )
    accepted = parse_query_generation(
        orjson.dumps(
            {
                "success": True,
                "sql": ("SELECT COUNT(*) FROM task WHERE department_name = '研发二部'"),
            }
        ).decode(),
        llm_service,
        max_batch_size=3,
    )

    assert rejected.success is False
    assert "correct clause" in (rejected.error_message or "")
    assert accepted.success is True


def test_batch_rejects_competing_plans_for_same_contract() -> None:
    llm_service = service()
    llm_service.chat_question.intent_context = {
        "decisions": [
            {
                "key": "metric.amount",
                "kind": "metric",
                "label": "金额",
                "locked": True,
                "bindings": [
                    {"identifier": "amount", "role": "measure", "aggregation": "sum"}
                ],
                "value": "SUM(amount)",
            }
        ]
    }
    raw = orjson.dumps(
        [
            {
                "success": True,
                "sql": "SELECT SUM(amount) AS total FROM orders",
            },
            {
                "success": True,
                "sql": "SELECT AVG(amount) AS total FROM orders",
            },
        ]
    ).decode()

    result = parse_query_generation(raw, llm_service, max_batch_size=3)

    assert result.success is False
    assert "requires SUM but uses AVG" in (result.error_message or "")


def test_dimension_contract_rejects_min_max_or_null_placeholder() -> None:
    llm_service = service()
    llm_service.chat_question.intent_context = {
        "decisions": [
            {
                "key": "grain.asset_level",
                "kind": "grain",
                "label": "资产层级",
                "locked": True,
                "bindings": [
                    {
                        "identifier": "apply_level",
                        "role": "group",
                        "aggregation": "none",
                    }
                ],
                "value": "按资产层级",
            }
        ]
    }

    collapsed = parse_query_generation(
        orjson.dumps(
            {
                "success": True,
                "sql": (
                    "SELECT company_name, MAX(apply_level) AS apply_level, "
                    "SUM(amount) FROM asset GROUP BY company_name"
                ),
            }
        ).decode(),
        llm_service,
        max_batch_size=3,
    )
    placeholder = parse_query_generation(
        orjson.dumps(
            {
                "success": True,
                "sql": (
                    "SELECT company_name, CAST(NULL AS SIGNED) AS apply_level, "
                    "SUM(amount) FROM asset GROUP BY company_name"
                ),
            }
        ).decode(),
        llm_service,
        max_batch_size=3,
    )

    assert collapsed.success is False
    assert "MAX" in (collapsed.error_message or "")
    assert placeholder.success is False
    assert "projected as NULL" in (placeholder.error_message or "")


def test_confirmed_calculation_can_aggregate_a_dimension_identifier() -> None:
    llm_service = service()
    llm_service.chat_question.intent_context = {
        "decisions": [
            {
                "key": "grain.asset_level",
                "kind": "grain",
                "label": "资产层级",
                "locked": True,
                "bindings": [
                    {
                        "identifier": "apply_level",
                        "role": "group",
                        "aggregation": "none",
                    }
                ],
                "value": "按企业展示代表层级",
            },
            {
                "key": "calculation.asset_level",
                "kind": "calculation",
                "label": "资产层级取值方式",
                "locked": True,
                "bindings": [
                    {
                        "identifier": "apply_level",
                        "role": "measure",
                        "aggregation": "max",
                    }
                ],
                "value": "每家企业取最高资产层级",
            },
        ]
    }

    result = parse_query_generation(
        orjson.dumps(
            {
                "success": True,
                "sql": (
                    "SELECT company_name, MAX(apply_level) AS apply_level "
                    "FROM asset GROUP BY company_name"
                ),
            }
        ).decode(),
        llm_service,
        max_batch_size=3,
    )

    assert result.success is True

    wrong_aggregation = parse_query_generation(
        orjson.dumps(
            {
                "success": True,
                "sql": (
                    "SELECT company_name, MIN(apply_level) AS apply_level "
                    "FROM asset GROUP BY company_name"
                ),
            }
        ).decode(),
        llm_service,
        max_batch_size=3,
    )

    assert wrong_aggregation.success is False
    assert "MIN" in (wrong_aggregation.error_message or "")


def test_metric_aggregation_is_validated_through_cte_lineage() -> None:
    llm_service = service()
    llm_service.chat_question.intent_context = {
        "decisions": [
            {
                "key": "metric.amount",
                "kind": "metric",
                "label": "最高金额",
                "locked": True,
                "bindings": [
                    {"identifier": "amount", "role": "measure", "aggregation": "max"}
                ],
                "value": "最高金额",
            }
        ]
    }

    accepted = parse_query_generation(
        orjson.dumps(
            {
                "success": True,
                "sql": (
                    "WITH stats AS (SELECT MAX(amount) AS total FROM asset) "
                    "SELECT total FROM stats"
                ),
            }
        ).decode(),
        llm_service,
        max_batch_size=3,
    )
    rejected = parse_query_generation(
        orjson.dumps(
            {
                "success": True,
                "sql": (
                    "WITH stats AS (SELECT MIN(amount) AS total FROM asset) "
                    "SELECT total FROM stats"
                ),
            }
        ).decode(),
        llm_service,
        max_batch_size=3,
    )

    assert accepted.success is True
    assert rejected.success is False
    assert "requires MAX but uses MIN" in (rejected.error_message or "")


def test_count_distinct_aggregation_is_recognized() -> None:
    llm_service = service()
    llm_service.chat_question.intent_context = {
        "decisions": [
            {
                "key": "metric.company_count",
                "kind": "metric",
                "label": "企业数",
                "locked": True,
                "bindings": [
                    {
                        "identifier": "company_id",
                        "role": "measure",
                        "aggregation": "count_distinct",
                    }
                ],
                "value": "去重企业数",
            }
        ]
    }

    result = parse_query_generation(
        orjson.dumps(
            {
                "success": True,
                "sql": "SELECT COUNT(DISTINCT company_id) FROM asset",
            }
        ).decode(),
        llm_service,
        max_batch_size=3,
    )

    assert result.success is True


def test_multiple_confirmed_aggregations_can_share_one_source_field() -> None:
    llm_service = service()
    llm_service.chat_question.intent_context = {
        "decisions": [
            {
                "key": "metric.amount.max",
                "kind": "metric",
                "label": "最高金额",
                "locked": True,
                "bindings": [
                    {"identifier": "amount", "role": "measure", "aggregation": "max"}
                ],
                "value": "最高金额",
            },
            {
                "key": "metric.amount.min",
                "kind": "metric",
                "label": "最低金额",
                "locked": True,
                "bindings": [
                    {"identifier": "amount", "role": "measure", "aggregation": "min"}
                ],
                "value": "最低金额",
            },
        ]
    }

    result = parse_query_generation(
        orjson.dumps(
            {
                "success": True,
                "sql": "SELECT MAX(amount), MIN(amount) FROM asset",
            }
        ).decode(),
        llm_service,
        max_batch_size=3,
    )

    assert result.success is True


def test_role_aware_contract_accepts_metric_dates_and_reduced_attributes() -> None:
    """Regression for chat 79: filters must not inherit measure aggregation."""
    llm_service = service()
    llm_service.chat_question.intent_context = {
        "decisions": [
            {
                "key": "grain.company",
                "kind": "grain",
                "label": "原始供应商",
                "locked": True,
                "bindings": [
                    {
                        "identifier": "company_name",
                        "role": "group",
                        "aggregation": "none",
                    }
                ],
            },
            {
                "key": "dimension.core_company",
                "kind": "dimension",
                "label": "核企名称",
                "locked": True,
                "bindings": [
                    {
                        "identifier": "core_company_name",
                        "role": "attribute",
                        "aggregation": "distinct_concat",
                    }
                ],
            },
            {
                "key": "dimension.supplier_level",
                "kind": "dimension",
                "label": "资产层级",
                "locked": True,
                "bindings": [
                    {
                        "identifier": "apply_level",
                        "role": "attribute",
                        "aggregation": "min",
                    }
                ],
            },
            {
                "key": "metric.signed_amount",
                "kind": "metric",
                "label": "累计签收额",
                "locked": True,
                "bindings": [
                    {
                        "identifier": "orig_asset_amt",
                        "role": "measure",
                        "aggregation": "sum",
                    },
                    {
                        "identifier": "sign_date",
                        "role": "filter",
                        "aggregation": "none",
                    },
                ],
            },
            {
                "key": "metric.financed_amount",
                "kind": "metric",
                "label": "累积融资额",
                "locked": True,
                "bindings": [
                    {
                        "identifier": "fin_apply_amt",
                        "role": "measure",
                        "aggregation": "sum",
                    },
                    {
                        "identifier": "fin_apply_date",
                        "role": "filter",
                        "aggregation": "none",
                    },
                ],
            },
        ]
    }
    sql = (
        "SELECT company_name, "
        "GROUP_CONCAT(DISTINCT core_company_name) AS core_company_name, "
        "MIN(apply_level) AS apply_level, "
        "SUM(CASE WHEN sign_date >= '2026-01-01' "
        "AND sign_date < '2027-01-01' THEN orig_asset_amt ELSE 0 END) AS sign_amt, "
        "SUM(CASE WHEN fin_apply_date >= '2026-01-01' "
        "AND fin_apply_date < '2027-01-01' THEN fin_apply_amt ELSE 0 END) AS fin_amt "
        "FROM finance WHERE company_name IS NOT NULL "
        "AND ((sign_date >= '2026-01-01' AND sign_date < '2027-01-01') "
        "OR (fin_apply_date >= '2026-01-01' AND fin_apply_date < '2027-01-01')) "
        "GROUP BY company_name"
    )

    result = parse_query_generation(
        orjson.dumps({"success": True, "sql": sql}).decode(),
        llm_service,
        max_batch_size=3,
        time_intent={
            "scope": "explicit",
            "start": "2026-01-01",
            "end_exclusive": "2027-01-01",
        },
    )

    assert result.success is True


def test_distinct_concat_order_is_projection_evidence_through_cte_lineage() -> None:
    """Regression for chat 85: aggregate-local ORDER is not result ordering."""
    llm_service = service()
    llm_service.protocol.type_key = "starrocks"
    llm_service.chat_question.intent_context = {
        "decisions": [
            {
                "key": "dimension.supplier_level",
                "kind": "dimension",
                "label": "供应商层级",
                "locked": True,
                "bindings": [
                    {
                        "identifier": "finance.apply_level",
                        "role": "attribute",
                        "aggregation": "distinct_concat",
                    }
                ],
            }
        ]
    }
    sql = (
        "WITH supplier_levels AS ("
        "SELECT company_name, "
        "GROUP_CONCAT(DISTINCT apply_level ORDER BY apply_level SEPARATOR ',') "
        "AS supplier_level FROM finance "
        "WHERE apply_level IS NOT NULL GROUP BY company_name"
        ") SELECT company_name, supplier_level FROM supplier_levels"
    )

    result = parse_query_generation(
        orjson.dumps({"success": True, "sql": sql}).decode(),
        llm_service,
        max_batch_size=3,
    )

    assert result.success is True


def test_explicit_time_boundaries_are_part_of_the_query_contract() -> None:
    time_intent = {
        "scope": "explicit",
        "start": "2026-01-01",
        "end_exclusive": "2027-01-01",
    }

    accepted = parse_query_generation(
        orjson.dumps(
            {
                "success": True,
                "sql": (
                    "SELECT SUM(amount) FROM asset "
                    "WHERE created_at >= '2026-01-01' "
                    "AND created_at < '2027-01-01'"
                ),
            }
        ).decode(),
        service(),
        max_batch_size=3,
        time_intent=time_intent,
    )
    rejected = parse_query_generation(
        orjson.dumps(
            {
                "success": True,
                "sql": "SELECT SUM(amount) FROM asset",
            }
        ).decode(),
        service(),
        max_batch_size=3,
        time_intent=time_intent,
    )

    assert accepted.success is True
    assert rejected.success is False
    assert "2026-01-01" in (rejected.error_message or "")
    assert "2027-01-01" in (rejected.error_message or "")


def test_explicit_time_range_must_cover_every_union_branch() -> None:
    time_intent = {
        "scope": "explicit",
        "start": "2026-01-01",
        "end_exclusive": "2027-01-01",
    }
    missing_branch = parse_query_generation(
        orjson.dumps(
            {
                "success": True,
                "sql": (
                    "SELECT created_at FROM task "
                    "WHERE created_at >= '2026-01-01' "
                    "AND created_at < '2027-01-01' "
                    "UNION ALL SELECT created_at FROM story"
                ),
            }
        ).decode(),
        service(),
        max_batch_size=3,
        time_intent=time_intent,
    )
    complete = parse_query_generation(
        orjson.dumps(
            {
                "success": True,
                "sql": (
                    "SELECT created_at FROM task "
                    "WHERE created_at >= '2026-01-01' "
                    "AND created_at < '2027-01-01' "
                    "UNION ALL SELECT created_at FROM story "
                    "WHERE created_at >= '2026-01-01' "
                    "AND created_at < '2027-01-01'"
                ),
            }
        ).decode(),
        service(),
        max_batch_size=3,
        time_intent=time_intent,
    )

    assert missing_branch.success is False
    assert "set-operation branch" in (missing_branch.error_message or "")
    assert complete.success is True


def test_qualified_contract_identifier_rejects_same_column_from_wrong_table() -> None:
    llm_service = service()
    llm_service.chat_question.intent_context = {
        "decisions": [
            {
                "key": "metric.amount",
                "kind": "metric",
                "label": "融资额",
                "locked": True,
                "bindings": [
                    {
                        "identifier": "finance.amount",
                        "role": "measure",
                        "aggregation": "sum",
                    }
                ],
                "value": "融资额合计",
            }
        ]
    }

    result = parse_query_generation(
        orjson.dumps(
            {
                "success": True,
                "sql": "SELECT SUM(asset.amount) FROM asset",
            }
        ).decode(),
        llm_service,
        max_batch_size=3,
    )

    assert result.success is False
    assert "finance.amount" in (result.error_message or "")


def test_omitted_dimension_does_not_create_an_executable_requirement() -> None:
    llm_service = service()
    llm_service.chat_question.intent_context = {
        "decisions": [
            {
                "key": "dimension.supplier_level",
                "kind": "dimension",
                "label": "供应商层级",
                "locked": True,
                "effect": "omit",
                "bindings": [],
                "value": "不输出",
            },
            {
                "key": "metric.amount",
                "kind": "metric",
                "label": "金额",
                "locked": True,
                "bindings": [
                    {"identifier": "amount", "role": "measure", "aggregation": "sum"}
                ],
                "value": "金额合计",
            },
        ]
    }

    result = parse_query_generation(
        orjson.dumps(
            {
                "success": True,
                "sql": "SELECT SUM(amount) AS amount FROM asset",
            }
        ).decode(),
        llm_service,
        max_batch_size=3,
    )

    assert result.success is True


def test_metric_aggregation_is_validated_through_wrapper_expression() -> None:
    llm_service = service()
    llm_service.chat_question.intent_context = {
        "decisions": [
            {
                "key": "metric.amount",
                "kind": "metric",
                "label": "金额",
                "locked": True,
                "bindings": [
                    {"identifier": "amount", "role": "measure", "aggregation": "sum"}
                ],
                "value": "金额合计",
            }
        ]
    }

    result = parse_query_generation(
        orjson.dumps(
            {
                "success": True,
                "sql": (
                    "WITH stats AS (SELECT MIN(amount) AS total FROM asset) "
                    "SELECT COALESCE(stats.total, 0) AS total FROM stats"
                ),
            }
        ).decode(),
        llm_service,
        max_batch_size=3,
    )

    assert result.success is False
    assert "requires SUM but uses MIN" in (result.error_message or "")


def test_time_contract_requires_comparison_predicates_not_free_literals() -> None:
    time_intent = {
        "scope": "explicit",
        "start": "2026-01-01",
        "end_exclusive": "2027-01-01",
    }
    result = parse_query_generation(
        orjson.dumps(
            {
                "success": True,
                "sql": (
                    "SELECT SUM(amount), '2026-01-01' AS start_value, "
                    "'2027-01-01' AS end_value FROM asset"
                ),
            }
        ).decode(),
        service(),
        max_batch_size=3,
        time_intent=time_intent,
    )

    assert result.success is False
    assert "half-open time range" in (result.error_message or "")


def test_confirmed_entity_value_must_bind_to_its_target_filter_field() -> None:
    llm_service = service()
    llm_service.chat_question.intent_context = {
        "decisions": [
            {
                "key": "entity.department",
                "kind": "entity",
                "label": "部门",
                "locked": True,
                "binding_phrase": "研发二部",
                "bindings": [
                    {
                        "identifier": "d_user.organization_name",
                        "role": "filter",
                        "aggregation": "none",
                    }
                ],
                "value": {"selected_options": [{"id": "value_1", "label": "研发二部"}]},
            }
        ]
    }
    accepted = parse_query_generation(
        orjson.dumps(
            {
                "success": True,
                "sql": ("SELECT id FROM d_user WHERE organization_name = '研发二部'"),
            }
        ).decode(),
        llm_service,
        max_batch_size=3,
    )
    rejected = parse_query_generation(
        orjson.dumps(
            {
                "success": True,
                "sql": "SELECT id FROM d_user WHERE name = '研发二部'",
            }
        ).decode(),
        llm_service,
        max_batch_size=3,
    )

    assert accepted.success is True
    assert rejected.success is False
    assert "required filter field" in (rejected.error_message or "")


def test_dimension_gate_checks_the_public_projection_not_nested_ctes() -> None:
    llm_service = service()
    llm_service.chat_question.intent_context = {
        "decisions": [
            {
                "key": "grain.asset_level",
                "kind": "grain",
                "label": "资产层级",
                "locked": True,
                "bindings": [
                    {
                        "identifier": "apply_level",
                        "role": "group",
                        "aggregation": "none",
                    }
                ],
                "value": "保留资产层级",
            }
        ]
    }

    result = parse_query_generation(
        orjson.dumps(
            {
                "success": True,
                "sql": (
                    "WITH stats AS ("
                    "SELECT company_name, MAX(apply_level) AS max_level "
                    "FROM asset GROUP BY company_name"
                    ") SELECT a.company_name, a.apply_level FROM asset a "
                    "LEFT JOIN stats s ON a.company_name = s.company_name"
                ),
            }
        ).decode(),
        llm_service,
        max_batch_size=3,
    )

    assert result.success is True


def test_dimension_gate_follows_public_projection_through_cte() -> None:
    llm_service = service()
    llm_service.chat_question.intent_context = {
        "decisions": [
            {
                "key": "grain.asset_level",
                "kind": "grain",
                "label": "资产层级",
                "locked": True,
                "bindings": [
                    {
                        "identifier": "apply_level",
                        "role": "group",
                        "aggregation": "none",
                    }
                ],
                "value": "保留资产层级",
            }
        ]
    }

    result = parse_query_generation(
        orjson.dumps(
            {
                "success": True,
                "sql": (
                    "WITH stats AS ("
                    "SELECT company_name, MAX(apply_level) AS apply_level "
                    "FROM asset GROUP BY company_name"
                    ") SELECT company_name, apply_level FROM stats"
                ),
            }
        ).decode(),
        llm_service,
        max_batch_size=3,
    )

    assert result.success is False
    assert "MAX" in (result.error_message or "")


def test_batch_allows_complementary_plans_with_shared_scope() -> None:
    llm_service = service()
    llm_service.chat_question.intent_context = {
        "decisions": [
            {
                "key": "scope.department",
                "kind": "scope",
                "label": "部门范围",
                "locked": True,
                "bindings": [
                    {
                        "identifier": "department_name",
                        "role": "filter",
                        "aggregation": "none",
                    }
                ],
                "value": "研发二部",
            }
        ]
    }
    raw = orjson.dumps(
        [
            {
                "success": True,
                "sql": (
                    "SELECT department_name, COUNT(task_id) FROM task "
                    "WHERE department_name = '研发二部' GROUP BY department_name"
                ),
            },
            {
                "success": True,
                "sql": (
                    "SELECT department_name, COUNT(story_id) FROM story "
                    "WHERE department_name = '研发二部' GROUP BY department_name"
                ),
            },
        ]
    ).decode()

    result = parse_query_generation(raw, llm_service, max_batch_size=3)

    assert result.success is True


def test_complementary_plans_receive_titles_for_their_own_projection() -> None:
    llm_service = service()
    llm_service.chat_question.intent_context = {
        "decisions": [
            {
                "key": "grain.department",
                "kind": "grain",
                "label": "部门",
                "locked": True,
                "bindings": [
                    {
                        "identifier": "department_name",
                        "role": "group",
                        "aggregation": "none",
                    }
                ],
            },
            {
                "key": "metric.task_count",
                "kind": "metric",
                "label": "Task数",
                "locked": True,
                "bindings": [
                    {
                        "identifier": "task_id",
                        "role": "measure",
                        "aggregation": "count",
                    }
                ],
            },
            {
                "key": "metric.story_count",
                "kind": "metric",
                "label": "Story数",
                "locked": True,
                "bindings": [
                    {
                        "identifier": "story_id",
                        "role": "measure",
                        "aggregation": "count",
                    }
                ],
            },
        ]
    }
    raw = orjson.dumps(
        [
            {
                "success": True,
                "sql": (
                    "SELECT department_name, COUNT(task_id) AS task_count "
                    "FROM task GROUP BY department_name"
                ),
            },
            {
                "success": True,
                "sql": (
                    "SELECT department_name, COUNT(story_id) AS story_count "
                    "FROM story GROUP BY department_name"
                ),
            },
        ]
    ).decode()

    result = parse_query_generation(raw, llm_service, max_batch_size=3)

    assert [plan["presentation_title"] for plan in result.plans] == [
        "按部门统计Task数（1）",
        "按部门统计Story数（2）",
    ]


def test_json_extraction_ignores_brackets_inside_sql_strings() -> None:
    raw = '模型说明：{"success":true,"sql":"SELECT \'{not_a_json_boundary}\' AS value"}'

    extracted = extract_nested_json(raw)

    assert extracted is not None
    assert orjson.loads(extracted)["success"] is True


def _prompt_question() -> SimpleNamespace:
    return SimpleNamespace(
        lang="简体中文",
        engine="MySQL",
        db_schema="# Table: asset",
        question="已确认查询口径：保持企业-核企组合",
        generation_question="汇总今年企业累计签收额和融资额",
        rule="",
        error_msg="",
        regenerate_record_id=None,
        plan_context="<plan-context>\n- 使用 transfer_amt\n</plan-context>",
    )


def test_sql_generation_uses_original_question_and_separate_plan_context() -> None:
    prompt = SqlProtocol("mysql").build_user_prompt(
        _prompt_question(),
        current_time="2026-07-29",
        change_title=False,
    )

    assert "汇总今年企业累计签收额和融资额" in prompt
    assert "已确认查询口径：保持企业-核企组合" not in prompt
    assert prompt.count("<plan-context>") == 1


def test_rest_generation_uses_same_question_projection_and_plan_context() -> None:
    prompt = RestProtocol("api").build_user_prompt(
        _prompt_question(),
        current_time="2026-07-29",
        change_title=False,
    )

    assert "汇总今年企业累计签收额和融资额" in prompt
    assert "已确认查询口径：保持企业-核企组合" not in prompt
    assert prompt.count("<plan-context>") == 1
