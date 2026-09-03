"""Field-role evidence extraction (plan 补强：字段角色标注).

从 mapper XML（确定性）+ service 写值点（继承 callgraph 线索）抽取每个字段的
角色证据：query（查询条件）/ result（结果列）/ updated（修改字段）/ 统计字段。

强关联绑定（签收金额↔签收日期类）：同一次 INSERT/UPDATE 里 set 的同表多字段
→ `set_weight: <组名>`（同组字段同时写入）。组名 = 首字段名派生（如
`sign_amount` → `sign_amount_group`），同一 mapper 方法内的绑定共享组名。

Usage::

    backend/venv/bin/python -m apps.knowledge.wiki.field_roles \
        --repo ~/IdeaProjects/pplatform-web \
        --out docs/wiki-knowledge/pplatform/substrate/field-roles.yaml
"""

from __future__ import annotations

import argparse
import re
from collections import defaultdict
from pathlib import Path

import yaml

WHERE_RE = re.compile(
    r"\b(?:where|and|or)\s+(\w+)\.(\w+)\s*(?:=|in|like|>|<|>=|<=|!=|<>)", re.I
)
SELECT_TABLE_RE = re.compile(r"\b(?:from|join|into|update)\s+([a-z][a-z0-9_]+)\b", re.I)
# MyBatis <insert>/<update> 内的 set 调用（service 层）：field: value
_SET_RE = re.compile(r"\.set(\w+)\(")
_AMOUNT_TIME_HINTS = re.compile(r"(amount|money|fee|date|time|qty|count|num)_?$")


def _mapper_tables(text: str) -> set[str]:
    return {m.group(1) for m in SELECT_TABLE_RE.finditer(text)}


def extract(repo: Path) -> dict[str, dict[str, list[str]]]:
    """表 → 字段 → 角色证据列表（query/result）。纯 dict 输出（YAML 安全）。"""
    roles: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    for mapper in repo.rglob("*Mapper.xml"):
        text = mapper.read_text(encoding="utf-8", errors="ignore")
        tables = _mapper_tables(text)
        if not tables:
            continue
        for m in WHERE_RE.finditer(text):
            col = m.group(2).lower()
            if col in ("1",) or col.startswith("db_tenant"):
                continue
            for table in tables:
                roles[table][col].add("query")  # WHERE 列在任意 join 表上：保守绑定
        for select in re.findall(r"SELECT\s+([\w,.\s*]+?)\s+FROM", text, re.I):
            for raw in select.split(","):
                col = raw.strip().split(".")[-1].split(" ")[0].lower()
                if col and col != "*" and not col.startswith("db_tenant"):
                    for table in tables:
                        roles[table][col].add("result")
    return {
        t: {f: sorted(r) for f, r in fields.items()}
        for t, fields in sorted(roles.items())
    }


def extract_groups(repo: Path) -> dict[str, list[dict]]:
    """同表同方法内连续 set 的字段组（强关联绑定，签收金额↔签收日期类）。

    service 层：一个方法体内 `.setXxx()` 的相邻字段对，且语义上金额/日期/
    数量类字段相邻出现 → 组。确定性规则，LLM 在此之上只补业务命名。
    排除：测试类/启动回调/框架生命周期方法（无业务语义）。"""
    groups: dict[str, list[dict]] = defaultdict(list)
    _CLASS = re.compile(r"class\s+(\w+)")
    _METHOD = re.compile(r"(?:public|protected|private)\s+[\w<>,\s\[\]]+\s+(\w+)\s*\(")
    _SKIP_CLASS = re.compile(r"(Test|Profile|Config|Application|Listener|Thread)$")
    _SKIP_METHOD = re.compile(
        r"(onApplication|afterPropertiesSet|destroy|run\b|main\b|init\b|stop\b)", re.I
    )
    for path in repo.rglob("*.java"):
        text = path.read_text(encoding="utf-8", errors="ignore")
        if ".set" not in text or "/test/" in str(path) or "/Test" in path.name:
            continue
        cls = _CLASS.search(text)
        if cls and _SKIP_CLASS.search(cls.group(1)):
            continue
        methods: list[tuple[str, str]] = []
        matches = list(_METHOD.finditer(text))
        for i, m in enumerate(matches):
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            methods.append((m.group(1), text[m.start() : end]))
        for method_name, body in methods:
            if _SKIP_METHOD.search(method_name):
                continue
            sets = [m.group(1) for m in _SET_RE.finditer(body)]
            fields = [_camel_to_snake(s) for s in sets]
            for i in range(len(fields) - 1):
                a, b = fields[i], fields[i + 1]
                if a == b:
                    continue
                if _AMOUNT_TIME_HINTS.search(a) and _AMOUNT_TIME_HINTS.search(b):
                    group_name = f"{a}_group"
                    groups[cls.group(1) if cls else path.stem].append(
                        {"method": method_name, "fields": [a, b], "group": group_name}
                    )
    return dict(groups)


def _camel_to_snake(name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    repo = Path(args.repo).expanduser()
    roles = extract(repo)
    groups = extract_groups(repo)
    payload = {
        "schema_version": "1.0",
        "note": "字段角色证据（query/result/update）+ 强关联字段组 — tmp 中间产物",
        "roles": roles,
        "field_groups": groups,
    }
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(
        yaml.safe_dump(payload, allow_unicode=True, sort_keys=False)
    )
    n_q = sum(1 for t in roles.values() for f, r in t.items() if "query" in r)
    n_g = sum(len(g) for g in groups.values())
    print(f"tables={len(roles)} query-evidence-fields={n_q} groups={n_g} -> {args.out}")


if __name__ == "__main__":
    main()
