---
name: knowledge-extraction
description: >-
  SQLBot 源码/库扫描辅助技能。从目标 Java + MyBatis-Plus 仓库跑 extract-* 脚本，
  产出 catalog / enums / relationships / callgraph 等参考基线，供问数 Wiki L0/L1
  （docs/wiki + tools.wiki_extract）对照。当用户需要扫描表目录、枚举、JOIN 候选、
  调用图，或维护 wiki 知识提取扫描基线时使用。不要产出 KnowledgePackage 或 submit。
---

# SQLBot 知识提取扫描（辅助）

## 权威路径（先读这个）

| 用途 | 路径 |
|---|---|
| Wiki 契约 | [`docs/wiki/`](../../../docs/wiki/README.md) |
| L0/L1 出门 | [`tools/wiki_extract/`](../../../tools/wiki_extract/README.md) → `docs/wiki/v2` → `docs/wiki/v3` |
| L1 Agent SOP | [`docs/wiki/l1_agent_playbook.md`](../../../docs/wiki/l1_agent_playbook.md) |
| 文档源 | `docs/wiki-knowledge/pplatform/req-index/` |

**本 skill 只提供扫描脚本。** 问数知识主路径是 Wiki 页 + DB 召回，**不是** KnowledgePackageV2 / `knowledge-package submit`（CLI 已迁 `.tmp/`）。

## 权威顺序

```
库字段实际值 > 代码读写(service/dao/mapper) > 文档主张 > 扫描基线
```

文档不赢代码；关系默认 `proposed`，有 `code_path` 验证才可 `confirmed`（见 wiki 契约）。

## 扫描脚本（本目录 `scripts/`）

| 脚本 | 产物 |
|---|---|
| `extract-catalog.py` | `@TableName` 表/字段目录 |
| `extract-enums.py` | Java 枚举 dictKey + 显示名 |
| `extract-relationships.py` | Mapper JOIN / 静态候选 |
| `extract-callgraph.py` | 入口可达性 |
| `extract-dbcatalog.py` | Spring 配置连库 introspect（可选） |

示例（仓库根）：

```bash
REPO=/path/to/pplatform-web
RAW=docs/wiki/v2/_raw/scanner
mkdir -p "$RAW/db"
backend/venv/bin/python .cursor/skills/knowledge-extraction/scripts/extract-catalog.py "$REPO" -o "$RAW/extract-catalog.yaml"
backend/venv/bin/python .cursor/skills/knowledge-extraction/scripts/extract-enums.py "$REPO" -o "$RAW/extract-enums.yaml"
backend/venv/bin/python .cursor/skills/knowledge-extraction/scripts/extract-relationships.py "$REPO" -o "$RAW/extract-relationships.yaml"
backend/venv/bin/python .cursor/skills/knowledge-extraction/scripts/extract-callgraph.py "$REPO" -o "$RAW/callgraph.yaml"
```

硬约束与枚举/关系细节见同目录 [`reference.md`](reference.md)（历史 KnowledgePackage 条款仅作扫描语义参考，**勿再 assemble/submit 单元包**）。

## Wiki 主流程（摘要）

```bash
export WIKI_EXTRACT_DSN='mysql://…'
backend/venv/bin/python -m tools.wiki_extract compile --out docs/wiki/v2 --database lowcode_pplatform
# Agent 按 l1_agent_playbook 写 docs/wiki/v2/_raw/l1_intermediate/
backend/venv/bin/python -m tools.wiki_extract l1 --l0 docs/wiki/v2 --out docs/wiki/v3 --code-root "$REPO"
```

管理端导入默认：`docs/wiki/v3`。运行时召回绑定后的 DB corpus。
