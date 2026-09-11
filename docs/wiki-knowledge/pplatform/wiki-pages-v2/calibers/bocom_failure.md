---
type: caliber
title: 交e保划扣失败
page_key: calibers/bocom_failure
domain: CA证书收费
status: draft
aliases: [bocom_txn_sts=01, 划扣失败]
oid: 1
scope:
  databases: ["<物理库名>"]
sources:
  - db:ca_fee_order
contract_version: "0.1"
---

# 交e保划扣失败

## 业务定位

以[[tables/ca_fee_order]]的 `bocom_txn_sts='01'` 判定，表示交e保（[[concepts/bocom]]）渠道划扣失败。该口径用于失败率与重试分析，**不应**被计入[[calibers/bocom_success]]；同时注意与[[calibers/bocom_pending_investigation]]（`02` 待查证）区分，后者结果未定。

## 需求背景

本次语义分析未提供需求文档主张（reqdoc 锚点），口径来自代码判定。

## 版本演进

- 本次语义分析未提供与本口径相关的需求文档变更主张（uncovered），无 `(document_claim，未证实)` 条目。

```ground:caliber
name: 交e保划扣失败
predicate: "ca_fee_order.bocom_txn_sts = '01'"
scope: ca_fee_order
evidence: code
```