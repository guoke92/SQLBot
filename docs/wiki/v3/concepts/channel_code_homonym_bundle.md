---
type: concept
title: 同名异义字段对照
page_key: channel_code_homonym_bundle
belong: concepts
domain: cross
status: draft
aliases: [同名异义, field homonym, channel_code 消歧]
maps_to: ''
field_targets: []
sources: ['field_semantics:homonyms', 'join_patterns§8']
created: '2026-09-22'
updated: '2026-09-22'
contract_version: '0.1'
related: []
also_confused_with: [channel_code_term, open_sso_channel_term, channel_archive_longteng,
  platform_product_code_term, wechat_apply_term, online_approval_wf]
adjudication: boundary
semantic_kind: homonym_index
join_hint: forbidden_across_senses
---

# 同名异义字段对照

列名相同、**业务含义不同**时：分建术语、`also_confused_with` 互指，**禁止**跨义 EQUI_JOIN。

## channel_code

| 术语 | 含义 | 主锚 |
|---|---|---|
| [[concepts/channel_code_term]] | 项目邀请码（业务口「项目码」） | `tenant_project.channel_code` |
| [[concepts/open_sso_channel_term]] | SSO/OpenAPI 渠道主数据 | `open_sso_channel.channel_code` |
| [[concepts/channel_archive_longteng]] | 企业建档落库渠道码（与 SSO 对齐） | `cust_company_info.channel_code` |

## 其它高频同名

| 列名 | 勿混 |
|---|---|
| `code` | `platform_product.code`（UUID）≠ `*.platform_product_code` / `product_code`（业务码） |
| `sp_no` | 企微/立项单号 [[concepts/wechat_apply_term]]（含 `tenant_project_approval.sp_no` 注释引用）≠ 上线审批实体本身 [[concepts/online_approval_wf]]（勿用 sp_no 代替 approval.code） |
| `product_code` | 同形多场景：先看 [[concepts/platform_product_code_term]] / [[concepts/funding_product_code_term]] / [[concepts/tenant_menu_product_code_term]]；角色表可能是内存 contains 非 SQL JOIN |
| `certification_no` | 企业统码 [[concepts/certification_no_term]] ≠ 人员证件号 |

## 同名同义（对照）

同一业务字段多表拷贝 → 见 [[concepts/platform_product_code_term]]、[[concepts/certification_no_term]] 等；JOIN 按值域重合，高可连（含 B↔C）。

登记源：`docs/wiki/v3/_raw/l1_intermediate/docs/field_semantics.yaml`
