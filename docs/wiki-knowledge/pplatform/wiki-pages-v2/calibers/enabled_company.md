---
type: caliber
title: 有效企业
page_key: calibers/enabled_company
domain: CA证书收费
status: draft
aliases: [enable=Y, 逻辑有效企业]
oid: 1
scope:
  databases: ["<物理库名>"]
sources:
  - db:ca_fee_company
contract_version: "0.1"
---

# 有效企业

## 业务定位

以[[tables/ca_fee_company]]的 `enable='Y'` 判定，是**逻辑启用**过滤条件。任何统计或业务判定在遍历企业台账前都应先叠加本口径，避免把已失效记录计入。它是**过滤条件**而非业务状态，与服务期（[[calibers/in_service_period]]）、缴费状态（[[calibers/paid_company]]）正交，需要组合使用。

## 需求背景

本次语义分析未提供需求文档主张（reqdoc 锚点），口径来自代码判定。

## 版本演进

- 本次语义分析未提供与本口径相关的需求文档变更主张（uncovered），无 `(document_claim，未证实)` 条目。

```ground:caliber
name: 有效企业
predicate: "ca_fee_company.enable = 'Y'"
scope: ca_fee_company
evidence: code
```