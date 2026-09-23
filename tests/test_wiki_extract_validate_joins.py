"""Unit tests for live EQUI_JOIN validation helpers (no DB required)."""

from __future__ import annotations

from tools.wiki_extract.validate_joins import (
    EndpointStats,
    JoinProbe,
    _decide_verdict,
    load_wiki_relations,
)


def _probe(
    *,
    join_hits: int,
    left_in: int,
    right_in: int,
    left_nn: int,
    right_nn: int,
    left_d: int,
    right_d: int,
) -> JoinProbe:
    p = JoinProbe(left="a.x", right="b.y")
    p.join_hits = join_hits
    p.left_in_right = left_in
    p.left_not_in_right = max(left_nn - left_in, 0)
    p.right_in_left = right_in
    p.right_not_in_left = max(right_nn - right_in, 0)
    p.left_in_right_ratio = round(left_in / left_nn, 4) if left_nn else 0.0
    p.right_in_left_ratio = round(right_in / right_nn, 4) if right_nn else 0.0
    p.left_stats = EndpointStats(
        table="a",
        column="x",
        non_null=left_nn,
        distinct_non_null=left_d,
    )
    p.right_stats = EndpointStats(
        table="b",
        column="y",
        non_null=right_nn,
        distinct_non_null=right_d,
    )
    return p


def test_decide_fk_like() -> None:
    verdict, _ = _decide_verdict(
        _probe(
            join_hits=100,
            left_in=80,
            right_in=10,
            left_nn=100,
            right_nn=10,
            left_d=80,
            right_d=10,
        )
    )
    assert verdict == "fk_like"


def test_decide_impossible_empty_join() -> None:
    verdict, _ = _decide_verdict(
        _probe(
            join_hits=0,
            left_in=0,
            right_in=0,
            left_nn=100,
            right_nn=50,
            left_d=40,
            right_d=20,
        )
    )
    assert verdict == "impossible"


def test_decide_false_friend_uuid_vs_code() -> None:
    verdict, _ = _decide_verdict(
        _probe(
            join_hits=3,
            left_in=3,
            right_in=3,
            left_nn=5000,
            right_nn=800,
            left_d=5000,
            right_d=800,
        )
    )
    assert verdict == "false_friend"


def test_decide_shared_domain() -> None:
    verdict, _ = _decide_verdict(
        _probe(
            join_hits=600,
            left_in=400,
            right_in=150,
            left_nn=800,
            right_nn=200,
            left_d=800,
            right_d=200,
        )
    )
    assert verdict == "shared_domain"


def test_load_wiki_relations_dedup(tmp_path) -> None:
    tables = tmp_path / "tables"
    tables.mkdir()
    fence = "\n".join(
        [
            "```ground:relation",
            "left: cust_a.x",
            "right: cust_b.y",
            "type: EQUI_JOIN",
            "trust: high",
            "authenticity: authentic",
            "```",
            "",
        ]
    )
    (tables / "cust_a.md").write_text("# a\n\n" + fence, encoding="utf-8")
    (tables / "cust_b.md").write_text("# b\n\n" + fence, encoding="utf-8")
    edges = load_wiki_relations(tmp_path)
    assert len(edges) == 1
    assert edges[0]["left"] == "cust_a.x"
    assert edges[0]["right"] == "cust_b.y"
    assert edges[0]["host"] == "cust_a"
