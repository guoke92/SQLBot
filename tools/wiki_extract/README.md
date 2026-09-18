# L0 库侧基础 Wiki 提取

旁路工具：从 **MySQL DSN** 编译 draft 表页 / 字典候选 / `instance_index.yaml` / REVIEW。  
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

只跑实例清单（连库或从已有 `profile_instance.yaml` 组装，不跑 LLM）：

```bash
backend/venv/bin/python -m tools.wiki_extract instance \
  --out docs/wiki-knowledge/pplatform/l0 \
  --database lowcode_pplatform
```

可选：`--tables t1,t2`、`--skip-profile`、`--db-url`（覆盖 env）。

L0 编译默认在有 LLM 配置时做 **字典甄别（dict_keep / dict_hold / drop）+ 注释派生 label + 近义列 + JOIN 真实性初审**（keep / label / JOIN 仍是 proposed，不是 confirmed；候选边全留）。实例清单走独立管线，不进 LLM 四档：

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
  _raw/profile_instance.yaml
  _raw/overlap.yaml
  _raw/llm_judge.yaml
  tables/*.md
  dicts/*.md
  instance_index.yaml
  _index.md
  _log.md
  .runs/l0/reviews.yaml
```

emit 会清空目标目录下历史遗留的 `enums/` 与 `value_index.yaml`。不再生成这两类产物。

L0 JOIN 口径（端点排除、类型对齐、`join_role` identity/business_code、likely/unlikely 阈值）只在 [`join_policy.py`](join_policy.py)；名称提名、值域探测、LLM propose 共用 `may_nominate_join`，不要在各层再写一份黑名单。码对码（含 `product_code`）是合法 EQUI_JOIN；同父表已有主键边时码边 `priority=secondary`。

字典甄别只在 [`dict_triage.py`](dict_triage.py)：LLM 初判 → 机械检查 → 不一致或测库单值则 LLM 复核。判决只有 `dict_keep | dict_hold | drop`。单值允许 drop（测库污染），不全码表 keep/hold。实例清单只在 [`instance_index.py`](instance_index.py)：业务列提名 + 审计/时间/主键/`*_id`/PII/密钥硬排除 + UUID/哈希/JSON 取值跳过 + TopK，写出 `instance_index.yaml`。两条管线互不共用 verdict；同一列可以同时有 dict 页和实例条目。

L0 JOIN 初审在 [`join_policy.py`](join_policy.py) 的 `seal_join_preview`：值域 likely **且** 列名/注释有关联语义才给边 `likely`；仅值域契合保留边为 `unknown`。

L0 不做：认证 JOIN、代码 confirmed label、主引用边、`inactive` 猜测、`default_filter` confirmed、共写、scenario。身份束关系全部 `proposed` 并进 `unverified_join`（含表族缩写列 `rule_info_id`→`funding_rule_info`、以及 `ref_本表_对端表`）。`label` 仅来自列注释映射。字典页键为 `表__字段`（不要 `::`）；表/字典页互链 `[[wikilink]]`。页面 `ground:relation` 写出 `authenticity` / `name_evidence` / `overlap` / `join_role` / `priority` 并按 authenticity 分组。emit 落 `_raw/{catalog,profile,profile_instance,overlap,llm_judge}.yaml`。

## L1（源码 + 文档中间成果）

第一步由 Coding Agent 按 [docs/wiki/l1_agent_playbook.md](../../docs/wiki/l1_agent_playbook.md) 写入 `_raw/l1_intermediate/`（Schema：[docs/wiki/l1_intermediate.md](../../docs/wiki/l1_intermediate.md)）。第二步纯程序：

```bash
backend/venv/bin/python -m tools.wiki_extract l1 \
  --l0 docs/wiki/v2 \
  --out docs/wiki/v3 \
  --code-root /path/to/pplatform-web
```

`--skip-code-check` 跳过 `code_path` 文件存在性（测试用）。出门仍全部 `status: draft`。拒绝写入 `wiki-pages*`。L1 会重渲染全部表页并写出可召回概念页 `concepts/catalog_summary.md`（每表一行压缩骨架）。

## 测试

```bash
backend/venv/bin/python -m pytest tools/wiki_extract/tests -v
```

不连真库。真库跑通不是 CI 门槛。
