---
type: caliber
title: 已支付订单
page_key: paid_order
domain: CA证书收费
status: draft
aliases: [PAID 订单, order_status=PAID]
oid: 1
scope:
  databases: ["<物理库名>"]
sources:
  - db:ca_fee_order
contract_version: "0.1"
belong: calibers
---

# 已支付订单

## 业务定位

以[[tables/ca_fee_order]]的 `order_status='PAID'` 判定，用于收入/缴费笔数统计。支付成功由交e保划扣成功后回写（见[[processes/ca_fee_order_state]]与[[rules/payment_precondition_rule]]）。

与[[calibers/paid_company]]的区别：本口径是**单据级**、反映历史交易；后者是**企业级当前状态**，会因服务到期而回退为 `UNPAID`。二者在同一时点不一定一致，跨期比对时需声明口径。

## 需求背景

本次语义分析未提供需求文档主张（reqdoc 锚点），口径来自代码枚举。

## 版本演进

- 本次语义分析未提供与本口径相关的需求文档变更主张（uncovered），无 `(document_claim，未证实)` 条目。

```ground:caliber
name: 已支付订单
predicate: "ca_fee_order.order_status = 'PAID'"
scope: ca_fee_order
evidence: code
```