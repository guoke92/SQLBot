"""Contract-derived result presentation tests."""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.chat.presentation import build_result_presentation, chart_columns
from apps.chat.query_contract import compile_query_contract
from apps.protocol.sql.identifier_validation import analyze_sql_contract_structure


def test_result_presentation_uses_contract_projection_before_schema_comments() -> None:
    contract = compile_query_contract(
        [
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
                "key": "metric.sign_amount",
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
            {
                "key": "metric.fin_amount",
                "kind": "metric",
                "label": "累计融资额",
                "locked": True,
                "bindings": [
                    {
                        "identifier": "fin_apply_amt",
                        "role": "measure",
                        "aggregation": "sum",
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
        ]
    )

    presentation = build_result_presentation(
        ["company_name", "cum_sign_amt", "cum_fin_amt", "supplier_level"],
        title="按企业主体统计累计签收额、累计融资额",
        contract=contract,
        projection_requirements={
            "company_name": ["grain.enterprise"],
            "cum_sign_amt": ["metric.sign_amount"],
            "cum_fin_amt": ["metric.fin_amount"],
            "supplier_level": ["dimension.supplier_level"],
        },
        schema_text="""# Table: asset
(company_name:varchar, 原始供应商),
(orig_asset_amt:decimal(38, 2), 原始资产金额),
(fin_apply_amt:decimal, 融资申请金额),
(apply_level:int, 资产层级)
""",
    )

    assert presentation == {
        "title": "按企业主体统计累计签收额、累计融资额",
        "columns": [
            {
                "field": "company_name",
                "label": "企业主体",
                "display": "企业主体(company_name)",
            },
            {
                "field": "cum_sign_amt",
                "label": "累计签收额",
                "display": "累计签收额(cum_sign_amt)",
            },
            {
                "field": "cum_fin_amt",
                "label": "累计融资额",
                "display": "累计融资额(cum_fin_amt)",
            },
            {
                "field": "supplier_level",
                "label": "供应商层级",
                "display": "供应商层级(supplier_level)",
            },
        ],
    }
    assert chart_columns(presentation) == [
        {"name": "企业主体(company_name)", "value": "company_name"},
        {"name": "累计签收额(cum_sign_amt)", "value": "cum_sign_amt"},
        {"name": "累计融资额(cum_fin_amt)", "value": "cum_fin_amt"},
        {"name": "供应商层级(supplier_level)", "value": "supplier_level"},
    ]


def test_ambiguous_alias_keeps_physical_name() -> None:
    contract = compile_query_contract(
        [
            {
                "key": "metric.first_amount",
                "kind": "metric",
                "label": "第一金额",
                "locked": True,
                "bindings": [
                    {"identifier": "a_amount", "role": "measure", "aggregation": "sum"}
                ],
            },
            {
                "key": "metric.second_amount",
                "kind": "metric",
                "label": "第二金额",
                "locked": True,
                "bindings": [
                    {"identifier": "b_amount", "role": "measure", "aggregation": "sum"}
                ],
            },
        ]
    )

    presentation = build_result_presentation(
        ["total_amt"],
        contract=contract,
        projection_requirements={
            "total_amt": ["metric.first_amount", "metric.second_amount"]
        },
    )

    assert presentation["columns"] == [
        {"field": "total_amt", "label": "", "display": "total_amt"}
    ]


def test_duplicate_schema_field_names_do_not_guess_a_label() -> None:
    presentation = build_result_presentation(
        ["name"],
        schema_text="""# Table: user
(name:varchar, 用户名称)
# Table: project
(name:varchar, 项目名称)
""",
    )

    assert presentation["columns"] == [
        {"field": "name", "label": "", "display": "name"}
    ]


def test_projection_lineage_maps_cte_aliases_to_contract_requirements() -> None:
    contract = compile_query_contract(
        [
            {
                "key": "grain.company",
                "kind": "grain",
                "label": "企业",
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
                "key": "metric.amount",
                "kind": "metric",
                "label": "累计金额",
                "locked": True,
                "bindings": [
                    {
                        "identifier": "orig_amount",
                        "role": "measure",
                        "aggregation": "sum",
                    }
                ],
            },
        ]
    )

    validation = analyze_sql_contract_structure(
        [
            (
                "WITH totals AS (SELECT company_name, SUM(orig_amount) AS total_amt "
                "FROM asset GROUP BY company_name) "
                "SELECT company_name, total_amt FROM totals"
            )
        ],
        contract,
        dialect="mysql",
    )
    projections = validation.per_plan_projections[0]

    assert validation.error is None
    assert {item.output_name: item.requirement_keys for item in projections} == {
        "company_name": ("grain.company",),
        "total_amt": ("metric.amount",),
    }
