"""Zero-trust checks: catalog physical names + optional code_path files."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from tools.wiki_extract.l1.loader import IntermediateBundle
from tools.wiki_extract.l1.schema import dict_page_key, parse_code_path, physical_pair


@dataclass
class ReviewItem:
    kind: str
    target: str
    message: str
    evidence: str = ""
    severity: str = "error"


@dataclass
class ValidationReport:
    errors: list[ReviewItem] = field(default_factory=list)
    warnings: list[ReviewItem] = field(default_factory=list)

    def add(
        self,
        kind: str,
        target: str,
        message: str,
        *,
        evidence: str = "",
        severity: str = "error",
    ) -> None:
        item = ReviewItem(
            kind=kind, target=target, message=message, evidence=evidence, severity=severity
        )
        (self.errors if severity == "error" else self.warnings).append(item)


def catalog_tables(catalog: dict[str, Any]) -> dict[str, dict[str, Any]]:
    tables = catalog.get("tables") if isinstance(catalog, dict) else None
    return tables if isinstance(tables, dict) else {}


def catalog_columns(table_meta: dict[str, Any]) -> set[str]:
    columns = table_meta.get("columns") if isinstance(table_meta, dict) else None
    if isinstance(columns, dict):
        return {str(name) for name in columns}
    if isinstance(columns, list):
        out: set[str] = set()
        for item in columns:
            if isinstance(item, dict) and item.get("name"):
                out.add(str(item["name"]))
            elif isinstance(item, str):
                out.add(item)
        return out
    return set()


def validate_bundle(
    bundle: IntermediateBundle,
    catalog: dict[str, Any],
    *,
    code_root: Path | None = None,
    skip_code_check: bool = False,
) -> ValidationReport:
    report = ValidationReport()
    tables = catalog_tables(catalog)
    index = _code_index(code_root) if code_root and not skip_code_check else {}

    for table, body in bundle.table_enhancements.items():
        _assert_table(report, tables, table, f"tables.{table}")
        columns = catalog_columns(tables.get(table) or {})
        filt = body.get("default_filter") or {}
        _check_predicate_endpoints(
            report, tables, f"tables.{table}.default_filter", filt.get("predicate")
        )
        _check_code_evidence(report, index, filt.get("evidence"), skip_code_check, f"tables.{table}")
        for group in body.get("written_with_groups") or []:
            for col in group.get("fields") or []:
                _assert_column(report, columns, table, str(col), f"tables.{table}.written_with")
            _check_code_evidence(
                report, index, group.get("evidence"), skip_code_check, f"tables.{table}.written_with"
            )

    for item in bundle.processes:
        table = str(item.get("table") or "")
        field = str(item.get("field") or "")
        _assert_table(report, tables, table, item.get("process_key") or table)
        _assert_column(
            report, catalog_columns(tables.get(table) or {}), table, field, item.get("process_key") or table
        )
        for stage in item.get("stages") or []:
            for trans in stage.get("transitions") or []:
                _check_code_evidence(
                    report,
                    index,
                    trans.get("evidence") or stage.get("evidence") or item.get("evidence"),
                    skip_code_check,
                    str(item.get("process_key") or ""),
                )

    for item in bundle.calibers:
        _check_field_targets(report, tables, item.get("field_targets") or [], item.get("caliber_key"))
        _check_code_evidence(
            report, index, item.get("evidence"), skip_code_check, str(item.get("caliber_key") or "")
        )

    for item in bundle.rules:
        _check_field_targets(report, tables, item.get("field_targets") or [], item.get("rule_key"))
        _check_code_evidence(
            report, index, item.get("evidence"), skip_code_check, str(item.get("rule_key") or "")
        )

    for rel in bundle.relations:
        for endpoint in (rel.get("left"), rel.get("right")):
            table, column = physical_pair(str(endpoint or ""))
            _assert_table(report, tables, table, str(endpoint))
            _assert_column(
                report, catalog_columns(tables.get(table) or {}), table, column, str(endpoint)
            )
        _check_code_evidence(
            report, index, rel.get("evidence"), skip_code_check, f"{rel.get('left')}={rel.get('right')}"
        )

    for key, body in bundle.dict_labels.items():
        table = str(body.get("table") or "")
        column = str(body.get("column") or "")
        _assert_table(report, tables, table, key)
        _assert_column(report, catalog_columns(tables.get(table) or {}), table, column, key)
        for code, meta in (body.get("values") or {}).items():
            _check_code_evidence(
                report,
                index,
                (meta or {}).get("evidence") if isinstance(meta, dict) else None,
                skip_code_check,
                f"{key}.{code}",
            )

    for item in bundle.concepts:
        maps_to = str(item.get("maps_to") or "")
        _check_anchor(report, tables, maps_to, item.get("concept_key"))
        _check_field_targets(
            report, tables, item.get("field_targets") or [], item.get("concept_key"), allow_value=True
        )

    for item in bundle.metrics:
        table = str(item.get("grain_table") or "")
        _assert_table(report, tables, table, item.get("metric_key") or table)
        field = str(item.get("field") or "")
        ft, fc = physical_pair(field)
        if ft:
            _assert_table(report, tables, ft, field)
            _assert_column(report, catalog_columns(tables.get(ft) or {}), ft, fc, field)
        _check_code_evidence(
            report, index, item.get("evidence"), skip_code_check, str(item.get("metric_key") or "")
        )

    for item in bundle.scenarios:
        for hub in item.get("hubs") or []:
            table = str(hub.get("table") or "")
            _assert_table(report, tables, table, item.get("scenario_key") or table)
        for shared in item.get("shared") or []:
            table = str(shared.get("table") or "")
            _assert_table(report, tables, table, item.get("scenario_key") or table)

    return report


def _assert_table(
    report: ValidationReport, tables: dict[str, Any], table: str, target: Any
) -> None:
    if not table:
        report.add("TABLE_MISSING", str(target), "empty table name")
        return
    if table not in tables:
        report.add("TABLE_NOT_IN_DB", str(target), f"table {table!r} not in catalog.yaml")


def _assert_column(
    report: ValidationReport,
    columns: set[str],
    table: str,
    column: str,
    target: Any,
) -> None:
    if not column:
        report.add("FIELD_MISSING", str(target), f"{table} empty column")
        return
    if table and columns and column not in columns:
        report.add(
            "FIELD_NOT_IN_DB",
            str(target),
            f"column {table}.{column} not in catalog.yaml",
        )


def _check_field_targets(
    report: ValidationReport,
    tables: dict[str, Any],
    targets: Any,
    owner: Any,
    *,
    allow_value: bool = False,
) -> None:
    for raw in targets or []:
        text = str(raw or "").strip()
        table, rest = physical_pair(text)
        if allow_value and rest.count(".") == 1:
            # dictKey.VALUE or table.column.VALUE — physical check on table.column
            column = rest.split(".", 1)[0]
            if table in tables:
                _assert_column(
                    report, catalog_columns(tables.get(table) or {}), table, column, owner
                )
                continue
        if table in tables:
            _assert_column(report, catalog_columns(tables.get(table) or {}), table, rest, owner)
        elif "__" in table:
            # dictKey.VALUE — dict keys are not catalog tables
            continue
        else:
            _assert_table(report, tables, table, owner)


def _check_anchor(
    report: ValidationReport, tables: dict[str, Any], maps_to: str, owner: Any
) -> None:
    table, rest = physical_pair(maps_to)
    if not table:
        report.add("ANCHOR_MISSING", str(owner), "maps_to empty")
        return
    if table in tables:
        column = rest.split(".", 1)[0] if rest else ""
        _assert_column(report, catalog_columns(tables.get(table) or {}), table, column, owner)
        return
    if "__" in table:
        return
    report.add("TABLE_NOT_IN_DB", str(owner), f"maps_to table {table!r} not in catalog.yaml")


def _check_predicate_endpoints(
    report: ValidationReport, tables: dict[str, Any], target: str, predicate: Any
) -> None:
    text = str(predicate or "")
    for token in text.replace("=", " ").replace("(", " ").replace(")", " ").split():
        if "." in token and not token.startswith("'") and not token.startswith('"'):
            table, column = physical_pair(token.strip(","))
            if table in tables:
                _assert_column(
                    report, catalog_columns(tables[table]), table, column.split()[0], target
                )


def _check_code_evidence(
    report: ValidationReport,
    index: dict[str, list[Path]],
    evidence: Any,
    skip: bool,
    target: str,
) -> None:
    parsed = parse_code_path(str(evidence or ""))
    if parsed is None:
        return
    if skip:
        return
    if not index:
        report.add(
            "CODE_PATH_UNCHECKED",
            target,
            "code_root missing; cannot verify code_path",
            evidence=str(evidence),
            severity="warning",
        )
        return
    filename, line = parsed
    matches = _lookup_code(index, filename)
    if not matches:
        report.add(
            "CODE_PATH_MISSING",
            target,
            f"code file not found: {filename}",
            evidence=str(evidence),
        )
        return
    path = matches[0]
    if line is not None:
        count = sum(1 for _ in path.open(encoding="utf-8", errors="replace"))
        if line > count:
            report.add(
                "CODE_PATH_LINE",
                target,
                f"{path.name} has {count} lines; requested {line}",
                evidence=str(evidence),
            )


def _code_index(root: Path) -> dict[str, list[Path]]:
    index: dict[str, list[Path]] = {}
    if not root.exists():
        return index
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in {".java", ".xml", ".kt"}:
            continue
        index.setdefault(path.name, []).append(path)
        rel = path.as_posix()
        index.setdefault(rel, []).append(path)
    return index


def _lookup_code(index: dict[str, list[Path]], filename: str) -> list[Path]:
    needle = filename.replace("\\", "/")
    if needle in index:
        return index[needle]
    name = Path(needle).name
    matches = list(index.get(name) or [])
    if len(matches) > 1:
        preferred = [p for p in matches if "customer-management" in p.as_posix()]
        if preferred:
            return preferred
    return matches


def dict_key_of(body: dict[str, Any]) -> str:
    table = str(body.get("table") or "")
    column = str(body.get("column") or "")
    return dict_page_key(table, column, body.get("dict"))
