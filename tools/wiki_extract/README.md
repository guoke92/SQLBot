# L0 库侧基础 Wiki 提取

旁路工具：从 **MySQL DSN** 编译 draft 表页 / 枚举候选 / `value_index` / REVIEW。  
**不**调用、不修改 `.cursor/skills/knowledge-extraction/scripts/`、`apps.knowledge.wiki.baseline|pipeline|ingest`。  
**不**写入 `wiki-pages/`、`wiki-pages-v2/`、`wiki-pages-v3/`、`docs/wiki-knowledge/*/db/`。  
**不**改运行时 `KNOWLEDGE_WIKI_PAGES_DIRS`。

契约：[docs/wiki/extract.md](../../docs/wiki/extract.md) §4 ①、[docs/wiki/pages.md](../../docs/wiki/pages.md)。页全部 `status: draft`。

## 用法

在仓库根目录、使用 backend venv（需要 `pymysql` + `pyyaml`）：

```bash
export WIKI_EXTRACT_DSN='mysql://user:pass@host:port/lowcode_pplatform'
backend/venv/bin/python -m tools.wiki_extract compile \
  --out docs/wiki-knowledge/pplatform/l0 \
  --database lowcode_pplatform
```

只扫库、不写页：

```bash
backend/venv/bin/python -m tools.wiki_extract introspect \
  --out docs/wiki-knowledge/pplatform/l0 \
  --database lowcode_pplatform
```

从已有 `_raw` 再编译（不连库）：

```bash
backend/venv/bin/python -m tools.wiki_extract compile \
  --from-raw docs/wiki-knowledge/pplatform/l0/_raw \
  --out docs/wiki-knowledge/pplatform/l0
```

可选：`--tables t1,t2`、`--skip-profile`、`--db-url`（覆盖 env）。

L0 编译默认在有 LLM 配置时做 **枚举去留 + 语义字段簇 + 近义列** 初审（`keep` 仍是 proposed，不是 confirmed）：

```bash
export WIKI_EXTRACT_LLM_BASE_URL='https://api.example.com/v1'
export WIKI_EXTRACT_LLM_API_KEY='...'
export WIKI_EXTRACT_LLM_MODEL='qwen-plus'
backend/venv/bin/python -m tools.wiki_extract compile \
  --from-raw docs/wiki-knowledge/pplatform/l0/_raw \
  --out docs/wiki-knowledge/pplatform/l0 \
  --llm
```

`--skip-llm` 只跑机械启发式。判断写入 `_raw/llm_judge.yaml`。

pplatform 示例配置（无密钥）：[`profiles/pplatform.example.yaml`](profiles/pplatform.example.yaml)。

## 出门

```
<out>/
  _raw/catalog.yaml
  _raw/profile.yaml
  tables/*.md
  enums/*.md
  value_index.yaml
  _index.md
  _log.md
  .runs/l0/reviews.yaml
```

L0 不做：认证 JOIN、代码 label、`default_filter` confirmed、共写、scenario。身份束关系与 LLM/前缀字段簇均为 `proposed` 并进 REVIEW。

## 测试

```bash
backend/venv/bin/python -m pytest tools/wiki_extract/tests/test_l0_compile.py -v
```

不连真库。真库跑通不是 CI 门槛。
