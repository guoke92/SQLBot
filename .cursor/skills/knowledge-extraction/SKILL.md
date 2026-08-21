---
name: knowledge-extraction
description: >-
  SQLBot 业务知识提取通用技能。从 pplatform-web（Java + MyBatis-Plus）源码提取
  表/字段目录、关联关系、字段枚举、状态流转、口径、指标、业务规则与业务场景，
  产出 KnowledgePackageV2 场景单元包（manifest + units/*.yaml + coverage.yaml）。
  当用户需要提取、补充、更新、维护 SQLBot 智能问数知识库/知识包/场景单元，
  或涉及建档、项目审批、资金规则、CA 认证等 pplatform-web 业务知识时使用。
---

# SQLBot 业务知识提取技能

## 1. 目标与产物

一句话：从 pplatform-web 源码提取「SQL 可生成」的完整语义模型，落成 KnowledgePackageV2 单元包。

| 产物 | 生成方 | 进知识包？ | 说明 |
|---|---|---|---|
| `catalog.yaml` | 脚本 | 否 | 全表/全字段目录（物理名/类型/注释/FK 候选），参考基线 |
| `enums.yaml` | 脚本 | 否 | **全量枚举字典**（dictKey+显示名），参考基线，不进包 |
| `relationships.yaml` | 脚本 + AI agent | **是（包级 relationships）** | 代码级关系清单 + 证据，扫描时并入 `package.relationships` |
| `manifest` + `units/*.yaml` | AI agent | **是（唯一入库物）** | 语义单元包，只含业务匹配的枚举值 |
| `coverage.yaml` | 人工/脚本 | 否 | 全量表清单，离线验收，`COVERAGE_GAP` 阻断 |

## 2. 权威顺序（冲突裁决）

```
库字段实际值 > 代码读写(service/dao/mapper) > 文档主张 > skill 导航
```

- 文档不赢代码；冲突显式标 `conflicts`，不得静默。
- 关系默认 `proposed`，只有绑定执行通过才 `confirmed`。

## 3. 两平面架构

- **目录平面**（脚本穷举，全量机械）：全表/全字段/FK 候选 + **全量枚举字典**，作为「有无遗漏」的验收基线。
- **语义平面**（AI agent 提炼）：关系/枚举/状态流转/口径/指标/规则/场景，**只含这些逻辑涉及的字段**。
- 字段身上有逻辑（有枚举/被关系引用/被指标引用/进流程）才进包；纯物理字段留在目录，运行时由 schema 召回兜底。

### 3.1 枚举同样分两平面（不进包 ≠ 不提取）

枚举是字典类知识，但**不是所有枚举都进包**。许多枚举是系统实现需要，不是业务知识（用户不会用自然语言问它）。

- **完整枚举 → `enums.yaml`**（脚本穷举，参考基线，独立放置）：后续处理、消歧、补漏时查阅。
- **只有业务匹配的枚举值 → 进包**（`field.dictionary`）：须同时满足——
  1. 该字段已在包内（出现在关系/口径/指标/流程/查询范式里）；
  2. 该枚举值有业务语义（用户会用自然语言指代），不是纯技术编码。

> 判定"系统实现枚举"的信号（供 AI agent 参考，非硬规则）：值是小写技术词/无业务语义（`time_unit`=year/month、`sign_mode`=01/02）；枚举名含技术词（`redirect_type`/`ensure_trigger`/`operate_type`/`query_result`）；位于 infra/common/api 基础包而非业务域包。

## 4. 分工（脚本 vs AI agent）

| 谁 | 做什么 | 脚本 |
|---|---|---|
| 脚本 | 目录穷举、mapper 写死 JOIN、静态 `ref_*`/`*_id` 候选、**枚举字典值** | `scripts/extract-catalog.py`、`scripts/extract-relationships.py`、`scripts/extract-enums.py` |
| **AI agent** | service/dao 数据流（读流转/写流转/跨方法参数传播）+ 枚举↔字段绑定、口径/指标/状态机/规则 | — |
| 脚本 | 装配校验 + 离线 QA | `scripts/knowledge-package.py scan/submit` |

> service/dao 的关联**不得用纯正则猜**。正则只能抓表面形态（`setXxx(a.getYyy())`、`.eq()`），
> 抓不准形参传播、反规范化拷贝、类型 CAST、读写时序。这一层必须 AI agent 读代码提取（见 `reference.md`）。

## 5. 提取流程（10 步）

1. **锁定快照边界**：确认 pplatform-web commit、目标业务域、范围内表。
2. **目录穷举**：`scripts/extract-catalog.py <repo> -o catalog.yaml`（全表/字段/注释/FK 候选）。
3. **静态关系**：`scripts/extract-relationships.py <repo> -o relationships.yaml`（mapper JOIN + 静态候选）。
4. **枚举字典**：`scripts/extract-enums.py <repo> -o enums.yaml`（Java 枚举类的 dictKey + 显示名，确定性）。
5. **场景穿透**（AI agent）：选一个业务场景，从入口方法顺链路读，补出**读流转 + 写流转 + 跨方法参数传播**，产出关系 + 流转（遵守 `reference.md` §硬约束）。
6. **提其余维度**（AI agent）：状态机（`processes.next_stages`）、口径（`calibers`）、指标（`metrics`）、业务规则（`domain_rules`）、术语（`concepts`）、查询范式（`query_patterns`）——每类的 HOW 见 `reference.md` §维度提取方法。
7. **组装单元**：一个场景一个 `units/<unit_id>.yaml`，共享表用最小声明约定。
8. **coverage.yaml**：穷举全量物理表，`COVERAGE_GAP` 阻断。
9. **离线校验**：`scripts/knowledge-package.py scan --strict <dir>`（结构 + QA 自检）+ `decompose <dir>` 干跑门禁（concept_of / merge_conflicts / orphan / stub 检查）。
10. **提交**：`scripts/knowledge-package.py submit <dir>`。

## 6. 输出契约（KnowledgePackageV2，六层八边）

- `schema_version: "2.0"`；顶层四段 `package/sources/evidence/knowledge_units` + 包级 `relationships`。
- 单元 = 一个可问数场景闭包，六层必须齐全并各自产出对应边（空边即返工）：

| 层 | 提取物 | 生成边 |
|---|---|---|
| L0 | sources + evidence（file:行号） | 无（作为依据） |
| L1 | datasets（fields 最小声明） | has_field |
| L2 | concepts（**field_targets**） | concept_of |
| L3 | processes（data_effects + next_stages） | reads/writes + precedes |
| L4 | calibers/metrics（field_targets / field+grain）、domain_rules（field_targets） | references_field |
| L5 | query_patterns（intended_specification.caliber_id） | validates |
| 跨单元 | 包级 relationships + 单元 unit_links | relation_endpoint + precedes/validates |

- 每个 concept 必须 `field_targets`；每个 caliber/rule 必须 `field_targets`；metric 必须有 `field` 或 `grain`（详见 reference.md §概念锚定）。
- `units` 是相对路径清单（不是 glob）；单文件内联 `knowledge_units` 是退化形态。

## 7. 硬约束（违反即返工，详见 reference.md）

1. 关系一律 `proposed`，禁止因「代码里写了」标 certified。
2. `ref_*` 目标字段须经 `.eq()`/JOIN 确证是 `code` 还是 `id`。
3. `*_id`/`*_code` 显式标目标表 + 主键 + 证据定位 `文件:行号`。
4. 类型 CAST 标注（`String←Long` 等）。
5. 反规范化拷贝字段标 `derived_from`，不标直连。
6. 租户隔离字段（`db_tenant_code`/`app_tenant_code`/`tenant_id`/`tenant_code`）不是关联。
7. 同名字段拷贝（`setXxxName(a.getName())`）不是关联。
8. 读写顺序落到 `processes`，不只出静态对子。
9. **n:n 或共享键/传递关系不是 JOIN**：`relationship_type: SHARED_KEY`（标注业务含义，各自 JOIN 主表、不得直接 JOIN 彼此）；只有一侧真的一键一行才标 `EQUI_JOIN`。
10. **concept 必须锚定**：每个 concept 声明 `field_targets`，指向本单元已声明字段；无锚定 = 返工（生成不了 concept_of 边，概念成孤岛）。
11. **共享表单一语义**：同一物理表/字段跨单元只允许一份权威声明，其余单元用最小声明且字段 payload（name/data_type/dictionary/description）逐字复制，否则 decompose 产生 intra-package 冲突。
12. **包级关系用物理表/字段名**：`left_table/left_field/right_table/right_field + evidence`，不用单元内 dataset_id。

## 8. 附加资源

- 详细约束 + schema 要点 + evidence kinds：`reference.md`
- 建档完整示例（关系/流转/维度清单）：`examples.md`
- 契约权威：`docs/业务系统知识库提取与构建指南-v1.4-增补.md`（本技能的行为权威）
- 架构 ADR：`docs/知识体系目标架构-v3.1.md`
- 方法论：`docs/业务系统知识库提取与构建指南-v1.md`
