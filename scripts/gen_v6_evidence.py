#!/usr/bin/env python3
"""DEPRECATED: KnowledgePackage v6 evidence helper.

Corpus trees live under ``.tmp/docs/knowledge-extraction/…``.
Current wiki path: ``tools.wiki_extract`` → ``docs/wiki/v2`` → ``docs/wiki/v3``.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
import yaml
from apps.knowledge.semantic.schema import KnowledgeUnitEntry, collect_evidence_refs

REPO = Path("/Users/fanjunwei/IdeaProjects/pplatform-web")
V6 = Path(".tmp/docs/knowledge-extraction/pplatform-web/system-knowledge-v6")


def build_index() -> dict[str, list[str]]:
    table_files: dict[str, list[str]] = {}
    for path in REPO.rglob("*.java"):
        try:
            text = path.read_text(errors="ignore")
        except OSError:
            continue
        for m in re.finditer(r'@TableName\s*\(\s*"([^"]+)"', text):
            tbl = m.group(1).split(".")[-1]
            table_files.setdefault(tbl, []).append(str(path.relative_to(REPO)))
    for path in REPO.rglob("*.xml"):
        if "mappers" not in str(path):
            continue
        try:
            text = path.read_text(errors="ignore")
        except OSError:
            continue
        for m in re.finditer(
            r"(?:from|join|update|insert\s+into)\s+([a-z_0-9]+)", text, re.I
        ):
            table_files.setdefault(m.group(1).lower(), []).append(
                str(path.relative_to(REPO))
            )
    return {t: sorted(set(files)) for t, files in table_files.items()}


def kind_of(eid: str) -> str:
    if "dict" in eid or "enum" in eid:
        return "code_path"
    if any(k in eid for k in ("schema", "model", "fields", "-do", "field")):
        return "database_schema"
    if any(k in eid for k in ("query", "mapper", "dao", "sql")):
        return "query_usage"
    return "code_path"


def citing_claims(u: KnowledgeUnitEntry) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for c in u.content.concepts:
        for e in c.evidence_refs:
            out.append((e, f"{c.name}: {c.definition}"))
    for r in u.content.domain_rules:
        for e in r.evidence_refs:
            out.append((e, f"规则 {r.label}: {r.content}"))
    for cal in u.content.calibers:
        for e in cal.evidence_refs:
            out.append((e, f"口径 {cal.label}: {cal.description}"))
    for m in u.content.metrics:
        for e in m.evidence_refs:
            out.append((e, f"指标 {m.name}: {m.description}"))
    for p in u.content.processes:
        for e in p.evidence_refs:
            out.append((e, f"阶段 {p.name}: {p.trigger}"))
        for de in p.data_effects:
            for e in de.evidence_refs:
                out.append((e, f"{p.name} {de.operation} {de.dataset}.{de.fields}"))
    for rel in u.content.relationships:
        for e in rel.evidence_refs:
            out.append(
                (
                    e,
                    f"关系 {rel.left.dataset}.{rel.left.field} -> {rel.right.dataset}.{rel.right.field}",
                )
            )
    for pat in u.content.verified_query_patterns:
        for e in pat.evidence_refs:
            out.append((e, f"查询范式 {pat.question}"))
    return out


def main() -> None:
    table_files = build_index()
    meta_dir = V6 / "_meta"
    meta_dir.mkdir(exist_ok=True)
    for unit_file in sorted((V6 / "units").glob("*.yaml")):
        u = KnowledgeUnitEntry.model_validate(yaml.safe_load(open(unit_file)))
        tables = [d.name for d in u.content.datasets]
        claims = citing_claims(u)
        sources: dict[str, dict] = {}
        evidence: dict[str, dict] = {}
        for eid in sorted(set(collect_evidence_refs(u))):
            locator = ""
            for t in tables:
                if table_files.get(t):
                    locator = table_files[t][0]
                    break
            src_id = f"src-{u.unit_id}"
            sources.setdefault(
                src_id,
                {
                    "source_id": src_id,
                    "kind": "source_code" if locator else "database_catalog",
                    "locator": locator or "/".join(tables),
                    "repository_revision": "ee434954e",
                },
            )
            claim = next(
                (c for eid2, c in claims if eid2 == eid), f"{u.title} 相关事实"
            )
            evidence[eid] = {
                "evidence_id": eid,
                "source_id": src_id,
                "evidence_kind": kind_of(eid),
                "locator": locator or "/".join(tables),
                "claim": claim[:300],
                "confidence": 0.8,
            }
        payload = {
            "unit_id": u.unit_id,
            "sources": list(sources.values()),
            "evidence": list(evidence.values()),
        }
        json.dump(
            payload,
            open(meta_dir / f"{u.unit_id}.json", "w"),
            ensure_ascii=False,
            indent=2,
        )
        print(f"{u.unit_id}: sources={len(sources)} evidence={len(evidence)}")


if __name__ == "__main__":
    main()
