# Wiki 知识体系统一方案（v3 · Decision-Complete）

> 日期：2026-09-07 · 状态：**统一权威稿**（取代 v2 重写稿与完整方案 v1 的「产品化决策」角色）
>
> 输入：
> - Karpathy [LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) 方法论
> - 既有 `wiki知识体系统一方案-v2.md` / `wiki知识体系完整方案-v1.md` / 页面契约 spec-v0
> - 第三方全链路 Review（缺陷排查 + 双轴状态机 + 证据链 + UI 全景）
> - **前提：存量 unit / semantic 旧知识体系已清除**；运行面唯一知识后端 = Wiki
>
> 契约权威不变：`docs/wiki页面契约-spec-v0.md`。召回/摄取接口规范继续有效。

---

## 0. 一句话定位

**把问数知识建成 Karpathy 意义上的「可复利 wiki」：原始证据不可变，页面是编译产物并持续维护；再加 ChatBI 合金——散文给人审、ground 锚点给规划器与门禁验。**

| Karpathy 层 | 问数落地 |
|---|---|
| Raw sources（不可变） | DB catalog/profile、repo 文本、需求文档、人工录入、对话观察 → `wiki_source_artifact` |
| The wiki（LLM 维护的持久合成物） | `wiki_page` + revision；运行时只读 published |
| The schema（纪律） | 页面契约 v0 + 摄取/合并/lint/发布门禁（程序盖章，模型只管内容） |

与纯个人 wiki 的关键差异：**消费者是 SQL 规划器 + 确定性门禁**，不是「读页综合的人」。因此一切偏离 Karpathy 的设计，必须能用一条问数失败模式解释。

---

## 1. 六条不可妥协原则（继承并收紧）

| # | 原则 | 说明 |
|---|---|---|
| P1 | **零信任解析** | ground/frontmatter 语法失败 → 丢块+警告，绝不猜测 |
| P2 | **确定性打底，LLM 只做语义跃迁** | AST/catalog/profile/callgraph 本地完成；LLM 只收预算切片后的证据包 |
| P3 | **权威序按知识问题分源**（见 §2） | 废除「全局单调优先级」导致的语义反转；冲突进 REVIEW，禁止静默覆盖 |
| P4 | **一物理实体一页** | 一表一页、一 dictKey 一页；slug=物理名；其余页只引用物理键 |
| P5 | **程序管结构，LLM 管内容** | page_key/sources/contract_version/status 盖章与门禁 |
| P6 | **召回失败零影响主链路** | wiki 任一失败 = 少一段文本；正确性由 plan_gate / 硬校验兜底 |

**新增（v3 相对 v2）**：

| # | 原则 | 说明 |
|---|---|---|
| P7 | **编译一次、查询复利** | 摄取时完成交叉引用、矛盾标注、合成；问答不从 raw 重推全书 |
| P8 | **好答案回填** | 澄清结论 / 成功范式 / 人工确认可经同一 ingest→REVIEW→publish 管道入库 |
| P9 | **运行可见性 ≠ 内容治理** | Content Status 与 Operational Visibility 解耦（§3） |
| P10 | **AccessScope 前置硬隔离** | 图扩展与召回只在授权子图上跑；拒绝话术脱敏，物理名只进审计 span |

---

## 2. 权威域划分（按知识问题，不按「源优先级总分」）

第三方 Review 的核心修正予以采纳：**按问题选唯一权威**，参照源只佐证/补语义。

| 知识问题 | 唯一权威 | 参照 | 冲突处理 |
|---|---|---|---|
| 物理 Schema / 类型 / 可空 / 索引 | **DB Catalog** | Entity/Mapper | 不一致 → `FIELD_NOT_IN_DB`，以 DB 为准 |
| 值域 / TopK / 分布 | **DB Profile** | 代码常量 | DB 高频但代码无 → `ENUM_VALUE_NOT_IN_DB` REVIEW |
| 枚举 Label / 状态名 / 编码映射 | **代码枚举/常量/转换器** | Profile、文档 | **禁止 LLM 脑补 Label**；无代码时 enum 页可只有 values |
| Join Path | **Mapper/SQL/Service 实际查询 + CONFIRMED field_relation** | DDL FK | 候选进 relation 底稿；确认后投影 |
| 事务强绑定 / 共写字段 | **Service 事务逻辑** | 文档 | 生成 process/rule，须带 code_path |
| 状态机 From/Event/To | **状态转换方法/校验器** | 需求演进史 | 文档只进散文「版本演进」 |
| 默认投影 / 常用 Filter | **Controller/API/VO/Mapper** | 历史问答 | pattern/query 页 |
| 术语 / 同义词 / 业务口径 | **注释+文档+手动 Wiki** | 对话澄清 | **必须**绑 `表.字段` 或 `表.字段=值` 才可进物理规划 |
| 跨模块全景 | **架构 README/设计文档** | 目录结构 | 仅导航；不得当物理真值 |

> 与旧 D7「库 > 代码 > 文档」兼容：库赢「存在性与实测」；代码赢「含义与流转」；文档赢「意图与时间线」。

---

## 3. 双轴状态机

### 3.1 Content Status（持久化）

```
draft → review → published → stale → review
                 published → retired
```

- 发布门禁：`lint` 零 Error + 引用闭包可解析
- `stale`：关联 DDL/代码/文档指纹漂移（异步标记）
- `retired`：物理实体删除或业务废弃

### 3.2 Operational Visibility（**请求时求值**，不冗余落库）

| 求值结果 | 条件 | 运行行为 |
|---|---|---|
| `available` | published ∧ 依赖资源可用 ∧ 用户有权 ∧ 页面未禁用 | 可召回 / 可渲染 |
| `resource_unavailable` | 表/字段 unchecked 或关系非 CONFIRMED 等 | 业务提示「模块维护中」；**不**吐物理名 |
| `permission_denied` | AccessScope 排除 | 若问题命中该页别名 → **ACCESS_DENIED 终态**（脱敏话术） |
| `page_disabled` | 管理员手动禁用（唯一需要持久的运维开关） | 同 unavailable |

**唯一例外持久字段**：`page_disabled`（及 Content Status）。其余可见性一律由 `AccessScope` + 资源 checked 状态在请求路径投影。

### 3.3 双速生命周期（DDL / 启停）

| 层 | 延迟 | 动作 |
|---|---|---|
| 即时 | 毫秒 | AccessScope / checked 变更 → 页面立刻不可见或不可规划 |
| 异步 | 秒～分钟 | `wiki_resource_lifecycle_event` → Stale / Lint / Review 项 |

禁止在 catalog 同步事务内级联重写几十个 wiki 页。

---

## 4. Karpathy 三操作 × 问数全链路

### 4.1 Ingest（编译进 wiki）

```
Raw → Substrate(E0–E3) → Step1 结构化语义 → Step2 FILE/REVIEW
    → 零信任解析 → 同层同实体确定性合并 → Lint → Page/Revision
```

- **L0 DB-only**：零 LLM，`baseline` 确定性生成 table/enum（及 FK→relation 段）
- **L1 +代码**：调用图切片 + 两步 LLM 语义页
- **L2 +文档/手动/对话**：同一门禁；作者身份不改变验证强度

提取面细节沿用 v2 §2.0（E0–E3 + Step A–F）；产品化时底稿进受管 substrate，**不进召回目录**。

### 4.2 Query（对 wiki 问，不对照 raw 重推）

运行时接线（现状已基本具备，v3 固化）：

| 点 | 行为 |
|---|---|
| `retrieve_context` | business recall → `<business_knowledge>` |
| 锚点闭包 | 命中页物理键 → 并入 schema 渲染清单（确定性，不占图配额） |
| `WikiSchemaRenderer` | table 权威 + enum label 内联 + relation 一行式 JOIN |
| plan_gate | missing_concepts → `recall(mode=physical)` 反弹 |
| 权限 | AccessScope 前置裁剪 store/邻接图；命中拒权别名 → 脱敏 ACCESS_DENIED |

**召回公式**对齐 llm-wiki `search.rs`（RRF + 页聚合 + 图配额）；向量故障降级纯词法。

### 4.3 Lint（健康巡检）

| 类 | 例子 |
|---|---|
| 结构 | slug、ground schema、broken-link、coverage gap |
| 对账 | FIELD_NOT_IN_DB、ENUM_VALUE_NOT_IN_DB、TYPE_FAMILY |
| 语义 | contradiction、orphan、duplicate、stale |
| 导航（Karpathy index 思想） | `_index` / 管理面目录：一页一行摘要，按 type 分面 |

### 4.4 特殊页：Index 与 Log

| Karpathy | 产品化 |
|---|---|
| `index.md` | `wiki_page` 目录视图 + 覆盖率仪表（表/枚举/关系覆盖）；运行时知识地图同源 |
| `log.md` | append-only：`wiki_build_job` / ingest span / REVIEW 裁决记录（可 `grep` 时间线） |

---

## 5. 合并、去重与旧模块边界

### 5.1 确定性合并边界（防实体污染）

**仅当**同时满足才程序化并集：

1. 同 `page_key`
2. 同 ground 块类型
3. 同实体键（表名 / dictKey / relation 端点对）

字段存在性以 Catalog 为准；枚举 Label 以代码为准。其余跨域冲突 → `wiki_page_review_item`。

### 5.2 与 terminology / data_training（单向收敛）

- **管理模块保留**，不做双向同步（防死循环）。
- 新知识统一走「新增 Wiki」。
- Prompt 组装层：按实体别名物理去重；**Published Wiki ≻ 裸术语/裸示例**。
- 不把 terminology 行「升级」成 wiki 的自动写回；需要时人工/批处理导入一次。

### 5.3 旧 unit 体系

**已清除**。配置面：

- `KNOWLEDGE_BACKEND` 固定语义为 wiki（可保留开关作紧急空跑，但无 unit 回退实现）
- `KNOWLEDGE_RECALL_STRATEGY`（unit/node）标记废弃，读路径忽略
- 文档/代码中 unit 双轨分支删除干净后关闭开关

---

## 6. 存储与缓存（产品化最小完备集）

### 6.1 核心表（阶段 1 必建）

| 表 | 职责 |
|---|---|
| `wiki_page` | 当前页权威（content status、page_disabled、corpus 归属） |
| `wiki_page_revision` | 不可变历史（回滚=新 revision，不改历史） |
| `wiki_page_anchor` | 物理锚点投影（表/字段/值），供闭包与权限裁剪 |
| `wiki_page_link` | wikilink 物化边 |
| `wiki_source_artifact` | 原始证据指针（hash/locator/excerpt） |
| `wiki_page_source` | 页↔证据（primary/support/context） |
| `wiki_page_review_item` | REVIEW 队列 |
| `wiki_corpus_generation` | **每 DS（或 oid+db）单调版本戳** |
| `wiki_build_job` / `wiki_embedding_job` | 任务与嵌入 |

阶段 4+ 再加：`wiki_candidate` / `wiki_candidate_observation`、`wiki_repo_connection`、`wiki_resource_lifecycle_event`。

### 6.2 缓存失效（修 Split-brain）

- 任何 publish / retire / disable / 锚点变更 → `corpus_generation += 1`
- 权限矩阵变更 → `permission_generation += 1`（可挂 workspace/user 指纹，或与 AccessScope fingerprint 对齐）
- 进程 LRU/`InMemoryWikiStore` **只认 generation**，废弃「纯 mtime 多进程共识」
- 文件目录语料保留为 **导出/冷启动/git-ops 备份面**；运行权威在 DB

### 6.3 权限与图扩展（修越权）

```
load published pages
  → filter by AccessScope(anchors ∩ allowed tables/fields)
  → build adjacency on remaining nodes only
  → RRF + graph expansion
```

拒绝侧信道：用户可见话术不含物理表字段名；内部 span 可记。

---

## 7. 关系通道与锚点闭包（已决议）

| 议题 | 决议 |
|---|---|
| relation 落点 | **先 table 页内 `ground:relation` 段**（渲染简单、闭包天然）；独立 relation 页后置 |
| 生成 | `field_relation=CONFIRMED` ∪ Mapper JOIN 底稿确定性投影；DB-only 用 FK |
| 渲染 | `WikiSchemaRenderer` 一行式 `a.col ← b.col` |
| 闭包 | business 召回后确定性抽物理键 → schema 清单；缺表页 → `SCHEMA_PAGE_MISSING` 遥测 |
| 门禁 | ready plan 引用表 ⊆ 闭包集合；缺则 advisory（不替代硬门禁） |

---

## 8. 对话复利（Dialogue Compounding）

对齐 Karpathy「good answers compound」，问数化落地：

| 信号 | 候选产物 | 路径 |
|---|---|---|
| 澄清选择落定 | concept / caliber 草稿 | observation → 频次聚类 → REVIEW → publish |
| 成功 SQL（人工收藏或高置信） | pattern / query 页 | 同管道；须过 lint |
| 负反馈 | 缺口 / contradiction REVIEW | 不自动改 published |

脱敏：只留谓词与枚举映射，抹明细行（姓名/证件/手机等）。

**最小闭环优先**：澄清结论 → concept 草稿（一条线），再扩 pattern。

---

## 9. 管理面（刻意瘦身）

第三方 UI 六大中心方向正确，但 **契约未冻前不做重 UI**。v3 产品切面：

| 优先级 | 面 | MVP |
|---|---|---|
| P0 | 页面库 | 列表分面（type/status）+ 详情（Markdown+ground 高亮）+ revision |
| P0 | 新增 Wiki | 文本/术语/示例 SQL → analyze → 同门禁提交 |
| P1 | Review 工作台 | 冲突/漂移/对话沉淀队列 + 白名单裁决动作 |
| P1 | 源连接 | DB 基线状态；Repo 连接（只读文本）；文档导入 |
| P2 | Overview | 覆盖率 / lint / stale / 命中与拒权遥测 |
| P2 | Job 控制台 | build/embed/lifecycle 日志 |

废除旧知识包 Workbench；前端空间收敛到 `frontend/src/views/knowledge/`（Wiki）。

---

## 10. 缺陷审计结论（第三方 7 项 → 采纳状态）

| # | 缺陷 | v3 处置 |
|---|---|---|
| 1 | 多进程 mtime 裂脑 | **采纳**：corpus/permission generation |
| 2 | 图扩展越权 | **采纳**：AccessScope 前置子图 |
| 3 | 拒权侧信道 | **采纳**：脱敏终态 + span 内详 |
| 4 | 粗暴全局合并污染 | **采纳**：§5.1 三元组边界 |
| 5 | 术语双向同步死循环 | **采纳**：单向收敛 |
| 6 | 代码探索 Token 爆炸 | **已有**：E0–E3 + ring≤2 + 预算；固化为硬约束 |
| 7 | DDL 级联阻塞 | **采纳**：双速解耦 |

---

## 11. 明确不做

- 多模态 / Deep Research / 查询时 LLM 自由翻页
- Obsidian 运行时依赖
- 与 terminology 双向写同步
- 重建 unit/semantic 双轨
- 第一期做完整「六大中心」重型前端
- 在 catalog 同步事务内同步重写全量 wiki

---

## 12. 分阶段落地（旧体系已清场后的重排）

### 阶段 0 — 收口（进行中/可立刻完成）

- 清除残留 unit 开关语义与死代码路径；`KNOWLEDGE_BACKEND=wiki` 为唯一实现
- 文档指向本 v3；v1/v2 标记为历史
- 确认 `terminology`/`data_training` 只读并存 + Prompt 去重钩子预留

### 阶段 1 — DB 权威存储 + L0 Baseline 产品化

- Alembic：§6.1 核心表 + corpus_generation
- profiling/metadata_scan 完成后确定性生成/更新 table+enum（+ FK relation 段）
- `InMemoryWikiStore` DB loader + generation 失效
- 去硬编码（ds_id/路径）
- **验收**：无代码仓也可对任意 DS 出 published 基线页；多 worker 缓存一致

### 阶段 2 — 运行时正确性收口

- AccessScope 裁剪召回/图（接现有 `apps.datasource.access`）
- 锚点闭包 + WikiSchemaRenderer relation 行（补齐能力回退）
- 值域对账 `ENUM_VALUE_NOT_IN_DB` 推广到 caliber/rule 字面量
- physical recall 与 ACCESS_DENIED 脱敏终态
- **验收**：多表 JOIN 不再纯靠猜；无权别名不泄漏物理名

### 阶段 3 — 统一手动入口 + Review MVP

- `POST /wiki/pages/analyze` + `POST /wiki/pages`
- 页面库 + 新增向导 + Review 队列 API
- **验收**：人写知识与 LLM 产物过同一 lint

### 阶段 4 — 代码仓摄取产品化

- `wiki_repo_connection` + 只读 workspace
- 静态分析套件任务化；Step1/2 租约 worker
- 同层合并 + 自动 REVIEW
- **验收**：L1 档位可开关；成本预算可观测

### 阶段 5 — 对话复利 + 遥测仪表

- observation → candidate → Review
- Overview 覆盖率/命中/拒权
- **验收**：真实澄清结论转正 ≥ N 例；金标回归不回退

---

## 13. 与既有文档关系

| 文档 | 关系 |
|---|---|
| `wiki页面契约-spec-v0.md` | **继续权威** |
| `wiki召回接口-v1.md` / `wiki源码摄取适配器-v1.md` | 接口规范继续有效；开关描述以本 v3 为准 |
| `wiki知识体系统一方案-v2.md` | 提取面 E0–E3 与评测结论仍有效；**产品化决策以本 v3 为准** |
| `wiki知识体系完整方案-v1.md` | 三层一闭环思想保留；阶段表被 §12 取代 |
| `知识体系目标架构-v3.1.md` | 历史 ADR；D1/D5/D7/D8 已映射进契约，不再作为运行实现依据 |

---

## 14. 成功标准（可测）

1. **复利**：同一业务问题第二次规划不再依赖 raw 重推断；命中 published 页与锚点闭包
2. **正确性**：枚举 Label 零脑补；DB/代码冲突 100% 进 REVIEW 而非静默
3. **安全**：无权用户无法经 wikilink/召回看到越权页；拒权无物理名泄漏
4. **可用**：wiki 存储/嵌入故障时问数主链路仍可跑（降级为无知识段）
5. **运维**：DDL 删除表后即时不可规划，异步 stale，主同步不阻塞
6. **生长**：澄清结论可转正为 concept；人工 Wiki 与摄取页同门禁
