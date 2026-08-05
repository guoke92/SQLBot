from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.chat.presentation import build_result_presentation  # noqa: E402
from apps.chat.query_contract import (  # noqa: E402
    FieldRef,
    GroupRequirement,
    OutputRequirement,
    QueryContract,
)
from apps.protocol.sql.identifier_validation import (  # noqa: E402
    analyze_sql_contract_structure,
)


def _contract() -> QueryContract:
    return QueryContract(
        requirements=[
            GroupRequirement(
                slot_id="company",
                label="企业名称",
                field=FieldRef(resource="asset", field="company_name"),
            ),
            GroupRequirement(
                slot_id="level",
                label="资产层级",
                field=FieldRef(resource="asset", field="apply_level"),
            ),
            OutputRequirement(
                slot_id="amount",
                label="累计签收额",
                field=FieldRef(resource="asset", field="sign_amt"),
                operation="sum",
            ),
        ]
    )


def test_business_label_and_physical_field_are_both_presented() -> None:
    presentation = build_result_presentation(
        ["company_name", "apply_level", "sign_amt"],
        contract=_contract(),
    )
    assert [item["display"] for item in presentation["columns"]] == [
        "企业名称(company_name)",
        "资产层级(apply_level)",
        "累计签收额(sign_amt)",
    ]


def test_projection_lineage_maps_sql_alias_to_the_contract_label() -> None:
    contract = _contract()
    validation = analyze_sql_contract_structure(
        [
            "SELECT company_name AS company, apply_level, SUM(sign_amt) AS total "
            "FROM asset GROUP BY company_name, apply_level"
        ],
        contract,
        dialect="mysql",
    )
    assert validation.status == "verified"
    lineage = {
        projection.output_name: projection.requirement_keys
        for projection in validation.per_plan_projections[0]
    }
    presentation = build_result_presentation(
        ["company", "apply_level", "total"],
        contract=contract,
        projection_requirements=lineage,
    )
    assert [item["display"] for item in presentation["columns"]] == [
        "企业名称(company)",
        "资产层级(apply_level)",
        "累计签收额(total)",
    ]


def test_schema_comment_is_only_an_unambiguous_fallback() -> None:
    schema = """
    CREATE TABLE asset (
      (status: varchar, 资产状态),
      (code: varchar, 编码)
    )
    """
    presentation = build_result_presentation(["status", "unknown"], schema_text=schema)
    assert presentation["columns"][0]["display"] == "资产状态(status)"
    assert presentation["columns"][1]["display"] == "unknown"
