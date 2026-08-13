#!/usr/bin/env python3
"""Scan, validate and submit AI智能问数 knowledge packages.

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

from apps.knowledge.importing.scanner import load_knowledge_package  # noqa: E402


def _write_package(value: dict[str, Any], output: str | None) -> None:
    content = yaml.safe_dump(value, allow_unicode=True, sort_keys=False)
    if output:
        Path(output).write_text(content, encoding="utf-8")
    else:
        print(content, end="")


def _load(path: str) -> dict[str, Any]:
    return load_knowledge_package(path).model_dump(mode="json", exclude_none=True)


def _post(
    *,
    base_url: str,
    action: str,
    token: str,
    package: dict[str, Any],
    datasource_id: int | None,
    datasource_name: str | None,
    include_kinds: list[str],
) -> dict[str, Any]:
    endpoint = f"{base_url.rstrip('/')}/api/v1/knowledge/import/{action}"
    body = json.dumps(
        {
            "package": package,
            "package_id": package["package_id"],
            "default_datasource_id": datasource_id,
            "default_datasource_name": datasource_name,
            "include_kinds": include_kinds,
        },
        ensure_ascii=False,
    ).encode()
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if token:
        headers["X-SQLBOT-TOKEN"] = (
            token if token.startswith("Bearer ") else f"Bearer {token}"
        )
    request = Request(endpoint, data=body, method="POST", headers=headers)
    try:
        with urlopen(request, timeout=300) as response:  # noqa: S310 - operator-selected URL
            result = json.loads(response.read().decode())
    except HTTPError as exc:
        detail = exc.read().decode(errors="replace")
        raise SystemExit(f"HTTP {exc.code}: {detail}") from exc
    except URLError as exc:
        raise SystemExit(f"cannot reach {endpoint}: {exc.reason}") from exc
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="AI智能问数 knowledge-package tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan = subparsers.add_parser(
        "scan", help="scan a file/directory and emit canonical YAML"
    )
    scan.add_argument("path")
    scan.add_argument("-o", "--output")

    validate = subparsers.add_parser(
        "validate", help="validate and summarize a package"
    )
    validate.add_argument("path")

    for action in ("preview", "apply"):
        command = subparsers.add_parser(
            action, help=f"{action} a package through the API"
        )
        command.add_argument("path")
        command.add_argument("--base-url", default="http://localhost:8000")
        command.add_argument("--token", default="")
        command.add_argument("--datasource-id", type=int)
        command.add_argument("--datasource-name")
        command.add_argument("--kind", action="append", default=[])
        if action == "apply":
            command.add_argument("--yes", action="store_true")

    args = parser.parse_args()
    package = _load(args.path)
    if args.command == "scan":
        _write_package(package, args.output)
        return
    if args.command == "validate":
        counts: dict[str, int] = {}
        for item in package["items"]:
            counts[item["kind"]] = counts.get(item["kind"], 0) + 1
        print(
            json.dumps(
                {
                    "valid": True,
                    "package_id": package["package_id"],
                    "total": len(package["items"]),
                    "counts": counts,
                    "warnings": package.get("generator", {}).get(
                        "scanner_warnings", []
                    ),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return
    if args.command == "apply" and not args.yes:
        raise SystemExit(
            "apply changes managed knowledge; pass --yes after reviewing preview"
        )
    result = _post(
        base_url=args.base_url,
        action=args.command,
        token=args.token,
        package=package,
        datasource_id=args.datasource_id,
        datasource_name=args.datasource_name,
        include_kinds=args.kind,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
