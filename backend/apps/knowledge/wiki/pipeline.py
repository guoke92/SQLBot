"""Wiki extraction pipeline entry (plan Step A / D / E / F).

提取面 v2 的编排器：Step A 提取计划（LLM×1，主题单元聚类 + 双源过滤清单
建议）→ Step D 主题穿透（wiki.ingest，五块上下文 + 回证提示词）→
Step E 零信任对账 → Step F 写入 ``wiki-pages/`` 子目录 + ``_index.md``。

计划单元是**工作分批单位**，不是落库概念：最终页面按业务术语/场景/概念
自然拆分（同一主题可能产 3-10 页）。单元聚类的认知来自 E0 系统文档
（架构/模块/入口定位），结构事实来自 E1 调用图——文档是入口，代码是准绳。

Usage::

    backend/venv/bin/python -m apps.knowledge.wiki.pipeline plan \
        --repo ~/IdeaProjects/pplatform-web \
        --substrate docs/wiki-knowledge/pplatform/substrate
    backend/venv/bin/python -m apps.knowledge.wiki.pipeline run \
        --repo ... --substrate ... --topic 企业建档
    backend/venv/bin/python -m apps.knowledge.wiki.pipeline update ...
"""

from __future__ import annotations

import argparse
import asyncio
import json
import re
from pathlib import Path
from typing import Any

import yaml

# ── Step A：提取计划 ─────────────────────────────────────────────────────────

_PLAN_SYSTEM = """你是系统架构分析师。基于系统文档（认知入口，可能滞后）与调用图入口
清单（代码事实），产出 wiki 页面提取计划。输出 JSON（不要 Markdown 围栏）：
{
  "plan_units": [
    {"topic": "企业建档", "entries": ["CustCompanyInfoController", "..."],
     "tables": ["cust_company_info"], "duty": "一句话职责",
     "doc_refs": ["business/客户管理平台业务规则文档.md"]}
  ],
  "excluded_entries": [{"class": "ApiMockController", "reason": "Mock 无业务语义"}],
  "exclude_globs": ["*/dto/*"],
  "reqdoc_include": ["concepts/**", "entities/*表.md"],
  "system_summary": "≤300字系统架构总述"
}
规则：
1. 入口覆盖率 100%：每个入口类必须 ∈ 某个 plan_unit.entries 或 excluded_entries，二选一；
2. 表归属以调用图 tables→entry_points 为准（输入已给），休眠表归入最相关单元并标 dormant；
3. 类名/表名只能来自输入清单，禁止发明；
4. topic 用业务术语命名（如"企业建档""CA证书收费"），不用技术分层词（controller/service）；
5. doc_refs 只列与该主题相关的系统文档路径；
6. exclude_globs 是你建议新增的源码侧忽略项（DTO 样板/纯技术包），
   reqdoc_include 是需求 wiki 侧的页面白名单建议（排除人物/部门/公司页）。"""

_REASK_TEMPLATE = """你上一轮的计划有缺口，请补全后重新输出完整 JSON：
{gaps}
原输入不变，规则不变。注意：输出必须仍是覆盖全部入口的完整计划，不要只输出差量。"""


def _load_callgraph(substrate_dir: Path) -> dict[str, Any]:
    return yaml.safe_load((substrate_dir / "callgraph.yaml").read_text())


def _load_db_tables(substrate_dir: Path, db_dir: Path | None) -> set[str]:
    """db 优先（存在性真值），缺 db 底稿时降级代码 catalog。

    代码有 DO 但库里无表的死代码（table-reconcile code_only）不计入——
    E2 权威序：库里不存在即不建页。"""
    if db_dir and (db_dir / "db-catalog.yaml").exists():
        data = yaml.safe_load((db_dir / "db-catalog.yaml").read_text())
        return set(data.get("tables") or {})
    code = yaml.safe_load((substrate_dir / "extract-catalog.yaml").read_text())
    tables = code.get("tables") or {}
    return set(
        tables.keys() if isinstance(tables, dict) else {t["table"] for t in tables}
    )


def _e0_context(repo: Path) -> str:
    """E0 系统文档：服务路由索引（截取路由表核心）+ 各知识文档标题清单。"""
    knowledge = repo / "lowcode-pplatform-common" / ".dev-standards" / "knowledge"
    parts: list[str] = []
    routing = knowledge / "service-routing-index.md"
    if routing.exists():
        text = routing.read_text()
        # 路由表是认知核心；服务全景表次之；其余截断
        parts.append(f"## 服务路由索引（节选）\n{text[:6000]}")
    listing: list[str] = []
    for sub in ("business", "codemap", "service"):
        d = knowledge / sub
        if d.is_dir():
            listing.extend(f"{sub}/{p.name}" for p in sorted(d.glob("*.md")))
    if listing:
        parts.append("## 知识文档清单（doc_refs 从这里选）\n" + "\n".join(listing))
    return "\n\n".join(parts)


def _entry_context(callgraph: dict[str, Any]) -> str:
    """紧凑入口上下文。正向（入口→表）会让每个入口携带全部可达表（约 50
    张），325 入口展开 175k 字符——实际信息量是"表 ← 哪些入口可达"的反向
    索引。改为：入口一行（类名 + 可达表数）+ 表→入口映射（每表 ≤6 入口）。"""
    entries = callgraph.get("entry_points") or []
    tables = callgraph.get("tables") or {}
    by_table: dict[str, list[str]] = {}
    for table, info in sorted(tables.items()):
        eps = sorted(info.get("entry_points") or [])
        by_table[table] = eps
    lines = [
        f"## 入口清单（{len(entries)} 类，按名排序）",
        ", ".join(sorted(entries)),
        "",
        "## 表→可达入口（每表最多列 6 个入口；空 = 休眠）",
    ]
    for table, eps in by_table.items():
        shown = ", ".join(eps[:6]) or "(dormant)"
        more = f" …+{len(eps) - 6}" if len(eps) > 6 else ""
        lines.append(f"{table}: {shown}{more}")
    return "\n".join(lines)


def _parse_llm_json(text: str) -> dict[str, Any]:
    nested = re.search(r"\{[\s\S]*\}", text)
    if not nested:
        raise ValueError("LLM 输出无 JSON 对象")
    return yaml.safe_load(nested.group(0))


def validate_plan(
    plan: dict[str, Any], *, callgraph: dict[str, Any], all_tables: set[str]
) -> dict[str, list[str]]:
    """确定性校验：入口覆盖率 100% + 表归属完整。返回缺口字典（空=通过）。

    表名允许带 "(dormant)" 标记（提示词要求休眠表显式标注）——校验前剥离。"""

    def _clean(name: str) -> str:
        return re.sub(r"\s*\(dormant\)\s*$", "", str(name).strip())

    entries = set(callgraph.get("entry_points") or [])
    planned: set[str] = set()
    for unit in plan.get("plan_units") or []:
        planned.update(unit.get("entries") or [])
    for exc in plan.get("excluded_entries") or []:
        planned.add(exc.get("class") or "")
    planned.discard("")
    gaps: dict[str, list[str]] = {}
    if missing_entries := sorted(entries - planned):
        gaps["missing_entries"] = missing_entries
    unknown = sorted(planned - entries)
    if unknown:
        gaps["unknown_entries"] = unknown

    covered_tables: set[str] = set()
    for unit in plan.get("plan_units") or []:
        covered_tables.update(_clean(t) for t in (unit.get("tables") or []))
    if missing_tables := sorted(all_tables - covered_tables):
        gaps["missing_tables"] = missing_tables
    # 计划提及但库/代码都没有的表是硬错误；代码有库无（死代码）可容忍——
    # LLM 拿到的入口→表映射来自调用图（含死代码表），强制剔除反而逼它撒谎。
    code_tables = _code_tables(callgraph)
    fabricated = sorted(covered_tables - all_tables - code_tables)
    if fabricated:
        gaps["unknown_tables"] = fabricated
    return gaps


def _code_tables(callgraph: dict[str, Any]) -> set[str]:
    return set(callgraph.get("tables") or {})


def make_plan(
    llm: Any, *, repo: Path, substrate_dir: Path, db_dir: Path | None
) -> dict[str, Any]:
    """Step A：一次 LLM 调用产提取计划；缺口重问一次；仍缺则中断留给人工。"""
    from langchain_core.messages import HumanMessage, SystemMessage

    callgraph = _load_callgraph(substrate_dir)
    all_tables = _load_db_tables(substrate_dir, db_dir)
    context = (
        f"{_e0_context(repo)}\n\n{_entry_context(callgraph)}\n\n"
        f"## 全部表（{len(all_tables)}）\n{', '.join(sorted(all_tables))}"
    )
    response = llm.invoke(
        [
            SystemMessage(content=_PLAN_SYSTEM),
            HumanMessage(content=context),
        ]
    )
    text = (
        response.content if isinstance(response.content, str) else str(response.content)
    )
    plan = _parse_llm_json(text)
    gaps = validate_plan(plan, callgraph=callgraph, all_tables=all_tables)
    if gaps:
        response = llm.invoke(
            [
                SystemMessage(content=_PLAN_SYSTEM),
                HumanMessage(
                    content=f"{context}\n\n{_REASK_TEMPLATE.format(gaps=json.dumps(gaps, ensure_ascii=False, default=str)[:4000])}"
                ),
            ]
        )
        text = (
            response.content
            if isinstance(response.content, str)
            else str(response.content)
        )
        plan = _parse_llm_json(text)
        gaps = validate_plan(plan, callgraph=callgraph, all_tables=all_tables)
    if gaps:
        raise SystemExit(
            f"提取计划仍有缺口（人工补 page-plan.yaml 后重跑）:\n{json.dumps(gaps, ensure_ascii=False, default=str)[:3000]}"
        )

    out = substrate_dir / "tmp" / "page-plan.yaml"
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "1.0",
        "system_summary": plan.get("system_summary", ""),
        "plan_units": plan.get("plan_units") or [],
        "excluded_entries": plan.get("excluded_entries") or [],
        "ignore_suggestions": {
            "exclude_globs": plan.get("exclude_globs") or [],
            "reqdoc_include": plan.get("reqdoc_include") or [],
        },
    }
    out.write_text(yaml.safe_dump(payload, allow_unicode=True, sort_keys=False))
    print(f"计划单元 {len(payload['plan_units'])} 个 → {out}")
    for unit in payload["plan_units"]:
        print(
            f"  {unit['topic']}: entries={len(unit.get('entries') or [])} tables={len(unit.get('tables') or [])}"
        )
    return payload


# ── Step D/E/F：按单元穿透 + 对账 + 写入 ────────────────────────────────────


def _normalize_page(content: str) -> str:
    """Step F 归一化（纯代码）：LLM 把 concept 锚点写进 ground:concept 块而
    非 frontmatter（两种写法都符合提示词直觉）——把块内 anchors 提升到
    frontmatter，保证 lint/召回看到的结构边一致。"""
    m = re.search(r"```ground:concept\n([\s\S]*?)\n```", content)
    if not m or "field_targets:" in content.split("---")[1]:
        return content
    try:
        block = yaml.safe_load(m.group(1))
    except yaml.YAMLError:
        return content
    if not isinstance(block, dict):
        return content
    inject = ""
    if (
        block.get("maps_to")
        and "maps_to:" not in content[: content.index("\n---\n", 3)]
    ):
        inject += f"maps_to: {block['maps_to']}\n"
    targets = block.get("field_targets") or []
    if targets:
        inject += "field_targets: [" + ", ".join(str(t) for t in targets) + "]\n"
    adjudication = block.get("adjudication")
    if adjudication:
        inject += f"adjudication: {adjudication}\n"
    confused = block.get("also_confused_with") or []
    if confused:
        inject += "also_confused_with: [" + ", ".join(str(c) for c in confused) + "]\n"
    if not inject:
        return content
    # 插在 frontmatter 结束标记前
    head, _, tail = content.partition("\n---\n")
    return f"{head}\n{inject}---\n{tail}"


def merge_same_key_page(baseline: str, semantic: str) -> str:
    """v0 §5.3 同 page_key 确定性合并（基线页 + 语义页）。

    块层不走 LLM：table.fields 以基线（db 全量真值）为底，语义字段的 desc
    并入（键经 contract.compact_block 统一归一，磁盘形态与基线一致）；
    语义独有字段追加（对账层已校验存在性）；散文保留语义页（业务叙述），
    frontmatter 保留语义页但 status 归 draft（合并产物需重审）。
    """
    from apps.knowledge.wiki.contract import compact_block, parse_page

    try:
        base = parse_page(baseline)
        sem = parse_page(semantic)
    except Exception:  # noqa: BLE001 — 解析失败：语义页独写（调用方保证存在基线才进来）
        return semantic

    base_table = next((b for b in base.ground_blocks if b.kind == "table"), None)
    sem_table = next((b for b in sem.ground_blocks if b.kind == "table"), None)
    if base_table is None or sem_table is None:
        return semantic

    base_fields = {
        f["name"]: f
        for f in (compact_block(x) for x in (base_table.data.get("fields") or []))
        if isinstance(f, dict) and f.get("name")
    }
    sem_fields = {
        f["name"]: f
        for f in (compact_block(x) for x in (sem_table.data.get("fields") or []))
        if isinstance(f, dict) and f.get("name")
    }

    merged: list[dict] = []
    for name, field in base_fields.items():  # 基线顺序为底
        enriched = dict(field)
        sem_desc = sem_fields.get(name, {}).get("desc")
        if sem_desc and not enriched.get("desc"):
            enriched["desc"] = sem_desc
        merged.append(enriched)
    extras = [f for n, f in sem_fields.items() if n not in base_fields]
    merged.extend(extras)  # 语义独有字段：对账层已校验存在性（FIELD_NOT_IN_DB）

    def _field_yaml(field: dict) -> list[str]:
        lines = [f"  - name: {field['name']}"]
        if field.get("type"):
            lines.append(f"    type: {field['type']}")
        if field.get("desc"):
            lines.append(f"    desc: {str(field['desc']).strip()}")
        if field.get("dict"):
            lines.append(f"    dict: {field['dict']}")
        if field.get("roles"):
            lines.append(f"    roles: [{', '.join(field['roles'])}]")
        return lines

    fence_lines = [
        "```ground:table",
        f"table: {base_table.data.get('table', base.page_key)}",
    ]
    if base_table.data.get("database"):
        fence_lines.append(f"database: {base_table.data['database']}")
    if base_table.data.get("desc"):
        fence_lines.append(f"desc: {base_table.data['desc']}")
    if base_table.data.get("inactive"):
        fence_lines.append("inactive: true")
    fence_lines.append("fields:")
    for field in merged:
        fence_lines.extend(_field_yaml(field))
    fence_lines.append("```")
    merged_fence = "\n".join(fence_lines)

    # 语义页正文里的 table 块替换为合并块
    new_body = re.sub(
        r"```ground:table\n[\s\S]*?\n```",
        merged_fence.replace("\\", "\\\\"),
        sem.body,
        count=1,
    )
    # frontmatter：语义页 + status 归 draft（合并产物需重审）
    head = semantic.split("\n---\n")[0]
    head = re.sub(r"status: \w+", "status: draft", head)
    return f"{head}\n---\n\n{new_body}"


def _drop_anchored_blocks(content: str, findings: list[dict[str, str]]) -> str:
    """按 anchor（kind:键）从页面删除对应 ground 围栏块（零信任真丢块）。
    仅精确匹配 kind+键；键取不到时退化为 kind 匹配（LLM 块无键属结构性失败，
    整 kind 丢弃是保守正确的）。"""
    exact: set[str] = set()
    kinds: set[str] = set()
    for f in findings:
        anchor = str(f.get("anchor") or "")
        kind, _, key = anchor.partition(":")
        if key:
            exact.add(anchor)
        else:
            kinds.add(kind)

    def _keep(match: re.Match) -> str:
        kind = match.group(1)
        body = match.group(2)
        key = ""
        for line in body.splitlines():
            m = re.match(
                r"\s*(table|enum|process|caliber|metric|rule|pattern):\s*(.+)", line
            )
            if m:
                key = m.group(2).strip().strip('"').strip("'")
                break
        anchor = f"{kind}:{key}"
        if anchor in exact or (not key and kind in kinds):
            return ""
        return match.group(0)

    return re.sub(r"```ground:(\w+)\n([\s\S]*?)\n```", _keep, content)


def _drop_duplicate_blocks(content: str) -> str:
    """重复 ground 块：保留首个，删后续同 kind 同键块。"""
    seen: set[tuple[str, str]] = set()

    def _keep(match: re.Match) -> str:
        kind = match.group(1)
        body = match.group(2)
        key = ""
        for line in body.splitlines():
            m = re.match(
                r"\s*(table|enum|process|caliber|metric|rule|pattern):\s*(.+)", line
            )
            if m:
                key = m.group(2).strip().strip('"').strip("'")
                break
        token = (kind, key)
        if token in seen:
            return ""
        seen.add(token)
        return match.group(0)

    return re.sub(r"```ground:(\w+)\n([\s\S]*?)\n```", _keep, content)


def run_unit(
    llm: Any,
    *,
    repo: Path,
    substrate_dir: Path,
    db_dir: Path,
    reqdoc_root: Path | None,
    out_dir: Path,
    unit: dict[str, Any],
) -> dict[str, int]:
    """跑一个计划单元：两步 LLM → Step E 零信任对账（真丢块）→ Step F 写入。

    丢块规则（零信任落地，非仅记录）：
    - 整页级 finding（PAGE_CONTRACT_FAILED）→ 整页拒绝；
    - 块级 finding（带 anchor=kind:键）→ 从页面删除该 ground 围栏块，散文保留；
    - 全部 findings 落 _reconcile_*.yaml 审计。"""
    import hashlib

    from apps.knowledge.wiki.contract import lint_page, parse_page
    from apps.knowledge.wiki.ingest import reconcile_page, semantic_ingest_v2

    result = semantic_ingest_v2(
        llm,
        repo=repo,
        substrate_dir=substrate_dir,
        db_dir=db_dir,
        reqdoc_root=reqdoc_root,
        unit=unit,
    )
    topic_dir = out_dir / ".runs" / unit["topic"]
    topic_dir.mkdir(parents=True, exist_ok=True)
    accepted = rejected = reviews = dropped_blocks = 0
    for fname, content in result["pages"]:
        content = _normalize_page(content)  # concept 锚点提升（纯代码归一化）

        rel = Path(fname)
        belong = rel.parts[0] if rel.parts and rel.parts[0] in {
            "tables",
            "enums",
            "concepts",
            "processes",
            "calibers",
            "rules",
            "metrics",
            "patterns",
            "queries",
            "sources",
            "scenarios",
        } else None
        findings = reconcile_page(
            content,
            db_dir=db_dir,
            repo=repo,
            page_key=rel.stem,
            belong=belong,
        )
        page_level = [f for f in findings if "anchor" not in f]
        block_findings = [f for f in findings if "anchor" in f]
        if page_level:
            rejected += 1
            slug = hashlib.sha1(fname.encode()).hexdigest()[:8]
            (topic_dir / f"_reconcile_{slug}.yaml").write_text(
                yaml.safe_dump(findings, allow_unicode=True)
            )
            print(f"  REJECT {fname}: {page_level[0]['code']}", flush=True)
            continue
        if block_findings:
            content = _drop_anchored_blocks(content, block_findings)
            dropped_blocks += len(block_findings)
            slug = hashlib.sha1(fname.encode()).hexdigest()[:8]
            (topic_dir / f"_reconcile_{slug}.yaml").write_text(
                yaml.safe_dump(block_findings, allow_unicode=True)
            )
        try:
            page = parse_page(content, page_key=Path(fname).stem, belong=belong)
        except Exception as exc:  # noqa: BLE001 — 丢块后契约仍失败：整页拒绝
            rejected += 1
            print(f"  REJECT {fname}: {str(exc)[:100]}", flush=True)
            continue
        # 契约结构检查（重复块）：零信任同权丢块
        known = {Path(f).stem for f, _ in result["pages"]} | {
            p.stem
            for p in out_dir.rglob("*.md")
            if not p.name.startswith("_") and ".runs" not in p.parts
        }
        dup = [
            f
            for f in lint_page(page, known_keys=known)
            if f.code == "DUPLICATE_GROUND_BLOCK"
        ]
        if dup:
            content = _drop_duplicate_blocks(content)
            dropped_blocks += len(dup)
            page = parse_page(content, page_key=Path(fname).stem, belong=belong)
            slug = hashlib.sha1(f"{fname}:dup".encode()).hexdigest()[:8]
            (topic_dir / f"_reconcile_{slug}.yaml").write_text(
                yaml.safe_dump(
                    [{"code": f.code, "message": f.message} for f in dup],
                    allow_unicode=True,
                )
            )
        # 同 page_key 已有页（基线 table/enum 页）→ v0 §5.3 确定性块合并，
        # 绝不整页覆盖：基线 fields/values 是存在性真值（51 字段全量），
        # 语义页贡献 desc/散文——覆盖会丢全量字段清单（G1 复发）。
        target = out_dir / fname
        if target.exists():
            content = merge_same_key_page(target.read_text(), content)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        accepted += 1
    for review in result["reviews"]:
        slug = hashlib.sha1(str(review.get("title", "")).encode()).hexdigest()[:8]
        (topic_dir / f"_review_{slug}.yaml").write_text(
            yaml.safe_dump(review, allow_unicode=True)
        )
        reviews += 1
    print(
        f"[{unit['topic']}] 页面 接受{accepted}/拒绝{rejected} | 对账丢块 {dropped_blocks} | REVIEW {reviews}",
        flush=True,
    )
    return {"accepted": accepted, "rejected": rejected, "reviews": reviews}


def run_plan(
    llm: Any,
    *,
    repo: Path,
    substrate_dir: Path,
    db_dir: Path,
    reqdoc_root: Path | None,
    out_dir: Path,
    only: list[str] | None,
) -> None:
    """逐单元跑 Step D-F；断点续跑（.runs/<topic>/_done 标记）。"""
    plan_path = substrate_dir / "tmp" / "page-plan.yaml"
    if not plan_path.exists():
        raise SystemExit("page-plan.yaml 不存在——先跑 plan 子命令")
    plan = yaml.safe_load(plan_path.read_text()) or {}
    units = plan.get("plan_units") or []
    if only:
        units = [u for u in units if u.get("topic") in only]
    todo = [
        u
        for u in units
        if not (out_dir / ".runs" / u["topic"] / "_done").exists()
        or (only and u["topic"] in only)
    ]
    print(f"待穿透单元 {len(todo)}/{len(units)}", flush=True)
    for unit in todo:
        run_unit(
            llm,
            repo=repo,
            substrate_dir=substrate_dir,
            db_dir=db_dir,
            reqdoc_root=reqdoc_root,
            out_dir=out_dir,
            unit=unit,
        )
        (out_dir / ".runs" / unit["topic"] / "_done").write_text("done")
    from apps.knowledge.wiki.baseline import rebuild_index

    rebuild_index(out_dir)


# ── 命令面 ───────────────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    plan_p = sub.add_parser("plan", help="Step A：生成提取计划")
    for p in (plan_p,):
        p.add_argument("--repo", required=True)
        p.add_argument("--substrate", required=True)
        p.add_argument("--db-dir", default="")

    run_p = sub.add_parser("run", help="Step D/E/F：按单元穿透（断点续跑）")
    run_p.add_argument("--repo", required=True)
    run_p.add_argument("--substrate", required=True)
    run_p.add_argument("--db-dir", default="")
    run_p.add_argument("--out", default="../docs/wiki-knowledge/pplatform/wiki-pages")
    run_p.add_argument("--reqdoc-root", default="")
    run_p.add_argument("--only", default="", help="逗号分隔 topic；强制重跑")

    args = parser.parse_args()
    from apps.ai_model.model_factory import LLMConfig, LLMFactory, OpenAILLM

    config = asyncio.run(_default_config())
    base = LLMFactory.create_llm(config)
    # 提取管线单次输出大（计划 JSON/整页 FILE 块），超时与重试高于聊天默认；
    # timeout 是构造参数（bind kwargs 会漏进 completion API 被拒），重建实例。
    if isinstance(base, OpenAILLM) and isinstance(config, LLMConfig):
        long_config = config.model_copy(
            update={
                "additional_params": {
                    **(config.additional_params or {}),
                    "request_timeout": 600,
                    "max_retries": 2,
                }
            }
        )
        llm = OpenAILLM(long_config).llm.bind(temperature=0.1, max_tokens=16000)
    else:
        llm = base.llm.bind(temperature=0.1, max_tokens=16000)
    repo = Path(args.repo).expanduser()
    substrate_dir = Path(args.substrate)
    db_dir = (
        Path(args.db_dir).expanduser() if args.db_dir else substrate_dir.parent / "db"
    )

    if args.cmd == "plan":
        make_plan(llm, repo=repo, substrate_dir=substrate_dir, db_dir=db_dir)
    elif args.cmd == "run":
        reqdoc_root = Path(args.reqdoc_root).expanduser() if args.reqdoc_root else None
        run_plan(
            llm,
            repo=repo,
            substrate_dir=substrate_dir,
            db_dir=db_dir,
            reqdoc_root=reqdoc_root,
            out_dir=Path(args.out),
            only=[s for s in args.only.split(",") if s],
        )


async def _default_config() -> Any:
    from apps.ai_model.model_factory import get_default_config

    return await get_default_config()


if __name__ == "__main__":
    main()
