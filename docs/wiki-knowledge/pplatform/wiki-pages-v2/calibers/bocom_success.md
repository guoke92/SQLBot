---
type: caliber
title: 交e保划扣成功
page_key: calibers/bocom_success
domain: CA证书收费
status: draft
aliases: [bocom_txn_sts=00, 划扣成功]
oid: 1
scope:
  databases: ["<物理库名>"]
sources:
  - db:ca_fee_order
contract_version: "0.1"
---

# 交e保划扣成功

## 业务定位

以[[tables/ca_fee_order]]的 `bocom_txn_sts='00'` 判定，表示交e保（[[concepts/bocom]]）渠道划扣成功。该口径是**支付结果的最底层凭据**，订单转 `PAID` 以其为依据（见[[processes/ca_fee_order_state]]）。

三个交易状态口径须成套使用：[[calibers/bocom_success]]（`00`）、[[calibers/bocom_failure]]（`01`）、[[calibers/bocom_pending_investigation]]（`02`）；`02` 属于结果未定，**不得并入成功或失败**。

## 需求背景

本次语义分析未提供需求文档主张（reqdoc 锚点），口径来自库表取值。

## 版本演进

- 本次语义分析未提供与本口径相关的需求文档变更主张（uncovered），无 `(document_claim，未证实)` 条目。

```ground:caliber
name: 交e保划扣成功
predicate: "ca_fee_order.bocom_txn_sts = '00'"
scope: ca_fee_order
evidence: db
```