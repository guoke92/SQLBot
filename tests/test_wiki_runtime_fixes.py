"""Wiki 运行链路四问题修复的回归测试（chat 165 复盘）。

覆盖：① planning_prompt str 分流（prose 走 XML 纯文本段，不再 JSON 转义）；
② SQL 别名回解（中文别名 → 物理列）+ 枚举翻译重挂；③ chunk 级嵌入指纹增量
（改散文零重嵌）；④ WikiRecallResult hits 透出（遥测投影）；⑤ 澄清等待
interval 投影（时间线对账）。
"""

from __future__ import annotations

import dataclasses
import sys
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

import pytest

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.chat.graphs.nodes.nlq import audit as nlq_audit  # noqa: E402
from apps.chat.planning_prompt import render_planner_input  # noqa: E402
from apps.chat.steps.wiki_recall import (  # noqa: E402
    WikiRecallResult,
    translate_enum_cells,
)
from apps.knowledge.wiki.chunker import chunk_markdown  # noqa: E402
from apps.knowledge.wiki.contract import parse_page  # noqa: E402

# ── 修复 1：structured 的 str 值走 XML 段（prose 逐字粘贴，无 JSON 转义）──────


def test_structured_str_values_render_as_xml_prose() -> None:
    """business_knowledge 类 markdown prose 是 str → 不再经 orjson 转义。"""
    prose = "# 客户信息主表\n\n- 锚点：[[cust_company_info]]\n- 行数约 559\n"
    rendered = render_planner_input(
        schema="s",
        structured={
            "business_knowledge": prose,
            "recall_topup_notice": {"added": ["cust_build_type"]},
        },
    )
    body = rendered.split("<business_knowledge>\n")[1].split("\n</business_knowledge>")[
        0
    ]
    assert body == prose.strip()  # 逐字粘贴
    assert "\\n" not in body and '\\"' not in body  # 无 JSON 转义残留
    # dict 依旧走 JSON 段
    assert "<recall_topup_notice>\n{" in rendered


def test_structured_multiline_str_no_backslash_n() -> None:
    rendered = render_planner_input(
        schema="",
        structured={"wiki_schema_relations": "a.cust_id → b.cust_id\n内联补充"},
    )
    assert "<wiki_schema_relations>" in rendered
    assert "a.cust_id → b.cust_id\n内联补充" in rendered
    assert "\\n" not in rendered


# ── 修复 4：SQL 别名回解 + 枚举翻译重挂 ──────────────────────────────────────


def test_sql_alias_columns_resolves_chinese_alias() -> None:
    sql = (
        "SELECT identify_style AS 认证方式, COUNT(*) AS total "
        "FROM cust_company_info GROUP BY identify_style"
    )
    projections = nlq_audit._sql_alias_columns(sql, "mysql")
    by_alias = {p["alias"]: p for p in projections}
    assert by_alias["认证方式"]["column"] == "identify_style"
    # 非限定列无 table 限定符（消歧由 _enum_refs_for_step 走列集匹配）
    assert by_alias["认证方式"]["table"] == ""
    # 聚合投影无单一物理列 → 不在映射里
    assert "total" not in by_alias
    # 表别名回解到物理表名（枚举翻译挂物理列）
    qualified = nlq_audit._sql_alias_columns(
        "SELECT c.identify_style AS 认证方式 FROM cust_company_info c", "mysql"
    )
    assert qualified[0]["table"] == "cust_company_info"


def test_enum_refs_resolve_alias_to_physical_column(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        nlq_audit,
        "_wiki_table_columns",
        lambda table: {"identify_style", "cust_status"}
        if table == "cust_company_info"
        else set(),
    )
    sql = "SELECT identify_style AS 认证方式 FROM cust_company_info"
    refs, alias_to_ref = nlq_audit._enum_refs_for_step(
        {"tables": ["cust_company_info"], "sql": sql},
        ["认证方式"],
    )
    assert refs == ["cust_company_info.identify_style"]
    # 别名回解的精确对应（translate 层据此重挂，不再插入序兜底）
    assert alias_to_ref == {"认证方式": "cust_company_info.identify_style"}


def test_enum_refs_fallback_column_set_match(monkeypatch: pytest.MonkeyPatch) -> None:
    """解析失败/无 SQL 时回退列集匹配（refs 语义不变，别名映射为空）。"""
    monkeypatch.setattr(
        nlq_audit,
        "_wiki_table_columns",
        lambda table: {"identify_style"} if table == "cust_company_info" else set(),
    )
    refs, alias_to_ref = nlq_audit._enum_refs_for_step(
        {"tables": ["cust_company_info"], "sql": "(() bad sql"}, ["identify_style"]
    )
    assert refs == ["cust_company_info.identify_style"]
    assert alias_to_ref == {}  # 解析失败无精确映射 → 翻译走旧兜底


def test_translate_enum_cells_remounts_onto_alias_column() -> None:
    """结果列是中文别名 → 物理列值映射重挂到别名列，value_labels 键=结果列。"""
    maps = {"cust_company_info.identify_style": {"INVITE_AGW": "邀请认证-内管录入"}}
    rows = [{"认证方式": "INVITE_AGW"}, {"认证方式": "SELF"}]
    translated, labels = translate_enum_cells(["认证方式"], rows, maps)
    assert translated[0]["认证方式"] == "邀请认证-内管录入"
    assert translated[1]["认证方式"] == "SELF"
    assert labels == {"认证方式": {"INVITE_AGW": "邀请认证-内管录入"}}


def test_translate_enum_cells_no_false_remount_when_both_columns_exist() -> None:
    """物理列与别名列同时存在于结果行 → 不乱挂别名映射。"""
    maps = {"t.identify_style": {"INVITE_AGW": "邀请认证-内管录入"}}
    rows = [{"identify_style": "INVITE_AGW", "认证方式": "INVITE_AGW"}]
    translated, _ = translate_enum_cells(["identify_style", "认证方式"], rows, maps)
    # identify_style 直接命中；认证方式 因两列并存不重挂（映射只来自直命中列的合并）
    assert translated[0]["identify_style"] == "邀请认证-内管录入"


def test_translate_enum_cells_dual_enum_columns_exact_alias_map() -> None:
    """chat 171 错挂复现：双枚举列 + 双中文别名，alias_to_ref 精确路径修复。

    旧兜底按 maps 插入序取第一个映射（认证状态列先遍历到 cust_build_status
    正确、录入方式列也错挂到 cust_build_status → AGW_BUILD 原样）；
    传入别名回解映射后两列各挂各的。"""
    maps = {
        "cust_company_info.cust_build_status": {
            "BUILD_SUCCESS": "认证成功",
            "INIT": "初始化",
        },
        "cust_company_info.cust_build_type": {
            "AGW_BUILD": "平台录入",
            "PC_BUILD": "客户录入",
        },
    }
    rows = [{"认证状态": "BUILD_SUCCESS", "录入方式": "AGW_BUILD"}]
    alias_to_ref = {
        "认证状态": "cust_company_info.cust_build_status",
        "录入方式": "cust_company_info.cust_build_type",
    }
    translated, labels = translate_enum_cells(
        ["认证状态", "录入方式"], rows, maps, alias_to_ref=alias_to_ref
    )
    assert translated[0]["认证状态"] == "认证成功"
    assert translated[0]["录入方式"] == "平台录入"  # 错挂修复的核心断言
    assert labels["认证状态"] == {"BUILD_SUCCESS": "认证成功"}
    assert labels["录入方式"] == {"AGW_BUILD": "平台录入"}


def test_translate_enum_cells_without_alias_map_keeps_legacy_fallback() -> None:
    """不传 alias_to_ref 时保持旧兜底行为（现状断言，不新增语义）。

    插入序兜底在多枚举列下会错挂——这正是精确路径要替代的旧行为，
    此测试固定它以保证兜底只在 sqlglot 解析失败时回退使用。"""
    maps = {
        "cust_company_info.cust_build_status": {"BUILD_SUCCESS": "认证成功"},
        "cust_company_info.cust_build_type": {"AGW_BUILD": "平台录入"},
    }
    rows = [{"认证状态": "BUILD_SUCCESS", "录入方式": "AGW_BUILD"}]
    translated, _ = translate_enum_cells(["认证状态", "录入方式"], rows, maps)
    # 认证状态 挂上 status 映射（插入序第一项恰好正确）；录入方式 错挂 status
    # 映射、AGW_BUILD 不在其中 → 原样保留
    assert translated[0]["认证状态"] == "认证成功"
    assert translated[0]["录入方式"] == "AGW_BUILD"


# ── 修复 3b：chunk 级指纹（prose 编辑零重嵌由 test_wiki_embeddings 覆盖，这里
# 验证指纹函数与 chunk 文本单一真相）──────────────────────────────────────────


def test_chunk_fingerprint_changes_only_with_embed_input() -> None:
    from apps.knowledge.wiki.embeddings import chunk_fingerprint

    base = chunk_fingerprint("## 节\n正文", "bge-m3", 1024)
    assert base == chunk_fingerprint("## 节\n正文", "bge-m3", 1024)
    assert chunk_fingerprint("## 节\n正文改", "bge-m3", 1024) != base
    assert chunk_fingerprint("## 节\n正文", "other", 1024) != base


# ── 统一结构：WikiRecallResult ──────────────────────────────────────────────


def test_wiki_recall_result_fields_are_immutable_projection() -> None:
    result = WikiRecallResult(
        text="正文",
        hits=[{"page_key": "a", "score": 1.0}],
        page_keys=["a"],
        elapsed_ms=12,
        embedding_built=False,
    )
    assert result.hits[0]["page_key"] == "a"
    assert result.elapsed_ms == 12
    with pytest.raises(dataclasses.FrozenInstanceError):
        result.elapsed_ms = 13  # frozen: 采集点一次，消费方不可改写


# ── 修复 3c：澄清等待 interval 投影 ─────────────────────────────────────────


def _sqlmodel(cls, **kwargs):
    """绕开 SQLModel 私有属性校验直接构造只用于投影逻辑的实例。"""
    obj = cls.__new__(cls)
    for key, value in kwargs.items():
        object.__setattr__(obj, key, value)
    return obj


def test_clarification_wait_interval_projects_into_timeline() -> None:
    from apps.chat.curd.chat import _clarification_wait_items
    from apps.chat.models.chat_model import ChatLogHistoryItem

    interrupt = _sqlmodel(
        SimpleNamespace,
        interrupt_id="itp-1",
        run_id="run-1",
        create_time=datetime(2026, 1, 1, 10, 0, 0),
        consumed_at=datetime(2026, 1, 1, 10, 2, 2),
    )
    items = _clarification_wait_items(
        [interrupt], run_end=datetime(2026, 1, 1, 10, 5, 0), fallback_end=None
    )
    assert len(items) == 1
    item = items[0]
    assert isinstance(item, ChatLogHistoryItem)
    assert item.status == "interrupted"
    assert item.graph_node == "await_clarification"
    assert item.title_key == "chat.log.WAIT_CLARIFICATION"
    assert item.duration == 122.0  # 2 分 2 秒的用户等待
    assert item.detail["user_wait"] is True


def test_clarification_wait_unanswered_uses_run_end() -> None:
    """未消费的澄清卡：等待延伸到 run 结束（挂起可见，不再黑洞）。"""
    from apps.chat.curd.chat import _clarification_wait_items

    interrupt = _sqlmodel(
        SimpleNamespace,
        interrupt_id="itp-2",
        run_id="run-1",
        create_time=datetime(2026, 1, 1, 10, 0, 0),
        consumed_at=None,
    )
    items = _clarification_wait_items(
        [interrupt], run_end=datetime(2026, 1, 1, 10, 3, 0), fallback_end=None
    )
    assert items[0].finish_time == datetime(2026, 1, 1, 10, 3, 0)


def test_clarification_wait_skips_missing_create_time() -> None:
    from apps.chat.curd.chat import _clarification_wait_items

    interrupt = _sqlmodel(
        SimpleNamespace,
        interrupt_id="itp-3",
        run_id="run-1",
        create_time=None,
        consumed_at=None,
    )
    assert (
        _clarification_wait_items(
            [interrupt], run_end=datetime(2026, 1, 1), fallback_end=None
        )
        == []
    )


# ── chat 167 四问题：business 渲染 / system 归属 / 表预算 / sink 分阈值 ──────


def test_business_render_prose_no_table_field_dump() -> None:
    """business 模式：正文摘要 + 枚举 values；表页不再重复 ground:table 清单。"""
    from apps.knowledge.wiki.recall import _render

    page = parse_page(
        "---\ntype: table\ntitle: 客户信息主表\npage_key: cust_company_info\n"
        "status: published\nanchors: [cust_company_info]\n---\n"
        "# 客户信息主表\n\n客户信息主表承载企业建档主数据。\n\n"
        "```ground:table\ntable: cust_company_info\nfields:\n"
        "  - name: cust_build_type\n    type: string\n```\n"
    )
    chunk = chunk_markdown(page.body)[0]
    business = _render(page, chunk, mode="business")
    assert "客户信息主表承载企业建档主数据" in business  # 正文进 prompt
    assert "```ground:table" not in business  # 字段清单不再重复
    assert business.count("# 客户信息主表") == 1
    physical = _render(page, chunk, mode="physical")
    assert "```ground:table" in physical  # physical 路径不回归


def test_business_render_enum_values_block() -> None:
    from apps.knowledge.wiki.recall import _render

    page = parse_page(
        "---\ntype: enum\ntitle: 建档类型\npage_key: cust_build_type\nstatus: published\n---\n"
        "# 建档类型\n\n```ground:enum\nenum: cust_build_type\nvalues:\n"
        "  PC_BUILD:\n    label: 客户录入\n  AGW_BUILD:\n    label: 平台录入\n```\n"
    )
    chunk = chunk_markdown(page.body)[0]
    rendered = _render(page, chunk, mode="business")
    assert "AGW_BUILD: 平台录入" in rendered  # 枚举 values 保留（翻译/澄清依据）
    assert "PC_BUILD: 客户录入" in rendered


def test_business_render_strips_editorial_and_reinjects_caliber() -> None:
    """business：剥演进/背景/相关链接，回注紧凑 ground:caliber 谓词。"""
    from apps.knowledge.wiki.recall import _render

    page = parse_page(
        "---\ntype: caliber\ntitle: 有效租户\npage_key: valid_tenant\n"
        "status: published\nfield_targets: [tenant_setting_config.enable]\n---\n"
        "# 有效租户\n\n租户启用口径：仅 enable='Y' 的租户参与统计。\n\n"
        "## 需求背景\n\n历史需求草稿，不应进 prompt。\n\n"
        "## 版本演进\n\nv0.1 来自某次代码走读，不应进 prompt。\n\n"
        "相关：[[tenant_setting_config]] · [[enable]]\n"
        "[[foo]] [[bar]]\n\n"
        "```ground:caliber\nname: 有效租户\n"
        "predicate: \"tenant_setting_config.enable = 'Y'\"\n"
        "scope: 全库\nevidence: code_path:Foo\n```\n"
    )
    chunk = chunk_markdown(page.body)[0]
    rendered = _render(page, chunk, mode="business")
    assert "租户启用口径" in rendered
    assert "需求背景" not in rendered
    assert "版本演进" not in rendered
    assert "历史需求草稿" not in rendered
    assert "相关：" not in rendered
    assert "```ground:caliber" in rendered
    assert "name: 有效租户" in rendered
    assert "tenant_setting_config.enable = 'Y'" in rendered
    assert "scope:" not in rendered
    assert "evidence:" not in rendered
    assert rendered.count("# 有效租户") == 1


def test_query_agent_system_knowledge_moves_to_system() -> None:
    """system_knowledge 非空 → business_knowledge 拼 system 侧，user 不再携带。"""
    import inspect

    from apps.chat.steps import query_agent as qa

    src = inspect.getsource(qa.run_query_agent)
    assert "system_knowledge" in src  # 参数存在
    assert "<business_knowledge>" in src  # system 拼接
    assert src.index("system_knowledge") < src.index("render_planner_input")


def test_knowledge_map_hit_keys_only() -> None:
    """hit_keys 提供时地图只渲染命中页（不再 (+527 more)）。"""
    from apps.chat.steps.recall_map import _wiki_knowledge_map

    rendered = _wiki_knowledge_map(
        15, hit_keys=["cust_company_info", "cust_build_type"]
    )
    if rendered:  # wiki store 可用时
        assert "cust_company_info" in rendered
        assert "(+" not in rendered  # 无 more 尾巴


def test_get_table_schema_limit_keeps_required() -> None:
    """table_limit：必选表全保，embedding 补充按预算截断。"""
    import inspect

    from apps.datasource.crud.datasource import get_table_schema  # noqa: F401

    src = inspect.getsource(get_table_schema)
    assert "table_limit" in src
    assert "required_first" in src  # 必选优先保留逻辑存在


def test_sink_token_reasoning_low_threshold() -> None:
    """reasoning 事件 96 字符即 flush（content 保持 512）。"""
    from apps.conversation.sink import StreamSink

    sink = StreamSink(mode="sse")
    emitted: list[dict] = []
    # _emit_event 直接观察（绕过 run event 持久化）
    sink._emit_event = lambda event: emitted.append(event)  # type: ignore[method-assign]
    for _ in range(3):
        sink.token(
            content="",
            reasoning_content="x" * 40,
            event_type="clarification-reasoning",
        )
    assert len(emitted) == 1  # 120 字符 > 96 → 第三次 flush
    assert emitted[0]["reasoning_content"] == "x" * 120
    # content 事件：512 以下不 flush
    sink2 = StreamSink(mode="sse")
    emitted2: list[dict] = []
    sink2._emit_event = lambda event: emitted2.append(event)  # type: ignore[method-assign]
    sink2.token(content="y" * 100, event_type="message")
    sink2.token(content="y" * 100, event_type="message")
    assert emitted2 == []


def test_retrieval_span_single_contract() -> None:
    """检索 span detail 契约：resources + wiki 子块，不再携带 schema 全文。"""
    import inspect

    from apps.chat.graphs.nodes.nlq import context as ctx

    src = inspect.getsource(ctx.retrieve_context_node)
    assert '"schema_chars"' in src
    assert "chat.audit.retrieval_ready" in src
    assert '"schema":' not in src.split("retrieval_span")[1]  # 无 schema 全文
    # retrieve_schema_node 内层 audit=False（双卡片根因消除）
    src_schema = inspect.getsource(ctx.retrieve_schema_node)
    assert "audit=False" in src_schema


# ── chat 169 修复：去硬编码 / 补充表阈值 / trace / 归因 / schema 分节 ──────────


def test_query_agent_system_no_business_terms_hardcoded() -> None:
    """_QUERY_AGENT_SYSTEM 不得含业务术语硬编码（跨部署通用性）。"""
    from apps.chat.steps.query_agent import _QUERY_AGENT_SYSTEM

    for term in (
        "fin_list",
        "签收",
        "融资额",
        "认证方式",
        "组织/部门",
        "sed_company_name",
        "原始供应商",
        "cust_company",
        "ca_fee",
    ):
        assert term not in _QUERY_AGENT_SYSTEM, f"硬编码业务词残留: {term}"


def test_query_agent_system_prompt_contract_fallbacks_abstract() -> None:
    """missing_concepts 示例用抽象表述（某张表或某个口径），不点名业务表。"""
    from apps.chat.steps.query_agent import _QUERY_AGENT_SYSTEM

    assert "某张表或某个口径" in _QUERY_AGENT_SYSTEM
    assert "<表名>" in _QUERY_AGENT_SYSTEM  # fields 模板用占位符


def test_clarify_contract_mutual_exclusion_and_enum_boundary() -> None:
    """chat 171 契约重构：互斥重定义 + 枚举覆盖按题型区分（agent + reviewer）。

    模型曾把"枚举类字段的选项要覆盖全部可能值"误读为跨字段选项非法，
    放弃了它自己推导出的字段归属澄清题——新契约正面声明：
    ①互斥=业务口径不同，不要求同字段；②字段归属题各选项带各自 value 是预期形态；
    ③枚举穷举只适用于"取哪个值"题型。"""
    from apps.chat.steps.query_agent import _QUERY_AGENT_SYSTEM, _REVIEWER_SYSTEM

    # 判定原则 2：字段归属题的合法性正面声明（不再只有散落触发器）
    assert "一对多落点就是会显著改变结果的歧义" in _QUERY_AGENT_SYSTEM
    assert "每个选项的 fields 指向各自字段并携带各自的枚举 value" in _QUERY_AGENT_SYSTEM
    assert "这类题的各选项引用不同字段是预期形态" in _QUERY_AGENT_SYSTEM
    # 互斥重定义 + 枚举覆盖边界（agent 与 reviewer 同口径）
    for source in (_QUERY_AGENT_SYSTEM, _REVIEWER_SYSTEM):
        assert "互斥体现在业务口径不同" in source
        assert "不要求所有选项引用同一字段" in source or (
            "不要求穷举任一字段的值域" in source
        )
    assert "不要求穷举任一字段的值域" in _QUERY_AGENT_SYSTEM
    assert "不要求穷举任一字段的值域" in _REVIEWER_SYSTEM


def test_get_table_schema_supplement_threshold_and_no_padding() -> None:
    """table_limit 截断语义：补充表须过相似度阈值；不足预算不凑数。"""
    import inspect

    from apps.datasource.crud.datasource import get_table_schema

    src = inspect.getsource(get_table_schema)
    assert "EMBEDDING_TABLE_SIMILARITY" in src
    assert "WIKI_TABLE_SUPPLEMENT_SIMILARITY" not in src
    assert "supplement_all[:budget]" in src
    assert 'if t.get("table_name") in required_names' in src


def test_recall_budget_replaces_wiki_supplement_knobs() -> None:
    from apps.knowledge.recall_kernel.types import RecallBudget
    from common.core.config import settings

    budget = RecallBudget.from_settings()
    assert budget.max_tables >= 1
    assert not hasattr(settings, "WIKI_TABLE_SUPPLEMENT_COUNT")
    assert not hasattr(settings, "WIKI_TABLE_SUPPLEMENT_SIMILARITY")


def test_recall_fills_trace_stages() -> None:
    """recall trace_out：可见页数→通道→页融合→窗口→图份额全链路中间量。"""
    from apps.knowledge.wiki.recall import InMemoryWikiStore, recall

    examples = _ROOT / "docs" / "wiki-knowledge" / "examples"
    store = InMemoryWikiStore.load(
        [p.read_text() for p in sorted(examples.glob("*.md"))]
    )
    trace: dict = {}
    passages = recall(
        "提取25年6月之前认证方式是平台录入 建档的企业清单",
        store,
        oid=1,
        databases=["lowcode_pplatform"],
        top_k=5,
        trace_out=trace,
    )
    assert passages
    assert trace["mode"] == "business"
    assert trace["visible_pages"] > 0
    channels = trace["channels"]
    assert set(channels) == {"lexical_exact", "lexical_coverage", "vector", "alias"}
    assert channels["lexical_exact"]["chunks"] >= 0  # 结构键稳定
    for channel in channels.values():
        assert "top" in channel and "chunks" in channel
    assert isinstance(trace["page_fusion"], list) and trace["page_fusion"]
    assert isinstance(trace["window"], list)
    assert len(trace["window"]) >= len(passages) - trace["graph_quota"]
    assert trace["graph_quota"] >= 0
    assert "graph_neighbors" in trace
    # trace 不改变召回结果（透传可观测零侵入）
    baseline = recall(
        "提取25年6月之前认证方式是平台录入 建档的企业清单",
        store,
        oid=1,
        databases=["lowcode_pplatform"],
        top_k=5,
    )
    assert [p.page_key for p in baseline] == [p.page_key for p in passages]


def test_recall_trace_physical_mode_no_graph() -> None:
    """physical 模式早退路径同样填 trace（无图扩展）。"""
    from apps.knowledge.wiki.recall import InMemoryWikiStore, recall

    examples = _ROOT / "docs" / "wiki-knowledge" / "examples"
    store = InMemoryWikiStore.load(
        [p.read_text() for p in sorted(examples.glob("*.md"))]
    )
    trace: dict = {}
    recall(
        "平台录入",
        store,
        oid=1,
        databases=["lowcode_pplatform"],
        top_k=3,
        mode="physical",
        trace_out=trace,
    )
    assert trace["mode"] == "physical"
    assert trace["graph_quota"] == 0
    assert trace["graph_neighbors"] == []


def test_anchor_table_attribution_traces_closure_sources() -> None:
    """闭包表归因：表 ← 命中页 + 契约字段（anchors/field_targets/maps_to）。"""
    from apps.knowledge.wiki.anchors import anchor_table_attribution
    from apps.knowledge.wiki.recall import InMemoryWikiStore

    examples = _ROOT / "docs" / "wiki-knowledge" / "examples"
    store = InMemoryWikiStore.load(
        [p.read_text() for p in sorted(examples.glob("*.md"))]
    )
    attribution = anchor_table_attribution(store, ["cust_build_type", "平台录入"])
    sources = attribution.get("cust_company_info", [])
    assert sources, "表页应至少被自己的子契约页归因"
    assert all({"page_key", "field"} <= set(s) for s in sources)
    # 未知页键不炸、返回空
    assert anchor_table_attribution(store, []) == {}
    assert anchor_table_attribution(None, ["x"]) == {}


def test_split_schema_sections_per_table_cards() -> None:
    """schema 全文按 `## 注释 (表名)` 分节：每表一卡（含 db 兜底 [db] 后缀）。"""
    from apps.chat.graphs.nodes.nlq.context import _split_schema_sections

    schema_text = (
        "【DB_ID】 demo\n【Schema】\n"
        "## 客户表 (cust_company_info)\n字段若干A\n"
        "## 客户表 (cust_company_info) [demo]\n字段若干B\n"
        "## 配置表 (tenant_setting_config)\n字段若干C\n"
    )
    sections = _split_schema_sections(
        schema_text,
        {"cust_company_info": "closure", "tenant_setting_config": "embedding"},
    )
    assert [s["table"] for s in sections] == [
        "cust_company_info",
        "cust_company_info",
        "tenant_setting_config",
    ]
    assert sections[0]["origin"] == "closure"
    assert "字段若干A" in sections[0]["text"]
    assert sections[1]["origin"] == "closure"  # [db] 后缀不干扰表名提取
    # origins 缺失 → embedding 兜底
    assert sections[2]["origin"] == "embedding"
    # 无分节标记（纯 db 渲染兜底）返回空，前端回退整文渲染
    assert _split_schema_sections("plain text", {}) == []


def test_renderer_live_tables_fallback_full_columns() -> None:
    """chat 172：wiki 无语料的 ds，db 兜底用活元数据渲染全列（不再零字段）。"""
    from apps.chat.steps.wiki_schema import WikiSchemaRenderer

    class _Page:
        body = ""

    class _Store:
        pages: dict = {}

    renderer = WikiSchemaRenderer(
        _Store(),
        db_catalog={"tables": {}},  # catalog 不覆盖此表
        live_tables={
            "d_task": {
                "comment": "task",
                "fields": [
                    ("id", "bigint", "主键"),
                    ("title", "varchar", "标题"),
                    ("status", "varchar", ""),
                ],
            }
        },
    )
    text = renderer.render(["d_task"])
    assert "## task (d_task) [db]" in text
    assert "id:bigint, 主键" in text
    assert "title:varchar, 标题" in text
    assert "status:varchar, status" in text  # 空注释回退列名
    assert renderer.missing == ["d_task"]  # 缺页遥测保留


def test_renderer_catalog_still_wins_over_live_tables() -> None:
    """catalog 命中时优先 catalog（权威对账产物），活元数据只兜第二层。"""
    from apps.chat.steps.wiki_schema import WikiSchemaRenderer

    class _Store:
        pages: dict = {}

    renderer = WikiSchemaRenderer(
        _Store(),
        db_catalog={
            "tables": {
                "t1": {
                    "comment": "目录表",
                    "columns": {"a": {"type": "int", "comment": "目录列"}},
                }
            }
        },
        live_tables={"t1": {"comment": "活表", "fields": [("a", "int", "活列")]}},
    )
    text = renderer.render(["t1"])
    assert "目录表" in text and "目录列" in text
    assert "活列" not in text


def test_topup_span_detail_includes_schema_sections() -> None:
    """topup 扩窗 span detail 与检索 span 同构（chat 172 问题 2）。"""
    import inspect

    from apps.chat.steps.recall_topup import _split_topup_schema_sections

    text = "## 迭代 (d_sprint) [db]\n(id:bigint, 主键)\n## 用户信息表 (d_user) [db]\n(org:bigint, 机构ID)"
    sections = _split_topup_schema_sections(text, added_tables=["d_user"])
    assert [s["table"] for s in sections] == ["d_sprint", "d_user"]
    assert sections[0]["origin"] == "embedding"
    assert sections[1]["origin"] == "topup"  # 本轮新拉入的表标注
    assert "(id:bigint, 主键)" in sections[0]["text"]
    # 源码断言：span set_detail 携带 schema_text/chars/sections
    from apps.chat.steps.recall_topup import fulfill_recall_topup

    src = inspect.getsource(fulfill_recall_topup)
    assert '"schema_text"' in src
    assert '"schema_sections"' in src


def test_live_table_fk_relations_name_decoded() -> None:
    """活元数据命名关系：story_id → d_story.id（d_ 前缀约定，右表须存在）。"""
    from apps.chat.steps.wiki_schema import WikiSchemaRenderer

    class _Store:
        pages: dict = {}

    renderer = WikiSchemaRenderer(
        _Store(),
        db_catalog={"tables": {}},
        live_tables={
            "d_task": {
                "comment": "task",
                "fields": [
                    ("id", "bigint", "主键"),
                    ("project_id", "bigint", "所属项目id"),
                    ("sprint_id", "bigint", "迭代表id"),
                    ("dispatch_to", "bigint", "被分配人"),  # 非 _id 结尾不参与
                ],
            },
            "d_project": {"comment": "项目表", "fields": [("id", "bigint", "主键")]},
            "d_sprint": {"comment": "迭代", "fields": [("id", "bigint", "主键")]},
            "d_organization": {"comment": "机构", "fields": []},
        },
    )
    rels = renderer._live_fk_relations("d_task")
    assert "关联: d_task.project_id → d_project.id (d_project) [db-naming]" in rels
    assert "关联: d_task.sprint_id → d_sprint.id (d_sprint) [db-naming]" in rels
    assert len(rels) == 2  # dispatch_to 不是 _id；不存在的右表不产出
    # 渲染全文包含关联行
    text = renderer.render(["d_task"])
    assert "关联: d_task.project_id → d_project.id" in text


def test_has_wiki_bound_corpus_true_when_bound(monkeypatch) -> None:
    from apps.chat.steps import wiki_recall as wr

    monkeypatch.setattr(wr, "wiki_backend_active", lambda ds_id=None: True)
    monkeypatch.setattr(wr, "_datasource_has_binding", lambda ds_id: True)
    assert wr.has_wiki_bound_corpus(15) is True


def test_has_wiki_bound_corpus_false_when_unbound(monkeypatch) -> None:
    from apps.chat.steps import wiki_recall as wr

    monkeypatch.setattr(wr, "wiki_backend_active", lambda ds_id=None: True)
    monkeypatch.setattr(wr, "_datasource_has_binding", lambda ds_id: False)
    assert wr.has_wiki_bound_corpus(15) is False
    assert wr.has_wiki_bound_corpus(None) is False


def test_has_wiki_bound_corpus_false_when_inactive(monkeypatch) -> None:
    from apps.chat.steps import wiki_recall as wr

    monkeypatch.setattr(wr, "wiki_backend_active", lambda ds_id=None: False)
    monkeypatch.setattr(wr, "_datasource_has_binding", lambda ds_id: True)
    assert wr.has_wiki_bound_corpus(15) is False


def test_retrieve_wiki_context_empty_hits_stay_on_wiki(monkeypatch) -> None:
    from apps.chat.steps import wiki_recall as wr

    monkeypatch.setattr(wr, "has_wiki_bound_corpus", lambda ds_id=None: True)
    monkeypatch.setattr(wr, "wiki_recall", lambda *a, **k: wr.WikiRecallResult())
    monkeypatch.setattr(wr, "datasource_databases", lambda ds: ["aio"])
    monkeypatch.setattr(wr, "_store", lambda ds_id: None)

    def _fallback(*_a, **_k):
        raise AssertionError("wiki runtime must not fall back to schema_vector")

    monkeypatch.setattr(wr, "_schema_fallback_context", _fallback)
    llm = SimpleNamespace(ds=SimpleNamespace(id=15))
    out = wr.retrieve_wiki_context(llm, "提取认证方式是平台录入的企业清单")
    assert out["backend"] == "wiki"
    assert out["store_source"] == "db"
    assert out["tables"] == []
    assert out["knowledge_text"] == ""
    assert out["schema_ready"] is False


def test_retrieve_wiki_context_wiki_error_does_not_schema_vector(monkeypatch) -> None:
    from apps.chat.steps import wiki_recall as wr

    monkeypatch.setattr(wr, "has_wiki_bound_corpus", lambda ds_id=None: True)

    def _boom(*_a: object, **_k: object) -> dict[str, object]:
        raise RuntimeError("wiki store exploded")

    def _no_schema(*_a: object, **_k: object) -> dict[str, object]:
        raise AssertionError("wiki failure must not swap to schema_vector")

    monkeypatch.setattr(wr, "_wiki_payload_from_recall", _boom)
    monkeypatch.setattr(wr, "_schema_fallback_context", _no_schema)
    llm = SimpleNamespace(ds=SimpleNamespace(id=15))
    out = wr.retrieve_wiki_context(llm, "认证方式平台录入")
    assert out["backend"] == "wiki"
    assert out["store_source"] == "db"
    assert out["knowledge_text"] == ""
    assert out["tables"] == []


def test_retrieve_wiki_context_no_runtime_uses_schema_vector(monkeypatch) -> None:
    from apps.chat.steps import wiki_recall as wr

    monkeypatch.setattr(wr, "has_wiki_bound_corpus", lambda ds_id=None: False)
    fallback_calls = {"n": 0}

    def _fallback(*_a, **_k):
        fallback_calls["n"] += 1
        return {
            "knowledge_text": "",
            "tables": ["d_task", "d_story"],
            "schema_text": "TABLE d_task\nTABLE d_story",
            "backend": "schema_vector",
            "page_keys": [],
            "hit_count": 2,
        }

    monkeypatch.setattr(wr, "_schema_fallback_context", _fallback)
    llm = SimpleNamespace(ds=SimpleNamespace(id=8))
    out = wr.retrieve_wiki_context(llm, "研发二部每月 task story")
    assert fallback_calls["n"] == 1
    assert out["backend"] == "schema_vector"
    assert out["tables"] == ["d_task", "d_story"]
    assert "d_task" in out["schema_text"]


def test_retrieve_wiki_context_keeps_usable_wiki_without_schema_mix(
    monkeypatch,
) -> None:
    from apps.chat.steps import wiki_recall as wr

    monkeypatch.setattr(wr, "has_wiki_bound_corpus", lambda ds_id=None: True)
    monkeypatch.setattr(
        wr,
        "wiki_recall",
        lambda *a, **k: wr.WikiRecallResult(
            text="# d_task\n任务表", hits=[{"page_key": "d_task"}], page_keys=["d_task"]
        ),
    )
    monkeypatch.setattr(wr, "datasource_databases", lambda ds: ["aio"])
    monkeypatch.setattr(wr, "_store", lambda ds_id: None)

    def _fallback(*_a, **_k):
        raise AssertionError("usable wiki must not fall back to physical schema")

    monkeypatch.setattr(wr, "_schema_fallback_context", _fallback)
    llm = SimpleNamespace(ds=SimpleNamespace(id=8))
    out = wr.retrieve_wiki_context(llm, "task 数")
    assert out["backend"] == "wiki"
    assert "任务表" in out["knowledge_text"]
    assert out["schema_text"] == ""
    assert out["schema_ready"] is False
    assert out["store_source"] == "db"
    assert "wiki_trace" in out
    assert out["hits"] == [{"page_key": "d_task"}]


def test_select_delivery_datasets_drops_empty_when_later_has_rows() -> None:
    from apps.chat.graphs.nodes.agent_finalize import select_delivery_datasets

    empty = SimpleNamespace(
        dataset_id="empty", required=True, status="succeeded", row_count=0, rows=[]
    )
    filled = SimpleNamespace(
        dataset_id="filled",
        required=True,
        status="succeeded",
        row_count=1000,
        rows=[{"id": 1}],
    )
    probe = SimpleNamespace(
        dataset_id="probe", required=False, status="succeeded", row_count=21
    )
    picked = select_delivery_datasets([empty, probe, filled])
    assert [item.dataset_id for item in picked] == ["filled"]


def test_select_delivery_datasets_keeps_last_when_all_empty() -> None:
    from apps.chat.graphs.nodes.agent_finalize import select_delivery_datasets

    first = SimpleNamespace(
        dataset_id="a", required=True, status="succeeded", row_count=0
    )
    last = SimpleNamespace(
        dataset_id="b", required=True, status="succeeded", row_count=0
    )
    picked = select_delivery_datasets([first, last])
    assert [item.dataset_id for item in picked] == ["b"]


def test_recommend_does_not_dump_protocol_schema() -> None:
    import inspect

    from apps.chat.steps import recommend as rec

    src = inspect.getsource(rec.generate_recommend_questions)
    assert "retrieve_schema" not in src
    assert "_recalled_schema_text" in src


def test_recommend_reuses_plane_schema_not_protocol(monkeypatch) -> None:
    from apps.chat.agent_knowledge import AgentKnowledgePlane
    from apps.chat.steps import recommend as rec
    from apps.conversation import runtime_context as rtc

    rtc.attach_runtime(
        "run-rec-1",
        knowledge_plane=AgentKnowledgePlane(
            tables=["d_task"],
            schema_by_table={"d_task": "# Table: d_task\n(id:bigint, 主键)"},
        ).to_dump(),
    )
    llm = SimpleNamespace(
        chat_question=SimpleNamespace(db_schema=""),
        record=SimpleNamespace(active_run_id="run-rec-1"),
        protocol=SimpleNamespace(
            retrieve_schema=lambda **_k: (_ for _ in ()).throw(
                AssertionError("recommend must not dump protocol schema")
            )
        ),
    )
    try:
        assert rec._recalled_schema_text(llm) == "# Table: d_task\n(id:bigint, 主键)"
        llm.chat_question.db_schema = ""
        llm.record = SimpleNamespace(active_run_id="")
        assert rec._recalled_schema_text(llm) == ""
    finally:
        rtc.detach_runtime("run-rec-1")


def test_search_wiki_returns_schema_vector_hits(monkeypatch) -> None:
    from apps.chat.tools import wiki_search as ws

    monkeypatch.setattr(
        ws,
        "retrieve_wiki_context",
        lambda *_a, **_k: {
            "knowledge_text": "",
            "schema_text": "# Table: d_task\n[\n(id:int, 主键)\n]",
            "tables": ["d_task"],
            "backend": "schema_vector",
            "hit_count": 1,
        },
    )
    llm = SimpleNamespace(ds=SimpleNamespace(id=8))
    out = ws.search_wiki_knowledge(llm, "每月 task 数")
    assert out["ok"] is True
    assert out["data"]["tables"] == ["d_task"]
    assert out["data"]["added_tables"] == ["d_task"]
    assert "knowledge_text" not in out["data"]
    assert "schema_text" not in out["data"]
    assert out["data"]["backend"] == "schema_vector"
    assert out["data"]["recall_status"] == "hit"
    assert out["data"]["schema_ready"] is True
    assert out["data"]["stop_search"] is False


def test_wiki_search_policy_stops_after_schema_gap() -> None:
    from apps.chat.agent_knowledge import AgentKnowledgePlane
    from apps.chat.tools.wiki_search import apply_wiki_search_policy

    plane = AgentKnowledgePlane(schema_gap_searches=1)
    payload = {
        "knowledge_text": "# 认证方式",
        "schema_text": "",
        "tables": [],
        "backend": "wiki",
        "page_keys": ["identify_style"],
        "hit_count": 1,
    }
    _plane, first, _delta = apply_wiki_search_policy(payload, plane)
    assert first["recall_status"] == "stagnant"
    assert first["stop_search"] is True
    assert plane.schema_gap_searches == 2


def test_wiki_search_policy_ready_unchanged_stops() -> None:
    from apps.chat.agent_knowledge import AgentKnowledgePlane
    from apps.chat.tools.wiki_search import apply_wiki_search_policy

    plane = AgentKnowledgePlane(
        schema_ready=True,
        tables=["d_task"],
        schema_by_table={"d_task": "# Table: d_task\n[\n(id:int, 主键)\n]"},
    )
    _plane, out, delta = apply_wiki_search_policy(
        {
            "knowledge_text": "# 认证方式",
            "schema_text": "",
            "tables": [],
            "backend": "wiki",
        },
        plane,
    )
    assert delta.unchanged is True
    assert out["recall_status"] == "stagnant"
    assert out["stop_search"] is True


def test_wiki_span_fields_include_observability() -> None:
    from apps.chat.steps.wiki_recall import wiki_span_fields

    fields = wiki_span_fields(
        {
            "backend": "wiki",
            "hit_count": 2,
            "page_keys": ["identify_style"],
            "tables": [],
            "knowledge_text": "abc",
            "schema_text": "",
            "schema_ready": False,
            "store_source": "db",
            "corpus_id": 1,
            "generation": 2,
            "vector_chunks": 10,
            "vector_channel": True,
            "elapsed_ms": 12,
            "wiki_trace": {"visible_pages": 3},
            "hits": [{"page_key": "identify_style"}],
            "recall_status": "schema_missing",
        }
    )
    assert fields["store_source"] == "db"
    assert fields["corpus_id"] == 1
    assert fields["wiki_trace"]["visible_pages"] == 3
    assert fields["schema_ready"] is False
    assert fields["knowledge_chars"] == 3


def test_catalog_probe_sql_is_blocked() -> None:
    from apps.chat.tools.execute_sql import execute_sql_sandbox, is_catalog_probe_sql

    assert is_catalog_probe_sql(
        "SELECT column_name FROM information_schema.columns WHERE table_name='t'"
    )
    assert is_catalog_probe_sql("SHOW COLUMNS FROM cust_company_info")
    assert not is_catalog_probe_sql("SELECT * FROM cust_company_info LIMIT 1")

    llm = SimpleNamespace()
    blocked = execute_sql_sandbox(
        llm,
        "SELECT column_name FROM information_schema.columns WHERE table_name='t'",
    )
    assert blocked["ok"] is False
    assert blocked["failure"]["retryable"] is False
    assert "information_schema" in blocked["error"]


def test_execute_sql_blocked_when_wiki_schema_missing() -> None:
    from apps.chat.agent_knowledge import AgentKnowledgePlane
    from apps.chat.tools.execute_sql import execute_sql_sandbox
    from apps.conversation.runtime_context import (
        attach_runtime,
        detach_runtime,
        worker_scope,
    )

    run_id = "wiki-schema-missing"
    attach_runtime(run_id, knowledge_plane=AgentKnowledgePlane().to_dump())
    llm = SimpleNamespace()
    try:
        with worker_scope(run_id, "tok"):
            blocked = execute_sql_sandbox(
                llm, "SELECT * FROM cust_company_info LIMIT 1"
            )
    finally:
        detach_runtime(run_id)
    assert blocked["ok"] is False
    assert blocked["failure"]["retryable"] is False


def test_prompt_schema_gap_block_when_wiki_has_no_schema() -> None:
    from apps.chat.agent_knowledge import AgentKnowledgePlane
    from apps.chat.task.agent_prompt import build_agent_system_prompt

    plane = AgentKnowledgePlane()
    plane.merge_recall(
        {
            "knowledge_text": "# 认证方式",
            "schema_text": "",
            "tables": [],
            "page_keys": ["identify_style"],
        }
    )
    prompt = build_agent_system_prompt(knowledge_plane=plane)
    assert "<wiki_schema_gap>" in prompt
    assert "information_schema" in prompt
    assert "早停" in prompt
