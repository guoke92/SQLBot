# 知识提取详细约束与契约要点

## 1. 权威顺序与证据种类

```
库字段实际值 > 代码读写(service/dao/mapper) > 文档主张 > skill 导航
```

| evidence kind | 含义 | 例 |
|---|---|---|
| `database_profile` | 库字段实际值/分布 | `cust_build_status` 实际取值 |
| `code_path` | 代码读写证据（文件:行号） | `OperCustFacade.java:1082` |
| `database_schema` | DDL/DO 字段定义 | `@TableName` + 字段 |
| `document_claim` | 文档主张（最弱） | 需求文档描述 |

> 休眠表只允许 `database_schema`（@TableName 声明）证据；`code_path`/`query_usage` 意味着存在调用链，与「休眠」矛盾。

## 2. service/dao 关联提取的三类代码事实

> **同一场景双入口**：管理端写入口（Controller + Application 保存流）与业务端读入口（Provider/@DubboService 消费流）是两条独立链路，**都要穿透并交叉核对**——只读消费端会漏掉保存/版本/幂等这类写规则（v9 提取 funding-rule 时因漏读 `FundRuleInfoApplication` 首版丢失 `version-increment-on-update` 规则）。

1. **读流转**：上一张表查询结果作为下一张表查询条件。
   `cust = getCustCompany(id)` → `custPerson = getCustPerson(cust.getCode(), personId)`
2. **写流转**：先查/建父表，再带父表 id/code 建子表。
   `pro.setProjectId("" + projectDO.getId())` → `custProjectRelService.save(pro)`
3. **跨方法参数传播**：形参/返回值/字段赋值在多方法间传递。
   `saveCustBuildRecord(companyId, personId, ...)` 的 `companyId` 来自上层调用方。

## 3. 硬约束（11 条，关系 + 表判定；concept 锚定/共享表/包级关系见 §7/§8）

1. **关系一律 `proposed`**：只有绑定执行通过才 `confirmed`；禁止因"代码里写了"就标 certified。
2. **`ref_*` 目标字段要确证，且整条关系须有代码引用**：`ref_<目标表>` 列名的目标表可从列名内嵌解析，但目标**字段**须经 `.eq()`/JOIN 确证是 `code` 还是 `id`，不得默认；**列名符合 `ref_*` 约定不等于存在关系**——须在 service/dao 中找到对该列的读/写/join 调用，全仓零引用（仅 DO 声明）时**不构成关系**（反例：`cust_auth_application.ref_cust_auth_application_tenant_product` 无任何 Java 引用，v6 曾按列名虚构、v9 剔除）。
3. **`*_id`/`*_code` 显式标目标**：必须给出目标表 + 主键字段 + 证据定位 `文件:行号`。
4. **类型 CAST 标注**：`pro.setProjectId("" + projectDO.getId())` 是 String←Long，写 `cast: long_to_string`。
5. **反规范化拷贝不标直连**：`cust_project_rel.product_id = tenant_project.product_id` 是派生，标 `derived_from: tenant_project.product_id`；真 FK 是 `tenant_project.product_id → tenant_product.id`。`funding_rule_detail.fund_rule_code_ref = funding_rule_info.code` 同理是保存时回写的冗余副本，标 `derived_from: funding_rule_info.code`，**不标 EQUI_JOIN 关系**（反例：v10 曾误标 EQUI_JOIN）。
6. **租户隔离不是关联**：`db_tenant_code` / `app_tenant_code` / `tenant_id` / `tenant_code` 排除。
7. **同名字段拷贝不是关联**：`setCompanyName(a.getName())`、`setBankCode(p.getBankCode())` 等纯拷贝（两侧字段名相同且非主键）排除。
8. **读写顺序落 `processes`**：只出静态"对子"不够，须产出读表顺序、写表顺序与 `data_effects`。
9. **n:n 或共享键/传递关系不是 JOIN，但要保留为 SHARED_KEY**：两表都多对一于同一键（n:n，如 `certification.ref_cust_company_info = account.ref_cust_company_info`），或两表都指向同一第三表（共享租户/共享项目），是「同维度事实」而非直接 JOIN，禁止标 `EQUI_JOIN`（只有「一侧真的一键一行」的 n:1/1:1 才是合法 JOIN）。**这类关系保留为 `relationship_type: SHARED_KEY`**，business_meaning 写清「两侧字段业务含义相同、取值一致，应各自 JOIN 到主表、不得直接 JOIN 彼此」——这是串联数据、判断查询 scope 的重要依据，不删除。只有纯字段拷贝（无串联价值）才删。
10. **表判定以 `@TableName` 为准（datasets/fields 只能来自 catalog）**：`extract-catalog.py` 用 `@TableName` + `@ApiModelProperty` 穷举物理表/列，这是 datasets 的唯一来源——不是「看到 `XxxDO` 类名后缀就算表」。`dataset.name` = 物理表名、`dataset.fields[].name` = 物理列名（对应 catalog 的 column，有 `@TableField("custom_col")` 覆盖时以注解为准）；`field_id` 是单元内逻辑 id（可自定义，跨单元共享时与权威单元一致）。外部接口（问卷星）、远程服务、MQ/ES/缓存没有 `@TableName`，不是表：只写进单元的 `assumptions`（如「问卷星 rspd_list 为外部接口数据集，非本地物理表」），**不写 `data_effects`**（`data_effects.dataset` 必须指向已声明的 catalog dataset）、**不进 query_patterns SQL**。
11. **休眠表保留 + 标记，不删除**：目录会列出所有 `@TableName` 表，包括休眠表（有 DO/Mapper/Service 但无入口调用链）。判休眠：`extract-callgraph.py` 先出机械可达性基线（哪些表无入口可达），AI agent 再从入口方法（`@RestController`/`@DubboService`/Facade/事件监听）DFS 复核，以编译期显式调用为准、反射/动态路由不计。休眠表**不删除**、保留在包内，只作**表级声明**（`dataset_id/name/description/database` + `inactive: true` + `fields: []`，字段留在 catalog），不进任何维度引用（relationships/metrics/calibers/rules/concepts/processes 不引用它，因为无业务逻辑可引用）；在 `coverage.yaml` 的 `inactive` 字段标注「无调用链证据」（结构化字段，非仅注释）。绑定时未匹配的表/字段软失效（标 WARNING），不阻断发布、不影响其他单元召回。反例：`funding_party_rule_cfg/detail/front` 有 DO/Mapper/Service 但资金链路由 `FundingPartyRuleProviderImpl`（@DubboService）走的是 `funding_rule_*`，前者即休眠表。

**物理表（有 `@TableName`）三分类**（外部接口不是物理表，见 §3.10）：
1. **活跃表**（有入口调用链）→ 进单元 `datasets`，字段最小声明；
2. **休眠表**（无入口调用链）→ `inactive: true + fields: []` 登记，不进维度；
3. **技术/迁移/日志表**（无问数场景：审计/日志/迁移基建、菜单/资源配置等）→ `coverage.yaml.excluded`。

> **`excluded` 判据是「无问数场景」，不是「暂未提取」**：有 `@TableName` 且有入口调用链的表，即使本包暂未提取单元，也不得 `excluded`，必须留 `COVERAGE_GAP` 提示待覆盖（反例：`cust_change_cfg`/`cust_oper_change_record` 有真实调用方，v6–v10 误列 excluded，v11 纠正为 GAP）。

## 4. 输出结构

包级关系写 `relationships.yaml`，扫描时并入 `package.relationships`（契约见 `schema.py::PackageRelationship`）。端点用**物理表名/字段名**，不是单元内 dataset_id：

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

- **EQUI_JOIN**：只有一侧真的一键一行（1:n / 1:1）才标；这类关系生成 relation_endpoint 边，召回时用于合成 JOIN。
- **SHARED_KEY**：n:n、共享键、传递关系——两侧字段业务含义相同、取值一致，但**不得直接 JOIN 彼此**（各自 JOIN 主表）；生成边时按共享键处理，不参与 JOIN 合成。
- **分工**：`relationships.yaml` 只收跨单元/包级的物理关系（一个关系涉及多个单元，或作为全局 schema 桥）；单元内部关系写进该单元 `content.relationships`。休眠表的静态 `ref_*`/FK 候选（无调用链）**不进任何关系**，只在目录留作候选。
- 端点允许不被任何单元声明（字段级最小声明的自然结果）：运行时生成 stub 节点并在绑定时对活库校验。
- 反规范化拷贝（`derived_from`）**不是关系**，不写进 relationships.yaml，只在 evidence 里标注源字段。

processes 的读写顺序按业务时序写进单元的 `content.processes[].data_effects`（`read/insert/update/delete/upsert`）。

## 5. 脚本必然出错的三个反例（为什么 service/dao 必须 AI agent）

| 反例 | 脚本行为 | 正确提取（读代码） |
|---|---|---|
| `cust_build_record.person_id → cust_person_info.id`：代码是 `setPersonId(personId)`，`personId` 是方法形参 | 漏掉（正则 `setXxx(var.getYyy())` 抓不到形参传播） | 顺参数链定位 `personId` 来自 `custPerson` |
| `cust_project_rel.product_id` | 误判为 `→ tenant_product.id` 直连、还抓到 `→ cust_change_cfg.id` 噪声 | 读 `pro.setProductId("" + projectDO.getProductId())` 识别为 `derived_from: tenant_project.product_id` |
| 建档读写时序（先查企业→查人→插项目关联→插建档记录） | 只能出静态对子 | 产出 `processes.writes` 顺序 |

## 6. 字段/关系的常见噪声（提取时主动排除）

- 租户隔离：`db_tenant_code`、`app_tenant_code`、`tenant_id`、`tenant_code`、`organization_id`。
- 工作流样板：`act_procinst_id` / `act_procinst_no` / `act_procinst_status` / `act_procinst_date`。
- 审计样板：`create_by` / `create_time` / `update_by` / `update_time` / `deleted` / `remark`。
- 序号字段：`_no`（order_no/certification_no/batch_no）既非关系也非枚举。
- 枚举字段：`_type` / `_status` / `_flag` / `_channel` / `_level` / `_mode` → 走 `field.dictionary`，不是关系。
- 休眠表 / 技术迁移日志表：前者 `inactive` 登记、后者 `excluded`，均不进维度引用（判据见 §3.11 物理表三分类）。
- 外部接口/远程服务（问卷星、RPC、MQ/ES/缓存）：不是表，只写 `assumptions`，不进 `datasets`/`data_effects`/query_patterns SQL（见 §3.10）。

## 7. KnowledgePackageV2 契约要点

- 顶层四段 `package` / `sources` / `evidence` / `knowledge_units` + 包级 `relationships`；`schema_version: "2.0"`。
- 单元槽位：`title/aliases/domain/applicability` + `concepts(field_targets)` + `processes(data_effects,next_stages)` + `datasets(fields)` + `relationships` + `calibers/metrics(field_targets/field+grain)` + `domain_rules(field_targets)` + `query_patterns` + `evidence_refs` + 顶层 `unit_links`。
- **休眠登记单元**：当单元所有 datasets 均 `inactive: true` 时允许六层全空（schema 放行），仅登记休眠表；不得再混入任何维度（schema 拒绝）。休眠表字段留在 catalog，不进包。
- **concept 必须 `field_targets`**：状态类→承载字典的字段（字典跨两个字段时两个都写）；实体类（概念即一张表）→该表 `id` 或业务键。键一致是硬要求，值措辞可有详略。
- 关系默认 `proposed`；查询范式 `PENDING_VALIDATION`。
- 跨单元共享表：目标表用最小声明（`dataset_id` + 仅本单元用到的字段），字段 payload（field_id/name/data_type/dictionary/description）与权威单元**逐字一致**。
- `unit_links`（prerequisite/validates）必须带 `via` + `evidence_refs`；数据耦合 shares_data 由运行时推导，**禁止声明**。
- `units` 是相对路径清单（非 glob）；单文件内联 `knowledge_units` 是退化形态。
- `coverage.yaml` 不入库、不进 Prompt、不门禁（`COVERAGE_GAP` 只做离线验收阻断）。`excluded`（技术/迁移/日志表）与 `inactive`（休眠表，保留+软失效）互斥，判据见 §3.11；`inactive` 表仍须在单元里以 `inactive: true` 表级声明覆盖，否则仍算 `COVERAGE_GAP`；暂未提取的活跃表既不 `excluded` 也不 `inactive`，留 `COVERAGE_GAP` 待覆盖。

## 8. 维度提取方法（关系之外每类的 HOW）

关系已在上文 §3–§5 给全。其余维度按此表执行：

| 维度 | 谁 | 方法 | 落点 |
|---|---|---|---|
| **枚举字典值** | 脚本 | `extract-enums.py` 扫 `*Enum.java` 的 `NAME("dictKey","显示名")`，确定性产出 dictKey+显示名；**全量进 `enums.yaml`，不进包** | `enums.yaml` |
| **枚举进包筛选** | AI agent | 枚举名 `XxxEnum` → 字段 `xxx`（蛇形候选）先在 catalog 核对；**只有字段已在包内 + 值有业务语义**才写 `field.dictionary`；系统实现枚举（time_unit/sign_mode/redirect_type 等）留在 `enums.yaml` 参考，不进包 | `field.dictionary` |
| **状态机** | AI agent | 收集 `setXxxStatus(Enum.Y.getDictKey())` 写值点，串成 `from→event→to`；**区分多套状态机**（建档有认证流 BUILD_* 与审核流 CUST_BUILD_* 两套）；event=业务动作（提交认证/审核通过） | `processes.next_stages` |
| **口径** | AI agent | 从 mapper WHERE + service 分支提取状态谓词组合，成 `名称 = 可执行谓词`；**标注 scope**（是全局定义还是某接口语境）；"认证成功"≠"审核通过"这类同义陷阱显式标注 | `calibers` |
| **指标** | AI agent | 从 mapper `COUNT(`/`SUM(`/`AVG(` + `GROUP BY` 聚合点归成业务指标；**标注 grain（去重粒度）**——COUNT(企业) 还是 COUNT(企业-项目关系) | `metrics` |
| **业务规则** | AI agent | 从 service 分支提取：锁/幂等/回滚/默认值/条件写值（如"供应商+ACFLOW→status='1'"） | `domain_rules` |
| **术语/场景** | AI agent | 从入口方法 + 注释 + 业务文档对齐：canonical term + aliases + 对应表 | `concepts` |
| **概念锚定** | AI agent | 每个 concept 写 `field_targets`：状态类→承载其 `dictionary` 的字段（字典跨字段时全写）；实体类→表 `id`/业务键；键值与该字段 dictionary 键一致 | `concept.field_targets` → concept_of 边 |
| **共享表治理** | AI agent | 每个物理表一个权威单元声明完整业务字段；其余单元最小声明且字段 payload 逐字复制 | decompose 零 intra-package 冲突 |
| **unit_links** | AI agent | 只有代码能证明调用链/状态校验时才声明 prerequisite/validates，`via` + `evidence_refs` 必填 | `unit_links` → precedes/validates 边 |
| **查询范式** | AI agent | 从 controller 端点 + mapper select 方法提取"按 X 查 Y 列表/数量" | `query_patterns` |
| **场景发现** | 脚本+AI agent | 脚本枚举 `@RestController`/`@DubboService`/Facade 入口；AI agent 归类成业务场景清单 | 场景清单 |

## 9. 证据自动生成

关系/口径/枚举/状态机/指标的每条证据都必须能定位到 `文件:行号`，`locator` 指向**真实 DO/Mapper 文件**（可含 `:行号`），不得用单元的「主 DO」代替。脚本用 grep/ast 产出 locator，AI agent 只补充"为什么"（分支语义），不手工抄行号。枚举脚本已自动带 `path`；关系脚本带 `evidence`。

## 10. 六层八边自检清单（交付前逐项打勾）

| 边 | 来源 | 自检问题 | 空边后果 |
|---|---|---|---|
| has_field | dataset.fields | 每个声明字段都进了包？ | 无字段可召回 |
| concept_of | concept.field_targets | 每个 concept 都有 field_targets？ | 概念孤岛，召回断链 |
| references_field | caliber/rule.field_targets、metric.field/grain | 每个口径/规则/指标都有字段指向？ | 口径不可执行 |
| reads/writes | process.data_effects | 每个阶段都有 data_effects？ | 无读写顺序 |
| precedes | process.next_stages + unit_links(prerequisite) | 多阶段有 next_stages 链？ | 状态机断裂 |
| relation_endpoint | 单元 relationships + 包级 relationships(EQUI_JOIN) | 真 FK 关系都有 evidence + 类型？ | 无法跨表 JOIN |
| validates | unit_links(validates) + query_patterns.intended_specification.caliber_id | 跨单元校验/范例可复用？ | 复用断裂 |

交付前用 `scripts/knowledge-package.py scan --strict` + `decompose` 干跑验证：`concept_of` 数 = concept 数、`merge_conflicts` = 0、孤儿字段 = 0、stub 节点仅来自显式 SHARED_KEY/外部引用。

## 11. 类型族与绑定校验码表（避免 FAIL）

字段 `data_type` 与目录比对按**类型族**（不是原样字符串相等）：

| 族 | 匹配关键字（忽略大小写，去掉括号精度） |
|---|---|
| string | char、text、string、clob |
| number | int、decimal、numeric、number、float、double、real |
| temporal | date、time、timestamp |
| boolean | bool、bit |
| structured | json、map、array、struct |

- `varchar` 与 `varchar(64)` 同族；`data_type` 不确定时留空（空类型与目录一律兼容），写错类型族会 FAIL。
- `varchar`↔`bigint` 对**字段声明**是 FAIL，对 **JOIN** 是 WARNING（SQL 里写清 CAST，如 `CAST(rel.project_id AS UNSIGNED) = project.id`）。

绑定校验码（`service.py::bind_and_validate` 产出，提取侧据此避免 FAIL）：

| code | 默认严重度 | 含义 | 提取侧怎么避免 |
|---|---|---|---|
| `DATASET_NOT_FOUND` | error/FAIL | 物理表不在当前数据源 | `name` 写真实表名，不是语义 ID |
| `FIELD_NOT_FOUND` | error/FAIL | 物理列不在该表 | `field.name` 写真实列名 |
| `FIELD_TYPE_MISMATCH` | error/FAIL | 声明类型族 ≠ 目录 | 按库填写或留空 `data_type` |
| `RELATIONSHIP_NOT_BOUND` | error/FAIL | 关系两端字段没绑上 | 先修好表/字段 |
| `RELATIONSHIP_TYPE_MISMATCH` | warning/error | JOIN 两端类型不同 | string/number→告警；其它不兼容→失败；SQL 写 CAST |
| `RELATIONSHIP_PROPOSED` | warning | status≠confirmed | 默认即可；双证据再 confirmed |
| `QUERY_PROTOCOL_UNSUPPORTED` | warning | 数据源非 SQL | 可保留示例 |
| `QUERY_VALIDATION_FAILED` | warning | SQL 无法通过目录/方言校验 | 物理表名、只读、可解析 |
| `QUERY_EXECUTION_FAILED` | warning | 只读执行失败 | 修正 SQL；不要假装 executed |
| `DATASOURCE_CATALOG_MISMATCH` | 包级 warning/error | 选中源缺少声明表 | 只声明该源真实存在的表 |

- 非维度引用的休眠表/字段（`inactive`）未匹配时降级为 WARNING，不阻断发布。
- 提交审核门禁：当前单元 DRAFT 且校验 PASS 或 WARNING；FAIL 被拒绝。

## 12. 坏样本与成功标准

**坏样本（禁止）**：
1. **泛化治理提醒当规则**：无 `field_targets` 的过程说明（如「代码关系必须经画像确认」）→ 写 README，不进包。
2. **技术完成=业务成功**：推送记录表成功 ≠ 建档成功，须用主数据状态字段表达业务终态。
3. **猜测字段**：无枚举/代码路径/画像时，不要写「某 flag 表示离职风险」，宁可 `assumptions` 或删字段。
4. **同名字段当关系**：`left.id → right.id` 必须有 JOIN 条件或外键证据。
5. **伪造已执行**：未在目标库执行时 verification 只能 PENDING_VALIDATION。
6. **一张表/一个词一个单元**：单元是场景闭环，不是表或词。
7. **1.0 条目塞 2.0**：扁平 items 不接受，必须重写成场景单元。

**成功标准（验收，当且仅当同时满足）**：
1. **结构通过**：KnowledgePackageV2 校验无异常、ID 唯一、证据与字段引用闭合。
2. **能绑定目标数据源**：每个 `dataset.name` 命中物理表、每个 `field.name` 命中物理列；缺表/缺字段/类型族冲突 → FAIL，包无法提交审核。
3. **场景可问数**：每个单元能回答「用户说某句业务话术时落到哪些表/字段/值/关系/过滤/口径」。
4. **不伪造**：未执行 SQL 不得写 executed/passed；关系默认 proposed。

