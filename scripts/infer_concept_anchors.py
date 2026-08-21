#!/usr/bin/env python
"""Infer concept field_targets for an existing KnowledgePackage 2.0 directory.

Bridge tool for packages authored before concept anchoring existed (ADR
knowledge-architecture v3.1, decision D4: progressive contract evolution).

Inference rules, strongest first:
  1. dictionary key partition - every concept dictionary key is covered by
     some field dictionary with the same value meaning; the concept anchors
     to all covering fields (a state concept often spans a status field and
     an audit field).
  2. dictionary value mention - empty-dictionary concept whose name or
     alias appears inside a field dictionary value (e.g. the onboarding
     concept matches the build_status values "未建档/建档中").
  3. dataset token match - empty-dictionary entity concept anchors to the
     id field of the dataset whose id/name tokens overlap the concept id.
  4. field name / description mentions as weaker fallbacks.

Usage:
    backend/venv/bin/python scripts/infer_concept_anchors.py <package_dir> [--write]

Default is a dry run printing a JSON report; --write annotates the unit
YAML files in place. Ambiguous or unmatched concepts stay unanchored and
feed the CONCEPT_UNANCHORED lint report for the next extraction pass.
"""
from __future__ import annotations

import argparse
import pathlib
import sys

import yaml

MAX_ANCHOR_FIELDS = 3
DATASET_TOKEN_THRESHOLD = 0.5


def _norm(value: str) -> str:
    return "".join((value or "").casefold().split())


def _tokens(value: str) -> set[str]:
    parts: set[str] = set()
    for chunk in (value or "").replace("-", "_").replace(".", "_").split("_"):
        chunk = chunk.casefold().strip()
        if chunk:
            parts.add(chunk)
    return parts


def _fields_of(datasets: list[dict[str, object]]) -> list[tuple[str, str, dict[str, str]]]:
    fields: list[tuple[str, str, dict[str, str]]] = []
    for dataset in datasets:
        dataset_id = str(dataset.get("dataset_id") or "")
        for field in dataset.get("fields") or []:
            dictionary = {
                str(key): str(value)
                for key, value in (field.get("dictionary") or {}).items()
            }
            fields.append((dataset_id, str(field.get("field_id") or ""), dictionary))
    return fields


def _cover_keys_by_field(
    concept_dict: dict[str, str],
    fields: list[tuple[str, str, dict[str, str]]],
) -> dict[tuple[str, str], set[str]]:
    """Map covering (dataset, field) -> covered concept keys.

    A key is covered exactly when a field dictionary holds the same key
    with the same value meaning. When no exact cover exists but the key
    appears in exactly one field, that unique loose cover still counts
    (extraction often words the concept meaning more specifically).
    """
    covering: dict[tuple[str, str], set[str]] = {}
    for key, meaning in concept_dict.items():
        exact = [
            (dataset_id, field_id)
            for dataset_id, field_id, dictionary in fields
            if dictionary.get(key) == meaning
        ]
        if exact:
            matched = exact
        else:
            loose = [
                (dataset_id, field_id)
                for dataset_id, field_id, dictionary in fields
                if key in dictionary
            ]
            matched = loose if len(loose) == 1 else []
        if not matched:
            continue
        for target in matched:
            covering.setdefault(target, set()).add(key)
    return covering


def _dataset_grouped_cover(
    concept_dict: dict[str, str],
    fields: list[tuple[str, str, dict[str, str]]],
    concept_id: str = "",
) -> list[tuple[str, str]] | None:
    """Anchor targets grouped by dataset via greedy set cover.

    State concepts frequently span two fields of the same table (a
    status field plus an audit field); grouping by dataset prefers that
    natural reading over one field per table. Returns None when some key
    stays uncovered or the covering set exceeds the field cap.
    """
    covering = _cover_keys_by_field(concept_dict, fields)
    if not covering:
        return None
    all_keys = set(concept_dict)
    by_dataset: dict[str, dict[tuple[str, str], set[str]]] = {}
    for target, keys in covering.items():
        by_dataset.setdefault(target[0], {})[target] = keys
    concept_tokens = _tokens(concept_id)
    covered: set[str] = set()
    chosen: list[tuple[str, str]] = []
    while covered != all_keys:
        remaining = all_keys - covered
        best_dataset = None
        best_gain = 0
        best_affinity = -1.0
        for dataset_id in sorted(by_dataset):
            gain = len(
                remaining
                & set().union(*by_dataset[dataset_id].values()),
            )
            if gain == 0:
                continue
            dataset_tokens = _tokens(dataset_id)
            affinity = (
                len(concept_tokens & dataset_tokens)
                / len(concept_tokens | dataset_tokens)
                if concept_tokens and dataset_tokens
                else 0.0
            )
            if gain > best_gain or (gain == best_gain and affinity > best_affinity):
                best_gain = gain
                best_affinity = affinity
                best_dataset = dataset_id
        if best_dataset is None or best_gain == 0:
            return None
        for target, keys in sorted(by_dataset[best_dataset].items()):
            if keys & remaining:
                chosen.append(target)
                covered |= keys & remaining
    if not chosen or len(chosen) > MAX_ANCHOR_FIELDS:
        return None
    return sorted(chosen)


def _value_mention_fields(
    names: list[str],
    fields: list[tuple[str, str, dict[str, str]]],
) -> list[tuple[str, str]]:
    """Fields whose dictionary values mention a concept name or alias."""
    targets: list[tuple[str, str]] = []
    for dataset_id, field_id, dictionary in fields:
        values_text = _norm(" ".join(dictionary.values()))
        if any(_norm(name) in values_text for name in names if _norm(name)):
            targets.append((dataset_id, field_id))
    return sorted(targets)


def _dataset_token_anchor(
    concept_id: str,
    datasets: list[dict[str, object]],
) -> tuple[str, str] | None:
    """Anchor an entity concept to its dataset id field via token overlap."""
    concept_tokens = _tokens(concept_id)
    if not concept_tokens:
        return None
    scored: list[tuple[float, str, str]] = []
    for dataset in datasets:
        dataset_id = str(dataset.get("dataset_id") or "")
        dataset_name = str(dataset.get("name") or "")
        id_tokens = _tokens(dataset_id)
        name_tokens = _tokens(dataset_name)
        if not id_tokens and not name_tokens:
            continue
        overlap = max(
            len(concept_tokens & id_tokens) / len(concept_tokens | id_tokens)
            if id_tokens
            else 0.0,
            len(concept_tokens & name_tokens) / len(concept_tokens | name_tokens)
            if name_tokens
            else 0.0,
        )
        if overlap >= DATASET_TOKEN_THRESHOLD:
            field_ids = [
                str(field.get("field_id") or "")
                for field in dataset.get("fields") or []
            ]
            anchor_field = "id" if "id" in field_ids else (field_ids[0] if field_ids else "")
            if anchor_field:
                scored.append((overlap, dataset_id, anchor_field))
    if not scored:
        return None
    scored.sort(key=lambda item: (-item[0], item[1]))
    if len(scored) > 1 and scored[0][0] == scored[1][0]:
        return None
    return scored[0][1], scored[0][2]


def infer_candidates(
    concept: dict[str, object],
    datasets: list[dict[str, object]],
) -> list[tuple[int, str, str, str]]:
    """Score same-unit fields as anchors for one concept.

    Returns (score, dataset_id, field_id, reason) tuples sorted by score
    descending. Pure function so tests can exercise it without YAML files.
    """
    name = str(concept.get("name") or "")
    aliases = [str(item) for item in (concept.get("aliases") or [])]
    definition = str(concept.get("definition") or "")
    concept_dict = {
        str(key): str(value)
        for key, value in (concept.get("dictionary") or {}).items()
    }
    fields = _fields_of(datasets)
    candidates: list[tuple[int, str, str, str]] = []
    if concept_dict:
        for dataset_id, field_id, dictionary in fields:
            if dictionary == concept_dict:
                candidates.append((100, dataset_id, field_id, "dictionary-match"))
    for dataset in datasets:
        dataset_id = str(dataset.get("dataset_id") or "")
        for field in dataset.get("fields") or []:
            field_id = str(field.get("field_id") or "")
            field_name = str(field.get("name") or "")
            description = str(field.get("description") or "")
            if _norm(name) and _norm(name) == _norm(field_name):
                candidates.append((70, dataset_id, field_id, "field-name-equals-concept"))
            for alias in [name, *aliases]:
                if _norm(alias) and _norm(alias) in _norm(description):
                    candidates.append((60, dataset_id, field_id, "concept-mentioned-in-field-description"))
                    break
            if _norm(field_name) and _norm(field_name) in _norm(definition):
                candidates.append((50, dataset_id, field_id, "field-mentioned-in-definition"))
    candidates.sort(key=lambda item: (-item[0], item[1], item[2]))
    return candidates


def infer_anchor(
    concept: dict[str, object],
    datasets: list[dict[str, object]],
) -> tuple[list[dict[str, str]], str] | None:
    """Best anchor decision for one concept.

    Returns (targets, reason) where targets is a non-empty list of
    {dataset, field} dicts, or None when no rule applies cleanly.
    """
    concept_dict = {
        str(key): str(value)
        for key, value in (concept.get("dictionary") or {}).items()
    }
    fields = _fields_of(datasets)
    if concept_dict:
        partition = _dataset_grouped_cover(
            concept_dict,
            fields,
            str(concept.get("concept_id") or ""),
        )
        if partition is not None:
            reason = (
                "dictionary-match"
                if len(partition) == 1
                else "dictionary-key-partition"
            )
            return [{"dataset": item[0], "field": item[1]} for item in partition], reason
        return None
    name = str(concept.get("name") or "")
    aliases = [str(item) for item in (concept.get("aliases") or [])]
    mentions = _value_mention_fields([name, *aliases], fields)
    if mentions:
        mention_datasets = {item[0] for item in mentions}
        if len(mention_datasets) == 1 and len(mentions) <= MAX_ANCHOR_FIELDS:
            return (
                [{"dataset": item[0], "field": item[1]} for item in mentions],
                "dictionary-value-mention",
            )
        return None
    token_anchor = _dataset_token_anchor(
        str(concept.get("concept_id") or ""), datasets
    )
    if token_anchor is not None:
        return (
            [{"dataset": token_anchor[0], "field": token_anchor[1]}],
            "dataset-token-match",
        )
    candidates = infer_candidates(concept, datasets)
    if not candidates:
        return None
    best = candidates[0]
    if any(item[0] == best[0] for item in candidates[1:]):
        return None
    return (
        [{"dataset": best[1], "field": best[2]}],
        best[3],
    )


def annotate_unit(unit: dict[str, object]) -> list[dict[str, object]]:
    """Annotate one unit dict in place; return a per-concept report."""
    content = unit.get("content") or {}
    datasets = list(content.get("datasets") or [])
    report: list[dict[str, object]] = []
    for concept in content.get("concepts") or []:
        concept_id = str(concept.get("concept_id") or "")
        if concept.get("field_targets"):
            report.append({"concept": concept_id, "status": "already-anchored"})
            continue
        anchor = infer_anchor(concept, datasets)
        if anchor is None:
            candidates = infer_candidates(concept, datasets)
            if candidates:
                report.append(
                    {
                        "concept": concept_id,
                        "status": "ambiguous",
                        "candidates": [
                            {"dataset": item[1], "field": item[2], "score": item[0]}
                            for item in candidates[:4]
                        ],
                    }
                )
            else:
                report.append({"concept": concept_id, "status": "none"})
            continue
        targets, reason = anchor
        concept["field_targets"] = targets
        report.append(
            {
                "concept": concept_id,
                "status": "anchored",
                "targets": targets,
                "reason": reason,
            }
        )
    return report


def annotate_package(package_dir: pathlib.Path, write: bool) -> dict[str, object]:
    manifest_path = None
    for name in (
        "knowledge-package.yaml",
        "knowledge-package.yml",
        "knowledge-package.json",
    ):
        candidate = package_dir / name
        if candidate.exists():
            manifest_path = candidate
            break
    if manifest_path is None:
        raise SystemExit(f"no knowledge-package manifest found under {package_dir}")
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    unit_paths = manifest.get("units") or []
    units: list[tuple[pathlib.Path, dict[str, object]]] = []
    if unit_paths:
        for relative in unit_paths:
            unit_file = package_dir / pathlib.Path(relative)
            units.append(
                (unit_file, yaml.safe_load(unit_file.read_text(encoding="utf-8")))
            )
    else:
        units.append((manifest_path, manifest))

    all_reports: dict[str, object] = {}
    changed_files: list[str] = []
    for unit_file, unit in units:
        report = annotate_unit(unit)
        unit_id = str(unit.get("unit_id") or unit_file.stem)
        all_reports[unit_id] = report
        if write and any(item.get("status") == "anchored" for item in report):
            unit_file.write_text(
                yaml.safe_dump(unit, allow_unicode=True, sort_keys=False),
                encoding="utf-8",
            )
            changed_files.append(str(unit_file))

    total = sum(len(items) for items in all_reports.values())
    anchored = sum(
        1
        for items in all_reports.values()
        for item in items
        if item.get("status") == "anchored"
    )
    already = sum(
        1
        for items in all_reports.values()
        for item in items
        if item.get("status") == "already-anchored"
    )
    ambiguous = sum(
        1
        for items in all_reports.values()
        for item in items
        if item.get("status") == "ambiguous"
    )
    none_count = total - anchored - already - ambiguous
    return {
        "units": all_reports,
        "summary": {
            "total_concepts": total,
            "anchored": anchored,
            "already_anchored": already,
            "ambiguous": ambiguous,
            "unmatched": none_count,
            "anchor_rate_after_bridge": (already + anchored) / total if total else 1.0,
        },
        "changed_files": changed_files,
        "write": write,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package_dir", type=pathlib.Path)
    parser.add_argument(
        "--write",
        action="store_true",
        help="annotate unit YAML files in place (default: dry run)",
    )
    args = parser.parse_args(argv)
    result = annotate_package(args.package_dir, write=args.write)
    import json

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())