# 问数 Wiki（契约）

> 日期：2026-09-15 · 状态：**唯一权威 SCHEMA**
>
> 给 **SQL 规划器 + 确定性门禁** 的编译产物。本目录定义对象怎么组合；实现跟着契约走，不以代码缺字段缩水。

## 读哪一份

先读 [architecture.md](architecture.md) 的对象图，再按面查细节：

| 文档 | 管什么 |
|---|---|
| [architecture.md](architecture.md) | 对象组合、原则、状态机、投影代数、规划器法律 |
| [pages.md](pages.md) | 语法、ground、claim_path、REVIEW、lint 码 |
| [extract.md](extract.md) | 怎么把库/源码/文档填进对象图（ingest/lint/promote） |
| [runtime.md](runtime.md) | 一次 query 的顺序：掩膜、召回、投影、门禁、澄清 |

冲突时：**原则与组合 → architecture；字段名 → pages；编译步骤 → extract；请求顺序 → runtime。** 不要用代码压契约，也不要在四份里各写一套 JOIN/澄清。

硬约束：绑定后运行时不得用 catalog 否定 wiki；提取不得拿旧问数 wiki 当生成上下文；ingest 不得写 `published`。

## 生命周期

```
ingest：raw → draft + REVIEW + _log
lint：结构门禁 + 语义健康（不改 published 正文）
promote：draft → published | retired     ← 唯一发布
query：published ∩ 勾选 → 投影代数 → JOIN/grain 门禁 → 澄清或 SQL
        好答案 → 下一次 ingest
```

语料文件在 `docs/wiki-knowledge/<system>/`。**契约只在本目录。**

## 实现对照（非契约）

| 面 | 代码（可能滞后） |
|---|---|
| 解析 / lint | `backend/apps/knowledge/wiki/contract.py` |
| 切块 | `chunker.py` |
| 召回 | `recall.py`、`apps/chat/steps/wiki_recall.py` |
| schema 投影 | `apps/chat/steps/wiki_schema.py` |
| 提取 | `apps/knowledge/wiki/` |
| L0 提取 | `tools/wiki_extract/`：`tables/`、`dicts/`、`instance_index.yaml`、`_raw/` 五件套 |
| L1 中间成果 | [l1_intermediate.md](l1_intermediate.md)（Coding Agent YAML） |
| L1 走读 SOP | [l1_agent_playbook.md](l1_agent_playbook.md) |
| L1 聚合渲染 | `tools/wiki_extract l1`：`reconcile.py` + `emitter.py`（9 类页，draft） |

语料切流是运维，不是 SCHEMA 条款。

## 废止

下列不再权威（多已迁至仓库根 `.tmp/`，冲突以本目录为准）：旧 `docs/wiki-knowledge/` 方案/指南/链路契约；`docs/wiki页面契约-spec-v0.md`；`docs/知识体系目标架构-v3.1.md`；`docs/业务系统知识库提取与构建指南-v1.md`；KnowledgePackage 11 步与 `knowledge-package submit`（只复用 `extract-*.py` 扫描脚本）。

**现行语料工作区：** `docs/wiki/v2`（L0+IR）→ `docs/wiki/v3`（L1 draft）。历史 `wiki-pages*` 在 `.tmp/`。运行时召回走 DB corpus，不依赖本地 pages 树。

**导入默认：** 管理端 / `KNOWLEDGE_WIKI_PAGES_DIRS` → `docs/wiki/v3`。若现场 `.env` 仍指向旧 `wiki-pages*`，请改为此路径，否则导入失败。
