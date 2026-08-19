"""Strict KnowledgePackage 2.0 scanner used by every file import surface."""

from __future__ import annotations

import json
from io import BytesIO
from pathlib import Path
from typing import Any
from zipfile import BadZipFile, ZipFile

import yaml

from apps.knowledge.semantic.schema import KnowledgePackageV2

_MANIFEST_NAMES = {
    "knowledge-package.yaml",
    "knowledge-package.yml",
    "knowledge-package.json",
}
_DOCUMENT_SUFFIXES = {".yaml", ".yml", ".json", ".jsonl"}


def document_locator(name: str | None) -> str:
    """Preserve selection-relative paths from pickers, drag-drop and ZIP members."""
    parts = [
        part
        for part in (name or "").replace("\\", "/").strip().lstrip("/").split("/")
        if part and part != "."
    ]
    if not parts or ".." in parts:
        return ""
    if any(part.startswith(".") or part == "__MACOSX" for part in parts):
        return ""
    return "/".join(parts)


def decode_document(name: str, content: str) -> Any:
    suffix = Path(name).suffix.lower()
    if suffix == ".jsonl":
        return [json.loads(line) for line in content.splitlines() if line.strip()]
    if suffix == ".json":
        return json.loads(content)
    if suffix in {".yaml", ".yml"}:
        return yaml.safe_load(content)
    raise ValueError(f"unsupported knowledge document: {name}")


def scan_package_payload(payload: dict[str, Any] | str) -> KnowledgePackageV2:
    if isinstance(payload, str):
        decoded = yaml.safe_load(payload)
    else:
        decoded = payload
    if not isinstance(decoded, dict):
        raise ValueError("KnowledgePackage 2.0 root must be an object")
    if decoded.get("schema_version") != "2.0":
        raise ValueError(
            "KnowledgePackage 1.0 is no longer accepted; extract a scene-oriented 2.0 package"
        )
    return KnowledgePackageV2.model_validate(decoded)


def scan_package_documents(documents: list[tuple[str, str]]) -> KnowledgePackageV2:
    """Find one canonical package from files, dropped directories or archives.

    Referenced evidence files are retained by their locator/hash in the manifest;
    they are not reinterpreted as independent knowledge items.
    """
    manifests: list[tuple[str, Any]] = []
    for name, content in sorted(documents):
        locator = document_locator(name)
        if not locator or Path(locator).name.lower() not in _MANIFEST_NAMES:
            continue
        manifests.append((locator, decode_document(locator, content)))
    if not manifests and len(documents) == 1:
        locator = document_locator(documents[0][0]) or documents[0][0]
        manifests.append((locator, decode_document(locator, documents[0][1])))
    if not manifests:
        raise ValueError(
            "no KnowledgePackage 2.0 manifest found (expected knowledge-package.yaml/json)"
        )
    if len(manifests) > 1:
        names = ", ".join(name for name, _payload in manifests)
        raise ValueError(f"multiple package manifests selected: {names}")
    return scan_package_payload(manifests[0][1])


def scan_package_files(documents: list[tuple[str, bytes]]) -> KnowledgePackageV2:
    """Decode uploaded documents and archives through one import path.

    Archives are transport only. Their paths are preserved for manifest
    discovery, while unsupported and hidden files are ignored.
    """
    expanded: list[tuple[str, str]] = []
    for name, content in documents:
        locator = document_locator(name)
        suffix = Path(locator or name).suffix.lower()
        if suffix == ".zip":
            try:
                with ZipFile(BytesIO(content)) as archive:
                    for member in archive.infolist():
                        member_path = Path(member.filename)
                        if member.is_dir():
                            continue
                        if member_path.is_absolute() or ".." in member_path.parts:
                            raise ValueError(
                                f"unsafe archive member: {member.filename}"
                            )
                        member_locator = document_locator(member.filename)
                        if (
                            not member_locator
                            or Path(member_locator).suffix.lower()
                            not in _DOCUMENT_SUFFIXES
                        ):
                            continue
                        expanded.append(
                            (
                                member_locator,
                                archive.read(member).decode("utf-8-sig"),
                            )
                        )
            except (BadZipFile, UnicodeDecodeError) as exc:
                raise ValueError(f"invalid knowledge archive: {name}") from exc
            continue
        if not locator or suffix not in _DOCUMENT_SUFFIXES:
            continue
        try:
            expanded.append((locator, content.decode("utf-8-sig")))
        except UnicodeDecodeError as exc:
            raise ValueError(f"knowledge document must be UTF-8: {name}") from exc
    if not expanded:
        raise ValueError("no supported knowledge documents found")
    return scan_package_documents(expanded)
