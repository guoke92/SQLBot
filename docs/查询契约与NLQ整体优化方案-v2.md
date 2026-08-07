# 查询契约与 NLQ 整体优化方案 v2

> **版本**：v2（相对 [查询契约与NLQ整体优化方案.md](./查询契约与NLQ整体优化方案.md) 的改进版；**不修改** v1 原文）  
> **配套交互**：[澄清交互-同轮暂停续跑方案-v2.md](./澄清交互-同轮暂停续跑方案-v2.md)  
> **对照分析摘要**：见文末附录；详细业界对照不替代本文决议  

---

## 0. 一句话目标（v2）

> **去冻结；业务歧义用短、准、可审计的澄清扫清（可显式采用推荐）；形成可执行契约后再生成 SQL；本阶段以 LLM 生成（确定性编译保留但关闭接线）；执行前修严重冲突；有数必发并以评分/解释披露质量；仅当不违背确认无法得到可执行 SQL 时同轮再暂停；用语义治理中长期减负，而不是加澄清轮次。**

---

## 1. 相对 v1 的主要改进

| 主题 | v1 | v2 |
|---|---|---|
| 澄清逃生 | 基本必须答完 | 增加 **按推荐全部继续**（显式、可审计） |
| 出题质量 | 主要靠 prompt | **schema 质检闸**：坏选项不下发 |
| 题量 | 硬顶 4 | **目标 1～2**，硬顶 4；强调短澄清 |
| 暂停工程 | 协议层 | 幂等 / 禁静默 skip / 原文保留（见交互 v2） |
| 有数后冲突 | 已规定不澄清 | 强化为与业界「可解释降置信」对齐的发布原则 |
| 战略减负 | 未展开 | 增加 **语义层/指标/视图** 中长期路线，避免澄清变相做 schema linking |
| 可观测 | 验收列表 | 增加运营指标与失败码 |
| 评估失败 | 三出口 | 保留，并强调与「推荐续跑」互不混淆 |

---

## 2. 已拍板决策摘要（v2）

| 项 | 决议 |
|---|---|
| 澄清强度 | 业务歧义尽量问清；实现/映射不问 |
| 澄清交互 | 同轮 pause + `continue`/`cancel`；删父子 record |
| 推荐续跑 | 每题均有推荐时可 `accept_recommendations`；记 assumption |
| 澄清次数 | ≤2 卡；第 2 卡仅确认冲突类；单卡目标 1～2、硬顶 4 |
| 评估出口 | 清晰直跑；不懂 → failed；系统异常重试后 → failed |
| 无契约生成 | 日常禁止 |
| 确认冲突 | 不违背确认的 repair → 再 pause → failed；禁静默改口径 |
| 有数后偏差 | **不 pause**；发布 + 评分 + 总结/口径说明 |
| simple_sql | 保留、关接线 |
| repair | 近现状双预算 + **强制 fallback** |
| population | 业务语言问范围，不问 JOIN |
| 追问 | 默认可 refine；防误 new |
| 语义治理 | P1+ 用指标/视图/样例 SQL **减少**澄清，不替代契约 |
| 历史兼容 | 不做 |

---

## 3. 分层职责（禁止重复治理）

```text
用户问题
  → 召回 / 实体 / schema / 时间
  → 语义评估 → draft / questions（经出题质检闸）
  → [可选] pause ←→ continue（作答或采用推荐）
  → materialize QueryContract
  → LLM SQL（本阶段）
  → validate_plan
  → 执行前严重契约差 → repair
  → 执行 → 结构分析
  → fallback → 评分 / 解释发布
```

| 产物 | 唯一后果 | 不管 |
|---|---|---|
| `ContractSlot` / `ClarificationQuestion` | `awaiting_input` | 表/JOIN/方言、SQL 修法 |
| `ContractIssue` | assumption / 日志 / 评分 | 弹卡、停死 |
| SQL/结果验证报告 | repair 或降分发布 | 问用户实现细节 |

禁止：`ContractIssue.action` 三态框架；全历史 ChatRecord 拼接进执行上下文。

执行上下文唯一：

```text
base_contract + 本轮 question + submitted_answers → 当前契约
```

---

## 4. 澄清内容与出题闸

### 4.1 白名单

- 统计主体 / 粒度  
- 指标口径  
- 模糊时间口径  
- 实体取值歧义  
- 用户话里的数据保留范围  
- 多事实 population（业务语言）  

### 4.2 黑名单

- 选表、JOIN、桥表、方言  
- 字段不存在 / 召回不全（系统修或失败，不问用户「选哪个物理列」充业务题）  
- 用户未提的过滤政策 → 保守默认 + assumption  
- 明细唯一标识伪题  
- 执行后缺指标 / 结构问题 → repair / 评分  

### 4.3 次数与口子

| 次序 | 允许 | 题量 |
|---|---|---|
| 第 1 次 | 白名单 | 目标 1～2，硬顶 **4** |
| 第 2 次 | 仅已确认不可执行 / 互斥 | **≤2** |
| 第 3 次+ | 禁止 | 已确认可执行则生成；否则 failed |

### 4.4 出题质检闸（v2 必做，唯一实现点）

在 `pause_intent` **之前**（评估规范化末段）：

1. 对每题每个 `set` 选项的 requirement 跑与生成共用的字段存在性校验  
2. 剔除非法选项；若题无剩余选项 → 丢弃该题，能默认则 assumption，不能则不影响其它题  
3. 若过滤后 **零题** 且已可执行形状 → 直接 `ready`，不 pause  
4. 若零题且不可执行 → failed 或系统侧再召回一次（**评估重试分账**），仍不行 failed  

禁止另写「展示层过滤」与「校验层」两套规则。

### 4.5 评估三出口（与推荐续跑不混）

| 情况 | 行为 |
|---|---|
| 清晰无歧义且可执行 | `ready` → 生成 |
| 有合格澄清题 | `pause` |
| 完全无法理解 / 无法形成可答且不可执行 | `failed` 换问法 |
| 评估系统异常，重试 1 次仍挂 | `failed` 澄清异常 |

**采用推荐** ≠ 评估失败跳过；必须用户显式 `accept_recommendations` 或逐题提交。

### 4.6 自定义回答

结构化已选锁定；自定义仅触发相关槽位再评估；不得扩大第 1 轮白名单题集。

---

## 5. 契约生命周期

### 5.1 删除

- 流程 freeze / `minimal_executable`  
- `IntentStatus.blocked` / `contract-preparation-blocked`  
- `confirmed → blocking → 停死`  

保留：Pydantic 对象不可变；技术向 `RunOutcome` 阻断（权限等）。

### 5.2 状态

```text
evaluating | needs_clarification | ready
```

`ready` ⇒ 必须有可执行契约。日常禁止 `contract=None` 生成。

### 5.3 materialize

```text
合格 questions → needs_clarification → pause
否则 build → has_executable_shape ? ready : failed（或冲突类第 2 卡）
validate_contract → ContractIssue → assumptions/评分，不改 blocked
```

`has_executable_shape`：detail 需 projection+resource；aggregate 需 output+resource。

### 5.4 evidence

只服务优先级与评分；`user:*` 高优先；不决定停死。

### 5.5 追问

默认 refine；高置信 new 或明显换题才丢弃继承。

---

## 6. SQL 生成

### 6.1 本阶段

- LLM 唯一主路径；契约强约束 prompt  
- `simple_sql` 保留、**关接线**；日后开启须共用 `validate_plan` 验收门  

### 6.2 确认冲突

1. 不违背确认的重写（repair）  
2. 仍无合法 SQL → 第 2 次 pause（冲突题）  
3. 再不行 failed  
禁止静默改 `user:answer`。

### 6.3 执行前严重差（可 repair）

确定性可识别：缺已确认 output、聚合 operation 不一致、时间槽 violated、predicate 明显不一致等。  
不可严格证明的 → warn，不阻断执行前（或仅降分）。

### 6.4 执行后

有成功结果 → **必须发布**；partial/结构差 → 评分 + 总结/口径说明；**禁止 pause**。  
空结果成功 ≠ failed。总结失败程序化兜底。

---

## 7. Repair、候选与发布

### 7.1 预算

近现状：`MAX_PLAN_REGEN` + `MAX_BATCH_ROUNDS`。  
铁律：repair 前写入 `fallback_candidate`；禁止清零嵌套输掉成功结果；有 fallback 不得空白失败。

### 7.2 候选唯一模型

```text
active_candidate / fallback_candidate / accepted_candidate
```

（可由 `rejected_candidate` 升级改名，禁止并行两套。）

### 7.3 解释性发布（v2 强化）

对齐 Copilot「如何得出」取向，成功/降级响应应能展示：

- 已确认口径摘要（契约要点）  
- assumptions（含「采用推荐」）  
- 需求完成度 / 主要扣分原因  
- 可查看 SQL（现有能力复用，不新造平行解释系统）  

---

## 8. 中长期：语义治理减负（v2 新增，不进 P0 双轨）

业界 ChatBI 用指标层/视图降低歧义；澄清不应长期充当 schema linking。

| 阶段 | 做什么 |
|---|---|
| P0 | 交互 + 契约门禁 + 出题闸 + fallback（本方案） |
| P1 | 加强术语/指标/训练样例召回质量；选项与指标绑定优先于裸列 |
| P2 | 视图或认证指标集缩小 linking；澄清题进一步下降 |

P1/P2 **不**另建澄清协议；只减少 pause 发生率。

---

## 9. 模块与分期

### 模块

| 模块 | 要点 |
|---|---|
| 交互 | 见澄清交互 v2 |
| `clarification.py` | 白黑名单 + **质检闸** + 题量 |
| `query_contract` / `semantic_intent` | 去冻结/blocked；materialize |
| `planning` / `nlq` | 执行前 repair；执行后不 pause；fallback |
| `simple_sql` | 关接线 |
| 前端 | 推荐续跑 + 质量/假设展示 |
| 观测 | 见下节 |

### 分期

**P0a** 澄清交互唯一路径（continue/cancel/推荐续跑/删父子）  
**P0b** 契约门禁 + 出题闸 + 评估三出口 + 关 simple_sql  
**P0c** fallback + 有数必发 + 解释字段  
**P1** resume 稳定 / 可选真 checkpoint（替换 hydrate，不并行）  
**P2** 语义治理减负  

---

## 10. 可观测指标（v2）

| 指标 | 用途 |
|---|---|
| `clarification_rate` | 是否过问 |
| `accept_recommendations_rate` | 逃生口是否好用 |
| `questions_per_card_p50/p95` | 题量是否失控 |
| `round2_rate` | 冲突再澄清是否异常高 |
| `assess_fail_rate` | 评估稳定性 |
| `continue_idempotency_conflict` | 双开/重放问题 |
| `fallback_publish_rate` | repair 丢结果是否消失 |
| `option_filtered_rate` | 质检闸是否过严/过松 |

---

## 11. 验收（总）

- 交互 v2 验收全部满足  
- 有合格业务歧义才 pause；推荐续跑可审计  
- 坏选项不下发；零合法题可直跑或失败，不弹空卡  
- 无 intent blocked / preparation-blocked / 父子澄清引用  
- 确认冲突无静默改口径；有数不因契约偏差再 pause  
- repair 有 fallback；主路径无 simple_sql  
- 文档与实现只有 v2 决议叙事（v1 仅存档）  

---

## 12. 明确不做

- EvidenceLedger / 冻结状态机 / 全历史拼接  
- `Issue.action` 框架  
- 超时自动 skip 生成  
- 有成功结果后的契约偏差澄清  
- parent+continue 双轨  
- P0 并行上语义层大重构（放到 P1/P2）  

---

## 13. 一句话总决议（v2）

> **同轮结构化澄清（可显式采用推荐）+ 出题 schema 闸 + 可修订契约 + LLM 生成 + 执行前修冲突 + 有数必发与 fallback；删除冻结停死与父子澄清；用语义治理中长期减问，不靠加轮次。**

---

## 附录 A. 业界对照如何影响 v2（摘要）

| 来源 | 吸收进 v2 |
|---|---|
| Cursor AskQuestion | 同 turn 结构化提问；防回灌/超时静默；禁自由文本失真 |
| OpenCode question | session 内 reply/reject；提问与权限分轨 |
| Kimi 深度研究 | 前置澄清 + **显式跳过/全面做** → 映射为 accept_recommendations |
| AmbiSQL / ChatBI | 歧义分类、短多选、库证据；交互与 linking 分层 |
| ThoughtSpot / Copilot | 歧义短问；出数后解释与降置信，不回问卷 |

| 未照搬 | 原因 |
|---|---|
| `/auto` 完全不问 | 与强澄清目标冲突 |
| 编码 Plan 逐步批工具 | ChatBI 要的是口径不是工具链审批 |
| 无限候选解释 | 问卷化与成本 |

---

## 附录 B. 文档关系

| 文件 | 角色 |
|---|---|
| `澄清交互-同轮暂停续跑方案.md` | v1 存档，勿改 |
| `查询契约与NLQ整体优化方案.md` | v1 存档，勿改 |
| `澄清交互-同轮暂停续跑方案-v2.md` | **现行交互决议** |
| `查询契约与NLQ整体优化方案-v2.md` | **现行整体决议（本文）** |
