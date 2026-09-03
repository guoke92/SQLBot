# Wiki 知识体系完整方案 v1

> 状态：讨论共识稿（2026-09-01 固化）。本文整合多轮讨论的完整方案：
> 产品化接入（DB/git/文档三来源）、证据基座层（预提取中间数据）、
> 锚定与下钻原则、正确性缺口修复清单。
> 现状代码处于原型期（CLI 提取 + 进程内召回 + git 目录存储），
> 本方案是目标态；落地次序见 §8。
>
> 相关文档：页面契约 `docs/wiki页面契约-spec-v0.md`、召回接口
> `docs/wiki-knowledge/wiki召回接口-v1.md`、旧体系 ADR
> `docs/知识体系目标架构-v3.1.md`（unit 包，与 wiki 并行靠
> `KNOWLEDGE_BACKEND` 切换）。

---

## 1. 总体架构：三层一闭环

```
┌─────────────────────────────────────────────────────────────┐
│ 来源层（受管连接，可独立存在、可组合）                          │
│   DB（现有 datasource） · 代码仓库（git URL+凭据，新增）      │
│   文档（上传/手动录入，补充）                                  │
├─────────────────────────────────────────────────────────────┤
│ 证据基座层（substrate）—— 预提取、带指纹、可缓存、可阶段性检查  │
│   内容级工件（带证据指针，可作 wiki 依据）                     │
│   导航级工件（只指导规划与读窗，不进锚点块）                    │
├─────────────────────────────────────────────────────────────┤
│ 知识层（wiki 页面）—— 锚定在 db 表/字段/取值/关系上的语义     │
│   table/enum（确定性生成） + caliber/process/concept/rule/    │
│   relation（LLM 语义合成，过对账门禁）                         │
├─────────────────────────────────────────────────────────────┤
│ 运行层（chat 图内）—— 召回 → 锚点闭包 → schema 渲染 → 规划     │
└─────────────────────────────────────────────────────────────┘
        ↑                                   │
        └──── 运行时遥测反哺提取（缺口闭环） ←─┘
```

四个支柱原则（后续所有决策的裁决依据）：

1. **权威顺序：库 > 代码 > 文档**（从提示词铁律升格为工程结构——
   不同级别工件在不同位置被消费、被验证、被缓存）。
2. **锚定不变式：wiki 知识的落点（直接或间接）必然在 db 表/字段/
   字段取值/关联关系上**。无锚点即 lint 拦截（`CONCEPT_UNANCHORED`
   等已有码表）。字段枚举 wiki/字段统计信息（topk/值分布）作为
   table 页的强力补充。
3. **零信任流水线：LLM 步骤被夹在两层确定性验证之间**——
   基座 QA → plan 覆盖校验 → 上下文覆盖遥测 → reconcile → publish。
   任何来源（LLM/人/文档）过同一门禁，作者身份不改变验证强度。
4. **零影响降级：wiki 层任何失败只表现为无该段**，绝不影响 chat 主链路。

---

## 2. 来源层：三类受管知识来源

### 2.1 DB（必须项，收益/成本比最高）

- **全流程接入产品**：db 三件套（catalog=表/列/注释/索引、
  profile=列统计与低基数 topk、sample=样本行）由现有 profiling
  worker（租约模式 `metadata_scan_run`）生成，per-datasource 维度。
  消灭 `extract-dbcatalog.py` 里 CLI 形态的连库/解密操作。
- **DB-only 档位（最基础能力）**：零 LLM、纯确定性生成
  table/enum 页（`baseline.py` 模式，带列全集断言），接入即生效。
  诚实边界：无代码枚举时 enum 页只有 values 无 label——
  **不用 LLM 猜 label（猜=偏移）**，等代码/文档接入后补全。
- **定时变更检测**：指纹 = 表集合+列集合+generated_at。变更后两层
  动作：受影响 table 页确定性重生成（廉价）；引用变更列的语义页
  标 stale（契约 `schema_fingerprints` 预留）。与 git 轮询共用
  同一个"知识刷新调度器"（挂现有租约 worker，不新造调度体系）。

### 2.2 代码仓库（git URL + 凭据）

- **当作新增一类"资产连接"设计**（同 datasource 地位），不是提取
  管线参数。凭据复用现有 datasource 密码加密存储；克隆到受管
  workspace 目录。
- **安全不变式：分析全程只做文本读取（regex/AST 级静态分析），
  永不执行目标仓库的构建工具**（mvn/gradle/npm）——守住这条，
  git 接入不引入"运行不可信代码"攻击面。
- **触发**：轮询优先（`git fetch`+HEAD 比对，裸机安装也可工作），
  webhook 可选后置。
- **增量的入口盲区规则**（必须）：callgraph 入口清单 ⊄
  plan.entries ∪ excluded_entries → 触发**重新 plan**，
  不只重跑旧单元（新增 Controller 不在旧单元监控集，是增量盲区）。
- **能力边界显式声明**：代码分析限 Spring+MyBatis-Plus 形态；
  非 Java 仓库降级为 DB-only+文档通道，连接健康页明示
  "代码语义提取不可用"，不静默产出空语义。
- **成本控制**：每主题两次 LLM 调用、40 万字符上下文。增量优先、
  预算上限、首次接入给成本预估。

### 2.3 文档上传 / 手动录入（补充手段）

- **文档上传落 reqdoc 三通道机制**（已有）：主张 anchor（双源
  evidence）/ prose_only / review。"值/字段/表名字面不得来自文档"
  铁律已进提示词与契约。上传先过 `ReqdocFilter` 白名单清洗。
- **手动录入 = 人当作者，不当特权来源**：走同一
  `parse_page` lint → reconcile → review → publish 门禁。
  契约是门禁，作者身份不改变验证强度。
- **缺口闭环（接住被禁用的运行时 capture）**：运行时遥测
  （`SCHEMA_PAGE_MISSING`、召回零命中、plan_gate verified_negative）
  → 汇成**知识缺口队列** → 人工用文档/手动录入定向回答 →
  过门禁发布 → 运行时生效。wiki 后端下运行时 capture 已禁用，
  该队列接住"运行时反哺生长"职责。
- **产品形态**：API 先行（服务缺口队列定向补齐），编辑器 UI 后置，
  不做通用 wiki 编辑器。

### 2.4 档位组合

| 档位 | 来源 | 性质 | 产出 |
|------|------|------|------|
| L0 | DB only | 零 LLM、确定性 | table+enum 页（schema/topk/值域/FK） |
| L1 | +代码 | LLM 语义提取 | caliber/process/concept/rule/relation 页 |
| L2 | +文档 | 回证固化 | 业务叙事增强、reqdoc anchor 双源 |

逐级可叠加、可单独存在；`oid`/`scope.databases`（物理库名）天然多租户对齐——数据源是知识来源、不是使用限制。

---

## 3. 证据基座层（substrate）：预提取中间数据

定位与旧"底稿"的关键差异：**从仓库外临时文件升格为产品内一等的
证据基座——预提取、带指纹、可缓存、可阶段性检查**。

### 3.1 信任模型：按"提取方法"分级，不按"来源"整体分级

分界线是**抄录 vs 转述**：

- **内容级（带证据指针的确定性抄录，可直接作 wiki 依据）**：
  - DB：schema、列统计与 topk、样本行（连库实测 dump，对结构
    而言"真且全"）
  - 源码：**枚举值→label 映射、常量、配置字面量**（这些在源码里
    就是字面量，抄录即源码本身的选择性转录，带
    `code_path:文件:行` 指针；重新读一遍不会得到更多——放开
    这一档正是省成本且不丢正确性之处）
- **导航级（真而不全，只指导规划与读窗，绝不进锚点块）**：
  callgraph 可达性、文件白名单、代码摘要、休眠表候选、域聚类。
  过时无害（最坏读窗口次优），缺了不代表不存在。

**语义合成内容**（口径/规则/状态机/术语桥）：源码里不是字面量，
抄录不出来——LLM 必须读方法体全文合成，这是"真实提取必须回到
源码"的准确适用范围。

**流转规则（写死）**：导航级工件只允许出现在规划输入和读窗选择；
内容级工件可进锚点但必须带证据指针；两者都不允许替代"语义合成
必须读源码全文"。防滑变：导航级数据不能变成事实上的内容过滤器
（提取器保留拉取白名单外文件的能力 + 覆盖遥测）。

### 3.2 工件清单

| 来源 | 工件 | 级别 | 增量指纹 |
|------|------|------|---------|
| DB | schema（表/列/注释/索引）、列统计 topk、样本行 | 内容级 | 表集+列集+generated_at |
| 源码 | 入口清单、枚举字典+setter 绑定、常量/配置字面量 | 内容级（code_path 指针） | 文件 mtime+size |
| 源码 | 调用关系（ring≤2）、文件白名单、休眠候选、代码摘要 | 导航级 | 同上（过时可容忍） |
| 源码 | 关系底稿（mapper JOIN + FK 候选） | 内容级（抄录） | 同上 |
| 文档 | 白名单页面池、词法命中索引 | 导航级（主张必须回证） | 页面集合指纹 |

### 3.3 基座层工程要求

1. **每个工件带契约**：schema 校验+版本号（现状是 ad-hoc YAML 无
   校验）；`db-enum-reconcile` 交叉对账模式推广成标配 QA。
2. **摘要守确定性**：类注释/javadoc 首段（extract-catalog 现状）；
   若引入 LLM 摘要必须带模型指纹缓存并标注"导航级不作内容"——
   否则偏移经规划器（Step A 读摘要）向下传导。
3. **一次预提取、多方复用**：wiki 提取、评测（knowledge_recall_eval）、
   知识地图、对账共享同一份；指纹变更只重算受影响工件。
4. **阶段性检查 = 可审计产品面**：每工件确定性 QA 门 →
   连接健康页（db 快照 2 天前/74 表、repo HEAD/链路 146 文件、
   枚举 412 类/37 歧义字段）。

---

## 4. 提取管线（现状 CLI → 目标产品化）

现状（`apps/knowledge/wiki/pipeline.py` CLI）：

```
plan（Step A，LLM×1：主题单元聚类+双源过滤建议）
 → run（Step D：五块上下文组装 → D1 语义分析 → D2 页面生成）
 → reconcile（Step E：零信任对账）
 → 写 wiki-pages/ 子目录 + _index.md
update：三路指纹触发（代码/需求文档/db）
管理：scripts/wiki_admin.py（lint/reviews/adjudicate/publish）
```

五块上下文（ingest.py）——内容事实来自一手证据：

1. E0 系统文档（认知定位）
2. E0.5 需求文档候选页（ReqdocFilter 白名单 → 词法命中）
3. **E1 代码链路整文件**（callgraph ring≤2，40 万字符预算，
   超长文件方法切片）——源码本体
4. **E2/E3 db 底稿切片**（连库实测）+ 代码枚举基线 + 对账差异
5. 既有同主题页（增量锚点）

产品化改造：

- plan/run/reconcile 改为租约 worker 任务（复用 profiling 模式）；
- 页面存储 git 目录 → **DB 表**（page/revision/review_item），
  `InMemoryWikiStore` 加 DB loader；文件导出保留作 git-ops 备份
  （双面架构：管理面写、运行面读）；
- `wiki_admin` 四命令 → API+管理页；
- 去硬编码：`oid=1`/`ds=15`/`KNOWLEDGE_WIKI_PAGES_DIRS` 默认
  pplatform 路径，全部参数化为 per-datasource 维度
  （**DB-only 的前置条件**）；
- LLM 编排在管线内复用 `LLMFactory`（600s 超时/重试参数已调）。

---

## 5. 知识结构与锚定

### 5.1 页面类型与锚点方式

| 类型 | 生成方 | 锚点 |
|------|--------|------|
| table | 纯代码（db∪code catalog，列全集断言） | `anchors:[表]` + ground:table |
| enum | 纯代码（强证据归并，ENUM_UNBOUND 优于错挂） | ground:enum `fields:[表.列]` |
| relation | 纯代码（关系底稿投影）——**待补** | ground:relation |
| caliber/process/concept/rule | LLM（读源码全文合成） | ground 块谓词 / `maps_to` / `field_targets` |

### 5.2 锚定不变式的运行时面：锚点闭包 + 关系通道

**契约给了锚点，运行时必须有"锚点闭包"义务**：凡被召回页引用的
物理键（`anchors`/`field_targets`/`maps_to` 谓词/枚举 carriers），
其表必须已在规划上下文中。现状只靠图扩展配额（15-30%，排名竞争，
概率性），必须升级为确定性闭包：

- **原则**：图扩展负责"发现"（把用户没提的相关语义页带进窗口），
  锚点闭包负责"落地"（引用即可见）。纯确定性代码，成本近零。
- 实现：business recall 结束后从 passage 元数据抽表名集合，并入
  schema 渲染清单（不占图配额）；表页缺失落 `SCHEMA_PAGE_MISSING`
  遥测 → 增量提取触发链。

### 5.3 关系通道（当前最大缺口，P0）

**契约就位但语料为零**：`ground:relation` 块、租户字段端点 lint
都已定义；但 `baseline.py` 只生成 table/enum 页，语料中 grep 不到
任何 ground:relation。同时 unit 后端的 `relationships` 槽位被 wiki
短路（`recall_knowledge_node` 置空 bundle），schema 渲染器不渲染
关系——**wiki 后端下规划器对表间关联一无所知**，`certified_
relation_count` 恒 0，多表 JOIN 全靠 LLM 从列名猜。这是切到 wiki
后端引入的能力回退。

补法（按序）：

1. **生成侧**：关系底稿（mapper JOIN+FK 候选，内容级抄录）确定性
   投影成 ground:relation 块（独立页或 table 页内 relation 段）。
   DB-only 档位天然获得 FK 关系。
2. **渲染侧**：`WikiSchemaRenderer` 表页附"关联:"一行式
   JOIN 路径（`cust_company_info.id ← cust_shareholder_info.
   ref_cust_company_info`）。
3. **门禁侧**：plan_gate 锚点一致性 lint（ready plan 引用表 ⊆
   锚点闭包集合，缺则 advisory）。

现状语料佐证图结构稠密：`cust_company_info` 33 个语义页链入、
`tenant_setting_config` 30、`ca_fee_order` 26——锚点闭包有富集空间。

---

## 6. 运行层接线（现状已实现部分）

`KNOWLEDGE_BACKEND=wiki` 灰度切换（`wiki_backend_active` 单一判定）：

| 运行点 | 实现 | 状态 |
|--------|------|------|
| 业务语义段 | `wiki_business_text`（RRF+图扩展+向量）→ plan_query 的 `business_knowledge` | ✅ |
| 门禁缺口 | `wiki_physical_text`（强命中质量门）并入反弹上下文 | ✅ |
| schema 渲染 | `WikiSchemaRenderer`（table 页权威+db 兜底+枚举 label 内联+`SCHEMA_PAGE_MISSING` 遥测） | ✅ |
| 知识地图 | `_wiki_knowledge_map`（页面清单渲染） | ✅ |
| 语义复核 | wiki 文本段作 caliber 依据（reviewer payload） | ✅ |
| 快照 v3 | `wiki_context` 持久化进 planning_context（可恢复/可审计） | ✅ |
| 枚举翻译 | `enum_maps_for`+`translate_enum_cells`（结果单元格值→label） | ⚠️ 见 §7 |
| capture | wiki 后端禁用（语义生长走提取管线+缺口队列） | ✅ 按设计 |
| 关系通道 | — | ❌ 见 §5.3 |
| 锚点闭包 | — | ❌ 见 §5.2 |

---

## 7. 正确性缺口清单（与产品化正交，先修）

上一轮 review 确认的实现级问题（合入前阻断项在前）：

**P1 阻断级**

1. `_enum_refs_for_step` 从 `step.get("fields")` 取列，但步骤条目
   （`_merge_batch_into_steps`）只有 `tables` 无 `fields` 键——
   枚举翻译在真实链路恒不触发。修法：用 `result.get("fields")`
   ∩ 表列集。
2. 默认值翻转：`KNOWLEDGE_BACKEND` 默认 wiki 且 allowlist 默认 `*`，
   短路不校验 store 可用性——无语料部署静默失去全部 unit 知识。
   修法：默认 allowlist 置空（=unit）或 store 感知短路。

**P2**

3. 对账只查存在性不查语义：值域校验（`ENUM_VALUE_NOT_IN_DB` 模式）
   推广到所有锚点块的 `表.列='字面量'`（caliber/rule/process/enum
   统一查 db 分布∪代码枚举∪样本行）——杀"平台录入 vs PC_BUILD"
   类语义反转。确定性代码，成本很低。
4. 读窗口静默丢失：上下文覆盖遥测（链路文件数/展示数/截断字节）
   落 run 报告；`_STRUCTURAL` 后缀过滤掉的 ring≤2 文件若含枚举/
   常量/转换器命名，转 REVIEW 而非静默丢。
5. lint 债：`recall_topup.py` 11 处 E402（`_wiki_backend` 插在 import
   前）；`config.py:26` 无谓回退引入 UP038；`planning_context.py:117`
   手改缩进；6 文件 ruff format 不过。
6. `_topup_on_failed_gates` 的 wiki_context 回写是 no-op（用旧值
   重建自己）；`physical_gate_hits` 在图状态缺位。

**P3**

7. 澄清恢复轮业务段刷新时序：replan 分支在 topup 前拉 wiki 文本，
   扩窗后口径与 gate bounce 不一致。
8. 行号验证收紧一档：被引行 ±2 行内须出现锚点块标识符。
9. `enum_maps_for` 正则重解析 ground 块，与 contract.py 的
   `parse_findings`/`compact_block` 双实现漂移风险——统一走
   `ground_blocks`。
10. 测试 `test_wiki_deepening.py:142` 断言带故意错别字的 `or` 备选
    分支；`value_labels` 无前端消费者（TurnAnswerV1 未透出）。
11. 变更集卫生：剔除 `docs/.obsidian/`、`data/run/*.pid`、已 stage
    的日志删除。
12. 语料治理：36 页 `scope: 字符串` 或空 scope，统一为
    `scope.databases: [lowcode_pplatform]`（物理库名，随 db-catalog 迁移）。

---

## 8. 落地次序

```
阶段 0（现在，合入前）：
  §7 P1×2 + P2 lint 债 → 本轮 diff 可合入
阶段 1（正确性闭环，CLI 形态内）：
  值域对账（§7.3）→ 覆盖遥测（§7.4）→ 关系通道（§5.3）→
  锚点闭包（§5.2）→ corpus fingerprint/wiki_hits 落库
阶段 2（DB-only 入产品）：
  去硬编码 → db 三件套挂 profiling worker → DB-only 确定性生成 →
  定时变更检测（知识刷新调度器）
阶段 3（git 接入）：
  repo 连接资产（安全评审：文本读取不变式）→ 代码底稿任务化 →
  轮询触发+入口盲区规则 → 成本控制
阶段 4（文档+管理面）：
  缺口队列 API → 文档上传走三通道 → 手动录入同门禁 →
  页面落 DB 表+发布 UI → 运行时遥测反哺闭环
阶段 5（收敛）：
  灰度数据（召回命中率/页缺失率/verified_negative 率）驱动：
  wiki 稳定后 unit 包退役评估；召回拆独立 daemon（接口文档预留）
```

排程理由：

- 正确性先于产品化——先给带洞流程修洞，再搬进去，否则是给带洞
  流程加产品外壳；CLI 形态在冷启动期是优势（提取花 LLM 预算、
  人工裁决 REVIEW，工程师本地跑+发布前把关正是该有的形态）。
- DB-only 先行——不依赖契约稳定、无 LLM 成本、即刻改善规划。
- UI 后置——契约 v0.1 还在动，过早 API/UI 会把草稿锁进产品承诺。
- git 与文档的先后可按实际需求对调（文档机制成本最低，贵在编辑器）。

---

## 9. 开放问题（待决）

1. relation 落独立页还是 table 页内段落？（倾向：先 table 页内
   relation 段——渲染简单、闭包天然；独立页后置）
2. 页面落 DB 的表结构（page/revision/review_item 细节）与
   `InMemoryWikiStore` DB loader 的缓存失效策略。
3. 缺口队列的条目生命周期（谁开、谁关、何时过期）。
4. `KNOWLEDGE_RECALL_STRATEGY`（unit/node）与 wiki 的关系——
   切 wiki 时该开关是否还需要语义。
5. unit 包退役判定标准（灰度指标阈值）。
