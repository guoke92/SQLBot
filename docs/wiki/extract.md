# 问数 Wiki 提取

> 权威：[README.md](README.md) · 对象图见 [architecture.md](architecture.md) · 语法见 [pages.md](pages.md)
>
> **ingest / lint / promote**：把库 / 源码 / 文档填进那张对象图。不定义召回。不跑 `knowledge-package submit`。附录命令不是契约。

## 1. 目标

填结构页（table/dict）+ 叠语义页（concept/caliber/…），不是平行跑三条管道再拼接。

库给出存在与候选；源码是含义、JOIN、共写、label 的唯一落地；文档只提供叫法。无代码验证不得 `confirmed`。文档钉不到源码 → 语义名称匹配 + REVIEW。

ingest 只产 **draft + REVIEW + `_log`**。`published`/`retired` 只由 promote 写。独立重提禁止把旧问数 wiki 当生成上下文。对话回流是又一次 ingest，不是第五档输入。

pplatform 需求原件在 `/Users/fanjunwei/Desktop/需求文档`（V1.0 规格说明书 + V1.3–V1.35 增量 docx）。L1 文档走读用 `docs/wiki-knowledge/pplatform/req-index/` 的 Markdown 抽取件；**后一版 + 现网代码**赢当前逻辑，旧版只留别名或 `recall: false` 展示。docx 不能当 `evidence` 二进制进库。覆盖门禁见 [l1_agent_playbook.md](l1_agent_playbook.md) §1.8 / §2。

## 2. 印证顺序（有机，不是 ETL 拼接）

```
文档用词 ──有源码桥梁──► 表.字段（可 confirmed）
        └──没有──────► 语义匹配 + REVIEW
版本史 ──► 展示区
源码读写/共写/label/生命周期  ←印证→  catalog / PK / 身份束 / profile
冲突 → REVIEW；一致且 code_path → 主张可 confirmed（页仍是 draft，直到 promote）
```

实例值进 `instance_index.yaml`，不进 wiki 页。

档位（库连不上则失败）：

| 档 | 输入 | 产品用词 → 库 | 编不出 |
|---|---|---|---|
| L0 | 库 | 列名/注释 | 认证 JOIN、生命周期、代码 label、共写 |
| L0+文档 | 库+文档 | 语义匹配 | 全部 REVIEW |
| L1 | 库+源码 | 注释/API/写值 | 文档叫法可能不全 |
| L1 全量 | 三者 | **先源码桥梁**，否则语义+REVIEW | — |

有源码时：库侧关系/共写候选必须用代码验。过 = confirmed；否 = DERIVED/丢弃；未验 = proposed + REVIEW。

分源：库赢存在与 PK/实测；代码赢 JOIN/label/流转；文档赢叫法与时间线（时间线只进展示区）。

## 3. 四操作（编译侧）

| 操作 | 做 |
|---|---|
| ingest | 读 raw（+ 增量时 published）；写 draft/patch + REVIEW + `_log`。一条源可改多页 |
| lint | published∪draft；只写 REVIEW/stale |
| promote | 结构 error=0 且 error 级 REVIEW 已清 → `published`/`retired`；bump generation |
| query | 见 [runtime.md](runtime.md)。好答案是下次 ingest 的 raw |

增量合并规则见 [pages.md](pages.md) §8。独立重提用新树；旧树只允许 lint 之后对比。

## 4. 按对象填，不按脚本字母

**① table / dict（必选，脚本）**  
catalog 列全集、`primary_key`、`name_anchors`（只点列：`name`/`code`/`title`/`*_name`；已作 JOIN `right` 的列剔除）、`grain` 初稿（无代码则套话 + 不逐表 REVIEW）、身份束关系全部 `proposed` 且 **候选边全留**（id 为主键边 `join_role=identity`；`code` / `product_code` / `platform_product_code` 等码对码为合法 `EQUI_JOIN`，`join_role=business_code`，同父表已有主键边时 `priority=secondary`。表族缩写列如 `rule_info_id`→`funding_rule_info`、以及 `ref_本表_对端表` 也提名。纯 DB **不标主引用**）。L0 JOIN **三层**（仍全部 proposed，无 `code_path` 不得 confirmed；包含率不是新 relation type）：① 列名启发式提名并写 `name_evidence`；② `_raw/overlap.yaml` 值域包含探测——**每条启发式边强制复核**，未解析列有界补漏；不拿裸 `id` / `create_time` / `update_time` / `req_time` / date·datetime 当重合端点；争议带扩 topK + 正反 `IN`；bigint/int 与 varchar 引用视为可兼容（Java Long→String 常规）；③ LLM 初审与有界补边**同时**吃 `name_evidence` + overlap（未探测标 `not_probed`），不得删边、不得标主引用。边的 `likely` 必须值域契合 **且** 列名/注释有关联语义；仅值域契合保留边，`authenticity=unknown`。低基数 profile（`distinct <= 32`）走 **dict_triage**（`dict_keep | dict_hold | drop`）；业务标识/名称列另采 `_raw/profile_instance.yaml` 走 **instance_index**（无基数上限，TopK；排除 PII、`*_id`、UUID/哈希/JSON 串）。L0 字典：低基数先入候选池，再 **LLM 初判 → 机械检查 → 机械与 LLM 不一致或测库单值则 LLM 复核**；`dict_keep`=明确代码集初审通过，`dict_hold`=证据不足保留待人工，`drop`=明确不是字典；**测库单值须区分不全码表与测库污染，允许 drop**，禁止一律 hold。实例清单与字典分轨，不共用四档 verdict；信用代码/公司名进 `instance_index.yaml`，不进 `dicts/`。字典页 `page_key` 用 `表__字段`（不要点号、不要单下划线、不要 `::`）；物理列仍是 `表.字段`。`label` 仅当列注释能解析出「码→中文」才写（`trust: proposed`，`evidence: database_schema`）；注释没有映射则省略，禁止无注释脑补。表页对字典列写 `[[dicts/表__字段]]`，字段 YAML 用紧凑键 `type`/`desc`，`dict` 列举码值、有中文则平行 `label`，不写 dict 页文件名；JOIN 块仍只写在 FK 页，但**两端表页都写** `[[tables/对端]]`。字典页回链表页。`inactive` 纯 DB 不置位（留给源码/文档证明休眠）。emit 必须落 `_raw/catalog.yaml` + `profile.yaml` + `profile_instance.yaml` + `overlap.yaml` + `llm_judge.yaml`，页面 relation 带 authenticity 分组。

**② 源码地图（有仓库，`recall: false`）**  
调用切片、字典 label、setter/mapper、同事务写入 → `written_with`、`default_filter` 证据。用代码验 ① 的关系。按 topic（批次，不是 scenario）加深语义页。

**场景怎么选表：** 看该问法在代码里实际读写了哪些表 → scenario `hubs` / `shared`。不要把本批次问到的列抄成 `window`。

confirmed EQUI_JOIN 写在 FK 表页。process / concept 边界同上。

**③ 文档叠加（必须已有 ①）**  
全量档走源码桥梁；否则语义匹配 + REVIEW。无锚新词不进向量。

**④ lint → promote**  
L0 不要求 scenario。L1 出门见 §6。

角色：脚本不许把候选写成认证 JOIN，不许 ingest 写 published。Agent 维护源码地图、起草口径散文，不许整仓自由翻。人只做 REVIEW 与 promote，不许手补 published。

## 5. 争议写在对象上

同一 dict 页里 confirmed 与 disputed 共存。REVIEW 指向 `belong/page_key#claim_path`。不要整页 draft、不要塞展示区、不要只留一侧。提取仍出**库全量**；勾选是运行时透镜。

## 6. 出门物

**所有档位：** 活跃 table（列全集、PK、名称锚；grain 无代码则 proposed）、身份束 proposed 关系、`dicts/`、`instance_index.yaml`。L0 **不要**把 proposed 关系当可 JOIN；出门后问数预期为单表。

**L1 另要：** 代码 label 的 dict；scenario（选表，不镜像 `scenes`）；concept（含易混裁决 + Catalog Summary）；钉同一列的 process；可执行 caliber；有证据的 `default_filter` / `written_with`；metric 仅当有聚合证据。pattern 默认不建，来自回流。source 页默认不建。

| 对象 | 必须 | 不要 |
|---|---|---|
| table | 物理表名；列全集；PK；名称锚 | 幻觉表；实例名当字典；字段上倒挂 `scenes`；在 rule 上再写一份 default_filter |
| dict | 一 dictKey；认证 label 来自代码 | 无注释脑补中文；把注释派生 label 写成 confirmed；把高基数实例名单写成 dict 页 |
| concept | `maps_to` 唯一锚 | 无锚；两页争同一锚却不声明 synonym/boundary |
| caliber | 可执行 predicate；跨表则 `using_relations` | 一值一页，除非反复被问的命名集合 |
| metric | caliber + `aggregation` + `grain_table` | 自由文本 grain；第二套 filter |
| rule | 写约束等；`field_targets` | 把 default_filter / 共写做成 rule |
| process | 同一列；transition 有 `code_path` | 分类字典假 From→To |
| scenario | hub+shared 选表 | 包名当场景；topic 当 scenario；列清单当窗；再写 grain |
| relation | EQUI_JOIN 才进图；无 `code_path` 不得 confirmed；码边 `join_role=business_code`，有主键边时 `priority=secondary` | 把码边当主键边；禁止码对码 EQUI_JOIN |
| pattern | SQL 过 JOIN 图；confirmed 须有证据 | 未审 SQL 当 few-shot；独立 query 类型 |

## 7. 写页纪律

问数页给规划器，不是代码说明书，也不是 runbook。

- **表页列全集，场景只选表。** 同一张表可被多场景引用；场景写 `hubs`/`shared`，不写 `window: [列…]`。全库骨架见 `concepts/catalog_summary`（每表一行，不把列注释铺进骨架）。
- **语义页必须有正文页面链接。** 图扩展只认 `[[wikilink]]`，不认 `related:`。L1 从物理锚 / hubs / 易混词生成 `## 页面链接`（`[[belong/page_key]]`）；孤表回链 Catalog Summary。
- **租户列**留表，**不作 JOIN 端点**。
- **grain / 名称锚 / 默认过滤 / 共写** 都写在表上。grain 跟 PK+代码如何按行处理。`written_with` 跟同一 setter/事务。
- **字典列要能进 SQL。** 有中文则有 dict 页；label 代码优先于列注释。Y/N 列释义不要回填进共享 `enable` 页。
- **只有生命周期列写 process。** 同一字典绑多列 → 每列各自 process。这条是生成约定，不要写进正文。
- **认证 label 只跟代码：** `displayName` / 枚举第二参数 > Javadoc/`//` > `@ApiModelProperty`「值 中文」。L0 允许从**列注释**解析码→中文（仍 `proposed`）；注释解析不出就不写。L1 代码 label 覆盖注释。没有中文就不编。
- **声明 ≠ 写入路径 ≠ 库分布。** 未落地、脏值、跨字典同名写成事实。禁止生成黑话（「不进本机」「本预览不另开页」）。边界写成「A 列答 X，B 列答 Y」。
- **版本史、排期进展示区；争议留召回面；ground 禁止进展示区。**

## 8. 术语桥

结构触发，不靠扫词：同表 ≥2 字典语义重叠；一字段多字典；同域跨表近似状态。命中必须 `boundary`（互链）或 `synonym`（`maps_to` 权威键，别名进 `aliases`）。

物理锚只许 `表.字段` / `dictKey.VALUE`，证据来自代码赋值 / `.eq()`。需求有代码无 → REVIEW 或展示「未落地」。代码有需求未命名 → 仍建 concept。

实证：`cust_build_type.PC_BUILD` 是客户录入，不是用户口中的「平台录入」。

## 9. 失败模式 → 对象图上的洞

| | 问数失败 | 缺的对象 | 验收 |
|---|---|---|---|
| F1 | 说法对不上值 | dict+concept | `maps_to` 可回证 |
| F2 | 状态谓词用错列 | process | 钉的是状态列 |
| F3 | 口径静默选边 | caliber boundary | 近义已互链 |
| F4 | JOIN 猜测 | table.relation | 无 code_path 非 confirmed |
| F5 | few-shot 带坏 JOIN | pattern | SQL ⊆ 图 |
| F6 | 缺列/缺表 | table | 活跃表无缺口+有 PK |
| F7 | 炸行 / 选错主档 | table.grain + scenario + metric | 继承同一张表的 grain |
| F8 | 金额时间拆开 | `written_with` | 同笔写入同组 |
| F9 | 漏有效集 | table.`default_filter` | 谓词可执行 |
| F10 | 找不到表/漏表 | Catalog Summary | 表名 + 表注释 + 主要字段可召回 |

机械 lint 全绿 ≠ 语义到位：活跃表相关语义页要有真实 payload；状态机/口径至少一条 `code_path`；不是 `count`+`enable=Y` 模板。

## 10. 目录与证据

```
docs/wiki-knowledge/<system>/
├── db/                 # catalog / profile
├── substrate/          # 扫描与对账（独立重提换新树）
├── req-index/          # 文档中间层
├── wiki-pages/         # 出门页（draft 与 published 同树）
│   ├── tables/ dicts/ concepts/ processes/
│   ├── calibers/ metrics/ rules/ patterns/ scenarios/
│   ├── _index.md
│   └── _log.md
└── .runs/<batch>/      # reviews.yaml、patch
```

中间产物与过滤清单不进召回。语料切流是运维，不是契约。L0 脚本另写仓库根的 `instance_index.yaml`（实例 TopK，不是 wiki 页），以及 `_raw/` 五件套（catalog / profile / profile_instance / overlap / llm_judge）。

`evidence` 前缀与 [pages.md](pages.md) 相同。substrate 里的 `code_enum` 落到页上改写成 `code_path:`。无 `code_path` 的 EQUI_JOIN / `written_with` / process transition / 字典 label 不得 `confirmed`。

`instance_index.yaml` 与 wiki 同时编译：键 `(table, column)`，来源 `_raw/profile_instance.yaml` TopK，随勾选过滤，**不是** wiki 页。catalog 指纹变化 → lint `STALE_VS_CATALOG`，按档位重跑 ①②③，不手改 published。

## 11. 回流

成功 SQL / 澄清选择 → ingest 成 draft `pattern`（`trust: proposed`）。可选执行后把记录写入 `evidence`。lint 过 JOIN 图，REVIEW 通过再 promote。不要 `queries/` 目录。

## 12. 成功标准

活跃表有列全集、PK、名称锚；hub 有 grain。label 零脑补。无代码验证的关系全是 proposed/REVIEW。ingest 产出 `published` 条数为 0。无桥梁的文档锚全是 REVIEW。wiki 页无实例名。

## 附录 A. 参考命令（非契约）

L0 库侧出门用独立工具 [`tools/wiki_extract/`](../../tools/wiki_extract/README.md)（`WIKI_EXTRACT_DSN` → `docs/wiki-knowledge/<system>/l0/`）。下面的 `extract-dbcatalog.py` 不是 L0 契约，勿再当出门路径。

只读扫描目标仓库文本，禁止跑 mvn/gradle。序：扫描 → 库侧合同 → 源码印证 → 文档叠加 → lint → promote。模块名以代码为准。

```bash
REPO=/path/to/java-repo
ROOT=docs/wiki-knowledge/<system>
SUB=$ROOT/substrate
DB=$ROOT/db
OUT=$ROOT/wiki-pages
SK=.cursor/skills/knowledge-extraction/scripts
PY=backend/venv/bin/python

$PY $SK/extract-callgraph.py "$REPO" -o $SUB/callgraph.yaml
$PY $SK/extract-dbcatalog.py --db-profile <spring-profile> --out-dir "$DB"
$PY $SK/extract-catalog.py "$REPO" -o $SUB/extract-catalog.yaml
$PY $SK/extract-enums.py "$REPO" -o $SUB/extract-enums.yaml
$PY $SK/extract-relationships.py "$REPO" -o $SUB/extract-relationships.yaml
$PY scripts/wiki_admin.py lint --pages $OUT
$PY scripts/wiki_admin.py reviews --pages $OUT
```

## 附录 B. L1 源码+文档（非契约）

Coding Agent 按 [l1_agent_playbook.md](l1_agent_playbook.md) 把走读事实写成 `_raw/l1_intermediate/` 小文件（Schema：[l1_intermediate.md](l1_intermediate.md)）。平台程序聚合、catalog 防幻觉、升权并渲染 9 类 draft 页：

```bash
backend/venv/bin/python -m tools.wiki_extract l1 \
  --l0 docs/wiki/v2 \
  --out docs/wiki/v3 \
  --code-root /path/to/pplatform-web
```

不写 `wiki-pages*`，不改运行时目录。ingest 仍不得写 `published`。
