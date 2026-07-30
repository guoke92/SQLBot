from __future__ import annotations

import sys
from pathlib import Path

from sqlalchemy import String

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.chat.binding_resolver import (  # noqa: E402
    binding_resource_names,
    resolve_entity_bindings,
    retain_binding_resources,
)
from apps.datasource.models.datasource import CoreField, CoreTable  # noqa: E402
from apps.dictionary.catalog import is_string_field_type  # noqa: E402
from apps.dictionary.matching import (  # noqa: E402
    best_matching_span,
    normalize_dictionary_value,
)
from apps.dictionary.models import (  # noqa: E402
    DictionaryFieldConfig,
    DictionaryValue,
)
from apps.knowledge.dictionary_recall import recall_dictionary  # noqa: E402
from apps.knowledge.models import FieldTarget, KnowledgeMatch  # noqa: E402
from apps.knowledge.scope import scope_knowledge_matches  # noqa: E402


class _Field:
    def __init__(self, name: str, field_type: str, comment: str = "") -> None:
        self.field_name = name
        self.field_type = field_type
        self.field_comment = comment
        self.custom_comment = comment


def _field(name: str, field_type: str, comment: str = "") -> _Field:
    return _Field(name, field_type, comment)


def test_dictionary_eligibility_is_based_on_physical_type() -> None:
    assert is_string_field_type(_field("department_name", "varchar(128)").field_type)
    assert is_string_field_type(_field("opaque_text", "text").field_type)
    assert not is_string_field_type(_field("department_id", "bigint").field_type)


def test_dictionary_status_uses_portable_string_storage() -> None:
    status_column = DictionaryFieldConfig.__table__.c.status
    assert isinstance(status_column.type, String)


def test_value_normalization_is_stable() -> None:
    assert normalize_dictionary_value("  ＡIO  平台 ") == "aio 平台"


def test_best_matching_span_is_language_neutral() -> None:
    assert best_matching_span("请统计研发二部的任务", "战客研发二部") == "研发二部"
    assert best_matching_span("show alpha-team workload", "alpha-team") == "alpha-team"


def test_binding_carries_physical_target_and_forces_schema_resource() -> None:
    match = KnowledgeMatch(
        source="dictionary",
        usages=["entity_binding"],
        query="研发二部",
        canonical="战客研发二部",
        alternatives=["三中心研发二部"],
        match_type="suffix",
        score=0.9,
        targets=[
            FieldTarget(
                ds_id=1,
                table_id=2,
                table_name="d_organization",
                field_id=3,
                field_name="organization_name",
            )
        ],
    )
    bindings = resolve_entity_bindings([match])
    assert bindings["resolved"]["研发二部"]["canonical"] == "战客研发二部"
    assert (
        bindings["resolved"]["研发二部"]["targets"][0]["field_name"]
        == "organization_name"
    )
    assert binding_resource_names(bindings) == ["d_organization"]
    assert retain_binding_resources(bindings, [])["resolved"] == {}


def test_ambiguous_binding_candidates_force_all_candidate_resources() -> None:
    bindings = {
        "resolved": {},
        "ambiguous": {
            "研发二部": {
                "options": [
                    {
                        "canonical": "研发二部",
                        "targets": [
                            {
                                "table_name": "d_user",
                                "field_name": "organization_name",
                            }
                        ],
                    },
                    {
                        "canonical": "研发二部项目组",
                        "targets": [
                            {
                                "table_name": "d_project",
                                "field_name": "organization_name",
                            }
                        ],
                    },
                ]
            }
        },
    }

    assert binding_resource_names(bindings) == ["d_user", "d_project"]


def test_dictionary_match_is_removed_outside_permission_scope() -> None:
    target = FieldTarget(
        ds_id=1,
        table_id=2,
        table_name="d_department",
        field_id=3,
        field_name="department_name",
    )
    dictionary = KnowledgeMatch(
        source="dictionary",
        usages=["entity_binding"],
        query="研发部",
        canonical="平台研发部",
        match_type="suffix",
        score=0.9,
        targets=[target],
    )
    terminology = KnowledgeMatch(
        source="terminology",
        usages=["prompt"],
        query="研发部",
        canonical="研发部门",
        match_type="semantic",
        score=0.7,
    )
    assert scope_knowledge_matches(
        [dictionary, terminology],
        allowed_targets=set(),
    ) == [terminology]
    assert (
        scope_knowledge_matches(
            [dictionary],
            allowed_targets={(2, 3)},
            row_restricted_tables={"d_department"},
        )
        == []
    )


def test_ambiguous_dictionary_match_is_not_forced_to_eq() -> None:
    target = FieldTarget(
        ds_id=1,
        table_id=2,
        table_name="department",
        field_id=3,
        field_name="name",
    )
    matches = [
        KnowledgeMatch(
            source="dictionary",
            usages=["entity_binding"],
            query="研发部",
            canonical=name,
            match_type="suffix",
            score=0.9,
            targets=[target],
        )
        for name in ("平台研发部", "产品研发部")
    ]
    bindings = resolve_entity_bindings(matches)
    assert "研发部" not in bindings["resolved"]
    assert bindings["ambiguous"]["研发部"]["match"] == "candidate"


def test_dictionary_recall_preserves_competing_values_for_ambiguity() -> None:
    config = DictionaryFieldConfig(
        id=1,
        oid=1,
        ds_id=1,
        table_id=2,
        field_id=3,
        enabled=True,
        max_values=500,
        schema_fingerprint="fingerprint",
        status="READY",
        published_generation=1,
        revision=1,
        value_count=2,
        create_time=None,
        update_time=None,
    )
    table = CoreTable(id=2, ds_id=1, table_name="department")
    field = CoreField(
        id=3,
        ds_id=1,
        table_id=2,
        field_name="name",
        field_type="varchar(128)",
    )
    rows = [
        (
            DictionaryValue(
                id=index,
                config_id=1,
                value=value,
                normalized_value=value,
                generation=1,
                create_time=None,
            ),
            config,
            table,
            field,
            0.9,
        )
        for index, value in enumerate(("平台研发部", "产品研发部"), start=1)
    ]

    class _Result:
        def all(self):
            return rows

    class _Session:
        def exec(self, _statement):
            return _Result()

    matches = recall_dictionary(
        _Session(),  # type: ignore[arg-type]
        question="研发部",
        oid=1,
        ds_id=1,
    )
    bindings = resolve_entity_bindings(matches)

    assert {match.canonical for match in matches} == {"平台研发部", "产品研发部"}
    assert "研发部" not in bindings["resolved"]
    assert bindings["ambiguous"]["研发部"]["match"] == "candidate"
