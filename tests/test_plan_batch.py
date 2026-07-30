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
    assert "计划 2" in (result.error_message or "")


def test_validated_physical_resources_replace_model_claim() -> None:
    raw = orjson.dumps(
        {"success": True, "sql": "SELECT 1", "tables": ["claimed"]}
    ).decode()
    result = parse_query_generation(raw, service(), max_batch_size=3)

    assert result.success is True
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
                "required_identifiers": ["company_name", "core_company_id"],
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
                "required_identifiers": ["department_name"],
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
                "required_identifiers": ["amount"],
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
    assert "competing plans" in (result.error_message or "")


def test_batch_allows_complementary_plans_with_shared_scope() -> None:
    llm_service = service()
    llm_service.chat_question.intent_context = {
        "decisions": [
            {
                "key": "scope.department",
                "kind": "scope",
                "label": "部门范围",
                "locked": True,
                "required_identifiers": ["department_name"],
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
