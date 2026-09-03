# 源码摄取适配器 v1（llm-wiki 能力空白的补充设计）

> llm-wiki 支持文档/PDF/网页摄取，**不支持从源码提取**。本 spec 是我们的独有补充。
> 与 v0 契约的衔接：底稿（catalog/enums/relationships YAML）常驻 `raw/sources/` 并由脚本刷新
> ——这同时回答 v0 开放问题 5（COVERAGE_GAP 验收依赖 catalog 常驻，本适配器即其供给方）。
> 核心原则：**确定性打底，LLM 只做语义跃迁**——代码不直接进 LLM，先过确定性扫描器打底，LLM 在扫描产物之上做语义分析。

## 1. 为什么必须有底稿（Ground Substrate）

纯 LLM 读代码产 wiki 的最大风险是**幻觉锚点**（编造字段/枚举/关联）。对策：现有提取技能的确定性扫描器
（catalog / enums / relationships，源自 `.cursor/skills/knowledge-extraction` 的脚本资产）产出**结构化底稿**，
页面的锚点块在发布时与底稿**机械对账**——幻觉锚点被确定性拦截，而非靠模型自觉。

```
业务系统仓库（Java + MyBatis-Plus）
   │
   ├─ 确定性扫描器（非 LLM）─────────────────────────────┐
   │   catalog：DDL/entity → 全表全字段+类型+注释          │ 结构化底稿
   │   enums：枚举类/字典表 → 全枚举值+label              │ （ground truth）
   │   relationships：mapper XML join/FK → 候选关联+证据  │
   ├─ 代码切片器（scope 切分）                            │
   │   按 表/领域模块 切：mapper XML + entity + service 片段│
   ▼                                                     ▼
Step 1：LLM 结构化分析（输入 = 底稿切片 + 代码切片）
Step 3：LLM 生成页面（页 + 锚点块 + wikilinks + REVIEW 块）
   │
   ▼
发布门禁：锚点块 ←对账→ 底稿（契约 A2 校验表）
```

## 2. 两步摄取（移植 llm-wiki ingest.ts 的链路）

| 步骤 | 输入 | 输出 | 参照实现 |
|---|---|---|---|
| Step 1 分析 | 底稿切片 + 代码切片 | 结构化分析（该 scope 的语义清单：枚举语义/状态流转/口径/术语） | `buildChunkAnalysisSystemPrompt` |
| Step 2 生成 | 分析 + 页面 schema + 现有 index | 页面（FILE 块）+ REVIEW 块 + log 条目 | `buildGenerationPrompt` |

关键提示词约定（直接移植）：
- 页面 frontmatter `sources` 必须含源文件引用（我们扩展为 `repo:path@rev`）；
- 页面路由遵循 schema 定义目录（我们的 type 体系）；
- REVIEW 块只输出高价值项（缺口/待确认），无则不输出；
- **同主题冲突**：走三路合并（`buildPageMergeSystemPrompt`）——保留双方事实、去重、冲突分离并标注来源，temperature 0.1，**不静默覆盖**。

## 3. Scope 粒度与增量

- **摄取单元 = 表 或 领域模块**；一个 scope 产 3~8 页（表业务页 + 其枚举页 + 关联概念页）；
- **增量键 = schema 指纹 + repo rev**：DDL 变更/代码合并 → 只重摄取受影响 scope；
  指纹漂移同时触发 lint `stale` → REVIEW 队列；
- **覆盖率闭环**：底稿全表清单 vs 已发布页锚点覆盖 → 未覆盖表/字段自动生成 `missing-page`
  REVIEW 项（coverage.yaml 思想的 wiki 化：从离线人工验收变为持续队列）。

## 4. 页面类型 → 提取产物映射

| 页面类型 | 主要来源 | 典型内容 |
|---|---|---|
| `enum` 页 | 底稿.enums + 代码注释/字典表 | 值语义、易混淆对照（`contrast_with`）——159 类问题的疫苗 |
| `table` 业务页 | 底稿.catalog + mapper/service 代码 | 行语义、业务键、常用过滤 |
| `process` 页 | service 状态机代码 | 状态流转、触发条件 |
| `caliber` 页 | 口径类代码/注释 | 过滤条件、默认谓词 |
| `concept` 页 | 跨 scope 术语 | 术语定义 + aliases |

## 5. 与文档摄取的统一

文档（需求/设计/手册/网页）与源码走**同一条两步管道、同一个页面契约、同一个 REVIEW 队列**，
差异仅在 Step 1 的输入预处理器（文档解析器 vs 源码扫描器+切片器）与对账基准（文档原文 vs 结构化底稿）。
