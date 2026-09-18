# 问数 Wiki 页面契约

> 权威：[README.md](README.md) · 对象怎么组合见 [architecture.md](architecture.md)
>
> 本文件是**语法**：一页怎么写、ground 怎么解析、主张怎么寻址。对象职责不在此重复。不随某一版解析器缺字段而缩水。

## 1. 格式原则

1. **零信任解析。** 语法失败 → 丢该块 + 警告，不猜测、不部分采纳。
2. **程序管结构，LLM 管内容。** `page_key` / `created` / `updated` / `sources` / `contract_version` 程序盖章；页 `status` 只经 promote。ingest 不得写 `published`。
3. **物理名锚定。** 跨页只写 `表.字段`、`dictKey.VALUE`。
4. **向后兼容。** 新增可选字段不升版；改语义必升版。未知 ground kind：警告 + 忽略。
5. **块合并是程序规则。** LLM 只合并散文。
6. **页是知识面。** 未确认与已确认写在同一 published 页上，用 `trust` 区分。

## 2. 目录 = 对象

| 目录 | `type` | slug | 本页上的 ground |
|---|---|---|---|
| `tables/` | `table` | 物理表名 | `ground:table`、`ground:relation` |
| `dicts/` | `dict` | dictKey，或 L0 `表__字段` | `ground:dict` |
| `concepts/` | `concept` | 业务语言 | 无（锚在 frontmatter） |
| `processes/` | `process` | 业务语言 | `ground:process` |
| `calibers/` | `caliber` | 业务语言 | `ground:caliber` |
| `metrics/` | `metric` | 业务语言 | `ground:metric` |
| `rules/` | `rule` | 业务语言 | `ground:rule` |
| `patterns/` | `pattern` | 业务语言 | `ground:pattern` |
| `scenarios/` | `scenario` | 业务语言 | `ground:scenario` |
| `sources/` | `source` | 源标识 | 无 |

- 没有 `queries/`：候选 SQL = `patterns/` 下 `status: draft`。
- 没有 `ground:cowrite`：共写是表字段的 `written_with`。
- `_index.md`、`_log.md` 是簿记，不是页。
- 语料内身份 `(belong, page_key)`。`type` 必须与目录一致。
- 歧义 wikilink 写成 `[[dicts/pay_status]]`。裸名仅全库唯一时解析。
- 实例清单不是 wiki 页：写入 `instance_index.yaml`（键 `(table, column)`），不进 `dicts/`。
- 源码地图：`recall: false`。

## 3. Frontmatter

| 字段 | 必填 | 写入者 | 说明 |
|---|---|---|---|
| `type` | ✓ | 校验 | 与目录一致 |
| `title` | ✓ | LLM | 含冒号须引号 |
| `page_key` | ✓ | 程序 | 目录内唯一 |
| `belong` | ✓ | 程序 | 以上级目录为准 |
| `domain` | table/dict/pattern 之外 ✓ | LLM | 业务域 |
| `status` | ✓ | **promote** | `draft` \| `published` \| `retired`。召回 = `published` |
| `aliases` | 推荐 | LLM | 词法/向量 |
| `anchors` | table/dict/pattern ✓ | 程序+校验 | 召回掩膜用的物理键；缺省则 table/dict=`page_key`，pattern=SQL 中的表 |
| `maps_to` | concept ✓ | LLM | **唯一**权威物理锚 |
| `field_targets` | concept 推荐；caliber/rule ✓ | LLM+校验 | 闭包；concept 必须包含 `maps_to` |
| `also_confused_with` / `adjudication` | 易混时成对必填 | LLM | 裸 page_key；`boundary` \| `synonym` |
| `sources` | ✓ | 程序 | |
| `created` / `updated` | ✓ | 程序 | |
| `tags` / `related` | 可选 | LLM | `related` 裸 slug，禁止 `[[..]]` |
| `databases` | 多库时 | 程序 | 空=不限 |
| `inactive` | 表可选 | — | 业务休眠；列全集仍在 |
| `schema_fingerprints` | 可选 | 程序 | stale 巡检，不是页 status |
| `recall` | 可选，默认 true | 人/程序 | `false` = 不进问数召回 |
| `contract_version` | ✓ | 程序 | **`"0.1"`** |

硬规则：首行 `---`；禁止 yaml 围栏包 frontmatter；数组内联；物理名不翻译。

```yaml
---
type: table
title: 企业主档表
page_key: cust_company_info
belong: tables
domain: 企业建档
status: published
aliases: [企业档案, 公司主档]
anchors: [cust_company_info]
sources: ["catalog.yaml", "CompanyService.java"]
created: 2026-09-15
updated: 2026-09-15
contract_version: "0.1"
---
```

## 4. 召回面 vs 展示面

切块 / 词法 / embedding **只吃召回面**。渲染仍可展示全文。

| 区域 | 标记 | 向量化 |
|---|---|---|
| 召回面 | 普通正文、` ```ground: ` | 是 |
| 展示面 | 标题为 `展示` / `版本演进` / `版本说明` / `给人看` / `本期说明` / `排期`（含子节）；或标题含 `不召回` | 否 |
| 展示围栏 | ` ```wiki:display ` / `display` / `wiki:norecall` / `norecall` | 否 |
| 整页关闭 | `recall: false` | 否 |

`ground:` 禁止进展示区。`proposed` / `disputed` 必须留在召回面。`rejected` 才可进展示区或删除。

## 5. 主张 `trust`

写出用 `trust`。读入兼容旧名 `confidence`（关系块还兼容历史 `status`）。只写一个；多个都写则必须相等。

| 值 | 召回 | 规划器 |
|---|---|---|
| `confirmed` | 是 | 硬路径（JOIN / 唯一锚 / 谓词 / 聚合 / 默认过滤） |
| `proposed` | 是 | 禁止硬 JOIN / 唯一锚 / 默认过滤 |
| `disputed` | 是 | 依赖则澄清；须带 `sides` |
| `rejected` | 否 | 当不存在 |

省略 = `confirmed`（旧页兼容）。新写入的 proposed/disputed **必须显式写**。

pattern 的「是否认证」也用 `trust`，不另造 `verification`。

## 6. Ground

围栏 info string = `ground:<kind>`，kind ∈ `{table, dict, relation, process, caliber, metric, rule, pattern, scenario}`。块内 YAML，无 `---`。同页同 kind 同键重复 → `DUPLICATE_GROUND_BLOCK`。

`evidence` 只许：`code_path:<file>[:<line>]` \| `database_profile:<locator>` \| `database_schema:<locator>` \| `document_claim:<locator>`。休眠表只允许 `database_schema`。不要发明 `code_enum:`。

### 6.1 `ground:table`（每表页恰一个）

结构合同的全部机器面都在这里：列、身份、投影、默认过滤、共写。关系另块，但仍在本页。

```yaml
table: cust_company_info
database: sqlbot
desc: 企业主档表
inactive: false
primary_key: [id]
grain: 一企一行（code 唯一）
name_anchors: [name, code]
default_filter:
  predicate: "cust_company_info.enable = 'Y'"
  trust: confirmed
  evidence: code_path:CompanyMapper.xml:20
fields:
  - name: cust_build_type
    type: string            # string|number|temporal|boolean|structured
    desc: 建档录入方式
    dict: [PC_BUILD, MOBILE_BUILD]
    label: [电脑端录入, 移动端录入]
    nullable: true
    written_with: []
```

- `fields` 覆盖 catalog 全部列。
- `written_with` 是写入同伴。
- `primary_key` ⊆ `fields`。活跃表必填 PK；hub / 被 metric 计数的表必填 `grain`。休眠表可省略 PK/grain/`default_filter`。
- `name_anchors` ⊆ `fields`，通常 `name`/`code`/`title`/`*_name`。已作本页 JOIN `right` 的列不得列入。实例值进 `instance_index.yaml`，不进 wiki 页。
- 字段键用 `type` / `desc`。字典列 `dict` 列举全部码值；有中文释义时平行写 `label`（与 `dict` 等长）。仅部分码有释义时 `label` 写成 `{码: 中文}`；全部无释义则省略 `label`。不要在字段上写 dict 页文件名（页键约定 `表__字段`）。表页链接仍写作 `[[dicts/表__字段]]`。
- `default_filter.trust` 非 confirmed 则不得自动套用。
- 全库骨架不写在每张表上：L1 另产可召回概念页 `concepts/catalog_summary`。每表一行：`- 表名: 表中文名(简要业务说明与核心维度/度量)`（同类列语义合并，大宽表适当增长，不逐列抄注释）。明细仍在各表页。

### 6.2 `ground:relation`（写在表页）

```yaml
type: EQUI_JOIN                  # EQUI_JOIN | SHARED_KEY | DERIVED
left: cust_company_info.id
right: cust_company_detail.company_id
cardinality: one_to_many         # 从 left 实体看 right
cast: null
trust: proposed
authenticity: unknown            # L0: likely | unknown | unlikely
join_role: identity              # L0: identity | business_code
priority: primary                # L0: 同父表有 identity 边时码边 secondary
evidence: code_path:CompanyService.java:88
derived_from: null
```

JOIN 图的边 = `EQUI_JOIN` ∧ `confirmed`。唯一键 `(left, right)`。**写在 FK 端所在表页**，对端不重复。n:n 用中间表两条边。租户/审计列不得作端点。`using_relations` 引用同一对，不另造关系名。L0 身份束候选边全部保留为 `proposed`，不标主引用；同对端多列就多条边。id/PK 边 `join_role=identity`；`code` / `product_code` / `platform_product_code` 等码对码是合法 EQUI_JOIN，`join_role=business_code`，同父表已有 identity 边时 `priority=secondary`。值域「A 包含 B」（IND）只作 `EQUI_JOIN` 的方向证据（`database_profile` + REVIEW / LLM 输入），**不要**新增 `CONTAINS` / `INCLUSION` 类型。L0 初审 `likely` 必须值域契合 **且** 列名/注释有关联语义；仅值域契合的边仍保留，但 `authenticity=unknown`、`preview_block=overlap_unsemantic`，REVIEW kind=`join_overlap_unsemantic`。L0 页面 relation 必须写出 `authenticity` / `name_evidence` / `overlap` / `join_role` / `priority`，并按 authenticity 分组（组内 identity/primary 在前）；有源码再删假边 / 标主边 / 升 `confirmed`。

### 6.3 `ground:dict`

```yaml
dict: cust_build_type
fields: [cust_company_info.cust_build_type]
values:
  PC_BUILD: { label: 平台录入, trust: confirmed }
  WAIT:
    label: 待签约
    trust: disputed
    sides:
      - { source: code, value: WAITING, label: 待签约 }
      - { source: db, value: WAIT }
mixed: false
```

字典页是**封闭低基数代码集**（`distinct <= 32`），不是公司名/信用代码等实例清单。YAML 主键为 `dict:`。认证 `label` 只跟代码（`confirmed`）。L0 可从列注释解析 label，必须 `trust: proposed` 且 `evidence: database_schema`；注释没有「码→中文」映射则省略，禁止脑补。L1 代码 label 覆盖注释。`mixed: true`（旧名 `ambiguous`）必须能指到 concept 的 `adjudication`。空字符串不得写入 `values`。L0 无独立 dictKey 时，`page_key` / `dict` 用 `表__字段`（例 `cust_person_info__realname_status`），不要点号（会和物理锚 `表.字段` 撞名），也不要 `表_字段`，也不要用 `::`（部分 git/路径工具不友好）。`fields` / `anchors` 仍写物理列 `表.字段`。表字段上的 `dict` 列举码值，不写字典 `page_key`。

同一列可以同时有 dict 页（码表）和 `instance_index.yaml` 条目（口语/高频实例定位）；两条管线互不共用 verdict。

### 6.4 `ground:scenario`

问法选表。主档不写 grain，继承 table。不要用列清单当分组，也不要给字段倒挂 `scenes`。

```yaml
scenario: company_build
hubs:
  - table: cust_company_info
    role: master
shared:
  - table: cust_setting_config
    role: auth_config
lifecycle:
  - dict: cust_build_status
    process: cust_build_status_flow
```

场景如何被选中：靠本页 `aliases` + 召回面被 RRF 命中（或澄清指定），不是靠字段倒挂 `scenes`。

需要单列时走口径/点名/JOIN，并入该列及其 `written_with` 同伴——不在 scenario 上开 `window: [col, …]`。

### 6.5 `ground:process`

```yaml
process: 企业建档流程
field: cust_company_info.cust_build_status   # 钉同一列
entry: 管理端新建企业
stages:
  - stage: 提交建档
    trigger: 用户提交
    effects:
      - { op: update, table: cust_company_info, fields: [cust_build_status] }
    transitions:
      - { from: DRAFT, event: 提交, to: SUBMITTED }
```

`from: null` = 初始。外部接口只进散文。

### 6.6 `ground:caliber`

```yaml
caliber: 已签约企业
field_targets: [cust_company_info.sign_status]
predicate: "cust_company_info.sign_status = 'SIGNED'"
scope: global                    # global | scenario
boundary: 回答"是否签约"；与 identify_style 无关
using_relations: []              # 谓词跨表时必填 [{left, right}, ...]
```

### 6.7 `ground:metric`

口径在 caliber 上；这里只加聚合。粒度继承 `grain_table` 的 `grain`。

```yaml
metric: 已签约企业数
caliber: 已签约企业
grain_table: cust_company_info
aggregation: count_distinct      # count | count_distinct | sum | avg | min | max
field: cust_company_info.id      # 被聚合列；COUNT 实体时用该表 PK
using_relations: []              # 超出 caliber 已声明的跨表时必填
```

- 禁止再写一套 `filter` / 自由文本 `grain`。
- many 端 COUNT 一 端实体必须 `count_distinct` + 一 端 PK。

### 6.8 `ground:rule`

只放 **写约束 / 非默认查询约束 / 缺省值**。默认过滤用表 `default_filter`，不要在 rule 再写一份同义谓词（lint 冲突）。

运行时：`write_constraint` / `default_value` **不**自动改写问数 SQL（只召回给人/规划器解释写路径）。`query_constraint` 召回为软约束，**不**自动 AND（自动默认谓词只有表 `default_filter`）。

```yaml
rule: 建档必填营业执照
field_targets: [cust_company_info.license_no]
impact: write_constraint         # write_constraint | query_constraint | default_value
content: 创建时必填，缺失拒绝保存
evidence: code_path:CompanyService.java:45
```

### 6.9 `ground:pattern`

```yaml
pattern: 已签约企业数量
question: 已签约的企业有多少
sql: |
  SELECT COUNT(DISTINCT c.id)
  FROM cust_company_info c
  WHERE c.sign_status = 'SIGNED'
calibers: [已签约企业]
trust: confirmed
evidence: database_profile:run/2026-09-15#1
```

- 候选：本页 `status: draft` + 主张 `proposed`。
- published 且 `confirmed` 才进 few-shot；须过 JOIN 图 lint；`confirmed` 须有执行记录或 REVIEW 人审通过（证据写在 `evidence`/`sources`）。
- 不写 `using_relations`：边从 SQL 抽。
- 不写 `verification` / `onboarding`。

### 6.10 概念页

```yaml
---
type: concept
title: 平台录入
aliases: [平台录入, PC端录入]
maps_to: cust_build_type.PC_BUILD
field_targets: [cust_build_type.PC_BUILD]
also_confused_with: [identify_style]
adjudication: boundary
---
identify_style 回答谁邀请/认证渠道；cust_build_type.PC_BUILD 回答从哪录入。
```

`maps_to` / `field_targets` = `表.字段` 或 `dictKey.VALUE`。易混无 `adjudication` → `TERM_UNADJUDICATED`。

全库表骨架是特殊概念页：`page_key: catalog_summary`，`recall: true`，`maps_to` 可省略；正文按前缀每表一行：`- 表名: 表中文名(简要业务说明，主键/业务键，以及核心维度/度量)`，同类列语义合并，大宽表适当增长，由 L1 编译从 catalog 生成，不要手写，不要把列注释铺进骨架。

## 7. 引用

| 通道 | 语法 | 用途 |
|---|---|---|
| 页面链接 | `[[page_key]]` 或 `[[belong/page_key]]` | 图扩展边 |
| 物理锚 | `表.字段`、`dictKey.VALUE` | 闭包 / 投影 |
| 关系边 | `{left, right}` | JOIN 图 / `using_relations` |
| 软关联 | `related: [slug]` | 展示 |

图扩展按无类型 wikilink 跑（一跳 + 配额），且只在勾选掩膜后的子图上。`related:` 不进图。L1 编译给语义页写 `## 页面链接`：从 `field_targets` / `maps_to` / `hubs` / `using_relations` / `also_confused_with` 解析**已存在**的页，写作 `[[belong/page_key]]`。没有邻页的孤表回链 `[[concepts/catalog_summary]]`。

## 8. 合并

同 `page_key` + 同 ground 种类 + 同实体键才程序并集。只合并进 draft/patch；冲突进 REVIEW。

| 块 | 键 | 冲突 |
|---|---|---|
| table.fields | `name` | catalog 胜 + REVIEW |
| table PK/grain/name_anchors/default_filter | 页级 | catalog/代码胜；文档冲突 → disputed |
| dict.values | dictKey | 代码 label 胜 + REVIEW |
| relation | `(left,right)` | REVIEW |
| process.stages | `stage` | transitions 幂等追加 |
| caliber/metric/rule/pattern | 页独占则替换 | 多源 → REVIEW |

`sources` 仅含当前源时允许整体替换 draft。独立重提禁止把旧问数 wiki 当生成上下文。

## 9. `claim_path`

`belong/page_key#path`。REVIEW 与澄清共用。

| path | 指向 |
|---|---|
| `fields.<col>` | 列；`fields.<col>.written_with` 共写 |
| `primary_key` / `grain` / `name_anchors` / `default_filter` | 表级 |
| `values.<CODE>` | 字典值 |
| `relations.<left>__<right>` | 关系；`.` 保留，两端用 `__` 接 |
| `hubs.<table>` | 场景选表 |
| `stages.<stage>` | 流程 |
| `predicate` / `aggregation` / `using_relations` | 口径/度量 |
| `sql` | 认证 SQL |
| `body` | 散文 |

例：`dicts/sign_status#values.WAIT`。无法解析 → `CLAIM_PATH_INVALID`。

## 10. REVIEW

队列，不是页 status。一项一条主张。权威文件：`.runs/<batch>/reviews.yaml`。草稿页内 `---REVIEW: kind | title ---` 仅给人看。

```yaml
id: rv_20260915_001
claim_path: dicts/sign_status#values.WAIT
kind: conflict                 # conflict | missing | stale | unanchored | unverified_join | coverage | other
severity: warning              # error | warning | info
status: open                   # open | accepted | rejected | deferred
sides:
  - { source: code, value: WAITING }
  - { source: db, value: WAIT }
created: 2026-09-15
sources: ["SignStatus.java"]
note: 代码常量与库实测不一致
```

promote：闭包上 open 的 error 必须清零。warning 可随 published 出门，对应主张不得 `confirmed`。**发布闭包：** 一张 `published` 表页所引用的 dict / 对端表 / scenario 所选表，必须已经是 `published`（或同一批 promote）。draft 字典不得被 published 表页 `[[dicts/…]]` 引用。

## 11. Lint（按不变量，不是一袋码）

结构 error 阻断 promote。允许页内 proposed/disputed。

**结构完整：** `TABLE_NOT_IN_CATALOG` `FIELD_NOT_IN_CATALOG` `TABLE_FIELDS_INCOMPLETE` `TABLE_PRIMARY_KEY_MISSING` `TYPE_FAMILY_MISMATCH` `NAME_ANCHOR_NOT_IN_FIELDS`

**继承与粒度：** `TABLE_GRAIN_MISSING`（hub / `grain_table` 所指表）`METRIC_AGGREGATION_MISSING` `METRIC_FANOUT`

**图：** `RELATION_ENDPOINT_UNBOUND` `TENANT_FIELD_AS_ENDPOINT` `PATTERN_JOIN_NOT_IN_GRAPH` `METRIC_USING_RELATIONS_REQUIRED`（跨表且未钉）

**叠加锚点：** `CONCEPT_UNANCHORED` `REF_TARGET_MISSING` `DORMANT_TABLE_REFERENCED` `COWRITE_FIELDS_UNBOUND` `PATTERN_SQL_TABLE_UNDECLARED` `PATTERN_CALIBER_MISMATCH` `RULE_DEFAULT_FILTER_DUP` `PUBLISHED_REF_DRAFT`（published 指向 draft 字典/表）

**发布面：** `DUPLICATE_GROUND_BLOCK` `GROUND_IN_DISPLAY` `CLAIM_PATH_INVALID` `INGEST_WROTE_PUBLISHED` `PATTERN_UNEVIDENCED_CONFIRMED`（confirmed 无执行记录且无已接受 REVIEW）

**语义健康（不阻断，进 REVIEW）：** `RELATION_CAST_REQUIRED` `RELATION_UNCONFIRMED` `MULTIPLE_JOIN_PATHS_UNDECLARED` `NAME_ANCHOR_SUSPECT_MISSING` `TERM_UNADJUDICATED` `ENUM_ORPHAN_VALUE` `STALE_VS_CATALOG` `DISPUTED_IN_DISPLAY` `COVERAGE_GAP` `ORPHAN_PAGE` `AMBIGUOUS_LINK` `BROKEN_LINK` `UNKNOWN_GROUND_KIND`

实现未覆盖某码 ≠ 契约没有该码。

## 12. 示例（表页：结构合同收在一页）

````markdown
---
type: table
title: 企业主档表
page_key: cust_company_info
belong: tables
domain: 企业建档
status: published
aliases: [企业档案]
anchors: [cust_company_info]
sources: ["catalog.yaml", "CompanyService.java"]
created: 2026-09-15
updated: 2026-09-15
contract_version: "0.1"
---

# 企业主档表

企业主档记录建档、认证与签约，是[[企业建档流程]]与[[已签约企业]]的核心表。

## 字段

```ground:table
table: cust_company_info
desc: 企业主档表
inactive: false
primary_key: [id]
grain: 一企一行（code 唯一）
name_anchors: [name, code]
default_filter:
  predicate: "cust_company_info.enable = 'Y'"
  trust: confirmed
  evidence: code_path:CompanyMapper.xml:20
fields:
  - name: id
    type: string
    nullable: false
  - name: name
    type: string
  - name: sign_amount
    type: number
    written_with: [sign_time]
  - name: sign_time
    type: temporal
    written_with: [sign_amount]
  - name: cust_build_type
    type: string
    dict: [PC_BUILD, MOBILE_BUILD]
    label: [电脑端录入, 移动端录入]
```

## 关联关系

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_company_detail.company_id
cardinality: one_to_many
trust: confirmed
evidence: code_path:CompanyService.java:88
```

## 版本演进

本期文档曾规划的字段未落库；不进召回。
````
