---
type: caliber
title: 交e保划扣待查证
page_key: bocom_txn_sts_02
domain: CA证书收费
status: draft
aliases:
  - bocom_txn_sts = 02
  - 划扣待查证
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:CaFeeConstants.java
contract_version: "0.1"
belong: calibers
---

该口径指 [[ca_fee_order]] 中 `bocom_txn_sts = '02'`，表示划扣结果待查证。它同时约束两处：定时补偿任务向银行查证（成功则补 `markPaid`，明确失败则禁止再次划扣），以及**台账编辑拦截**（不允许人工把待查证订单标记为已缴费），见 [[bocom_idempotent_verify]]、[[ledger_edit_limit]]。

## 需求背景

银行响应超时会产生「不确定」，若人工介入可能造成状态与资金不一致，故以中间态冻结人工操作，改由查证任务收敛。

## 版本演进

- v0（本页）：依据语义分析口径证据建立。

```ground:caliber
name: 交e保划扣待查证
predicate: ca_fee_order.bocom_txn_sts = '02'
scope: 定时补偿查证、台账编辑拦截
evidence: CaFeeConstants.java
```