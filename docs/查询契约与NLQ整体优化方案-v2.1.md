# 查询契约与 NLQ 整体优化方案 v2.1

> **历史存档：不再作为实现依据。现行标准见 [NLQ 查询规划与澄清体系重构方案 v3](./NLQ查询规划与澄清体系重构方案-v3.md)。**

> **版本**：v2.1（相对 [查询契约与NLQ整体优化方案-v2.md](./查询契约与NLQ整体优化方案-v2.md)；**不修改** v1/v2 原文）  
> **配套交互**：[澄清交互-同轮暂停续跑方案-v2.1.md](./澄清交互-同轮暂停续跑方案-v2.1.md)  
> **现行实施以本文件 + 交互 v2.1 为准**

---

## 0. 一句话目标

> **去冻结；短、准、可审计的澄清（进卡必有推荐，可显式或非交互采用推荐）；可执行契约后再 LLM 生成 SQL；执行前只对可判定严重冲突 repair/再澄清；不可判定的偏差不 pause；有数必发并以固定 explain 结构披露；用语义治理中长期减问。**

---

## 1. 相对 v2 的决议补强

| 缺口 | v2.1 |
|---|---|
| 无推荐题仍可进卡 | **禁止**；无推荐则补全或删题 |
| 执行前「说不清」的契约差 | **不 pause**；warn + 继续 / repair 耗尽后 failed 或降分发布（见 6.3） |
| 解释字段未规格化 | **`outcome.explain` 固定合同**（见 7.3） |
| MCP/无 UI | 见交互 v2.1：自动采用推荐或 failed |
| 自定义扩题 | 规范化器硬约束，见交互 v2.1 |
| 未完成 record | 24h 过期 failed；列表计进行中 |

v2 其余决议（去冻结、有数必发、fallback、关 simple_sql、≤2 卡等）全部继承。

---

## 2. 决策摘要（现行）

| 项 | 决议 |
|---|---|
| 澄清交互 | 同轮 pause + continue/cancel；删父子 record |
| 进卡条件 | schema 合法 **且** 每题有有效推荐 |
| 推荐续跑 | 用户显式，或非交互通道服务端等价采用 |
| 次数/题量 | ≤2 卡；第 2 卡仅冲突类；目标 1～2 题，硬顶 4 |
| 评估出口 | 清晰直跑；不懂 failed；异常重试后 failed |
| 无契约生成 | 日常禁止 |
| 确认冲突 | 不违背确认 repair →（仅可判定且无合法 SQL）第 2 次 pause → failed |
| 不可判定契约差 | **不 pause**；warn / 降分 |
| 有数后偏差 | 不 pause；发布 + explain |
| simple_sql | 保留、关接线 |
| repair | 双预算过渡 + 强制 fallback |
| 追问 | 默认 refine |
| 语义治理 | P1/P2 减问 |
| 历史兼容 | 不做 |

---

## 3. 分层职责

与 v2 相同：Slot/Question → pause；ContractIssue → 假设/评分；SQL/结果报告 → repair 或降分发布。  
禁止 `Issue.action`、全历史拼接。

执行上下文：

```text
base_contract + 本轮 question + submitted_answers → 当前契约
```

---

## 4. 澄清内容与出题闸

### 4.1～4.3 白/黑名单与次数

与 v2 相同（业务白名单、实现黑名单、2 卡收窄、题量目标 1～2 / 顶 4）。

### 4.4 出题质检闸（唯一实现点，v2.1 加强）

在 `pause_intent` 前：

1. 选项 requirement 字段校验；剔非法选项  
2. 题无合法选项 → 丢弃该题  
3. **推荐强制**：每题必须有仍指向合法选项的 recommended；否则删题或触发评估修复重试（计入评估重试，≠ SQL repair）  
4. 零题 + 可执行 → ready；零题 + 不可执行 → failed  
5. 非交互通道：见交互 v2.1，可能跳过 pause  

### 4.5 评估三出口

与 v2 相同；**采用推荐**仅来自用户 continue 或非交互自动采用，≠ 评估失败跳过。

### 4.6 自定义

结构化锁定；再评估 **不得**新增第 1 类白名单题（规范化器强制）。

---

## 5. 契约生命周期

与 v2 相同：删 freeze / minimal_executable / intent blocked；`ready` 必有可执行契约；materialize；evidence 只服务优先级与评分；追问默认 refine。

---

## 6. SQL 生成

### 6.1～6.2

与 v2 相同：本阶段 LLM；确认冲突时不违背确认的 repair → 无合法 SQL 才第 2 次 pause。

### 6.3 执行前契约差（v2.1 钉死）

| 类型 | 条件 | 行为 |
|---|---|---|
| **可判定严重差** | 规则/AST 能确定：缺已确认 output、operation 不一致、时间槽 violated、predicate 与确认明显不一致等 | 计入 repair；耗尽后若仍无合法可执行计划 → 第 2 次 pause（冲突题）或 failed |
| **不可判定差** | AST 不可观察、召回不全、bridge 难证、alias 不确定、`unsupported`、无法证明「多余过滤」等 | **禁止 pause**；记 warn / ContractIssue；有可执行计划则执行，质量降分 |
| **执行后才发现** | 结构问题、跑出来才知的 partial | **禁止 pause**；有成功结果则发布 + explain |

铁律：**检测不到的语义问题不得转化成向用户追问。**

### 6.4 执行后

有成功结果必发布；禁止因契约/结构偏差再 pause；空结果成功 ≠ failed。

---

## 7. Repair、候选与解释合同

### 7.1～7.2

与 v2 相同：双预算 + fallback 铁律；`active` / `fallback` / `accepted` 唯一候选模型。

### 7.3 `outcome.explain` 固定合同（v2.1 必做）

成功或 degraded 的 terminal outcome **必须**带（或可空但字段齐全）的解释块，前后端只认这一处，不另造平行结构：

```json
{
  "outcome": {
    "status": "success | degraded | failed | …",
    "quality": { "…现有评分…" },
    "explain": {
      "contract_summary": [ { "label": "…", "value": "…" } ],
      "assumptions": [ { "slot_id": "…", "code": "…", "label": "…", "detail": "…" } ],
      "gaps": [ { "code": "…", "message": "…", "severity": "warn|info" } ],
      "completion_score": 0,
      "completion_reasons": [ "…" ]
    }
  }
}
```

约束：

- `assumptions` 与 intent 内 assumptions 同源，发布时快照进 explain  
- `gaps` 来自契约 partial / 结构问题 / 不可判定 warn，**不是**新澄清题  
- SQL 展示复用现有 step/sql 通道，不放进第二套 explain 树  
- failed 时 explain 可只含失败原因，字段仍存在  

---

## 8. 语义治理减负

与 v2 相同：P1 术语/指标召回；P2 视图/认证指标；不另建澄清协议。

---

## 9. 分期

**P0a** 交互 v2.1（continue/cancel/推荐强制/非交互策略/删父子）  
**P0b** 契约门禁 + 出题闸 + 不可判定不 pause + 关 simple_sql  
**P0c** fallback + `outcome.explain` 合同  
**P1** resume/checkpoint 替换 hydrate；未完成 record 运维  
**P2** 语义治理减问  

---

## 10. 可观测

继承 v2 指标，并增加：

| 指标 | 用途 |
|---|---|
| `questions_dropped_missing_recommendation` | 推荐强制是否过严 |
| `non_interactive_auto_accept_rate` | MCP 自动采用推荐占比 |
| `non_interactive_fail_need_clarify` | 无 UI 且无法自动采用 |
| `undetermined_contract_warn_rate` | 不可判定差是否过多 |
| `awaiting_expired_rate` | 暂停过期 |

---

## 11. 验收（相对 v2 增量）

- 进卡题 100% 有合法推荐  
- 不可判定契约差零 pause  
- terminal success/degraded 必含 `outcome.explain` 字段集  
- MCP：无推荐则 failed 需交互，有推荐则不 pause  
- 自定义扩题被规范化器拒绝  
- 继承 v2 全部验收；文档现行叙事为 v2.1  

---

## 12. 明确不做

继承 v2，并明确：

- 不可判定语义 → 向用户追问  
- 非交互通道静默无契约硬跑  
- 多套 explain / 质量结构并行  

---

## 13. 一句话总决议（v2.1）

> **进卡必有推荐；同轮澄清可显式或非交互采用推荐；可判定冲突才 repair/再澄清，不可判定只降分；有数必发且 explain 字段唯一；删除冻结与父子澄清双轨。**

---

## 附录. 文档关系

| 文件 | 角色 |
|---|---|
| `澄清交互-同轮暂停续跑方案.md` / `…整体优化方案.md` | v1 存档 |
| `…-v2.md`（交互与整体） | v2 存档 |
| `澄清交互-同轮暂停续跑方案-v2.1.md` | **现行交互** |
| `查询契约与NLQ整体优化方案-v2.1.md` | **现行整体（本文）** |
| `NLQ优化方案-v2索引.md` | 索引（指向现行版本） |
