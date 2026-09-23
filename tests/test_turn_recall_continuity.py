"""Multi-turn knowledge continuity: RecallRequest pins, snapshot rehydration,
caliber binding survival, and kernel budget behaviour around pinned tables."""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.chat.caliber_surface import (  # noqa: E402
    ingest_confirmed_calibers,
    project_confirmed_calibers,
    render_caliber_lines,
)
from apps.chat.memory_slots import (  # noqa: E402
    MemorySlots,
    hydrate_memory_slots_from_referenced_turns,
)
from apps.chat.steps.recall_request import (  # noqa: E402
    RecallRequest,
    build_recall_request,
    sql_references,
)
from apps.knowledge.recall_kernel.tables import (  # noqa: E402
    PINNED_EVIDENCE,
    resolve_wiki_tables,
    trim_schema_chars,
)
from apps.knowledge.recall_kernel.types import (  # noqa: E402
    RecallBudget,
    TableCandidate,
)

_CORPUS = _ROOT / "docs" / "wiki" / "v3"


# ── RecallRequest ───────────────────────────────────────────────────────────


def test_sql_references_resolves_aliases_and_skips_star() -> None:
    tables, columns = sql_references(
        "SELECT c.cust_name, p.user_type, count(*) FROM cust_company_info c "
        "JOIN cust_person_info p ON p.ref_cust_company_info = c.code "
        "WHERE c.enable = 'Y' GROUP BY c.cust_name, p.user_type LIMIT 100",
        dialect="mysql",
    )
    assert tables == ["cust_company_info", "cust_person_info"]
    assert columns["cust_company_info"] == {"cust_name", "code", "enable"}
    assert columns["cust_person_info"] == {"user_type", "ref_cust_company_info"}


def test_sql_references_degrades_on_garbage() -> None:
    assert sql_references("not sql at all ((") == ([], {})
    assert sql_references("") == ([], {})


def test_build_recall_request_single_turn_is_plain() -> None:
    req = build_recall_request("查询企业清单")
    assert req == RecallRequest.simple("查询企业清单")
    assert not req.is_continuation
    assert RecallRequest.coerce("x").query == "x"
    assert RecallRequest.coerce(req) is req


def test_build_recall_request_continuation_pins_baseline_and_prior_pages() -> None:
    req = build_recall_request(
        "加上城市维度",
        baseline_sql="SELECT cust_name FROM cust_company_info WHERE enable='Y'",
        prior_questions=["查询启用的企业", "只看金融机构"],
        prior_page_keys=["dicts/user_type", "calibers/valid"],
        prior_tables=["cust_company_info", "cust_person_info"],
        dialect="mysql",
    )
    assert req.is_continuation
    assert req.question == "加上城市维度"
    assert req.query == "查询启用的企业\n只看金融机构\n加上城市维度"
    assert req.pin_tables == ("cust_company_info", "cust_person_info")
    assert req.pin_pages == ("dicts/user_type", "calibers/valid")
    assert req.required_fields == {"cust_company_info": ("cust_name", "enable")}
    span = req.as_span_fields()
    assert span["pin_tables"] == ["cust_company_info", "cust_person_info"]


def test_recall_request_rehydrate_is_pin_only() -> None:
    req = RecallRequest.rehydrate(
        pin_tables=["cust_company_info"],
        pin_pages=["dicts/identify_style", "tables/cust_company_info"],
        required_fields={"cust_company_info": ("cust_name", "enable")},
        question="加上城市维度",
    )
    assert req.is_continuation
    assert req.query == ""
    assert req.question == "加上城市维度"
    assert req.pin_tables == ("cust_company_info",)
    assert req.pin_pages == ("dicts/identify_style", "tables/cust_company_info")
    assert "加上城市" not in req.query
    assert req.as_span_fields()["retrieval_query"] == ""


# ── kernel: pinned tables ───────────────────────────────────────────────────


def _anchor_store(attribution: dict[str, list[str]]) -> object:
    class _Store:
        pages: dict[str, object] = {}

        def get_page(self, key: str) -> object | None:
            return None

    return _Store()


def test_resolve_wiki_tables_keeps_pinned_first_outside_cap(monkeypatch) -> None:
    from apps.knowledge.recall_kernel import tables as kernel_tables

    monkeypatch.setattr(
        kernel_tables,
        "anchor_table_attribution",
        lambda store, seeds: {
            "t_a": [{"page_key": "p1"}, {"page_key": "p2"}],
            "t_b": [{"page_key": "p1"}],
            "t_c": [{"page_key": "p3"}],
        },
    )
    kept, cut = resolve_wiki_tables(
        _anchor_store({}),
        page_keys=["p1", "p2", "p3"],
        budget=RecallBudget(max_tables=2),
        pinned_tables=["baseline_tbl", "t_c"],
    )
    names = [item.name for item in kept]
    assert names[:2] == ["baseline_tbl", "t_c"]  # pinned first, in pin order
    assert names[2:] == ["t_a", "t_b"]  # cap applies to the rest only
    assert cut == []
    pinned = {item.name: item for item in kept if item.source == "pinned"}
    assert pinned["baseline_tbl"].evidence == (PINNED_EVIDENCE,)
    assert pinned["t_c"].evidence == (PINNED_EVIDENCE, "p3")  # anchor evidence merged


def test_trim_schema_chars_measures_projection_and_never_drops_pinned() -> None:
    tables = [
        TableCandidate(
            name="pinned", evidence=(PINNED_EVIDENCE,), score=0, source="pinned"
        ),
        TableCandidate(name="a", evidence=("p",), score=1, source="anchor"),
        TableCandidate(name="b", evidence=("p",), score=1, source="anchor"),
    ]
    bodies = {"pinned": "x" * 100, "a": "y" * 100, "b": "z" * 100}
    # Projection halves the size → everything fits without dropping tables.
    kept, cut = trim_schema_chars(
        tables, bodies, schema_chars=160, measure=lambda text: len(text) // 2
    )
    assert [t.name for t in kept] == ["pinned", "a", "b"] and cut == []
    # Without projection the tail is dropped, but the pinned table survives.
    kept, cut = trim_schema_chars(tables, bodies, schema_chars=50)
    assert [t.name for t in kept] == ["pinned"] and cut == ["b", "a"]


# ── snapshot persistence + hydration ────────────────────────────────────────


def test_memory_slots_hydrate_knowledge_refs_prior_questions_and_bindings() -> None:
    referenced = [
        {"question": "查询启用的企业", "datasets": []},
        {
            "question": "加上管理员数量",
            "datasets": [
                {
                    "sql": "SELECT 1 FROM cust_company_info",
                    "fields": ["n"],
                    "row_count": 1,
                }
            ],
            "confirmed_calibers": [
                {
                    "question": "「管理员」按哪个口径",
                    "label": "联系人类型为管理员",
                    "meaning": "联系人表的账号类型",
                    "fields": [{"table": "cust_person_info", "field": "user_type"}],
                }
            ],
            "knowledge_refs": {
                "page_keys": ["dicts/user_type", "concepts/admin"],
                "tables": ["cust_company_info", "cust_person_info"],
            },
        },
    ]
    slots = hydrate_memory_slots_from_referenced_turns(MemorySlots(), referenced)
    assert slots.knowledge_refs == {
        "page_keys": ["dicts/user_type", "concepts/admin"],
        "tables": ["cust_company_info", "cust_person_info"],
    }
    assert slots.prior_questions == ["查询启用的企业", "加上管理员数量"]
    assert slots.active_baseline_sql == "SELECT 1 FROM cust_company_info"
    entry = next(iter(slots.confirmed_calibers.values()))
    assert entry["fields"] == [{"table": "cust_person_info", "field": "user_type"}]
    baseline = slots.extract_change_baseline()
    assert baseline["prior_question"] == "加上管理员数量"
    # Round-trip through the answer surface keeps the physical binding.
    surface = project_confirmed_calibers(slots.model_dump())
    assert surface[0]["fields"] == [{"table": "cust_person_info", "field": "user_type"}]
    target: dict[str, object] = {}
    ingest_confirmed_calibers(target, surface)
    assert next(iter(target.values()))["fields"][0]["field"] == "user_type"


def test_render_caliber_lines_is_compact_with_binding() -> None:
    lines = render_caliber_lines(
        {
            "q1": {
                "question": "「管理员」按哪个口径",
                "label": "联系人类型为管理员",
                "meaning": "联系人表的账号类型",
                "fields": [{"table": "cust_person_info", "field": "user_type"}],
            },
            "q2": {"label": "仅启用"},
            "q3": "actual_amount",
        }
    )
    assert lines == [
        "- 「「管理员」按哪个口径」→ 联系人类型为管理员：联系人表的账号类型（cust_person_info.user_type）",
        "- 仅启用",
        "- actual_amount",
    ]


def test_caliber_fields_accept_name_alias_and_preserve_value() -> None:
    from apps.chat.caliber_surface import _caliber_item, ingest_confirmed_calibers

    item = _caliber_item(
        {
            "question": "按哪个维度",
            "label": "按团队",
            "value": "按团队",
            "fields": [{"table": "d_organization", "name": "organization_name"}],
        },
        source="clarification",
    )
    assert item is not None
    assert item["value"] == "按团队"
    assert item["fields"] == [{"table": "d_organization", "field": "organization_name"}]
    target: dict[str, object] = {}
    ingest_confirmed_calibers(target, [item])
    stored = next(iter(target.values()))
    assert stored["value"] == "按团队"
    assert stored["fields"][0]["field"] == "organization_name"


def test_turn_answer_contract_carries_knowledge_refs() -> None:
    from apps.chat.graphs.nodes.nlq.audit import _record_snapshot_values
    from apps.chat.turn_contracts import QueryTurnAnswer
    from apps.conversation.outcome import successful_outcome

    snapshot = _record_snapshot_values(
        [],
        analysis_text="ok",
        finish=True,
        outcome=successful_outcome(),
        execution_mode="agent",
        knowledge_refs={"page_keys": ["dicts/user_type"], "tables": ["t"]},
    )
    answer = QueryTurnAnswer.model_validate(
        {**snapshot["answer"], "answer_revision": 1, "source_run_id": "r1"}
    )
    assert answer.knowledge_refs == {"page_keys": ["dicts/user_type"], "tables": ["t"]}


def test_clarify_resume_message_is_chinese_and_bound(monkeypatch) -> None:
    from contextlib import contextmanager
    from unittest.mock import MagicMock

    from apps.chat.graphs.nodes.agent_clarify import await_agent_clarification_node
    from apps.chat.task.agent_prompt import build_agent_system_prompt
    from apps.conversation.messages import deserialize_messages
    from langchain_core.messages import HumanMessage, SystemMessage

    @contextmanager
    def _scope():
        yield MagicMock()

    pending = SimpleNamespace(interrupt_id="i1", version=1, status="answered")
    dummy_span = MagicMock()
    dummy_span.id = 1
    monkeypatch.setattr("apps.chat.graphs.nodes.agent_clarify.session_scope", _scope)
    monkeypatch.setattr(
        "apps.chat.graphs.nodes.agent_clarify.create_interrupt",
        lambda *_a, **_k: pending,
    )
    monkeypatch.setattr(
        "apps.chat.graphs.nodes.agent_clarify.ensure_clarification_span",
        lambda **_k: dummy_span,
    )
    monkeypatch.setattr(
        "apps.chat.graphs.nodes.agent_clarify.interrupt",
        lambda _public: [{"question_id": "caliber", "option_id": "opt_a"}],
    )
    state = {
        "run_id": "run-clarify",
        "record_id": 9,
        "sink": "json",
        "tool_rounds": 2,
        "knowledge_plane": {},
        "memory_slots": {},
        "messages": [
            SystemMessage(content=build_agent_system_prompt()),
            HumanMessage(content="查一下"),
        ],
        "tool_steps": [
            {
                "ok": True,
                "result": {
                    "data": {
                        "clarification_card": {
                            "questions": [
                                {
                                    "question_id": "caliber",
                                    "question": "「管理员」按哪个口径",
                                    "options": [
                                        {
                                            "option_id": "opt_a",
                                            "label": "联系人类型为管理员",
                                            "description": "联系人表的账号类型",
                                            "fields": [
                                                {
                                                    "table": "cust_person_info",
                                                    "field": "user_type",
                                                }
                                            ],
                                        }
                                    ],
                                }
                            ]
                        }
                    }
                },
            }
        ],
    }
    out = await_agent_clarification_node(state)
    messages = deserialize_messages(out["messages"])
    text = str(messages[-1].content)
    assert text.startswith("用户已完成澄清")
    assert "cust_person_info.user_type" in text
    assert "不要再询问已确认的项" in text
    assert "The user" not in text
    system = str(messages[0].content)
    assert "<memory_slots>" not in system
    assert "confirmed_calibers（用户已确认的口径" not in system
    assert "联系人类型为管理员" in text


# ── real corpus end-to-end (skipped when the corpus is not checked out) ─────


@pytest.mark.skipif(not _CORPUS.exists(), reason="pplatform wiki corpus not present")
def test_continuation_recall_keeps_baseline_tables_and_rehydrates_pages(
    monkeypatch,
) -> None:
    from apps.chat.agent_knowledge import AgentKnowledgePlane
    from apps.chat.steps import wiki_recall as wr
    from apps.knowledge.wiki.contract import PageContractError
    from apps.knowledge.wiki.recall import InMemoryWikiStore

    try:
        store = InMemoryWikiStore.load_dir(_CORPUS)
    except PageContractError as exc:
        pytest.skip(f"bound wiki corpus still uses retired enums/ contract: {exc}")
    monkeypatch.setattr(wr, "_store", lambda ds_id=None: store)
    monkeypatch.setattr(wr, "has_wiki_bound_corpus", lambda ds_id=None: True)
    monkeypatch.setattr(wr, "_ds_allowlisted", lambda ds_id: True)
    monkeypatch.setattr(wr, "_embedding_index", lambda store, ds_id: None)
    monkeypatch.setattr(wr, "datasource_databases", lambda ds: ["lowcode_pplatform"])
    llm = SimpleNamespace(ds=SimpleNamespace(id=1, type="mysql"))

    first = wr.retrieve_wiki_context(llm, "查询认证方式为平台录入的企业清单")
    assert "cust_company_info" in first["tables"]
    # Relevant identify_style pages are pinned and the catalog swaps topk.
    assert any("identify_style" in str(key) for key in first["page_keys"])
    plane = AgentKnowledgePlane()
    plane.merge_recall(first)
    catalog = plane.schema_catalog_text()
    assert "identify_style" in catalog
    assert "SIMPLE(SIMPLE)" not in catalog
    refs = plane.knowledge_refs()

    follow_up = "加上管理员和经办人的数量"
    cold = wr.retrieve_wiki_context(llm, follow_up)
    assert "cust_company_info" not in cold["tables"]  # the follow-up alone loses it

    req = build_recall_request(
        follow_up,
        baseline_sql=(
            "SELECT c.cust_name, c.identify_style, c.create_time FROM cust_company_info c "
            "WHERE c.identify_style = 'AGW_BUILD'"
        ),
        prior_questions=["查询认证方式为平台录入的企业清单"],
        prior_page_keys=refs["page_keys"],
        prior_tables=refs["tables"],
        dialect="mysql",
    )
    warm = wr.retrieve_wiki_context(llm, req)
    assert warm["tables"][0] == "cust_company_info"
    assert "cust_person_info" in warm["tables"]
    assert set(refs["page_keys"]) <= set(warm["page_keys"])
    assert set(warm["evidence_fields"]["cust_company_info"]) >= {
        "cust_name",
        "identify_style",
        "create_time",
    }
    plane2 = AgentKnowledgePlane()
    plane2.merge_recall(warm)
    catalog2 = plane2.schema_catalog_text()
    # All columns stay full lines (folding retired).
    assert "create_time:datetime, 创建时间" in catalog2
    assert "identify_style" in catalog2
    assert "user_type" in catalog2
    stats = plane2.prompt_stats()
    assert stats["schema_chars"] <= stats["schema_chars_full"]

    recalled = {"n": 0}
    orig = wr.wiki_recall

    def _count(*args: object, **kwargs: object):
        recalled["n"] += 1
        return orig(*args, **kwargs)

    monkeypatch.setattr(wr, "wiki_recall", _count)
    pin_req = RecallRequest.rehydrate(
        pin_tables=refs["tables"],
        pin_pages=refs["page_keys"],
        required_fields={
            "cust_company_info": ("cust_name", "identify_style", "create_time")
        },
        question=follow_up,
    )
    pin = wr.retrieve_wiki_context(llm, pin_req)
    assert recalled["n"] == 0
    assert pin_req.query == ""
    assert "cust_company_info" in pin["tables"]
    assert set(refs["page_keys"]) <= set(pin["page_keys"])


def test_search_wiki_mid_turn_pins_plane_working_set() -> None:
    """Mid-turn search_wiki pins the working set and does not concat old queries."""
    from apps.chat.agent_knowledge import AgentKnowledgePlane
    from apps.chat.tools.wiki_search import _continuation_request

    empty = _continuation_request(AgentKnowledgePlane(), "城市")
    assert empty.query == "城市"
    assert not empty.is_continuation

    plane = AgentKnowledgePlane()
    plane.merge_recall(
        {
            "query": "查询认证方式为平台录入的企业",
            "question": "查询认证方式为平台录入的企业",
            "tables": ["cust_company_info"],
            "page_keys": ["dicts/identify_style", "concepts/admin"],
            "schema_text": (
                "## 企业 (cust_company_info)\n"
                "identify_style:varchar, 认证方式, dict=identify_style\n"
                "create_time:datetime, 创建时间"
            ),
            "evidence_fields": {"cust_company_info": ["identify_style", "create_time"]},
            "wiki_passages": {"dicts/identify_style": "# identify_style\nAGW"},
        }
    )
    req = _continuation_request(plane, "城市")
    assert req.is_continuation
    assert req.question == "查询认证方式为平台录入的企业"
    assert req.query == "城市"
    assert "查询认证方式为平台录入的企业" not in req.query
    assert req.pin_tables == ("cust_company_info",)
    assert "dicts/identify_style" in req.pin_pages
    assert set(req.required_fields["cust_company_info"]) >= {
        "identify_style",
        "create_time",
    }

    named = _continuation_request(
        plane, "rules/excel-import-operation-config-rule 项目运营配置"
    )
    assert named.query == ""
    assert named.pin_tables == ("cust_company_info",)
    assert "rules/excel-import-operation-config-rule" in named.pin_pages
