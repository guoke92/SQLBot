"""Deterministic 9-type wiki page renderer. No LLM, no repair.py."""

from __future__ import annotations

import datetime as dt
import re
import shutil
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

from tools.wiki_extract.emit import (
    _FlowList,
    _assert_isolated,
    _dump,
    _relation_neighbors,
    field_dict_page_key,
    render_dict_page,
    render_table_page,
)
from tools.wiki_extract.l1.pages import dict_from_page, parse_page
from tools.wiki_extract.l1.schema import PAGE_TYPES, dict_page_key

_SEMANTIC_DIRS = (
    "concepts",
    "processes",
    "calibers",
    "metrics",
    "rules",
    "scenarios",
    "patterns",
)


def emit_l1(
    model: dict[str, Any],
    out: Path,
    *,
    l0_dir: Path | None = None,
    copy_untouched: bool = True,
    extra_reviews: list[dict[str, Any]] | None = None,
) -> dict[str, int]:
    out = out.resolve()
    _assert_isolated(out)
    today = str(model.get("generated_at") or dt.date.today().isoformat())
    for name in ("tables", "dicts", *_SEMANTIC_DIRS):
        (out / name).mkdir(parents=True, exist_ok=True)
    runs = out / ".runs" / "l1"
    runs.mkdir(parents=True, exist_ok=True)
    raw = out / "_raw"
    raw.mkdir(parents=True, exist_ok=True)

    if l0_dir is not None and copy_untouched:
        _copy_untouched(Path(l0_dir), out)

    # Prefer richer labels already on disk (prior L1) when the L0 model is code-only.
    hydrate_dict_labels_from_dir(model, out / "dicts")
    # Keep table field dict/label aligned with the (possibly hydrated) dict pages.
    from tools.wiki_extract.l1.reconcile import sync_table_fields_with_dicts

    sync_table_fields_with_dicts(model)

    neighbors = _relation_neighbors(model.get("tables") or {})
    extra_neighbors = model.get("tables") or {}
    for tname, compiled in extra_neighbors.items():
        for other in compiled.get("related_tables") or []:
            neighbors.setdefault(tname, [])
            if other not in neighbors[tname]:
                neighbors[tname].append(other)

    index = _wiki_index(model)
    enhanced_tables = set(model.get("enhanced_tables") or [])
    table_count = 0
    for tname, compiled in (model.get("tables") or {}).items():
        compiled = dict(compiled)
        compiled.pop("clusters", None)
        for field in compiled.get("fields") or []:
            if isinstance(field, dict):
                field.pop("cluster", None)
        compiled["l1_enhanced"] = tname in enhanced_tables
        nb = neighbors.get(tname) or []
        has_dict = any(
            field_dict_page_key(field, tname)
            for field in compiled.get("fields") or []
            if isinstance(field, dict)
        )
        fallback = None if nb or has_dict else [("concepts", "catalog_summary")]
        (out / "tables" / f"{tname}.md").write_text(
            render_table_page(
                compiled,
                today,
                neighbors=nb,
                fallback_links=fallback,
                dicts=model.get("dicts") or {},
            ),
            encoding="utf-8",
        )
        table_count += 1

    # Always rewrite dict pages from the model so they stay consistent with tables.
    dict_count = 0
    for key, item in (model.get("dicts") or {}).items():
        (out / "dicts" / f"{key}.md").write_text(
            render_dict_page(_dict_item(item, key), today), encoding="utf-8"
        )
        dict_count += 1

    counts = {
        "tables": table_count,
        "dicts": dict_count,
        "concepts": _write_list(
            out / "concepts", model.get("concepts") or [], render_concept, today, index
        ),
        "processes": _write_list(
            out / "processes", model.get("processes") or [], render_process, today, index
        ),
        "calibers": _write_list(
            out / "calibers", model.get("calibers") or [], render_caliber, today, index
        ),
        "metrics": _write_list(
            out / "metrics", model.get("metrics") or [], render_metric, today, index
        ),
        "rules": _write_list(
            out / "rules", model.get("rules") or [], render_rule, today, index
        ),
        "scenarios": _write_list(
            out / "scenarios", model.get("scenarios") or [], render_scenario, today, index
        ),
        "patterns": _write_list(
            out / "patterns", model.get("patterns") or [], render_pattern, today, index
        ),
        "display": _write_list(
            out / "concepts", model.get("display") or [], render_display_page, today, index
        ),
    }
    catalog_page = render_catalog_summary(model, today)
    if catalog_page:
        (out / "concepts" / "catalog_summary.md").write_text(catalog_page, encoding="utf-8")
        counts["concepts"] = int(counts.get("concepts") or 0) + 1

    reviews = list(extra_reviews or model.get("reviews") or [])
    _write_reviews(runs / "reviews.yaml", reviews, today)
    _copy_instance_index(l0_dir, out)
    (out / "_index.md").write_text(_index_markdown(model, counts, today), encoding="utf-8")
    (out / "_log.md").write_text(_log_markdown(model, counts, today), encoding="utf-8")
    counts["reviews"] = len(reviews)
    counts["page_types"] = len(PAGE_TYPES)
    return counts


def render_concept(
    item: dict[str, Any], today: str, index: dict[str, set[str]] | None = None
) -> tuple[str, str]:
    key = _slug(item.get("concept_key") or item.get("page_key") or item.get("title"))
    title = str(item.get("title") or item.get("concept_key") or key)
    maps_to = str(item.get("maps_to") or "")
    field_targets = list(item.get("field_targets") or [])
    if maps_to and maps_to not in field_targets:
        field_targets = [maps_to, *field_targets]
    pairs = _pairs_from_physicals(field_targets)
    for other in item.get("also_confused_with") or []:
        pairs.append(("concepts", _slug(other)))
    related = _related_tables(pairs, index)
    front: dict[str, Any] = {
        "type": "concept",
        "title": title.replace(":", "："),
        "page_key": key,
        "belong": "concepts",
        "domain": item.get("domain") or "cust",
        "status": "draft",
        "aliases": _FlowList(list(item.get("aliases") or [])),
        "maps_to": maps_to,
        "field_targets": _FlowList(field_targets),
        "sources": _FlowList(_sources(item)),
        "created": today,
        "updated": today,
        "contract_version": "0.1",
    }
    if related:
        front["related"] = _FlowList(related)
    if item.get("also_confused_with"):
        front["also_confused_with"] = _FlowList(list(item["also_confused_with"]))
    if item.get("adjudication"):
        front["adjudication"] = item["adjudication"]
    body = str(item.get("explanation") or item.get("content") or title).strip()
    body = _with_page_links(body, pairs, index, self_belong="concepts", self_key=key)
    return key, _page(front, title, body)


def render_process(
    item: dict[str, Any], today: str, index: dict[str, set[str]] | None = None
) -> tuple[str, str]:
    key = _slug(item.get("process_key") or item.get("page_key"))
    title = str(item.get("title") or item.get("description") or key)
    table = str(item.get("table") or "")
    field = str(item.get("field") or "")
    physical = f"{table}.{field}" if table and field and "." not in field else field or table
    pairs = _pairs_from_physicals([physical, table, key])
    stages = []
    for stage in item.get("stages") or []:
        packed: dict[str, Any] = {"stage": stage.get("stage")}
        if stage.get("trigger"):
            packed["trigger"] = stage["trigger"]
        transitions = []
        for trans in stage.get("transitions") or []:
            row = {
                "from": trans.get("from"),
                "event": trans.get("event"),
                "to": trans.get("to"),
            }
            if trans.get("guards"):
                row["guards"] = trans["guards"]
            if trans.get("evidence"):
                row["evidence"] = trans["evidence"]
            transitions.append(row)
        if transitions:
            packed["transitions"] = transitions
        effects = []
        for trans in stage.get("transitions") or []:
            for effect in trans.get("side_effects") or []:
                effects.append(
                    {
                        "op": effect.get("action") or "update",
                        "table": effect.get("table"),
                        "fields": _FlowList(list(effect.get("fields") or [effect.get("field")])),
                    }
                )
                pairs.extend(_pairs_from_physicals([effect.get("table")]))
        if effects:
            packed["effects"] = effects
        stages.append(packed)
    related = _related_tables(pairs, index) or ([table] if table else [])
    front = {
        "type": "process",
        "title": title.replace(":", "："),
        "page_key": key,
        "belong": "processes",
        "domain": item.get("domain") or "cust",
        "status": "draft",
        "anchors": _FlowList([physical] if physical else []),
        "field_targets": _FlowList([physical] if physical else []),
        "sources": _FlowList(_sources(item, extra=_process_evidence(item))),
        "created": today,
        "updated": today,
        "contract_version": "0.1",
        "related": _FlowList(related),
    }
    ground = {
        "process": title,
        "field": physical,
        "entry": item.get("entry") or "",
        "stages": stages,
    }
    blurb = str(item.get("description") or f"钉列 `{physical}`。")
    body = blurb + "\n\n```ground:process\n" + _dump(ground).rstrip() + "\n```\n"
    body = _with_page_links(body, pairs, index, self_belong="processes", self_key=key)
    return key, _page(front, title, body)


def render_caliber(
    item: dict[str, Any], today: str, index: dict[str, set[str]] | None = None
) -> tuple[str, str]:
    key = _slug(item.get("caliber_key") or item.get("page_key"))
    title = str(item.get("title") or item.get("caliber_key") or key)
    pairs = _pairs_from_physicals(item.get("field_targets") or [])
    pairs.extend(_pairs_from_relations(item.get("using_relations") or []))
    related = _related_tables(pairs, index)
    front = {
        "type": "caliber",
        "title": title.replace(":", "："),
        "page_key": key,
        "belong": "calibers",
        "domain": item.get("domain") or "cust",
        "status": "draft",
        "field_targets": _FlowList(list(item.get("field_targets") or [])),
        "sources": _FlowList(_sources(item)),
        "created": today,
        "updated": today,
        "contract_version": "0.1",
    }
    if related:
        front["related"] = _FlowList(related)
    ground = {
        "caliber": title,
        "field_targets": _FlowList(list(item.get("field_targets") or [])),
        "predicate": item.get("predicate"),
        "scope": item.get("scope") or "global",
        "boundary": item.get("boundary") or "",
        "using_relations": list(item.get("using_relations") or []),
    }
    if item.get("evidence"):
        ground["evidence"] = item["evidence"]
    body = (
        str(item.get("boundary") or title)
        + "\n\n```ground:caliber\n"
        + _dump(ground).rstrip()
        + "\n```\n"
    )
    body = _with_page_links(body, pairs, index, self_belong="calibers", self_key=key)
    return key, _page(front, title, body)


def render_metric(
    item: dict[str, Any], today: str, index: dict[str, set[str]] | None = None
) -> tuple[str, str]:
    key = _slug(item.get("metric_key") or item.get("page_key"))
    title = str(item.get("title") or item.get("metric_key") or key)
    caliber = str(item.get("caliber") or "")
    grain = str(item.get("grain_table") or "")
    pairs = _pairs_from_physicals([grain, item.get("field")])
    pairs.extend(_pairs_from_relations(item.get("using_relations") or []))
    if caliber:
        pairs.append(("calibers", _slug(caliber)))
    related = [slug for slug in (caliber, grain) if slug]
    front = {
        "type": "metric",
        "title": title.replace(":", "："),
        "page_key": key,
        "belong": "metrics",
        "domain": item.get("domain") or "cust",
        "status": "draft",
        "sources": _FlowList(_sources(item)),
        "created": today,
        "updated": today,
        "contract_version": "0.1",
        "related": _FlowList(related),
    }
    ground = {
        "metric": title,
        "caliber": item.get("caliber"),
        "grain_table": item.get("grain_table"),
        "aggregation": item.get("aggregation"),
        "field": item.get("field"),
        "using_relations": list(item.get("using_relations") or []),
    }
    if item.get("evidence"):
        ground["evidence"] = item["evidence"]
    body = "```ground:metric\n" + _dump(ground).rstrip() + "\n```\n"
    body = _with_page_links(body, pairs, index, self_belong="metrics", self_key=key)
    return key, _page(front, title, body)


def render_rule(
    item: dict[str, Any], today: str, index: dict[str, set[str]] | None = None
) -> tuple[str, str]:
    key = _slug(item.get("rule_key") or item.get("page_key"))
    title = str(item.get("title") or item.get("rule_key") or key)
    pairs = _pairs_from_physicals(item.get("field_targets") or [])
    related = _related_tables(pairs, index)
    front = {
        "type": "rule",
        "title": title.replace(":", "："),
        "page_key": key,
        "belong": "rules",
        "domain": item.get("domain") or "cust",
        "status": "draft",
        "field_targets": _FlowList(list(item.get("field_targets") or [])),
        "sources": _FlowList(_sources(item)),
        "created": today,
        "updated": today,
        "contract_version": "0.1",
    }
    if related:
        front["related"] = _FlowList(related)
    ground = {
        "rule": title,
        "field_targets": _FlowList(list(item.get("field_targets") or [])),
        "impact": item.get("impact") or "write_constraint",
        "content": item.get("content") or title,
    }
    if item.get("evidence"):
        ground["evidence"] = item["evidence"]
    body = (
        str(item.get("content") or title)
        + "\n\n```ground:rule\n"
        + _dump(ground).rstrip()
        + "\n```\n"
    )
    body = _with_page_links(body, pairs, index, self_belong="rules", self_key=key)
    return key, _page(front, title, body)


def render_scenario(
    item: dict[str, Any], today: str, index: dict[str, set[str]] | None = None
) -> tuple[str, str]:
    key = _slug(item.get("scenario_key") or item.get("page_key"))
    title = str(item.get("title") or item.get("scenario_key") or key)
    pairs: list[tuple[str, str]] = []
    hubs = []
    for hub in item.get("hubs") or []:
        packed: dict[str, Any] = {
            "table": hub.get("table"),
            "role": hub.get("role") or "master",
        }
        if hub.get("note"):
            packed["note"] = hub["note"]
        hubs.append(packed)
        pairs.extend(_pairs_from_physicals([hub.get("table")]))
    shared = []
    for row in item.get("shared") or []:
        packed_shared: dict[str, Any] = {
            "table": row.get("table"),
            "role": row.get("role") or "",
        }
        if row.get("note"):
            packed_shared["note"] = row["note"]
        shared.append(packed_shared)
        pairs.extend(_pairs_from_physicals([row.get("table")]))
    for row in item.get("lifecycle") or []:
        if not isinstance(row, dict):
            continue
        if row.get("dict"):
            pairs.append(("dicts", _slug(row["dict"])))
        if row.get("process"):
            pairs.append(("processes", _slug(row["process"])))
    related = _related_tables(pairs, index)
    front = {
        "type": "scenario",
        "title": title.replace(":", "："),
        "page_key": key,
        "belong": "scenarios",
        "domain": item.get("domain") or "cust",
        "status": "draft",
        "aliases": _FlowList(list(item.get("aliases") or [])),
        "sources": _FlowList(_sources(item)),
        "created": today,
        "updated": today,
        "contract_version": "0.1",
    }
    if related:
        front["related"] = _FlowList(related)
    ground: dict[str, Any] = {"scenario": key, "hubs": hubs}
    if shared:
        ground["shared"] = shared
    if item.get("lifecycle"):
        ground["lifecycle"] = item["lifecycle"]
    blurb = str(item.get("description") or title)
    body = blurb + "\n\n```ground:scenario\n" + _dump(ground).rstrip() + "\n```\n"
    body = _with_page_links(body, pairs, index, self_belong="scenarios", self_key=key)
    return key, _page(front, title, body)


def render_pattern(
    item: dict[str, Any], today: str, index: dict[str, set[str]] | None = None
) -> tuple[str, str]:
    key = _slug(item.get("pattern_key") or item.get("page_key"))
    title = str(item.get("title") or item.get("pattern_key") or key)
    pairs = [("calibers", _slug(name)) for name in item.get("calibers") or []]
    front = {
        "type": "pattern",
        "title": title.replace(":", "："),
        "page_key": key,
        "belong": "patterns",
        "status": "draft",
        "sources": _FlowList(_sources(item)),
        "created": today,
        "updated": today,
        "contract_version": "0.1",
        "recall": False,
    }
    ground = {
        "pattern": title,
        "question": item.get("question"),
        "sql": item.get("sql"),
        "calibers": _FlowList(list(item.get("calibers") or [])),
        "trust": item.get("trust") or "proposed",
    }
    if item.get("evidence"):
        ground["evidence"] = item["evidence"]
    body = "```ground:pattern\n" + _dump(ground).rstrip() + "\n```\n"
    body = _with_page_links(body, pairs, index, self_belong="patterns", self_key=key)
    return key, _page(front, title, body)


def render_display_page(
    item: dict[str, Any], today: str, index: dict[str, set[str]] | None = None
) -> tuple[str, str]:
    key = _slug(item.get("page_key") or item.get("title") or "display")
    title = str(item.get("title") or key)
    front = {
        "type": "concept",
        "title": title.replace(":", "："),
        "page_key": key,
        "belong": "concepts",
        "domain": item.get("domain") or "display",
        "status": "draft",
        "recall": False,
        "sources": _FlowList(_sources(item, extra=[item.get("doc_source")])),
        "created": today,
        "updated": today,
        "contract_version": "0.1",
    }
    body = "## 版本演进\n\n" + str(item.get("content") or title) + "\n"
    body = _with_page_links(body, [], index, self_belong="concepts", self_key=key)
    return key, _page(front, title, body)


_AUDIT_COLUMNS = {
    "enable",
    "create_time",
    "update_time",
    "create_by",
    "update_by",
    "create_user",
    "update_user",
    "act_procinst_id",
    "act_procinst_no",
    "act_procinst_status",
    "act_procinst_date",
    "organization_id",
    "db_tenant_code",
    "app_tenant_code",
    "remark",
}
_TABLE_PREFIXES = (
    "cust_",
    "tenant_",
    "ca_fee_",
    "ca_",
    "funding_",
    "wechat_",
    "wec_",
    "platform_",
    "project_",
)
_TABLE_PROFILES: dict[str, tuple[str, str]] = {
    # ca (2)
    "ca_certification_info": (
        "企业CA证书认证记录",
        "企业cust_id, 批次号, 实名JSON",
    ),
    "ca_cfca_upgrade_report": (
        "CFCA证书升级上报",
        "企业ID/统码, 角色, 任务task_id, 异常内容",
    ),
    # ca_fee (4)
    "ca_fee_company": (
        "[核心主档] 企业CA服务费管理",
        "企业名称, 统码, 所属租户, 锁定年费标准, 缴费状态PAID/UNPAID, 服务起止日, 首次锁定项目ID",
    ),
    "ca_fee_order": (
        "[核心主档] CA服务费订单与支付",
        "订单号order_no, 企业ID/统码, 触发项目ID, 租户ID, 角色, 支付状态/金额/渠道",
    ),
    "ca_fee_project_config": (
        "项目级CA收费配置",
        "项目ID, 租户ID, 年费标准, 缴费渠道",
    ),
    "ca_fee_special_config": (
        "特殊企业年费白名单",
        "项目ID, 统码, 自定年费标准",
    ),
    # cust (31)
    "cust_access_secret": (
        "OpenAPI接入秘钥",
        "应用channel, 凭证公私钥",
    ),
    "cust_account_info": (
        "[核心主档] 客户银行账号",
        "账号, 户名, 开户行/联行号, 省市代码, 默认标识, 账户状态",
    ),
    "cust_app_channel_config": (
        "应用与渠道映射配置",
        "app_id, app_tenant_code(渠道码), enable",
    ),
    "cust_auth_application": (
        "客户产品开通记录",
        "产品编码, 开通状态, 管理员",
    ),
    "cust_auth_application_config": (
        "客户产品开通个性配置",
        "企业cust_id, 签署方式",
    ),
    "cust_build_record": (
        "建档同步中台日志",
        "企业ID, 中台企业ID, 状态",
    ),
    "cust_certification_info": (
        "企业认证核验记录",
        "企业code, 认证类型, 核验状态",
    ),
    "cust_change_cfg": (
        "企业变更项配置",
        "变更项item_code, 材料说明",
    ),
    "cust_change_record": (
        "企业信息变更轨迹",
        "企业ID/名称, 变更类型, 流程号",
    ),
    "cust_company_info": (
        "[核心主档大宽表] 客户企业信息主表",
        "企业code, 统码certification_no, 名称/曾用名, 法人, 认证方式identify_style, 录入方式cust_build_type, 客户/认证状态, 建档时间create_time, 省市地址, 开户账号",
    ),
    "cust_company_lifecycle_info": (
        "企业冻结/解冻留痕",
        "企业ID/code, 冻结原因及附件",
    ),
    "cust_company_survey_state": (
        "问卷星活动访问状态",
        "企业ID, 首访用户/时间, 抽奖状态",
    ),
    "cust_company_survey_whitelist": (
        "问卷调研企业白名单",
        "企业ID, 企业名称",
    ),
    "cust_config_mapping": (
        "内外编码映射字典",
        "内部编码, 外部编码, 渠道",
    ),
    "cust_customized_product": (
        "快捷入口导航配置",
        "企业cust_id, 产品名, url",
    ),
    "cust_group_rel": (
        "集团成员企业层级树",
        "成员企业ID, 父/根企业ID, level, 状态",
    ),
    "cust_head_company_info": (
        "总公司主档执照",
        "统码, 全称/简称, 法人, 注册地址",
    ),
    "cust_interworking_product": (
        "跨租户产品授权",
        "企业cust_id, 租户ID, 产品编码, 状态",
    ),
    "cust_invite_info": (
        "企业建档邀请记录",
        "客户ID, 联系人/手机, 渠道码, 进度",
    ),
    "cust_message_send_policy": (
        "消息推送开关配置",
        "场景码scenes_type, 消息类型, 开关",
    ),
    "cust_oper_change_record": (
        "运营对接人变更记录",
        "企业ID, 变更前后运营人员, 原因",
    ),
    "cust_person_info": (
        "[核心主档] 客户联系人与经办人档案",
        "姓名, 手机/邮箱, 证件类型/号码, 建档经办人, 关联用户ID, 实名状态",
    ),
    "cust_project_code_record": (
        "项目邀请码输入记录",
        "企业ID, 用户ID, 渠道码, 验证状态",
    ),
    "cust_project_pushcust": (
        "SSO跳转默认项目映射",
        "来源/目标SSO渠道, 默认项目ID",
    ),
    "cust_project_rel": (
        "[核心关联大宽表] 客户项目关联表",
        "企业code, 项目ID, 产品ID, 租户code, 渠道码channel_code, 角色(核心/供应商), 关联状态status, 配置模式config_model, 展示标记",
    ),
    "cust_role_info": (
        "企业产品角色关联",
        "企业code, 产品角色, 状态",
    ),
    "cust_setting_config": (
        "认证规则与协议配置",
        "变更审核开关, 协议文本, 授权书模式",
    ),
    "cust_sftp": (
        "客户SFTP对账连接信息",
        "host, 用户名, 渠道",
    ),
    "cust_shareholder_info": (
        "客户股东出资信息",
        "企业code, 股东名, 证件号, 出资额",
    ),
    "cust_survey_answer": (
        "问卷调研答卷明细",
        "问卷编码, 企业ID, 题号, 选项内容",
    ),
    "cust_user_rel": (
        "用户与企业角色归属",
        "用户ID, 企业ID, 客户角色",
    ),
    # funding (4)
    "funding_exception_resolution": (
        "资方报错解析建议",
        "资方标识, 产品code, 报错关键字, 建议",
    ),
    "funding_rule_detail": (
        "资方准入规则明细",
        "规则头ID rule_info_id, 资方标识, 规则键值",
    ),
    "funding_rule_front_cfg": (
        "资方规则前端元数据",
        "产品code, 规则层, 前端字段key",
    ),
    "funding_rule_info": (
        "[核心主档] 资方准入规则头",
        "资方标识funding_party_mark, 资方名称, 产品编码product_code, 规则状态ACTIVE/INACTIVE/PENDING, 版本号",
    ),
    # platform (3)
    "platform_product": (
        "[核心主档] 平台产品基础配置",
        "平台编码, 产品编码product_code, 产品名称, 默认菜单, 多项目/多角色支持",
    ),
    "platform_product_client": (
        "平台产品客户端配置",
        "产品ID, 客户端类型, 跳转url, 状态",
    ),
    "platform_product_cust_role": (
        "平台产品企业角色字典",
        "产品编码product_code, 企业角色编码",
    ),
    # project (1)
    "project_file_info": (
        "项目运营文档管理",
        "项目ID, 标题, 模块类型",
    ),
    # tenant (18)
    "tenant_interworking_product": (
        "租户互通产品授权与额度",
        "租户ID, 产品ID, 状态, 融资额度/期限上限",
    ),
    "tenant_interworking_project": (
        "租户互通产品项目绑定",
        "租户ID, 产品ID, 项目ID",
    ),
    "tenant_migarory_log": (
        "租户项目迁移流水",
        "产品编码, 批次号, 状态, 请求报文",
    ),
    "tenant_migarory_log_bak": (
        "租户迁移日志备份",
        "产品编码, 批次号, 状态",
    ),
    "tenant_product": (
        "[核心主档] 租户引入产品配置",
        "租户ID, 平台产品ID, 产品名称/类型, 目标客群, 融资额度/期限上限, 增信措施",
    ),
    "tenant_product_menu": (
        "租户产品功能菜单",
        "产品code, 角色, 菜单ID",
    ),
    "tenant_product_menu_res": (
        "租户产品菜单按钮权限",
        "产品code, 菜单ID, 按钮资源ID",
    ),
    "tenant_project": (
        "[核心主档大宽表] 租户项目全量运营配置",
        "项目ID/编码, 名称, 渠道码channel_code, 平台产品编码, 项目状态, 企微审批号wechat_audit_no, 立项审批通过时间, 运营/查验/风控对接人A/B及组别, 方案/业务经理, 首笔落地时间, 自定义字段一/二/三",
    ),
    "tenant_project_approval": (
        "[核心主档] 租户项目审批主单",
        "审批号approval_no, 关联项目code, 审批类型, 工作流状态, 方案经理, 企微号sp_no, 简易/低风险",
    ),
    "tenant_project_approval_business_info": (
        "审批项目业务推送详情",
        "产品编码, 来源系统, 配置版本, 费率规则",
    ),
    "tenant_project_approval_flow": (
        "项目审批流程节点实例",
        "关联审批单, 节点编码/名称/顺序, 节点状态, 审批人",
    ),
    "tenant_project_approval_flow_comment": (
        "项目审批评论抄送",
        "关联审批单, 备注内容, 抄送人",
    ),
    "tenant_project_approval_flow_config": (
        "项目审批流程模板配置",
        "流程编码flow_code, 节点编码/名称, 顺序",
    ),
    "tenant_project_approval_flow_credit": (
        "[核心主档] 项目审批授信额度明细",
        "核心企业/资方ID及名称, 授信额度, 集团额度标识, 额度起止日, 循环标识",
    ),
    "tenant_project_approval_flow_file": (
        "项目审批影像附件",
        "业务key, 影像分类, 文件名/ID/url, 审批节点",
    ),
    "tenant_project_approval_flow_node": (
        "项目审批节点操作记录",
        "关联审批单, 节点编码, 操作/审批类型, 操作人",
    ),
    "tenant_setting_config": (
        "[核心配置大宽表] 贴牌租户主配置",
        "租户code/名称, 平台名, 统码, 接入模式access_mode(STANDARD/DIRECT_INIT), 客服电话, 小程序/公众号, 默认项目, 协议签署配置, 业务开关",
    ),
    "tenant_setting_config_share": (
        "[核心配置大宽表] 共享租户配置",
        "租户名称, 平台名, 统码, 客服信息/二维码, 小程序/公众号, 域名/展示配置",
    ),
    # wec (2)
    "wec_project_cust_operation_rel": (
        "微企链企业运营对接",
        "关联ID, 企业ID, 角色, 运营对接人A/B。历史关系",
    ),
    "wec_project_operation_rel": (
        "微企链历史关联运营配置",
        "历史项目ID, 运营/查验/风控对接人。新配置已收敛至tenant_project",
    ),
    # wechat (2)
    "wechat_project_approval_apply": (
        "[核心主档大宽表] 企微立项审批流申请",
        "企微审批号sp_no, 立项名称, 主项目/上线名, 资方全称/分支行, 核心企业全称, 产品类型, 审批时间/类型",
    ),
    "wechat_project_approval_field_history": (
        "企微立项字段变更历史",
        "立项apply_id, 审批号sp_no, 字段名/标签, 变更前后值",
    ),
    # other (11)
    "argeement_migratory_record": (
        "协议电子化迁移记录",
        "客户ID, 产品编码, 协议名/编号, 状态",
    ),
    "async_io_task": (
        "异步任务处理日志",
        "任务号task_no, 任务名称/类型, 发起人, 状态",
    ),
    "authorization_agreement": (
        "管理员授权确认书签署表",
        "企业ID/名称, 管理员ID/姓名, 授权状态",
    ),
    "client_api_sync_error": (
        "API调用失败重试队列表",
        "服务类名, 重试次数",
    ),
    "gpt_learn_poster_log": (
        "审核卡片引流埋点日志",
        "",
    ),
    "lc_sql_init_log": (
        "底层插件SQL初始化记录",
        "",
    ),
    "migratory_user_record": (
        "账号体系迁移记录",
        "用户ID user_id, 登录状态is_login",
    ),
    "open_sso_channel": (
        "开放登录SSO渠道配置",
        "渠道码channel_code, tenant_code/db_tenant_code产融租户标识, appId, channel_kind LOCAL_SYS/STANDARD, SSO clientId/secret",
    ),
    "operation_user": (
        "运营人员基础信息",
        "姓名, 运营中台ID operation_id, 组别, 状态",
    ),
    "org_manage": (
        "组织机构行政层级树",
        "机构编码code, 机构名称, 机构号org_no, 状态",
    ),
    "short_link": (
        "外链短链生成与重定向",
        "短链编号, 源长链source_url, 永久有效标识",
    ),
}


def render_catalog_summary(model: dict[str, Any], today: str) -> str:
    catalog = model.get("_catalog") or {}
    tables_in = catalog.get("tables") or {}
    if not tables_in:
        return ""
    compiled_tables = model.get("tables") or {}
    groups: dict[str, list[str]] = {}
    for tname in tables_in:
        groups.setdefault(_table_prefix(str(tname)), []).append(str(tname))
    database = str(catalog.get("database") or model.get("database") or "")
    lines = [
        "全库表骨架。每表一行：- 表名: 业务定位(核心列/主键/状态)。大宽表与主档保留较全业务维度，小表/关联表/日志表极致精炼。",
        "",
    ]
    for prefix in sorted(groups, key=lambda name: (name == "other", name)):
        names = sorted(groups[prefix])
        lines.append(f"## {prefix}（{len(names)}）")
        lines.append("")
        for tname in names:
            tmeta = tables_in.get(tname) or {}
            compiled = compiled_tables.get(tname) or {}
            lines.append(_catalog_table_line(str(tname), compiled, tmeta))
        lines.append("")
    front = {
        "type": "concept",
        "title": "全库表骨架",
        "page_key": "catalog_summary",
        "belong": "concepts",
        "status": "draft",
        "recall": False,
        "aliases": _FlowList(["Catalog Summary", "表目录", "库表一览"]),
        "sources": _FlowList(
            [f"database_schema:{database}"] if database else ["database_schema:catalog"]
        ),
        "created": today,
        "updated": today,
        "contract_version": "0.1",
    }
    return _page(front, "全库表骨架", "\n".join(lines).rstrip() + "\n")


def _table_prefix(name: str) -> str:
    for prefix in _TABLE_PREFIXES:
        if name.startswith(prefix):
            return prefix.rstrip("_")
    return "other"


def _catalog_table_line(
    tname: str, compiled: dict[str, Any], catalog_table: dict[str, Any]
) -> str:
    profile = _TABLE_PROFILES.get(tname)
    if profile:
        title, desc = profile
        if desc:
            return f"- {tname}: {title}({desc})"
        return f"- {tname}: {title}"
    keys = _catalog_keys(compiled, catalog_table)
    core = _catalog_core(compiled, catalog_table, set(keys.split("/")) if keys else set())
    comment = str((catalog_table.get("comment") or "")).strip() or tname
    bits = [p for p in (keys, core) if p]
    if bits:
        return f"- {tname}: {comment}({', '.join(bits)})"
    return f"- {tname}: {comment}"


_CJK_PHRASE_RE = re.compile(r"[\u4e00-\u9fff]{3,}")
# Only field-like blurbs (UI often invents these); skip generic nouns.
_FIELD_LIKE_SUFFIXES = (
    "时间",
    "日期",
    "金额",
    "费率",
    "号码",
    "编号",
    "额度",
    "期限",
)


def iter_ungrounded_profile_phrases(
    catalog: dict[str, Any],
) -> list[tuple[str, str]]:
    """Return (table, phrase) when a field-like profile blurb is not grounded."""
    tables = catalog.get("tables") or {}
    if not isinstance(tables, dict):
        return []
    bad: list[tuple[str, str]] = []
    for tname, profile in _TABLE_PROFILES.items():
        tmeta = tables.get(tname)
        if not isinstance(tmeta, dict):
            continue
        _title, desc = profile
        if not desc:
            continue
        columns = tmeta.get("columns") or {}
        if not isinstance(columns, dict):
            columns = {}
        comments = [
            str((meta or {}).get("comment") or "").strip()
            for meta in columns.values()
        ]
        col_names = {str(n) for n in columns}
        table_comment = str(tmeta.get("comment") or "").strip()
        grounds = [c for c in comments if c] + ([table_comment] if table_comment else [])
        grounds.extend(col_names)
        for phrase in _CJK_PHRASE_RE.findall(str(desc)):
            if not any(phrase.endswith(suf) for suf in _FIELD_LIKE_SUFFIXES):
                continue
            if _phrase_grounded(phrase, grounds):
                continue
            bad.append((str(tname), phrase))
    return bad


def _phrase_grounded(phrase: str, grounds: list[str]) -> bool:
    for ground in grounds:
        if not ground:
            continue
        if phrase in ground or ground in phrase:
            return True
        if len(phrase) >= 4 and SequenceMatcher(None, phrase, ground).ratio() >= 0.55:
            return True
    return False


def _catalog_keys(compiled: dict[str, Any], catalog_table: dict[str, Any]) -> str:
    columns = catalog_table.get("columns") or {}
    if not isinstance(columns, dict):
        columns = {}
    pk = [
        str(x)
        for x in (compiled.get("primary_key") or catalog_table.get("primary_key") or [])
        if x
    ]
    if not pk:
        pk = [name for name, meta in columns.items() if str((meta or {}).get("key") or "") == "PRI"]
    keys: list[str] = []
    for name in pk:
        if name in columns and name not in keys:
            keys.append(name)
    anchors = [str(x) for x in (compiled.get("name_anchors") or []) if x]
    for name in anchors:
        if name in {"code", "certification_no"} and name in columns and name not in keys:
            keys.append(name)
            break
    if "code" in columns and "code" not in keys and len(keys) < 2:
        keys.append("code")
    return "/".join(keys[:2])


def _catalog_core(
    compiled: dict[str, Any],
    catalog_table: dict[str, Any],
    skip: set[str],
) -> str:
    columns = catalog_table.get("columns") or {}
    if not isinstance(columns, dict):
        columns = {}
    ordered: list[str] = []
    seen: set[str] = set(skip)

    def add(name: str) -> None:
        if name and name not in seen and name in columns and not _is_catalog_noise(name):
            ordered.append(name)
            seen.add(name)

    for name in compiled.get("name_anchors") or []:
        add(str(name))
    for field in compiled.get("fields") or []:
        if isinstance(field, dict) and field_dict_page_key(field, str(compiled.get("table") or "")):
            add(str(field.get("name") or ""))
    for name, meta in columns.items():
        comment = str((meta or {}).get("comment") or "").strip()
        if comment:
            add(str(name))
    for name in columns:
        add(str(name))

    buckets: dict[str, list[str]] = {}
    leftover: list[str] = []
    for name in ordered:
        family = _catalog_family(name)
        if family:
            buckets.setdefault(family, []).append(name)
        else:
            leftover.append(name)

    tokens: list[str] = []
    hints = [name for name in leftover if name in _HINT_COLUMNS]
    for name in hints:
        if len(tokens) >= 2:
            break
        tokens.append(name)
    for family in _FAMILY_PRIORITY:
        if len(tokens) >= _CATALOG_CORE_LIMIT:
            break
        members = buckets.get(family) or []
        if len(members) >= 2:
            tokens.append(f"{family}×{len(members)}")
        elif len(members) == 1:
            tokens.append(members[0])
    if len(tokens) < 4:
        for name in leftover:
            if name in tokens:
                continue
            tokens.append(name)
            if len(tokens) >= min(4, _CATALOG_CORE_LIMIT):
                break
    return " ".join(tokens[:_CATALOG_CORE_LIMIT])


def _catalog_family(name: str) -> str:
    if name.startswith("ref_") or (name.endswith("_id") and name not in {"id"}):
        return "关联"
    if any(name.endswith(suf) for suf in _GEO_SUFFIXES):
        return "区划"
    if any(name.endswith(suf) for suf in _AMOUNT_SUFFIXES):
        return "金额"
    if name in _STATUS_NAMES or any(name.endswith(suf) for suf in _STATUS_SUFFIXES):
        return "状态/类型"
    if name.endswith("_name") or name in {"name", "title"}:
        return "名称"
    return ""


def _is_catalog_noise(name: str) -> bool:
    if name in _AUDIT_COLUMNS or name in _BLOB_COLUMNS:
        return True
    return any(name.endswith(suf) for suf in _BLOB_SUFFIXES)


def _clip_chars(text: str, limit: int) -> str:
    compact = " ".join(text.split())
    if len(compact) <= limit:
        return compact
    return compact[:limit]


def _write_list(
    directory: Path,
    items: list[dict[str, Any]],
    renderer: Any,
    today: str,
    index: dict[str, set[str]] | None = None,
) -> int:
    count = 0
    for item in items:
        key, text = renderer(item, today, index=index)
        (directory / f"{key}.md").write_text(text, encoding="utf-8")
        count += 1
    return count


_BELONG_ORDER = (
    "tables",
    "dicts",
    "processes",
    "calibers",
    "metrics",
    "rules",
    "scenarios",
    "patterns",
    "concepts",
)


def _wiki_index(model: dict[str, Any]) -> dict[str, set[str]]:
    index: dict[str, set[str]] = {name: set() for name in _BELONG_ORDER}
    index["tables"] = {str(name) for name in (model.get("tables") or {})}
    catalog = model.get("_catalog") or {}
    index["tables"].update(str(name) for name in (catalog.get("tables") or {}))
    index["dicts"] = {str(name) for name in (model.get("dicts") or {})}
    for item in model.get("concepts") or []:
        index["concepts"].add(
            _slug(item.get("concept_key") or item.get("page_key") or item.get("title"))
        )
    for item in model.get("display") or []:
        index["concepts"].add(_slug(item.get("page_key") or item.get("title")))
    index["concepts"].add("catalog_summary")
    for item in model.get("processes") or []:
        index["processes"].add(_slug(item.get("process_key") or item.get("page_key")))
    for item in model.get("calibers") or []:
        index["calibers"].add(_slug(item.get("caliber_key") or item.get("page_key")))
    for item in model.get("metrics") or []:
        index["metrics"].add(_slug(item.get("metric_key") or item.get("page_key")))
    for item in model.get("rules") or []:
        index["rules"].add(_slug(item.get("rule_key") or item.get("page_key")))
    for item in model.get("scenarios") or []:
        index["scenarios"].add(_slug(item.get("scenario_key") or item.get("page_key")))
    for item in model.get("patterns") or []:
        index["patterns"].add(_slug(item.get("pattern_key") or item.get("page_key")))
    return index


def _pairs_from_physicals(values: Any) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    if isinstance(values, (list, tuple, set)):
        raws = list(values)
    else:
        raws = [values]
    for raw in raws:
        text = str(raw or "").strip()
        if not text:
            continue
        token = text.split()[0].strip("`'\"(),")
        if not token:
            continue
        left, dot, right = token.partition(".")
        if not left:
            continue
        pairs.append(("tables", left))
        pairs.append(("dicts", left))
        pairs.append(("processes", left))
        if "__" in left:
            pairs.append(("tables", left.split("__", 1)[0]))
        if dot:
            col = right.split("=")[0].strip().strip("'\"")
            if col and col.replace("_", "").isalnum():
                dkey = dict_page_key(left, col)
                pairs.append(("dicts", dkey))
                pairs.append(("processes", dkey))
        elif "__" in token:
            pairs.append(("dicts", token))
            pairs.append(("processes", token))
            pairs.append(("tables", token.split("__", 1)[0]))
        else:
            pairs.append(("tables", token))
    return pairs


def _pairs_from_relations(using: Any) -> list[tuple[str, str]]:
    values: list[Any] = []
    for row in using or []:
        if isinstance(row, dict):
            values.append(row.get("left"))
            values.append(row.get("right"))
        else:
            values.append(row)
    return _pairs_from_physicals(values)


def _related_tables(
    pairs: list[tuple[str, str]], index: dict[str, set[str]] | None
) -> list[str]:
    seen: list[str] = []
    known = None if index is None else (index.get("tables") or set())
    for belong, key in pairs:
        if belong != "tables" or not key:
            continue
        if known is not None and key not in known:
            continue
        if key not in seen:
            seen.append(key)
    return seen


def _page_link_section(
    pairs: list[tuple[str, str]],
    index: dict[str, set[str]] | None,
    *,
    self_belong: str = "",
    self_key: str = "",
) -> str:
    seen: set[tuple[str, str]] = set()
    kept: list[tuple[str, str]] = []
    rank = {name: i for i, name in enumerate(_BELONG_ORDER)}
    for belong, key in pairs:
        belong = str(belong or "").strip()
        key = _slug(key)
        if not belong or not key:
            continue
        if belong == self_belong and key == self_key:
            continue
        if index is not None and key not in (index.get(belong) or set()):
            continue
        ident = (belong, key)
        if ident in seen:
            continue
        seen.add(ident)
        kept.append(ident)
    kept.sort(key=lambda item: (rank.get(item[0], 99), item[1]))
    if not kept and index is not None and not (
        self_belong == "concepts" and self_key == "catalog_summary"
    ):
        if "catalog_summary" in (index.get("concepts") or set()):
            kept.append(("concepts", "catalog_summary"))
    if not kept:
        return ""
    lines = ["## 页面链接", ""]
    for belong, key in kept:
        lines.append(f"- [[{belong}/{key}]]")
    return "\n".join(lines) + "\n"


def _with_page_links(
    body: str,
    pairs: list[tuple[str, str]],
    index: dict[str, set[str]] | None,
    *,
    self_belong: str = "",
    self_key: str = "",
) -> str:
    section = _page_link_section(
        pairs, index, self_belong=self_belong, self_key=self_key
    )
    if not section:
        return body
    return body.rstrip() + "\n\n" + section


def _page(front: dict[str, Any], title: str, body: str) -> str:
    cleaned = {k: v for k, v in front.items() if v not in (None, "", [], {})}
    return (
        "---\n"
        + _dump(cleaned).rstrip()
        + "\n---\n\n"
        + f"# {title}\n\n"
        + body.rstrip()
        + "\n"
    )


def _sources(item: dict[str, Any], extra: list[Any] | None = None) -> list[str]:
    out: list[str] = []
    for raw in [item.get("evidence"), item.get("doc_source"), *(extra or [])]:
        text = str(raw or "").strip()
        if text and text not in out:
            if not text.startswith(("code_path:", "database_", "document_claim:")):
                text = f"document_claim:{text}" if "/" in text or text.endswith(".md") else text
            out.append(text)
    for stage in item.get("stages") or []:
        for trans in stage.get("transitions") or []:
            ev = str(trans.get("evidence") or "").strip()
            if ev and ev not in out:
                out.append(ev)
    if not out:
        out.append("code_path:l1_intermediate")
    return out


def _process_evidence(item: dict[str, Any]) -> list[str]:
    out: list[str] = []
    for stage in item.get("stages") or []:
        if stage.get("evidence"):
            out.append(str(stage["evidence"]))
        for trans in stage.get("transitions") or []:
            if trans.get("evidence"):
                out.append(str(trans["evidence"]))
    return out


def _slug(value: Any) -> str:
    text = str(value or "").strip()
    return text.replace(" ", "_").replace("/", "_") or "untitled"


def _dict_item(item: dict[str, Any], key: str) -> dict[str, Any]:
    packed = dict(item)
    packed.setdefault("dict", key)
    table = str(packed.get("table") or "")
    column = str(packed.get("column") or "")
    if table and column:
        packed.setdefault("fields", [f"{table}.{column}"])
        packed["dict"] = packed.get("dict") or dict_page_key(table, column, key)
    return packed


def hydrate_dict_labels_from_dir(model: dict[str, Any], dicts_dir: Path) -> int:
    """Fill empty in-memory dict labels from an existing out/dicts tree.

    Prior L1 runs may have kept richer labels on disk while a fresh L0 reload
    only has codes. Hydrate before table/dict rewrite so both stay aligned.
    IR ``dict_labels`` (already applied) win over disk when both set a label.
    """
    if not dicts_dir.is_dir():
        return 0
    dicts = model.setdefault("dicts", {})
    filled = 0
    for path in sorted(dicts_dir.glob("*.md")):
        try:
            item = dict_from_page(parse_page(path.read_text(encoding="utf-8")))
        except Exception:
            continue
        key = str(item.get("dict") or path.stem)
        if not key:
            continue
        target = dicts.get(key)
        if target is None:
            dicts[key] = item
            filled += 1
            continue
        tvals = target.setdefault("values", {})
        if not isinstance(tvals, dict):
            continue
        for code, meta in (item.get("values") or {}).items():
            if not isinstance(meta, dict):
                continue
            lab = str(meta.get("label") or "").strip()
            if not lab:
                continue
            row = tvals.get(code)
            if not isinstance(row, dict):
                row = {"trust": str(meta.get("trust") or "proposed")}
                tvals[str(code)] = row
            if str(row.get("label") or "").strip():
                continue
            row["label"] = lab
            if meta.get("evidence") and not row.get("evidence"):
                row["evidence"] = meta.get("evidence")
            filled += 1
    return filled


def _copy_untouched(l0_dir: Path, out: Path) -> None:
    for folder in ("tables", "dicts"):
        src = l0_dir / folder
        dest = out / folder
        if not src.exists():
            continue
        dest.mkdir(parents=True, exist_ok=True)
        for path in src.glob("*.md"):
            target = dest / path.name
            if not target.exists():
                shutil.copy2(path, target)
    for name in ("instance_index.yaml",):
        src = l0_dir / name
        if src.exists() and not (out / name).exists():
            shutil.copy2(src, out / name)


def _copy_instance_index(l0_dir: Path | None, out: Path) -> None:
    if l0_dir is None:
        return
    src = l0_dir / "instance_index.yaml"
    if src.exists():
        shutil.copy2(src, out / "instance_index.yaml")


def _write_reviews(path: Path, reviews: list[dict[str, Any]], today: str) -> None:
    path.write_text(
        _dump({"generated_at": today, "items": reviews}),
        encoding="utf-8",
    )


def _index_markdown(model: dict[str, Any], counts: dict[str, int], today: str) -> str:
    lines = [
        f"# L1 index ({today})",
        "",
        f"- database: `{model.get('database') or ''}`",
        f"- domains: {', '.join(model.get('domains') or []) or '(none)'}",
        f"- intermediate files: {len(model.get('l1_files') or [])}",
        f"- tables: {counts.get('tables', 0)}",
        f"- dicts: {counts.get('dicts', 0)}",
        f"- concepts: {counts.get('concepts', 0)}",
        f"- processes: {counts.get('processes', 0)}",
        f"- calibers: {counts.get('calibers', 0)}",
        f"- metrics: {counts.get('metrics', 0)}",
        f"- rules: {counts.get('rules', 0)}",
        f"- scenarios: {counts.get('scenarios', 0)}",
        f"- patterns: {counts.get('patterns', 0)}",
        "",
        "## catalog",
        "",
        "- [[concepts/catalog_summary]]",
        "",
        "## tables",
        "",
    ]
    for name in sorted((model.get("tables") or {}).keys()):
        lines.append(f"- [[tables/{name}]]")
    for belong in _SEMANTIC_DIRS:
        lines.extend(["", f"## {belong}", ""])
        directory_keys = {
            "concepts": "concept_key",
            "processes": "process_key",
            "calibers": "caliber_key",
            "metrics": "metric_key",
            "rules": "rule_key",
            "scenarios": "scenario_key",
            "patterns": "pattern_key",
        }
        key_name = directory_keys[belong]
        for item in model.get(belong) or []:
            slug = _slug(item.get(key_name) or item.get("page_key"))
            lines.append(f"- [[{belong}/{slug}]]")
    lines.append("")
    return "\n".join(lines)


def _log_markdown(model: dict[str, Any], counts: dict[str, int], today: str) -> str:
    return (
        f"# L1 log ({today})\n\n"
        f"intermediate files: {len(model.get('l1_files') or [])}\n\n"
        + "\n".join(f"- {k}: {v}" for k, v in counts.items())
        + "\n"
    )
