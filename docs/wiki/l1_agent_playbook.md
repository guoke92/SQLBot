# L1 Coding Agent 走读实操指南

> 第一步只产 `_raw/l1_intermediate/` 下的离散 YAML。不要直接写 Wiki Markdown，不要调用 `repair.py`，不要拿旧 `wiki-pages*` 当生成上下文。Schema：[l1_intermediate.md](l1_intermediate.md)。

目标：把「入口 → 落库」的事实交给第二步程序去做聚合、catalog 防幻觉和 9 类页面渲染。

## 0. 开工前

1. 打开 L0 语料：`<l0>/tables/`、`<l0>/dicts/`、`<l0>/_raw/catalog.yaml`。
2. 物理名 **只许** 出现在 catalog 里的表/列。列名用库名（`certification_no`），不要用 Java 驼峰或文档口头名。
3. 选一个业务域（目录名 ascii：`cust`、`tenant`、`ca_fee`）。一次会话只写这一个域。
4. 输出根：`<l0>/_raw/l1_intermediate/code/<domain>/` 与 `.../docs/`。
5. 证据格式：
   - 源码：`code_path:FileName.java:行号`（文件名足够；第二步会在 `--code-root` 下解析）
   - 库：`database_schema:库.表.列` / `database_profile:表.列`
   - 文档：`document_claim:文件名#章节`

没有 `code_path` 就不要自称 confirmed。第二步也不会升权。

## 1. 源码走读 SOP

按 **一个业务操作** 追，不要扫包名。

```
HTTP Controller
  → Application / Facade
  → Service / Domain
  → Dao / Mapper.xml / lambdaQuery
  → DO @TableName
```

### 1.1 找入口

- Spring `@RequestMapping` / `@PostMapping` 在 `*Controller.java`
- 记方法名、行号、调用的 Application 方法
- 同一入口如果分支很多，拆成多份 `traces/<op>.trace.yaml`，每份一个主路径

### 1.2 追到表

- `@TableName("cust_company_info")` 或 Mapper XML 的 `FROM` / `JOIN`
- `lambdaQuery().eq(DO::getX, …)` → 列名转 snake_case 后必须能在 catalog 对上
- JOIN 只记 **等值** 且代码里真实出现的 `left = right`。码对码合法，但 `join_role: business_code`；id/PK 才是 `identity`
- 常见坑：L0 可能把 `cust_company_info.id` 接到 `ref_*` 列；代码实际是 `code = ref_cust_project_rel_cust_company_info`。以代码为准，写成新边，并在 `note` 里说明。第二步会把共享同一 FK 列的 L0 `id` 边标 `disputed`，并写 `JOIN_CONFLICT` REVIEW。跨类型等值（varchar 存 Long）可加 `cast:`

### 1.3 默认过滤与共写

有效集：列表接口 / XML `WHERE enable = 'Y'`、主数据 `data_type = '1'`、状态枚举。写成 `default_filter.predicate`（可执行 SQL 片段，带表前缀）。

共写：同一 `lambdaUpdate().set(...).set(...)` 或同一 `@Transactional` 里一起 `set` 的列 → `written_with_groups`。

### 1.4 状态机

只有生命周期列才写 process。同一字典绑多列 → 每列各自一份。

对每个 `from → event → to`：

- `from`/`to` 必须是枚举 `dictKey`（不是 displayName）
- 至少一条 `code_path` 指向 `setCustBuildStatus` / `updateStatus` / XML `SET`
- 副作用（另表置位）写在 `side_effects`

分类字典不要编假 From→To。

### 1.5 字典中文

优先级：**枚举第二参数 / `displayName` > 常量 Javadoc > `@ApiModelProperty`「值 中文」**。

- 没有中文就不写 label
- 不要用列注释覆盖代码 label（L0 注释是 proposed；L1 代码胜）
- Y/N 列不要合并进共享 `enable` 页以外的释义

### 1.6 口径与规则

- 口径：列表/统计 SQL 里反复出现的谓词（例：生效企业 = `BUILD_SUCCESS` ∧ `EFFECT` ∧ `enable='Y'` ∧ `data_type='1'`）
- 规则：唯一性校验、必填拒绝保存。`impact: write_constraint` 不自动改问数 SQL
- 跨表谓词必须能指出 JOIN 边（`using_relations: [{left, right}]`）

### 1.7 本域交付清单

`code/<domain>/` 至少：

| 文件 | 有则写 |
|---|---|
| `table_enhancements.yaml` | 默认过滤 / 共写 |
| `relations_dicts.yaml` | 实证 JOIN + 代码 label |
| `processes.yaml` | 生命周期列 |
| `calibers_rules.yaml` | 可执行口径 + 写约束 |
| `scenarios.yaml` 或 trace 内 `scenario` | hub + shared 选表 |

不要输出 `tables/*.md`。

### 1.8 覆盖门禁（漏提的根因就在这里）

只追「建档主路径」会漏卫星表、旁路操作、字典 label。一域收工前必须做完下面六项，并跑 `wiki_extract l1-coverage --prefix <domain>`。

1. **操作清单，不只主提交。** 从 `*Controller` / `*Application` 列出 freeze / unfreeze / disable / change / invite / Policy / `Assert.isTrue` / `checkBeforeSave`。每个公开写库方法至少一份 `traces/<op>.trace.yaml`（或在已有 process 里写清 `from→to` + 副作用）。
2. **catalog 同前缀表。** `cust_*` 等前缀表要么 enhancement + JOIN/口径，要么在某条 trace 的 `gaps:` 写「走读过、无问数语义」。禁止默默跳过。
3. **FK 样列扫一遍。** 已 enhancement 的表上，`ref_*` / `*_id`（排除 `id`/`create_by`）每条要么 `confirmed_relations`，要么注明「代码未等值使用」。`lambdaUpdate` 按 name 匹配不是 EQUI_JOIN，写成 process/caliber，不要假装 JOIN。
4. **L0 keep 字典补 label。** 已 enhancement 表上的 `dicts/表__字段`：有 `displayName`/常量注释就写 `dict_labels`；没有中文就不编。L0 脏值（带引号的码、`CORE_ADMIN`、人员 `status=N`）保持 proposed、不给 label。
5. **负向事实。** 操作 A 不写列 B 时写进 rule/process `note`（例：企业冻结不写 `cust_person_info.enable`）。问数最容易把旁路当成主路径。
6. **文档覆盖见 §2。** 覆盖命令列出 req-index 文件数；agent 按域标签走读，禁止只读 V1.0 规格说明书。

## 2. 文档走读 SOP

原件根：`/Users/fanjunwei/Desktop/需求文档`（docx/xlsx，按版本号迭代）。工作副本：`docs/wiki-knowledge/pplatform/req-index/`（已抽 Markdown）。第二步 `evidence` 仍写 `document_claim:文件名#章节`。

ingest **不能直吃 docx**。req-index 比 Desktop 旧时先刷新抽取，再写 IR。不要把 2GB 原文拷进 git。

### 2.1 版本叠加

- **当前逻辑**：现网源码 > 最新版本需求（目前 Desktop 到 V1.35）> 更早版本。
- **叫法/别名**：旧版仍可进 `aliases`；被后一版废掉的流程只进 `*_display.yaml`（`recall: false`）或 concept 里写「V1.x 曾…，现码是…」。
- **冲突**：文档主张与代码赋值不一致 → 仍写 concept，`evidence` 双源，第二步 `DOC_UNBRIDGED` 或正文写清「代码为准」。禁止用旧需求覆盖 `CustCompanyCaPolicy` 这类现网强制规则。
- V1.0 规格说明书只解决「认证方式 vs 建档通道」这类基础用词；管理员变更、冻结留痕、签章限制在 V1.17 / V1.19 / V1.26 等增量里。

### 2.2 单篇怎么走

1. 抽出业务名词与别名。
2. **先找源码桥梁**：文档用词是否等于某 `dictKey` / 某赋值。有桥梁 → `maps_to` 可以等第二步 confirmed；没桥梁 → 仍写 concept，`evidence: document_claim:…`，第二步打 `DOC_UNBRIDGED`。
3. 易混成对：`also_confused_with` + `adjudication: boundary|synonym`，正文写清「A 列答 X，B 列答 Y」。
4. 版本史、排期、人员分工 → `*_display.yaml`，`recall: false`。
5. 禁止把文档时间线写进 ground。

`平台录入` 这类口语句：必须核常量注释。pplatform 里 `PC_BUILD` 注释是「客户录入」，`AGW_BUILD` 才是「平台录入」。不要按字面猜。

## 3. 会话纪律（防截断）

- 一域一会话；大域再按操作拆 trace
- 每个文件写完就落盘，不要等「全部想完再输出」
- 禁止 `... 其余略`、禁止省略 values
- 发现 catalog 没有的表/列：停笔，记进 trace `gaps:`，不要编

## 4. 增量

代码只改了客户模块：只重写 `code/cust/`。第二步全量 `rglob` 合并，2 秒内重渲。

## 5. 验收（Agent 自检）

- [ ] 所有 `表.字段` 能在 `catalog.yaml` 找到
- [ ] 每条将升权的主张都有真实 `code_path` 且行号落在文件内
- [ ] JOIN 端点不是租户列 / `create_time` / 裸 `id` 对无语义列
- [ ] process 钉的是状态列，transition 的码来自枚举 dictKey
- [ ] concept 有唯一 `maps_to`；易混有裁决
- [ ] 没有 Wiki 页面、没有 `status: published`
- [ ] `l1-coverage --prefix <domain>` 的 missing_tables / unconfirmed_fks 要么已补 IR，要么写入 trace `gaps:`
- [ ] 本域相关 req-index 概念已抽术语；与代码冲突的已标明代码为准
