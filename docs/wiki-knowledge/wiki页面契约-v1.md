# Wiki 页面契约 v1

> **状态：已被取代（superseded）。** 权威契约 = [`docs/wiki页面契约-spec-v0.md`](../wiki页面契约-spec-v0.md)
> （v0 在锚点块语法、页面身份规则、写入管线、lint 码表上全面优于本稿，评审采纳）。
> 本文保留作设计过程记录；Python 消费实现已对齐 v0（`backend/apps/knowledge/wiki/contract.py`）。
> 与 v0 的差异决议：锚点块改单围栏 ```ground:kind；表/枚举页 slug=物理名、业务页保留 CJK；
> 多租户字段推迟阶段二（V0 靠 project-per-DS + 页面可选 scope 声明）。

## 1. 页面骨架

```markdown
---
page_key: cust-company-build-type        # 必填，^[a-z0-9][a-z0-9-]*$，全局唯一
title: 建档录入方式                        # 必填，业务语言标题（中文）
aliases: [平台录入, PC端录入, 网关录入]      # 召回词法路的匹配面，建议 2~8 个
domain: 企业建档                           # 必填，分类/聚类依据
type: enum                                # 必填：enum|table|concept|caliber|process
oid: 1                                    # 必填，工作区隔离
scope:                                    # 必填，可见性围栏依据（物理库名）
  databases: [lowcode_pplatform]        # 物理库名（非环境 ds_id）
sources:                                  # 必填，溯源（代码摄取 = repo:path@rev）
  - repo:pplatform-web@8f3a2c1:src/main/resources/mapper/CustCompanyInfoMapper.xml
refs:                                     # 过期检测依据（lint: stale）
  schema_fingerprints: ["74855b61..."]
status: published                         # draft → in_review → published（recall 只取 published）
version: 3                                # 乐观锁（LLM 一触多页并发写）
updated: 2026-08-29
---

## 概述
（自由散文区——LLM 善写善维护：业务背景、易混淆点、常见误用）

<!-- ground:enum -->
```yaml
enum: cust_company_info.cust_build_type
values:
  PC_BUILD:  {label: 平台录入, note: 企业经平台PC端录入建档}
  AGW_BUILD: {label: 网关录入, note: 网关渠道自动建档}
contrast_with: identify-style
```
<!-- /ground -->

## 关联
- [[identify-style|认证方式]]（易混淆：认证方式≠录入方式）
- [[company-build-process|企业建档流程]]
```

## 2. 锚点块（严格格式，发布时确定性解析）

标记语法：`<!-- ground:<kind> -->` 与 `<!-- /ground -->` 之间包一个 ```yaml 围栏。
切块时锚点块是**原子块**（永不切断，含标记行）。

| kind | 必填字段 | 发布门禁校验 |
|---|---|---|
| `enum` | `enum`（表.字段）、`values`（键→{label,note}） | 表/字段存在于 catalog；枚举键 ⊆ catalog 枚举；不一致=**拒绝发布** |
| `table` | `table`、`row_semantic` | 表存在（catalog）；scope 内可见 |
| `field` | `table`、`field`、`semantic` | 字段存在 |
| `relation` | `a`、`b`（表.字段）、`kind`、`cardinality` | 两端存在；kind ∈ 类型族（equi_join/hierarchy/bridge…） |
| `caliber` | `name`、`definition`、`filters` | filters 可被 sqlglot 轻解析 |
| `rule` | `rule_id`、`statement`、`scope` | scope 引用存在 |
| `process` | `states[]`、`transitions[]` | 状态键与本页或其他页 enum 锚点一致 |

解析失败 = 拒绝发布（进 REVIEW 队列，附错误详情）。**不存在静默降级。**

## 3. Wikilink 约定

- 语法 `[[page-key]]` 或 `[[page-key|alias]]`；
- 目标归一化：去 `.md`/`.markdown`、去 `#锚点`、strip、小写；
- 每页**至少一条出链**（lint `no-outlinks`）；
- 解析别名注册 4 类：page_key、title、aliases、（预留）路径——图扩展邻接表与缺页判定均基于此。

## 4. REVIEW 块（生产时同步产出）

```
---REVIEW: missing-page | 平台录入的审核规则---
（描述 + 预生成检索查询 + 建议动作）
---END REVIEW---
```

类型：`contradiction | duplicate | missing-page | stale | confirm | suggestion`。
ingest / lint / 回填三处共用此机制——**生产与审核是同一次 LLM 调用的两个输出**。

## 5. Lint 规则清单

**结构 lint（确定性，= 发布门禁）**
- `slug-invalid`：page_key 不合规范
- `anchor-schema`：锚点块字段缺失/类型错误
- `anchor-ref-missing`：锚点引用的表/字段不在 catalog
- `enum-mismatch`：枚举键与 catalog 枚举集不一致
- `broken-link`：wikilink 目标不可解析
- `no-outlinks`：零出链

**语义 lint（LLM 持续循环，物化进 REVIEW 队列）**
- `contradiction`：页间冲突声明
- `stale`：`refs.schema_fingerprints` 与当前 catalog 指纹漂移
- `orphan`：零入链且非 hub
- `missing-page`：高频被引但无页
- `duplicate`：同主题重复页（→ 触发三路合并流程）

## 6. 生命周期

```
draft → in_review（REVIEW 队列人工处置）→ published
published --(stale lint / schema 漂移)--> in_review
published --(三路合并/更新)--> version+1
```

`recall` 只消费 `published`；draft 永不进入 NLQ（治理红线）。
