# 知识积累完整架构设计

> **权威序：** 落地计划（含 §11）> `knowledge-catalog-linkage-revision.md` > `knowledge-accumulation-implementation.md` > **本文**。  
> 废止/降级：自研 V-T12 join 矿（改为触发 `mine_query_log_joins`）；Catalog P0 阻塞 Conversation；MVP 含 process 表（可后置）。  
> 覆盖：Catalog Plane（库侧挖掘）+ Conversation Plane（对话沉淀）  
> 含：分层、模块、触发、生命周期、信任升格、**血缘审计（可审查任一条知识的完整处理过程）**  
> 日期：2026-08-07

---

## 1. 目标与边界

### 1.1 目标

1. **当次问数**：澄清扫清业务歧义 → 生成可执行 SQL → 结果可发布。  
2. **跨会话复用**：把「库事实」与「已确认业务语义」沉淀为可召回资产。  
3. **不淹没 LLM**：先裁决再注入；Bind/Structural 尽量不进长上下文。  
4. **不污染知识库**：候选隔离；认证前不全局强制；漂移可失效。

### 1.2 三分边界

| 系统 | 职责 | 非职责 |
|------|------|--------|
| **Chat / Graph** | 会话编排、SSE、ChatRecord/ChatLog | 不作组织级口径真相 |
| **Contract** | 当次执行意图（可修订） | 不替代跨会话知识库 |
| **Knowledge** | 跨会话资产 + 生效编排 | 不替代 schema sync；不堵答数 |

### 1.3 双平面

| 平面 | 回答的问题 | 主资产 |
|------|------------|--------|
| **Catalog** | 有什么表、长什么样、怎么连、枚举值 | Schema / Profile / Stats / Relation / Dictionary |
| **Conversation** | 业务怎么算、用户怎么说、怎么查过 | Caliber / Example / Term / Process（辅） |

---

## 2. 分层架构

```text
L6  Experience
    Chat UI · Clarification Card · Config Assistant · 审核台
        │
L5  Runtime Orchestration
    NLQ LangGraph（拓扑不因知识分叉）
        │
L4  Knowledge Compile          ← 唯一生效闸
    Bind | Structural | Constrain | Exemplify | Clarify | Drop
        │
L3  Retrieval Providers        ← 只产候选，不裁决
    Schema · Relation · Dict · Term · Caliber · Example · Process
        │
L2  Published Assets           ← Source of Truth
    Catalog 正式产物 ∪ Conversation 正式产物
        │
L1  Staging / Candidates       ← 检疫区，默认不召回进 NLQ
    knowledge_staging · relation CANDIDATE · dict 未发布代
        │
L0  Capture / Mine
    Catalog: sync · facts_only · semantic · dict refresh
    Conversation: turn extract · user save · correction
        │
Infra
    ChatRecord · ChatLog · Datasource · Embedding · Queue · Executor
```

**依赖：** 写 L0→L1→L2→Index；读 L2→L3→L4→L5。Index（向量）可重建，非真相。

---

## 3. 模块划分

### 3.1 模块地图

```text
apps/datasource/profiling + crud + dictionary     # Catalog L0–L2（已有）
apps/terminology + data_training                  # Term/Example 物理表（已有）
apps/knowledge/
  capture/     # Conversation L0
  staging/     # Conversation L1
  assets/      # Caliber/Example/Process + 适配 Term/Training
  index/       # 可重建 embedding
  retrieval/   # L3 Providers
  compile/     # L4
  lineage/     # 不可变事件流 + 审查 API（§10）
  promotion/   # 升格/降格规则（与 lineage 同事务打点）
apps/chat/...  # Contract + NLQ 消费 Bundle；ChatLog.knowledge_apply 反链
config_assistant/  # L6 运营 + show_knowledge_lineage
```

### 3.2 职责矩阵

| 模块 | 输入 | 输出 | 禁止 |
|------|------|------|------|
| Catalog Mine | DS、表选择、队列 | profile/stats/CANDIDATE/DDL CONFIRMED | 写 Caliber；问数时采矿 |
| Dictionary | configure/refresh | published_generation 快照 | ask 时远程 DISTINCT |
| Capture | TurnSnapshot / 保存事件 | KnowledgeCandidate[] | 直写 Published |
| Staging | Candidate | pending/conflict/rejected | 被 NLQ 召回 |
| Assets | Publish 命令 | 正式行 + version/supersede | 拼 prompt |
| Index | 正式行变更 | embedding | 存业务真相 |
| Retrieval | question+scope+stage | 候选列表+score | Bind/截断最终集 |
| Compile | 多路候选+本轮上下文 | KnowledgeBundle | 写库 |
| Assess/Generate | Bundle | 澄清或 SQL | 私自堆知识 |
| ChatLog | 当次 NLQ | 执行审计、knowledge_apply 反链 | 当知识生命周期库 |
| Lineage | 资产变更 | 不可变事件+证据快照 | 篡改历史；替代 ChatLog |

### 3.3 Compile 输出合同

```text
KnowledgeBundle {
  bound: Requirement[]              # 进 Contract，0 prompt token
  structural: StructuralHints       # schema/relation/stats（可适配 get_table_schema）
  constrain_cards: Card[]           # 短约束，计入预算
  exemplars: Card[]                 # ≤K 骨架
  clarify_hints: ClarificationQuestion[]
  dropped: Hit[]                    # 仅日志
  apply_log: ApplyHit[]             # 写入 ChatLog
}
```

### 3.4 优先级（冻结）

```text
P0 本轮用户原话 / 本轮澄清回答
P1 certified/golden Caliber·Term（可 Bind）
P2 Dictionary 发布值 · CONFIRMED Relation（Structural）
P3 trusted Caliber（强 Constrain，默认不 Bind）· trusted Example
P4 published Example/Term（弱）
P5 Process · Relation CANDIDATE · admitted（默认 Drop）
```

### 3.5 Apply 强度

| Apply | 含义 | 进 LLM？ |
|-------|------|----------|
| Bind | 直接进 Contract / 实体绑定 | 否 |
| Structural | schema/成本/CONFIRMED join | 走 schema 通道，不占口径卡片 |
| Constrain | 短卡片约束 | 是，预算内 |
| Exemplify | few-shot 骨架 | 是，≤K |
| Clarify | 冲突或业务槽 | 出题，不塞冲突双方全文 |
| Drop | 丢弃 | 否（仅日志） |

---

## 4. 资产模型

### 4.1 Catalog 资产

| 资产 | 存储 | 发布态 | 默认 Apply |
|------|------|--------|------------|
| Schema + Embedding | core_table/field | sync 即用 | Structural |
| Profile / Stats | snapshot + approx_rows | generation / READY | Structural |
| Relation | field_relation | CANDIDATE→CONFIRMED | CONFIRMED→Structural；CANDIDATE→Drop |
| Dictionary | dictionary_value | published_generation | Bind（实体） |

### 4.2 Conversation 资产

| 资产 | 存储 | 发布态 | 默认 Apply |
|------|------|--------|------------|
| Term | terminology | enabled+published | Constrain |
| Caliber | business_caliber（新） | staging→published；认证后可 Bind | Bind/Constrain |
| Example | data_training | staging→published | Exemplify |
| Process | process_episode（新） | 派生检索 | Exemplify（弱） |
| Entity 增补 | → dictionary staging | 随 dict 发布 | → Catalog Bind |

### 4.3 统一元数据（概念）

```text
scope, status,
trust_tier: observed|admitted|published|trusted|certified|golden,
certified: bool,
source_type,                 # chat_auto|user_save|admin|import|ddl|probe|…
natural_key, version, superseded_by, embedding?,
# 血缘（必填关联，见 §10）
lineage_id,                  # 稳定血缘根 ID（跨 version 不变）
provenance: KnowledgeProvenance  # 当前头指针摘要
```

---

## 5. 全部沉淀触发场景（Capture Triggers）

下列为**实际应支持**的触发面。每一类都给出：条件、抽取物、信任、是否可 auto-publish。

### 5.1 Catalog 侧触发

| ID | 触发名 | 条件 | 抽取/写入 | 信任 | Auto-publish |
|----|--------|------|-----------|------|--------------|
| **C-T1** | Schema Sync | chooseTables / sync_catalog / sync_single / 建 DS 选表 | 表字段替换；reconcile dict；enqueue facts_only | 物理事实 | Schema 即时；profile 经 READY |
| **C-T2** | Facts Bootstrap | worker 领取 facts_only/full | stats、field_profile、DDL FK→CONFIRMED、publish generation、re-embed | 高（DDL FK）/中（采样 profile） | Profile 达门槛才 READY；DDL 可 CONFIRMED |
| **C-T3** | Semantic Mining | facts 后 high_value 或手动 semantic/full/manual | relation CANDIDATE、探针证据 | 中低 | **否**（保持 CANDIDATE） |
| **C-T4** | Relation Decide | Admin/Config `decide_field_relation` | CANDIDATE→CONFIRMED/REJECTED | 高 | 人审即发布 |
| **C-T5** | Dictionary Configure | Admin 配置字段 | field_config | — | 未 refresh 前不进 NLQ |
| **C-T6** | Dictionary Refresh | 手动/工具 refresh | DISTINCT→新 generation→published | 高（截断拒发） | 成功则切换 published |
| **C-T7** | Manual Profile Refresh | API/config refresh_metadata_profile | 重跑 facts/semantic | 同 C-T2/T3 | 同左 |
| **C-T8** | Schema Drift Reconcile | sync 指纹变化 | dict STALE；profile STALE；对话资产 disable（焊接后） | — | 失效，非新知识 |

### 5.2 Conversation 侧触发

| ID | 触发名 | 条件 | 抽取物 | suggested_trust | Auto-publish |
|----|--------|------|--------|-----------------|--------------|
| **V-T1** | 澄清链成功 | clarification_parent 子 turn 含 submitted_answers，且后续 outcome∈{success,degraded} 且有成功 step | Caliber（user:answer 子句）、Entity、Process、可选 Example | Caliber/Entity=high；Process=high | **否**（Caliber 默认 pending）；Entity 可合并至 dict staging |
| **V-T2** | 无澄清但查询成功 | status=ready，有 SQL，quality 达阈值，至少一 step 成功 | Example、Process；仅当 clause 含 user:question 强证据时可选 Caliber draft | Example=medium；Process=medium | Example 默认关；Caliber 更严 |
| **V-T3** | 用户显式「保存为口径」 | UI/API save_caliber | Caliber 从当前 Contract 快照 | high + certified 候选 | 可一键 pending→人审快速发布 |
| **V-T4** | 用户显式「保存为样例」 | UI/API save_example | Example（planning_question + SQL 骨架） | high | 可快速发布到 data_training |
| **V-T5** | 用户显式「保存术语」 | UI/API save_term | Term | high | 审后/管理员可发 |
| **V-T6** | 纠错 / Refine 否定 | 下轮 omit/replace 已确认槽，或明确否定旧口径 | 旧资产 supersede **候选**；新 Caliber/Process 负样本 | — | **禁止** silent 覆盖正式库 |
| **V-T7** | Thumbs down / 负反馈 | 用户点踩或「SQL 不对」 | 命中 Example/Caliber trust↓；Process 负样本 | low | 踢出 Bind 池；可进 review |
| **V-T8** | Thumbs up / 收藏 | 用户点赞 | 提高 staging 优先级；可建议 publish | — | 仍建议人审 Caliber |
| **V-T9** | 评估失败但 SQL 成功 | contract=None 或 assess 降级，仍执行成功 | Process（low）；可选 Example pending | low | **不**抽 Caliber |
| **V-T10** | 部分成功 / degraded | 部分 step 成功，quality 低或 partial contract | Process；Example 仅成功 step 骨架 | low–medium | 默认 staging only |
| **V-T11** | 同 chat 基线继承（非全局沉淀） | new_intent_context(base_contract) | **不写知识库**；仅当次 draft 种子 | — | N/A（会话记忆≠组织知识） |
| **V-T12** | 稳定 Join 模式（反向 Catalog） | 多次成功 turn 使用相同资源对 + 可解析 equi-join | field_relation **CANDIDATE** source=chat | medium | **否** |
| **V-T13** | Config Assistant 运营写入 | 助手工具创建/编辑术语、确认关系、发布 staging | 各对应正式资产 | high（人工） | 按工具语义 |
| **V-T14** | 批量导入 | Excel/API 导入 terminology、data_training | Term/Example | 中高 | 按现有导入策略 |
| **V-T15** | 管理员禁用/恢复 | disable/enable 正式资产 | 状态变更 | — | 即时影响召回 |

### 5.3 明确不触发沉淀

- 澄清中未完成（needs_clarification 停住）的中间 draft  
- 纯 model assumption（无 user 证据）且用户未确认  
- 一次性主键/订单号等 ephemeral 字面量作 Caliber  
- 权限子查询、平台默认 LIMIT、内部 span  
- Relation CANDIDATE 未确认前  
- Dictionary 未 published 的 generation  
- Process 全文 reasoning dump（可指针到 ChatLog，不进正式语义库）

---

## 6. 沉淀全过程（Capture → 使用）

以下为**通用流水线**；各触发只是入口不同。

### 阶段 0：形成 TurnSnapshot（运行时结束时）

```text
TurnSnapshot {
  record_id, chat_id, ds_id, oid, assistant_id?,
  original_question, planning_question,
  intent_context (contract, answers, assumptions, questions),
  clarification_parent_id?,
  plans[], steps[] (sql, data, error),
  outcome, quality, contract_status,
  knowledge_apply_from_this_turn[]   # 本轮用过哪些资产
}
```

异步投递，**失败不影响**已发布答案。

### 阶段 1：Capture（识别与抽取）

```text
for each enabled extractor matching trigger:
  if not eligible(trigger, snapshot): skip
  emit KnowledgeCandidate {
    kind, payload, natural_key, scope,
    source_record_id, evidence_level,
    suggested_trust, quality_snapshot, trigger_id
  }
```

**Eligible 要点：**

- 可复用结构（非 ephemeral）  
- scope 已知  
- Caliber：需 user_confirmed 或 V-T3  
- Example：exec 成功 + quality 门槛（或 V-T4）  
- Entity：用户选中选项  
- Process：成功必抽；失败可抽 low  

**Payload 要点：**

- Caliber：`contract_fragment`（与 QueryContract 同构）、label、summary、field_targets  
- Example：`question_norm`、`sql_skeleton`（字面量参数化）、contract_summary  
- Entity：phrase、canonical、field 定位  
- Process：压缩 Episode（understanding / clarification / generation / outcome）  
- Term：word、other_words、description  

### 阶段 2：Staging 检疫（Admission）

对每条 Candidate **依次**：

1. **Schema 对齐**：field_targets 在当前 catalog 存在；否则 reject 或 conflict。  
2. **Natural_key 去重**：同 key → merge/更新候选，不堆多条。  
3. **冲突检测**：同 label 不同 clause_signature → `conflict`，禁止 auto-publish。  
4. **字面量清洗**：Example/Process 骨架化。  
5. **范围校验**：ds/assistant 与 source record 一致。  
6. **有害 SQL**：非只读等 → 拒绝 Example。  
7. **优先级**：user_supplement / certified 与 auto 冲突 → 自动项降权。

状态：`draft → pending | conflict | rejected`。

**Staging 默认永不被 Compile 召回。**

### 阶段 3：Publish（进入 L2）

| 动作 | 谁 | 结果 |
|------|----|------|
| 人审 Publish | Admin / Config Assistant | status=published；写 assets；入索引队列 |
| 白名单 Auto | 工作区策略 | 仅 Example/Entity 等宽松项；Caliber 默认关 |
| Supersede | 新版发布 | 旧版 superseded_by；召回只见 head |
| Disable | 运营/漂移/负反馈 | 即时退出召回 |

Catalog 侧 Publish 对应：profile READY 世代、dict published_generation、relation CONFIRMED。

### 阶段 4：Index

```text
on publish/update/disable:
  upsert or delete embedding(label+summary+question_patterns)
  索引失败 → 标 embed_stale，不回滚正式行
```

### 阶段 5：Retrieval（下一次问数）

```text
query = retrieval_question 或 planning 摘要
scope filter = oid + ds + assistant
status = published ∧ enabled ∧ trust≥通道门槛

各 Provider topK（小）:
  Schema/Profile/Relation/Dict/Term/Caliber/Example/Process
→ 附 score, trust, certified, usage_success
```

### 阶段 6：Compile（裁决）

```text
merge candidates
  → 去重（natural_key / 语义簇）
  → 冲突 → Clarify 或只留 P0/P1
  → 分级 Apply
  → 按 stage 硬预算截断
  → KnowledgeBundle + apply_log
```

**分 stage：**

| Stage | 侧重 |
|-------|------|
| assess | Bind Caliber/Entity；Constrain Term/Caliber；Clarify；**不要**大 SQL Example |
| generate | 未 Bind 约束；Exemplify ≤2；已 Bind 只留锁定一行 |
| repair | 仅与错误相关的 1 条负样本/方言提示 |

### 阶段 7：使用（NLQ）

```text
bound → 合并进 draft / Contract（槽位锁定，LLM 不得擅自改写该槽）
structural → get_table_schema / 成本门禁
constrain_cards → assess/generate prompt 段
exemplars → few-shot
clarify_hints → needs_clarification 卡片
apply_log → ChatLog span
```

### 阶段 8：反馈闭环

```text
命中且成功 → usage_success++
命中且失败/纠错 → trust↓，踢出 Bind；可 supersede 候选
长期无命中 → 降检索权重（冷数据）
schema 漂移 → disable 依赖资产
```

---

## 7. 端到端场景详解

### 场景 S1：首次澄清成功并沉淀（V-T1 + C-T*）

**用户：**「今年华为的签收额」

| 步 | 层 | 细节 |
|----|-----|------|
| 1 | L0 Catalog 已备 | 表已 sync；profile READY；客户-订单 CONFIRMED；company_name 已 dict refresh |
| 2 | L3–L4 assess | Schema Structural；Dict 召回「华为」多候选→Clarify；无签收额 Caliber |
| 3 | L5 澄清 | Q1 华为取值；Q2 签收额含税/合同。用户作答 → submitted_answers |
| 4 | L5 生成执行 | Contract 齐 → SQL 成功 → 发布结果 |
| 5 | L0 Capture V-T1 | Caliber「签收额」fragment+field_targets；Entity 华为；Process episode；Example 骨架 |
| 6 | L1 Staging | schema 校验通过；Caliber pending；Entity→dict staging；Example pending |
| 7 | L6 升格 | Caliber 经 E8 **certify→certified**（不仅 published）+ index；未认证不可 Bind |
| 8 | 下次 | 见 S2 |

### 场景 S2：认证口径复用（召回使用全链路）

**用户：**「今年签收额按区域」

| 步 | 细节 |
|----|------|
| Retrieval | CaliberProvider 命中「签收额」score 高、certified |
| Compile assess | **Bind** output+time_window；区域 group 未知→可能 Clarify 或模型推断+assumption |
| Structural | 表/join/rows 照常 |
| Generate | 锁定口径一行说明；可选 1 条 Example；**不再**塞完整签收额定义长文 |
| 执行发布 | 成功；usage_success++ |
| Capture | V-T2 可再积 Example；不重复建同 natural_key Caliber（去重 merge） |

### 场景 S3：口径冲突（用户补充优先）

**库内：** certified 签收额=含税  
**用户：**「按合同口径的签收额」

| 步 | 细节 |
|----|------|
| Compile | P0 用户原话与 P1 Caliber 冲突 → **Clarify 一题**（非双全文） |
| 用户选合同 | 本轮 Bind 合同口径 |
| Capture V-T1/T3 | 新 Caliber pending |
| Publish | supersede 旧含税版；旧版不召回 |

### 场景 S4：无澄清成功问数（V-T2）

**用户：**「cust_company 里 status=1 的企业名」

| 步 | 细节 |
|----|------|
| 无澄清 | Contract 由 assess 直接 ready（或弱契约） |
| 成功 | Capture Example+Process；无 user:answer → **不**抽强制 Caliber |
| Staging | Example pending；auto-publish 若关闭则等人审 |
| 召回 | 相似问法 Exemplify SQL 骨架 |

### 场景 S5：显式保存（V-T3/T4/T5）

用户点「保存为口径/样例/术语」→ Capture 带 `explicit_save` → staging 高优先级 → 可快速审发 → 立即进入下轮 Retrieval。

### 场景 S6：纠错（V-T6/T7）

| 步 | 细节 |
|----|------|
| 用户否定旧口径或 thumbs down | 命中资产 trust↓；Bind 禁用 |
| Capture | supersede 候选 + Process 负样本 |
| 不 silent 改正式行 | 待人审或新 Caliber 发布后 supersede |

### 场景 S7：评估失败降级成功（V-T9）

assess 挂掉 → contract=None → 仍 NL→SQL 成功 → 只 Process(+可选 Example pending) → **禁止** Caliber。

### 场景 S8：Schema 漂移（C-T8）

| 步 | 细节 |
|----|------|
| sync 字段改名 | dict STALE；profile STALE |
| 焊接 | 引用旧字段的 Caliber/Example → disabled |
| 下轮 | 不再 Bind；可能重新澄清 |
| 修复 | 新 version fragment → publish |

### 场景 S9：库侧语义候选（C-T3/T4）

| 步 | 细节 |
|----|------|
| semantic | 写 CANDIDATE only |
| Compile | **Drop**（不进 schema） |
| 人审 CONFIRMED | 下轮 Structural 进【Confirmed relations】 |
| 错误路径（禁止） | CANDIDATE 进 get_table_schema |

### 场景 S10：Dictionary 全链路（C-T5/T6 + V-T1 Entity）

| 步 | 细节 |
|----|------|
| configure+refresh | published 快照 |
| 问数 | Dict recall → 消歧或 Bind |
| 用户选新同义 | Entity candidate → dict staging → 下世代 refresh/publish |
| ask 时 | **永不**现场 DISTINCT |

### 场景 S11：稳定 Join 反写（V-T12）

多次成功同 join → `field_relation` CANDIDATE source=chat → 人审 → CONFIRMED → Structural。  
**禁止**自动 CONFIRMED。

### 场景 S12：部分成功 / degraded（V-T10）

只沉淀成功 step 的 Example 骨架 + Process；Caliber 仅对 user:answer 且仍成立的子句；trust 偏低。

### 场景 S13：同 chat 基线（V-T11）

`base_contract` 种子当次 draft — **不写** L1/L2；组织复用靠已发布 Caliber。

### 场景 S14：运营与导入（V-T13/T14/T15）

Config/Excel 写入正式库或 staging；disable 即时生效；与自动采集同一召回过滤。

### 场景 S15：Compile 防淹没（横切）

10 条相似口径 → 去重留 certified → 接近分冲突 Clarify → 其余 Drop；Exemplify≤2；卡片字数封顶；apply_log 可审计。

---

## 8. 与 NLQ Graph 的挂接（不改拓扑）

```text
resolve_access_scope
  →（触发）retrieval providers
  → compile(assess)
  → ground_entities          # Dict Bind/Clarify
  → match_training           # 可并入 Example provider
  → retrieve_schema          # Structural
  → assess_clarity
  → compile(generate)        # 增量 exemplars
  → generate_queries → execute → decide → …
  → on terminal accept/complete → async capture
```

---

## 9. 信任升格（Trust Promotion）— 自动沉淀如何变成可信知识

> 核心命题：**Capture 只证明「发生过」；Publish 只证明「进过库」；Trusted/Certified 才证明「可以代表组织口径去 Bind」。**  
> 升格是独立闸门，不能与「写进 staging」或「published 可被 Exemplify」混为一谈。

### 9.1 为什么必须单独设计升格

| 误解 | 风险 |
|------|------|
| 澄清成功 = 全局真理 | 情境性口径（这次含税）污染所有后续问数 |
| 执行成功 = 口径正确 | SQL 碰巧跑通 ≠ 业务定义对 |
| published = 可 Bind | 未认证样例/弱口径会静默改写用户意图 |
| 用量高 = 可信 | 错口径被反复命中会自我强化 |

业内对应：ThoughtSpot coaching / Wren memory store 确认；Catalog 已有 `CANDIDATE→CONFIRMED` 与 dict 发布代。Conversation 必须有**按资产分档**的同等阶梯。

### 9.2 信任阶梯（统一状态，分权生效）

```text
L0  observed     Capture / 检疫中           → 不召回
L1  admitted     Staging 通过 pending       → 不召回（仅运营可见）
L2  published    已进正式库可检索           → 默认可 Exemplify / 弱 Constrain
L3  trusted      自动或半自动升格条件满足   → 强 Constrain；Example 加权
L4  certified    人工认证 / 显式保存并审核  → 可 Bind（Caliber）
L5  golden       组织黄金（可选）           → Bind + 高权重；变更需管理员
```

**与 Compile Apply 硬绑定（推荐默认）：**

| 最高档 | Caliber | Example | Relation | Process |
|--------|---------|---------|----------|---------|
| admitted | Drop | Drop | Drop | Drop |
| published | 弱 Constrain 或 Drop* | Exemplify | — | 弱 Exemplify |
| trusted | **强 Constrain，默认不 Bind** | Exemplify 优先 | — | 禁止 Bind |
| certified / golden | **Bind** | Exemplify 优先 | CONFIRMED≡certified | 禁止 Bind |

\* 工作区可规定未认证 Caliber 完全不进 prompt。  
Dictionary `published_generation` ≈ trusted；Relation `CANDIDATE`≡admitted，`CONFIRMED`≡certified。

### 9.3 升格证据包（Evidence Pack）

| ID | 证据 | 来源 |
|----|------|------|
| E1 | 用户确认（user:answer / 显式保存） | 澄清、V-T3/T4/T5 |
| E2 | 执行成功 | outcome |
| E3 | 质量门槛（非 unreliable 等） | result_quality |
| E4 | 复现（独立 turn≥N） | usage / 再次确认 |
| E5 | Schema 仍有效 | catalog |
| E6 | 无未解冲突 | staging/assets |
| E7 | 窗口内无负反馈 | feedback |
| E8 | 人工背书 | admin/config |
| E9 | 全局成立（非纯情境） | 策略/人审 |
| E10 | 来源可靠（DDL/dict 校验） | Catalog |

### 9.4 按资产升格路径

**Caliber（最严，唯一默认可 Bind）：**  
`V-T1 → admitted` →  
(1) V-T3+人审 E8 → **certified→Bind**；或  
(2) E1∧E2∧E3∧E4∧E5∧E6∧E7 → **trusted（仅强 Constrain）** → 再 E8 → certified；或  
(3) 审核台 E8 → certified。  
**默认：trusted 仍不 Bind。** 禁：仅 V-T2/V-T9、冲突未解、schema 失效。

**Example（中）：** E2∧E3∧E5∧E7 → 可选 auto **published**（Exemplify）；复现/V-T4→trusted 加权；**永不 Bind**。Auto 默认建议关。

**Term：** 同义合并可谨慎；新定义要 E8。  

**Entity→Dict：** staging → configure 存在 + 发布代 → published≈trusted。  

**Relation：** CANDIDATE=admitted；人工/DDL CONFIRMED=certified；禁探针自动确认。  

**Process：** 最多弱 Exemplify；不设 certified/Bind。  

**Profile/Stats：** READY 门槛 → Structural trusted；不走 Caliber 阶梯。

### 9.5 自动 vs 人工

| 动作 | 自动？ | 条件 |
|------|--------|------|
| admitted→published Example | 可选 | 开关+E2 E3 E5 E7 |
| admitted→published Caliber | **默认否** | 人审/显式保存流 |
| published→trusted Caliber | 可 | E1–E7 |
| trusted→certified Caliber | **默认否** | E8 |
| CANDIDATE→CONFIRMED | **否**（非 DDL） | E8；DDL 用 E10 |
| 任意→Caliber Bind | 仅 certified | Compile 硬编码 |

### 9.6 降格（对称且更激进）

点踩/纠错 → demote 或 disable；schema 漂移 → 立即踢 Bind；冲突新认证 → supersede；失败率高 → trusted 降 published。  
**降格自动、升格保守。**

### 9.7 模块与运营

```text
evaluate_promotion(asset) -> Decision
apply_promotion / demote
队列：待认证 Caliber · 可 trusted 候选 · 冲突降格 · Relation CANDIDATE
工具：certify_caliber · promote_example · list_promotion_queue
```

策略旋钮：`caliber_bind_requires=certified`、`example_auto_publish=false`、`reproduce_count_N=2..3`、`allow_user_certify` 等。

### 9.8 升格场景

**U1** 澄清一次 → 人审认证（主路径）→ certified → Bind。  
**U2** 复现升 trusted（强 Constrain，仍不 Bind）→ 再人工 certify。  
**U3** 显式保存快轨 → 简化人审 → certified。  
**U4** 误认证后纠错 → demote/disable → 新口径重走 U1。  
**U5** Example 开关打开 → published Exemplify，永不 Bind。

### 9.9 升格验收

1. admitted Caliber 零 Bind。  
2. 无 E8 不能自动 certified。  
3. CANDIDATE 永不 Structural。  
4. 降格/漂移后下轮立即不可 Bind。  
5. apply_log 含 trust_tier 与 promotion_path。

---

## 10. 血缘与审计（Provenance）— 任一条知识可审查完整处理过程

> 要求：**知识来源、检疫结果、升格依据、使用与降格**都必须与资产强关联，支持从任意一条知识反查「从哪来、凭什么升、谁批的、被谁用过、为何失效」。  
> 与 ChatLog 分工：ChatLog 审计**当次 NLQ 执行**；Knowledge Lineage 审计**资产生命周期**。NLQ 命中通过 `knowledge_apply` 双向挂接。

### 10.1 设计原则

1. **一资产一血缘根**：`lineage_id` 跨 version/supersede 稳定；每次 publish/promote 追加事件，不改写历史。  
2. **事件不可变**：只追加 `KnowledgeLineageEvent`，禁止改旧事件。  
3. **证据快照化**：升格时把 Evidence Pack **固化进事件 payload**（含当时 record_id、quality、schema fingerprint），避免事后源记录被改导致「证据消失」。  
4. **外键可点穿**：事件引用 `ChatRecord.id`、`clarification_parent_id`、`metadata_scan_run.id`、`staging_id`、`actor_user_id`、ChatLog span id（若有）。  
5. **头摘要 + 事件流**：资产行上保留 `provenance` 摘要便于列表；详情拉全量事件。  
6. **与 Compile 一致**：`apply_log` 必须带 `asset_id + lineage_id + trust_tier + event_id(升格到当前档的那次)`。

### 10.2 数据模型

#### KnowledgeProvenance（资产头摘要）

```text
KnowledgeProvenance {
  lineage_id: str
  origin_trigger: C-T*|V-T*          # 首次捕获触发器
  origin_source_type: chat_auto|…
  origin_record_id?: int             # 首个 ChatRecord
  origin_scan_run_id?: int           # Catalog 挖掘
  origin_staging_id?: str
  current_trust_tier: …
  certified_by?: user_id
  certified_event_id?: str
  last_event_id: str
  last_event_at: datetime
  evidence_summary: { e1..e10: bool|count }  # 当前是否仍满足
}
```

#### KnowledgeLineageEvent（不可变事件）

```text
KnowledgeLineageEvent {
  event_id, lineage_id, asset_kind, asset_id, asset_version,
  at, actor: { type: system|user|admin|assistant, id? },
  action:  # 见下表
  from_tier?, to_tier?,
  trigger_id?,                   # C-T* / V-T*
  refs: {
    record_ids[],                # ChatRecord
    clarification_parent_id?,
    chat_log_ids[]?,             # 相关 span
    scan_run_id?,
    staging_id?,
    parent_event_id?,            # 因果链
    related_asset_ids[]?,        # 合并/supersede 对端
  },
  evidence_snapshot: {           # 升格/降格时必填
    pack: { E1..E10: value },
    planning_question?,
    contract_fragment?,
    sql_skeleton?,
    quality_snapshot?,
    schema_fingerprint?,
    notes?,
  },
  decision: { result: allow|deny|noop, reason_code, reason_text? },
  payload: {}                    # 差异/合并细节等
}
```

#### action 枚举（完整处理过程覆盖）

| action | 含义 |
|--------|------|
| captured | L0 抽取产生 candidate |
| quarantine_passed / quarantine_failed | Staging 检疫 |
| merged | natural_key 合并进已有候选/资产 |
| conflict_marked / conflict_resolved | 冲突 |
| published | 进入 L2 |
| indexed / index_failed | 向量索引 |
| promotion_evaluated | 跑升格规则（无论是否通过） |
| promoted | 升档（附 evidence_snapshot） |
| certified | 人工认证（E8） |
| demoted | 降档 |
| disabled / enabled | 启停 |
| superseded | 被新版替代 |
| recalled | 被 Retrieval 命中（可采样/计数，详单可聚合） |
| applied | 被 Compile 采用（bind/constrain/exemplify）— 可写精简事件或只写 ChatLog 反链 |
| feedback_positive / feedback_negative | 点赞点踩 |
| schema_invalidated | 漂移失效 |
| corrected | 纠错流产生 supersede 候选 |

### 10.3 来源关联（Knowledge ↔ Source）

| 知识类型 | 必须关联的来源 | 升格时额外固化 |
|----------|----------------|----------------|
| Caliber | origin `record_id` + `user:answer` question_ids；contract_fragment | E1–E8 快照、认证人、复现 record_ids[] |
| Example | record_id、sql_skeleton、planning_question | quality、是否 explicit_save |
| Term | 创建 actor、可选来源 record | 审核人 |
| Entity/Dict 增补 | record_id、field 定位、canonical | publish generation |
| Relation CANDIDATE | scan_run_id 或 chat record_ids；probe 证据 | decide 时 actor + 理由 |
| Relation CONFIRMED DDL | extract 约束来源/scan | E10 |
| Process | record_id、episode 指针 | 不认证 |

**多来源复现（E4）：** `promoted` 事件的 `refs.record_ids` 列出全部独立 turn；头摘要 `evidence_summary.E4=count`。

### 10.4 审查入口（产品能力）

从任意资产详情页必须能看到：

1. **时间线**：该 `lineage_id` 下全部事件（旧→新）。  
2. **来源跳转**：一键打开源 ChatRecord / 澄清父记录 / profiling run。  
3. **升格卷宗**：最近一次 `promoted/certified` 的 evidence_snapshot 原文。  
4. **使用轨迹**：近期 `applied`（或由 ChatLog `knowledge_apply` 反查 record 列表）。  
5. **当前有效性**：E5 schema、是否 superseded、trust_tier。  

API 示意：

```text
GET /knowledge/assets/{id}                 # 含 provenance 头
GET /knowledge/lineage/{lineage_id}/events # 全量时间线
GET /knowledge/assets/{id}/usage           # 反查 ChatRecord
```

Config Assistant：`show_knowledge_lineage(asset_id)`。

### 10.5 与 ChatLog 的双向挂接

```text
NLQ Compile 时:
  ChatLog.span.payload.knowledge_apply[] = {
    asset_id, lineage_id, trust_tier, apply, promotion_event_id
  }

知识侧（可选异步）:
  append applied 事件（采样或全量，按量级配置）
  或仅依赖 ChatLog 反查，避免事件爆炸
```

**推荐：** 命中详情以 ChatLog 为准做反查；lineage 上保留聚合计数 + 最近 N 次 applied 引用，全量审计走「按 asset 查 ChatLog」。

### 10.6 不可省略的审计检查点（写入规范）

任一资产变更路径必须打点：

```text
captured → quarantine_* → published → indexed
         → promotion_evaluated → promoted/certified
         →（使用）applied via ChatLog
         → demoted|disabled|superseded|schema_invalidated
```

缺事件 = 发布/升格 API 失败（事务内写事件）。

### 10.7 示例：一条 Caliber 的完整卷宗

```text
lineage_id=cal_签收额_ds9
1 captured          V-T1 record=1001 answers=[q_tax] fragment=…
2 quarantine_passed staging=st_88
3 published         tier=published actor=system（若策略允许）/ 或仅 pending
4 promotion_evaluated deny reason=need_E8
5 certified         tier=certified actor=admin:7
                    evidence_snapshot={E1:true,E2:true,E3:good,E8:admin7, records:[1001]}
6 applied           via chat_log on record=1050 apply=bind
7 applied           record=1102
8 feedback_negative record=1120 → demoted trusted→ 或 disabled
9 captured          V-T3 新口径 record=1121
10 superseded       old → new lineage head
```

审查员打开资产 → 看见 1–10，并可点进 1001/1050 对话与 SQL。

### 10.8 红线（审计）

1. 无 `captured`/`certified` 事件不得出现可 Bind 的 Caliber。  
2. 升格事件无 `evidence_snapshot` 视为非法。  
3. 禁止覆盖历史事件；更正用新事件。  
4. supersede 必须写明 `related_asset_ids`。  
5. 源 ChatRecord 删除策略：事件内快照仍保留；外链标 broken（软删优先）。

---

## 11. 红线
## 11. 红线

1. Staging / Relation CANDIDATE / 未发布 dict **默认不进** Compile 召回。  
2. Semantic **禁止**自动 CONFIRMED 非 DDL 关系。  
3. Profile/注释 **禁止**自动变 Caliber。  
4. 问数 **禁止**现场 mining / DISTINCT。  
5. 单次澄清成功 **不等于** 全局 Bind（需认证/显式保存/策略）。  
6. Assess/Generate **禁止**绕过 Compile 私自堆知识。  
7. 用户当轮输入 **永远高于** 已发布知识。  
8. **published ≠ trusted ≠ certified**；默认仅 certified 可 Caliber Bind。  
9. **降格自动、升格保守**；禁止用量独自身把错口径推到 Bind。
10. 任一条可 Bind/可召回知识必须具备可追溯 **lineage 事件流**；升格必带 evidence_snapshot。
11. 禁止篡改历史 lineage 事件；ChatLog 与 lineage 双向可点穿。

---

## 12. 分期

| 期 | 内容 |
|----|------|
| P0 | Catalog 排水/SR stats/READY；Compile 接口薄实现 |
| P1 | Caliber staging+认证升格；**lineage 事件模型**；promotion 队列；Example 确认；漂移降格 |
| P2 | 复现→trusted；Process 弱召回；V-T12；水位；usage 反查；策略旋钮 |

---

## 13. 配套

- 交互画布：Cursor Canvas `dual-knowledge-architecture.canvas.tsx`（含「信任升格」「血缘审计」）  
- 库侧问题清单：`docs/catalog-mining-analysis-and-optimization.md`
