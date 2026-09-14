---
type: concept
title: 供应商
page_key: supplier
domain: CA证书收费
status: draft
aliases: [SUPPLIER]
oid: 1
scope:
  databases: ["<物理库名>"]
sources:
  - db:ca_fee_company
  - db:ca_fee_order
  - code:CaFeePaymentCheckApplication.java
contract_version: "0.1"
maps_to: company_type / source_company_type = 'SUPPLIER'
field_targets:
  - ca_fee_company.source_company_type
  - ca_fee_order.company_type
adjudication: synonym
also_confused_with: []
belong: concepts
---

# 供应商

## 业务定位

**供应商**在 CA 收费场景下是**可收费角色之一**，在[[tables/ca_fee_company]]中以 `source_company_type='SUPPLIER'` 记录首次锁定的来源角色，在[[tables/ca_fee_order]]中以 `company_type='SUPPLIER'` 记录订单归属角色。其年费标准取项目配置的 `supplier_annual_fee`（见[[tables/ca_fee_project_config]]）。

**同义词**：`SUPPLIER`。

是否参与收费校验见[[rules/chargeable_company_role_rule]]与口径[[calibers/chargeable_company_role]]；与核企（[[concepts/core_enterprise]]）的区别仅在角色取值与年费标准来源，均为本域可收费对象。

## 需求背景

本次语义分析未提供需求文档主张（reqdoc 锚点），术语边界来自库表字段与代码枚举。

## 版本演进

- 本次语义分析未提供与本术语相关的需求文档变更主张（uncovered），无 `(document_claim，未证实)` 条目。