# L1 中间成果 Schema（离散 YAML）

> 权威语法仍是 [pages.md](pages.md)。本文件只定义 **Coding Agent 第一步** 写进 `_raw/l1_intermediate/` 的小文件，**不是** Wiki 页面。第二步由 `tools/wiki_extract l1` 聚合、校验、升权并渲染 9 类页。

走读 SOP：[l1_agent_playbook.md](l1_agent_playbook.md)。

## 目录

```
<l0>/_raw/l1_intermediate/
├── code/<domain>/
│   ├── table_enhancements.yaml
│   ├── processes.yaml
│   ├── calibers_rules.yaml
│   ├── relations_dicts.yaml
│   ├── scenarios.yaml          # 可选
│   └── traces/<op>.trace.yaml  # 可选
└── docs/
    ├── <topic>_concepts.yaml
    ├── <topic>_metrics.yaml
    └── <topic>_display.yaml
```

- 单文件建议 **100–400 行**。禁止把整仓塞进一个 YAML。
- 文件名即 kind；也可显式写 `kind:`。
- 物理名必须是 catalog 里的 `表` / `表.字段`。字典页键是 `表__字段`。
- `evidence` 只许：`code_path:<file>[:<line>]`、`database_schema:`、`database_profile:`、`document_claim:`。
- 无 `code_path` 的 JOIN / 默认过滤 / 共写 / 流转 **不得** 在第二步升为 `confirmed`。
- `dict_labels` 可用 `document_claim:`（码 ⊆ L0 values，保持 `proposed`）；仅 `code_path` 可升 `confirmed`。
- Catalog Summary 由第二步生成；改 `_TABLE_PROFILES` 时短语必须对得上列注释，否则 `CATALOG_BLURB_UNGROUNDED`。

模板：[`tools/wiki_extract/l1/templates/`](../../tools/wiki_extract/l1/templates/)。

## 源码侧

### `table_enhancements.yaml`

```yaml
kind: table_enhancements
domain: cust
tables:
  cust_company_info:
    default_filter:
      predicate: "cust_company_info.enable = 'Y'"
      evidence: code_path:CustCompanyIfoEnchanceService.java:653
    written_with_groups:
      - fields: [cust_build_status, cust_status]
        evidence: code_path:CustCompanyInfoDao.java:58
```

`written_with_groups` 只列本领域要升权的共写组。全库骨架不在 IR 里手写，由第二步从 catalog 生成 `concepts/catalog_summary`。

### `processes.yaml`

钉 **同一物理列**。`process_key` 建议 `表__字段`。

### `calibers_rules.yaml`

- `calibers[]`：`caliber_key`、可执行 `predicate`、`field_targets`、`boundary`
- `rules[]`：`rule_key`、`impact` ∈ `write_constraint | query_constraint | default_value`、`content`、`field_targets`
- 不要把 `default_filter` 再写成 rule

### `relations_dicts.yaml`

- `confirmed_relations[]`：`left` / `right` 为 `表.字段`；`type` 默认 `EQUI_JOIN`。与 L0 同 FK 列但另一端不同的 proposed 边，第二步标 `disputed` 并写 `JOIN_CONFLICT`。varchar 存 bigint 时写 `cast: varchar←bigint`。
- `dict_labels.<表__字段>`：`table`、`column`、`values.<CODE>.{label, evidence}`
- label 必须来自枚举 `displayName` / 常量注释，禁止脑补

### `traces/*.trace.yaml`（可选）

一次 Controller→DB 走读快照。可内嵌 `scenario:`，第二步会收成 scenario 页。

## 文档侧

### `*_concepts.yaml`

`maps_to` 唯一锚：`表.字段` 或 `dictKey.VALUE`。易混必须成对写 `also_confused_with` + `adjudication`（`boundary` | `synonym`）。

### `*_metrics.yaml`

口径在 caliber 上；这里只加 `aggregation` + `grain_table` + `field`。禁止第二套 filter。

### `*_display.yaml`

版本史、排期。整页 `recall: false`，不进向量。

## 第二步命令

```bash
backend/venv/bin/python -m tools.wiki_extract l1 \
  --l0 docs/wiki/v2 \
  --out docs/wiki/v3 \
  --code-root /path/to/pplatform-web
```

覆盖检查（不写页）：

```bash
backend/venv/bin/python -m tools.wiki_extract l1-coverage \
  --l0 docs/wiki/v2 \
  --prefix cust \
  --req-index docs/wiki-knowledge/pplatform/req-index
```

出门仍全部 `status: draft`。不写 `wiki-pages*`，不改 `KNOWLEDGE_WIKI_PAGES_DIRS`。
