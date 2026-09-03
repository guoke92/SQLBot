---
type: rule
title: 台账编辑限制
page_key: ledger_edit_restrictions
domain: CA证书收费与订单
status: published
aliases: []
oid: 1

sources: ["code", "enrich:wiki-admin"]
contract_version: "0.1"
field_targets: [ca_fee_order.bocom_txn_sts, ca_fee_order.order_status]
scope:
  databases: [lowcode_pplatform]
---

台账编辑限制规则约束运营操作：订单状态仅支持 PENDING/PAID 手动编辑，不允许 PAID 回退为 PENDING；交e保查证中（bocom_txn_sts=02）不可手动标记已缴费。

## 需求背景

为避免运营误操作导致已支付订单回退或交e保在途订单被错误标记，必须设置明确的编辑约束。

## 版本演进

v0.1 草稿：来自 CaFeeLedgerOperateService.editOrder 的代码证据。

```ground:rule
name: 台账编辑限制
content: "订单状态仅支持PENDING/PAID手动编辑；不允许PAID改回PENDING；交e保查证中(bocom_txn_sts=02)不可手动标记已缴费"
impact: "运营操作约束"
field_targets:
  - ca_fee_order.order_status
  - ca_fee_order.bocom_txn_sts
evidence: code_path:CaFeeLedgerOperateService.editOrder
```

相关：[[ca_fee_order]]、[[ca_fee_order_order_status]]、[[bocom-provider]]