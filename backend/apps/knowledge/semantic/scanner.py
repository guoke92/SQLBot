"""Strict KnowledgePackage 2.0 scanner used by every file import surface."""

from __future__ import annotations

import json
import posixpath
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


def _unit_locator(manifest_locator: str, unit_path: str) -> str:
    """Resolve a manifest-relative unit path to the same normalized locator used
    for files arriving from pickers, drag-drop and ZIP members."""
    base = posixpath.dirname(manifest_locator)
    candidate = unit_path if not base else posixpath.join(base, unit_path)
    return document_locator(candidate)


def _assemble_package(
    manifest_locator: str,
    manifest: Any,
    documents_by_locator: dict[str, str],
) -> KnowledgePackageV2:
    """Assemble the single semantic contract from a manifest plus unit files.

    ``units`` is an on-disk authoring/transport concern only. It is removed
    before validation so ``KnowledgePackageV2`` remains the sole semantic
    contract and no second schema is introduced.
    """
    if not isinstance(manifest, dict):
        raise ValueError("KnowledgePackage 2.0 manifest root must be an object")
    unit_paths = manifest.get("units")
    inline_units = manifest.get("knowledge_units")
    if unit_paths is not None and inline_units is not None:
        raise ValueError("manifest cannot define both `units` and `knowledge_units`")
    if unit_paths is None:
        return scan_package_payload(manifest)

    if not isinstance(unit_paths, list) or not unit_paths:
        raise ValueError("manifest `units` must be a non-empty list of relative paths")
    entries: list[Any] = []
    for unit_path in unit_paths:
        if not isinstance(unit_path, str) or not unit_path.strip():
            raise ValueError("manifest `units` entries must be non-empty strings")
        locator = _unit_locator(manifest_locator, unit_path.strip())
        raw = documents_by_locator.get(locator)
        if raw is None:
            raise ValueError(f"unit file not found: {unit_path}")
        entries.append(decode_document(locator, raw))

    assembled = {key: value for key, value in manifest.items() if key != "units"}
    assembled["knowledge_units"] = entries
    return scan_package_payload(assembled)


def scan_package_documents(documents: list[tuple[str, str]]) -> KnowledgePackageV2:
    """Find one canonical package from files, dropped directories or archives.

    The package may be a single inline manifest or a manifest referencing one
    file per knowledge unit under ``units``. Referenced evidence files are
    retained by their locator/hash in the manifest; they are not reinterpreted
    as independent knowledge items.
    """
    manifests: list[tuple[str, Any]] = []
    documents_by_locator: dict[str, str] = {}
    for name, content in sorted(documents):
        locator = document_locator(name)
        if not locator:
            continue
        if Path(locator).name.lower() in _MANIFEST_NAMES:
            manifests.append((locator, decode_document(locator, content)))
        elif Path(locator).suffix.lower() in _DOCUMENT_SUFFIXES:
            documents_by_locator[locator] = content
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
    manifest_locator, manifest = manifests[0]
    manifest = _attach_companion_relationships(
        manifest_locator, manifest, documents_by_locator
    )
    return _assemble_package(manifest_locator, manifest, documents_by_locator)


def _attach_companion_relationships(
    manifest_locator: str,
    manifest: Any,
    documents_by_locator: dict[str, str],
) -> Any:
    """Merge a sibling relationships.yaml into the manifest when present.

    Extraction authors may keep package-scoped physical relations in a
    standalone companion file next to the manifest (the v4 layout); the
    scanner folds it into the contract so no second import path exists.
    """
    if not isinstance(manifest, dict) or "relationships" in manifest:
        return manifest
    base = posixpath.dirname(manifest_locator)
    for name in ("relationships.yaml", "relationships.yml", "relationships.json"):
        companion = posixpath.join(base, name) if base else name
        raw = documents_by_locator.get(companion)
        if raw is None:
            continue
        decoded = decode_document(companion, raw)
        if isinstance(decoded, dict) and decoded.get("relationships"):
            return {**manifest, "relationships": decoded["relationships"]}
        break
    return manifest


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
