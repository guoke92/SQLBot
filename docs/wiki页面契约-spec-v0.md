# Wiki 页面契约 Spec v0（评审稿）

> 日期：2026-08-28
> 状态：**评审稿**——阶段一评审物，评审通过后作为 llm_wiki 项目 `schema.md` 的权威来源与投影编译器/lint 的实现依据
> 定位：知识体系全链路切换 llm-wiki 形态后的**页面格式契约**。页面是事实载体（artifact of record），严格块是机器确定性解析的最小面。
> 关联文档：《知识体系目标架构-v3.1》（本契约继承其 D1/D5/D7/D8 设计成果，见 §1.3 映射表）

---

## 0. 设计原则（不可妥协项）

1. **零信任解析**。所有 ground 块由确定性解析器消费；任何语法失败 → **丢弃该块 + 记入 ingest 警告日志**，绝不猜测、绝不部分采纳。llm_wiki 实测：无清洗层时约 45% 的模型生成 frontmatter 不可解析——ground 块语法更复杂，防御层只能加强不能省略。
2. **LLM 管内容，程序管结构**。frontmatter 的 `page_key/created/updated/sources/contract_version` 由程序盖章覆写，模型输出只是草案；`status` 变更只经人工/门禁。
3. **权威顺序继承 v3.1 D7**：`库字段实际值 > 代码读写 > 文档主张 > schema 导航`。冲突显式落 review 队列，禁止静默覆盖。
4. **物理名锚定**。跨页引用一律用物理键（`表名.字段名`、`dictKey.VALUE`），不用页内逻辑 id。这是对 §7「共享表 payload 逐字复制」教训的结构性消解：表页即唯一权威声明，其余页面只引用物理键，复制税在格式层面不存在。
5. **契约演进向后兼容**。`contract_version` 递增；新增可选字段不升版；改语义必升版并写迁移说明。解析器对未知 ground 块种类：警告 + 忽略（forward-compatible）。
6. **合并确定性**。ground 块的合并是程序规则，不是 LLM 调用（§5.3）；LLM 合并只作用于散文区。

---

## 1. 页面分类学与目录路由

### 1.1 目录 → 页面类型（type 必须与目录一致，沿用 llm_wiki schema 路由校验）

| 目录 | `type` | 身份规则（slug） | 承载 ground 块 | 对应 v3.1 层/边 |
|---|---|---|---|---|
| `wiki/tables/` | `table` | **物理表名**（如 `cust_company_info`），跨语言稳定 | `ground:table`、`ground:relation` | L1 物理锚点；has_field、relation_endpoint |
| `wiki/enums/` | `enum` | **dictKey**（如 `cust_build_type`） | `ground:enum` | L1 字典 |
| `wiki/concepts/` | `concept` | 业务语言 slug（CJK 保留，不罗马化） | 无（锚点在 frontmatter） | L2 概念；concept_of |
| `wiki/processes/` | `process` | 业务语言 slug | `ground:process` | L3 流程；reads/writes、precedes |
| `wiki/calibers/` | `caliber` | 业务语言 slug | `ground:caliber` | L4 口径；references_field |
| `wiki/metrics/` | `metric` | 业务语言 slug | `ground:metric` | L4 指标；references_field |
| `wiki/rules/` | `rule` | 业务语言 slug | `ground:rule` | L4 规则；references_field |
| `wiki/patterns/` | `pattern` | 业务语言 slug | `ground:pattern` | L5 范例；validates |
| `wiki/scenarios/` | `scenario` | 业务语言 slug | 无（纯组织页） | 场景闭包导航 |
| `wiki/queries/` | `query` | 回填问答沉淀页 | 无 | Query→wiki 回填产物 |
| `wiki/sources/` | `source` | 源标识（脚本基线/代码域说明） | 无 | L0 证据的"源摘要"层 |

### 1.2 关键身份规则

- **一物理表一页、一 dictKey 一页**（D1 的 wiki 化）：全库唯一权威声明，其余页面只引用。表页 slug 用物理名保证跨包/跨语言增量重提取时身份稳定（等价于 v3.1 的 `norm(db.table)` 归并键）。
- 语料内唯一身份是 **`(belong, page_key)`**：`belong` = 上级目录（`tables`/`enums`/`concepts`/…），`page_key` 只在同一目录内唯一。跨目录允许同名（如 `concepts/pay_status` 与 `enums/pay_status`）。
- 概念/流程/口径等业务页 slug 由标题派生（kebab-case / CJK 保留）；文件名 stem 应对齐 `page_key`。
- `[[wikilink]]`：裸 `[[pay_status]]` 仅在全库唯一时解析；歧义须写成 `[[enums/pay_status]]`。
- 休眠表：表页照常存在，frontmatter `inactive: true`，`ground:table` 中 `fields` 为空（字段留 catalog 基线）。

### 1.3 与 v3.1 决策的映射（本契约"继承"而非"放弃"的证明）

| ADR 决策 | wiki 形态对应物 |
|---|---|
| D1 节点化真相灭复制税 | 一表/一字典一权威页 + 物理键引用（§1.2、原则 4） |
| D5 全层索引灭检索盲区 | ground 块随页面被 chunk 级嵌入，字段/字典词汇全部进向量索引 |
| D8 声明即边 | `[[wikilink]]` + ground 块锚点声明即边；边类型语义由解析器从块种类+页类型对推导（§4.3） |
| D7 三合并点权威序 | M1=提取提示词证据规则；M2=§5.3 确定性块合并；M3=catalog 驱动 lint（§6，脚本刷新 catalog 即重校验） |
| D2 运行时只读不可变快照 | V0 以 `status: published` 门禁 + git 历史替代；版本钉扎留待阶段二独立服务补齐（已知取舍） |

---

## 2. Frontmatter 契约

### 2.1 字段表

| 字段 | 类型 | 必填 | 写入者 | 校验/说明 |
|---|---|---|---|---|
| `type` | §1.1 枚举 | ✓ | LLM 起草，程序校验 | 必须与目录一致，不一致整页拒绝（沿用 llm_wiki 路由校验） |
| `title` | string | ✓ | LLM | 含冒号须引号 |
| `page_key` | slug | ✓ | **程序盖章** | 目录内唯一；非法草稿（`caliber/foo`、`calibers.foo`）导入时规范化为裸 slug |
| `belong` | 目录名 | ✓ | **程序盖章** | 上级目录 `tables`/`enums`/…；以磁盘路径为准，frontmatter 冲突则整页拒绝 |
| `domain` | string | tables/enums/patterns 之外必填 | LLM | 业务域，域名校准沿用 `package.domains` 语义（含 `renamed_from`） |
| `status` | `draft` \| `published` \| `retired` | ✓ | **人/门禁** | 召回资格 = `published`；lint 全 error 清零才可发布 |
| `aliases` | string[] | 推荐 | LLM | 业务别名/用户说法；进向量索引词表（chunk 覆盖 frontmatter） |
| `anchors` | string[] | tables/enums/patterns 必填 | LLM+校验 | 物理键清单，如 `[cust_company_info]`、`[cust_company_info.cust_build_type]` |
| `field_targets` | string[] | concept/caliber/rule **必填** | LLM+校验 | 物理键（`表.字段`）或字典值锚（`dictKey.VALUE`） |
| `sources` | string[] | ✓ | **程序盖章** | 当前源文件名强制在列（沿用 canonicalizeSourcesField） |
| `created` / `updated` | date | ✓ | **程序盖章** | 沿用 stampGeneratedFrontmatterDates |
| `tags` | string[] | 可选 | LLM | 裸字符串数组 |
| `related` | string[] | 可选 | LLM | **裸 page_key**，禁止 `[[..]]`/`.md`/`wiki/` 前缀（沿用 llm_wiki 规则） |
| `inactive` | bool | 表页可选 | LLM | 休眠表标记 |
| `contract_version` | string | ✓ | **程序盖章** | 当前 spec 版本，如 `0.1` |

### 2.2 格式硬规则（继承 llm_wiki，全部保留）

- 首行必须 `---`，禁止 yaml 代码围栏包裹，禁止 `frontmatter:` 前缀（sanitize 层修复）；
- 数组一律内联 `[a, b]`；`related`/`aliases` 写裸值不写 wikilink；
- 物理名一律原样保留不翻译（`cust_build_type` 不译、不拼音化）。

### 2.3 语法示例

```yaml
---
type: table
title: 企业主档表
page_key: cust_company_info
domain: 企业建档
status: draft
aliases: [企业档案, 公司主档]
anchors: [cust_company_info]
field_targets: []          # 表页不使用
sources: ["catalog.yaml", "CompanyService.java"]
created: 2026-08-28
updated: 2026-08-28
tags: [主数据]
related: [cust-company-detail]
contract_version: "0.1"
---
```

---

## 3. Ground 块语法（8 种）

### 3.0 通用规则

- 围栏 info string 必须是 `ground:<kind>`，kind ∈ {`table`, `enum`, `relation`, `process`, `caliber`, `metric`, `rule`, `pattern`}；未知 kind → 警告 + 忽略。
- 块内为 **YAML**（无 `---` 文档分隔符，直接映射）。
- **唯一键**：每 kind 有块级唯一键（见各块），同页重复键 → lint error `DUPLICATE_GROUND_BLOCK`。
- **证据字段**：`evidence` 取值 `code_path:<file>[:<line>]` | `database_profile:<locator>` | `database_schema:<locator>` | `document_claim:<locator>`；休眠表只允许 `database_schema`。
- **版面建议**（服务 chunk 召回）：每个 ground 块置于稳定的 `##` 小节下（如 `## 字段`、`## 关联关系`），使块与标题路径同 chunk 入索引。

### 3.1 `ground:table`（每表页恰一个）

```yaml
table: cust_company_info
database: sqlbot                # 单库可省，多库必填
description: 企业主档表
inactive: false
fields:                          # 只声明有业务语义的字段；未列字段留 catalog 基线
  - name: cust_build_type
    data_type: string            # 类型族词表：string|number|temporal|boolean|structured（沿用 §11）
    description: 建档录入方式
    dictionary: cust_build_type  # 指向 enums 页 slug；无则省略
    nullable: true
  - name: sign_status
    data_type: string
    description: 签约状态
    dictionary: sign_status
```

校验：`table` 必在 catalog；`fields[].name` 必在 catalog 该表（`FIELD_NOT_IN_CATALOG`）；`data_type` 族比对（`TYPE_FAMILY_MISMATCH`）；`dictionary` 指向的 enums 页必须存在。

### 3.2 `ground:enum`

```yaml
enum: cust_build_type
fields: [cust_company_info.cust_build_type]   # 承载字段（物理键；歧义绑定时多个）
values:
  PC_BUILD: { label: 平台录入 }
  AGW_BUILD: { label: 网关录入 }
ambiguous: false                 # 一字段绑多枚举类时 true，必须附 adjudication 指针
```

校验：dictKey/显示名与 enums.yaml 基线一致（不一致 → catalog 胜 + review）；`ENUM_ORPHAN_VALUE`：值无任何使用点（process/rule/pattern/term 引用）→ warning。

### 3.3 `ground:relation`

```yaml
type: EQUI_JOIN                  # EQUI_JOIN | SHARED_KEY | DERIVED
left: cust_company_info.id
right: cust_company_detail.company_id
cardinality: many_to_one         # one_to_one | many_to_one | one_to_many
cast: null                       # 类型族不同必填，如 string_to_number
status: proposed                 # proposed(默认) | confirmed(绑定执行通过)
evidence: code_path:CompanyService.java:88
derived_from: null               # DERIVED 时：源物理键，如 cust_company_info.parent_id
```

硬规则（对应 reference §3）：租户隔离字段（`tenant_id/tenant_code/db_tenant_code/app_tenant_code/organization_id`）作为端点 → **lint error 拒绝**；`type: DERIVED` 不产生 JOIN 边，只标注冗余来源；n:n/共享键必须 `SHARED_KEY`；唯一键 = `(left, right)` 有序对。

### 3.4 `ground:process`（状态机 + 读写效果合一，对应 L3）

```yaml
process: 企业建档流程
entry: 管理端新建企业
stages:
  - stage: 创建建档
    trigger: 管理端保存
    effects:
      - { op: insert, table: cust_company_info, fields: [cust_build_type, cust_build_status] }
    transitions: []
  - stage: 提交建档
    trigger: 用户提交
    effects:
      - { op: update, table: cust_company_info, fields: [cust_build_status] }
    transitions:
      - { from: DRAFT, event: 提交, to: SUBMITTED, field: cust_company_info.cust_build_status }
```

规则：`transitions[].from: null` 表示初始状态（对应"创建时固定写值"）；`effects.table` 必须是已声明表页的锚点（外部接口只进散文/`assumptions`，禁止入 effects——沿用 §3.10）。

### 3.5 `ground:caliber`

```yaml
caliber: 已签约企业
field_targets: [cust_company_info.sign_status]
predicate: "cust_company_info.sign_status = 'SIGNED'"
scope: global                    # global | <语境说明>
boundary: 回答"是否签约"；与"认证方式 identify_style"无关
```

### 3.6 `ground:metric`

```yaml
metric: 已签约企业数
field: cust_company_info.id      # field 与 grain 至少其一（沿用契约硬要求）
grain: 企业                      # 去重粒度声明
caliber: 已签约企业              # 引用 caliber 页 page_key；或内联 predicate
```

### 3.7 `ground:rule`

```yaml
rule: 建档必填营业执照
field_targets: [cust_company_info.license_no]
impact: write_constraint         # write_constraint | query_constraint | default_value
content: 创建时必填，缺失拒绝保存
evidence: code_path:CompanyService.java:45
```

### 3.8 `ground:pattern`

```yaml
pattern: 已签约企业数量
question: 已签约的企业有多少
sql: |
  SELECT COUNT(DISTINCT c.id)
  FROM cust_company_info c
  WHERE c.sign_status = 'SIGNED'
calibers: [已签约企业]
verification: PENDING_VALIDATION   # PENDING_VALIDATION | executed（未在目标库执行禁止 executed）
```

校验：SQL 中表必须在 anchors/catalog（`SQL_TABLE_NOT_DECLARED`）；`calibers` 引用必须存在且与 metric/caliber 自洽（`PATTERN_CALIBER_MISMATCH`，坏样本 11）。

### 3.9 概念页（术语桥，无 ground 块）

```yaml
---
type: concept
title: 平台录入
aliases: [平台录入, PC端录入]
field_targets: [cust_build_type.PC_BUILD]   # 字典值锚点
maps_to: cust_build_type.PC_BUILD
also_confused_with: [identify_style]
adjudication: boundary           # boundary(边界规则) | synonym(同义说明)
---
正文写清：与"认证方式"的边界——identify_style 回答"谁邀请/认证渠道"，
cust_build_type.PC_BUILD 回答"从哪录入"；混用后果……
```

`adjudication` 缺失且 `also_confused_with` 非空 → lint `TERM_UNADJUDICATED`（近似语义裁决未完成）。

---

## 4. 交叉引用与锚点解析

### 4.1 三种引用通道

| 通道 | 语法 | 消费方 |
|---|---|---|
| 页面链接（图边） | `[[page_key]]` 或 `[[belong/page_key]]` | 裸链接仅在唯一时解析；歧义须带 belong |
| 物理锚点（结构边） | `表.字段`、`dictKey.VALUE`（frontmatter `field_targets/anchors` + 块内字段） | ground 解析器 → 投影结构 |
| 软关联 | frontmatter `related: [slug]` | 展示/导航 |

### 4.2 别名解析

frontmatter `aliases` 随页面内容被 chunk 化入向量索引（词法召回天然覆盖业务说法）；llm_wiki 的图别名归一（path/stem/title/空格-连字符/小写）保持默认，不新增机制。

### 4.3 边类型推导（解析器职责，非图存储职责）

**明确决策：wiki 图存储无类型邻接（llm_wiki 现状不动）；类型语义在投影时由解析器从「块种类 × 页类型对」推导**：concept→table = concept_of；process 块 effects = reads/writes；ground:relation = relation_endpoint；pattern.calibers = validates。图扩展召回按无类型边跑（一跳 + 配额保底），类型过滤在投影层做。

---

## 5. 写入时管线（防御层）与合并规则

### 5.1 管线序列（标注 llm_wiki 现状 / 本契约新增）

```
parseFileBlocks（FILE 协议，不变）
→ isSafeIngestPath（路径安全，不变）
→ sanitizeIngestedFileContent（扩展，见 5.2）
→ stampGeneratedFrontmatterDates / canonicalizeSourcesField / page_key 盖章（扩展）
→ 【新】groundExtract：扫描 ground 块 → YAML 解析；失败=丢块+警告日志
→ 【新】groundValidate：§3 各块校验规则；失败=丢块+警告（页面仍写入，散文保留）
→ schema 路由校验 type↔目录（不变机制）
→ 语言守卫（不变）
→ 合并（§5.3）
→ 写入 + 确定性 index/log（不变）
→ 完整性门禁：硬失败/未修复截断 → 抛错，不缓存不入向量（不变）
```

### 5.2 sanitize 扩展（关键集成点）

现有 `sanitizeIngestedFileContent` 会剥模型误加的代码围栏——**必须为 ` ```ground:` 围栏加白名单**，否则 ground 块会被 fence 清洗误伤。这是实现期第一个要落的小改动。

### 5.3 ground 块确定性合并（替代"LLM 正文合并"对块的作用）

页面合并三层中，**块层不走 LLM**：

| 块 | 键 | 合并规则 | 冲突处理 |
|---|---|---|---|
| table.fields | `name` | 并集 | 同名字段 `data_type/description` 冲突 → **catalog 胜** + review |
| enum.values | `dictKey` | 并集 | label 冲突 → 基线胜 + review |
| relation | `(left,right)` | 幂等 | cardinality/type 冲突 → review |
| process.stages | `stage` | 并集 | transitions 按 `(from,event,to)` 幂等追加；冲突 → review |
| caliber/metric/rule/pattern | `page_key` | 新源独占页则整体替换；多源页冲突 → review | 无静默覆盖 |

- **独占替换规则**（沿用 isOwnedOnlyBySource 语义）：页面 `sources` 仅含当前源时，重提取允许整体替换块与正文（收缩过时措辞不复活）；多源共享页走合并。
- 散文区合并沿用 llm_wiki LLM merge + 失败回退。
- 冲突一律生成 review 项（M2：PUBLISHED 胜出 → 冲突队列的 wiki 化）。

---

## 6. Lint 规则码表（与现有码表映射）

| lint code | 级别 | 来源 | 检查内容 |
|---|---|---|---|
| `TABLE_NOT_IN_CATALOG` | error | DATASET_NOT_FOUND | ground:table.table 不在 catalog 基线 |
| `FIELD_NOT_IN_CATALOG` | error | FIELD_NOT_FOUND | fields[].name 不在 catalog 该表 |
| `TYPE_FAMILY_MISMATCH` | error | FIELD_TYPE_MISMATCH | data_type 族 ≠ catalog（varchar↔bigint 对声明 FAIL） |
| `RELATION_ENDPOINT_UNBOUND` | error | RELATIONSHIP_NOT_BOUND | 关系两端 `表.字段` 无处声明/不在 catalog |
| `RELATION_CAST_REQUIRED` | warning | RELATIONSHIP_TYPE_MISMATCH | 两端类型族不同且未带 cast |
| `RELATION_UNCONFIRMED` | warning | RELATIONSHIP_PROPOSED | status=proposed（默认态，提示非错误） |
| `TENANT_FIELD_AS_ENDPOINT` | error | reference §3.6 | 租户/审计/同名拷贝字段作关系端点 |
| `CONCEPT_UNANCHORED` | error | ADR lint | concept 缺 field_targets/maps_to |
| `REF_TARGET_MISSING` | error | 裸声明坏样本 12 | field_targets/anchors/calibers 引用的物理键或页面不存在 |
| `TERM_UNADJUDICATED` | warning | §8 近似语义 | also_confused_with 非空且无 adjudication |
| `ENUM_ORPHAN_VALUE` | warning | 完备校验 | 枚举值无使用点 |
| `DORMANT_TABLE_REFERENCED` | error | §3.11 | inactive 表被 effects/relations/pattern 引用 |
| `PATTERN_SQL_TABLE_UNDECLARED` | error | §3.10 | pattern SQL 引用未声明表 |
| `PATTERN_CALIBER_MISMATCH` | error | 坏样本 11 | pattern.calibers 与 metric/caliber 不自洽 |
| `PATTERN_FAKE_EXECUTED` | error | 坏样本 5 | verification=executed 但无执行记录 |
| `DUPLICATE_GROUND_BLOCK` | error | 本契约 | 同页同 kind 同键重复 |
| `ORPHAN_PAGE` | info | 图洞察 | 入链=0 的内容页（lint 循环/图洞察探测器） |
| `STALE_VS_CATALOG` | warning | schema drift | catalog 版本前移后页面未复检（M3 触发器） |
| `COVERAGE_GAP` | info | coverage.yaml | catalog 活跃表无 table 页（离线验收，阻断出包） |

**发布门禁**：`status: draft → published` 当且仅当该页及其引用闭包 lint 无 error（warning 放行）——对应现行「DRAFT 且 PASS/WARNING 才可提交审核」。

---

## 7. 投影与解析契约（召回消费）

### 7.1 V0（验证期）：客户端解析

SQLBot 调 `POST /api/v1/projects/{id}/search`（`include_content: true`），客户端按本 spec 解析 ground 块。**解析器实现两份（TS 参考实现 / Python 消费实现），必须通过同一套 fixture 测试**（fixture = §8 示例页 + 边界坏样本），保证两侧行为一致。

### 7.2 解析输出（类型化结构）

```
TableDecl { page_key, table, database, inactive, fields[] }
EnumDecl  { page_key, enum, fields[], values{}, ambiguous }
RelationDecl { left, right, type, cardinality, cast, status, evidence }
ProcessDecl { page_key, stages[] { stage, trigger, effects[], transitions[] } }
CaliberDecl / MetricDecl / RuleDecl / PatternDecl { page_key, …, field_targets, status }
```

每条声明附带 `page_key + status`（召回资格过滤在消费端做：仅 `published`）。

### 7.3 Round-trip 审计（迁移与回归门禁）

`页面 → 解析 → 规范化重序列化 → 页面` 必须字节级稳定（canonical form）。CI 用 §8 示例 + 坏样本集跑 round-trip，diff 非零即 fail。

### 7.4 V1（阶段二）：`/recall` 服务端组装端点

返回解析后的块集合 + 图扩展邻居（按页类型加权），把消费端解析上移服务端。接口设计留待独立服务立项，本契约的块语法即其载荷。

---

## 8. 完整示例（生成提示词将内嵌此页作为格式范例）

````markdown
---
type: table
title: 企业主档表
page_key: cust_company_info
domain: 企业建档
status: draft
aliases: [企业档案, 公司主档]
anchors: [cust_company_info]
sources: ["catalog.yaml", "CompanyService.java"]
created: 2026-08-28
updated: 2026-08-28
tags: [主数据]
related: [cust-company-detail, cust-build-type]
contract_version: "0.1"
---

# 企业主档表

企业主档（cust_company_info）记录企业的建档、认证与签约信息，
是[[企业建档流程]]与[[已签约企业]]口径的核心表。

## 字段

```ground:table
table: cust_company_info
database: sqlbot
description: 企业主档表
inactive: false
fields:
  - name: cust_build_type
    data_type: string
    description: 建档录入方式
    dictionary: cust_build_type
    nullable: true
  - name: cust_build_status
    data_type: string
    description: 建档状态
    dictionary: cust_build_status
    nullable: false
  - name: sign_status
    data_type: string
    description: 签约状态
    dictionary: sign_status
    nullable: false
```

## 关联关系

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_company_detail.company_id
cardinality: one_to_many
cast: null
status: proposed
evidence: code_path:CompanyService.java:88
derived_from: null
```

## 业务规则

[[建档必填营业执照]]：创建时 license_no 必填，缺失拒绝保存（见 [[企业建档流程]] 写入口）。
````

> 坏样本对照（生成提示词同步内嵌）：`related: [[cust-company-detail]]`（非法 YAML）；ground 块包在 ` ```yaml ` 围栏里（kind 丢失）；`data_type: varchar(64)`（应写族 `string`）；relation 端点写逻辑 id 而非物理键。

---

## 9. 与 llm_wiki 机制的对接点清单（实现顺序）

| # | 改动 | 位置 | 规模 |
|---|---|---|---|
| 1 | sanitize 白名单 `ground:` 围栏 | `src/lib/ingest-sanitize.ts` | 小 |
| 2 | frontmatter 盖章扩展（page_key/contract_version/anchors 校验） | `ingest.ts` 盖章层 | 小 |
| 3 | groundExtract/groundValidate + 警告日志 | 新模块 `src/lib/ground-blocks.ts`（纯函数，阶段二可平移服务端） | 中 |
| 4 | 确定性块合并（page-merge 扩展：块先抽出，散文才走 LLM merge） | `src/lib/page-merge.ts` + `ingest.ts` | 中 |
| 5 | lint 规则集（§6）+ catalog lint 输入 | 新模块 + lint 子系统挂接 | 中 |
| 6 | schema.md 路由（§1.1 目录表）+ 提取技能 v2（SKILL.md 平移 + 4 脚本作技能资源） | 项目 schema.md + 技能目录 | 中 |
| 7 | 回填接入：pending 源 POST（复用 clip/ingest 管线） | api_server 或 clip 通道 | 小 |
| 8 | 生成提示词内嵌 §8 示例 + 坏样本（两步 ingest 的 Step2 system prompt 组装） | `buildGenerationPrompt` 的 schema 注入 | 小 |
| 9 | （可选）/recall 组装端点 | api_server | 后置 |

## 10. 开放问题（评审需裁决）

1. `ground:process` 将状态机与读写效果合一——是否需要拆分（拆分利于状态机单独召回，合一利于穿透叙事）？
2. scenario 页是否保留为独立页面，还是降级为 `domain` 字段 + index 分组？（倾向保留：场景闭包是审计与回填的自然单元）
3. pattern SQL 的方言校验放哪端？（V0 建议 SQLBot 消费端校验，lint 只做表存在性）
4. `status` 过滤在 V0 由消费端做，llm_wiki search 是否需要加 frontmatter 过滤参数（阶段二再说）？
5. 目录平面（全量表/字段 catalog）在 wiki 形态下不入库——`COVERAGE_GAP` 验收依赖 catalog.yaml 常驻 `raw/sources/` 并被脚本刷新，是否可接受？
