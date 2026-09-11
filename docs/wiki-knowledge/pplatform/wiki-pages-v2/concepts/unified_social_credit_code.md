---
type: concept
title: 统码
page_key: concepts/unified_social_credit_code
domain: CA证书收费
status: draft
aliases: [统一社会信用代码, certification_no]
oid: 1
scope:
  databases: ["<物理库名>"]
sources:
  - db:ca_fee_company
  - db:ca_fee_order
contract_version: "0.1"
maps_to: ca_fee_company.certification_no、ca_fee_order.certification_no
field_targets:
  - ca_fee_company.certification_no
  - ca_fee_order.certification_no
adjudication: synonym
also_confused_with: [企业ID, companyId]
sources: ["enrich:wiki-admin"]
---

# 统码

## 业务定位

**统码**即统一社会信用代码，是 CA 收费域内企业的**唯一标识**，用于关联企业主数据。库表字段名为 `certification_no`，出现在[[tables/ca_fee_company]]（企业台账）与[[tables/ca_fee_order]]（订单）两侧，是两表对齐同一家企业的业务键。

**同义词**：统一社会信用代码、`certification_no`。

**易混边界**：统码 ≠ **企业ID / companyId**。统码是工商登记口径的、全局唯一的社会信用代码；`companyId` 是产融平台内部的企业主键 ID。二者可能同时出现在同一业务流程中，但**不可互相替代**做关联或去重——引用企业时应显式说明使用的是哪一个。

## 需求背景

本次语义分析未提供需求文档主张（reqdoc 锚点），术语边界来自库表字段语义。

## 版本演进

- 本次语义分析未提供与本术语相关的需求文档变更主张（uncovered），无 `(document_claim，未证实)` 条目。

相关：[[ca_fee_company]] [[ca_fee_order]]
