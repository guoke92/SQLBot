---
type: caliber
title: 核企/供应商角色
page_key: chargeable_company_role
domain: CA证书收费
status: draft
aliases: [source_company_type in CORE,SUPPLIER, 可收费角色]
oid: 1
scope:
  databases: ["<物理库名>"]
sources:
  - db:ca_fee_company
contract_version: "0.1"
belong: calibers
---

# 核企/供应商角色

## 业务定位

以[[tables/ca_fee_company]]的 `source_company_type` 是否落在 `('CORE','SUPPLIER')` 判定，用于圈定**可收费角色**。该口径与[[rules/chargeable_company_role_rule|收费对象规则]]一一对应：仅这两类角色需要校验 CA 服务费，其他角色（如 `PROJECT_COMPANY`）直接放行。

角色术语含义见[[concepts/core_enterprise]]与[[concepts/supplier]]。

## 需求背景

本次语义分析未提供需求文档主张（reqdoc 锚点），口径来自代码判定。

## 版本演进

- 本次语义分析未提供与本口径相关的需求文档变更主张（uncovered），无 `(document_claim，未证实)` 条目。

```ground:caliber
name: 核企/供应商角色
predicate: "ca_fee_company.source_company_type in ('CORE','SUPPLIER')"
scope: ca_fee_company
evidence: code
```