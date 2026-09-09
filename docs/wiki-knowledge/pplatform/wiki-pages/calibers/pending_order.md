---
type: caliber
title: 待支付订单
page_key: pending_order
belong: calibers
domain: CA证书收费与订单
status: published
aliases: []
oid: 1

sources: ["db", "enrich:wiki-admin"]
contract_version: "0.1"
field_targets: [ca_fee_order.order_status]
scope:
  databases: [lowcode_pplatform]
---

待支付订单口径用于识别尚未完成支付、仍处于可支付或可关闭状态的 CA 服务费订单。

## 需求背景

订单操作约束和支付确认流程都依赖 PENDING 状态，协议签署、交e保支付确认与台账编辑限制均以该状态为前提。

## 版本演进

v0.1 草稿：基于数据库字段语义确定口径。

```ground:caliber
name: 待支付订单
predicate: "ca_fee_order.order_status = 'PENDING'"
scope: 订单维度
evidence: db
```

相关：[[ca_fee_order]]、[[ca_fee_order_order_status]]、[[agreement_signing_precondition]]、[[bocom_payment_confirmation]]