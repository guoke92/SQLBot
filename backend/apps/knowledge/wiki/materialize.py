"""Single wiki body writer: replay claim patches onto an import baseline.

Import, page chat, pasted text, and conversation sediment all call this.
Nothing else assigns ``wiki_page.body_md``.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from datetime import date
from typing import Any

import yaml

from apps.knowledge.wiki.contract import (
    BELONG_TO_TYPE,
    PAGE_STATUSES,
    PAGE_TYPES,
    Finding,
    PageContractError,
    _slug_valid,
    lint_page,
    parse_page,
)

PATCH_OPS = frozenset(
    {
        "upsert_claim",
        "dispute_claim",
        "add_alias",
        "open_review",
        "create_page",
        "replace_base",
        "promote",
    }
)
MAINTAIN_ORIGINS = frozenset({"maintain", "conversation", "document"})
OVERLAY_STATUSES = frozenset({"applied", "conflicted"})
_NOTES_HEADING = "## 维护说明"
_FENCE_OPEN = re.compile(r"^```ground:(?P<kind>[a-z-]+)\s*$")
_FENCE_CLOSE = re.compile(r"^```\s*$")
_BUSINESS_BELONGS = frozenset(
    {"concepts", "processes", "calibers", "metrics", "rules", "patterns", "scenarios"}
)
_TABLE_LOCKED = frozenset({"primary_key", "grain", "name_anchors", "default_filter"})
_CONCEPT_FIELDS = frozenset(
    {"maps_to", "field_targets", "also_confused_with", "adjudication"}
)
_EXCLUSIVE_FIELDS: dict[str, frozenset[str]] = {
    "caliber": frozenset(
        {
            "caliber",
            "field_targets",
            "predicate",
            "scope",
            "boundary",
            "using_relations",
        }
    ),
    "metric": frozenset(
        {
            "metric",
            "caliber",
            "grain_table",
            "aggregation",
            "field",
            "using_relations",
        }
    ),
    "rule": frozenset({"rule", "field_targets", "impact", "content"}),
    "pattern": frozenset({"pattern", "question", "sql", "calibers"}),
    "scenario": frozenset({"scenario", "hubs", "shared", "lifecycle"}),
}


@dataclass
class PatchOutcome:
    status: str
    review_title: str = ""
    review_body: str = ""


@dataclass
class MaterializeResult:
    body: str
    outcomes: list[PatchOutcome] = field(default_factory=list)


def content_sha(body: str) -> str:
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def cap_trust(origin: str, requested: str) -> str:
    """Conversation, documents, and the maintain loop cannot mint confirmed."""
    if origin in MAINTAIN_ORIGINS or origin == "maintain":
        return "proposed"
    if requested in {"confirmed", "proposed", "disputed", "rejected"}:
        return requested
    return "proposed"


def materialize_markdown(
    base_body: str, patches: list[dict[str, Any]]
) -> MaterializeResult:
    """Replay overlay patches onto ``base_body``. ``replace_base`` is a no-op.

    ``proposed`` and ``rejected`` rows stay in the log and do not change the body.
    """
    body = str(base_body or "")
    outcomes: list[PatchOutcome] = []
    for patch in patches:
        op = str(patch.get("op") or "")
        origin = str(patch.get("origin") or "maintain")
        status = str(patch.get("status") or "applied")
        if status in {"proposed", "rejected"}:
            outcomes.append(PatchOutcome(status=status))
            continue
        if op == "replace_base" or origin == "import":
            outcomes.append(PatchOutcome(status="applied"))
            continue
        if status == "conflicted" and op != "open_review":
            body, outcome = _ensure_recorded_review(body, patch)
            outcomes.append(outcome)
            continue
        body, outcome = _apply_one(body, patch)
        outcomes.append(outcome)
    return MaterializeResult(
        body=body.strip() + ("\n" if body.strip() else ""), outcomes=outcomes
    )


def force_frontmatter_status(body: str, status: str) -> str:
    meta, prose = _split_frontmatter(body)
    meta["status"] = status
    return _dump(meta, prose)


def compose_import_body(
    file_body: str,
    overlays: list[dict[str, Any]],
    *,
    existing_status: str | None,
) -> tuple[str, str]:
    """Replay maintenance onto a new file baseline.

    Pages that already carry overlay patches keep their stored status.
    Pages with only import history take the status written in the file.
    """
    result = materialize_markdown(file_body, overlays)
    body = result.body
    if existing_status and overlays:
        return force_frontmatter_status(body, existing_status), existing_status
    try:
        parsed = parse_page(body)
    except PageContractError:
        return body, existing_status or "draft"
    status = parsed.status if parsed.status in PAGE_STATUSES else "draft"
    return body, status


_PROMOTE_BLOCKING = frozenset(
    {
        "DUPLICATE_GROUND_BLOCK",
        "GROUND_IN_DISPLAY",
        "CLAIM_PATH_INVALID",
        "INGEST_WROTE_PUBLISHED",
        "PATTERN_UNEVIDENCED_CONFIRMED",
        "GROUND_PARSE_FAILED",
    }
)


def promotion_blockers(
    body: str,
    *,
    siblings: list[dict[str, str]] | None = None,
) -> list[Finding]:
    """Structural lint plus the published closure for table and dict links."""
    page = parse_page(body)
    known = {page.page_key, f"{page.belong}/{page.page_key}"}
    for item in siblings or []:
        belong = str(item.get("belong") or "")
        page_key = str(item.get("page_key") or "")
        if page_key:
            known.add(page_key)
        if belong and page_key:
            known.add(f"{belong}/{page_key}")
    findings = [
        item
        for item in lint_page(page, known_keys=known)
        if item.code in _PROMOTE_BLOCKING
    ]
    for link in page.links:
        resolved = _physical_link(link.target, siblings or [])
        if resolved is None:
            continue
        belong, page_key = resolved
        match = next(
            (
                item
                for item in siblings or []
                if item.get("belong") == belong and item.get("page_key") == page_key
            ),
            None,
        )
        if match is None or match.get("status") != "published":
            findings.append(
                Finding(
                    "CLOSURE_UNPUBLISHED",
                    f"[[{link.target}]] 指向的{belong}页尚未发布",
                )
            )
    return findings


def _physical_link(
    target: str, siblings: list[dict[str, str]]
) -> tuple[str, str] | None:
    text = target.strip().strip("/")
    if "/" in text:
        belong, _, page_key = text.partition("/")
        belong = {"table": "tables", "dict": "dicts"}.get(belong, belong)
        if belong in {"tables", "dicts"} and page_key:
            return belong, page_key
        return None
    hits = [
        item
        for item in siblings
        if item.get("page_key") == text and item.get("belong") in {"tables", "dicts"}
    ]
    if len(hits) == 1:
        return str(hits[0]["belong"]), str(hits[0]["page_key"])
    return None


def blank_page(
    *,
    belong: str,
    page_key: str,
    title: str,
    source_ref: str,
) -> str:
    page_type = BELONG_TO_TYPE.get(belong, "")
    meta = {
        "type": page_type,
        "title": title,
        "page_key": page_key,
        "belong": belong,
        "status": "draft",
        "sources": [source_ref] if source_ref else [],
        "contract_version": "0.1",
        "created": date.today().isoformat(),
        "updated": date.today().isoformat(),
    }
    return _dump(meta, f"# {title}\n")


def _apply_one(body: str, patch: dict[str, Any]) -> tuple[str, PatchOutcome]:
    op = str(patch.get("op") or "")
    payload = patch.get("payload") if isinstance(patch.get("payload"), dict) else {}
    origin = str(patch.get("origin") or "maintain")
    source_ref = str(patch.get("source_ref") or "").strip()
    local = _local_path(str(patch.get("claim_path") or ""))
    if op not in PATCH_OPS:
        return _conflict(body, patch, "未知补丁", f"不认识的操作 {op}")
    if op == "create_page":
        return _create_page(body, payload, source_ref)
    if op == "promote":
        return _promote_status(body, payload, patch)
    if not body.strip():
        return _conflict(body, patch, "页面不存在", "没有基线页，不能改主张")
    try:
        meta, prose = _split_frontmatter(body)
    except ValueError as exc:
        return _conflict(body, patch, "页面无法解析", str(exc))
    if op == "add_alias":
        alias = str(payload.get("alias") or "").strip()
        if not alias:
            return _conflict(body, patch, "别名为空", "add_alias 需要 alias")
        aliases = [str(item) for item in (meta.get("aliases") or [])]
        if alias not in aliases:
            aliases.append(alias)
        meta["aliases"] = aliases
        _stamp(meta, source_ref)
        return _dump(meta, prose), PatchOutcome(status="applied")
    if op == "open_review":
        title = str(payload.get("title") or "待核对").strip()
        kind = str(payload.get("type") or payload.get("kind") or "maintain").strip()
        review_body = str(payload.get("body") or "").strip() or title
        return _append_review(body, kind, title, review_body), PatchOutcome(
            status="applied", review_title=title, review_body=review_body
        )
    if local in _TABLE_LOCKED:
        return _conflict(
            body,
            patch,
            "表级结构以导入基线为准",
            "主键、粒度、名称锚点和默认过滤只跟随导入",
        )
    if local == "notes" or local.startswith("notes") or local == "body":
        text = str(payload.get("text") or payload.get("body") or "").strip()
        if not text:
            return _conflict(body, patch, "说明为空", "notes 需要 text")
        stamped = f"{text}\n\n来源：{source_ref}" if source_ref else text
        _stamp(meta, source_ref)
        return _append_note(_dump(meta, prose), stamped), PatchOutcome(status="applied")
    if local.startswith("values."):
        code = local.split(".", 1)[1]
        return _upsert_dict_value(meta, prose, code, payload, origin, source_ref, patch)
    if local.startswith("fields."):
        name = local.split(".", 1)[1]
        return _upsert_field(meta, prose, name, payload, origin, source_ref, patch)
    if local == "relations" or local.startswith("relations"):
        return _upsert_relation(meta, prose, payload, origin, source_ref, patch)
    if local.startswith("stages."):
        stage = local.split(".", 1)[1]
        return _upsert_stage(meta, prose, stage, payload, source_ref, patch)
    if (
        str(meta.get("type") or "") == "concept"
        and local.split(".", 1)[0] in _CONCEPT_FIELDS
    ):
        return _upsert_concept(meta, prose, local, payload, source_ref, patch)
    kind = _exclusive_kind(meta, local)
    if kind:
        return _upsert_exclusive(
            meta, prose, kind, local, payload, origin, source_ref, patch
        )
    if op == "dispute_claim":
        return _dispute(meta, prose, local, source_ref, patch)
    return _conflict(
        body, patch, "主张路径无法落地", f"claim_path {local or '空'} 没有对应的合并键"
    )


def _promote_status(
    body: str, payload: dict[str, Any], patch: dict[str, Any]
) -> tuple[str, PatchOutcome]:
    status = str(payload.get("status") or "").strip()
    if status not in PAGE_STATUSES:
        return _conflict(body, patch, "发布状态不合法", status or "空")
    if not body.strip():
        return _conflict(body, patch, "页面不存在", "没有可发布的页")
    try:
        meta, prose = _split_frontmatter(body)
    except ValueError as exc:
        return _conflict(body, patch, "页面无法解析", str(exc))
    meta["status"] = status
    meta["updated"] = date.today().isoformat()
    return _dump(meta, prose), PatchOutcome(status="applied")


def _create_page(
    body: str, payload: dict[str, Any], source_ref: str
) -> tuple[str, PatchOutcome]:
    if body.strip():
        return _conflict(
            body, {"claim_path": "page"}, "页面已存在", "create_page 只用于还没有的页"
        )
    belong = str(payload.get("belong") or "").strip()
    page_key = str(payload.get("page_key") or "").strip()
    title = str(payload.get("title") or page_key).strip()
    if belong not in _BUSINESS_BELONGS:
        return _conflict(
            body,
            {"claim_path": "page"},
            "不能新建物理页",
            "表和枚举页只能由导入生成；维护可以改已有页",
        )
    page_type = BELONG_TO_TYPE.get(belong, "")
    if page_type not in PAGE_TYPES or not _slug_valid(page_type, page_key):
        return _conflict(
            body, {"claim_path": "page"}, "页标识不合法", f"{belong}/{page_key}"
        )
    return blank_page(
        belong=belong, page_key=page_key, title=title, source_ref=source_ref
    ), PatchOutcome(status="applied")


def _upsert_dict_value(
    meta: dict[str, Any],
    prose: str,
    code: str,
    payload: dict[str, Any],
    origin: str,
    source_ref: str,
    patch: dict[str, Any],
) -> tuple[str, PatchOutcome]:
    fences = _fences(prose)
    target = next((item for item in fences if item["kind"] == "dict"), None)
    if target is None or not isinstance(target["data"], dict):
        return _conflict(
            _dump(meta, prose),
            patch,
            "没有枚举块",
            f"页上没有 ground:dict，不能写取值 {code}",
        )
    data = target["data"]
    values = data.get("values") if isinstance(data.get("values"), dict) else {}
    current = values.get(code) if isinstance(values.get(code), dict) else {}
    label = str(payload.get("label") or "").strip()
    requested = str(payload.get("trust") or "proposed")
    trust = cap_trust(origin, requested)
    if (
        current
        and str(current.get("trust") or "") == "confirmed"
        and label
        and label != str(current.get("label") or "")
        and origin in MAINTAIN_ORIGINS
    ):
        review = f"{code} 已确认含义是「{current.get('label') or ''}」，维护来源给出「{label}」，未覆盖。"
        text = _append_review(
            _dump(meta, prose),
            "dict_label",
            f"枚举 {code} 含义冲突",
            review + (f"\n来源：{source_ref}" if source_ref else ""),
        )
        return text, PatchOutcome(
            status="conflicted",
            review_title=f"枚举 {code} 含义冲突",
            review_body=review,
        )
    nxt = dict(current)
    if label:
        nxt["label"] = label
    nxt["trust"] = (
        trust
        if not current
        else (
            str(current.get("trust"))
            if str(current.get("trust") or "") == "confirmed"
            and origin in MAINTAIN_ORIGINS
            else trust
        )
    )
    if source_ref and not nxt.get("evidence"):
        nxt["evidence"] = source_ref
    values[code] = nxt
    data["values"] = values
    prose = _replace_fence(prose, target, data)
    _stamp(meta, source_ref)
    return _dump(meta, prose), PatchOutcome(status="applied")


def _upsert_field(
    meta: dict[str, Any],
    prose: str,
    name: str,
    payload: dict[str, Any],
    origin: str,
    source_ref: str,
    patch: dict[str, Any],
) -> tuple[str, PatchOutcome]:
    fences = _fences(prose)
    target = next((item for item in fences if item["kind"] == "table"), None)
    if target is None or not isinstance(target["data"], dict):
        return _conflict(
            _dump(meta, prose),
            patch,
            "没有表块",
            f"页上没有 ground:table，不能写字段 {name}",
        )
    data = target["data"]
    fields = data.get("fields") if isinstance(data.get("fields"), list) else []
    field_row = next(
        (
            item
            for item in fields
            if isinstance(item, dict) and str(item.get("name") or "") == name
        ),
        None,
    )
    if field_row is None:
        review = f"字段 {name} 不在导入基线的列全集里，未新增。"
        text = _append_review(
            _dump(meta, prose), "missing_field", f"字段 {name} 不存在", review
        )
        return text, PatchOutcome(
            status="conflicted", review_title=f"字段 {name} 不存在", review_body=review
        )
    note = str(payload.get("desc") or payload.get("text") or "").strip()
    label = str(payload.get("label") or "").strip()
    code = str(payload.get("code") or "").strip()
    if code:
        codes = field_row.get("dict") if isinstance(field_row.get("dict"), list) else []
        labels = (
            field_row.get("label") if isinstance(field_row.get("label"), dict) else {}
        )
        existing = str(labels.get(code) or "")
        if (
            code in codes
            and existing
            and label
            and existing != label
            and origin in MAINTAIN_ORIGINS
        ):
            review = f"{name}.{code} 已有含义「{existing}」，维护来源给出「{label}」，未覆盖。"
            text = _append_review(
                _dump(meta, prose), "dict_label", f"字段 {name}.{code} 含义冲突", review
            )
            return text, PatchOutcome(
                status="conflicted",
                review_title=f"字段 {name}.{code} 含义冲突",
                review_body=review,
            )
        if code not in codes:
            codes = [*codes, code]
        if label:
            labels = {**labels, code: label}
        field_row["dict"] = codes
        if labels:
            field_row["label"] = labels
        prose = _replace_fence(prose, target, data)
    if note:
        prose = _append_note(
            prose,
            f"字段 {name}：{note}" + (f"（来源：{source_ref}）" if source_ref else ""),
        )
    _stamp(meta, source_ref)
    return _dump(meta, prose), PatchOutcome(status="applied")


def _upsert_relation(
    meta: dict[str, Any],
    prose: str,
    payload: dict[str, Any],
    origin: str,
    source_ref: str,
    patch: dict[str, Any],
) -> tuple[str, PatchOutcome]:
    left, right = _relation_ends(str(patch.get("claim_path") or ""), payload)
    if not left or not right:
        return _conflict(
            _dump(meta, prose), patch, "关系端点缺失", "relation 需要 left 和 right"
        )
    fences = _fences(prose)
    match = None
    for item in fences:
        if item["kind"] != "relation" or not isinstance(item["data"], dict):
            continue
        data = item["data"]
        if (
            str(data.get("left") or "") == left
            and str(data.get("right") or "") == right
        ):
            match = item
            break
    cardinality = str(payload.get("cardinality") or "").strip()
    if match is not None:
        current = match["data"]
        current_card = str(current.get("cardinality") or "")
        if (
            cardinality
            and current_card
            and cardinality != current_card
            and origin in MAINTAIN_ORIGINS
        ):
            review = (
                f"{left} → {right} 已有基数 {current_card}，"
                f"维护来源给出 {cardinality}，未覆盖。"
            )
            text = _append_review(
                _dump(meta, prose), "relation", "关系基数冲突", review
            )
            return text, PatchOutcome(
                status="conflicted", review_title="关系基数冲突", review_body=review
            )
        if cardinality and not current_card:
            current["cardinality"] = cardinality
        note = str(payload.get("note") or "").strip()
        if note:
            current["authenticity_note"] = note
        if source_ref and not current.get("evidence"):
            current["evidence"] = source_ref
        prose = _replace_fence(prose, match, current)
    else:
        block = {
            "type": "EQUI_JOIN",
            "left": left,
            "right": right,
            "cardinality": cardinality or "one_to_many",
            "trust": cap_trust(origin, str(payload.get("trust") or "proposed")),
            "evidence": source_ref,
        }
        note = str(payload.get("note") or "").strip()
        if note:
            block["authenticity_note"] = note
        prose = _append_fence(prose, "relation", block)
    _stamp(meta, source_ref)
    return _dump(meta, prose), PatchOutcome(status="applied")


def _relation_ends(claim_path: str, payload: dict[str, Any]) -> tuple[str, str]:
    left = str(payload.get("left") or "").strip()
    right = str(payload.get("right") or "").strip()
    local = _local_path(claim_path)
    raw = local.split(".", 1)[1] if local.startswith("relations.") else ""
    if "__" in raw:
        path_left, path_right = raw.split("__", 1)
        left = left or path_left.strip()
        right = right or path_right.strip()
    return left, right


def _exclusive_kind(meta: dict[str, Any], local: str) -> str | None:
    page_type = str(meta.get("type") or "")
    allowed = _EXCLUSIVE_FIELDS.get(page_type)
    if not allowed:
        return None
    head = local.split(".", 1)[0]
    if head in allowed or local in allowed:
        return page_type
    return None


def _exclusive_updates(
    kind: str, local: str, payload: dict[str, Any]
) -> dict[str, Any]:
    allowed = _EXCLUSIVE_FIELDS[kind]
    updates = {key: value for key, value in payload.items() if key in allowed}
    if updates:
        return updates
    head = local.split(".", 1)[0]
    if head in allowed and "." not in local:
        if "value" in payload:
            return {head: payload["value"]}
        if "text" in payload:
            return {head: payload["text"]}
    return {}


def _foreign_sources(
    meta: dict[str, Any], data: dict[str, Any], source_ref: str
) -> bool:
    sources = [str(item) for item in (meta.get("sources") or []) if str(item)]
    evidence = str(data.get("evidence") or "")
    others = [item for item in sources if item != source_ref]
    if evidence and evidence != source_ref:
        others.append(evidence)
    return bool(others)


def _upsert_concept(
    meta: dict[str, Any],
    prose: str,
    local: str,
    payload: dict[str, Any],
    source_ref: str,
    patch: dict[str, Any],
) -> tuple[str, PatchOutcome]:
    key = local.split(".", 1)[0]
    if _foreign_sources(meta, {}, source_ref):
        return _conflict(
            _dump(meta, prose),
            patch,
            "概念已有其他来源",
            "这一页已经有别的来源，未覆盖。",
        )
    if key in payload:
        value = payload[key]
    elif "value" in payload:
        value = payload["value"]
    elif "text" in payload:
        value = payload["text"]
    else:
        return _conflict(_dump(meta, prose), patch, "没有可写入的字段", f"{key} 需要值")
    meta[key] = value
    _stamp(meta, source_ref)
    return _dump(meta, prose), PatchOutcome(status="applied")


def _upsert_exclusive(
    meta: dict[str, Any],
    prose: str,
    kind: str,
    local: str,
    payload: dict[str, Any],
    origin: str,
    source_ref: str,
    patch: dict[str, Any],
) -> tuple[str, PatchOutcome]:
    fences = _fences(prose)
    target = next((item for item in fences if item["kind"] == kind), None)
    data = target["data"] if target and isinstance(target["data"], dict) else None
    current = data if isinstance(data, dict) else {}
    confirmed = (
        str(current.get("trust") or "") == "confirmed" and origin in MAINTAIN_ORIGINS
    )
    if confirmed or _foreign_sources(meta, current, source_ref):
        title = f"{kind} 已确认" if confirmed else f"{kind} 已有其他来源"
        review = (
            "已确认主张不能由维护覆盖。"
            if confirmed
            else "这一页已经有别的来源，未覆盖。"
        )
        return _conflict(_dump(meta, prose), patch, title, review)
    updates = _exclusive_updates(kind, local, payload)
    if kind == "pattern" and payload.get("trust"):
        updates["trust"] = cap_trust(origin, str(payload.get("trust") or "proposed"))
    if not updates:
        return _conflict(
            _dump(meta, prose),
            patch,
            "没有可写入的字段",
            f"{local or kind} 没有对应的草稿字段",
        )
    merged = dict(current)
    if not merged:
        merged[kind] = str(meta.get("title") or meta.get("page_key") or kind)
    merged.update(updates)
    if source_ref and not merged.get("evidence"):
        merged["evidence"] = source_ref
    if target is None:
        prose = _append_fence(prose, kind, merged)
    else:
        prose = _replace_fence(prose, target, merged)
    _stamp(meta, source_ref)
    return _dump(meta, prose), PatchOutcome(status="applied")


def _upsert_stage(
    meta: dict[str, Any],
    prose: str,
    stage_name: str,
    payload: dict[str, Any],
    source_ref: str,
    patch: dict[str, Any],
) -> tuple[str, PatchOutcome]:
    fences = _fences(prose)
    target = next((item for item in fences if item["kind"] == "process"), None)
    if target is None or not isinstance(target["data"], dict):
        return _conflict(
            _dump(meta, prose), patch, "没有流程块", "页上没有 ground:process"
        )
    data = target["data"]
    stages = data.get("stages") if isinstance(data.get("stages"), list) else []
    stage = next(
        (
            item
            for item in stages
            if isinstance(item, dict) and str(item.get("stage") or "") == stage_name
        ),
        None,
    )
    if stage is None:
        stage = {"stage": stage_name, "transitions": []}
        stages.append(stage)
    transitions = (
        stage.get("transitions") if isinstance(stage.get("transitions"), list) else []
    )
    incoming = {
        "from": str(payload.get("from") or ""),
        "event": str(payload.get("event") or ""),
        "to": str(payload.get("to") or ""),
        "evidence": source_ref,
    }
    if not any(
        isinstance(item, dict)
        and str(item.get("from") or "") == incoming["from"]
        and str(item.get("event") or "") == incoming["event"]
        and str(item.get("to") or "") == incoming["to"]
        for item in transitions
    ):
        transitions.append(incoming)
    stage["transitions"] = transitions
    data["stages"] = stages
    prose = _replace_fence(prose, target, data)
    _stamp(meta, source_ref)
    return _dump(meta, prose), PatchOutcome(status="applied")


def _dispute(
    meta: dict[str, Any],
    prose: str,
    local: str,
    source_ref: str,
    patch: dict[str, Any],
) -> tuple[str, PatchOutcome]:
    if local.startswith("values."):
        code = local.split(".", 1)[1]
        fences = _fences(prose)
        target = next((item for item in fences if item["kind"] == "dict"), None)
        if target and isinstance(target["data"], dict):
            values = (
                target["data"].get("values")
                if isinstance(target["data"].get("values"), dict)
                else {}
            )
            current = values.get(code)
            if isinstance(current, dict):
                current["trust"] = "disputed"
                values[code] = current
                target["data"]["values"] = values
                prose = _replace_fence(prose, target, target["data"])
    title = f"主张存疑 {local or 'page'}"
    review = str(
        patch.get("payload", {}).get("reason") or "维护来源要求把这条主张标为存疑"
    )
    if source_ref:
        review = f"{review}\n来源：{source_ref}"
    _stamp(meta, source_ref)
    return _append_review(_dump(meta, prose), "disputed", title, review), PatchOutcome(
        status="applied", review_title=title, review_body=review
    )


def _ensure_recorded_review(
    body: str, patch: dict[str, Any]
) -> tuple[str, PatchOutcome]:
    payload = patch.get("payload") if isinstance(patch.get("payload"), dict) else {}
    title = str(payload.get("review_title") or patch.get("claim_path") or "冲突")
    if title and title in body:
        return body, PatchOutcome(status="conflicted", review_title=title)
    review_body = str(payload.get("review") or "这条维护主张与基线冲突，未覆盖。")
    return _append_review(body, "maintain", title, review_body), PatchOutcome(
        status="conflicted", review_title=title, review_body=review_body
    )


def _conflict(
    body: str, _patch: dict[str, Any], title: str, review: str
) -> tuple[str, PatchOutcome]:
    text = body
    if body.strip():
        text = _append_review(body, "maintain", title, review)
    return text, PatchOutcome(
        status="conflicted", review_title=title, review_body=review
    )


def _stamp(meta: dict[str, Any], source_ref: str) -> None:
    if source_ref:
        sources = [str(item) for item in (meta.get("sources") or [])]
        if source_ref not in sources:
            sources.append(source_ref)
        meta["sources"] = sources
    meta["updated"] = date.today().isoformat()


def _local_path(claim_path: str) -> str:
    text = claim_path.strip()
    if "#" in text:
        text = text.split("#", 1)[1]
    return text.strip()


def _split_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    if not content.startswith("---\n"):
        raise ValueError("page must start with YAML frontmatter")
    end = content.find("\n---\n", 4)
    if end < 0:
        raise ValueError("frontmatter not closed")
    meta = yaml.safe_load(content[4:end])
    if not isinstance(meta, dict):
        raise ValueError("frontmatter must be a mapping")
    return meta, content[end + 5 :]


def _dump(meta: dict[str, Any], prose: str) -> str:
    dumped = yaml.safe_dump(
        meta, allow_unicode=True, sort_keys=False, width=1000
    ).rstrip()
    body = prose.lstrip("\n")
    return f"---\n{dumped}\n---\n\n{body}".rstrip() + "\n"


def _fences(prose: str) -> list[dict[str, Any]]:
    lines = prose.splitlines()
    found: list[dict[str, Any]] = []
    index = 0
    while index < len(lines):
        opener = _FENCE_OPEN.match(lines[index])
        if not opener:
            index += 1
            continue
        start = index
        kind = opener.group("kind")
        index += 1
        payload: list[str] = []
        while index < len(lines) and not _FENCE_CLOSE.match(lines[index]):
            payload.append(lines[index])
            index += 1
        if index >= len(lines):
            break
        end = index
        raw = "\n".join(payload)
        try:
            data = yaml.safe_load(raw)
        except yaml.YAMLError:
            data = None
        found.append(
            {"kind": kind, "start": start, "end": end, "raw": raw, "data": data}
        )
        index += 1
    return found


def _replace_fence(prose: str, fence: dict[str, Any], data: dict[str, Any]) -> str:
    lines = prose.splitlines()
    dumped = yaml.safe_dump(
        data, allow_unicode=True, sort_keys=False, width=1000
    ).rstrip()
    replacement = [f"```ground:{fence['kind']}", *dumped.splitlines(), "```"]
    nxt = lines[: fence["start"]] + replacement + lines[fence["end"] + 1 :]
    return "\n".join(nxt) + ("\n" if prose.endswith("\n") else "")


def _append_fence(prose: str, kind: str, data: dict[str, Any]) -> str:
    dumped = yaml.safe_dump(
        data, allow_unicode=True, sort_keys=False, width=1000
    ).rstrip()
    block = f"```ground:{kind}\n{dumped}\n```\n"
    return prose.rstrip() + "\n\n" + block


def _append_review(body: str, kind: str, title: str, review: str) -> str:
    if title and title in body and "---REVIEW:" in body:
        return body
    block = f"---REVIEW: {kind} | {title}---\n{review.strip()}\n---END REVIEW---\n"
    return body.rstrip() + "\n\n" + block


def _append_note(body: str, text: str) -> str:
    paragraph = text.strip()
    if not paragraph:
        return body
    if _NOTES_HEADING not in body:
        return body.rstrip() + f"\n\n{_NOTES_HEADING}\n\n{paragraph}\n"
    if paragraph in body:
        return body
    lines = body.splitlines()
    start = next(
        index for index, line in enumerate(lines) if line.strip() == _NOTES_HEADING
    )
    end = len(lines)
    for index in range(start + 1, len(lines)):
        if lines[index].startswith("## "):
            end = index
            break
    lines[end:end] = ["", paragraph]
    return "\n".join(lines).rstrip() + "\n"
