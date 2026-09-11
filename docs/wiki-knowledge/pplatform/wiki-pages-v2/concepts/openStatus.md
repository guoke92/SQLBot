---
type: concept
title: openStatus 开通状态
page_key: concepts/openStatus
domain: 平台产品配置
status: draft
aliases: [openStatus, productOpenStatus, 开通状态]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:tenant_product.open_status
  - code:cust_auth_application.open_status
maps_to: tenant_product.open_status
adjudication: boundary
also_confused_with: [cust_auth_application.open_status]
contract_version: "0.1"
sources: ["enrich:wiki-admin"]
---

openStatus / productOpenStatus / 开通状态在默认语境下映射到 [[tables/tenant_product]] 的 `open_status`，即租户产品开通状态。

边界：租户产品开通状态与客户产品开通状态枚举值不同——租户产品用 Y/P/N（[[processes/tenant-product-open-status]]），客户产品用 OPENED/OPENING/NOT_OPENED（[[processes/cust-product-open-status]]，字段位于 [[tables/cust_auth_application]]）。两者不可按同一套取值解析。

## 需求背景

语义分析未提供该术语的 reqdoc 主张，需求背景不做需求文档层面的断言。

## 版本演进

v0 契约首次建档，术语裁决与边界来自语义分析的术语桥证据。

## 关联

- 状态机：[[processes/tenant-product-open-status]]、[[processes/cust-product-open-status]]
- 口径：[[calibers/tenant-open-product]]、[[calibers/cust-open-product]]
- 表：[[tables/tenant_product]]、[[tables/cust_auth_application]]

相关：[[tenant_product]]
