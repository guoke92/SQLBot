from apps.chat.plan_facts import extract_sql_plan_facts
from apps.chat.query_risk import QueryRiskInput, classify_query_risk


def test_simple_single_metric_query_is_low_risk() -> None:
    facts = extract_sql_plan_facts("SELECT SUM(amount) total FROM orders")
    result = classify_query_risk(QueryRiskInput(facts=(facts,)))
    assert result.level == "low"


def test_two_plain_aggregates_are_not_mislabeled_as_derived_metric() -> None:
    facts = extract_sql_plan_facts(
        "SELECT supplier, SUM(signed_amount), SUM(financed_amount) "
        "FROM finance GROUP BY supplier"
    )
    result = classify_query_risk(QueryRiskInput(facts=(facts,)))
    codes = {item.code for item in result.reasons}
    assert "MULTIPLE_METRICS" in codes
    assert "DERIVED_METRIC" not in codes


def test_distinct_preaggregation_is_not_derived_metric() -> None:
    facts = extract_sql_plan_facts(
        """SELECT company_name, SUM(amt) total FROM (
               SELECT DISTINCT asset_no, company_name, amt FROM finance
           ) staged GROUP BY company_name"""
    )
    result = classify_query_risk(QueryRiskInput(facts=(facts,)))
    codes = {item.code for item in result.reasons}
    assert facts.distinct_count >= 1
    assert "DERIVED_METRIC" not in codes


def test_case_aggregation_is_still_derived_metric() -> None:
    facts = extract_sql_plan_facts(
        "SELECT SUM(CASE WHEN status='paid' THEN amt ELSE 0 END) total FROM finance"
    )
    result = classify_query_risk(QueryRiskInput(facts=(facts,)))
    assert "DERIVED_METRIC" in {item.code for item in result.reasons}


def test_or_spliced_time_filters_are_high_risk() -> None:
    facts = extract_sql_plan_facts(
        """SELECT supplier, SUM(amount) FROM finance
           WHERE sign_date >= '2026-01-01' OR apply_date >= '2026-01-01'
           GROUP BY supplier"""
    )
    result = classify_query_risk(
        QueryRiskInput(
            facts=(facts,),
            schema_text="sign_date timestamp, apply_date timestamp, amount decimal",
        )
    )
    assert result.level == "high"
    assert "MULTIPLE_TIME_BASIS" in {item.code for item in result.reasons}


def test_separate_metric_dates_are_not_mixed_time_basis() -> None:
    facts = extract_sql_plan_facts(
        """WITH sign AS (
               SELECT company_name, SUM(amt) total FROM asset
               WHERE confirm_date >= '2026-01-01' GROUP BY company_name
           ), fin AS (
               SELECT company_name, SUM(amt) total FROM finance
               WHERE apply_date >= '2026-01-01' GROUP BY company_name
           )
           SELECT s.company_name, s.total, f.total
           FROM sign s LEFT JOIN fin f ON s.company_name = f.company_name"""
    )
    result = classify_query_risk(
        QueryRiskInput(
            facts=(facts,),
            schema_text="confirm_date varchar, apply_date varchar",
            certified_relation_count=0,
        )
    )
    codes = {item.code for item in result.reasons}
    assert "MULTIPLE_TIME_BASIS" not in codes
    assert "UNTRUSTED_RELATION" not in codes


def test_untrusted_join_is_high_risk() -> None:
    facts = extract_sql_plan_facts(
        "SELECT a.id, b.name FROM account a JOIN customer b ON a.customer_id=b.id"
    )
    result = classify_query_risk(
        QueryRiskInput(facts=(facts,), certified_relation_count=0)
    )
    assert result.level == "high"
    assert "UNTRUSTED_RELATION" in {item.code for item in result.reasons}


def test_actual_ambiguous_entity_shape_is_high_risk() -> None:
    facts = extract_sql_plan_facts("SELECT COUNT(*) FROM task")
    result = classify_query_risk(
        QueryRiskInput(
            facts=(facts,),
            entity_bindings={
                "ambiguous": {
                    "研发二部": {
                        "options": [
                            {"canonical": "研发二部"},
                            {"canonical": "三中心研发二部"},
                        ]
                    }
                }
            },
        )
    )
    assert result.level == "high"
    assert "AMBIGUOUS_ENTITY" in {item.code for item in result.reasons}


def test_explicit_time_range_not_proven_is_high_risk() -> None:
    facts = extract_sql_plan_facts("SELECT SUM(amount) FROM finance")
    result = classify_query_risk(
        QueryRiskInput(
            facts=(facts,),
            temporal_evidence={
                "start": "2026-01-01",
                "end_exclusive": "2027-01-01",
            },
        )
    )
    assert result.level == "high"
    assert "EXPLICIT_TIME_NOT_PROVEN" in {item.code for item in result.reasons}


def test_risk_classification_is_deterministic() -> None:
    facts = extract_sql_plan_facts(
        "SELECT region, COUNT(*) FROM customer GROUP BY region"
    )
    value = QueryRiskInput(facts=(facts,), evidence_kinds=("user_question",))
    assert classify_query_risk(value) == classify_query_risk(value)
