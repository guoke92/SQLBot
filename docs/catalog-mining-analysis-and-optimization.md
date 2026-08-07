# 库侧知识挖掘：问题分析与优化方案

> 范围：Catalog Plane（schema sync、catalog stats、field profile、relation mining、dictionary）  
> 对照：业内语义层 / Wren memory / ThoughtSpot coaching / NL2SQL catalog enrichment 常见实践  
> 关联代码：`backend/apps/datasource/profiling/`、`dictionary/`、`crud/catalog_stats.py`、`crud/datasource.py#get_table_schema`、`graphs/current/metadata.yaml`  
> 日期：2026-08-07

---

## 1. 背景与目标

### 1.1 库侧挖掘在整体中的位置

SQLBot 的跨会话知识分为两平面：

| 平面 | 职责 | 本文件覆盖 |
|------|------|------------|
| **Catalog Plane** | 库里有什么、长什么样、怎么连、枚举值 | ✅ |
| **Conversation Plane** | 业务怎么算、用户怎么说、怎么查过 | 另文；本文仅写焊接点 |

库侧目标：为 NLQ 提供**可信、可发布、可失效**的结构与统计上下文，且**候选不得静默当真**。

### 1.2 当前流水线（现状）

```text
chooseTables / sync_catalog / sync_single
  → 写 core_table / core_field
  → 触发表/DS embedding
  → enqueue facts_only + schedule_worker_kick()
       → run_facts_bootstrap:
            refresh_table_stats
            profile_field（逐字段）
            extract_table_constraints → DDL FK → CONFIRMED
            publish_table_profile_generation
            re-embed
       → is_high_value_table? → enqueue semantic
            → metadata.yaml agent + mining tools
            → 仅写 field_relation CANDIDATE

dictionary（另路）:
  configure → refresh → published_generation 快照
  sync 时 reconcile → STALE（不自动重刷）
```

Chat 消费现状：

| 产物 | 是否进 NLQ |
|------|------------|
| 表/DS embedding | ✅ 选表 |
| profile null/ndv/minmax | ✅ schema 文案 / embedding 文本 |
| approx_rows | ✅ schema + 成本门禁（有值时） |
| CONFIRMED EQUI_JOIN/HIERARCHY | ✅ `【Confirmed relations】` |
| Relation CANDIDATE | ❌（正确） |
| profile top_values | ❌（未进 schema） |
| BINDING 等 kind | ❌ |
| dictionary published | ✅ entity_binding（需先配置并 refresh） |

### 1.3 总体评价

**值得保留的设计：**

1. Facts（确定性 worker）与 Semantic（agent 只写 CANDIDATE）分离。  
2. Profile / Dictionary **世代发布**；问数不打远程 DISTINCT。  
3. Chat **只消费 CONFIRMED + published**；X6 图不作 join 真相。  
4. Dictionary 刷新事务与截断拒发较严谨。

**核心短板：** 运维闭环不完整、SR/Doris 统计缺失、质量门槛偏松、挖到的信号消费不足、与对话平面未焊接。

---

## 2. 分层问题分析

### 2.1 架构与控制面

| ID | 问题 | 现状证据 | 影响 | 严重度 |
|----|------|----------|------|--------|
| A1 | Worker 无耐久排水 | `schedule_worker_kick` → `executor.submit(run_profiling_worker_once)`；`max_jobs=8` 单次有限；无 lifespan/cron drain | 重启后 PENDING/过期 RUNNING 悬挂；积压需反复人工/同步触发 | P0 |
| A2 | SCHEDULED / WATERMARK 空转 | `ScanTrigger` 枚举存在，无生产者 | 无 schema 变更时知识过期 | P1 |
| A3 | ProfileStatus.STALE 未真正驱动 | 模型有 STALE，缺统一写入与消费策略 | 指纹变化与展示/召回不一致 | P1 |
| A4 | Scan SUCCEEDED ≠ Profile READY | `worker` 在 bootstrap 后一律 `mark_run_succeeded` | 运维误判「挖矿成功」 | P0 |
| A5 | Semantic 也 bump pending_generation | `enqueue_table_scan` 统一 +1 | 世代语义混乱，误伤 facts 预期 | P1 |
| A6 | 双图漂移 | sync `reconcile_relation_graph` 不重投影 CONFIRMED→X6 | UI 与 `field_relation` 真相不一致 | P1 |
| A7 | 与 Conversation 无统一 Compile | schema/dict/term 各 step 注入 | 长期上下文膨胀、优先级不一致 | P1（整体架构） |

### 2.2 采集层（Mining）

| ID | 问题 | 现状证据 | 影响 | 严重度 |
|----|------|----------|------|--------|
| M1 | StarRocks/Doris catalog stats 跳过 | `catalog_stats.fetch_table_stats_keyed` 对 doris/starrocks 直接空结果 | `approx_rows` 空 → 高价值门禁弱 → semantic 少跑；成本门禁失效 | P0 |
| M2 | 采样偏置 | `profile_field` 以 LIMIT 前缀为主 | ndv/topk/null 系统偏差 | P1 |
| M3 | 宽表串行打点 | bootstrap 对每个 checked 字段远程 profile | 租约 600s 易超时；队列头阻塞 | P1 |
| M4 | 探针门槛松 / 来源坍塌 | name 相似度门槛偏松；upsert 多记为 PROBE | 候选噪声大、难审计 | P1 |
| M5 | Fanout/公式探针偏启发式 | 工具层估计非真 cardinality | 误导 agent 写候选 | P2 |
| M6 | 高价值门禁过度依赖行数 | `priority.is_high_value_table`：`approx_rows>=10000` 等 | SR/Doris 上几乎不触发 semantic | P0（随 M1） |
| M7 | top_values 挖了不用 | 快照有 top_values，`render_table_schema_text` 未用 | 枚举消歧全靠人手开 dictionary | P1 |
| M8 | BINDING/DERIVED 闲置 | kind 枚举存在，chat 不消费 | 挖掘投入无回报 | P2 |

### 2.3 检疫与发布层（Admission）

| ID | 问题 | 现状证据 | 影响 | 严重度 |
|----|------|----------|------|--------|
| P1a | Profile 部分成功即 READY | `publish_table_profile_generation`：`success_count > 0` 即 ok | 稀疏/有偏快照被当作权威 | P0 |
| P1b | Dictionary 更严、Profile 更松 | dict 截断拒发；profile 允许 advisory error | 质量标准不统一 | P1 |
| P1c | 候选人审队列弱 | agent 写 CANDIDATE；确认靠 API/config tool | 高置信候选沉没或长期不理 | P1 |
| P1d | Draft 注释不落库 | `allow_apply=False` 正确，但无待审存储 | 业务说明挖完即丢 | P2 |
| P1e | DDL 自动 CONFIRMED 与「agent 不确认」需文档钉死 | `upsert_ddl_foreign_keys` | 认知混乱，非功能 bug | P2 |

### 2.4 存储与运行时资源

| ID | 问题 | 影响 | 严重度 |
|----|------|------|--------|
| S1 | stats commit 与 bootstrap rollback 交织 | session 生命周期脆 | P1 |
| S2 | profiling 与 embedding 共用大线程池 | 背压互相拖死 | P1 |
| S3 | embedding 刷新失败仅 warning | schema 文本已变、向量未更新 | P2 |

### 2.5 Chat 消费层

| ID | 问题 | 影响 | 严重度 |
|----|------|------|--------|
| C1 | 结构信号消费不全 | top_values/BINDING 未进规划上下文 | 消歧/同义弱 |
| C2 | Dictionary 全手动 | 低 ndv 列不会自动建议配置 | 实体澄清覆盖不足 |
| C3 | 无 schema 漂移 → 对话资产失效 | 字段改名后旧 Caliber 仍可能被召回（Conversation 落地后尤甚） | P1（焊接） |
| C4 | CANDIDATE 未泄漏进 chat | — | **保持，勿改坏** |

### 2.6 可观测性

| ID | 问题 | 影响 | 严重度 |
|----|------|------|--------|
| O1 | 缺队列深度/租约年龄/字段耗时指标 | 生产排障靠日志 | P1 |
| O2 | 挖矿不进 ChatLog（可接受）但缺 ops 计数 | 无法算成功率、部分 READY 率 | P1 |

---

## 3. 与业内方案对照（简表）

| 能力 | 业内常见 | SQLBot 现状 | 结论 |
|------|----------|-------------|------|
| 候选/确认分离 | 强 | 强（CANDIDATE vs CONFIRMED） | 保持 |
| 发布快照进推理 | 强 | 强（profile/dict generation） | 保持 |
| 持续刷新 | 定时/水位 | 仅 sync 脉冲 | 补排水+水位 |
| 仓统计覆盖 | 主流仓 | SR/Doris 空 | 必补 |
| 采样质量 | 可声明 | LIMIT 前缀 | 升级 |
| 枚举进消歧 | 语义层/词典 | dict 手动；topk 闲置 | 克制消费 |
| 人审队列 | coaching 队列 | 工具零散 | 补运营 |
| 与业务口径一体 | 语义层 metrics | 对话平面未接 | 薄连接 |

---

## 4. 优化方案（按问题对应）

### 4.1 P0：稳定与可信（建议首迭代）

#### O-P0-1 Worker 耐久化与启动回收

**对应问题：** A1  

**方案：**

1. `main.py` lifespan（或独立轻量 cron）启动时：  
   - 将过期 `RUNNING` 回收为 `PENDING`；  
   - 循环调用 `run_profiling_worker_once` 直至返回 0 或达安全上限。  
2. 定时（如每 1–5 分钟）再 drain 一次（实现 `ScanTrigger.SCHEDULED` 的生产者可二期）。  
3. `run_profiling_worker_once` 支持 `until_idle=True` 内部循环，避免外部反复 kick。

**验收：** 杀进程留下 PENDING → 重启后自动消化；积压表可在无新 sync 时被扫完。

**主要改动：** `profiling/worker.py`、`profiling/service.py`、`main.py` lifespan。

---

#### O-P0-2 StarRocks/Doris 内部库 catalog stats

**对应问题：** M1、M6  

**方案：**

1. `fetch_table_stats_keyed`：  
   - **external catalog**：继续跳过（或单独策略）；  
   - **内部库**：查 `information_schema.tables`（及引擎可用的行数/大小字段）写入 `approx_rows` / `data_bytes`。  
2. 补单测：`tests/test_catalog_stats` 或扩展现有 starrocks 测试。  
3. 验证 `is_high_value_table` 与 `validate_plan` 成本门禁在 SR/Doris 上生效。

**验收：** 内部 SR 表 sync 后 `core_table.approx_rows` 非空；大表可触发 semantic follow-up。

**主要改动：** `crud/catalog_stats.py`、必要时 `starrocks_catalog.py` 辅助。

---

#### O-P0-3 Scan 结果与 READY 语义对齐

**对应问题：** A4、P1a  

**方案：**

1. `run_facts_bootstrap` 返回明确 `status`：`READY | PARTIAL | FAILED | UNSUPPORTED`。  
2. **仅** `READY` 时 `mark_run_succeeded`；`FAILED` → `mark_run_failed`；`PARTIAL` → 单独终态或 failed+可重试策略（产品二选一，推荐：不升 active generation，run 标 `PARTIAL`）。  
3. `publish_table_profile_generation`：  
   - `success_count / total_fields >= threshold`（建议默认 0.8，可配置）；  
   - 或「主键/时间/高优先级列必成功」；  
   - 否则**不**推进 `active_profile_generation`，保留上一代 READY。

**验收：** 故意让半数字段 profile 失败 → active generation 不变；run 不显示纯 SUCCEEDED 掩盖失败。

**主要改动：** `bootstrap.py`、`service.publish_table_profile_generation`、`worker.py`。

---

### 4.2 P1：好用与可运营

#### O-P1-1 采样与关键列策略

**对应问题：** M2、M3  

**方案：**

1. 方言能力探测：支持则 `TABLESAMPLE` / `ORDER BY rand()` / 分块；写入 `sample_method`。  
2. 宽表：优先 profile —— 有注释、字符串、疑似枚举（后续用短采样估 ndv）、主键/时间列；其余降频或跳过。  
3. 每 DS 并发上限（如 1–2 张表同时 profile），与 embedding 池隔离。

**验收：** 同表两次 profile 的 topk 不再严重贴主键前缀；宽表不再轻易租约超时。

---

#### O-P1-2 关系探针质量与来源

**对应问题：** M4、M5  

**方案：**

1. upsert 前：类型兼容（数值-数值、字符串-字符串等）过滤。  
2. 保留真实 `RelationSource`（NAME / OVERLAP / PROBE / LLM）。  
3. 工具内硬阈值：低于阈值不写库；hierarchy/fanout 写明证据字段。  
4. Admin/Config：「候选队列」按 confidence × 表热度排序，批量确认/拒绝。

**验收：** 候选可按来源筛选；明显类型不匹配不再入库。

---

#### O-P1-3 挖到的信号克制进 Chat

**对应问题：** M7、C1、C2  

**方案：**

1. `render_table_schema_text`：对 `approx_distinct` 低且有 `top_values` 的字段，附加最多 N 个值（长度预算，如每字段 5 值、总增 200–400 字）。  
2. CONFIRMED `BINDING`：以「同义/同实体字段」短行注入，**不**进 join 块。  
3. Profile 发现低 ndv 字符串列 → Config/API **建议** `configure dictionary`（不自动 refresh）。  
4. 全部走预算，禁止整列枚举倾倒。

**验收：** 未配 dictionary 时，低基数字段仍能辅助 LLM/澄清；prompt 增量可控。

---

#### O-P1-4 控制面修补

**对应问题：** A2、A3、A5、A6、S1、S2  

**方案：**

| 项 | 做法 |
|----|------|
| Generation | 仅 `facts_only` / `full` 的 facts 阶段 bump `pending_generation`；semantic/validate 复用当前 active |
| STALE | schema_fingerprint 变更时写 `ProfileStatus.STALE`；enqueue 去重仍要标脏 |
| 关系图 | sync 后调用与 `project_confirmed_relations_graph` 等价逻辑重投影 X6 |
| Session | stats 刷新纳入 bootstrap 显式阶段，避免「commit + rollback」交织 |
| 线程池 | `profiling_executor` 小池；embedding 池分离 |

---

#### O-P1-5 与 Conversation 平面薄连接

**对应问题：** C3、整体双平面  

**方案：**

1. **失效：** `sync_catalog` / 字段删除改名 → 扫描 `business_caliber` / example 的 `field_targets` → `disabled` 或 `pending_revalidate`（Conversation 表落地后）。  
2. **实体回写：** 澄清选中值 → `dictionary_value` staging（`source=chat`），仅已 configure 字段，走发布代。  
3. **关系反向：** 多次成功稳定 join → 只写 `CANDIDATE`（`source=chat`），永不直接 CONFIRMED。  
4. **Compile：** Structural（schema/relation/stats/dict）与 Caliber/Example 共用优先级文档；实现可分阶段接入 `knowledge.compile`。

**验收：** 字段改名后旧口径不再 Bind；用户选的实体值可进入下一字典世代。

---

#### O-P1-6 可观测性

**对应问题：** O1、O2  

**方案：**

轻量 metrics（日志结构化或内部计数即可）：

- queue_depth、oldest_pending_age  
- lease_expire_count、run_partial_rate  
- fields_profiled_per_min、semantic_enqueue_rate  
- stats_coverage_by_db_type（SR 非空率）

不新建第二套业务审计表；ChatLog 仅在 NLQ 侧记 `knowledge_apply`。

---

### 4.3 P2：逼近可运营轻量语义层

| ID | 方案 | 对应问题 |
|----|------|----------|
| O-P2-1 | Watermark：行数/校验变化触发 profile/dict 刷新 | A2 |
| O-P2-2 | Draft 表注释/候选说明落 `pending_review` | P1d |
| O-P2-3 | 真 cardinality SQL 改进 fanout | M5 |
| O-P2-4 | 错误 CONFIRMED 的使用率降权/告警 | 运营 |
| O-P2-5 | 完整接入 Knowledge Compile 预算闸 | A7 |
| O-P2-6 | BINDING/MAP 产品化语义与 UI | M8 |

---

## 5. 明确不做（防过度设计）

1. Semantic agent **自动 CONFIRMED** 非 DDL 关系。  
2. Profile / 注释 **自动写成 Caliber**（业务口径属 Conversation）。  
3. 问数请求内 **现场**跑 mining SQL / DISTINCT。  
4. 把 CANDIDATE 注入 `get_table_schema`。  
5. 为挖矿新建平行于 ChatLog 的完整「第二时间线」。  
6. 一期上完整 Ontology / LookML 替代现有 clause 模型。

---

## 6. 目标架构（优化后）

```text
                    ┌──────────────────────────────┐
                    │     Cognition Control Plane   │
                    │  enqueue · lease · drain ·    │
                    │  STALE · metrics · schedules  │
                    └──────────────┬───────────────┘
                                   │
     ┌─────────────────────────────┼─────────────────────────────┐
     ▼                             ▼                             ▼
 facts_only                   semantic                      dictionary
 (stats+profile+DDL)          (CANDIDATE only)              (publish gen)
     │                             │                             │
     └──────────── publish / confirm ────────────────────────────┘
                                   │
                    ┌──────────────▼───────────────┐
                    │     Published Catalog IO      │
                    │  schema text · CONFIRMED ·    │
                    │  dict snapshot · approx_rows  │
                    └──────────────┬───────────────┘
                                   │
                    ┌──────────────▼───────────────┐
                    │   Compile (Structural+)       │
                    │   + Conversation providers    │
                    └──────────────┬───────────────┘
                                   ▼
                               NLQ Graph
```

---

## 7. 实施计划与验收

### 7.1 迭代划分

| 迭代 | 交付 | 验收焦点 |
|------|------|----------|
| **Iter-1（P0）** | Worker drain+reclaim；SR/Doris stats；READY/SUCCEEDED 对齐；部分失败不升代 | 重启可消化队列；SR 有行数；失败不假成功 |
| **Iter-2（P1 质量+消费）** | 采样/关键列；关系来源与门槛；topk/BINDING 克制注入；dict 建议；池隔离；generation/STALE/重投影 | schema 更有用；候选更干净；图一致 |
| **Iter-3（P1 焊接+观测）** | 漂移失效；实体→dict；chat→relation 候选；metrics；Compile 接线（可先文档+最小实现） | 双平面不互相污染 |
| **Iter-4（P2）** | 水位刷新；审核队列；cardinality；运营降权 | 持续新鲜与可治理 |

### 7.2 跨切验收标准（总）

1. Chat 路径**零** CANDIDATE relation、**零**远程 dictionary DISTINCT。  
2. 内部 SR/Doris 表 stats 覆盖率达标（按环境定义，如 ≥95% 有 `approx_rows`）。  
3. Profile 部分失败**不**覆盖上一代 READY。  
4. 进程重启后积压任务可自动排空。  
5. Schema 注入增量受预算约束（可配置）。  
6. 字段破坏性变更后，依赖该字段的对话口径不可再 Bind（焊接后）。  

### 7.3 关键测试建议

| 测试 | 目的 |
|------|------|
| Worker lease reclaim + drain | A1 |
| Doris/SR stats 非 external | M1 |
| publish 低于阈值不升代 | P1a |
| `get_table_schema` 仅 CONFIRMED | C4 回归 |
| top_values 预算注入 | O-P1-3 |
| sync 后 X6 含新 CONFIRMED | A6 |
| fingerprint 变更 → STALE | A3 |

---

## 8. 关键文件索引

| 区域 | 路径 |
|------|------|
| Worker | `backend/apps/datasource/profiling/worker.py` |
| Bootstrap | `backend/apps/datasource/profiling/bootstrap.py` |
| Publish / enqueue | `backend/apps/datasource/profiling/service.py` |
| Priority | `backend/apps/datasource/profiling/priority.py` |
| Mining tools | `backend/apps/datasource/profiling/tools_impl.py` |
| Graph | `backend/graphs/current/metadata.yaml` |
| Stats | `backend/apps/datasource/crud/catalog_stats.py` |
| Chat schema | `backend/apps/datasource/crud/datasource.py` (`get_table_schema`) |
| Relations UI | `backend/apps/datasource/relation_service.py` |
| Dictionary | `backend/apps/dictionary/service.py` |
| Dict recall | `backend/apps/knowledge/dictionary_recall.py` |
| Protocol profile | `backend/apps/protocol/sql/protocol.py` |

---

## 9. 总结

| 维度 | 一句话 |
|------|--------|
| **现状** | 发布纪律与确认边界扎实，属于「有纪律的 catalog profiler」 |
| **主伤** | 流水线不耐久、SR/Doris 无统计、READY 门槛松、信号消费不足 |
| **主攻** | P0 排水+统计+发布诚实；P1 质量/克制消费/双平面焊接 |
| **红线** | 不自动确认非 DDL 关系；不把挖掘当业务口径；问数不现场采矿 |

按本文 **Iter-1 → Iter-2** 推进，即可在不推翻现有架构的前提下，显著提升库侧知识对 NLQ 的稳定贡献，并为 Conversation 平面留下干净接口。
