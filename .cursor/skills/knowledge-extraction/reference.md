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

## 2. service/dao 关联提取的三类代码事实

1. **读流转**：上一张表查询结果作为下一张表查询条件。
   `cust = getCustCompany(id)` → `custPerson = getCustPerson(cust.getCode(), personId)`
2. **写流转**：先查/建父表，再带父表 id/code 建子表。
   `pro.setProjectId("" + projectDO.getId())` → `custProjectRelService.save(pro)`
3. **跨方法参数传播**：形参/返回值/字段赋值在多方法间传递。
   `saveCustBuildRecord(companyId, personId, ...)` 的 `companyId` 来自上层调用方。

## 3. 硬约束（9 条，违反即返工）

1. **关系一律 `proposed`**：只有绑定执行通过才 `confirmed`；禁止因"代码里写了"就标 certified。
2. **`ref_*` 目标字段要确证**：`ref_<目标表>` 列名的目标表可从列名内嵌解析，但目标**字段**须经 `.eq()`/JOIN 确证是 `code` 还是 `id`，不得默认。
3. **`*_id`/`*_code` 显式标目标**：必须给出目标表 + 主键字段 + 证据定位 `文件:行号`。
4. **类型 CAST 标注**：`pro.setProjectId("" + projectDO.getId())` 是 String←Long，写 `cast: long_to_string`。
5. **反规范化拷贝不标直连**：`cust_project_rel.product_id = tenant_project.product_id` 是派生，标 `derived_from: tenant_project.product_id`；真 FK 是 `tenant_project.product_id → tenant_product.id`。
6. **租户隔离不是关联**：`db_tenant_code` / `app_tenant_code` / `tenant_id` / `tenant_code` 排除。
7. **同名字段拷贝不是关联**：`setCompanyName(a.getName())`、`setBankCode(p.getBankCode())` 等纯拷贝（两侧字段名相同且非主键）排除。
8. **读写顺序落 `processes`**：只出静态"对子"不够，须产出读表顺序、写表顺序与 `data_effects`。
9. **n:n 或共享键/传递关系不是 JOIN，但要保留为 SHARED_KEY**：两表都多对一于同一键（n:n，如 `certification.ref_cust_company_info = account.ref_cust_company_info`），或两表都指向同一第三表（共享租户/共享项目），是「同维度事实」而非直接 JOIN，禁止标 `EQUI_JOIN`（只有「一侧真的一键一行」的 n:1/1:1 才是合法 JOIN）。**这类关系保留为 `relationship_type: SHARED_KEY`**，business_meaning 写清「两侧字段业务含义相同、取值一致，应各自 JOIN 到主表、不得直接 JOIN 彼此」——这是串联数据、判断查询 scope 的重要依据，不删除。只有纯字段拷贝（无串联价值）才删。

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

## 7. KnowledgePackageV2 契约要点

- 顶层四段 `package` / `sources` / `evidence` / `knowledge_units` + 包级 `relationships`；`schema_version: "2.0"`。
- 单元槽位：`title/aliases/domain/applicability` + `concepts(field_targets)` + `processes(data_effects,next_stages)` + `datasets(fields)` + `relationships` + `calibers/metrics(field_targets/field+grain)` + `domain_rules(field_targets)` + `query_patterns` + `evidence_refs` + 顶层 `unit_links`。
- **concept 必须 `field_targets`**：状态类→承载字典的字段（字典跨两个字段时两个都写）；实体类（概念即一张表）→该表 `id` 或业务键。键一致是硬要求，值措辞可有详略。
- 关系默认 `proposed`；查询范式 `PENDING_VALIDATION`。
- 跨单元共享表：目标表用最小声明（`dataset_id` + 仅本单元用到的字段），字段 payload（name/data_type/dictionary/description）与权威单元**逐字一致**。
- `unit_links`（prerequisite/validates）必须带 `via` + `evidence_refs`；数据耦合 shares_data 由运行时推导，**禁止声明**。
- `units` 是相对路径清单（非 glob）；单文件内联 `knowledge_units` 是退化形态。
- `coverage.yaml` 不入库、不进 Prompt、不门禁（`COVERAGE_GAP` 只做离线验收阻断）。

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

关系/口径/枚举/状态机/指标的每条证据都必须能定位到 `文件:行号`。脚本用 grep/ast 产出 locator，AI agent 只补充"为什么"（分支语义），不手工抄行号。枚举脚本已自动带 `path`；关系脚本带 `evidence`。

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

