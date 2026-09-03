---
type: caliber
title: 已支付订单
page_key: paid_order
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

已支付订单口径用于识别已经完成支付、进入已缴费状态的 CA 服务费订单。

## 需求背景

支付确认成功后将订单标记为 PAID，后续台账编辑受此状态约束，规则评估中“服务期内已缴费”的部分判断也依赖 PAID 订单。

## 版本演进

v0.1 草稿：基于数据库字段语义确定口径。

```ground:caliber
name: 已支付订单
predicate: "ca_fee_order.order_status = 'PAID'"
scope: 订单维度
evidence: db
```

相关：[[ca_fee_order]]、[[ca_fee_order_order_status]]、[[bocom_payment_confirmation]]、[[ledger_edit_restrictions]]