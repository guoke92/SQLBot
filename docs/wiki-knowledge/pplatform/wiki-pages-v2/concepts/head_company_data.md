---
type: concept
title: headCompanyData
page_key: concept/head_company_data
domain: CA证书认证
status: draft
aliases: [是否总公司行]
oid: 1
scope:
  databases: [unknown]
sources: [code]
contract_version: "0.1"
maps_to: ca_certification_info行标识
adjudication: boundary
also_confused_with: [headCompany]
field_targets:
  - ca_certification_info.head_company_data
---

headCompanyData 是 [[tables/ca_certification_info]] 上的行标识，回答「这一行代表的是分公司自身，还是总公司」：Y 表示总公司行，N 表示分公司自身行。它同时是行幂等键的组成部分（[[calibers/ca_row_idempotent_key]]）。

## 边界与辨析

- headCompanyData 标识 CA 认证行是分公司自身（N）还是总公司（Y）；headCompany 是 cust_company_info 的字段，表示企业本身是否总公司。两者语义层级不同：前者是「这次认证为谁办」，后者是「这家企业是什么性质」，不能互相替换。
- 分公司场景下同一企业会同时产生 headCompanyData=N 与 Y 两行并分别上送签章中台，见 [[rules/branch_dual_row]]。

## 需求背景

语义分析中 reqdoc_claims 为空，暂无可引用的需求文档主张。字段取值 Y/N 与双行行为均来自代码证据。

## 版本演进

暂无文档化的版本演进证据。

相关页面：[[calibers/ca_row_idempotent_key]]、[[rules/branch_dual_row]]、[[tables/ca_certification_info]]。