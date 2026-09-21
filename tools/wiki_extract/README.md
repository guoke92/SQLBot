# L0 / L1 Wiki 提取

旁路工具：从 **MySQL DSN** 编译 L0 draft（表页 / 字典 / `instance_index`），再由 Coding Agent IR + `l1` 聚合成 L1 draft。

**工作区（现行）：**

| 阶段 | 目录 |
|---|---|
| L0 + IR | `docs/wiki/v2/`（含 `_raw/l1_intermediate/`） |
| L1 出门 | `docs/wiki/v3/` |
| 文档源 | `docs/wiki-knowledge/pplatform/req-index/` |

**边界：**

- **不**写入已迁走的 `wiki-pages*`（历史树在 `.tmp/`）
- **不**调用 `apps.knowledge.wiki.baseline|pipeline|ingest`（旧 pages 管线）
- 运行时召回走 **DB corpus + 向量**；`KNOWLEDGE_WIKI_PAGES_DIRS` 仅管理端导入默认（现为 `docs/wiki/v3`）

契约：[docs/wiki/extract.md](../../docs/wiki/extract.md)、[docs/wiki/pages.md](../../docs/wiki/pages.md)。页全部 `status: draft`。

## L0 用法

仓库根目录 + backend venv（`pymysql` + `pyyaml`）：

```bash
export WIKI_EXTRACT_DSN='mysql://user:pass@host:port/lowcode_pplatform'
backend/venv/bin/python -m tools.wiki_extract compile \
  --out docs/wiki/v2 \
  --database lowcode_pplatform
```

只扫库、不写页：

```bash
backend/venv/bin/python -m tools.wiki_extract introspect \
  --out docs/wiki/v2 \
  --database lowcode_pplatform
```

从已有 `_raw` 再编译（不连库；有 `overlap.yaml` 则合并值域复核）：

```bash
backend/venv/bin/python -m tools.wiki_extract compile \
  --from-raw docs/wiki/v2/_raw \
  --out docs/wiki/v2 \
  --skip-llm
```

值域探测 / 实例清单：

```bash
backend/venv/bin/python -m tools.wiki_extract overlap --out docs/wiki/v2 --database lowcode_pplatform
backend/venv/bin/python -m tools.wiki_extract instance --out docs/wiki/v2 --database lowcode_pplatform
```

可选：`--tables t1,t2`、`--skip-profile`、`--db-url`（覆盖 env）。

带 LLM 字典甄别：

```bash
export WIKI_EXTRACT_LLM_BASE_URL='https://api.example.com/v1'
export WIKI_EXTRACT_LLM_API_KEY='...'
export WIKI_EXTRACT_LLM_MODEL='qwen-plus'
backend/venv/bin/python -m tools.wiki_extract compile \
  --from-raw docs/wiki/v2/_raw \
  --out docs/wiki/v2 \
  --llm
```

`--skip-llm` 只跑机械启发式。判断写入 `_raw/llm_judge.yaml`。

示例配置（无密钥）：[`profiles/pplatform.example.yaml`](profiles/pplatform.example.yaml)。

## L0 出门

```
docs/wiki/v2/
  _raw/catalog.yaml
  _raw/profile.yaml
  _raw/profile_instance.yaml
  _raw/overlap.yaml
  _raw/llm_judge.yaml
  _raw/l1_intermediate/   # Agent 手写 IR（compile 不擦除）
  tables/*.md
  dicts/*.md
  instance_index.yaml
  _index.md
  _log.md
  .runs/l0/reviews.yaml
```

emit 会清空目标下历史遗留的 `enums/` 与 `value_index.yaml`。不再生成这两类产物。

L0 JOIN / 字典甄别 / 实例清单口径见 `join_policy.py`、`dict_triage.py`、`instance_index.py`（与契约 §4① 一致）。

## L1

Coding Agent 按 [docs/wiki/l1_agent_playbook.md](../../docs/wiki/l1_agent_playbook.md) 写 `_raw/l1_intermediate/`，再：

```bash
backend/venv/bin/python -m tools.wiki_extract l1 \
  --l0 docs/wiki/v2 \
  --out docs/wiki/v3 \
  --code-root /path/to/pplatform-web
```

出门仍全部 `status: draft`。拒绝写入 `wiki-pages*`。会写出 `concepts/catalog_summary.md`。

导入 DB 前请明确是否需 promote 为 `published`（运行时默认只召回 published；若环境已放行 draft 则可直接导入 `docs/wiki/v3`）。

## 测试

```bash
backend/venv/bin/python -m pytest tools/wiki_extract/tests -v
```
