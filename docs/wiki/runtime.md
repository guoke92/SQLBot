# 问数 Wiki 运行时

> 权威：[README.md](README.md) · 对象图见 [architecture.md](architecture.md) · 语法见 [pages.md](pages.md)
>
> **query 操作**：规划器怎么读 published wiki。公式与法律在架构里；本文只写请求上的顺序与投影。实现未追上以契约为准。

## 1. 一次 query

```
published 页树
    → 召回语义出门（scenario/concept/caliber/rule/process/metric + 命中的 pattern）
      缺概念时再召回结构（table/dict/relation）
    → ∩ 勾选 ∩ 权限 ∩ ¬disabled
    → 主张打标
    → 按命中表的 PK/名称锚/锚点列/共写同伴投影 prompt；Catalog Summary 作全库骨架；default_filter 出默认 WHERE
    → 门禁：JOIN 图 / grain / fan-out
    → 澄清卡或 SQL
    → 好答案只进下一次 ingest
```

未绑定 → 物理目录，直到第一次编译。已绑定缺表页 → 不规划该表（P6b），禁止 catalog 直渲。业务段未命中 → 主链路仍跑（P6a），JOIN/grain 门禁仍在。

目录 markdown 只是导入源。运行权威 = published 快照（`corpus_generation`）。

## 2. 可见性（三轴在请求上求值）

顺序不能收成一个开关：先 published，再勾选/权限，再读 `confidence`，再按场景裁列。

| 结果 | 行为 |
|---|---|
| `available` | 可召回；schema 只投已选列 |
| `selection_excluded` | 静默移出；问题只依赖它们 → `selection_excluded` 澄清 |
| `permission_denied` | 脱敏拒绝；用户话术无物理名 |
| `page_disabled` | 同 excluded（运维开关，不写页） |

- 表未勾选：表页不进 schema；只锚该表的语义页本 DS 不可用；图扩展不得经过该表。
- 字段未勾选：表页仍在，丢掉该列；只依赖该列的口径本轮不可执行。
- 再勾选下一请求生效，不 ingest、不 bump 语料 generation。
- `inactive` ≠ 未勾选：默认不进工作集，问到仍只读 wiki。
- `proposed`/`disputed` 只要锚还在勾选集内，就不是 excluded。

权限在勾选之后裁子图。勾选变更不重嵌向量。锚点/发布变更才 `corpus_generation += 1`；权限矩阵变更才 `permission_generation += 1`。

## 3. 召回

返回渲染文本（直拼提示词）+ 命中清单（`page_key`、`claim_path`、`confidence`）。只切召回面。

主路径是 RRF（词法 × 向量）+ wikilink 一跳扩展，不是把全书塞进上下文。`_index`/`_log`/`source`/`recall: false` 不进规划硬路径。draft/retired 不进。

```
切块原子（标题层级 + ground 围栏不切断）；recall=false 的块不嵌入
超采 top_k×3（≥30）→ RRF：Σ 1/(60+rank) → 页分 = top + min(0.3×Σ尾, 1−top)
种子 = 直接命中前 20；business 图配额 ceil(limit×(0.30−0.15×向量覆盖率)) clamp[1, limit−1]
围栏：published ∧ 库名交集 ∧ anchors∩勾选；扩展只在掩膜子图
```

`business` 窗口大；`physical` 窗口小、图扩展降为候选。命中的 `scenarios/*` 必须进入本轮 `present_pages`（或等价），否则选表不生效。渲染必须能区分 confirmed/proposed/disputed。

pattern：仅 published ∧ confirmed 可作为 few-shot。

## 4. 门禁 = 用结构页，不另查 catalog

**JOIN。** 从已召回/闭包的表页收边（FK 端那一页，对端不重复），再 ∩ 勾选。生成的等值 JOIN 必须是子图上的路径。`proposed`/`SHARED_KEY`/`DERIVED` 不当边。L0 `authenticity=likely` 仍是 proposed，不得当 confirmed 边。n:n 只走中间表。多路径且 caliber/metric 未 `using_relations` → `multiple_join_paths`。pattern 的边从 SQL 抽取后走同一张图。L0 图为空 → 只许单表。

**粒度。** 聚合必须能指到某张表的 `grain`（metric 经 `grain_table` 继承）。无 grain → `missing_grain`。fan-out 拒绝。

**WHERE。** 表 `default_filter` 且 confirmed → 默认 AND；用户明确推翻则记录。`rule.query_constraint` 只召回、不自动 AND。

**投影。** prompt 用架构公式（Catalog Summary 主要字段 ∪ 场景所选表的 PK/名称锚 ∪ 锚点列 ∪ written_with ∪ JOIN 端点）。SQL 列的法律是 **存在∩许可**（wiki fields ∩ 勾选），不是 prompt 子集——未提示到的列，只要页上有且已勾选，仍允许出现在 SQL。禁止把字段上的 `scenes` 当投影输入。

**值。** 固定字典取值走 dict 页解析映射；自然语言实例定位走 `instance_index.yaml`（键 `(table, column)`，随勾选过滤）。

**场景命中。** scenario 页被召回（或澄清指定）后写入 `present_pages`，选表才生效。只命中 table 页 ≠ 命中了某个 scenario。

## 5. 澄清

触发器字段：`reason`（架构封闭枚举）、`claim_path`、选项。投影到已有 `ClarificationCard`：`why`←`reason`，`fields`←锚。`disputed` / 多路径不得 `recommended` 当默认。`schema_page_missing` 允许凑不齐两个物理锚选项。选择 → ingest，不写 published。

## 6. 对象怎么进规划器

按架构 §1 的图用：table/dict 给 schema 与 JOIN 图；Catalog Summary 给全库骨架；concept 桥说法；caliber/metric/process/scenario/rule 给谓词与选表；pattern 给认证 SQL。实例定位用 `instance_index`，不入 wiki 树。禁止 catalog 补列、编 label、把 Java 包当场景、把 draft pattern 当 few-shot、把 `written_with` 当 JOIN、按问法给字段打 `scenes`。

## 7. 成功标准

JOIN ⊆ 掩膜后 confirmed 图；grain 能指回表；未勾选/无权不漏出；disputed 必澄清且无静默默认；P6a/P6b 成立；第二次规划不翻 raw。
