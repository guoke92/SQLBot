---
type: caliber
title: 待支付订单
page_key: calibers/pending_order
domain: CA证书收费
status: draft
aliases: [PENDING 订单, order_status=PENDING]
oid: 1
scope:
  databases: ["<物理库名>"]
sources:
  - db:ca_fee_order
contract_version: "0.1"
---

# 待支付订单

## 业务定位

以[[tables/ca_fee_order]]的 `order_status='PENDING'` 判定，是"未缴费且仍可发起支付"的订单集合。这是支付准入状态，也是续费、催缴类统计的基口径。

注意库中存在 `PAIDING`、`UNPAID` 等**代码枚举之外的取值**（见[[processes/ca_fee_order_state]]），本口径仅覆盖 `PENDING`，不覆盖这些值；若需要"全部未支付"的口径，须另行评审定义。

## 需求背景

本次语义分析未提供需求文档主张（reqdoc 锚点），口径来自代码枚举。

## 版本演进

- 本次语义分析未提供与本口径相关的需求文档变更主张（uncovered），无 `(document_claim，未证实)` 条目。

```ground:caliber
name: 待支付订单
predicate: "ca_fee_order.order_status = 'PENDING'"
scope: ca_fee_order
evidence: code
```