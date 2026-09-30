"""SQL feature corpus: extract joins/formulas and ingest by source."""

from __future__ import annotations

import pytest

from tools.wiki_extract.sql_corpus import (
    SqlFeatureCorpus,
    SqlRecord,
    SqlSource,
    extract_sql_features,
    proposed_edges,
)


def _record(record_id: str, sql: str, source: str = SqlSource.INIT_EXISTING.value) -> SqlRecord:
    return SqlRecord(record_id=record_id, source=source, sql=sql)


def test_equality_join_resolves_aliases() -> None:
    features = extract_sql_features(
        _record(
            "q1",
            """
            SELECT T2.Zip
            FROM frpm AS T1
            INNER JOIN schools AS T2 ON T1.CDSCode = T2.CDSCode
            WHERE T1.County = 'Fresno'
            """,
        )
    )
    assert features.parse_error == ""
    pairs = {(item.left, item.right) for item in features.equality_joins}
    assert ("frpm.CDSCode", "schools.CDSCode") in pairs
    assert features.transform_joins == []
    assert features.named_formulas == []


def test_multi_column_on_clause_groups_predicates() -> None:
    features = extract_sql_features(
        _record(
            "q2",
            """
            SELECT results.raceid
            FROM results
            JOIN pitstops
              ON results.raceid = pitstops.raceid
             AND results.driverid = pitstops.driverid
            """,
        )
    )
    assert len(features.equality_joins) == 2
    assert len(features.join_groups) == 1
    group = features.join_groups[0]
    assert group.tables == ("pitstops", "results")
    assert len(group.predicates) == 2


def test_transform_join_and_named_formula() -> None:
    features = extract_sql_features(
        _record(
            "q3",
            """
            SELECT SUBSTR(bond.bond_id, 1, 7) AS atom_id1
            FROM bond
            JOIN connected
              ON CONCAT(bond.molecule_id, '_1') = connected.atom_id
             AND bond.bond_id = connected.bond_id
            """,
        )
    )
    assert len(features.transform_joins) == 1
    transform = features.transform_joins[0]
    assert "bond.molecule_id" in transform.fields
    assert "connected.atom_id" in transform.fields
    assert any(item.alias == "atom_id1" and item.nested is False for item in features.named_formulas)
    assert any(item.left.endswith("bond_id") and item.right.endswith("bond_id") for item in features.equality_joins)


def test_subquery_output_resolves_to_base_table() -> None:
    features = extract_sql_features(
        _record(
            "q4",
            """
            SELECT A.uop_cd,
                   A.trans_amt + P.total_planned AS current_spend_and_planned
            FROM accounting_table AS A,
                 (SELECT source_code, SUM(planned_amt) AS total_planned
                  FROM planning_table
                  WHERE country_code = 'USA'
                  GROUP BY source_code) AS P
            WHERE A.uop_cd = P.source_code
            """,
        )
    )
    pairs = {(item.left, item.right) for item in features.equality_joins}
    assert ("accounting_table.uop_cd", "planning_table.source_code") in pairs
    formulas = {item.alias: item for item in features.named_formulas}
    assert "current_spend_and_planned" in formulas
    assert "accounting_table.trans_amt" in formulas["current_spend_and_planned"].fields
    assert "planning_table.planned_amt" in formulas["current_spend_and_planned"].fields
    assert formulas["total_planned"].nested is True


def test_self_join_kept_same_alias_filter_dropped() -> None:
    features = extract_sql_features(
        _record(
            "q5",
            """
            SELECT a.code
            FROM tenant_project_approval AS a
            JOIN tenant_project_approval AS b
              ON a.code = b.ref_tenant_project_approval_tenant_project_approval
            WHERE a.code = a.name
            """,
        )
    )
    assert len(features.equality_joins) == 1
    join = features.equality_joins[0]
    assert join.left.startswith("tenant_project_approval.")
    assert join.right.startswith("tenant_project_approval.")


def test_parse_error_is_recorded() -> None:
    features = extract_sql_features(_record("bad", "SELECT FROM"))
    assert features.parse_error
    assert features.equality_joins == []


def test_replace_then_upsert_then_remove() -> None:
    corpus = SqlFeatureCorpus()
    init_a = _record(
        "a",
        "SELECT 1 FROM tenant_project AS t JOIN cust_project_rel AS c ON t.id = c.project_id",
    )
    init_b = _record(
        "b",
        "SELECT 1 FROM platform_product AS p JOIN tenant_product AS tp ON p.product_code = tp.platform_product_code",
    )
    first = corpus.replace_source(SqlSource.INIT_EXISTING.value, [init_a, init_b])
    assert first.added == 2
    assert corpus.aggregated()["by_source"]["init_existing"] == 2

    again = corpus.replace_source(SqlSource.INIT_EXISTING.value, [init_a])
    assert again.removed == 1
    assert again.updated == 1
    assert corpus.aggregated()["by_source"]["init_existing"] == 1

    accepted = SqlRecord(
        record_id="run-9",
        source=SqlSource.USER_ACCEPTED.value,
        sql="SELECT 1 FROM tenant_project AS t JOIN project_file_info AS f ON t.id = f.project_id",
        question="项目运营文件",
    )
    manual = SqlRecord(
        record_id="ex-1",
        source=SqlSource.MANUAL_EXAMPLE.value,
        sql="SELECT 1 FROM tenant_project AS t JOIN cust_project_rel AS c ON t.id = c.project_id",
    )
    delta = corpus.upsert([accepted, manual])
    assert delta.added == 2
    aggregated = corpus.aggregated()
    project_edges = [
        row
        for row in aggregated["equality_joins"]
        if {row["left"].split(".", 1)[0], row["right"].split(".", 1)[0]}
        == {"cust_project_rel", "tenant_project"}
    ]
    assert project_edges[0]["support"] == 2
    sources = {item["source"] for item in project_edges[0]["records"]}
    assert sources == {SqlSource.INIT_EXISTING.value, SqlSource.MANUAL_EXAMPLE.value}

    corpus.remove(SqlSource.USER_ACCEPTED.value, ["run-9"])
    assert corpus.aggregated()["by_source"]["user_accepted"] == 0


def test_unknown_source_rejected() -> None:
    corpus = SqlFeatureCorpus()
    with pytest.raises(ValueError, match="unknown sql source"):
        corpus.upsert([SqlRecord(record_id="x", source="ad_hoc", sql="SELECT 1")])


def test_save_load_roundtrip(tmp_path) -> None:
    corpus = SqlFeatureCorpus()
    corpus.upsert(
        [
            _record(
                "a",
                "SELECT t.id FROM tenant_project AS t JOIN ca_fee_order AS o ON t.id = o.project_id",
                source=SqlSource.MANUAL_EXAMPLE.value,
            )
        ]
    )
    path = tmp_path / "corpus.yaml"
    corpus.save(path)
    loaded = SqlFeatureCorpus.load(path)
    assert loaded.aggregated()["equality_joins"][0]["support"] == 1
    assert loaded.aggregated()["by_source"]["manual_example"] == 1


def test_proposed_edges_stay_proposed() -> None:
    corpus = SqlFeatureCorpus()
    corpus.upsert(
        [
            _record(
                "q",
                """
                SELECT CONCAT(a.molecule_id, '_1') AS atom_id1
                FROM bond AS a
                JOIN atom AS b
                  ON a.molecule_id = b.molecule_id AND a.atom_id = b.atom_id
                WHERE CONCAT(a.molecule_id, '_1') = b.atom_id
                """,
            )
        ]
    )
    edges = proposed_edges(corpus.aggregated())
    kinds = {row["type"] for row in edges}
    assert "EQUI_JOIN" in kinds
    assert "MULTI_COLUMN_JOIN" in kinds
    assert "TRANSFORM_JOIN" in kinds
    assert "NAMED_FORMULA" in kinds
    assert {row["trust"] for row in edges} == {"proposed"}
    assert {row["source"] for row in edges} == {"sql_corpus"}
