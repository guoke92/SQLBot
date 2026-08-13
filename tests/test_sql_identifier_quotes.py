from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from types import SimpleNamespace

from apps.protocol.sql.protocol import (  # noqa: E402
    SqlProtocol,
    rewrite_identifier_quotes,
)


def test_postgres_quotes_become_mysql_backticks() -> None:
    sql = 'SELECT "company_name" FROM "dw_mid_crm_wec_xun_core_fin_list"'
    rewritten = rewrite_identifier_quotes(
        sql, dialect="mysql", quote_prefix="`"
    )
    assert "`company_name`" in rewritten
    assert '"company_name"' not in rewritten


def test_already_backticked_sql_is_stable() -> None:
    sql = "SELECT `company_name` FROM `dw_mid_crm_wec_xun_core_fin_list`"
    rewritten = rewrite_identifier_quotes(
        sql, dialect="mysql", quote_prefix="`"
    )
    assert "`company_name`" in rewritten


def test_postgres_target_keeps_double_quotes() -> None:
    sql = 'SELECT "company_name" FROM "customer"'
    rewritten = rewrite_identifier_quotes(
        sql, dialect="postgres", quote_prefix='"'
    )
    assert "company_name" in rewritten


def test_prompt_bundle_uses_protocol_type_for_quote_rules() -> None:
    question = SimpleNamespace(
        lang="简体中文",
        sqlbot_name="SQLBot",
        engine="StarRocks 3.x",
        db_schema="schema",
        sample_data="",
        terminologies="",
        data_training="",
        custom_prompt="",
    )
    starrocks = SqlProtocol("starrocks").build_prompt_bundle(question)
    postgres = SqlProtocol("pg").build_prompt_bundle(question)
    assert "外层加反引号（`）" in starrocks.rules
    assert "外层加双引号（\"）" not in starrocks.rules
    assert "外层加双引号（\"）" in postgres.rules
