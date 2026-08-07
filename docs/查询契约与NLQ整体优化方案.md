# 查询契约与 NLQ 整体优化方案

> 配套文档：[澄清交互-同轮暂停续跑方案.md](./澄清交互-同轮暂停续跑方案.md)（交互唯一路径，本文不重复展开）。  
> 原则：去冻结、强澄清、有数必发、不建双轨、不做存量兼容。

---

## 0. 一句话目标

> **去掉流程冻结；澄清阶段用业务语言扫清会改变结果的歧义；形成当前契约后再生成 SQL；本阶段 SQL 以 LLM 为主（确定性编译保留但关闭接线）；LLM 服从已确认口径；执行前处理严重语义冲突；有成功结果就发布并用评分说明质量；仅当不违背确认就无法给出可执行 SQL 时，才同轮再暂停澄清。**

---

## 1. 已拍板决策摘要

| 项 | 决议 |
|---|---|
| 澄清强度 | 尽量问清业务歧义再生成（非「能猜就少问」） |
| 澄清交互 | 同轮暂停 / `continue` 续跑；删父子 record（见配套文档） |
| 澄清次数 | 最多 2 卡；第 2 次仅「已确认不可执行 / 互斥」；单卡 ≤4 题 |
| 评估出口 | 清晰直跑；完全不懂 → 失败换问法；澄清系统异常重试后 → 失败 |
| 无契约生成 | 基本禁止（日常必须可执行契约） |
| 确认 vs 可执行冲突 | 先不违背确认的 repair → 再暂停澄清 → 再不行失败；禁止静默改口径 |
| 有数后契约偏差 | **不澄清**，只评分 + 总结披露 |
| simple_sql | 架构保留，**本阶段关闭接线** |
| repair 预算 | 近现状双预算 + **强制 fallback**（不得丢成功结果） |
| 多事实 population | 业务语言必问（不问表/JOIN） |
| 追问继承 | 可判 new/refine，**默认偏 refine** |
| 历史兼容 | 不做 |

---

## 2. 分层职责（禁止重复治理）

```text
用户问题
  → 召回 / 实体 / schema / 时间
  → 语义评估 → draft / questions
  → [可选] 同轮 pause/continue（见配套文档）
  → materialize 当前 QueryContract
  → LLM 生成 SQL（本阶段）
  → protocol.validate_plan（技术门禁）
  → 执行前严重契约差 → 共享 repair 预算
  → 执行 → 结构分析
  → fallback 铁律 → 评分发布
```

三类产物各管一条出路：

| 产物 | 唯一后果 | 不管 |
|---|---|---|
| `ContractSlot` / `ClarificationQuestion` | `awaiting_input` 暂停 | 实现细节、字段映射、SQL 修法 |
| `ContractIssue` | assumption / 日志 / 评分 | 弹澄清卡、停死流程 |
| SQL / 结果验证报告 | repair 或降分发布 | 问用户怎么写 JOIN |

**禁止**把 `clarify | repair | warn` 塞进 `ContractIssue.action`。  
**禁止**拼接全部 ChatRecord 历史作执行上下文；执行只消费：

```text
base_contract + 本轮 question + submitted_answers → 当前契约
```

审计链仅用于追溯。

---

## 3. 澄清内容边界（与交互文档配合）

### 3.1 白名单（可问）

- 统计主体 / 粒度  
- 指标口径  
- 时间口径（用户表达模糊时）  
- 实体取值歧义  
- 用户话里出现的数据保留范围  
- 多事实 **population**（交集 / 单侧 / 并集）——纯业务语言  

### 3.2 黑名单（不可问）

- 选表、JOIN、桥表、方言写法  
- `field_not_in_schema` / 召回不全  
- 用户未提的系统过滤政策 → 保守默认 + assumption  
- 明细列表再问「唯一标识」  
- SQL 缺字段 / 结果结构问题 → repair / 评分  

### 3.3 次数与口子收窄

| 次序 | 允许 | 题量 |
|---|---|---|
| 第 1 次 | 白名单业务歧义 | 尽量少，硬上限 **4** |
| 第 2 次 | 仅已确认不可执行 / 确认互斥 | **≤2** |
| 第 3 次起 | 禁止 | 按已确认生成；仍不可执行 → failed |

「口子收窄」用**允许题型集合缩小**实现，不靠模型自觉。

### 3.4 评估三出口

| 情况 | 行为 |
|---|---|
| 清晰、无业务歧义、可执行形状 | `ready` + 契约 → 生成 |
| 完全无法理解 / 无法形成可答业务题 | **failed**，提示换问法 |
| 评估链路系统异常，重试 1 次后仍挂 | **failed：澄清异常**（不生成 SQL） |

意图评估重试与 SQL repair **分账**。

### 3.5 自定义回答

- 已选结构化选项：锁定不重问  
- 自定义：仅相关槽位再评估；不得借机扩大白名单  
- 若需再问：优先同 record 第 2 次暂停（且仅冲突类），否则 assumption  

---

## 4. 契约生命周期

### 4.1 删除

- 流程意义的 `freeze` / 「冻结后不可改」  
- `minimal_executable`（confirmed-only salvage）  
- `IntentStatus.blocked`（契约准备失败）及 `contract-preparation-blocked`  
- `_severity_for(confirmed → blocking → 停死)`  

保留：Pydantic 对象 `frozen=True`（防原地改）；`RunOutcome` 级权限等技术阻断可保留。

### 4.2 状态

```text
evaluating | needs_clarification | ready
```

- `ready` ⇒ 必须有可执行 `QueryContract`  
- 日常路径禁止 `contract=None` 生成；失败应在评估/澄清出口消化  

### 4.3 materialize（唯一成型入口）

```text
有白名单 questions → needs_clarification → pause_intent
否则 build contract
  has_executable_shape → ready(contract)
  否则 → 能构造业务/冲突题则 pause；否则 failed
validate_contract → 只产 ContractIssue → assumptions/评分，不改 status 为 blocked
```

`has_executable_shape`：

- detail：≥1 projection + 可解析 resource  
- aggregate：≥1 output + 可解析 resource  
- 仅有 predicate/order 等不能单独成契  

### 4.4 source / evidence

只用于优先级、评分、说明。  
`user:question` / `user:answer:*` = 高优先级约束。  
不用于：能否进 SQL、是否停死。

### 4.5 追问继承

```text
有 base_contract 且本轮不像全新问题 → 默认 refine 合并
仅高置信 new 或明显换题 → 丢弃继承
```

防模型随口 `new` 切断口径。执行上下文仍不拼全文历史。

---

## 5. SQL 生成

### 5.1 双路径定位（本阶段）

| 路径 | 本阶段 |
|---|---|
| 确定性编译 `simple_sql` | **保留模块，拆除/关闭接线**；不进主路径 |
| LLM | **唯一启用路径**；prompt 强制遵循当前契约与 `user:*` |

日后开启编译的条件：契约稳定、白名单极窄、与 `validate_plan` **同一验收门**（禁止第二套 accept）。

### 5.2 LLM 与已确认事实

1. 默认服从已确认槽位  
2. 冲突：在不违背确认下重写（计 SQL repair）  
3. 仍无合法 SQL → 同轮第 2 次 `pause_intent`（冲突题）  
4. 禁止静默改 `user:answer` 还当高可信成功  

### 5.3 执行前严重语义差（可 repair， ideally 未执行）

仅确定性可识别项，例如：

- 明确要求的 output 缺失  
- 聚合 operation 不一致  
- 时间槽明确 violated  
- predicate 与确认明显不一致  

仅 warn：AST 不可观察、召回不全、bridge 难证、alias 不确定、`unsupported`。

执行前修不好且无法不违背确认 → pause（无成功业务结果）或 failed。

### 5.4 执行后（有数）

- 有成功 step → **必须发布**（可 degraded）  
- 契约 partial / 结构不完美 → **评分 + 总结**，**禁止**再 `pause_intent`  
- 空结果（0 行成功）→ 正常结果，不因空变 failed  
- 总结失败 → 程序化兜底，不影响数据卡  

「能执行 ≠ 与契约一致」；执行后的偏差是**质量问题**，不是交互分叉。

---

## 6. Repair、候选与发布

### 6.1 预算（本阶段）

短期保留近似现状：

- 计划侧 regen（如 `MAX_PLAN_REGEN`）  
- 执行后轮次（如 `MAX_BATCH_ROUNDS`）  

**铁律（必须落地，否则架构空话）：**

1. 进入 repair 前，若有成功结果 → 写入 `fallback_candidate`  
2. 禁止用清空重来输掉已有成功结果  
3. 有 fallback 时最终不得空白失败  
4. 结构 repair **禁止**把计数清零后无限嵌套（日志区分两类重试；用户侧只说自动重试）  

后续若难排查，再收成单一 `MAX_REPAIR_ATTEMPTS`（单独变更，不与交互双轨并存）。

### 6.2 候选语义（唯一模型）

```text
active_candidate      当前验证/执行
fallback_candidate    最近「至少一条成功 step」的候选
accepted_candidate    最终展示
```

（可用现有 `rejected_candidate` 升级语义并改名，**不要**并行两套候选字段。）

```text
if active 有成功结果 → accept active（可 degraded）
elif fallback 有成功结果 → accept fallback（degraded）
else → failed
```

### 6.3 真正 failed

- 评估：无法理解、澄清系统异常耗尽  
- 技术：不可解析、非只读、明确不存在标识符、权限/连接、预算内全失败且无 fallback  
- 二次澄清后仍无法在不违背确认下生成可执行 SQL  
- 用户 cancel 等待  

---

## 7. 质量与前端

- `contract_status` / assumptions / 结构问题 → `result_quality` 降分  
- 低分 → `degraded` + 仅供参考文案，**不挡有数发布**  
- 删除 `contract-preparation-blocked` 分支  
- 澄清文案：确认会影响结果的业务口径（等待中）  
- 执行详情：本阶段 `generation_source` 多为 `llm`  

---

## 8. 模块改动总表（与交互文档一致处不重复造轮）

| 模块 | 契约/生成/repair | 交互（详见配套文档） |
|---|---|---|
| `query_contract.py` | 去流程 freeze / minimal_executable；materialize + executable_shape | — |
| `semantic_intent.py` | 去 blocked；ready 必有契约；三出口；refine 偏置 | status 与 awaiting 对齐 |
| `clarification.py` | 白/黑名单；题量；第 2 次收窄；自定义不扩题 | 评估失败不硬跑 |
| `contract/validation.py` | 诊断不转停死 | — |
| `planning.py` | 执行前严重差透出；关闭 compiled 主路径调用 | — |
| `simple_sql.py` | 保留文件，拆除接线 | — |
| `nlq.py` / `plan_policy.py` | fallback 铁律；执行后不因契约偏差 pause | `run_mode` / `pause_intent` / `hydrate_resume` |
| `plan_policy.py` | 双预算 + 禁清零丢结果 | — |
| `result_quality.py` | 无契约不应出现在成功路径；partial 降分 | — |
| 前端 | 质量/假设展示；去 preparation-blocked | continue / 同 record SSE |
| 模型 | 可升 intent 版本 | drop `clarification_parent_id` |
| YAML | 尽量不增并行 graph；`run_mode` 路由 | 见配套文档 |

---

## 9. 实施分期（整块替换，不留双轨）

### P0a — 澄清交互唯一路径（优先）

见配套文档第 12 节：continue/cancel、pause、删父子、前端同 record。

### P0b — 契约与门禁

1. 去 intent blocked / freeze 停死 / preparation-blocked  
2. 澄清白名单 + 上限 4 + 最多 2 卡 + 第 2 次收窄  
3. 评估三出口  
4. materialize + has_executable_shape；ready 必有契约  
5. 执行前严重冲突 → repair；执行后有数只评分  
6. refine 偏置  
7. 关闭 `simple_sql` 接线  

### P0c — fallback 与发布

1. `fallback_candidate` 铁律  
2. 终端有成功结果必发布  
3. 评分/总结披露偏差  

### P1 — 体验与可选深化

1. resume_cache 指纹与短路径稳定  
2. （可选）LangGraph checkpoint 真暂停——**替换** hydrate 拼装，不是并行第二套  
3. 监控：澄清率、二卡率、失败原因、fallback 率  
4. 契约稳定后再评估打开确定性编译  

调试包、打包脚本与核心流程拆开提交。

---

## 10. 验收标准（总）

**交互**

- 澄清过程不新增第二条用户消息；同 `record_id` 完成  
- `clarification_parent_id` / `clarification_for_record_id` 零引用（除 drop 迁移）  
- `awaiting_input` ⇒ `finish=false`  

**澄清与契约**

- 有实质业务歧义 → 暂停澄清；无歧义可执行 → 直跑  
- 单卡 ≤4；意图链 ≤2 卡；第 2 卡仅冲突类  
- 完全不懂 / 澄清异常 → failed，不生成 SQL  
- 无日常 `contract=None` 生成；无意图 preparation-blocked  

**生成与发布**

- 确认冲突：不违背确认的 repair → 再澄清 → 失败；无静默改口径  
- 执行成功有数据 → 必发布；偏差只靠评分/总结  
- repair 失败但有过成功候选 → 发布该候选  
- 主路径不调用 `simple_sql`  
- 追问默认能继承上一有效契约（误 new 有防护）  

**防双轨**

- 无父子澄清协议与 continue 并存  
- 无 `ContractIssue.action` 三态框架  
- 无第二套 SQL accept / 第二套候选模型  
- 无「能跑优先」与「强澄清」两套互相打架的文档叙事（以本文为准）  

---

## 11. 明确不做（减法清单）

- EvidenceLedger / RequirementRevision / ContractSnapshot 表与状态机  
- 全历史 ChatRecord 拼接进 prompt  
- 多轮开放式 contract repair 循环  
- 手写通用 SQL Builder（本阶段）  
- 图内为契约偏差在「已有成功结果」后再 pause  
- 任何「过渡期双写 parent + continue」  

---

## 12. 一句话总决议

> **同轮暂停澄清（唯一交互）+ 可修订契约（去冻结）+ LLM 生成（编译暂关）+ 执行前修严重冲突 + 有数必发与 fallback；删除一切父子澄清与契约停死旁路，不留兼容双轨。**
