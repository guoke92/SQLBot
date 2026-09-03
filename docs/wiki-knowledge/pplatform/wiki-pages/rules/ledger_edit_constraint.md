---
type: rule
title: 台账编辑约束
page_key: ledger_edit_constraint
domain: ca_cert_fee
status: published
aliases: []
oid: 1

sources: ["code", "enrich:wiki-admin"]
contract_version: "0.1"
field_targets: [ca_fee_order.bocom_txn_sts, ca_fee_order.order_status, ca_fee_order.version]
scope:
  databases: [lowcode_pplatform]
---

# 台账编辑约束

业务定位：限制人工运营对台账的修改范围，确保数据准确性和一致性。

## 需求背景

运营人员可能误改订单状态或金额。该规则限定订单状态只能为 PENDING/PAID，已缴费订单不可改为未缴费，交 e 保查证中不可改为已缴费，并通过乐观锁防止并发冲突。

## 版本演进

当前约束基于代码实现，未来可能增加审计日志或操作权限控制。

```ground:rule
name: 台账编辑约束
content: orderStatus 仅支持 PENDING/PAID；已缴费订单不允许改为未缴费；交e保查证中(bocom_txn_sts=02)不可改已缴费；使用 version 乐观锁
impact: 人工运营纠错限制
field_targets: ["ca_fee_order.order_status", "ca_fee_order.version", "ca_fee_order.bocom_txn_sts"]
evidence: code:CaFeeLedgerOperateService.editOrder
```

[[ca_fee_order]] · [[pay_status]] · [[bocom-provider]]