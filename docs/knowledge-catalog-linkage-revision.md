# 知识积累落地校准：库侧现状 × Conversation 联动

> **权威序：** 落地计划（含 §11 锁定裁决）> 本文 > `knowledge-accumulation-implementation.md` > `knowledge-accumulation-architecture.md`。  
> 前提：Catalog / metadata mining **已基本落地**（见当前 `apps/datasource/profiling/`）。  
> 本文校准此前方案，明确 **Conversation 知识沉淀** 与库侧的职责边界与联动接口，作为开工依据。  
> 日期：2026-08-07  
> 配套：`knowledge-accumulation-architecture.md` · `knowledge-accumulation-implementation.md` · `catalog-mining-analysis-and-optimization.md`（P0 表已过时）

---

## 1. 库侧挖掘：当前实现摘要（熟悉用）

### 1.1 流水线

```text
sync_catalog / sync_single / chooseTables
  → core_table/field
  → dictionary reconcile（指纹漂移 → STALE）
  → relation_graph reconcile（布局修剪）
  → RANK embedding（仅结构文本，见 schema_text.RANK）
  → enqueue facts_only + worker kick

Worker（startup drain + kick）：
  claim_next_run (SKIP LOCKED + lease)
  → run_facts_bootstrap（受 mining_policy 门控）
       catalog_stats（含内部 Doris/StarRocks information_schema）
       DDL FK → field_relation CONFIRMED (source=ddl)
       profile_field → FieldProfileSnapshot
       publish generation（成功率门槛，默认 ≥50%）
  → 高价值 ∧ policy.has_agent_work → SEMANTIC
       metadata.yaml ReAct
       → 仅 CANDIDATE（含探针、mine_query_log_joins）
  → 终态 SUCCEEDED | PARTIAL | FAILED（诚实）

Chat 消费：
  RANK embedding → 选表
  PROMPT schema = render(PROMPT) + 【Confirmed relations】
  dictionary READY+published → entity_binding
  CANDIDATE / 未发布 dict / STALE stats → 不进 NLQ 强制路径
```

### 1.2 关键模块

| 模块 | 路径 | 职责 |
|------|------|------|
| Facts | `profiling/bootstrap.py` | 确定性统计/画像/DDL |
| Worker | `profiling/worker.py` | drain、PARTIAL、semantic 跟随 |
| Policy | `profiling/policy.py` + `capability_catalog.py` | lite/standard/deep/custom |
| Schema 双用途 | `datasource/schema_text.py` | RANK vs PROMPT 分离 |
| Stats | `crud/catalog_stats.py` | 内部 SR/Doris 已支持；external catalog 仍 skip |
| 关系真相 | `field_relation` + `relation_service.py` | CONFIRMED 进 chat；X6 仅布局 |
| 历史 SQL 挖 join | `profiling/query_log_joins.py` | ChatRecord SQL → CANDIDATE（**已实现部分「对话→Catalog」**） |
| Soft signals | `profiling/soft_signals.py` | brief/agent，非业务口径 |
| Dict | `dictionary/*` + `knowledge/dictionary_recall.py` | 仅 published；无 chat source 回写 |
| Knowledge 今日 | `knowledge/service.py` | **仅** Term + Dict recall，无 Compile/Caliber |

### 1.3 相对旧文档的校正

| 旧 P0 缺口 | 现状 |
|------------|------|
| Worker 无排水 | ✅ `run_profiling_worker_drain` + lifespan kick |
| SR/Doris stats 空 | ✅ 内部库走 mysql 系 information_schema |
| 假 SUCCEEDED / 任意成功即 READY | ✅ PARTIAL + 成功率门槛 |
| top_values 不用 | ✅ PROMPT 低 ndv 注入 topk |
| semantic 乱 bump generation | ✅ 仅 facts/full 分配 pending_generation |
| Conversation 平面 | ❌ **仍未开工**（设计文档 only） |

**仍可后续优化（不挡 Conversation 开工）：** 定时 SCHEDULED、采样质量、宽表限流、候选人审队列 UX、BINDING 进 prompt、dict chat 回写、sync 后强制 reproject 等。

---

## 2. 双平面职责（冻结，按现状重申）

| | **Catalog Plane（已完成主体）** | **Conversation Plane（本次落地）** |
|--|--------------------------------|-------------------------------------|
| 问题 | 有什么、长什么样、怎么连、枚举值 | 业务怎么算、用户怎么说、怎么查过 |
| 写入方 | sync / profiling worker / dict refresh / 人审关系 | turn capture / 用户保存 / 认证 |
| 正式资产 | schema、profile、stats、CONFIRMED relation、dict | Caliber、Example、Term 增强、Process |
| 候选 | relation CANDIDATE、dict 未发布代 | knowledge_staging |
| 默认进 NLQ | PROMPT 结构 + CONFIRMED + published dict | **仅 certified Caliber Bind**；Example Exemplify |
| 禁止 | 写 Caliber；CANDIDATE 进 schema | 写 CONFIRMED（非经人审）；污染 RANK embedding |

**已有交叉：`mine_query_log_joins` 属于 Catalog 能力**，从历史成功 SQL 产 CANDIDATE。Conversation **不要再实现第二套 join 矿**；成功 turn 最多 **触发/加速** 该能力，或把 V-T12 定义为「调用 Catalog 既有入口」。

---

## 3. 联动设计（修订版）

### 3.1 读路径联动（Compile 组装）

```text
compile_knowledge_for_turn(stage):
  structural ← 适配 get_table_schema / render_table_schema_text(PROMPT)
               + get_published_relations(CONFIRMED)
               （不复制 mining，只消费发布态）
  entity     ← DictionaryProvider（现有 recall_dictionary）
  term       ← TerminologyProvider（现有）
  caliber    ← CaliberProvider（新建，trust 过滤）
  example    ← ExampleProvider（data_training + 新 meta）
  process    ← ProcessProvider（弱，后置）

  # 永不召回：relation CANDIDATE、staging、未 certify 的 Bind
```

**要点：** Catalog 继续用现有 PROMPT 通道；Conversation 不把 profile 再塞一份进口径卡片，避免双份爆炸。Compile 统一 **优先级 + 预算 + apply_log**。

### 3.2 写路径联动（薄连接）

| ID | 方向 | 机制 | 实现归属 |
|----|------|------|----------|
| **L-1** | Catalog → Conversation | schema 指纹/字段删除 → **disable Caliber/Example** + lineage `schema_invalidated` | Conversation 监听 sync / reconcile 钩子 |
| **L-2** | Conversation → Catalog | 澄清实体选中 → dict **staging/增量**（source=chat）→ 仍须 published 才进 NLQ | dictionary 扩展 + Capture Entity |
| **L-3** | Conversation → Catalog | 成功 SQL → **复用** `mine_query_log_joins`（或 enqueue 带 query_log_joins 的 semantic/lite 任务） | **不新建** join 抽取器 |
| **L-4** | Catalog → Conversation | profile 低 ndv / soft_signals → **建议** configure dictionary 或澄清优先字段（可选） | 运营/assess 提示，不自动 Caliber |
| **L-5** | Catalog → Conversation | CONFIRMED join 存在 → 澄清少问「怎么连」，多问 population | clarification prompt / Compile 提示 |
| **L-6** | 共用治理心智 | CANDIDATE/admitted → 人审 → CONFIRMED/certified | 运营台并列：关系队列 + 口径队列 |
| **L-7** | 共用审计 | Catalog scan_run_id / Conversation lineage_id；NLQ `knowledge_apply` | ChatLog + lineage 事件 |

### 3.3 明确不再重复建设

| 旧方案表述 | 修订 |
|------------|------|
| V-T12 自研稳定 join 沉淀 | **改为** 触发或依赖 `query_log_joins`；人审仍走 `decide_field_relation` |
| Conversation 自建 Structural 存储 | **禁止**；只读 Catalog 发布态 |
| Profile 自动变 Caliber | **禁止** |
| Capture 与 profiling 共用一张 staging 表 | **概念同构、表分离**（metadata_scan_run / field_relation vs knowledge_staging） |
| Phase A「Catalog P0」作为 Conversation 阻塞 | **解除阻塞**；Catalog 收尾项并行即可 |

### 3.4 策略层邻近、配置分离

- `mining_policy`（DS/表，081）：管 facts/agent 能力。  
- `KnowledgePolicy`（workspace/设置）：管 caliber_bind_requires、example_auto_publish、预算等。  
设置页可并列展示，**不要**塞进同一个 JSON 以免耦合。

---

## 4. Conversation 落地范围（在库侧已完成后）

### 4.1 MVP（垂直切片，优先）

```text
1. Migration: knowledge_staging + business_caliber + knowledge_event
   （example 先复用 data_training + meta JSONB；process 可二期）
2. lineage.append_event（同事务）
3. Capture V-T1（澄清成功）→ staging
4. certify API + 简单队列
5. CaliberProvider + compile(assess)：仅 certified Bind
6. nlq：assess 前 compile；成功后 async capture
7. ChatLog knowledge_apply
8. 资产详情：lineage 时间线（可先 API）
9. L-1 最小：sync 字段变更时 disable 命中 field_targets 的 caliber
```

**演示：** 澄清签收额 → 认证 → 第二次 Bind → 打开 lineage。

### 4.2 紧随（仍属知识积累主路径）

- V-T3 保存为口径；V-T2 Example staging  
- compile(generate) + Example Exemplify + 预算  
- L-2 Entity→dict（需 dictionary 小扩展）  
- demote / thumbs（若有反馈入口）  
- 复现 → trusted（仍不 Bind）

### 4.3 后置

- Process episode  
- L-3 成功 turn 触发 `mine_query_log_joins`  
- L-4 soft_signals 建议配字典  
- 完整运营台 UX、usage 反查聚合  

### 4.4 Catalog 并行收尾（非阻塞）

定时 drain、候选人审 UX、采样改进、BINDING 提示、sync reproject —— 按库侧优化文档 P1/P2 排期，**不挡** MVP。

---

## 5. NLQ 挂接顺序（实现时）

```text
现有:
  recall_knowledge (term+dict) → … → retrieve_schema → assess → generate

目标:
  compile(assess) 内含 term+dict+caliber(+structural 引用)
    → assess（消费 bound / clarify_hints）
    → retrieve_schema（保持 Catalog PROMPT，或由 compile.structural 驱动同一函数）
    → compile(generate) → generate
    → accept → enqueue capture
```

过渡期：`match_knowledge` / `match_training` 可暂留，但 **Bind 只来自 compile**；最终合并避免双通道。

---

## 6. 红线（联动版）

1. Chat 不消费 CANDIDATE / 未发布 dict / admitted Caliber（Bind）。  
2. RANK embedding 不被 Conversation / profile 污染（已由 schema_text 保证，勿破坏）。  
3. Catalog 不写 Caliber；Conversation 不写 CONFIRMED（经 `decide_field_relation` 除外）。  
4. Join 挖掘以 `query_log_joins` 为准，禁止第二套解析器。  
5. 升格必写 lineage + evidence_snapshot；降格/漂移即时生效。  
6. 用户当轮 > certified > Catalog 结构。

---

## 7. 开工建议

**立即开始 Conversation MVP（§4.1）**，与 Catalog 小优化并行。  

**第一个 PR 建议：**  
`082/083` migration（staging+caliber+lineage）+ `lineage` 服务单测 + 空 compile 骨架挂 nlq（先 no-op Bundle），再迭代 capture/certify。

**不需要**再实现一遍库侧 P0；实现文档 Phase A 中 Catalog 条目改为「已完成，仅跟踪剩余 P1」。
