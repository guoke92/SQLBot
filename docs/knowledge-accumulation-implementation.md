# 知识沉淀：完整设计与实现方案

> **权威序：** 落地计划（含 §11）> `knowledge-catalog-linkage-revision.md` > **本文** > `knowledge-accumulation-architecture.md`。  
> 本文是 **可落地的实现规格**，与架构总览配套：  
> - 架构与场景：`docs/knowledge-accumulation-architecture.md`  
> - **库侧现状 × 联动校准（开工必读）：** `docs/knowledge-catalog-linkage-revision.md`  
> - 库侧挖矿专项：`docs/catalog-mining-analysis-and-optimization.md`（P0 表已过时，以校准文为准）  
> 日期：2026-08-07 · **校准：Catalog 主体已落地，Conversation 可开工**  
> **实现状态：** Alembic `083` + `apps/knowledge/{compile,lineage,capture,staging,assets,api}` 已落地；迁移号用 **083**（非 082）。

---

## 0. 一句话与范围

**做什么：** Catalog 挖掘已基本完成；本阶段落地 Conversation 沉淀（Caliber/Example/Process）与 **Compile**，用 Staging → 信任升格 → Lineage 把知识安全送进 NLQ，并与库侧做薄联动（漂移失效、实体→dict、复用 `query_log_joins`）。

**不做什么：** 不问数现场采矿；不自动 CONFIRMED 非 DDL 关系；不把 profile 当业务口径；不绕过 Compile 堆 prompt；不建第二套 join 矿 / 第二套执行审计。

**成功标准：**

1. 澄清确认的口径可认证后 Bind，同类问题少问。  
2. 任一条知识可打开 lineage 看到完整处理过程。  
3. admitted/CANDIDATE 永不静默进 NLQ 强制路径。  
4. Catalog 发布态（PROMPT + CONFIRMED + published dict）由 Compile.Structural/Entity 消费，不双写。  
5. Prompt 知识增量受预算约束，可观测。

---

## 1. 目标架构（实现视角）

```text
┌─ Catalog Plane（主体已落地）─────────────────────────────┐
│  sync → facts → semantic(CANDIDATE) → decide / published │
│  RANK≠PROMPT；mining_policy；query_log_joins（已有）      │
└───────────────────────────┬─────────────────────────────┘
                            │ Structural / Dict（只读发布态）
┌─ Conversation Plane（本次落地）─┼─────────────────────────┐
│  turn capture → staging → publish → promote/certify      │
│  lineage events (append-only)                            │
└───────────────────────────┬─────────────────────────────┘
                            ▼
              compile_knowledge_for_turn(stage)
                            │
         bound / structural / cards / clarify / apply_log
                            ▼
                     NLQ LangGraph
                            │
              async capture ← accept/complete
              L-1 漂移失效 · L-2 实体→dict · L-3 触发 query_log_joins
```

### 1.1 信任档 × Apply（Compile 硬编码）

| trust_tier | Caliber | Example | Relation | Dict |
|------------|---------|---------|----------|------|
| admitted | Drop | Drop | Drop | Drop |
| published | 弱 Constrain 或 Drop* | Exemplify | — | — |
| trusted | 强 Constrain，默认不 Bind | 加权 Exemplify | — | published≈trusted |
| certified | **Bind** | 加权 Exemplify | CONFIRMED | — |

\* 工作区策略可关闭未认证 Caliber 的 Constrain。

### 1.2 模块落点（代码树）

```text
backend/apps/knowledge/
  models.py              # 扩展 DTO：Bundle/Card/ApplyHit（运行时）
  service.py             # recall_knowledge（现有）→ 逐步让位 compile
  providers.py           # Term + Dict（现有）
  dictionary_recall.py
  scope.py
  # ----- 新增 -----
  capture/
    snapshot.py          # TurnSnapshot 从 NlqState/record 组装
    extractors.py        # Caliber/Example/Entity/Process/Term
    triggers.py          # V-T* / 与 C-T* 钩子注册
    runner.py            # async enqueue capture job
  staging/
    service.py           # quarantine, merge, conflict
    models.py            # KnowledgeStagingRow
  assets/
    caliber.py           # business_caliber CRUD
    example.py           # 适配 data_training
    process.py           # process_episode
    term_adapter.py      # terminology
  promotion/
    rules.py             # Evidence Pack + 策略
    service.py           # evaluate / promote / demote / certify
  lineage/
    models.py            # KnowledgeLineageEvent
    service.py           # append_event（同事务）
    api.py               # 审查查询
  index/
    embed.py             # caliber/example embedding 任务
  retrieval/
    caliber_provider.py
    example_provider.py
    process_provider.py
    catalog_adapter.py   # 包装 get_table_schema 为 StructuralHints
  compile/
    bundle.py            # KnowledgeBundle v2
    policy.py            # 预算、优先级
    compile.py           # compile_knowledge_for_turn
  api/
    router.py            # staging/publish/certify/lineage

backend/alembic/versions/
  082_knowledge_conversation_plane.py   # 建议下一迁移号

# Catalog 加固（已有目录内改）
apps/datasource/profiling/worker.py|service.py|bootstrap.py
apps/datasource/crud/catalog_stats.py
```

---

## 2. 数据模型（表设计）

### 2.1 `knowledge_staging`

| 列 | 类型 | 说明 |
|----|------|------|
| id | bigint PK | |
| oid | bigint | workspace |
| kind | text | caliber\|example\|term\|entity\|process |
| status | text | draft\|pending\|conflict\|rejected\|promoted |
| natural_key | text | 去重键 |
| scope | jsonb | {ds_id, assistant_id?} |
| payload | jsonb | Candidate 全文 |
| trigger_id | text | V-T1… |
| source_record_id | bigint | |
| suggested_trust_tier | text | |
| quality_snapshot | jsonb | |
| conflict_with | bigint[] | |
| lineage_id | text | 预分配 |
| create_time / update_time | timestamptz | |

索引：`(oid, kind, status)`、`natural_key`、`source_record_id`。

### 2.2 `business_caliber`

| 列 | 类型 | 说明 |
|----|------|------|
| id | bigint PK | |
| lineage_id | text UNIQUE 语义根 | 同 lineage 多 version 用 id+version |
| version | int | |
| oid, datasource_id, advanced_application_id | | scope |
| label, summary | text | |
| contract_fragment | jsonb | QueryContract 子句子集 |
| field_targets | jsonb | [{resource, field, …}] |
| synonyms | jsonb | |
| trust_tier | text | published\|trusted\|certified\|… |
| certified | bool | |
| enabled | bool | |
| superseded_by | bigint | |
| provenance | jsonb | 头摘要 |
| embedding | vector | |
| natural_key | text | |
| create_by / certify_by | bigint | |
| create_time / update_time | | |

### 2.3 `process_episode`

压缩轨迹：`lineage_id, oid, ds_id, question_norm, episode jsonb, trust_tier, enabled, embedding, source_record_id, provenance`。  
**最高 published，禁止 certified/Bind。**

### 2.4 `knowledge_lineage_event`

| 列 | 类型 |
|----|------|
| event_id | text PK (ulid) |
| lineage_id | text | indexed |
| asset_kind, asset_id, asset_version | |
| at | timestamptz |
| actor | jsonb |
| action | text |
| from_tier, to_tier | text |
| trigger_id | text |
| refs | jsonb |
| evidence_snapshot | jsonb |
| decision | jsonb |
| payload | jsonb |

**仅 INSERT。** 唯一约束可选 `(lineage_id, event_id)`。

### 2.5 复用现表（适配，不复制）

| 资产 | 表 | 改造 |
|------|-----|------|
| Term | `terminology` | 可选加 `lineage_id`/`trust_tier`/`provenance` JSONB；或旁表 meta |
| Example | `data_training` | 同上；`question`+`description`(SQL)；加 `sql_skeleton`/`natural_key`/`trust_tier` 列或 JSON meta |
| Dict | `dictionary_*` | 已有 generation；entity 回写走现有 refresh/staging 字段扩展 `source=chat` |
| Relation | `field_relation` | 已有 CANDIDATE/CONFIRMED；chat 反写只写 CANDIDATE + source |

### 2.6 工作区策略（配置）

存 `settings` 或 workspace JSON（勿散落魔法数）：

```text
KnowledgePolicy {
  caliber_bind_requires: "certified"          # 默认
  caliber_auto_trusted: true                  # 复现→trusted，不 Bind
  example_auto_publish: false
  reproduce_count_n: 3
  promotion_window_days: 90
  allow_user_certify: false                   # 仅 admin 认证
  assess_constrain_uncertified_caliber: false
  applied_lineage_full: false                 # applied 事件采样
  compile_budgets: {
    assess: { constrain_cards: 3, card_chars: 120, exemplars: 0 },
    generate: { constrain_cards: 2, exemplars: 2, card_chars: 200 },
    repair: { exemplars: 1 }
  }
}
```

---

## 3. 核心流程实现规格

### 3.1 Capture（异步）

**钩子位置：** `nlq.py` 在 `accepted_candidate` 确定或 `complete` 终态后（澄清卡等待则不 capture 成功链）：

```text
enqueue_knowledge_capture(TurnSnapshot)
```

实现：`common.utils.embedding_threads` 同类线程池 **或** 轻量 DB 队列表 `knowledge_capture_job`（推荐队列表，可重启排水，与 profiling 一致）。

**TurnSnapshot 字段：** 见架构文档阶段 0；从 `llm_service.record`、`intent_context`、`active/accepted_candidate`、`outcome` 组装。

**Extractors（按 trigger）：**

| Trigger | 条件函数 | 产出 |
|---------|----------|------|
| V-T1 | clarification_parent + answers + success step | Caliber(user:answer), Entity, Process, Example? |
| V-T2 | ready + success + quality_ok | Example, Process |
| V-T3/4/5 | API 显式 | 对应 kind，explicit_save |
| V-T6/7 | refine/feedback | demote 请求 + 负样本 Process |
| V-T9 | contract None + success | Process only |
| V-T10 | degraded | 低信任 Example/Process |
| V-T12 | 批作业扫描 | relation CANDIDATE |

每个 candidate：`natural_key` 算法见架构文档；预分配 `lineage_id`；`append_event(captured)`。

### 3.2 Staging 检疫

```python
def admit(candidate) -> StagingRow:
    check_schema(field_targets)
    merge_or_conflict(natural_key)
    scrub_literals(payload)
    validate_scope()
    reject_unsafe_sql()  # example
    status = pending|conflict|rejected
    append_event(quarantine_*)
```

**默认不召回。**

### 3.3 Publish / Promote / Certify

```python
@transaction
def publish_from_staging(staging_id, actor):
    asset = insert_asset(...)
    append_event(published)
    enqueue_embed(asset)
    staging.status = promoted

@transaction
def certify_caliber(asset_id, actor, note):
    assert evaluate_promotion(...).allows_certify or actor.is_admin
    asset.trust_tier = certified
    append_event(certified, evidence_snapshot=freeze_pack(...))
    # 同事务，缺事件则 rollback
```

`evaluate_promotion`：实现架构 §9 Evidence Pack；返回 `PromotionDecision`。

**降格：** `demote` / `disable` / `schema_invalidate` 同样打事件，Compile 下轮立即。

### 3.4 Compile（NLQ 唯一知识闸）

```python
def compile_knowledge_for_turn(ctx: CompileContext, stage: Literal["assess","generate","repair"]) -> KnowledgeBundle:
    cands = []
    cands += catalog_adapter.structural(ctx)       # schema 侧可懒加载
    cands += dict_provider.recall(...)
    cands += term_provider.recall(...)
    cands += caliber_provider.recall(...)          # filter trust/scope
    cands += example_provider.recall(...)
    cands += process_provider.recall(...)          # 低预算
    # relation CANDIDATE 永不进入
    return decide(cands, ctx, stage, policy)
```

**decide 顺序：** 优先级链 → natural_key 去重 → 冲突 Clarify → Apply by tier → 预算截断 → `apply_log`。

**接入点（最小改动拓扑）：**

1. `assess_clarity_node` 前：`compile(..., assess)` → bound 合并 draft；clarify_hints 并入 questions。  
2. `generate_queries_node` 前：`compile(..., generate)` → plan_context / few-shot。  
3. 现有 `match_knowledge` / `match_training`：逐步改为 provider，避免双通道；过渡期 Compile 内调用，step 只打日志。

### 3.5 Lineage 审查 API

```text
GET  /api/v1/knowledge/assets/{kind}/{id}
GET  /api/v1/knowledge/lineage/{lineage_id}/events
GET  /api/v1/knowledge/assets/{kind}/{id}/usage      # 查 ChatLog/record
POST /api/v1/knowledge/staging/{id}/publish
POST /api/v1/knowledge/calibers/{id}/certify
POST /api/v1/knowledge/assets/{kind}/{id}/disable
POST /api/v1/chat/records/{id}/save-caliber|save-example   # V-T3/T4
```

权限：`require_permissions` + ws_admin（certify/disable）；save-* 可为会话用户。

前端：资产详情时间线；Chat 结果「保存为口径」；运营「待认证队列」。

### 3.6 Catalog 加固（并行迭代，同属知识可信度）

见 `catalog-mining-analysis-and-optimization.md` Iter-1：

1. Worker drain + boot reclaim  
2. StarRocks/Doris 内部 stats  
3. READY 门槛与 scan 成功语义对齐  

无这三项，Structural 输入不可信，Conversation 升格也难（E5/成本门禁）。

### 3.7 双平面焊接

| 事件 | 实现 |
|------|------|
| sync 字段删除/改名 | `invalidate_calibers_for_fields(ds, fields)` → disable + `schema_invalidated` 事件 |
| Entity 澄清选中 | staging kind=entity → merge dictionary_value（source=chat）或待 refresh |
| 稳定 join | 定时作业 V-T12 → `upsert_relation_candidate` source=chat |

---

## 4. 与现有代码的衔接清单

| 现有 | 动作 |
|------|------|
| `apps/knowledge/service.recall_knowledge` | 保留 Term/Dict；Compile 编排其上 |
| `apps/chat/steps/knowledge.py` | 改为取 Compile 子集或标记 deprecated |
| `apps/chat/steps/training.py` | Example provider 统一 |
| `apps/chat/graphs/nodes/nlq.py` | 钩子 compile + capture |
| `apps/chat/semantic_intent` / `clarification` | 消费 bound；去掉准备态 blocked（可并行） |
| `get_table_schema` | catalog_adapter 包装，不复制逻辑 |
| `field_relation` / `decide_field_relation` | 保持；chat 只写 CANDIDATE |
| `dictionary` | 扩展来源；不改「只读 published」 |
| `data_training` / `terminology` | meta 列或旁表 |
| `ChatLog` / `log_span` | payload.knowledge_apply |
| Config assistant | certify / lineage / publish tools |
| `mining_policy` (081) | Catalog 侧策略；与 KnowledgePolicy 分开但可在 DS 设置页邻近展示 |

---

## 5. 分阶段实现计划（PR 级）

### Phase A — 地基（约 3–5 天）

**目标：** Conversation 表 + lineage 基建（**Catalog P0 已完成，不再阻塞**）。

| 任务 | 交付 |
|------|------|
| A1 | Migration：staging、caliber、process_episode、lineage_event；training/term meta |
| A2 | `lineage.append_event` + 单测（不可变、缺事件事务失败） |
| A3 | ~~Catalog P0~~ → **已完成**；仅跟踪 P1（定时/采样/候选人审 UX）并行 |
| A4 | KnowledgePolicy 配置读取 |
| A5 | `compile_knowledge_for_turn` 骨架挂 nlq（可先透传现有 term+dict） |

**验收：** lineage 单测绿；nlq 走 compile 入口且行为与今日等价。

### Phase B — Conversation 主闭环（约 2 周）

| 任务 | 交付 |
|------|------|
| B1 | Capture TurnSnapshot + V-T1/V-T2 extractors + 异步 job |
| B2 | Staging quarantine |
| B3 | Publish caliber/example；certify API；审核队列 API |
| B4 | CaliberProvider + compile assess（Bind 仅 certified） |
| B5 | nlq 接入 compile(assess) + capture 钩子 |
| B6 | ChatLog knowledge_apply；资产详情 lineage UI（可先简易） |

**验收：** 澄清成功→pending→admin certify→下轮 Bind；admitted 零 Bind；lineage 可见 captured→certified。

### Phase C — 召回完整与防淹没（约 1–1.5 周）

| 任务 | 交付 |
|------|------|
| C1 | compile(generate) + Example provider；预算截断 |
| C2 | V-T3/T4 保存按钮 |
| C3 | demote/disable/漂移失效 |
| C4 | L-1 schema 指纹漂移 → disable caliber |
| C5 | 统一替换双通道 match_training/knowledge |

**验收：** 预算指标；保存快轨；字段改名后旧 Caliber 不可 Bind。

### Phase D — 增强（约 1–2 周）

| 任务 | 交付 |
|------|------|
| D1 | 复现→trusted 自动（仍不 Bind） |
| D2 | Process 弱召回；V-T9/T10 |
| D3 | L-3：成功 turn **触发**既有 `mine_query_log_joins`（不自研第二套） |
| D4 | L-2 Entity→dict staging |
| D5 | Config assistant 工具齐全；promotion 队列 UX |
| D6 | usage 反查；策略旋钮 |

### Phase E — Contract 协同（可与 B/C 并行）

去掉 intent `blocked` 停死、澄清只认业务槽位等（见前序架构讨论），避免知识 Bind 后又被准备态打死。

---

## 6. 测试矩阵

| 层级 | 用例 |
|------|------|
| Unit | natural_key；quarantine；promotion E1–E8；compile 去重/预算/certified-only Bind |
| Unit | lineage 缺事件 rollback；evidence_snapshot 必填 |
| Integration | V-T1→certify→下轮 assess bound |
| Integration | CANDIDATE 不进 get_table_schema |
| Integration | schema 失效 disable caliber |
| Integration | worker drain / Doris stats（Catalog） |
| API | certify 权限；lineage 列表排序 |
| 回归 | 现有 clarification / planning / dictionary 测试 |

---

## 7. 观测与运营

**指标：** staging_pending_count、certify_latency、bind_rate、compile_drop_rate、capture_job_backlog、caliber_disable_on_drift。

**ChatLog：** `knowledge_apply[]`。

**运营日清：** 待认证 Caliber 队列；冲突队列；Relation CANDIDATE 队列（已有）。

---

## 8. 风险与缓解

| 风险 | 缓解 |
|------|------|
| 自动沉淀脏数据 | Caliber 默认不 publish/不 Bind；升格要 E8 |
| 事件表膨胀 | applied 采样；recalled 聚合 |
| 与旧 recall 双通道 | Phase C 强制合并 Compile |
| 实现过重 | 严格按 Phase A→B；Process / L-3 join 触发放 D |
| 源 record 删除 | 快照在 event；外链 soft |

---

## 9. 里程碑定义「知识沉淀 MVP」

同时满足即 MVP：

1. V-T1 capture → staging → **人工 certify** → Caliber **Bind**。  
2. Lineage 从 captured 到 certified 可查，evidence_snapshot 非空。  
3. Compile 为 assess 知识唯一入口（至少 Caliber/Dict/Term）。  
4. Compile.Structural/Entity 只读 Catalog 发布态（不双写）。  
5. 红线测试：admitted/CANDIDATE 不 Bind/不进 schema。

---

## 10. 文档与画布索引

| 文档 | 内容 |
|------|------|
| `knowledge-catalog-linkage-revision.md` | **库侧现状 + 联动修订（开工必读）** |
| `knowledge-accumulation-architecture.md` | 分层、触发全表、升格、血缘、场景 |
| `catalog-mining-analysis-and-optimization.md` | 库侧历史分析（P0 已过时） |
| `knowledge-accumulation-implementation.md`（本文） | 表、API、模块、分期、测试 |

---

## 11. 建议立即开工顺序

```text
1) Phase A1–A2–A5：表 + lineage + compile 骨架
2) Phase B：Capture V-T1 → certify → Bind（产品可感知）
3) Phase C：预算、保存、L-1 漂移失效
4) Phase D：L-2/L-3、Process、运营台
5) Catalog P1 并行（不挡 Conversation）
```

**第一个可演示垂直切片：**  
「澄清签收额 → 运营认证 → 第二次问数 Bind → 打开资产看见完整 lineage」。
