# KnowledgePackage 2.0 第三方提取规范

> 给离线提取 Agent 的**唯一执行合同**。按本文产出的 YAML，应能在 SQLBot 中完成：登记 → 绑定数据源 → 校验（允许告警）→ 提交审核。  
> 代码权威：`backend/apps/knowledge/semantic/schema.py`（结构）与 `backend/apps/knowledge/semantic/service.py` 的 `bind_and_validate`（物理校验）。二者冲突时以代码为准。  
> 运行时目标：场景知识单元，不是术语/口径/关系/示例的扁平条目，也不是把代码切片进向量库。

---

## 0. 成功标准（验收）

提取完成，当且仅当同时满足：

1. **结构通过**：`KnowledgePackageV2` 校验无异常；ID 唯一；证据与字段引用闭合。
2. **能绑定目标数据源**：每个 `dataset.name` 能在目录里命中物理表；每个 `field.name` 能命中物理列。缺表、缺字段、字段类型族冲突会导致 **FAIL**，包无法提交审核。
3. **场景可问数**：每个知识单元能回答「用户说出某句业务话术时，落到哪些表、字段、值、关系、过滤或口径」。纯百科、纯工程规范、无数据落点的治理提醒不算完成。
4. **不伪造**：没有在目标库只读执行过的 SQL，不得写 `executed: true` / `passed: true`。关系默认 `proposed`。

允许 **WARNING**（仍可提交审核）：关系未人工确认、JOIN 两端 `varchar`↔`bigint` 需 CAST、查询示例解析/执行未通过。  
不允许 **FAIL**：表/字段找不到、字段类型族冲突、关系两端未绑定、JOIN 类型完全不兼容。

---

## 1. 一句话原则

不要做项目百科，不要把代码/文档切片后塞进知识包。每一段写入 `knowledge_units` 的内容，都必须改变问数时的选表、选字段、选值、JOIN、过滤或粒度。

```text
skills / 需求 / 设计  →  场景索引（不入库）
代码 / Mapper / 枚举   →  读写与状态证据
DDL / 只读库画像      →  表 / 字段 / 值 / 关系
                ↓
        KnowledgePackage 2.0 YAML
                ↓
     登记 → 绑定 → 校验 → 审核 → 发布
```

权威顺序（冲突时按此取舍，文档不能赢）：

```text
库字段实际值  >  当前代码读写  >  业务文档主张  >  skill / 规范导航
```

---

## 2. 产物边界（不要混）

| 产物 | 是否导入 SQLBot | 内容 |
|---|---|---|
| 工作目录 / README / 场景索引 / 待复核清单 / coverage | **否** | 域地图、冲突、假设、未提取范围、覆盖矩阵 |
| **唯一导入物**：包目录（manifest + `units/`）或单文件 manifest | **是** | `schema_version: "2.0"` 的完整包 |

磁盘上的知识包**推荐按单元拆分**，一个 `unit_id` 一个文件：

```text
<pkg>/
├── knowledge-package.yaml   # manifest：schema_version + package + sources + evidence + units
└── units/
    ├── enterprise-onboarding.yaml   # 每个文件顶层就是一个 KnowledgeUnitEntry
    └── ...
```

`units` 是**显式清单**（manifest 里的相对路径列表），不是目录 glob。`sources` / `evidence` 只在 manifest 写一次，单元通过 `evidence_refs` 引用；不在每个单元里重复声明。单文件（manifest 内联 `knowledge_units`、无 `units`）仍被接受，是拆分形式的退化形态，组装逻辑同一条。

禁止再产出或当作导入入口：

- KnowledgePackage **1.0**（顶层 `items`、`package_id` 与 `schema_version: "1.0"`）
- `asset-candidates.yaml`、`facts.jsonl`、`relations.jsonl`、`source-catalog.jsonl`
- 一张表一个单元、K1–K5 候选清单、Staging 条目

导入方式：选择该 manifest（或含它的目录/ZIP）后**直接登记**，没有预检/登记两步。scanner 把 manifest + `units/*.yaml` 组装回唯一的 `KnowledgePackageV2`，`units` 只是磁盘作者/传输格式，不进入语义契约。同 `package_id` + `package.revision` 内容变了必须**递增 revision**，否则登记失败。

### 2.1 coverage.yaml（全量覆盖清单，不入库）

提取侧必须在包目录放一份 `coverage.yaml`，把目标系统**所有**物理表（由 `@TableName` / 数据字典枚举）写进 `tables`，并把明确不做问数的工程/运维表写进 `excluded`。覆盖不由人工声明，而由 lint 自动判定：任一 unit 的 `dataset.name` 命中即 covered。

```yaml
schema_version: '1.0'
repository: pplatform-web
repository_revision: ee434954e
table_source: pplatform-apaas @TableName
tables:
  - cust_company_info
  - cust_build_record
  # ... 必须穷举，不允许漏表
excluded:
  tenant_migarory_log: 迁移日志，无问数场景
```

没有 coverage.yaml 时 `scan` 只做结构校验；有 coverage.yaml 时额外输出 QA 报告。`COVERAGE_GAP`（`tables` 中既未覆盖又未排除的表）是**阻断项**，作为「全系统无遗漏」的验收依据；其余为 advisory 质量信号。覆盖判定以 `dataset.name`（物理表名）为准，`dataset.dataset_id` 是逻辑名、不参与覆盖比对。

---

## 3. 提取工作流

### 3.1 第一遍：只建场景索引

扫描 skills、业务规则、代码地图、需求/设计文档，产出目录，**不写知识单元**：

| 业务域 | 候选场景 | 问数适用性 | 本包是否成单元 |

skill 与开发规范只做导航。禁止把「必须经画像确认」「技术完成不等于业务成功」这类过程说明写成 `domain_rules`。

### 3.2 第二遍：代码与数据闭环

对每个准备成单元的场景，沿 Controller → Service → Mapper/SQL → 表字段穿透：

- 写路径更新了哪些字段、在什么条件下；
- 读路径用了哪些 JOIN、WHERE、去重粒度、状态字典；
- 枚举/常量的**物理值**（以库为准，不以展示文案为准）。

有只读库时：核对表名、列名、真实枚举分布。没有库时：关系必须 `proposed`，假设写入 `assumptions`，不得标 `confirmed`。

### 3.3 第三遍：收成场景单元

一个 `unit_id` = 一个可问数的业务场景闭环（例如「企业建档与主数据」「企业关联项目」），不是一个词、也不是一张表。

跨场景靠**共享物理表名/字段名**拼接，不建单元关系图。每个单元写清 `applicability`（用来回答什么）以及不要用来回答什么。

写入顺序：

```text
sources → evidence → datasets（含字段）→ relationships → metrics / calibers → domain_rules → verified_query_patterns
```

先保证字段闭包，再写引用这些字段的内容。

---

## 4. 包结构（硬约束）

顶层**只允许**四段。`package` / `knowledge_units` / `content` / `SemanticFieldRef` 均为 `extra="forbid"`，多写任何未知字段会直接校验失败。

这四段描述的是**组装后**的 `KnowledgePackageV2`（唯一语义契约）。磁盘 manifest 用 `units: [units/a.yaml, ...]` 声明单元文件时，`units` 是传输字段、组装前会被移除，不能与内联 `knowledge_units` 同时出现；单元文件顶层直接是 `KnowledgeUnitEntry`，不含 `units` / `knowledge_units` 包裹层。

```yaml
schema_version: "2.0"
package: { ... }
sources: []
evidence: []
knowledge_units: []
```

禁止出现 1.0 字段：`items`、`defaults`、`target`、顶层 `package_id`（必须写在 `package.package_id`）。

### 4.1 `package`

| 字段 | 约束 |
|---|---|
| `package_id` | 非空；长期稳定；同一业务系统包不要改名 |
| `revision` | 整数 ≥ 1；内容变更必须递增 |
| `title` | 非空 |
| `namespace` | 非空；运行时 `unit_key` = `{namespace}:{unit_id}` |
| `description` | 可空字符串 |

### 4.2 `sources`

每条：`source_id`（包内唯一）、`kind`、`locator`（仓库相对路径、类名或可定位标识，禁止写「代码」）。  
允许额外字段。建议 `kind`：`mapper` / `enum` / `source_code` / `business_document` / `database_catalog`。

### 4.3 `evidence`

每条：`evidence_id`（包内唯一）、`source_id`（必须已存在）、`evidence_kind`、`locator`、`claim`（一句可验证事实）、`confidence`（0～1）。  
一条证据只说一件事。`claim` 必须能支撑后续概念/口径/规则，不能写「看到了相关代码」。

建议 `evidence_kind`：`document_claim` / `code_path` / `database_schema` / `database_profile` / `query_verification`。

### 4.4 `knowledge_units`（每个单元）

必填：`unit_id`（包内唯一）、`title`、`domain`、`description`、`content.datasets` **至少 1 个**，且 `processes` / `metrics` / `calibers` / `domain_rules` / `verified_query_patterns` **至少一类非空**。

| 字段 | 作用 |
|---|---|
| `aliases` | 用户可能说的同义词，供召回 |
| `applicability` | 本单元回答哪些问数，不回答哪些 |
| `evidence_refs` | 只能引用顶层 `evidence_id` |
| `assumptions` | 未画像确认的假设 |
| `conflicts` | 文档/代码/库不一致；问数应澄清，不要悄悄选边 |
| `confidence` | 单元整体可信度，不能替代单条 evidence |
| `revision` | 单元内容版本，≥ 1；同 `unit_id`+`revision` 内容变了会登记失败 |

`content` 固定八个桶，禁止增删键名：

`concepts` / `processes` / `datasets` / `relationships` / `metrics` / `calibers` / `domain_rules` / `verified_query_patterns`

---

## 5. 引用规则（最容易写错）

系统里有两套名字，必须分开：

| 名称 | 写什么 | 用在哪里 |
|---|---|---|
| 语义 ID | `dataset_id`、`field_id` | 关系、口径、规则、流程 `data_effects`、指标的 `{dataset, field}` |
| 物理名 | `dataset.name`、`field.name` | 绑定目录、查询示例 SQL |

`SemanticFieldRef`：

```yaml
{ dataset: company, field: build_status }   # dataset_id + field_id，不是表名/列名
```

- `dataset` 必须等于本单元某个 `dataset_id`
- `field` 必须等于该 dataset 下某个 `field_id`（**不是** `cust_build_status`）
- `data_effects.fields` 同样是 `field_id` 列表
- 查询 SQL 必须使用**物理表名和物理列名**

错误示例：关系写成 `field: cust_build_status`，而 `field_id` 是 `build_status` → 结构校验失败。  
错误示例：SQL 写成 `FROM company` 而物理表是 `cust_company_info` → 绑定后查询告警或找不到表。

绑定匹配规则：

- 表：`dataset.name` 与目录 `table_name` 忽略大小写；`dataset.database` 可空。单 schema 数据源目录里 `database_name` 常为空，唯一表名仍可命中。
- 列：`field.name` 与目录 `field_name` 忽略大小写。

---

## 6. 各内容桶怎么写

### 6.1 concepts

`concept_id`、`name`、`definition` 必填，**`field_targets` 必填（指向本单元已声明字段）**。`definition` 必须落到阶段、状态值、字段或数据边界，禁止「指企业建档这个过程」。

锚定规则：

- 状态类概念 → 承载其 `dictionary` 的字段；字典跨两个字段时两个都写。
- 实体类概念（概念即一张表）→ 该表 `id` 或业务键字段。
- 概念 dictionary 的键与该字段 dictionary 的键一致（键一致是硬要求，值措辞可有详略）。

```yaml
- concept_id: build-success
  name: 建档成功
  aliases: [认证成功, 有效已建档企业]
  definition: 主数据建档状态为 BUILD_SUCCESS 且企业生效。
  dictionary: {BUILD_SUCCESS: 认证成功, EFFECT: 生效}
  field_targets:
  - {dataset: company, field: build_status}
  - {dataset: company, field: status}
  evidence_refs: [ev-build-status-dict, ev-effect-cust]
```

同一语义只出现一次：用 `aliases` 和 `dictionary`，不要把「建档 / 企业建档 / 客户建档」拆成三个概念。展示文案与口语可以不同，**值以库字段为准**。

### 6.2 processes

每个阶段用 `data_effects` 描述对数据的读写。`operation` **只允许**：`read` / `insert` / `update` / `delete` / `upsert`。

`data_effects.dataset`、`fields` 必须已在本单元 `datasets` 中声明（`fields` = `field_id`）。

要把「推送完成」和「建档成功」分成不同阶段，禁止用技术完成冒充业务成功。

### 6.3 datasets

一个 dataset = 一个业务数据对象（一行代表什么必须写进 `description`）。过程表、关系表、历史表不要当成业务对象计数。

每个字段尽量提供：`field_id`、`name`（物理列）、`data_type`、状态/类型 `dictionary`、`evidence_refs`。

**没有依据就不要猜字段含义。** `data_type` 不确定时宁可留空：空类型与目录一律兼容；写错类型族会 **FAIL**。

类型族（绑定用，不是原样字符串相等）：

| 族 | 匹配关键字（忽略大小写，去掉括号精度） |
|---|---|
| string | char、text、string、clob |
| number | int、decimal、numeric、number、float、double、real |
| temporal | date、time、timestamp |
| boolean | bool、bit |
| structured | json、map、array、struct |

`varchar` 与 `varchar(64)` 同族；`varchar` 与 `bigint` 对**字段声明**是 FAIL，对 **JOIN** 是 WARNING（需 CAST）。

### 6.4 relationships

`left` / `right` 必须是已声明字段。禁止仅凭 `xxx_id` 或同名推定。

| 字段 | 要求 |
|---|---|
| `relationship_type` | 默认 `EQUI_JOIN` |
| `cardinality` | 建议 `1:1` / `1:n` / `n:1` / `n:n` |
| `business_meaning` | 必填级建议；审核展示用 |
| `status` | 默认 `proposed`。仅当代码 JOIN **且**库画像/外键同时支持时才 `confirmed` |

`proposed` 绑定后是 **WARNING**，不是失败。两端字段未绑上是 **FAIL**。两端 `string`↔`number` 是 WARNING；`date`↔`boolean` 等是 FAIL。

JOIN 列类型不同时，查询示例里应写清 CAST，例如 `CAST(rel.project_id AS UNSIGNED) = project.id`。

### 6.5 metrics

`aggregation`（如 `COUNT_DISTINCT` / `SUM` / `AVG`）、可选 `field`、`grain`、`filters`。引用的字段必须已声明。`filters` 只写能落成字段谓词的条件。

### 6.6 calibers

可执行口径，不是中文口号，也不是 SQL 片段。

- `contract_fragment`：结构化谓词（建议 `predicates: [{field, operator, values}]`，`field` 用 `dataset_id.field_id`）
- `field_targets`：非空，全部为本单元已声明字段

同一口径不要拆成多条规则。

### 6.7 domain_rules

三条同时非空，否则结构校验失败：

- `applicability`：适用哪些问数
- `query_impact`：如何改变选表/粒度/过滤
- `field_targets`：至少一个物理字段

没有字段落点的治理提醒、提取过程说明、代码规范 **禁止** 进入本桶。

### 6.8 verified_query_patterns

`question` + 非空 `query`。SQL 用物理名。导入**不要求**已执行。

推荐：

```yaml
verification:
  status: PENDING_VALIDATION
```

禁止在未执行时写 `executed: true` / `passed: true`。

允许使用命名参数（如 `:project_id`），绑定校验会先替换成 `'1'` 再做目录检查。查询解析失败、执行失败、非 SQL 数据源 → **WARNING**，不单独把整包打成 FAIL。

查询必须是只读；示例应能在目标库安全执行（最多探 1 行）。不要写空 SQL、伪 SQL、只有题目。

### 6.9 包级 relationships（跨单元物理关系）

跨单元关系写包级 `relationships`（manifest 顶层或独立 `relationships.yaml`，导入时并入契约）。端点用**物理表名/字段名**，不是单元内 dataset_id：

```yaml
relationships:
- left_table: cust_project_rel
  left_field: project_id
  right_table: tenant_project
  right_field: id
  evidence: write-flow:OperCustFacade.java:1082
  relationship_type: EQUI_JOIN   # EQUI_JOIN（真 FK 连接）| SHARED_KEY（共享键/传递，非 JOIN）
  cardinality: many_to_one
```

- **EQUI_JOIN**：只有一侧真的一键一行（1:n / 1:1）才标；生成 relation_endpoint 边，召回时合成 JOIN。
- **SHARED_KEY**：n:n / 共享键 / 传递关系——两侧字段业务含义相同、取值一致，但不得直接 JOIN 彼此（各自 JOIN 主表）。
- 端点允许不被任何单元声明（字段级最小声明的自然结果）：运行时生成 stub 节点并在绑定时对活库校验（lint `RELATION_UNDECLARED_ENDPOINT` 仅提示）。
- 每条关系必须带 `evidence`（write-flow / read-flow / java-eq / ref-convention）。反规范化拷贝（derived_copy）不是关系，不写进 relationships，只在 evidence 标注源字段。

### 6.10 unit_links（跨场景语义方向）

只有代码能证明调用链/状态校验时才声明（数据耦合 shares_data 由运行时推导，**禁止声明**）：

```yaml
unit_links:
- target_unit: enterprise-onboarding
  kind: prerequisite       # prerequisite（目标单元是前置流程）| validates（本单元校验目标状态）
  via: [{dataset: company, field: build_status}]
  evidence_refs: [ev-sign-service-checks-build-status]
  description: 签署协议前校验企业建档状态为审核通过。
```

`target_unit` 必须是同包内 unit_id；`via` 必须解析到本单元的 dataset/field；`evidence_refs` 必填且指向包内证据。拿不准就不写——缺一条只损失召回广度，错一条污染扩展。

---

## 7. 绑定校验码表（导入后系统会跑）

包级绑定会打**当前每个单元的最新非退役版本**。数据源覆盖不足（声明表未全部出现在目录）会给出包级告警，但仍会绑定，以便各单元展示缺表。

| code | 默认严重度 | 含义 | 提取侧怎么避免 |
|---|---|---|---|
| `DATASET_NOT_FOUND` | error / FAIL | 物理表不在当前数据源 | `name` 写成真实表名；不要写语义 ID |
| `FIELD_NOT_FOUND` | error / FAIL | 物理列不在该表 | `field.name` 写成真实列名 |
| `FIELD_TYPE_MISMATCH` | error / FAIL | 声明类型族 ≠ 目录 | 按库填写或留空 `data_type` |
| `RELATIONSHIP_NOT_BOUND` | error / FAIL | 关系两端字段没绑上 | 先修好表/字段 |
| `RELATIONSHIP_TYPE_MISMATCH` | warning 或 error | JOIN 类型不同 | string/number → 告警；其它不兼容 → 失败；SQL 里写 CAST |
| `RELATIONSHIP_PROPOSED` | warning | `status != confirmed` | 默认即可；有双证据再 confirmed |
| `QUERY_PROTOCOL_UNSUPPORTED` | warning | 数据源不是 SQL | 可保留示例 |
| `QUERY_VALIDATION_FAILED` | warning | SQL 无法通过目录/方言校验 | 物理表名、只读、可解析 |
| `QUERY_EXECUTION_FAILED` | warning | 只读执行失败 | 修正 SQL；不要假装 executed |
| `DATASOURCE_CATALOG_MISMATCH` | 包级 warning/error | 选中源缺少声明表 | 只声明该源真实存在的表，或换源 |

提交审核门禁：当前单元必须是 `DRAFT`，且校验为 `PASS` 或 `WARNING`。`FAIL` 会被拒绝。

---

## 8. 最小可登记模板

第三方应先让本模板通过结构校验，再扩展业务内容。

```yaml
schema_version: "2.0"

package:
  package_id: example-minimal-v1
  revision: 1
  title: 最小业务知识包
  namespace: example
  description: 确认 2.0 结构与引用闭包的最小示例。

sources:
  - source_id: code-status-enum
    kind: enum
    locator: com.example.enums.BuildStatusEnum

evidence:
  - evidence_id: ev-build-success
    source_id: code-status-enum
    evidence_kind: code_path
    locator: BuildStatusEnum#BUILD_SUCCESS
    claim: 建档成功状态对应物理值 BUILD_SUCCESS。
    confidence: 0.95
  - evidence_id: ev-company-schema
    source_id: code-status-enum
    evidence_kind: database_schema
    locator: cust_company_info
    claim: 企业主数据表含建档状态字段 cust_build_status。
    confidence: 0.95

knowledge_units:
  - unit_id: company-status
    revision: 1
    title: 企业建档状态
    aliases: [建档状态]
    domain: enterprise
    applicability: 企业主数据状态查询；不用于项目成员清点
    description: >
      通过 cust_build_status 区分建档成功、建档中和建档失败。
      不能只用 create_time 判断建档成功。
    content:
      concepts:
        - concept_id: build-success
          name: 建档成功
          aliases: [有效已建档企业]
          definition: cust_build_status='BUILD_SUCCESS' 的企业主数据。
          dictionary:
            BUILD_SUCCESS: 建档成功
          evidence_refs: [ev-build-success]
      processes: []
      datasets:
        - dataset_id: company
          name: cust_company_info
          description: 企业主/过程记录，一行一家企业。
          fields:
            - field_id: id
              name: id
              data_type: bigint
              evidence_refs: [ev-company-schema]
            - field_id: build_status
              name: cust_build_status
              data_type: varchar
              dictionary:
                BUILD_SUCCESS: 建档成功
              evidence_refs: [ev-build-success]
      relationships: []
      metrics: []
      calibers:
        - caliber_id: build-success-company
          label: 建档成功企业
          description: 建档状态为 BUILD_SUCCESS 的企业主数据。
          contract_fragment:
            predicates:
              - field: company.build_status
                operator: eq
                values: [BUILD_SUCCESS]
          field_targets:
            - { dataset: company, field: build_status }
          evidence_refs: [ev-build-success]
      domain_rules: []
      verified_query_patterns:
        - pattern_id: count-build-success
          question: 建档成功企业有多少
          query: >
            SELECT COUNT(1) AS built_company_count
            FROM cust_company_info
            WHERE cust_build_status = 'BUILD_SUCCESS'
          intended_specification:
            grain: company
            caliber_id: build-success-company
          verification:
            status: PENDING_VALIDATION
          evidence_refs: [ev-build-success]
    evidence_refs: [ev-build-success, ev-company-schema]
    assumptions: []
    conflicts: []
    confidence: 0.9
```

更完整的场景样例见 `docs/knowledge-extraction/knowledge-package-2.0.example.yaml`。

---

## 9. 必须避免的坏样本

### 9.1 泛化治理提醒当规则

```yaml
# 错误：无 field_targets，不能改变查询
- rule_id: verify-before-publish
  label: 代码关系必须经数据库画像确认
  content: 本包关系只作为候选。
```

过程说明写进 README，不要进包。

### 9.2 技术完成 = 业务成功

推送记录表的成功 ≠ 建档成功。必须用主数据状态字段表达业务终态，并在 concepts / processes / calibers 中分开。

### 9.3 猜测字段

无枚举、无代码路径、无画像时，不要写「某 flag 表示离职风险」。宁可 `assumptions` 或删掉该字段。

### 9.4 同名字段当关系

```yaml
# 错误
left: { dataset: project, field: id }
right: { dataset: product, field: id }
```

必须有 JOIN 条件或外键/画像证据，并写清基数与业务含义。

### 9.5 伪造已执行

未在目标库执行时，`verification` 只能是待校验，不能 `executed/passed: true`。

### 9.6 一张表一个单元 / 一个词一个单元

单元是场景闭环。跨场景共享表时，各单元各自声明自己用到的字段即可，靠物理表名对齐。

### 9.7 把 1.0 条目塞进 2.0

`kind: terminology|caliber|relation|example` 的扁平 `items` **不会被接受**。必须重写成场景单元。

---

## 10. 交付物

目录中**唯一会被扫描导入**的清单文件名：

- `knowledge-package.yaml` / `.yml` / `.json`

一次选择多个文件、目录或 ZIP 时：只认上述清单；隐藏文件、`__MACOSX`、README 会被忽略。选中**多个**清单会失败。UTF-8（允许 BOM）。ZIP 只是传输，路径中禁止 `..`。

建议同时交付（不导入）：

```text
knowledge-package.yaml
README.md              # 范围、域清单、权威来源、未提取项
review-questions.md    # 冲突、低置信度关系、缺失画像
```

敏感数据：密码、密钥、证件号、整行样本不得进入知识包。

---

## 11. 交付前自检

### 11.1 结构校验（必做）

在 SQLBot 仓库：

```bash
backend/venv/bin/python - <<'PY'
from pathlib import Path
from apps.knowledge.semantic.scanner import scan_package_payload

path = Path("knowledge-package.yaml")  # 换成实际路径
pkg = scan_package_payload(path.read_text())
print("package:", pkg.package.package_id, "rev", pkg.package.revision)
print("sources/evidence/units:", len(pkg.sources), len(pkg.evidence), len(pkg.knowledge_units))
for unit in pkg.knowledge_units:
    ds = [f"{d.dataset_id}->{d.name}" for d in unit.content.datasets]
    print("-", unit.unit_id, "datasets", ds)
PY
```

通过：无 Pydantic / ValueError；`source_id`、`evidence_id`、`unit_id` 唯一；所有 `evidence_refs` 与字段引用闭合。

### 11.2 绑定预期自检（人工对照目标库）

对每个 dataset / field：

- [ ] `name` 在目标数据源真实存在
- [ ] `data_type` 为空或与目录同族
- [ ] 关系两端字段都会被绑定
- [ ] 查询 SQL 只用物理名、只读、表在目录中
- [ ] 关系默认 `proposed`，未双证据不 `confirmed`
- [ ] 每个 unit 至少能回答一个「话术 → 表/字段/值/口径」问题
- [ ] `conflicts` 已记录口径冲突（例如「有效企业」含不含变更中）
- [ ] 没有用 `create_time` 顶替业务完成时间，除非代码就是如此且已写明

### 11.3 给 Agent 的最短执行清单

1. 扫 skills / 业务文档，只建场景索引。  
2. 从 Mapper、枚举、Service 提取表、列、状态值、JOIN、写路径。  
3. 有库则画像；无库则 `proposed` + `assumptions`。  
4. `sources` / `evidence` → `datasets` → 其余桶。  
5. 按场景聚合 `knowledge_units`。  
6. 跑 11.1 脚本。  
7. 未确认项进 README / review-questions，不进规则桶。

### 11.4 QA 自检（覆盖 + 语义质量，必做）

```bash
backend/venv/bin/python scripts/knowledge-package.py scan <包目录>
```

`qa.coverage` 给出 total / covered / excluded / gaps / undeclared；`qa.issues` 逐条给 code、severity（`blocking` / `advisory`）、unit、message。验收规则：

- `COVERAGE_GAP`（blocking）：`tables` 里既未覆盖又未排除的物理表，必须清零或补 `excluded` 理由，否则视为「全系统提取有遗漏」。
- `UNDECLARED_DATASET`（advisory）：unit 用了清单外物理表，改 coverage.yaml 或改正表名。
- `METRIC_MISSING`（advisory）：unit 没有可复用 `metrics`（聚合 + 粒度），导致「X 有多少」无法直接落到度量。
- `PROCESS_NOT_SERIALIZED`（advisory）：多阶段 `processes` 没有 `next_stages` 链或引用了未知 stage。
- `RELATION_UNJUSTIFIED`（advisory）：关系没有 `evidence_refs`。
- `FAKE_EXECUTED`（advisory）：查询范例标了 `executed/passed` 却无执行证据。
- `DOC_UNDERUSED`（advisory）：`evidence` 声明后无任何 unit 引用。

这些规则只做评审与验收，不改变 `KnowledgePackageV2` 的语义契约；结构校验仍以 11.1 为准。

---

## 12. 导入后在 SQLBot 里会发生什么（提取侧只需知道验收）

```text
登记 DRAFT
  → 选择覆盖声明表最多的数据源并绑定
  → 校验：FAIL 须改包或改声明；WARNING 可提交
  → 提交审核（整包当前有效单元）
  → 审核中心按单元批准 / 拒绝 / 请求补充
  → 全部批准后发布；问数只召回已发布单元
```

提取 Agent **不负责**调用这些 API；负责让包在绑定后不要 FAIL，并且单元对问数有用。

包阶段（由当前有效单元派生，供工作台展示）：全草稿=已登记；任一审核中=审核中；全部已批准或已发布=已批准；全部已发布=已发布。旧版 fork 后自动退役，不参与绑定/校验/提交/发布。
