# Wiki 知识提取规范指南 v1

> 日期：2026-09-10 · 状态：**问数 Wiki 提取操作权威**  
> 读者：执行提取的 agent / 工程师。格式语法不在本文展开，见契约；召回与产品化不在本文操作面。

本文把已落地的提取管线收成一份可执行 runbook。阶段名与代码一致；文档与代码冲突以本文「权威裁决表」为准。

---

## 0. 本文地位、读者、不做什么

**本文 = 问数 Wiki 提取的唯一操作权威。** 写页面、跑脚本、过门禁、独立重提，只认本文 + 其交叉引用。

| 交叉引用 | 管什么 | 与本文关系 |
|---|---|---|
| [`docs/wiki页面契约-spec-v0.md`](../wiki页面契约-spec-v0.md) + [`contract.py`](../../backend/apps/knowledge/wiki/contract.py) | ground 语法、frontmatter、lint 全码表 | **格式权威**；本文只列提取需要的子集 |
| [`wiki知识体系统一方案-v3.md`](./wiki知识体系统一方案-v3.md) | 产品/运行时、双轴状态、P1–P10 | **不**另写提取步骤 |
| [`wiki知识体系统一方案-v2.md`](./wiki知识体系统一方案-v3.md) §2.0 | E0–E3 / Step A–F 设计语义 | 提取面设计来源；**执行序以代码为准**（见 §1、§3） |
| [`wiki源码摄取适配器-v1.md`](./wiki源码摄取适配器-v1.md) | 确定性打底 + 两步 ingest 思想 | 细节以 `ingest.py` 为准 |
| [`wiki召回接口-v1.md`](./wiki召回接口-v1.md) | 运行时召回 | **本文不覆盖召回操作** |
| [`.cursor/skills/knowledge-extraction/`](../../.cursor/skills/knowledge-extraction/) | 扫描器脚本 + 读码硬约束 | wiki **不跑** `knowledge-package submit`；HOW 已转写进 §7.4 / §12 / §13 |
| 实现 | `pipeline.py` / `ingest.py` / `baseline.py` / `filters.py` / `field_roles.py` / `scripts/wiki_admin.py` / `scripts/wiki_enrich.py` | **操作真值**，高于过时方案叙述 |

**读者**：跑提取的人（含 AI agent）。假设已能在 `backend/` 用 venv 调 Python。

**本文不做什么**：

- 不定义召回算法、embedding、datasource 绑定（见召回接口 / `corpus_store.py`）
- 不把 KnowledgePackageV2 当 wiki 产物（`knowledge-package.py scan/decompose/submit` 是旧 unit 旁路）
- 不设计产品化 worker / `wiki_*` 受管表（v3 阶段二）
- 不把好答案回填当本轮必做（已知债，见 §17）

**旧文档降级**：

| 文档 | 地位 |
|---|---|
| `wiki页面契约-v1.md` | superseded（权威 = spec-v0） |
| `wiki知识体系完整方案-v1.md` / `wiki知识体系总体方案.md` | 失败模式 F1–F7 仍对照；阶段表以本文 + v3 为准 |
| `docs/业务系统知识库提取与构建指南-v1.md` 及 v1.4 增补 | 历史经验；与本文冲突则废弃 |
| skill `SKILL.md` 11 步 | **unit 包路径**；wiki 只复用其脚本与读码约束 |

---

## 1. 权威裁决表 + 按知识问题分源 + 证据 kind

### 1.1 文档 vs 代码冲突（必须当场记住）

| 冲突 | 裁决 |
|---|---|
| v2 §2.0 把 Step A 写在 B/C 之前；`pipeline.plan` 实际读取 `callgraph.yaml` | **执行序 ≠ 字母序**。先 B+C+E3（+ field-roles + 三方对账），再 baseline+enrich，再 A，再 D1/D2/E/F。字母名保留以对接代码注释 |
| v2 Step D 上下文含「既有 wiki」；`assemble_context` 只有四块 | **独立重提禁止读旧问数 wiki**。block⑤ 未实现，升格为硬禁令 |
| 技能 11 步 vs wiki 页面树 | wiki 主路径不跑 `knowledge-package submit` |
| 契约 11 种目录 vs 现语料 | **问数最小完备集** = table / enum / concept / process / caliber / rule；metric / pattern / scenario 有证据才建；query / source 默认不做 |
| 「库 > 代码 > 文档」vs 「代码是术语桥」 | **按知识问题分源**（下表），不是单一总分 |

### 1.2 按知识问题分源

| 知识问题 | 唯一权威 | 参照 | 冲突处理 |
|---|---|---|---|
| 表/字段是否存在、类型、可空、索引 | **E2 DB catalog** | Entity `@TableName` / `@TableField` | 不一致 → `FIELD_NOT_IN_DB` / 三方对账 `db_only`/`code_only`，以 DB 为准建页 |
| 实测值域 / TopK / 行数 | **E2 profile/sample** | 代码常量 | DB 有、代码无 → `ENUM_VALUE_NOT_IN_DB` 或 `db-enum-reconcile` REVIEW |
| 枚举 dictKey → 业务 label、状态名 | **E3 源码枚举/常量 + Javadoc/行内注释** | 需求用词 | **禁止 LLM 脑补 label** |
| Join / 写值 / 状态机 From→To | **Service/Mapper 实际读写 + 注释** | 需求流程 | 无 `code_path` 不得落 ground |
| 用户说法、同义/易混边界 | **需求用词 + 代码注释/API 文案** | — | 物理锚必须来自代码赋值/`.eq()` |
| 版本意图（「本期不处理」） | **需求文档** | — | 只进散文 `## 版本演进`；代码已实现则以代码落锚 |
| 怎么切单元 | **E1 调用图** | E0 路由文档 | E1 不做语义裁决 |

权威序压缩版：**E2 > E3（含注释）> E0.5 > E0**；E1 只管切分。

### 1.3 证据 kind（写入 `sources` / ground `evidence`）

| kind | 含义 | 例 |
|---|---|---|
| `database_profile` / `db_dist` | 库字段实际值/分布 | `cust_build_type` 98.8% `AGW_BUILD` |
| `database_schema` | DDL / catalog 列 | `db:db-catalog.yaml` |
| `code_path` | 读写证据 `文件:行号` | `CustCompanyInfoApplication.java:88` |
| `code_enum` | 枚举/常量类 + 注释 | `CustBuildTypeConstant.PC_BUILD` |
| `document_claim` / `reqdoc:<slug>` | 需求主张（最弱） | 未回证不得进 ground |
| `enrich:wiki-admin` | 程序 enrich 盖章 | 关系节/scope/行数 |

休眠表只允许 `database_schema`；出现 `code_path` 则与「休眠」矛盾，须重判。

---

## 2. 目录与文件清单

中间产物 **不进召回**。运行时只认 `wiki-pages/`（或独立重提的 `wiki-pages-v2/`）。

```
docs/wiki-knowledge/<system>/          # 例：pplatform
├── db/                                # E2
│   ├── db-catalog.yaml
│   ├── db-profile.yaml
│   └── db-sample.yaml
├── substrate/                         # E1 + E3（独立重提用 substrate-v2/）
│   ├── callgraph.yaml
│   ├── extract-catalog.yaml
│   ├── extract-enums.yaml
│   ├── extract-relationships.yaml
│   ├── field-roles.yaml
│   └── tmp/
│       ├── page-plan.yaml             # Step A 产物
│       ├── code-ignore.yaml           # 源码过滤（人固化）
│       ├── reqdoc-filter.yaml         # E0.5 白名单（人固化）
│       ├── table-reconcile.yaml       # 表级三方对账
│       ├── db-enum-reconcile.yaml     # 枚举值 db vs 代码
│       └── enum-unbound.yaml          # baseline 未绑字段的枚举
├── req-index/                         # E0.5 中间层（docx→md）；或指向 Test-wiki
└── wiki-pages/                        # 最终语料（独立重提：wiki-pages-v2/）
    ├── _index.md                      # 程序生成，勿手改
    ├── tables/ enums/ concepts/ processes/ calibers/ rules/
    └── .runs/<topic>/                 # _review_*.yaml _reconcile_*.yaml _done
```

过滤清单与对账 YAML 是**一等产物**，不是可选附录。Step A 只给 `ignore_suggestions`，人工写入 `tmp/` 后全管线共用 [`filters.py`](../../backend/apps/knowledge/wiki/filters.py)。

---

## 3. 端到端执行序（锁定）

字母名对接代码；**必须按下图顺序跑**。

```
过滤清单初值
  → B callgraph + C db + E3 catalog/enums/relationships + field-roles
  → 三方对账（table-reconcile / db-enum-reconcile）
  → baseline（tables + enums）
  → enrich（必跑）
  → Step A pipeline plan
  → 人补 page-plan + 固化 ignore/filter
  → Step D1/D2 → E → F（按 topic，断点 _done）
  → 若又跑过 baseline：再 enrich
  → lint / reviews / adjudicate（publish 按操作面，见 §14）
  → 仅独立重提：与旧 wiki 横向对比
```

Step A–B–C 低频固化（schema 指纹 + repo rev 驱动重跑）；Step D 才消耗 LLM。

---

## 4. 底稿阶段（B / C / E3 + field-roles + 三方对账）

### 4.1 输入

| 输入 | 说明 |
|---|---|
| Java 仓库 | Spring + MyBatis-Plus；分析只读文本，**禁止执行** mvn/gradle/npm |
| DB | 默认识别目标仓 Spring profile（pplatform：`application-qa2-local.properties`）；连不上则显式降级 |
| `repository_revision` | `git -C <repo> rev-parse HEAD`，写入底稿或提取日志 |

### 4.2 命令（在仓库根，使用 `backend/venv`）

```bash
REPO=/path/to/java-repo
SUB=docs/wiki-knowledge/<system>/substrate   # 独立重提改 substrate-v2
DB=docs/wiki-knowledge/<system>/db
PY=backend/venv/bin/python
SK=.cursor/skills/knowledge-extraction/scripts

# B — E1
$PY $SK/extract-callgraph.py "$REPO" -o $SUB/callgraph.yaml

# C — E2（连不上 DB：不要静默；本步失败则后续以 E3 建页并在页上标缺 db）
$PY $SK/extract-dbcatalog.py \
  --db-profile "$REPO/lowcode-pplatform-application/src/main/resources/application-qa2-local.properties" \
  --database lowcode_pplatform \
  --out-dir "$DB"

# E3
$PY $SK/extract-catalog.py "$REPO" -o $SUB/extract-catalog.yaml
$PY $SK/extract-enums.py "$REPO" -o $SUB/extract-enums.yaml
$PY $SK/extract-relationships.py "$REPO" -o $SUB/extract-relationships.yaml
$PY -m apps.knowledge.wiki.field_roles --repo "$REPO" --out $SUB/field-roles.yaml
```

`extract-catalog.py` 使用 `@TableName` + `@ApiModelProperty`（及 `@TableField` 覆盖列名）。  
`extract-enums.py` 扫 `*Enum` 的 `NAME("dictKey","显示名")`，以及 **interface / `*Constant` / `*Constants` / `constant(s)/` 包** 中的字符串（或 int）常量；label 取前置 Javadoc/`//`，无注释仍提取并标 `unlabeled`。setter 绑定认 `Enum|Constant|Constants`。**这份 YAML 只是基线**：写值点、字面量、`.name()` vs `getDictKey`、未使用常量都可以推翻它——LLM 必须 `enum_audit`。

### 4.3 产出文件

见 §2。底稿带 `generated_at` / 源 rev 的，重跑可覆盖；**不要**把 substrate 拷进 `wiki-pages/`。

### 4.4 三方对账（出门必做）

无独立 CLI 时用确定性比对生成 `substrate/tmp/table-reconcile.yaml`：

- `db_only`：在 `db-catalog` 不在代码 catalog（动态表名/他服务建表）→ Step D 确认
- `code_only`：代码有 DO、库无表 → 死代码/未部署，**不建 table 页**（`pipeline._load_db_tables`：库不存在即不建页）
- `dormant_confirmed`：callgraph `dormant_candidates` ∩（库有或库无）

`db-enum-reconcile.yaml`：profile TopK 值 ∉ 代码枚举 dictKey → `mismatches[]`（table/field/value）。ingest 会把该主题表的 mismatch 注入 D 上下文。

### 4.5 注释进入 E3（硬规则）

| 来源 | 用途 |
|---|---|
| `@ApiModelProperty` | 字段业务名 → table 页 `desc`、concept 别名候选 |
| 枚举第二个参数 / 常量字段 Javadoc/`//` | **enum label 的首选来源**（含 interface 常量）；无注释时机械提取标 unlabeled，由 LLM 按写值点补 |
| 方法/类 Javadoc、行内 `//` | 业务别名、易混说明 → `term_bridges.aliases` / `boundary`；**物理锚仍来自赋值与 `.eq()`** |

机械提取（`extract-*.yaml`）是底稿不是真值：实现若与声明不一致（死常量、字面量直写、`.name()` 而非 `getDictKey`、DTO 拷贝冒充 JOIN），以写值点 + DB TopK 为准，`enum_audit` / `relation_audit` 记录推翻。禁止用需求文档发明 label。

### 4.6 出门检查

- [ ] `callgraph.yaml` 有 `entry_points` 与 `per_entry`
- [ ] `db-catalog.yaml` 顶层 `database` 有值；或已记录 `DB_UNAVAILABLE`
- [ ] 三份 extract + `field-roles.yaml` 存在
- [ ] `table-reconcile.yaml` / `db-enum-reconcile.yaml` 已写
- [ ] HEAD 已钉死
- [ ] `ENUM_UNBOUND` 待 baseline 后记账

---

## 5. 基线页 + enrich 不变量

### 5.1 baseline

```bash
cd backend
venv/bin/python -m apps.knowledge.wiki.baseline \
  --substrate ../docs/wiki-knowledge/<system>/substrate \
  --db-dir ../docs/wiki-knowledge/<system>/db \
  --out ../docs/wiki-knowledge/<system>/wiki-pages
```

只生成 **tables + enums** 存在性真值页。slug = 物理表名 / dictKey。无代码 label 时 enum 页可以只有 values——**不许 LLM 补 label**。未绑定字段的枚举写入 `substrate/tmp/enum-unbound.yaml`。

休眠表：表页可存在，`inactive: true`，`fields` 为空。

### 5.2 enrich（baseline 后必跑）

```bash
backend/venv/bin/python scripts/wiki_admin.py enrich \
  --pages ../docs/wiki-knowledge/<system>/wiki-pages
```

确定性注入：`## 关联表`、断链补链、`scope.databases` 归一、行数、重建 `_index.md`。  
**不变量**：任何一次 `baseline` 整页重写都会抹掉关联节 → **必须再 enrich**。

`--force` 重建已有关联节；`--dry-run` 只列将改写的页。

### 5.3 出门检查

- [ ] 每个 db 表有对应 `tables/<name>.md`（`code_only` 除外）
- [ ] enum 页 slug = dictKey；label 可追溯到代码
- [ ] 表页含 enrich 的 `## 关联表`（有关系底稿时）
- [ ] `_index.md` 为程序生成

---

## 6. Step A 提取计划

### 6.1 命令

```bash
cd backend
venv/bin/python -m apps.knowledge.wiki.pipeline plan \
  --repo /path/to/java-repo \
  --substrate ../docs/wiki-knowledge/<system>/substrate \
  --db-dir ../docs/wiki-knowledge/<system>/db
```

一次 LLM：读 E0（见 §19）+ 入口/表反向索引。缺口 **重问一次**；仍缺则 `SystemExit`，人工补 `tmp/page-plan.yaml`。

### 6.2 JSON 契约（提示词真值）

```json
{
  "plan_units": [
    {
      "topic": "企业建档",
      "entries": ["CustCompanyInfoController", "OperCustFacade"],
      "tables": ["cust_company_info"],
      "duty": "一句话职责",
      "doc_refs": ["business/客户管理平台业务规则文档.md"]
    }
  ],
  "excluded_entries": [{"class": "ApiMockController", "reason": "Mock 无业务语义"}],
  "exclude_globs": ["*/dto/*"],
  "reqdoc_include": ["concepts/**"],
  "system_summary": "≤300字"
}
```

规则：入口覆盖率 100%（∈ `entries` 或 `excluded_entries`）；类名/表名只能来自输入；topic 用业务术语；休眠表可标 `(dormant)`。

`validate_plan` 缺口键：`missing_entries` / `unknown_entries` / `missing_tables` / `unknown_tables`。

写出：`substrate/tmp/page-plan.yaml`（含 `ignore_suggestions`）。

### 6.3 人闸（强制）

1. 抽检：每个高问数 topic 是否同时包含 **写入口（Controller/Application）与读入口（Provider/Facade/@DubboService）**。只写不读 = 域失败，改 plan 后重跑 A 或手改 YAML。
2. 把 `ignore_suggestions.exclude_globs` 合并进 `tmp/code-ignore.yaml`。
3. 把 `reqdoc_include` 合并进 `tmp/reqdoc-filter.yaml`（`include_only` 白名单）。
4. Mock/生成代码进 `excluded_entries`，不要塞进穿透。

### 6.4 出门检查

- [ ] `validate_plan` 空缺口或已人工闭环
- [ ] 双入口已写入相关 topic
- [ ] 两份 filter YAML 已固化（不是只存在于 plan 的 suggestions）

---

## 7. Step D 穿透

```bash
cd backend
venv/bin/python -m apps.knowledge.wiki.pipeline run \
  --repo /path/to/java-repo \
  --substrate ../docs/wiki-knowledge/<system>/substrate \
  --db-dir ../docs/wiki-knowledge/<system>/db \
  --out ../docs/wiki-knowledge/<system>/wiki-pages \
  --reqdoc-root ../docs/wiki-knowledge/<system>/req-index \
  [--only 企业建档,企业认证审核]
```

`--only` 逗号分隔 topic，**强制重跑**（忽略 `_done`）。无 `--only` 时跳过已有 `_done` 的单元。topic 名若含 `/`，`.runs` 目录写成 `-`。D2 若解析不到 `---FILE---` 会重试一次，并把分析/生成原文写入 `.runs/<topic>/_analysis.yaml`、`_generation.md`。

### 7.1 四块上下文与预算

`assemble_context` 实际组装（**无旧 wiki 块**）：

| 块 | 来源 | 预算 |
|---|---|---|
| ① `[系统文档]` | E0：`doc_refs` 全文节选，缺则路由索引 | `_E0_BUDGET` = 8000 字符 |
| ② `[需求文档]` | `ReqdocFilter` 后词法命中，最多 6 页 | `_REQDOC_BUDGET` = 6000 |
| ③ `[代码]` | 入口 `per_entry` **ring≤2** 结构性类型整文件 | `_TOKEN_BUDGET` = 400_000 字符 |
| ④ `[DB 实测]`+`[代码]底稿` | catalog/profile 切片 + 枚举 + db-enum mismatch | 见 `ingest._block_substrate` |

代码链优先级（同 ring 内）：Application → Controller → ServiceImpl → Service → Manager → DomainService → Dao → Mapper → DO。超长文件按方法体花括号切片。`CodeIgnore.should_scan` 为 false 的路径跳过。

**禁止**把旧 `wiki-pages/` 放进上下文或 `--out` 指向旧树做「就地生成」（独立重提见 §14）。

docx **不得**作为 `reqdoc_root`。先抽成 md 树（§19），再传入。

### 7.2 D1 分析 JSON

系统提示词要求输出（不要 Markdown 围栏）：

```json
{
  "field_semantics": [{"table","field","meaning","evidence":"db|code"}],
  "state_machines": [{"name","field",
     "states":[{"value","label","source":"code_enum|db_dist"}],
     "transitions":[{"from","event","to","evidence":"code_path:文件:行"}]}],
  "calibers": [{"name","predicate":"表.字段 = '值'","scope","evidence"}],
  "term_bridges": [{"term","aliases":[],"maps_to","also_confused_with":[],
     "adjudication":"boundary|synonym","boundary"}],
  "rules": [{"name","content","impact","field_targets":[],"evidence"}],
  "reqdoc_claims": [{"claim","code_status":"confirmed|refuted|uncovered",
     "code_evidence":"文件:行","action":"anchor|prose_only|review"}]
}
```

铁律：

1. 值/字段/表名字面只来自 `[DB][代码]`；需求不能发明结构。
2. 需求主张三通道：代码证实 → `anchor`（双源 evidence）；有出入 → `prose_only`（以代码落块，差异写散文）；无覆盖 → `review`（不落 ground）。
3. 状态值优先 db 分布；代码枚举缺失时 `source: db_dist`。
4. 状态机 transition 必须有真实代码位置。

### 7.3 D2 FILE / REVIEW 协议

每个页面：

```
---FILE: concepts/认证状态.md ---
---
type: concept
title: ...
page_key: ...
domain: ...
status: draft
...
---
正文
```ground:<kind>
...
```
---END FILE---
```

路径首段 ∈ `{tables,enums,concepts,processes,calibers,rules,metrics,patterns}`，且 = `type`。

REVIEW：

```
---REVIEW: missing-page | 标题---
描述
---END REVIEW---
```

类型：`contradiction | duplicate | missing-page | stale | confirm | suggestion`。

规则摘要：每页每种 ground 至多一个；concept **不写** `ground:concept`（锚点只在 frontmatter）；禁止发明锚点值。

### 7.4 Agent 读码规程（wiki 化，不跳去 skill）

**双入口**：同一业务主题必须沿 **管理端写入口** 与 **业务端读入口** 各穿一遍并交叉核对。只穿写入会导致漏掉消费端触发的保存/版本/幂等（历史：漏读 Application 首版 → 丢失版本号递增）。plan 的 `entries` 必须覆盖两条链。

**三类代码事实**（关系提取）：

1. 读流转：上一张表查询结果作为下一张表条件。
2. 写流转：先父后子，`child.setParentId(parent.getId())`。
3. 跨方法参数传播：形参来自上层，正则抓 `setXxx(a.getYyy())` 会漏。

**写值点清单**（穿透时逐点记录，再推导，不要事后重读猜）：

`字段 + 值类型（常量/枚举/参数传播）+ 条件（无条件/分支）+ 所属流程`

先剔除噪声：`deleted` / `version` / 审计字段的固定写值。然后分类：

| 形态 | 落页 |
|---|---|
| 固定写值（无条件+常量） | 状态机初始 / rule 默认值 |
| 条件写值（分支写不同枚举） | `rules` |
| 状态递进（同字段多流程不同枚举） | `process` transitions |
| 分阶段写入（同表不同字段集合） | 多 process 的读写效果 + 互链 |

**关系硬约束（wiki）**：

- 关系默认 `proposed`，禁止因「代码里写了」标 confirmed。
- `ref_*` 必须有读/写/join；全仓零引用则剔除。目标字段经 `.eq()`/JOIN 确证是 `code` 还是 `id`。
- 租户隔离字段不是关联；同名字段拷贝不是关联；反规范化标 `derived_from`，不标直连。
- n:n / 共享键 → 表页关联说明为 SHARED_KEY，不得教规划器直接 JOIN 彼此。
- enrich 目前把关系写成散文 `## 关联表`，**不**生成 `ground:relation`（已知债 §17）。语义页可用 wikilink 指向表页。

**注释**：类/方法/字段注释中的业务说法进 `aliases` 与散文；label 仍只许枚举/常量注释。

**域失败条件**：只穿一条入口；concept 无锚；枚举 label 脑补；口径无 `code_path`；近似语义三信号未裁决。

---

## 8. Step E 对账码表与丢块/拒写

`reconcile_page` 对 ground vs E2∪E3，并校验 `code_path` 文件存在、行号范围内。

| code | 范围 | 上层动作 |
|---|---|---|
| `PAGE_CONTRACT_FAILED` | 整页 | **拒写** |
| `TABLE_NOT_IN_DB` | 块 `anchor` | **丢该 ground 块**，散文保留 |
| `FIELD_NOT_IN_DB` | 块 | 丢块 |
| `FIELD_MALFORMED` | 块 | 丢块 |
| `ENUM_VALUE_NOT_IN_DB` | 块 | 丢块 |
| `EVIDENCE_FILE_MISSING` | 块 | 丢块 |
| `EVIDENCE_LINE_OUT_OF_RANGE` | 块 | 丢块 |

全部 findings 写入 `.runs/<topic>/_reconcile_<hash>.yaml`。

`DUPLICATE_GROUND_BLOCK`：保留首个同 kind+键，删后续。

---

## 9. Step F 写入、合并、`_index`、`.runs`

1. `_normalize_page`：若 LLM 误写 `ground:concept`，把 `maps_to` / `field_targets` / `adjudication` / `also_confused_with` 提升到 frontmatter。
2. 同 `page_key` 已有基线 table 页 → `merge_same_key_page`：**不得整页覆盖**。`fields` 以基线全量为底，语义只补空 `desc`；散文取语义页；合并后 `status: draft`。
3. 写入 `--out/<FILE 路径>`。
4. REVIEW 块 → `.runs/<topic>/_review_*.yaml`。
5. 单元成功后写 `_done`。
6. 全部单元结束后 `rebuild_index`。

断点续跑依赖 `_done`。要重跑某 topic：`--only` 或删该目录 `_done`。

---

## 10. 门禁：lint / reviews / adjudicate / publish / verify

```bash
PAGES=../docs/wiki-knowledge/<system>/wiki-pages
PY=backend/venv/bin/python

$PY scripts/wiki_admin.py lint --pages $PAGES
$PY scripts/wiki_admin.py reviews --pages $PAGES
$PY scripts/wiki_admin.py adjudicate --id <slug> --action skip|create-page --pages $PAGES
$PY scripts/wiki_admin.py publish --page tables/cust_company_info.md --pages $PAGES
$PY scripts/wiki_admin.py verify --pages $PAGES
```

**lint 硬错误**（`wiki_admin._ERROR_CODES`，publish 阻断）：

`GROUND_PARSE_FAILED` `DUPLICATE_GROUND_BLOCK` `CONCEPT_UNANCHORED` `REF_TARGET_MISSING` `ENUM_GENERIC_COLUMN`  
+ §8 全部 reconcile 码。

**软/咨询**（不进硬错误集，仍应治理）：`BROKEN_LINK` `NO_OUTLINKS` `TERM_UNADJUDICATED` `SEMANTIC_PAGE_UNLINKED_TABLE` `TABLE_PAGE_NO_RELATIONS` 及 catalog 门控的 `TYPE_FAMILY_MISMATCH` 等。

**人闸**：每个 topic 抽检 `_review` / `_reconcile`；`adjudicate` 的 `create-page` 只标记意图，**不会自动写新页**（需按 REVIEW 手写或重跑 D）。`skip` 归档为 `_done_*`。

**publish**：当前实现只 lint **单页**，不是引用闭包全检（§17）。独立重提默认识别为 draft 语料，**不要**对 v2 树批量 publish 到生产，除非对比报告已裁决切流。

**verify**：关系列是否在 catalog、行数、scope 形态。

**覆盖验收**（无 `coverage.yaml` 子命令）：

```
COVERAGE_GAP ≡ db 活跃表 − tables/ 页
```

外加：callgraph 可达但无语义页的主题；`CONCEPT_UNANCHORED`；enum 有业务值无 concept 术语桥。技术/日志表可排除（对账 `hint` + 无问数场景），**有入口的活跃表不得当 excluded 掩盖缺口**。

---

## 11. 页类型提取细则

### 11.1 问数最小完备集（每主题应力争）

| type | 来源 | 必填锚点 | 出门 | 坏样本 |
|---|---|---|---|---|
| `table` | baseline(E2∪E3) + enrich | `ground:table` 物理名、fields 来自 catalog | slug=表名 | 幻觉表；用语义 id 当表名 |
| `enum` | baseline(E3+profile) | `ground:enum` dictKey；label 来自代码注释 | slug=dictKey | LLM 猜「平台录入」；一页塞多 dictKey |
| `concept` | D1 `term_bridges` | frontmatter `maps_to` 或 `field_targets`；`adjudication` | 无 ground 块 | 无锚；多页同 title 不互链 |
| `process` | 写值点串成的状态机 | `ground:process` states + transitions 带 `code_path` | 与 enum 值一致 | 用 `create_time` 冒充业务状态 |
| `caliber` | mapper WHERE / 分支谓词 | `ground:caliber` filters；`code_path` | 近义口径互链边界 | 无 field、无证据的「有效」空话 |
| `rule` | 锁/幂等/默认值/条件写值 | `ground:rule` + `field_targets` | 可执行 | 无字段的治理口号 |

### 11.2 可选（有证据才建，禁止空壳）

| type | 何时建 |
|---|---|
| `metric` | 有 COUNT/SUM/AVG + grain 证据 |
| `pattern` | 有可复现成功 SQL（回填或 mapper 范例） |
| `scenario` | 需要跨页导航闭包时 |

`query` / `source`：本规范默认不做。

### 11.3 一物理实体一页

一表一页、一 dictKey 一页。其余页只引用物理键 `表.字段` / `表.字段=值`。跨目录允许同 slug（`concepts/pay_status` vs `enums/pay_status`），wikilink 歧义须写 `[[enums/pay_status]]`。

---

## 12. 术语桥专项（同义 / 近义 / 易混 / 多页争锚）

D1 字段：`term_bridges[{term, aliases, maps_to, also_confused_with, adjudication, boundary}]`。

**检测是结构触发的，不靠扫词**，三信号必查：

1. 同表 ≥2 个字典字段，取值/显示名语义空间重叠（认证方式 vs 录入方式都像在回答「企业怎么进来的」）。
2. `extract-enums.yaml` 的 `ambiguous_fields`（一字段绑多枚举类）与 `convention_mismatch`。
3. 同域跨表近似编码/状态字段（`auth-status` vs `auth-state`；`cust_status` vs `cust_build_status` vs `check_status`）。

每个命中必须裁决为二者之一：

| adjudication | 含义 | 写法 |
|---|---|---|
| `boundary` | 不同问题 | `also_confused_with` + `boundary` 写清各自答什么、混用后果；两边互链 |
| `synonym` | 同一语义或冗余粒度 | `maps_to` 指向权威物理键；别名进 `aliases`；禁止第二页再争同一锚而不声明同义 |

**物理锚**只许 `表.字段` 或 `表.字段=值`，证据来自代码读写，不是需求字面。  
需求有、代码无落库 → `reqdoc_claims.action=review` 或散文「未落地」。  
代码有、需求无显式命名 → 仍建 concept，散文注明「需求未显式命名」。

**禁止**：无互链的重复 `title`（如四个「企业角色」各 maps_to 不同字段却都叫企业角色且不声明边界）。应拆成带边界的多页，或一页 synonym + 分字段说明。

实证疫苗：`cust_build_type`：`PC_BUILD` = 客户录入，`AGW_BUILD` = 平台录入（源码常量注释）。用户说「平台录入」不得映射到 PC_BUILD。

---

## 13. 质量门槛 + 失败模式 F1–F7

机械 lint 全绿 ≠ 语义到位。每个活跃表相关的语义页应同时满足：

1. 字段/枚举 payload 真实（catalog / enums.yaml / 注释），无退化（description 抄回字段名、全 varchar、有枚举不填）。
2. 至少 1 条 `code_path`（非仅 `database_schema`），状态机/口径尤其如此。
3. 非 `count` + `enable=Y` 模板。
4. 写值语义已按 §7.4 分类落位。
5. 近似语义三信号已按 §12 裁决，业务别名已进 concept。
6. concept 有锚；口径/规则有 field 指向。

| # | 问数失败 | 对应页 | 提取源 | 验收 |
|---|---|---|---|---|
| F1 | 枚举值↔说法鸿沟 | enum + concept | 代码注释 + 术语桥 | label 可回证；`maps_to` 对得上 catalog |
| F2 | 状态谓词错误 | process | 写值点 | 谓词字段 ∈ 状态字段，不是时间列顶替 |
| F3 | 口径静默选边 | caliber | WHERE + 边界 | 近义口径有 boundary 互链 |
| F4 | JOIN 猜测 | table 关联节 | relationships + enrich | 端点在 catalog；租户字段不当 JOIN |
| F5 | SQL 范式 | pattern（可选） | 成功 SQL | 本轮可不建；有则与 caliber 自洽 |
| F6 | 表/字段不可见 | table | catalog | `COVERAGE_GAP`=0（活跃表） |
| F7 | 选错主表 | concept/scenario + 表页 | 入口职责 | topic.duty 与主表一致 |

---

## 14. 三条操作面

### 14.1 独立重提（本战役默认）

目标：从权威源生成**另一棵**语料树，生成期零读旧 wiki。

```
docs/wiki-knowledge/pplatform/
  wiki-pages/          # 旧版冻结，只读对比
  wiki-pages-v2/       # 新树
  substrate-v2/
  req-index/
```

- `--substrate` / `--out` 全部指向 v2。
- `--reqdoc-root` 指向 `req-index` 或 Test-wiki 的 `wiki/`，**不要**指向旧问数 `wiki-pages`。
- 工作集禁止打开旧页面正文 / 旧 `.runs` 裁决当生成输入。
- 跑完全部 D–F 与 lint 后，才允许打开旧树做 §14.1 对比（见战役交付 `wiki-v2-vs-v1-comparison.md`）。
- **不要**把运行时 `KNOWLEDGE_WIKI_PAGES_DIRS` 切到 v2，直到对比报告经人确认。

### 14.2 增量（`update.py`）

```bash
backend/venv/bin/python -m apps.knowledge.wiki.update \
  --repo ... --substrate ... [--reqdoc-root ...] [--dry-run]
```

产出变更报告（代码指纹 / 需求新页 / db 指纹）。**不会自动** `pipeline run`。按报告 `--only` 重跑单元。入口清单相对 plan 有新增类 → 必须重新 `plan`，不能只重跑旧 topic（增量盲区）。

### 14.3 日常发布

对**已确认**的语料树：`lint` 硬错误清零 → 抽检 reviews → `publish` 单页 draft→published。召回默认只消费 published（运行时另有 draft 临时开关时以代码为准）。

---

## 15. CLI 速查（含 v2 隔离）

以下均在仓库根；`<SYS>=pplatform`，独立重提把 `substrate`/`wiki-pages` 换成 `*-v2`。

```bash
REPO=/Users/fanjunwei/IdeaProjects/pplatform-web
ROOT=docs/wiki-knowledge/pplatform
SUB=$ROOT/substrate-v2
DB=$ROOT/db
OUT=$ROOT/wiki-pages-v2
REQ=$ROOT/req-index
PY=backend/venv/bin/python
SK=.cursor/skills/knowledge-extraction/scripts

$PY $SK/extract-callgraph.py "$REPO" -o $SUB/callgraph.yaml
$PY $SK/extract-dbcatalog.py --db-profile "$REPO/lowcode-pplatform-application/src/main/resources/application-qa2-local.properties" --out-dir "$DB"
$PY $SK/extract-catalog.py "$REPO" -o $SUB/extract-catalog.yaml
$PY $SK/extract-enums.py "$REPO" -o $SUB/extract-enums.yaml
$PY $SK/extract-relationships.py "$REPO" -o $SUB/extract-relationships.yaml
cd backend && $PY -m apps.knowledge.wiki.field_roles --repo "$REPO" --out ../$SUB/field-roles.yaml

cd backend && $PY -m apps.knowledge.wiki.baseline --substrate ../$SUB --db-dir ../$DB --out ../$OUT
cd .. && $PY scripts/wiki_admin.py enrich --pages $OUT --substrate $SUB --db-dir $DB --force

cd backend && $PY -m apps.knowledge.wiki.pipeline plan --repo "$REPO" --substrate ../$SUB --db-dir ../$DB
cd backend && $PY -m apps.knowledge.wiki.pipeline run --repo "$REPO" --substrate ../$SUB --db-dir ../$DB --out ../$OUT --reqdoc-root ../$REQ
# LLM 跑完后：盖章 page_key、回填表基线；枚举页与 LLM 合并（基线键保全，不整页覆盖）
cd backend && $PY -m apps.knowledge.wiki.pipeline repair --out ../$OUT --substrate ../$SUB --db-dir ../$DB
cd .. && $PY scripts/wiki_admin.py enrich --pages $OUT --substrate $SUB --db-dir $DB --force

$PY scripts/wiki_admin.py lint --pages $OUT
$PY scripts/wiki_admin.py reviews --pages $OUT
$PY scripts/wiki_admin.py verify --pages $OUT
$PY -m apps.knowledge.wiki.update --repo "$REPO" --substrate ../$SUB --dry-run
```

`pipeline` 子命令：`plan` / `run` / `repair`。`update` 在 `wiki.update`。`extract-enums` 会写 `java_name`/`stored_as`（`.name()` vs `getDictKey`），并收录 interface/`*Constants`；`extract-relationships` 会写同名拷贝 `SHARED_KEY`。二者都只是基线，LLM `enum_audit`/`relation_audit` 可推翻。`pipeline run` 对已有枚举页做 `merge_enum_page`（键保全 + note/stored_as）。

---

## 16. 阶段检查表

复制到工作笔记打勾。

**底稿**

- [ ] HEAD 已记录
- [ ] E1/E2/E3/field-roles 文件齐全
- [ ] E2 失败已显式记录（非静默）
- [ ] table-reconcile / db-enum-reconcile 已写
- [ ] 过滤 YAML 初值存在

**基线**

- [ ] baseline 已跑
- [ ] enrich 已跑（rebuild 后再次）
- [ ] `enum-unbound.yaml` 已阅

**计划**

- [ ] plan 无 validate 缺口或已手补
- [ ] 双入口已覆盖高问数域
- [ ] filter 已从 suggestions 固化

**穿透（每 topic）**

- [ ] 写+读都穿了
- [ ] 写值点已分类
- [ ] 术语三信号已裁决
- [ ] `_done` 存在；reconcile/review 已抽检

**门禁**

- [ ] lint 硬错误 = 0 或已挂账
- [ ] COVERAGE_GAP（活跃表）已知
- [ ] 独立重提：对比报告已出，**未**自动切流

---

## 17. 已知实现债与本轮不做

| 债 | 现实 | 本轮 |
|---|---|---|
| ingest 块⑤ 既有 wiki | 未组装 | 独立重提当硬禁令，不修代码 |
| `pipeline update` 子命令 | 只有 `wiki.update` 报告 | 不自动重跑 |
| baseline `ground:relation` | 无；enrich 散文关联节 | 不改 baseline |
| publish 引用闭包 | 只 lint 单页 | 独立重提不批量 publish |
| spec-v0 §6 部分码 | `RELATION_*` `PATTERN_*` `ORPHAN_PAGE` `STALE_VS_CATALOG` `COVERAGE_GAP` 未进 `lint_page` | 覆盖用手算 §10 |
| 回填面 | 未落地 | 不做 |
| `knowledge-package` | 旁路 | 不跑 submit |
| E0 路径写死 pplatform | `lowcode-pplatform-common/.dev-standards/knowledge` | 缺则 A 认知退化，须在附录标明 |

---

## 18. 禁止项

- 用旧问数 wiki 正文/旧 reconcile 裁决当生成输入（独立重提）
- 把 docx 直接传给 `--reqdoc-root`
- 文档或模型发明表/字段/枚举值
- 脑补 enum label（尤其 `PC_BUILD`/`AGW_BUILD`）
- 静默覆盖冲突（必须 REVIEW 或对比报告）
- 整页覆盖 baseline 表字段全集
- 复制 `count` + `enable=Y` 模板当语义页
- 多页争同一 `maps_to` 却不互链、不声明 synonym/boundary
- 只穿透写入口
- 执行目标仓库构建工具
- 口令写入底稿或提交 git
- 未确认对比报告就把运行时语料根切到 v2

---

## 19. 附录：pplatform 路径

| 项 | 路径 / 值 |
|---|---|
| 源码 | `/Users/fanjunwei/IdeaProjects/pplatform-web` |
| 钉 rev | 开提时 `git -C ... rev-parse HEAD`（历史底稿曾钉 `ee434954e`） |
| E0 | `{repo}/lowcode-pplatform-common/.dev-standards/knowledge/`（`service-routing-index.md` + `business/` `codemap/` `service/`） |
| 缺 E0 | Step A 几乎无系统认知，plan 质量下降，须人工加大抽检 |
| 需求原件 | `/Users/fanjunwei/Desktop/需求文档`（V1.0–V1.35 docx + 专题 xlsx） |
| E0.5 接入 | **原件 → `docs/wiki-knowledge/pplatform/req-index/` md**（或已有 Test-wiki 的 `wiki/` 目录）。ingest 只扫 `*.md` |
| 需求默认优先切片 | V1.30–V1.35 + `非供应商角色建档梳理.xlsx` + `非自主认证建档&变更.docx` + `产融平台数据迁移涉及的改造需求V1.2.docx` + SSO 设计；更早版本按域检索补洞 |
| Test-wiki（若可用） | 历史设计路径 `/Users/fanjunwei/workspace/Test-wiki`；`reqdoc-filter.yaml` 按相对 `wiki/` 的 glob |
| DB profile | `{repo}/lowcode-pplatform-application/src/main/resources/application-qa2-local.properties` |
| 物理库名 | `lowcode_pplatform`（`scope.databases`） |
| 独立重提目录 | `substrate-v2/` `wiki-pages-v2/` `req-index/` |
| 旧语料 | `docs/wiki-knowledge/pplatform/wiki-pages/`（冻结） |
| 项目内文档 | `{repo}/docs/`、`AGENTS.md`、相关 `.cursor/skills` → 可摘入 `req-index/project-docs/` |

**E0.5 原件抽取最低要求**：每份 docx 变成 `req-index/concepts/<slug>.md` 或 `req-index/entities/` 下带少量 frontmatter 的 md，正文含版本号与业务规则原句。`reqdoc-filter.yaml` 的 `include_only` 必须覆盖这些相对路径（独立索引可用 `concepts/**` + `entities/**`）。xlsx 抽成表格 md（角色清单、状态对照）。

**对比报告条目格式**（独立重提收尾）：

```yaml
id: CMP-ENT-ROLE-01
severity: P0|P1|P2
kind: CONFLICT|V1_ONLY|V2_ONLY|SYN_IMPROVED|OMISSION_V2
v1_pages: []
v2_pages: []
evidence: {db, code_comment, req}
verdict_proposal: prefer_v2|prefer_v1|merge|needs_human
```

切流 / 合并旧独有真值：**人确认后**才做，不在提取 runbook 自动步骤内。
