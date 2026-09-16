# 问数 Wiki 提取

> 权威：[README.md](README.md) · 对象图见 [architecture.md](architecture.md) · 语法见 [pages.md](pages.md)
>
> **ingest / lint / promote**：把库 / 源码 / 文档填进那张对象图。不定义召回。不跑 `knowledge-package submit`。附录命令不是契约。

## 1. 目标

填结构页（table/enum）+ 叠语义页（concept/caliber/…），不是平行跑三条管道再拼接。

库给出存在与候选；源码是含义、JOIN、**字段簇**、共写、label 的唯一落地；文档只提供叫法。无代码验证不得 `confirmed`。文档钉不到源码 → 语义名称匹配 + REVIEW。

ingest 只产 **draft + REVIEW + `_log`**。`published`/`retired` 只由 promote 写。独立重提禁止把旧问数 wiki 当生成上下文。对话回流是又一次 ingest，不是第五档输入。

## 2. 印证顺序（有机，不是 ETL 拼接）

```
文档用词 ──有源码桥梁──► 表.字段（可 confirmed）
        └──没有──────► 语义匹配 + REVIEW
版本史 ──► 展示区
源码读写/共写/字段簇/label/生命周期  ←印证→  catalog / PK / 身份束 / profile
冲突 → REVIEW；一致且 code_path → 主张可 confirmed（页仍是 draft，直到 promote）
```

实例值进 `value_index`，不进 wiki 页。

档位（库连不上则失败）：

| 档 | 输入 | 产品用词 → 库 | 编不出 |
|---|---|---|---|
| L0 | 库 | 列名/注释 | 认证 JOIN、生命周期、代码 label、有证据的字段簇、共写 |
| L0+文档 | 库+文档 | 语义匹配 | 全部 REVIEW |
| L1 | 库+源码 | 注释/API/写值 | 文档叫法可能不全 |
| L1 全量 | 三者 | **先源码桥梁**，否则语义+REVIEW | — |

有源码时：库侧关系/共写候选必须用代码验。过 = confirmed；否 = DERIVED/丢弃；未验 = proposed + REVIEW。

分源：库赢存在与 PK/实测；代码赢 JOIN/label/**字段簇**/流转；文档赢叫法与时间线（时间线只进展示区）。

## 3. 四操作（编译侧）

| 操作 | 做 |
|---|---|
| ingest | 读 raw（+ 增量时 published）；写 draft/patch + REVIEW + `_log`。一条源可改多页 |
| lint | published∪draft；只写 REVIEW/stale |
| promote | 结构 error=0 且 error 级 REVIEW 已清 → `published`/`retired`；bump generation |
| query | 见 [runtime.md](runtime.md)。好答案是下次 ingest 的 raw |

增量合并规则见 [pages.md](pages.md) §8。独立重提用新树；旧树只允许 lint 之后对比。

## 4. 按对象填，不按脚本字母

**① table / enum（必选，脚本）**  
catalog 列全集、`primary_key`、`name_anchors`（只点列）、`grain` 初稿（无代码则 proposed）、身份束关系全部 `proposed`（id/code 才倾向当键，name 倾向拷贝）、profile → `value_index`。`common` 簇可按列名启发式（id/enable/时间戳/code）。其余簇先用前缀提名，再由 **LLM 按注释/取值做语义分组与近义列 REVIEW**（仍是 proposed，证据只有 `database_schema`，不是 `code_path`）。L0 枚举：低基数先提名，**LLM 只 keep 封闭代码集**；人名/租户/密码/实例名单降为 `value_index` 或丢弃。无代码 label。休眠表 `inactive`，可省略 PK/grain/`default_filter`。

**② 源码地图（有仓库，`recall: false`）**  
调用切片、枚举 label、setter/mapper、同事务写入 → `written_with`、**字段簇**（同一 VO/form/resultMap/前缀/写入组）、`default_filter` 证据。用代码验 ① 的关系。按 topic（批次，不是 scenario）加深语义页。

**场景怎么选出簇：** 看该问法在代码里实际读写了哪些列 → 映射到列所属簇 → `clusters` 取并集（`common` 不必写）。不要把本批次问到的列抄成 `window`。

簇按代码模块切，不按本批次问了哪些列切。confirmed EQUI_JOIN 写在 FK 表页。process / concept 边界同上。

**③ 文档叠加（必须已有 ①）**  
全量档走源码桥梁；否则语义匹配 + REVIEW。无锚新词不进向量。

**④ lint → promote**  
L0 不要求 scenario。L1 出门见 §6。

角色：脚本不许把候选写成认证 JOIN，不许 ingest 写 published。Agent 维护源码地图、起草口径散文，不许整仓自由翻。人只做 REVIEW 与 promote，不许手补 published。

## 5. 争议写在对象上

同一 enum 页里 confirmed 与 disputed 共存。REVIEW 指向 `belong/page_key#claim_path`。不要整页 draft、不要塞展示区、不要只留一侧。提取仍出**库全量**；勾选是运行时透镜。

## 6. 出门物

**所有档位：** 活跃 table（列全集、PK、名称锚、`common` 簇；grain 无代码则 proposed）、身份束 proposed 关系、`value_index`。L0 **不要**把 proposed 关系当可 JOIN；出门后问数预期为单表。

**L1 另要：** 代码 label 的 enum；**有代码证据的字段簇**；scenario（`clusters` 引用表上的簇，不镜像 `scenes`）；concept（含易混裁决）；钉同一列的 process；可执行 caliber；有证据的 `default_filter` / `written_with`；metric 仅当有聚合证据。pattern 默认不建，来自回流。source 页默认不建。

| 对象 | 必须 | 不要 |
|---|---|---|
| table | 物理表名；列全集；PK；名称锚；字段簇（分区） | 幻觉表；实例名当枚举；字段上倒挂 `scenes`；在 rule 上再写一份 default_filter |
| enum | 一 dictKey；label 来自代码 | LLM 猜中文 |
| concept | `maps_to` 唯一锚 | 无锚；两页争同一锚却不声明 synonym/boundary |
| caliber | 可执行 predicate；跨表则 `using_relations` | 一值一页，除非反复被问的命名集合 |
| metric | caliber + `aggregation` + `grain_table` | 自由文本 grain；第二套 filter |
| rule | 写约束等；`field_targets` | 把 default_filter / 共写做成 rule |
| process | 同一列；transition 有 `code_path` | 分类字典假 From→To |
| scenario | hub+clusters+shared；簇 key 在表上 | 包名当场景；topic 当 scenario；列清单当窗；再写 grain |
| relation | EQUI_JOIN 才进图；无 `code_path` 不得 confirmed | 同名拷贝当 JOIN |
| pattern | SQL 过 JOIN 图；confirmed 须有证据 | 未审 SQL 当 few-shot；独立 query 类型 |

## 7. 写页纪律

问数页给规划器，不是代码说明书，也不是 runbook。

- **簇不是切表，也不是按问法切列。** 表页列全集。按代码模块 / 关联性分区：`common`（id/enable/时间戳/有则 code）、账户（账号/户名/开户行）、认证、签约… 表页用 `### 簇名` 列全名，禁止 `…`。字段只标 `cluster`，不写 `scenes`。
- **场景只选簇。** 同一张表可被多场景引用；场景写 `clusters:`，不写 `window: [列…]`。未归簇列留表页，点名再展开。
- **租户列**留表、放入 `common` 或独立 `tenant` 簇，**不作 JOIN 端点**。
- **grain / 名称锚 / 默认过滤 / 共写 / 簇** 都写在表上。grain 跟 PK+代码如何按行处理。`written_with` 跟同一 setter/事务；与簇冲突时不拆开账户列。
- **字典列要能进 SQL。** 有中文则有 enum；label 代码优先于列注释。Y/N 列释义不要回填进共享 `enable` 页。
- **只有生命周期列写 process。** 同一字典绑多列 → 每列各自 process。这条是生成约定，不要写进正文。
- **label 只跟代码：** `displayName` / 枚举第二参数 > Javadoc/`//` > `@ApiModelProperty`「值 中文」。没有中文就不编。
- **声明 ≠ 写入路径 ≠ 库分布。** 未落地、脏值、跨字典同名写成事实。禁止生成黑话（「不进本机」「本预览不另开页」）。边界写成「A 列答 X，B 列答 Y」。
- **版本史、排期进展示区；争议留召回面；ground 禁止进展示区。**

## 8. 术语桥

结构触发，不靠扫词：同表 ≥2 字典语义重叠；一字段多枚举；同域跨表近似状态。命中必须 `boundary`（互链）或 `synonym`（`maps_to` 权威键，别名进 `aliases`）。

物理锚只许 `表.字段` / `dictKey.VALUE`，证据来自代码赋值 / `.eq()`。需求有代码无 → REVIEW 或展示「未落地」。代码有需求未命名 → 仍建 concept。

实证：`cust_build_type.PC_BUILD` 是客户录入，不是用户口中的「平台录入」。

## 9. 失败模式 → 对象图上的洞

| | 问数失败 | 缺的对象 | 验收 |
|---|---|---|---|
| F1 | 说法对不上值 | enum+concept | `maps_to` 可回证 |
| F2 | 状态谓词用错列 | process | 钉的是状态列 |
| F3 | 口径静默选边 | caliber boundary | 近义已互链 |
| F4 | JOIN 猜测 | table.relation | 无 code_path 非 confirmed |
| F5 | few-shot 带坏 JOIN | pattern | SQL ⊆ 图 |
| F6 | 缺列/缺表 | table | 活跃表无缺口+有 PK |
| F7 | 炸行 / 选错主档 | table.grain + scenario + metric | 继承同一张表的 grain |
| F8 | 金额时间拆开 | `written_with` | 同笔写入同组 |
| F9 | 漏有效集 | table.`default_filter` | 谓词可执行 |
| F10 | 账户列被问法拆散 | table.clusters | 账号/户名/开户行同簇；场景只选簇 |

机械 lint 全绿 ≠ 语义到位：活跃表相关语义页要有真实 payload；状态机/口径至少一条 `code_path`；不是 `count`+`enable=Y` 模板。

## 10. 目录与证据

```
docs/wiki-knowledge/<system>/
├── db/                 # catalog / profile
├── substrate/          # 扫描与对账（独立重提换新树）
├── req-index/          # 文档中间层
├── wiki-pages/         # 出门页（draft 与 published 同树）
│   ├── tables/ enums/ concepts/ processes/
│   ├── calibers/ metrics/ rules/ patterns/ scenarios/
│   ├── _index.md
│   └── _log.md
└── .runs/<batch>/      # reviews.yaml、patch
```

中间产物与过滤清单不进召回。语料切流是运维，不是契约。

`evidence` 前缀与 [pages.md](pages.md) 相同。substrate 里的 `code_enum` 落到页上改写成 `code_path:`。无 `code_path` 的 EQUI_JOIN / `written_with` / process transition / 枚举 label / 非前缀猜测的簇 不得 `confirmed`。

`value_index` 与 wiki 同时编译：键 `(table, column)`，来源 profile TopK ∪ 字典实例，随勾选过滤，**不是** wiki 页。catalog 指纹变化 → lint `STALE_VS_CATALOG`，按档位重跑 ①②③，不手改 published。

## 11. 回流

成功 SQL / 澄清选择 → ingest 成 draft `pattern`（`confidence: proposed`）。可选执行后把记录写入 `evidence`。lint 过 JOIN 图，REVIEW 通过再 promote。不要 `queries/` 目录。

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
