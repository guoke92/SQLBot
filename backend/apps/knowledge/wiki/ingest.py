"""Wiki semantic ingest v2 (plan Step D + E) — five-block context, evidence
backing (回证), zero-trust reconciliation.

每主题单元两次 LLM 调用（两步摄取形状不变）：

Step D — 上下文组装器（纯代码，五块）：
  ① E0 系统文档 doc_refs 全文（认知定位）
  ② E0.5 需求文档 wiki 候选页（ReqdocFilter 白名单过滤 → 词法检索命中，标
     ``reqdoc:<slug>`` 溯源）——业务含义/概念的补充与参考
  ③ E1 核心链路整文件（per_entry ring≤2 结构性类型，token 预算分批；
     ring3+ 仅列路径）——代码是准绳
  ④ E2/E3 底稿切片（db-catalog/profile/sample + 代码枚举 + 对账差异）
  ⑤ 既有 wiki 同主题页（增量锚点）

Step D1 — 语义分析（LLM）：reqdoc 主张走三通道（anchor 回证固化 /
prose_only 散文 / review 待裁决）；值/字段/表名字面只来自 [DB][代码]。
Step D2 — 页面生成（LLM）：FILE/REVIEW 块协议（v0 契约）。
Step E — 零信任对账（纯代码）：锚点 vs E2∪E3 底稿；回证行号真实性验证。
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml
from langchain_core.messages import HumanMessage, SystemMessage

from apps.knowledge.wiki.filters import CodeIgnore, ReqdocFilter

_FILE_RE = re.compile(r"---FILE:\s*([^\n]+?)\s*---\n([\s\S]*?)---END FILE---")
_REVIEW_RE = re.compile(
    r"---REVIEW:\s*([\w-]+)\s*\|\s*(.+?)\s*---\n([\s\S]*?)---END REVIEW---"
)
_STRUCTURAL = re.compile(
    r"(Service|Impl|Manager|Dao|Mapper|DO|Application|Controller|Provider|"
    r"Facade|Job|Listener|Consumer|Processor|Handler|Repository|Helper)$"
)
_TOKEN_BUDGET = 400_000  # 单批字符预算（≈10万 token；入口+应用层+service 全链语义优先）
_MIN_FILE_KEEP = 8_000  # 截断保留的最小头部（低于此值不值得截断，直接停）
_MAX_FILE_WHOLE = 100_000  # 超过此值的单文件按方法切片（保留签名+核心方法体）
# 链路类型优先级：入口/应用层全文 > service 实现 > DO/Mapper。同 ring 内
# 按类型权重消耗预算——146 个链路文件全量 3MB，预算必须聚焦高语义密度层。
_CHAIN_PRIORITY = (
    "Application",
    "Controller",
    "ServiceImpl",
    "Service",
    "Manager",
    "DomainService",
    "Dao",
    "Mapper",
    "DO",
)
_REQDOC_BUDGET = 6_000
_E0_BUDGET = 8_000

_ANALYSIS_SYSTEM = """你是业务系统代码语义分析师。输入分四层证据（分层标注）：
[DB 实测]（最强：结构/真实值分布）· [代码]（service/mapper 全文）·
[需求文档]（业务主张与流程表述，作为业务含义的补充与参考）· [系统文档]（认知参考）。
输出 JSON（不要 Markdown 围栏）：
{
  "field_semantics": [{"table","field","meaning","evidence":"db|code"}],
  "state_machines": [{"name","field",
     "states":[{"value","label","source":"code_enum|db_dist"}],
     "transitions":[{"from","event","to","evidence":"code_path:文件:行"}]}],
  "calibers": [{"name","predicate":"表.字段 = '值'","scope","evidence"}],
  "term_bridges": [{"term","aliases":[],"maps_to","also_confused_with":[],
     "adjudication":"boundary|synonym","boundary"}],
  "rules": [{"name","content","impact","field_targets":[],"evidence"}],
  "reqdoc_claims": [{"claim","code_status":"confirmed|refuted|uncovered",
     "code_evidence":"文件:行","action":"anchor|prose_only|review"}]
}
铁律：
1. 值/字段/表名字面只来自 [DB][代码] 层，[需求文档] 不能发明结构数据；
2. [需求文档] 的流程/规则表述：在 [代码] 中找到对应实现证据（分支/写值点/
   状态迁移）→ 固化为锚点块，evidence 记双源 "code_path:文件:行 + reqdoc:slug"
   （action=anchor）；表述与实现有出入 → 以代码为准落块、差异写散文说明
   （action=prose_only+差异）；代码无覆盖 → action=review，主张进 REVIEW 不落块；
3. 状态值优先 db 分布（代码枚举缺失时标 source:db_dist）；
4. 状态机 transitions 必须标注真实代码位置；拿不准的进 reqdoc_claims 或 review。"""

_GENERATION_SYSTEM = """你是 wiki 维护者。基于语义分析产出 v0 契约页面。每个页面一个
---FILE: <路径>.md --- ... ---END FILE--- 块（路径含子目录：tables/enums/concepts/
processes/calibers/rules/metrics/patterns，子目录=type）。frontmatter 必含
type/title/page_key/domain/status: draft/aliases/oid: 1/scope.databases: [<物理库名>]/
sources/contract_version: "0.1"。正文=散文（业务定位/## 需求背景/## 版本演进）+
```ground:<kind> 锚点块 + [[wikilinks]]。
规则：
1. 锚点块字段值逐字来自语义分析的 [DB][代码] 证据；禁止发明；
2. **每页每种 ground 块至多一个**（唯一键不重复）；混合主张/待确认内容写进
   散文或 REVIEW 块，不要另起 ground 块；
3. concept 页的锚点只进 frontmatter（maps_to/field_targets/adjudication/
   also_confused_with），**不写 ground 块**——concept 无锚点块（v0 §3.9）；
   块内容用 YAML（不要 JSON 大括号）；
4. reqdoc_claims action=anchor 的内容：锚点块 evidence 写双源
   "code_path:文件:行 + reqdoc:slug"；业务叙述写进 ## 需求背景；
5. action=uncovered 的主张只进 ## 版本演进 并页首标注 (document_claim，未证实)；
6. 语义不确定处输出 ---REVIEW: <type> | <title>--- ... ---END REVIEW--- 块。"""


def sanitize_llm_page(content: str) -> str:
    """LLM 输出清洗：剥 markdown 围栏/前置散文，定位 frontmatter 真实起点。"""
    text = content.replace("\r\n", "\n").strip()
    fence = re.search(r"```(?:markdown|md)\n([\s\S]*?)\n```", text)
    if fence and "---" in fence.group(1):
        text = fence.group(1).strip()
    start = text.find("\n---\n")
    if text.startswith("---\n") or text.startswith("--- "):
        return text
    if start >= 0:
        return text[start + 1 :]
    return text


def parse_file_blocks(text: str) -> list[tuple[str, str]]:
    return [
        (m.group(1).strip(), sanitize_llm_page(m.group(2)))
        for m in _FILE_RE.finditer(text)
    ]


def parse_review_blocks(text: str) -> list[dict[str, str]]:
    return [
        {"type": m.group(1), "title": m.group(2), "body": m.group(3).strip()}
        for m in _REVIEW_RE.finditer(text)
    ]


# ── 五块上下文组装器（纯代码） ───────────────────────────────────────────────


def _block_e0(repo: Path, doc_refs: list[str]) -> str:
    knowledge = repo / "lowcode-pplatform-common" / ".dev-standards" / "knowledge"
    parts: list[str] = []
    for ref in doc_refs[:4]:
        path = knowledge / ref
        if path.exists():
            parts.append(f"### {ref}\n{path.read_text()[:4000]}")
    if not parts:
        routing = knowledge / "service-routing-index.md"
        if routing.exists():
            parts.append(f"### service-routing-index.md\n{routing.read_text()[:4000]}")
    return "\n\n".join(parts)[:_E0_BUDGET]


def _block_reqdoc(
    reqdoc_root: Path | None, reqdoc_filter: ReqdocFilter, keywords: list[str]
) -> str:
    """E0.5：白名单过滤后的页面池上做词法检索，命中页正文引入（溯源 reqdoc:slug）。"""
    if reqdoc_root is None or not reqdoc_root.exists():
        return ""
    pages = reqdoc_filter.iter_pages(reqdoc_root)
    scored: list[tuple[float, str, str]] = []
    for path in pages:
        text = path.read_text(encoding="utf-8", errors="ignore")
        slug = path.stem
        score = sum(1.0 for kw in keywords if kw and kw in text) + (
            2.0 if any(kw and kw in slug for kw in keywords) else 0.0
        )
        if score > 0:
            # 剥 frontmatter，只留正文
            body = re.sub(r"\A---\n[\s\S]*?\n---\n", "", text).strip()
            scored.append((score, slug, body))
    scored.sort(key=lambda item: -item[0])
    parts = [
        f"### reqdoc:{slug}（需求文档主张，作为业务含义补充参考）\n{body[:2500]}"
        for _score, slug, body in scored[:6]
    ]
    return "\n\n".join(parts)[:_REQDOC_BUDGET]


def _block_code_chain(
    repo: Path, callgraph: dict[str, Any], entries: list[str], code_ignore: CodeIgnore
) -> str:
    """E1：入口 per_entry 分层可达合并，ring≤2 结构性文件整读，token 预算分批。

    预算按优先级消耗：入口类全文 > application 层 > service 层 > dao 层
    （ring 内再按文件名排序稳定分批）。首块给批号，后续批次由上层循环补齐。
    """
    per_entry = callgraph.get("per_entry") or {}
    file_to_name = {v["file"]: k for k, v in (callgraph.get("classes") or {}).items()}
    merged: dict[str, int] = {}
    for entry in entries:
        for file, depth in (per_entry.get(entry) or {}).items():
            merged[file] = min(merged.get(file, 99), depth)
    chain = sorted(
        (
            f
            for f, d in merged.items()
            if d <= 2 and _STRUCTURAL.search(file_to_name.get(f, ""))
        ),
        key=lambda f: (
            merged[f],
            _chain_priority(file_to_name.get(f, "")),
            f,
        ),
    )
    parts: list[str] = []
    budget = _TOKEN_BUDGET
    for rel in chain:
        if not code_ignore.should_scan(rel):
            continue
        path = repo / rel
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if len(text) > _MAX_FILE_WHOLE:
            text = _slice_java(text, _MAX_FILE_WHOLE)
        if len(text) > budget:
            if budget < _MIN_FILE_KEEP:
                break  # 预算剩余太少，连截断头部都无意义
            # 预算尽：截断保留头部（方法签名/类注释密度最高），标记截断
            parts.append(
                f"### {rel} (ring{merged[rel]}, 截断)\n```java\n{text[:budget]}\n```"
            )
            budget = 0
            break
        budget -= len(text)
        parts.append(f"### {rel} (ring{merged[rel]})\n```java\n{text}\n```")
        if budget <= 0:
            break
    included = {
        p.split(" (ring")[0].removeprefix("### ") for p in parts if p.startswith("### ")
    }
    remaining = [f for f, _d in merged.items() if f not in included][:120]
    outer = [f for f, d in merged.items() if d > 2][:80]
    if remaining or outer:
        parts.append(
            "### 未全文给出的链路文件（按需参考）\n"
            + "\n".join(sorted(set(remaining) | set(outer)))
        )
    return "\n\n".join(parts)


def _chain_priority(class_name: str) -> int:
    """越小越先入上下文：应用层 > service 实现 > dao/do。"""
    for index, suffix in enumerate(_CHAIN_PRIORITY):
        if class_name.endswith(suffix):
            return index
    return len(_CHAIN_PRIORITY)


_METHOD_SIG = re.compile(
    r"^\s{4}(?:@\w+(?:\([^)]*\))?\s+)*(?:public|protected|private)\s+[^\n=;{]+\(",
    re.M,
)


def _slice_java(text: str, limit: int) -> str:
    """超长 Java 文件切片：类头（注释/字段/签名区）+ 逐个完整方法体，到预算止。

    方法边界用花括号配平（编译期结构，不靠正则猜语义）；保不住完整方法时
    保留头部——签名与字段声明是语义密度最高的部分。"""
    if len(text) <= limit:
        return text
    head_end = text.find("class ")
    head_end = (
        text.find("{", head_end) + 1 if head_end >= 0 else min(len(text), limit // 4)
    )
    out = [text[:head_end]]
    used = head_end
    pos = head_end
    lines = text[pos:]
    for m in _METHOD_SIG.finditer(lines):
        start = m.start()
        # 方法体花括号配平
        depth = 0
        i = lines.find("{", m.end())
        if i < 0:
            continue
        j = i
        while j < len(lines):
            if lines[j] == "{":
                depth += 1
            elif lines[j] == "}":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        method = lines[start : j + 1]
        if used + len(method) > limit:
            break
        out.append(method)
        used += len(method)
    return "\n    // …（方法切片，略）\n".join(out) if len(out) > 1 else text[:limit]


def _block_substrate(substrate_dir: Path, db_dir: Path, tables: list[str]) -> str:
    """E2/E3：该主题表的 db 结构+分布+样本首行 + 代码枚举 + 对账差异。"""
    parts: list[str] = []
    db_catalog = db_dir / "db-catalog.yaml"
    db_profile = db_dir / "db-profile.yaml"
    if db_catalog.exists():
        data = yaml.safe_load(db_catalog.read_text()) or {}
        sel = {t: data["tables"][t] for t in tables if t in (data.get("tables") or {})}
        if sel:
            parts.append(
                f"### [DB 实测] 表结构\n{yaml.safe_dump(sel, allow_unicode=True, sort_keys=False)[:9000]}"
            )
    if db_profile.exists():
        data = yaml.safe_load(db_profile.read_text()) or {}
        sel = {t: data["tables"][t] for t in tables if t in (data.get("tables") or {})}
        if sel:
            parts.append(
                f"### [DB 实测] 值分布（真实枚举+权重）\n{yaml.safe_dump(sel, allow_unicode=True, sort_keys=False)[:6000]}"
            )
    enums_path = substrate_dir / "extract-enums.yaml"
    if enums_path.exists():
        enums = yaml.safe_load(enums_path.read_text()) or {}
        rows = [
            e
            for e in enums.get("enums") or []
            if isinstance(e, dict)
            and any(t in str(e.get("field", "")) or t in str(e) for t in tables)
        ]
        if rows:
            parts.append(
                f"### [代码] 枚举基线\n{yaml.safe_dump(rows, allow_unicode=True, sort_keys=False)[:5000]}"
            )
    reconcile = substrate_dir / "tmp" / "db-enum-reconcile.yaml"
    if reconcile.exists():
        data = yaml.safe_load(reconcile.read_text()) or {}
        rows = [m for m in data.get("mismatches") or [] if m.get("table") in tables]
        if rows:
            parts.append(
                f"### [对账] db 分布超出代码枚举的值（真实存在，代码未声明）\n{yaml.safe_dump(rows, allow_unicode=True, sort_keys=False)[:3000]}"
            )
    return "\n\n".join(parts)


def assemble_context(
    *,
    repo: Path,
    substrate_dir: Path,
    db_dir: Path,
    reqdoc_root: Path | None,
    topic: str,
    entries: list[str],
    tables: list[str],
    doc_refs: list[str] | None = None,
) -> str:
    callgraph = _load_yaml(substrate_dir / "callgraph.yaml")
    code_ignore = CodeIgnore.load(substrate_dir / "tmp" / "code-ignore.yaml")
    reqdoc_filter = ReqdocFilter.load(substrate_dir / "tmp" / "reqdoc-filter.yaml")
    keywords = [topic, *tables[:8]]
    blocks = [
        f"# 主题：{topic}",
        "## [系统文档]（认知参考，可能滞后；业务描述仅作补充）",
        _block_e0(repo, doc_refs or []),
        "## [需求文档]（业务含义补充；结构数据不可来源于此层）",
        _block_reqdoc(reqdoc_root, reqdoc_filter, keywords),
        "## [代码]（service/mapper 链路全文——语义与结构的准绳）",
        _block_code_chain(repo, callgraph, entries, code_ignore),
        "## [DB 实测] 与 [代码] 底稿",
        _block_substrate(substrate_dir, db_dir, tables),
    ]
    return "\n\n".join(b for b in blocks if b.strip())


def _load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text()) or {}


# ── Step D 主流程 ────────────────────────────────────────────────────────────


def semantic_ingest_v2(
    llm: Any,
    *,
    repo: Path,
    substrate_dir: Path,
    db_dir: Path,
    reqdoc_root: Path | None,
    unit: dict[str, Any],
) -> dict[str, Any]:
    """两步摄取一个主题单元。Returns {analysis, pages, reviews}."""
    topic = unit["topic"]
    context = assemble_context(
        repo=repo,
        substrate_dir=substrate_dir,
        db_dir=db_dir,
        reqdoc_root=reqdoc_root,
        topic=topic,
        entries=unit.get("entries") or [],
        tables=unit.get("tables") or [],
        doc_refs=unit.get("doc_refs"),
    )
    step1 = llm.invoke(
        [
            SystemMessage(content=_ANALYSIS_SYSTEM),
            HumanMessage(content=context),
        ]
    )
    analysis_text = (
        step1.content if isinstance(step1.content, str) else str(step1.content)
    )
    analysis = _parse_json(analysis_text)

    gen_human = (
        f"## 语义分析（唯一事实来源）\n{analysis_text[:16000]}\n\n"
        f"## 输出要求\n为主题「{topic}」生成页面：涉及表各一个 table 页、"
        f"每个状态机一个 process 页、每个口径一个 caliber 页、"
        f"每个术语桥一个 concept 页、每条规则一个 rule 页（只产出分析中有证据支撑的）。\n"
        f"每个页面必须包在 ---FILE: <目录>/<slug>.md --- 与 ---END FILE--- 之间；"
        f"目录必须是 tables/enums/concepts/processes/calibers/rules 之一。"
        f"禁止只输出 REVIEW 而不产出 FILE。"
    )
    step2 = llm.invoke(
        [
            SystemMessage(content=_GENERATION_SYSTEM),
            HumanMessage(content=gen_human),
        ]
    )
    generation = step2.content if isinstance(step2.content, str) else str(step2.content)
    pages = parse_file_blocks(generation)
    if not pages:
        # 模型偶发只吐 REVIEW / 用错围栏：重试一次，避免整主题空跑仍写 _done
        retry = llm.invoke(
            [
                SystemMessage(content=_GENERATION_SYSTEM),
                HumanMessage(
                    content=(
                        gen_human
                        + "\n\n上次输出没有可解析的 ---FILE: ... ---END FILE--- 块。"
                        "请仅按该协议重新输出全部页面，首字符必须是 '-'。"
                    )
                ),
            ]
        )
        generation = (
            retry.content if isinstance(retry.content, str) else str(retry.content)
        )
        pages = parse_file_blocks(generation)
    return {
        "analysis": analysis,
        "pages": pages,
        "reviews": parse_review_blocks(generation),
        "generation": generation,
    }


def _parse_json(text: str) -> dict[str, Any]:
    nested = re.search(r"\{[\s\S]*\}", text)
    return yaml.safe_load(nested.group(0)) if nested else {}


# ── Step E：零信任对账（纯代码） ─────────────────────────────────────────────


def reconcile_page(
    page_content: str,
    *,
    db_dir: Path,
    repo: Path,
    page_key: str | None = None,
    belong: str | None = None,
) -> list[dict[str, str]]:
    """锚点块 vs E2∪E3 底稿对账 + 回证行号验证。返回 findings（丢块决策在上层）。

    对账码表（单一权威，admin 门禁与 REVIEW 消费同此清单）：
    PAGE_CONTRACT_FAILED / TABLE_NOT_IN_DB / FIELD_NOT_IN_DB / FIELD_MALFORMED /
    ENUM_VALUE_NOT_IN_DB / EVIDENCE_FILE_MISSING / EVIDENCE_LINE_OUT_OF_RANGE
    ——全部视为 error 级（丢块依据）。

    findings[0..n] 带可选 ``anchor`` 键：定位出错块（kind+块内键），上层据此
    真丢块（而非只记录）。整页级 finding（PAGE_CONTRACT_FAILED）无 anchor。
    ``page_key`` 传文件名 stem 以程序盖章——否则 LLM 把路径写进 frontmatter
    page_key（如 'concepts/operator'）会被 slug 校验整页误拒。"""
    from apps.knowledge.wiki.contract import compact_block, parse_page

    findings: list[dict[str, str]] = []
    try:
        page = parse_page(
            page_content,
            page_key=page_key,
            override_page_key=True,
            belong=belong,
        )
    except Exception as exc:  # noqa: BLE001 — 契约失败整页拒绝并报告
        return [{"code": "PAGE_CONTRACT_FAILED", "message": str(exc)[:200]}]

    def _anchor(block) -> str:
        key = str(
            block.data.get("table")
            or block.data.get("enum")
            or block.data.get("process")
            or block.data.get("caliber")
            or block.data.get("metric")
            or block.data.get("rule")
            or block.data.get("pattern")
            or ""
        )
        return f"{block.kind}:{key}" if key else block.kind

    db_tables: dict[str, Any] = {}
    if (db_dir / "db-catalog.yaml").exists():
        db_tables = (
            yaml.safe_load((db_dir / "db-catalog.yaml").read_text()) or {}
        ).get("tables") or {}
    for block in page.ground_blocks:
        data = compact_block(block.data)
        if block.kind == "table":
            table = data.get("table") or ""
            if table and table not in db_tables:
                findings.append(
                    {
                        "code": "TABLE_NOT_IN_DB",
                        "anchor": _anchor(block),
                        "message": f"{table} 不在 db catalog",
                    }
                )
                continue
            columns = set((db_tables.get(table) or {}).get("columns") or {})
            for f in data.get("fields") or []:
                if not isinstance(f, dict):
                    findings.append(
                        {
                            "code": "FIELD_MALFORMED",
                            "anchor": _anchor(block),
                            "message": f"{table}: 字段行非映射 {str(f)[:40]}",
                        }
                    )
                    continue
                name = str(f.get("name") or "")
                if name and columns and name not in columns:
                    findings.append(
                        {
                            "code": "FIELD_NOT_IN_DB",
                            "anchor": _anchor(block),
                            "message": f"{table}.{name}",
                        }
                    )
        elif block.kind == "enum":
            values = set((data.get("values") or {}).keys())
            profile_path = db_dir / "db-profile.yaml"
            if profile_path.exists():
                profile = yaml.safe_load(profile_path.read_text()) or {}
                for field_ref in data.get("fields") or []:
                    table_name, _, col = str(field_ref).partition(".")
                    dist = (
                        (profile.get("tables") or {})
                        .get(table_name, {})
                        .get("column_stats", {})
                        .get(col, {})
                        .get("values")
                    )
                    if dist is not None:
                        outside = set(map(str, values)) - set(map(str, dist)) - {""}
                        if outside:
                            findings.append(
                                {
                                    "code": "ENUM_VALUE_NOT_IN_DB",
                                    "anchor": _anchor(block),
                                    "message": f"{field_ref}: {sorted(outside)[:5]}",
                                }
                            )
        # 回证行号真实性：evidence 里的 code_path:文件:行 必须可打开且行存在
        evidence = str(data.get("evidence") or "")
        m = re.search(r"code_path:([^:]+):(\d+)", evidence)
        if m:
            src = repo / m.group(1)
            if not src.exists():
                findings.append(
                    {
                        "code": "EVIDENCE_FILE_MISSING",
                        "anchor": _anchor(block),
                        "message": m.group(1),
                    }
                )
            else:
                lines = src.read_text(encoding="utf-8", errors="ignore").splitlines()
                if int(m.group(2)) > len(lines):
                    findings.append(
                        {
                            "code": "EVIDENCE_LINE_OUT_OF_RANGE",
                            "anchor": _anchor(block),
                            "message": evidence[:80],
                        }
                    )
    return findings
