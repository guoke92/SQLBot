# Wiki 知识体系统一方案（v2 重写稿）

> 日期：2026-08-31 · 状态：**重写评审稿**（应"先不考虑当前实现，回顾完整方案 + llm-wiki 项目方案与指导文档，重新统一设计"的要求）
> 本文取代《wiki知识体系总体方案.md》v1 的角色：给出**单一、完整、自洽**的目标架构，覆盖 提取→存储→管理→召回→消费→回填 全链路，并显式列出"设计 vs 当前实现"的差距清单。
> 输入源：llm-wiki 项目解剖（架构/两步摄取/search.rs 管线/REVIEW 队列/回填/管理面）、`docs/wiki页面契约-spec-v0.md`、`wiki源码摄取适配器-v1.md`、`wiki召回接口-v1.md`、P1/P1.5/P2 验收事实（comparison-report §一–八）。

---

## 0. 一句话定位

**把"数据问数的知识"建成一个 llm-wiki 形态的页面宇宙：确定性扫描器打底（真值），LLM 两步摄取做语义跃迁（说法），零信任契约解析（防线），RRF 混合召回直拼 prompt（消费），确定性门禁兜底（终审），澄清结论回填页面（生长）。**

消费者决定一切：llm-wiki 的页面是"给人读的知识"；我们的页面是**给规划器用的语义契约 + 给人审的载体**——所以每个设计偏离 llm-wiki 的地方，都必须能用一条问数失败模式来解释。页面形态始终是**散文 + 结构化数据的合金**：散文区（人审、业务背景、版本演进、边界叙述）+ ground 锚点块（机器确定性解析、lint 对账、召回结构边）——两者缺一，要么不可审计，要么不可消费；这正对应 Test-wiki（纯散文、零锚点）与旧 unit 包（纯结构、缺叙述）各自的天花板。

## 1. 六条不可妥协原则（全链路通约）

| # | 原则 | 出处 |
|---|---|---|
| P1 | **零信任解析**：任何模型产物（frontmatter/ground 块）语法失败 → 丢块+警告，绝不猜测、绝不部分采纳；页面散文保留 | llm-wiki 实测 45% frontmatter 不可解析；v0 §0.1 |
| P2 | **确定性打底，LLM 只做语义跃迁**：代码不直接进 LLM，先过扫描器（catalog/enums/relationships），锚点块发布时与底稿机械对账——幻觉锚点被拦截而非靠模型自觉 | 摄取适配器 v1；159 语义反转实证（PC_BUILD=客户录入，源码真值胜过模型推断） |
| P3 | **权威序 D7**：库字段实际值 > 代码读写 > 文档主张。冲突不静默覆盖，落 REVIEW 队列 | v3.1 D7；比对报告 §一 |
| P4 | **一物理实体一页**：一表一页、一 dictKey 一页，物理名做 slug，其余页面只引用物理键——复制税在格式层面不存在 | v0 §1.2；v3.1 D1 |
| P5 | **程序管结构，LLM 管内容**：page_key/created/updated/sources/contract_version 程序盖章；status 只经人工/门禁 | v0 原则 2 |
| P6 | **召回层永不破坏运行时**：wiki 召回的任何失败 = 少一个文本段，规划器照常运行；确定性由门禁体系保证，不由知识系统结构保证 | 召回接口 v1 首部；142 门禁实证 |

## 2. 全链路架构（七个面）

### 2.0 提取面 v2 重设计（应"跟当前实现出入很大"的评审意见重写）

**当前实现的真实形态（P1.5 已跑通的）**：域分组 = 表名前缀聚类（人工写死 13 组 DOMAIN_GROUPS）；Step1 的"代码证据" = 每组最多 6 个文件、按关键词命中行过滤后截 1500 字符的**碎片切片**；系统指导文档（服务路由索引/代码地图/业务规则）**完全没有进入提取输入**；调用图脚本只用于休眠表判定；底稿全部来自代码扫描，**数据库本体一次都没被读取**。这四个缺陷正是评审意见指出的方向性问题——提取面必须从"表名聚簇 + 关键词碎片"升级为"**架构认知驱动的全链路穿透**"。

#### 2.0.1 四层证据体系（新：db 实测是最强证据）

| 层 | 来源 | 产出 | 权威序位置 |
|---|---|---|---|
| E0 系统指导文档 | 目标仓库 `.dev-standards/knowledge/`（服务路由索引→服务详情→代码地图→业务规则）+ README/需求/设计文档 | 系统全景认知、业务域清单、入口模式 | 认知入口（最弱证据，不得作为最终依据） |
| E0.5 需求文档 wiki（Test-wiki） | `/Users/fanjunwei/workspace/Test-wiki`（raw 源 = 桌面《需求文档》按版本迭代 docx，已摄取 402 页：concept 252 / entity 91 / source 37 / query 14 / finding 5） | **业务意图层**：版本演进、业务规则、状态新增（如"审批撤销"枚举）、校验规则、产品口径（如供票开通三校验）、人物/团队归属 | 业务语义补充源：文档主张 → 弱于代码与库，但**时间维度独有**（代码只有现在时，文档有"V1.13 引入/本期不处理"的演进史） |
| E1 调用链底稿 | **确定性脚本**：入口类枚举（Controller/@DubboService/Facade/Listener/Job）→ 结构性类型 BFS → per_entry 分层可达调用图 + DO/Mapper→表归并 | 每个入口的可达文件清单（ring0-2 核心链路）、休眠表基线 | 结构骨架（确定） |
| E2 数据库底稿 | **连接目标 DB**（从 spring 配置文件解析 jdbc url；连不上时降级代码扫描）：`information_schema` 全表/字段/索引/DDL + `ANALYZE TABLE` 后的行数/统计信息 + 每表最新 N 行样本数据（脱敏）+ 后续可扩展 BI 统计指标（distinct 分布/空值率/最大最小值） | 真实存在性 + 真实值域 + 真实枚举分布 | **最强证据**（库 > 代码 > 文档） |
| E3 代码扫描底稿 | 现有 extract-catalog/enums/relationships（`@TableName`/`@ApiModelProperty`/枚举/JOIN） | 字段注释语义、枚举字典、关系候选 | 佐证与补充（db 不知道"注释说了什么"） |

权威序不变但更具体：**E2 db 实测 > E3 代码扫描（代码佐证 db、补充语义）> E0.5 需求文档 wiki > E0 系统文档**；E1 调用链是"知识单元怎么切"的结构依据，不做语义裁决。

**E0.5 的接入方式（明确：不做第二套 wiki，做受控引用）**：Test-wiki 是独立 llm-wiki 项目（研究型 schema：entity/concept/finding），与问数 wiki（v0 契约：8 种 ground 锚点）**不同构**——它的页面无物理锚点（402 页中仅 2 页提到物理表名）、无 ground 块、slug 是业务语言。因此不做整库合并（会污染契约语料），而是：
1. **抽取而非搬迁**：按域从 Test-wiki 检索相关页（词法+图扩展），把**业务规则/状态新增/口径主张**抽取进目标 wiki 的对应页面（rule/process/caliber/concept 页的散文区与 ground 块），`sources` 记 `reqdoc:<页面slug>`；
2. **冲突即 REVIEW**：文档主张与 E2/E3 冲突时（如文档说"本期不处理"但代码已实现），以代码/库为准、文档差异落 REVIEW（这正是"文档是入口不是最终依据"）；
3. **时间维度保留**：版本演进信息（V1.13 引入/V1.35 新增）写进页面散文区（`## 版本演进` 小节），服务人审与口径溯源，不进 ground 块。

#### 2.0.2a 中间产物定位与目录约定（评审补充，明确）

**E0–E3 底稿全部是中间数据（tmp 性质），只服务 wiki 页面生成，不是 wiki 的最终信息、不参与召回展示**：

```
docs/wiki-knowledge/pplatform/
├── substrate/          # E1+E3 代码侧底稿（catalog/enums/relationships/callgraph）——tmp 中间产物
│   └── tmp/            #   原始过程数据（db 样本行全文、llm 认知草案、白名单草稿）
├── db/                 # E2 db 底稿（db-catalog/db-enums/db-profile）——tmp 中间产物
└── wiki-pages/         # 唯一的"最终语料"目录（经合并+lint+发布门禁），运行时 KNOWLEDGE_WIKI_PAGES_DIRS 只指这里
```

- 底稿文件带 `generated_at` / 源 rev / db fingerprint，可随时删掉重建（重建唯一成本是重跑脚本）；
- LLM 生成页面的 `sources` 引用底稿文件名（溯源），但底稿本身不进页面目录、不入召回；
- 运行时只认 `wiki-pages/`——中间产物目录任何时候删空都不影响线上召回。

**db 连接配置源约定**：默认读 `/Users/fanjunwei/IdeaProjects/pplatform-web/lowcode-pplatform-application/src/main/resources/application-qa2-local.properties`（`DB_SERVER/DB_PORT/DB_USERNAME/DB_PASSWORD/DB_PUBLICKEY`，druid RSA 解密，脚本内置）；支持 `--db-profile <path>` 换配置文件或 `--db-url/--db-user/--db-pass` 直接指定。口令不落盘、不进日志；样本行按列类型脱敏（文本列截断、只保留低基数枚举/状态列的分布统计）。

#### 2.0.2 完整提取流程（六步，替换原"双源统一管道"段）

```
Step A 系统认知 + 白名单 + 域→入口映射（LLM 主导，脚本辅助）
  LLM 读 E0 全部指导文档 + E1 的 entry_points 清单 → 输出：系统架构总述、
  初步域清单、代码入口模式；同时制定/补全【排除白名单】
  （构建产物/前端样式/测试工具/生成代码/配置样板——逻辑无关内容，
  写成 repo-rooted glob 清单，之后所有脚本扫描与 LLM 切片都跳过）。
  【实证修正】域→入口的映射必须由 LLM 依据路由文档给出（每域选主入口
  清单），脚本按 java 包名自动聚类不可靠——多模块仓库里包段混杂层级名
  （application/controller/service）与业务名（cust/product），实测 51 个
  "包名域"中大量是层级碎片。E1 的职责是给 per_entry 分层可达
  （ring0-2=核心链路），域的切分认知归 LLM。
Step B 调用链底稿（脚本，一次固化，全程复用）
  extract-callgraph.py v2：入口枚举（Controller/@DubboService/Facade/
  Listener/Job/XxlJob 等）→ 结构性类型 BFS（Service/Impl/Dao/Mapper/DO/
  Application 等才扩展；DTO/枚举/常量只作叶子）→ 输出 per_entry 分层可达
  （ring0-1=入口+直属服务，ring2=service impl/dao 层，…按深度排序）、
  表归并（DO→Mapper→@TableName）、休眠候选；产物 callgraph.yaml 固化入
  substrate/。Step D 每域取"入口清单 → 各自 per_entry 可达文件按层合并"
  作为穿透上下文——LLM 不再从零扫代码。
  【实测】单入口可达 ~790 文件（结构性裁剪后，从 1284 降下来），
  ring0-2 约 140 文件构成核心链路；52/74 表可达。
Step C 数据库底稿（脚本，只读）
  解析 spring 配置 jdbc url → 连接 → information_schema（表/字段/索引/注释/DDL）
  → ANALYZE TABLE → 行数 + 统计 → 每表 LIMIT N 样本行（列值脱敏：只保留
  枚举/状态/低基数列的值分布，文本列截断）→ db-catalog.yaml 固化
  （连不上 DB → 显式降级：以 E3 为准并在每页标 evidence 缺 db 层）
Step D 域穿透（LLM 主导 + 调用链/底稿约束 —— 核心变化点）
  按 LLM 域映射（Step A 产物）逐域穿透；
  每域 LLM 拿到四块上下文：
  ① E0 该域业务规则文档 + E0.5 Test-wiki 该域相关页（业务规则/状态新增/版本演进）
  ② E1 该域入口可达的核心链路文件（整文件阅读，不是关键词碎片）
  ③ E2/E3 底稿切片（表结构+真实值分布+枚举基线+对账差异）
  ④ 既有 wiki 该域页面（增量合并而非每次重建）
  → 沿写入口与读入口两条链路穿透（沿用 reference.md §2/§5 方法：
  读流转/写流转/参数传播/写值点清单）；E0.5 的业务主张在穿透中被
  代码证实→正式落页，被证伪→REVIEW，代码无覆盖→标注 document_claim
  证据强度保留
Step E 底稿对账（脚本，零信任）
  LLM 页面的锚点块 ←机械对账→ E2∪E3 合并底稿（字段在不在、类型族、
  枚举值真值、db 分布佐证）；失败=丢块+REVIEW；coverage 缺口自动生成
  missing-page REVIEW
Step F 写入（不变）
  sanitize → 盖章 → groundExtract/Validate → 路由 → 合并 → 写入+index
```

Step A–B–C 都是**一次性/低频增量**的固化底稿（schema 指纹 + repo rev 驱动重跑）；Step D 才消耗 LLM token，且每个域的上下文是"完整链路文件 + 三层底稿"，不是现在的 1500 字符碎片。

#### 2.0.3 与 llm-wiki 流程的对齐说明

llm-wiki 的摄取 = "读源材料 → Step1 分析 → Step2 生成"，其源材料是自包含文档。我们对齐的是**管道形状**（两步、FILE/REVIEW 协议、sanitize、合并），替换的是 **Step1 的输入预处理**：llm-wiki 的"文档解析器"位置上放的是我们独有的"**架构认知 + 调用图切片器 + db 画像**"三件套。这正是摄取适配器 v1"确定性打底、LLM 只做语义跃迁"在提取面的完整展开——v1 文档没说清楚的"打底"到底打到多厚，本节给出答案：E0–E3 四层。

**Test-wiki（E0.5）复用了 llm-wiki 的原生能力**：需求文档按版本迭代（111 个 docx），正是 llm-wiki 文档摄取的主场——桌面《需求文档》→ Test-wiki 项目（已摄取 402 页）→ 我们的问数 wiki 按**域引用抽取**。即：llm-wiki 不只被"参考"，它作为工具链真实运行在文档源上；问数 wiki 是它的下游消费者之一（另一路消费者是通用研究问答）。

```
┌─────────────────────────────────────────────────────────────────────────┐
│ ① 提取面（双源统一管道）                                                  │
│   源A: 业务系统源码        源B: 文档/网页/对话回填  （llm-wiki 原生）        │
│    │ 确定性扫描器               │ 文档解析器                              │
│    │ catalog/enums/relations    │ (同一两步管道，不同 Step1 预处理器)        │
│    ▼                           ▼                                       │
│   底稿 substrate(YAML, 常驻 raw/sources) ── scope 切片(表/域)            │
│    │                                                                   │
│   Step1 LLM 结构化分析（读底稿切片+代码切片，产语义清单）                     │
│   Step2 LLM 生成（FILE 块页面 + REVIEW 块，纯块协议，首字符必须 `-`）        │
│    ▼                                                                   │
│   写入防御层：sanitize(ground 围栏白名单) → 盖章 → groundExtract/Validate  │
│   → 锚点对账底稿 → 目录路由(type↔dir) → 合并 → 写入+index/log              │
├─────────────────────────────────────────────────────────────────────────┤
│ ② 存储面                                                                │
│   验证期: git 管理的页面目录（一个数据源 = 一棵页面树）                       │
│   目录=类型: tables/ enums/ concepts/ processes/ calibers/ metrics/       │
│              rules/ patterns/ scenarios/ queries/ sources/               │
│   嵌入缓存: .wiki-embeddings.json（指纹=模型+维度+页面集合，变更增量重嵌）     │
│   产品化(阶段二): PG wiki_page 表 + embedding_fingerprint 家法             │
├─────────────────────────────────────────────────────────────────────────┤
│ ③ 管理面（REVIEW 是唯一的人工裁决通道）                                    │
│   REVIEW 项四类: contradiction / duplicate / missing-page / suggestion   │
│   来源: 摄取 REVIEW 块 + lint findings + coverage 缺口 + schema 漂移        │
│   裁决: 预置动作白名单（Create Page | Skip | Deep Research）               │
│   自动清理: missing-page 若页面已存在→resolve；矛盾/语义类保守留人工           │
│   发布门禁: draft→published 当且仅当页面+引用闭包 lint 零 error              │
├─────────────────────────────────────────────────────────────────────────┤
│ ④ 召回面（llm-wiki search.rs 公式逐条对齐 + 两阶段问数特化）                  │
│   load_dir → 切块(标题感知+ground 围栏原子) → 通道:                        │
│     词法: CJK bigram+run, filename_exact×200 / title短语×50 /             │
│           正文短语×20(计次≤10) / 标题token×5 / 正文token×1                 │
│           + 别名/值标签页级加成（问数特化，值⊂文本哲学的页面版）                │
│     向量: chunk 级超采 top_k×3(≥30) → 页面聚合 top+min(0.3×tail,1−top)     │
│     融合: RRF score=Σ1/(60+rank)；向量故障静默降级纯词法                     │
│     图扩展: [[wikilink]] 一跳，种子≤20，邻居分Σ1/(rank+1)/61；              │
│           配额=ceil(limit×(0.30−0.15×向量覆盖率)) clamp[1,limit−1]          │
│   两阶段: business(业务语义, 窗口5~10, 图配额全开)                          │
│           physical(门禁缺口检索, 窗口小, 图降格候选竞争)                      │
│   围栏: published only + scope.databases 库名交集（对向量通道同样生效）        │
│   输出: RenderedPassage{page_key,title,score,source,related_to,text}      │
├─────────────────────────────────────────────────────────────────────────┤
│ ⑤ 消费面（SQLBot 运行时）                                                 │
│   retrieve_context: recall(business) → <business_knowledge> 段            │
│   plan_gate missing_concepts: recall(physical) → 反弹上下文段               │
│   知识地图: 页面清单渲染 → <knowledge_map>                                │
│   命中遥测: page_key/score/source → query_run.agent_decision["wiki_hits"] │
│   开关: KNOWLEDGE_BACKEND=unit|wiki + per-DS allowlist 灰度                 │
├─────────────────────────────────────────────────────────────────────────┤
│ ⑥ 终审面（确定性门禁，不属知识系统但依赖其缺口声明）                           │
│   plan_gate 反弹(一次) / T4 修复前扩表 / 硬门禁重校验 —— 已建，保持不动        │
├─────────────────────────────────────────────────────────────────────────┤
│ ⑦ 回填面（好答案复利，llm-wiki "good answers compound"）                   │
│   触发: 澄清结论落定 / 用户采纳的 SQL / 人工收藏                            │
│   产物: concept 术语桥候选 / pattern 范例候选（写为 pending 源）              │
│   管道: 复用两步摄取 → 三层合并 → REVIEW → 发布（与①完全同一条管道）           │
└─────────────────────────────────────────────────────────────────────────┘
```

## 3. 页面契约要点（v0 采纳，不变）

8 种 ground 块（table/enum/relation/process/caliber/metric/rule/pattern）+ 概念术语桥（frontmatter 锚点）+ 3 种组织页（scenario/query/source）。关键机制：

- **round-trip 审计**：页面→解析→规范化重序列化→页面 字节级稳定，CI 固定；
- **catalog 驱动 lint**：TABLE/FIELD_NOT_IN_CATALOG、TYPE_FAMILY_MISMATCH、TENANT_FIELD_AS_ENDPOINT 零容忍、COVERAGE_GAP 阻断出包；
- **确定性块合并**：块层不走 LLM（table.fields 并集+catalog 胜；enum.values 并集+基线胜；relation 幂等；独占源整体替换）；
- **校验码表**见 v0 §6（18 项），发布门禁 = 引用闭包零 error。

## 4. 语义层地位：定量结论（P2 评测，64 题）

| 语料形态 | 命中率 |
|---|---|
| 仅基线层（扫描器直出 175 页） | **35%** |
| 基线 + 语义层（语义页 REVIEW 发布后） | **77%** |
| 宽松判定（口径/概念页替代算对） | ~90% |

**结论（写入架构 DNA）**：基线层给存在性与真值锚点，语义层给业务说法；两者缺一，召回腰斩。扫描器与 LLM 是互补层不是竞争层——这是 P1.5 十三域全量摄取后不再动摇的架构判断。

## 5. 当前实现 vs 本方案的差距清单（诚实盘点，按危害排序）

> 现状资产：wiki 引擎 2322 行（contract/chunker/graph/recall/embeddings/ingest/full_extract/convert/substrate_convert）+ 运行时接缝（steps/wiki_recall.py, KNOWLEDGE_BACKEND 开关）+ 语料四堆（substrate-pages 175 / semantic-full 96+81 REVIEW / pages 21 / legacy-union 881）+ 全量回归 614 绿。

### G1 · 语料双子集冲突，未做"一物理实体一页"合并【危害最高，违反 P4】

substrate-pages 与 semantic-full 存在 **36 个 page_key 碰撞（35 个是 table 页）**：如 `ca_certification_info` 同时存在基线版（34 字段、源码底稿）和语义版（LLM 生成、字段键用了 `field` 而非契约要求的 `name`）。`InMemoryWikiStore` 以 page_key 为 dict 键——**后加载者静默覆盖先加载者**，谁进 KNOWLEDGE_WIKI_PAGES_DIRS 的前半段谁被丢，且无任何告警。方案 §2① 的确定性块合并（§5.3）根本没有跑在这两堆语料之间。

**修法（M1）**：写一次性合并器走 v0 §5.3 块合并规则（基线胜字段存在性/类型，语义层贡献 description/meaning 附加；同 page_key 语义 table 页与基线页合并为单页），产出**唯一语料目录**（目标 ~235 页 + enum/concept），lint 硬错误清零后发布。此后 KNOWLEDGE_WIKI_PAGES_DIRS 只指这一个目录。

### G2 · 语义页质量缺口成批存在【违反 P1 的"落地面"】

- 【已迁移】43 页曾把表名填进 scope.datasources（如 `datasources: [ca_certification_info]`）——现已统一为 scope.databases 物理库名——LLM 幻觉 + 摄取时未对账底稿；
- 语义 table 页 ground:table 块用 `field:`/`meaning:` 键，契约要求 `name:`/`description:`（lint 未查键名，属契约子集实现遗漏）；
- 语义页 `status: draft` 未经发布门禁即参与了 77% 评测（评测利好为真，但生产围栏会把它们全滤掉——**评测语料与生产围栏不一致**）。

**修法（M1 同批）**：合并器内做 schema 归一（键名修正/scope 修正/底稿对账），lint 扩 `GROUND_KEY_INVALID` 码；修正后统一发布。评测重跑确认 77% 不倒退。

### G3 · 语义摄取域覆盖不全【P2 已记账】

13 域中 REVIEW 81 项未处置；`_review_table_*.json` 形态显示"表有 catalog 无字段语义"类缺口（如 cust_user_rel）。coverage 闭环（底稿全表 vs 页面锚点）应从"一次性人工"升级为**常驻 REVIEW 来源**（适配器 v1 §3 的原设计）。

### G4 · 回填面（⑦）零代码【方案有设计、无落地】

澄清结论→概念页候选、好答案→pattern 候选的管道未实现。这是"知识体系随使用生长"的核心闭环，也是 159 类问题的长效疫苗。**修法（P3 阶段）**：`steps/` 挂澄清结论采集 → pending 源目录 → 复用 full_extract 两步摄取 → REVIEW 队列。入口最小化：先做"澄清结论 → concept 页草稿"一条线。

### G5 · physical 阶段召回未接线【召回接口 v1 §3 的一半】

`mode="physical"`（plan_gate missing_concepts 检索、图降格候选竞争）未接入 plan_gate 反弹路径；当前反弹仍只走 recall_map/值索引。**修法（P3）**：`plan_gate` 对 missing_concepts 逐概念调 `recall(mode=physical)`，命中作为反弹上下文段（与现有扩表机制互补，不替代）。

### G6 · 知识地图仍走 unit 体系【切换不彻底的残留】

`render_knowledge_map`（recall_map.py:110）读的是 unit 编译面。KNOWLEDGE_BACKEND=wiki 的 DS 应改为渲染 wiki 页面清单（index 语义）。**修法（P3 小项）**：wiki 后端分支 + `wiki_knowledge_map()` 渲染器。

### G7 · 管理面无 UI/命令【验证期可接受，记账】

REVIEW 队列目前是 JSON 文件堆；裁决/发布门禁/lint 巡检无命令面。**修法（P4）**：`scripts/wiki_admin.py`（lint 报告 / REVIEW 列表+裁决 / 发布 / coverage 报告），产品化再谈服务化 UI。

### G8 · 提取面与目标形态的结构性差距【v2 新增，评审主议题】

1. **域分组是表名前缀聚类**（full_extract.py DOMAIN_GROUPS 人工写死 13 组），不是从调用图入口聚类——域边界靠人猜，漏域/错域无机械信号；
2. **Step1 代码证据是关键词碎片**（`_read_source_slices`：每组 ≤6 文件、命中行过滤、1500 字符截断）——LLM 从未读过一条完整调用链路，状态机/参数传播这类跨方法语义基本靠猜；
3. **系统指导文档未进提取输入**（服务路由索引/代码地图/业务规则文档就在目标仓库 `.dev-standards/knowledge/`，参考技能 reference.md §1 明确要求"文档是入口"，但 P1.5 管线没接）；
4. **调用链脚本只用于休眠表**（extract-callgraph.py 现状 = 可达性布尔值），没有产出"每域入口→可达文件清单"这个穿透上下文；
5. **数据库本体零参与**——没有表/字段/索引/统计信息/样本数据（ANALYZE TABLE），E2 层整体缺失，"库 > 代码 > 文档"权威序的第一环落空；
6. **无排除白名单机制**——扫描器只有 `_BOILERPLATE` 字段名单，没有 repo 级"逻辑无关文件/目录"过滤（构建产物/测试/生成代码会进 LLM 视野浪费上下文甚至污染）。

**修法（提取面 v2，本方案 §2.0）**：E0–E3 四层证据体系 + Step A–F 六步流程，其中 Step B（调用图固化）、Step C（db 底稿）为新脚本资产，Step A（LLM 认知+白名单）、Step D（域穿透换上下文）为管线改造。**连通性已实测通过**（2026-08-31）：qa2-local profile 的 druid RSA 口令成功解密，`172.16.111.194:23306` 可达，`lowcode_pplatform` 库 75 表（information_schema 探针返回 ca_certification_info=737 行/cust_company_info=88695 行等），枚举列实际分布直读成功——且 `cust_build_type` 的 column_default='AGW_BUILD'、实际数据 98.8% AGW_BUILD（PC_BUILD 1176 行/SIMPLE 1 行——SIMPLE 不在代码枚举基线，db 层当场抓获）这类**db 实测事实**正是 E2 层价值的直接证明。**Step B/C 已实现并固化**：callgraph.yaml v2（325 入口、per_entry 分层可达、休眠 6 表与 db 三方对账确认 5 张死代码）+ db 三件套（catalog/profile/sample，877 列画像）+ 两份对账报告（db-enum-reconcile 21 项、table-reconcile 6+5 项）均已落 `substrate/` 与 `db/`。E0.5（Test-wiki 402 页）已调研：业务规则/版本演进密度高（如供票产品三校验、审批撤销状态新增），但零物理锚点——按 §2.0.1 受控引用接入。

### 明确不做（与 v1 结论一致）

多模态、Deep Research、通用 chat agent 运行时、Obsidian 生态、查询时 LLM 自由读页、usage 衰减（llm-wiki 也没有，`updated` 字段+stale lint 够用）。

## 6. 阶段路线（重排后）

| 阶段 | 内容 | 验收 |
|---|---|---|
| ~~P0/P1/P1.5/P2~~ | 契约+引擎+源码直提+全量语义摄取+向量通道+开关灰度 | 已完成（见 §4 评测）；**提取面按 G8 判定为临时形态，被 E0–E3 v2 取代** |
| **E1 提取面 v2 底稿**（✅ 已完成 2026-08-31） | Step B 调用图 v2（325 入口 per_entry 分层可达）+ Step C db 底稿（75 表/877 列画像）+ 三方对账报告 ×2 + E0/E0.5 文档源盘点 | callgraph.yaml 覆盖全部入口 ✓；db×代码 catalog 对账 ✓（6 db-only/5 code-only/21 枚举差异）；E0.5 Test-wiki 402 页调研完成 ✓ |
| **E2 穿透重提 + M1 语料统一**（下一步） | Step A LLM 认知（域→入口映射+白名单）+ Step D 逐域穿透（四块上下文：E0/E0.5 文档 + E1 核心链路整读 + E2/E3 底稿 + 既有页增量）→ Step E 对账 → 全量重生成；G1 合并器 + G2 schema 归一 + lint 扩码 | 与 P1.5 语料抽样比对质量可举证（重点：E0.5 业务规则页是否被代码证实落页）；碰撞 0；lint 硬错误 0；round-trip CI 绿；评测重跑 ≥77% |
| **P3 运行时补全** | G5 physical 接线 + G4 回填最小闭环（澄清→concept 草稿）+ G6 wiki 知识地图 | 159 类问题端到端：业务词→概念页→规划器；回填 2-3 例真实结论入库 |
| **P3.5 灰度放量** | 真实 DS allowlist 灰度 + 金标回归（表召回@k/值命中/澄清率 ≥ unit） | 达标才翻默认 |
| **P4 产品化** | G7 管理命令面 + PG 服务化（版本钉扎/多租户 oid//recall 组装端点） | unit 退役 |

## 7. 与 llm-wiki 的最终取舍账（重申并固化）

**取**：两步摄取+增量缓存、FILE/REVIEW 块协议、sanitize+盖章防御层、RRF/聚合/图扩展全套公式、REVIEW 预置动作白名单、三层合并+锁定字段、好答案回填思想、目录即类型路由。
**改**（每条对应一条问数失败模式）：源码摄取适配器（幻觉锚点 159）、catalog lint+coverage 闭环（漂移/盲区 138）、两阶段召回（级联映射 159）、锚点块机器验收（错误数据 142）、回填问数化（语义映射持续补全 159）。
**舍**：多模态、Deep Research、通用 agent、查询时自由读页。

---

### 附：本文档与既有文档的关系

- `docs/wiki页面契约-spec-v0.md` — 页面格式权威，**继续有效**（G2 修正后语义页才真正满足它）；
- `wiki源码摄取适配器-v1.md` / `wiki召回接口-v1.md` — 提取/召回的接口规范，**继续有效**，G5/G6 即其未完成条款；
- `wiki知识体系总体方案.md` v1 — 被本文取代，其阶段表以本文 §6 为准；
- `pplatform/comparison-report.md` — 验收证据链（§一 语义反转 / §六 历史比对 / §七 全量直提 / §八 向量评测），作为本文结论的引用源保留。
