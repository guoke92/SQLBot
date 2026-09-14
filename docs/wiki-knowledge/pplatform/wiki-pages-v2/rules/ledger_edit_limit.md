---
type: rule
title: 台账编辑限制规则
page_key: ledger_edit_limit
domain: CA证书收费
status: draft
aliases:
  - 编辑限制
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:CaFeeLedgerOperateService.java
contract_version: "0.1"
belong: rules
---

台账订单编辑仅支持 `PENDING`／`PAID`；已缴费订单不允许改为未缴费；交e保 `bocom_txn_sts=02`（待查证）不允许人工标记已缴费。涉及口径 [[order_status_pending]]、[[order_status_paid]]、[[bocom_txn_sts_02]]，与自动收敛逻辑的关系见 [[bocom_idempotent_verify]]。

## 需求背景

台账是运营人工介入的入口，但人工修改不能破坏支付事实：已缴订单回退会造成重复收费风险，待查证订单改价会造成状态与资金不一致。

## 版本演进

- v0（本页）：依据语义分析规则证据建立。

```ground:rule
name: 台账编辑限制规则
content: 台账订单编辑仅支持 PENDING/PAID；已缴费订单不允许改为未缴费；交e保查证中 bocom_txn_sts=02 不允许人工标记已缴费
impact: 保障台账状态与支付状态一致
field_targets:
  - ca_fee_order.order_status
  - ca_fee_order.bocom_txn_sts
evidence: CaFeeLedgerOperateService.editOrder
```