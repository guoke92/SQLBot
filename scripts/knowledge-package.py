#!/usr/bin/env python3
"""Scan, validate and submit KnowledgePackage 2.0 packages.

The offline extraction contract is KnowledgePackageV2. A package is either a
single ``knowledge-package.yaml`` with inline ``knowledge_units`` or a manifest
referencing one file per unit under ``units``. Both forms assemble to the same
``KnowledgePackageV2`` through the semantic scanner, so the CLI has one read
path and the server has one import path.

Run with the backend virtual environment so the command uses the same Pydantic
and YAML versions as the server:

    backend/venv/bin/python scripts/knowledge-package.py scan <path>
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

import yaml  # noqa: E402

from apps.knowledge.graph.decompose import plan_decomposition  # noqa: E402
from apps.knowledge.semantic.lint import lint_package, load_coverage  # noqa: E402
from apps.knowledge.semantic.scanner import scan_package_files  # noqa: E402
from apps.knowledge.semantic.schema import KnowledgePackageV2  # noqa: E402

_DOCUMENT_SUFFIXES = {".yaml", ".yml", ".json", ".jsonl"}
_COVERAGE_NAMES = {"coverage.yaml", "coverage.yml"}


def _load(path: str) -> tuple[KnowledgePackageV2, dict | None]:
    p = Path(path)
    if p.is_dir():
        documents: list[tuple[str, bytes]] = []
        for file in sorted(p.rglob("*")):
            if file.is_file() and file.suffix.lower() in _DOCUMENT_SUFFIXES:
                if file.name in _COVERAGE_NAMES:
                    continue
                documents.append((file.relative_to(p).as_posix(), file.read_bytes()))
        if not documents:
            raise SystemExit(f"no knowledge documents found under: {path}")
        return scan_package_files(documents), _load_coverage(p)
    if p.is_file():
        return scan_package_files([(p.name, p.read_bytes())]), _load_coverage(p.parent)
    raise SystemExit(f"not a file or directory: {path}")


def _load_coverage(directory: Path) -> dict | None:
    for name in _COVERAGE_NAMES:
        candidate = directory / name
        if candidate.is_file():
            return load_coverage(candidate)
    return None


def _summary(package: KnowledgePackageV2) -> dict[str, Any]:
    buckets: dict[str, int] = {}
    for unit in package.knowledge_units:
        content = unit.content.model_dump(mode="json")
        for name, value in content.items():
            if isinstance(value, list):
                buckets[name] = buckets.get(name, 0) + len(value)
    return {
        "valid": True,
        "schema_version": package.schema_version,
        "package_id": package.package.package_id,
        "revision": package.package.revision,
        "namespace": package.package.namespace,
        "units": len(package.knowledge_units),
        "sources": len(package.sources),
        "evidence": len(package.evidence),
        "content_buckets": buckets,
    }


def _decompose_report(package: KnowledgePackageV2) -> dict[str, Any]:
    """Dry-run decomposition: is the package ready for the node/edge plane?"""
    from collections import Counter

    plan = plan_decomposition(package)
    concepts = sum(1 for unit in package.knowledge_units for _ in unit.content.concepts)
    edges_by_kind = dict(Counter(edge.edge_kind for edge in plan.edges))
    return {
        "nodes": len(plan.nodes),
        "nodes_by_kind": dict(Counter(node.node_kind for node in plan.nodes.values())),
        "edges": len(plan.edges),
        "edges_by_kind": edges_by_kind,
        "concept_of": edges_by_kind.get("concept_of", 0),
        "concepts": concepts,
        "concepts_anchored": all_concepts_anchored(package),
        "merge_conflicts": plan.stats.get("merge_conflicts", 0),
        "stub_nodes": plan.stats.get("stub_nodes", 0),
    }


def all_concepts_anchored(package: KnowledgePackageV2) -> int:
    """Count concepts that carry at least one field_targets anchor."""
    return sum(
        1
        for unit in package.knowledge_units
        for concept in unit.content.concepts
        if concept.field_targets
    )


def _post(base_url: str, token: str, package: KnowledgePackageV2) -> dict[str, Any]:
    endpoint = f"{base_url.rstrip('/')}/api/v1/knowledge/packages"
    body = json.dumps(
        {"package": package.model_dump(mode="json")}, ensure_ascii=False
    ).encode()
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if token:
        headers["X-SQLBOT-TOKEN"] = (
            token if token.startswith("Bearer ") else f"Bearer {token}"
        )
    request = Request(endpoint, data=body, method="POST", headers=headers)
    try:
        with urlopen(request, timeout=300) as response:  # noqa: S310 - operator-selected URL
            return json.loads(response.read().decode())
    except HTTPError as exc:
        detail = exc.read().decode(errors="replace")
        raise SystemExit(f"HTTP {exc.code}: {detail}") from exc
    except URLError as exc:
        raise SystemExit(f"cannot reach {endpoint}: {exc.reason}") from exc


def main() -> None:
    parser = argparse.ArgumentParser(description="KnowledgePackage 2.0 tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan = subparsers.add_parser(
        "scan", help="assemble a file/directory and print a validation summary"
    )
    scan.add_argument("path")
    scan.add_argument(
        "-o",
        "--output",
        help="optional: write the assembled package as one canonical YAML for inspection",
    )
    scan.add_argument(
        "--strict",
        action="store_true",
        help="promote CONCEPT_UNANCHORED / FAKE_EXECUTED to blocking and fail on them",
    )

    decompose = subparsers.add_parser(
        "decompose",
        help="dry-run node/edge decomposition to verify six-layer closure",
    )
    decompose.add_argument("path")

    submit = subparsers.add_parser(
        "submit", help="assemble and register a package through the API"
    )
    submit.add_argument("path")
    submit.add_argument("--base-url", default="http://localhost:8000")
    submit.add_argument("--token", default="")

    args = parser.parse_args()
    try:
        package, coverage = _load(args.path)
        if args.command == "scan":
            if args.output:
                content = yaml.safe_dump(
                    package.model_dump(mode="json", exclude_none=True),
                    allow_unicode=True,
                    sort_keys=False,
                )
                Path(args.output).write_text(content, encoding="utf-8")
            summary = _summary(package)
            if coverage is not None:
                qa = lint_package(package, coverage, strict=args.strict)
                summary["qa"] = qa
                if args.strict and qa["summary"]["blocking"]:
                    print(json.dumps(summary, ensure_ascii=False, indent=2))
                    raise SystemExit(
                        f"strict scan failed: {qa['summary']['blocking']} blocking issue(s)"
                    )
            print(json.dumps(summary, ensure_ascii=False, indent=2))
            return
        if args.command == "decompose":
            print(json.dumps(_decompose_report(package), ensure_ascii=False, indent=2))
            return
        result = _post(args.base_url, args.token, package)
    except ValueError as exc:
        raise SystemExit(f"invalid knowledge package: {exc}") from exc
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
