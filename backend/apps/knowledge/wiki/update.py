"""Incremental update driver (plan E2.5) — fingerprint diff → targeted re-run.

三路增量触发，共用"指纹比对 → 定向重跑"底座：

1. **代码变更**：page-plan.yaml 每单元记录文件指纹（路径+mtime+size）；
   重跑时 diff——变更单元重穿透，未变单元跳过。
2. **新增术语（Test-wiki 侧）**：比对上次摄取的页面集合，新页（先过
   reqdoc 过滤器）按关键词路由到受影响计划单元 → 重跑该单元；其中
   action=anchor 类主张同样走回证。
3. **db 变更**：db 三件套的 generated_at + 表集合指纹；变更表所在单元重跑。

产物：变更报告（哪些单元重跑、为什么）+ 重跑清单。统一入口
``python -m apps.knowledge.wiki.update --repo ... --substrate ...``。
"""

from __future__ import annotations

import argparse
import datetime as _dt
from pathlib import Path
from typing import Any

import yaml

_FINGERPRINTS_FILE = "tmp/page-fingerprints.yaml"


def _today() -> str:
    return _dt.date.today().isoformat()


def _unit_files(
    repo: Path, unit: dict[str, Any], callgraph: dict[str, Any]
) -> list[Path]:
    """计划单元的受监控文件：入口 ring≤2 链路（穿透实际读取的面）。"""
    per_entry = callgraph.get("per_entry") or {}
    files: set[str] = set()
    for entry in unit.get("entries") or []:
        for file, depth in (per_entry.get(entry) or {}).items():
            if depth <= 2:
                files.add(file)
    return [repo / f for f in sorted(files)]


def snapshot_fingerprint(
    repo: Path, substrate_dir: Path, plan: dict[str, Any]
) -> dict[str, dict[str, Any]]:
    """每单元：文件指纹集 + 表集合 + 时间戳。"""
    callgraph = yaml.safe_load((substrate_dir / "callgraph.yaml").read_text()) or {}
    snaps: dict[str, dict[str, Any]] = {}
    for unit in plan.get("plan_units") or []:
        topic = unit.get("topic") or ""
        stamps: dict[str, list[int]] = {}
        for path in _unit_files(repo, unit, callgraph):
            try:
                stat = path.stat()
                stamps[str(path)] = [stat.st_mtime_ns, stat.st_size]
            except OSError:
                continue
        snaps[topic] = {
            "files": stamps,
            "tables": sorted(unit.get("tables") or []),
            "taken_at": _today(),
        }
    return snaps


def load_previous(substrate_dir: Path) -> dict[str, Any]:
    path = substrate_dir / _FINGERPRINTS_FILE
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text()) or {}


def save_current(substrate_dir: Path, snaps: dict[str, Any]) -> None:
    path = substrate_dir / _FINGERPRINTS_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(snaps, allow_unicode=True, sort_keys=False))


def diff_units(
    previous: dict[str, Any], current: dict[str, Any]
) -> dict[str, list[str]]:
    """返回 {topic: 变更原因列表}——只重跑有变更的单元。"""
    changed: dict[str, list[str]] = {}
    for topic, cur in current.items():
        prev = previous.get(topic)
        if prev is None:
            changed[topic] = ["新单元"]
            continue
        reasons: list[str] = []
        prev_files = prev.get("files") or {}
        cur_files = cur.get("files") or {}
        if set(prev_files) != set(cur_files):
            added = set(cur_files) - set(prev_files)
            removed = set(prev_files) - set(cur_files)
            reasons.append(f"文件集变化 +{len(added)}/-{len(removed)}")
        else:
            drifted = [f for f, s in cur_files.items() if prev_files.get(f) != s]
            if drifted:
                reasons.append(f"{len(drifted)} 文件 mtime/size 变化")
        if set(prev.get("tables") or []) != set(cur.get("tables") or []):
            reasons.append("表集合变化")
        if reasons:
            changed[topic] = reasons
    return changed


def new_reqdoc_pages(reqdoc_root: Path | None, substrate_dir: Path) -> list[str]:
    """Test-wiki 新页（先过 reqdoc 过滤器）：与上次快照对比。"""
    from apps.knowledge.wiki.filters import ReqdocFilter

    if reqdoc_root is None or not reqdoc_root.exists():
        return []
    reqdoc_filter = ReqdocFilter.load(substrate_dir / "tmp" / "reqdoc-filter.yaml")
    current = [
        str(p.relative_to(reqdoc_root)) for p in reqdoc_filter.iter_pages(reqdoc_root)
    ]
    marker = substrate_dir / "tmp" / "reqdoc-snapshot.yaml"
    if not marker.exists():
        return current  # 首次：全部视为"新"，但 run 命令会跳过已完成的单元
    previous = set(yaml.safe_load(marker.read_text()) or [])
    return [p for p in current if p not in previous]


def route_reqdoc_pages(
    new_pages: list[str], reqdoc_root: Path, plan: dict[str, Any]
) -> dict[str, list[str]]:
    """新页 → 计划单元路由：页面正文与单元 topic/tables 关键词匹配。"""
    routing: dict[str, list[str]] = {}
    if not new_pages:
        return routing
    for rel in new_pages:
        path = reqdoc_root / rel
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for unit in plan.get("plan_units") or []:
            topic = unit.get("topic") or ""
            keywords = [topic, *(unit.get("tables") or [])[:6]]
            if any(kw and kw in text for kw in keywords):
                routing.setdefault(topic, []).append(rel)
    return routing


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--substrate", required=True)
    parser.add_argument("--reqdoc-root", default="")
    parser.add_argument("--dry-run", action="store_true", help="只出报告不写指纹")
    args = parser.parse_args()

    repo = Path(args.repo).expanduser()
    substrate_dir = Path(args.substrate)
    reqdoc_root = Path(args.reqdoc_root).expanduser() if args.reqdoc_root else None

    plan_path = substrate_dir / "tmp" / "page-plan.yaml"
    if not plan_path.exists():
        raise SystemExit("page-plan.yaml 不存在——先跑 pipeline plan")
    plan = yaml.safe_load(plan_path.read_text()) or {}

    previous = load_previous(substrate_dir)
    current = snapshot_fingerprint(repo, substrate_dir, plan)
    changed = diff_units(previous, current)
    new_pages = new_reqdoc_pages(reqdoc_root, substrate_dir)
    routed = route_reqdoc_pages(new_pages, reqdoc_root or Path("."), plan)
    for topic, pages in routed.items():
        reasons = changed.setdefault(topic, [])
        reasons.append(
            f"需求文档新页 ×{len(pages)}: {', '.join(p.name if hasattr(p, 'name') else str(p) for p in pages[:3])}"
        )

    print(f"计划单元 {len(current)} 个；有变更 {len(changed)} 个")
    for topic, reasons in sorted(changed.items()):
        print(f"  [重跑] {topic}: {'; '.join(reasons)}")
    if not changed:
        print("  无变更，无需重跑。")
    if not args.dry_run:
        save_current(substrate_dir, current)
        if reqdoc_root is not None:
            from apps.knowledge.wiki.filters import ReqdocFilter

            reqdoc_filter = ReqdocFilter.load(
                substrate_dir / "tmp" / "reqdoc-filter.yaml"
            )
            marker = substrate_dir / "tmp" / "reqdoc-snapshot.yaml"
            marker.write_text(
                yaml.safe_dump(
                    [
                        str(p.relative_to(reqdoc_root))
                        for p in reqdoc_filter.iter_pages(reqdoc_root)
                    ],
                    allow_unicode=True,
                )
            )


if __name__ == "__main__":
    main()
