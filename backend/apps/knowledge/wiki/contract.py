"""Wiki page contract (v0 spec: docs/wiki页面契约-spec-v0.md).

Zero-trust parsing: structural violations on required fields raise
PageContractError; unknown ground kinds are warn-and-ignore (forward
compatible); ground content problems surface as lint findings for the
review queue — never silent adoption. Identity rules follow
``docs/wiki/pages.md``: tables/enums use physical names (cross-language
stable), business pages keep CJK slugs.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

import yaml

_GROUND_FENCE_RE = re.compile(r"^```ground:(?P<kind>[a-z-]+)\s*$")
_WIKILINK_RE = re.compile(r"\[\[(?P<target>[^\]|]+)(?:\|(?P<alias>[^\]]+))?\]\]")
_REVIEW_RE = re.compile(
    r"---REVIEW:\s*(?P<type>[\w-]+)\s*\|\s*(?P<title>.+?)\s*---\n"
    r"(?P<body>.*?)---END REVIEW---",
    re.S,
)
_FENCE_CLOSE_RE = re.compile(r"^```\s*$")

PHYSICAL_SLUG_RE = re.compile(r"^[a-z][a-z0-9_]*$")  # 表名
ENUM_SLUG_RE = re.compile(
    r"^[a-z][a-z0-9_]*((::|\.)[a-z][a-z0-9_]*)?$"
)  # dictKey；L0 表::字段（物理锚仍是 表.字段）
BUSINESS_SLUG_RE = re.compile(r"^[\w-]+$")  # 业务页：CJK 保留，不罗马化（v0 §1.1）
PAGE_STATUSES = {"draft", "published", "retired"}
PAGE_TYPES = {
    "table",
    "enum",
    "concept",
    "process",
    "caliber",
    "metric",
    "rule",
    "pattern",
    "query",
    "source",
    "scenario",
}
TYPE_TO_BELONG = {
    "table": "tables",
    "enum": "enums",
    "concept": "concepts",
    "process": "processes",
    "caliber": "calibers",
    "metric": "metrics",
    "rule": "rules",
    "pattern": "patterns",
    "query": "queries",
    "source": "sources",
    "scenario": "scenarios",
}
BELONG_TO_TYPE = {value: key for key, value in TYPE_TO_BELONG.items()}
BELONG_DIRS = frozenset(TYPE_TO_BELONG.values())
_KEY_PREFIXES = frozenset(PAGE_TYPES) | BELONG_DIRS
GROUND_KINDS = {
    "table",
    "enum",
    "relation",
    "process",
    "caliber",
    "metric",
    "rule",
    "pattern",
    "scenario",
}
# v0 §3.3 硬规则：租户/审计/同名拷贝字段不得作关系端点
_TENANT_FIELDS = frozenset(
    {"tenant_id", "tenant_code", "db_tenant_code", "app_tenant_code", "organization_id"}
)
_TYPE_FAMILIES = {
    "string": {"char", "varchar", "text", "string"},
    "number": {
        "int",
        "bigint",
        "smallint",
        "decimal",
        "numeric",
        "number",
        "float",
        "double",
    },
    "temporal": {"date", "datetime", "timestamp", "time", "temporal"},
    "boolean": {"bool", "boolean"},
    "structured": {"json", "jsonb", "structured"},
}


class PageContractError(ValueError):
    """Structural violation — the page cannot be accepted at all."""

    def __init__(self, errors: list[str]) -> None:
        super().__init__("; ".join(errors))
        self.errors = errors


@dataclass(frozen=True)
class GroundAnchor:
    kind: str
    data: dict[str, Any]
    raw: str


@dataclass(frozen=True)
class WikiLink:
    target: str
    alias: str


@dataclass(frozen=True)
class ReviewItem:
    type: str
    title: str
    body: str


@dataclass(frozen=True)
class WikiPage:
    page_key: str
    title: str
    type: str
    status: str
    body: str
    belong: str = ""
    aliases: tuple[str, ...] = field(default_factory=tuple)
    domain: str = ""
    databases: tuple[str, ...] = field(
        default_factory=tuple
    )  # scope.databases 物理库名围栏；空=不限（数据源是来源不是使用限制）
    anchors: tuple[str, ...] = field(default_factory=tuple)  # 物理键清单
    field_targets: tuple[str, ...] = field(default_factory=tuple)  # 结构边
    sources: tuple[str, ...] = field(default_factory=tuple)
    tags: tuple[str, ...] = field(default_factory=tuple)
    related: tuple[str, ...] = field(default_factory=tuple)  # 软关联（裸 slug）
    maps_to: str = ""
    also_confused_with: tuple[str, ...] = field(default_factory=tuple)
    adjudication: str = ""
    inactive: bool = False
    recall: bool = True
    contract_version: str = "0.1"
    schema_fingerprints: tuple[str, ...] = field(
        default_factory=tuple
    )  # stale lint 依据
    ground_blocks: tuple[GroundAnchor, ...] = field(default_factory=tuple)
    unknown_ground_kinds: tuple[str, ...] = field(default_factory=tuple)
    parse_findings: tuple[Finding, ...] = field(
        default_factory=tuple
    )  # v0 §0.1：语法失败=丢块+警告（页面散文保留），警告进 REVIEW 队列
    links: tuple[WikiLink, ...] = field(default_factory=tuple)
    reviews: tuple[ReviewItem, ...] = field(default_factory=tuple)

    @property
    def identity_aliases(self) -> tuple[str, ...]:
        return (
            self.page_key.lower(),
            self.title.lower(),
            *(a.lower() for a in self.aliases),
        )

    @property
    def store_key(self) -> str:
        """Corpus-unique identity: belong/page_key (fall back to type dir)."""
        belong = self.belong or TYPE_TO_BELONG.get(self.type, "")
        if belong:
            return f"{belong}/{self.page_key}"
        return self.page_key


def normalize_link_target(target: str) -> str:
    text = target.strip()
    text = re.sub(r"\.(md|markdown)$", "", text, flags=re.I)
    text = text.split("#", 1)[0]
    text = text.strip().lower()
    text = re.sub(r"^wiki/", "", text)
    return text


def normalize_page_key(raw: str) -> str:
    """Strip accidental type/dir prefixes and spaces from a page_key draft."""
    text = str(raw or "").strip().strip("'\"")
    for sep in ("/", "."):
        if sep not in text:
            continue
        prefix, rest = text.split(sep, 1)
        if prefix in _KEY_PREFIXES and rest.strip():
            text = rest.strip()
            break
    text = re.sub(r"\s+", "-", text)
    return text


def infer_belong(page_type: str, *, directory: str | None = None) -> str:
    if directory and directory in BELONG_DIRS:
        return directory
    return TYPE_TO_BELONG.get(page_type, "")


def _slug_valid(page_type: str, slug: str) -> bool:
    if page_type == "table":
        return bool(PHYSICAL_SLUG_RE.match(slug))
    if page_type == "enum":
        return bool(ENUM_SLUG_RE.match(slug))
    return bool(BUSINESS_SLUG_RE.match(slug))


def _parse_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    if not content.startswith("---\n"):
        raise PageContractError(["page must start with YAML frontmatter (---)"])
    end = content.find("\n---\n", 4)
    if end < 0:
        raise PageContractError(["frontmatter not closed (missing '\\n---\\n')"])
    meta = yaml.safe_load(content[4:end])
    if not isinstance(meta, dict):
        raise PageContractError(["frontmatter must be a YAML mapping"])
    return meta, content[end + 5 :]


def _parse_ground_blocks(
    body: str,
) -> tuple[tuple[GroundAnchor, ...], tuple[str, ...], tuple[Finding, ...]]:
    """Fence info-string syntax ```ground:<kind>（v0 §3.0 + §0.1 零信任）.

    Unknown kinds: warn-and-ignore（前向兼容）。坏 YAML：**丢弃该块 + 警告**，
    页面散文保留（v0 §0.1——一个坏块不杀死整页，发布门禁兜底质量）。
    fence 未闭合属于结构破坏，仍然 raise。
    """
    anchors: list[GroundAnchor] = []
    unknown: list[str] = []
    findings: list[Finding] = []
    lines = body.splitlines()
    index = 0
    while index < len(lines):
        opener = _GROUND_FENCE_RE.match(lines[index])
        if not opener:
            index += 1
            continue
        kind = opener.group("kind")
        index += 1
        payload: list[str] = []
        closed = False
        while index < len(lines):
            if _FENCE_CLOSE_RE.match(lines[index]):
                closed = True
                index += 1
                break
            payload.append(lines[index])
            index += 1
        if not closed:
            raise PageContractError([f"ground:{kind} fence not closed"])
        if kind not in GROUND_KINDS:
            unknown.append(kind)  # 警告 + 忽略（v0 §3.0）
            continue
        try:
            data = yaml.safe_load("\n".join(payload))
        except yaml.YAMLError as exc:
            findings.append(
                Finding(
                    "GROUND_PARSE_FAILED",
                    f"ground:{kind} YAML 解析失败已丢弃（页面散文保留）: {exc}",
                )
            )
            continue
        if not isinstance(data, dict):
            findings.append(
                Finding(
                    "GROUND_PARSE_FAILED",
                    f"ground:{kind} 必须是 YAML 映射，已丢弃（页面散文保留）",
                )
            )
            continue
        anchors.append(GroundAnchor(kind=kind, data=data, raw="\n".join(payload)))
    return tuple(anchors), tuple(unknown), tuple(findings)


def parse_page(
    content: str,
    *,
    page_key: str | None = None,
    override_page_key: bool = False,
    belong: str | None = None,
) -> WikiPage:
    """Parse one page; structural violations raise PageContractError.

    Identity is ``(belong, page_key)``. Frontmatter ``page_key`` wins over
    filename stem unless ``override_page_key=True`` (LLM ingest drafts).
    ``belong`` from the parent directory is authoritative when provided.
    Illegal drafts like ``caliber/foo`` are normalized to ``foo``.
    """
    meta, body = _parse_frontmatter(content)
    fm_key = str(meta.get("page_key") or "").strip()
    if page_key is not None and (override_page_key or not fm_key):
        meta = {**meta, "page_key": page_key}

    def strings(key: str) -> tuple[str, ...]:
        return tuple(
            str(item).strip() for item in (meta.get(key) or []) if str(item).strip()
        )

    errors: list[str] = []
    raw_key = str(meta.get("page_key") or "")
    page_key = normalize_page_key(raw_key)
    title = str(meta.get("title") or "").strip()
    page_type = str(meta.get("type") or "")
    status = str(meta.get("status") or "")
    fm_belong = str(meta.get("belong") or "").strip()
    dir_belong = str(belong or "").strip()
    if dir_belong:
        if fm_belong and fm_belong != dir_belong:
            errors.append(f"belong {fm_belong!r} 与目录 {dir_belong!r} 不一致")
        resolved_belong = dir_belong
    elif fm_belong:
        resolved_belong = fm_belong
    else:
        resolved_belong = infer_belong(page_type)
    if resolved_belong and resolved_belong not in BELONG_DIRS:
        errors.append(
            f"belong must be one of {sorted(BELONG_DIRS)}, got {resolved_belong!r}"
        )
    expected_type = BELONG_TO_TYPE.get(resolved_belong)
    if expected_type and page_type and page_type != expected_type:
        errors.append(
            f"type {page_type!r} 与 belong {resolved_belong!r} 不一致"
            f"（应为 {expected_type}）"
        )
    if page_type not in PAGE_TYPES:
        errors.append(f"type must be one of {sorted(PAGE_TYPES)}")
    if status not in PAGE_STATUSES:
        errors.append(f"status must be one of {sorted(PAGE_STATUSES)}")
    if not title:
        errors.append("title is required")
    if page_key and page_type in PAGE_TYPES and not _slug_valid(page_type, page_key):
        rule = (
            "物理名（表 snake_case；枚举 dictKey 或 L0 表::字段）"
            if page_type in {"table", "enum"}
            else "业务 slug（CJK 保留）"
        )
        errors.append(f"page_key {page_key!r} 不符合 {page_type} 页的 {rule}")
    if errors:
        raise PageContractError(errors)

    # scope 围栏：只认块式 scope.databases（物理库名）。旧形态（datasources
    # ds_id、平铺 datasources、点式 scope.datasources）不静默兼容——记 warn
    # finding 交迁移/巡检清洗，防旧值悄悄变成"空 = 不限"扩大可见面。
    scope_meta = meta.get("scope") if isinstance(meta.get("scope"), dict) else {}
    legacy_scope: list[str] = []
    if "datasources" in scope_meta:
        legacy_scope.append("scope.datasources")
    if "datasources" in meta:
        legacy_scope.append("datasources（平铺）")
    if "datasources" in str(meta.get("scope") or ""):
        legacy_scope.append("scope.datasources（点式）")
    databases = tuple(
        folded
        for folded in dict.fromkeys(
            str(item).strip().lower()
            for item in (scope_meta.get("databases") or [])
            if str(item).strip()
        )
        if folded
    )
    if legacy_scope:
        parse_findings_extra = [
            Finding(
                "LEGACY_SCOPE",
                f"废弃围栏形态 {legacy_scope}——请改为 scope.databases（物理库名）",
            )
        ]
    else:
        parse_findings_extra = []

    anchors_blocks, unknown, parse_findings = _parse_ground_blocks(body)
    parse_findings = (*parse_findings, *parse_findings_extra)
    links = tuple(
        WikiLink(
            target=normalize_link_target(match.group("target")),
            alias=(match.group("alias") or "").strip(),
        )
        for match in _WIKILINK_RE.finditer(body)
    )
    reviews = tuple(
        ReviewItem(
            type=match.group("type"),
            title=match.group("title"),
            body=match.group("body").strip(),
        )
        for match in _REVIEW_RE.finditer(content)
    )
    refs = meta.get("refs") if isinstance(meta.get("refs"), dict) else {}
    return WikiPage(
        page_key=page_key,
        title=title,
        type=page_type,
        status=status,
        body=body,
        belong=resolved_belong,
        aliases=strings("aliases"),
        domain=str(meta.get("domain") or ""),
        databases=databases,
        anchors=strings("anchors"),
        field_targets=strings("field_targets"),
        sources=strings("sources"),
        tags=strings("tags"),
        related=strings("related"),
        maps_to=str(meta.get("maps_to") or ""),
        also_confused_with=strings("also_confused_with"),
        adjudication=str(meta.get("adjudication") or ""),
        inactive=bool(meta.get("inactive") or False),
        recall=meta.get("recall") is not False,
        contract_version=str(meta.get("contract_version") or "0.1"),
        schema_fingerprints=tuple(
            str(f) for f in (refs.get("schema_fingerprints") or [])
        ),
        ground_blocks=anchors_blocks,
        unknown_ground_kinds=unknown,
        parse_findings=parse_findings,
        links=links,
        reviews=reviews,
    )


@dataclass(frozen=True)
class Finding:
    code: str
    message: str


def _field_family_ok(declared: str, baseline: dict[str, Any]) -> bool:
    family = str(baseline.get("family") or "").lower()
    members = _TYPE_FAMILIES.get(family, set())
    return not members or declared.lower() in members


def lint_page(
    page: WikiPage,
    *,
    known_keys: set[str],
    catalog: dict[str, Any] | None = None,
) -> list[Finding]:
    """v0 §6 lint 码表（结构可查子集）；findings 喂 REVIEW 队列，不静默采纳。"""

    def _fold(name: str) -> str:
        # 与 graph.fold_key 同一 snake/kebab 折叠语义（避免模块级循环导入）
        return normalize_link_target(name).replace("_", "-")

    findings: list[Finding] = list(page.parse_findings)
    tables = (catalog or {}).get("tables") if isinstance(catalog, dict) else None
    baseline_enums = (catalog or {}).get("enums") if isinstance(catalog, dict) else None

    for kind in page.unknown_ground_kinds:
        findings.append(
            Finding("UNKNOWN_GROUND_KIND", f"未知 ground 块种类 {kind!r}（忽略）")
        )

    seen: dict[tuple[str, str], int] = {}
    for block in page.ground_blocks:
        data = block.data
        if block.kind == "relation":
            unique = ("relation", f"{data.get('left')}|{data.get('right')}")
        else:
            key_value = str(
                data.get(block.kind) or data.get("table") or data.get("process") or ""
            )
            unique = (block.kind, key_value)
        seen[unique] = seen.get(unique, 0) + 1
    for (kind, key_value), count in seen.items():
        if count > 1:
            findings.append(
                Finding(
                    "DUPLICATE_GROUND_BLOCK",
                    f"ground:{kind} 键 {key_value!r} 重复 {count} 次",
                )
            )

    folded_known = {_fold(k) for k in known_keys}
    folded_known.add(_fold(page.page_key))
    folded_known.add(_fold(page.store_key))
    identities = set(folded_known)
    bare_groups: dict[str, set[str]] = {}
    for folded in identities:
        bare = folded.rsplit("/", 1)[-1]
        if bare:
            bare_groups.setdefault(bare, set()).add(folded)

    def _bare_unique(bare: str) -> int:
        group = bare_groups.get(bare) or set()
        store_keys = {item for item in group if "/" in item}
        slugs = {item for item in group if "/" not in item}
        covered = {item.rsplit("/", 1)[-1] for item in store_keys}
        return len(store_keys) + len(slugs - covered)

    for link in page.links:
        folded = _fold(link.target)
        if folded in folded_known:
            continue
        bare = folded.rsplit("/", 1)[-1]
        hits = _bare_unique(bare) if "/" not in folded else 0
        if hits == 1:
            continue
        if hits > 1:
            findings.append(
                Finding(
                    "AMBIGUOUS_LINK",
                    f"[[{link.target}]] 对应多页，请写成 [[belong/{link.target}]]",
                )
            )
            continue
        findings.append(Finding("BROKEN_LINK", f"[[{link.target}]] 无法解析为已知页面"))
    if not page.links:
        findings.append(Finding("NO_OUTLINKS", "页面没有任何出链"))

    if page.type == "concept" and not page.field_targets and not page.maps_to:
        findings.append(
            Finding("CONCEPT_UNANCHORED", "concept 页缺 field_targets/maps_to")
        )
    if page.also_confused_with and not page.adjudication:
        findings.append(
            Finding("TERM_UNADJUDICATED", "近似语义裁决未完成（缺 adjudication）")
        )

    # 锚定完备度（advisory——enrich 可确定性修复，存量不阻断 publish）：
    # 语义页引用了物理表（field_targets/maps_to）但正文没有对应 wikilink，
    # 图扩展与锚点闭包都会因此少带相关表页。带 catalog 时只对真实存在的
    # 表报警——DTO/参数类（MessageContext.verifyCode 等）不是表，不误报。
    if page.type not in {"table", "enum"}:
        linked = {
            normalize_link_target(link.target).replace("_", "-") for link in page.links
        }
        referenced = {
            normalize_link_target(str(ref).partition(".")[0]).replace("_", "-")
            for ref in (
                *page.field_targets,
                *(ref for ref in page.anchors if "." in ref),
            )
        }
        if tables is not None:
            known_folded = {
                normalize_link_target(name).replace("_", "-") for name in tables
            }
            referenced = {ref for ref in referenced if ref in known_folded}
        unlinked = sorted(referenced - linked)
        if unlinked:
            findings.append(
                Finding(
                    "SEMANTIC_PAGE_UNLINKED_TABLE",
                    f"引用表 {unlinked[:3]} 未在正文出链（[[表名]]）——锚链断裂",
                )
            )
    if page.type == "table" and "关联" not in page.body:
        findings.append(
            Finding(
                "TABLE_PAGE_NO_RELATIONS",
                "表页无关联节——孤表（可能真实孤立，也可能关系未提取）",
            )
        )

    def _check_physical_ref(ref: str) -> None:
        if tables is None or not ref:
            return
        table_name, _, field_name = ref.partition(".")
        table = tables.get(table_name)
        if table is None:
            findings.append(
                Finding(
                    "REF_TARGET_MISSING",
                    f"物理键 {ref!r} 的表 {table_name!r} 不在 catalog",
                )
            )
        elif field_name and field_name not in table.get("fields", {}):
            findings.append(
                Finding("REF_TARGET_MISSING", f"物理键 {ref!r} 的字段不在 catalog")
            )

    for ref in (*page.field_targets, *(ref for ref in page.anchors if "." in ref)):
        _check_physical_ref(ref)

    if tables is not None:
        _enum_carriers: dict[tuple[str, ...], str] = {}
        for block in page.ground_blocks:
            data = compact_block(block.data)
            if block.kind == "table":
                name = str(data.get("table") or "")
                table = tables.get(name)
                if table is None:
                    findings.append(
                        Finding("TABLE_NOT_IN_CATALOG", f"表 {name!r} 不在 catalog")
                    )
                    continue
                for field_entry in data.get("fields") or []:
                    fname = str(field_entry.get("name") or "")
                    if fname and fname not in table.get("fields", {}):
                        findings.append(
                            Finding(
                                "FIELD_NOT_IN_CATALOG", f"{name}.{fname} 不在 catalog"
                            )
                        )
                    elif fname and not _field_family_ok(
                        str(field_entry.get("type") or ""),
                        table["fields"][fname],
                    ):
                        findings.append(
                            Finding(
                                "TYPE_FAMILY_MISMATCH",
                                f"{name}.{fname} 类型族与 catalog 不一致",
                            )
                        )
            elif block.kind == "enum":
                # 防复发码 1：泛列承载（.type/.status/.code 等列挂载多表）——
                # 历史教训：19 页挂 .type、14 页挂 .status、3 页挂 .code（73 表吞吐）。
                _GENERIC = {
                    "type",
                    "status",
                    "code",
                    "flag",
                    "mode",
                    "level",
                    "source",
                    "channel",
                    "state",
                }
                _enum_refs = [str(r) for r in data.get("fields") or []]
                _generic_hits = [
                    r for r in _enum_refs if r.partition(".")[2] in _GENERIC
                ]
                if len(_generic_hits) > 1:
                    findings.append(
                        Finding(
                            "ENUM_GENERIC_COLUMN",
                            f"泛列 {sorted(set(_generic_hits))[:3]} 承载多表"
                            f"（{len(_generic_hits)} 处）——泛列只允许单表强证据绑定",
                        )
                    )
                # 防复发码 2：同物理列多页——归并器应保证一列一权威页
                _enum_carriers.setdefault(
                    tuple(sorted(_enum_refs)), str(data.get("enum") or page.page_key)
                )
                dict_key = str(data.get("enum") or "")
                known = (baseline_enums or {}).get(dict_key)
                if known is not None:
                    extra = sorted(set(data.get("values") or {}) - set(known))
                    if extra:
                        findings.append(
                            Finding(
                                "ENUM_NOT_IN_BASELINE",
                                f"{dict_key} 声明了基线外的枚举值 {extra}（catalog 胜，转 review）",
                            )
                        )
            elif block.kind == "relation":
                for side in ("left", "right"):
                    ref = str(data.get(side) or "")
                    field_name = ref.partition(".")[2]
                    if field_name in _TENANT_FIELDS:
                        findings.append(
                            Finding(
                                "TENANT_FIELD_AS_ENDPOINT",
                                f"租户/审计字段 {ref!r} 不得作为关系端点",
                            )
                        )
                    _check_physical_ref(ref)
    # 防复发码 2 落地：同承载列集合出现在多个枚举块（页内重复）——跨页重复由
    # 全量巡检（每页 carriers 并集比对）在 admin lint 层做，页内先拦一层。
    return findings


# v0.2 紧凑键别名：description→desc、data_type→type、dictionary→dict、
# meaning→desc（同一语义单键）。写侧统一紧凑键；读侧（lint/reconcile/merge/
# eval）一律经 compact_block 归一——这是唯一的键归一化实现，禁止各处内联。
_COMPACT_FIELD_ALIASES = {
    "description": "desc",
    "meaning": "desc",
    "data_type": "type",
    "dictionary": "dict",
    "field": "name",
}


_PHYSICAL_TARGET_RE = re.compile(r"^[a-z][a-z0-9_]*\.[A-Za-z][A-Za-z0-9_]*$")


def compact_block(data: Any) -> Any:
    if not isinstance(data, dict):
        return data
    out = dict(data)
    # LLM 方言：columns[{field,meaning}] → fields[{name,desc}]
    if "fields" not in out and isinstance(out.get("columns"), list):
        out["fields"] = out.pop("columns")
    elif "columns" in out:
        out.pop("columns", None)
    for old, new in _COMPACT_FIELD_ALIASES.items():
        if old in out and new not in out:
            out[new] = out.pop(old)
        elif old in out:
            out.pop(old, None)
    fields = out.get("fields")
    if isinstance(fields, list):
        # enum 块的 fields 是 表.列 字符串（非 dict）——原样保留；
        # table 块的 fields 是字段映射 dict——递归归一。
        out["fields"] = [compact_block(f) if isinstance(f, dict) else f for f in fields]
    raw_values = out.get("values")
    if isinstance(raw_values, list):
        converted: dict[str, Any] = {}
        for item in raw_values:
            if isinstance(item, dict) and item.get("value") is not None:
                key = str(item["value"])
                info = {k: v for k, v in item.items() if k != "value"}
                if "label" not in info and info.get("desc"):
                    info["label"] = info["desc"]
                converted[key] = info or {"label": key}
            elif item is not None:
                converted[str(item)] = {"label": str(item)}
        out["values"] = converted
    return out


def stamp_frontmatter(content: str, *, stem: str, belong: str = "") -> str:
    """盖章 page_key/belong，并从合法 maps_to 回填 field_targets。

    磁盘页以文件名 stem 为身份；LLM 草稿常写成 ``table.foo`` / ``concepts/foo``，
    不盖章则渲染器/索引按错误键查找。解析失败时仍做正则盖章，不丢散文。
    """
    match = re.match(r"\A(---\n)([\s\S]*?)(\n---\n)", content)
    if not match:
        return content
    front = match.group(2)
    page_key = normalize_page_key(stem)
    if re.search(r"^page_key:", front, re.M):
        front = re.sub(
            r"^page_key:.*$", f"page_key: {page_key}", front, count=1, flags=re.M
        )
    else:
        front = f"page_key: {page_key}\n{front}"
    if belong:
        if re.search(r"^belong:", front, re.M):
            front = re.sub(
                r"^belong:.*$", f"belong: {belong}", front, count=1, flags=re.M
            )
        else:
            front = f"{front.rstrip()}\nbelong: {belong}"
    maps_raw = ""
    maps_match = re.search(r'^maps_to:\s*"?([^"\n]+)"?\s*$', front, re.M)
    if maps_match:
        maps_raw = maps_match.group(1).strip()
    has_targets = re.search(r"^field_targets:\s*\[", front, re.M)
    if maps_raw and _PHYSICAL_TARGET_RE.match(maps_raw) and not has_targets:
        front = f"{front.rstrip()}\nfield_targets: [{maps_raw}]"
    return f"{match.group(1)}{front}{match.group(3)}{content[match.end() :]}"
