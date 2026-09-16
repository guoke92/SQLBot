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

从已有 `_raw` 再编译（不连库；有 `overlap.yaml` 则合并值域复核）：

```bash
backend/venv/bin/python -m tools.wiki_extract compile \
  --from-raw docs/wiki-knowledge/pplatform/l0/_raw \
  --out docs/wiki-knowledge/pplatform/l0
```

只跑值域探测（连库，写出 `_raw/overlap.yaml`，不改页）：

```bash
backend/venv/bin/python -m tools.wiki_extract overlap \
  --out docs/wiki-knowledge/pplatform/l0 \
  --database lowcode_pplatform
```

可选：`--tables t1,t2`、`--skip-profile`、`--db-url`（覆盖 env）。

L0 编译默认在有 LLM 配置时做 **枚举去留 + 注释派生 label + 语义字段簇 + JOIN 真实性初审**（keep / label / JOIN 仍是 proposed，不是 confirmed；候选边全留）：

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
  _raw/overlap.yaml
  tables/*.md
  enums/*.md
  value_index.yaml
  _index.md
  _log.md
  .runs/l0/reviews.yaml
```

L0 JOIN 口径（端点排除、类型对齐、拷贝码、likely/unlikely 阈值）只在 [`join_policy.py`](join_policy.py)；列名启发式、值域探测、LLM 初审共用，不要在各层再写一份。

L0 不做：认证 JOIN、代码 confirmed label、主引用边、`inactive` 猜测、`default_filter` confirmed、共写、scenario。身份束关系全部 `proposed` 并进 `unverified_join`（含表族缩写列 `rule_info_id`→`funding_rule_info`、以及 `ref_本表_对端表`）。`label` 仅来自列注释映射。枚举页键为 `表::字段`；表/枚举页互链 `[[wikilink]]`。

## 测试

```bash
backend/venv/bin/python -m pytest tools/wiki_extract/tests/test_l0_compile.py tools/wiki_extract/tests/test_l0_overlap.py tools/wiki_extract/tests/test_l0_llm_refine.py -v
```

不连真库。真库跑通不是 CI 门槛。
