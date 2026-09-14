---
type: caliber
title: 交e保划扣明确失败
page_key: bocom_txn_sts_01
domain: CA证书收费
status: draft
aliases:
  - bocom_txn_sts = 01
  - 划扣明确失败
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:CaFeeConstants.java
contract_version: "0.1"
belong: calibers
---

该口径指 [[ca_fee_order]] 中 `bocom_txn_sts = '01'`，表示银行侧明确失败，用于**禁止重复划扣**。与 `02` 待查证的区别在于：`01` 是确定性结论，`02` 需要向银行查证后才有结论，见 [[bocom_txn_sts_02]]、[[bocom_idempotent_verify]]。

## 需求背景

明确失败若允许再次发起，会导致同一订单反复出金尝试与对账困难，故在支付入口直接拦截。

## 版本演进

- v0（本页）：依据语义分析口径证据建立。

```ground:caliber
name: 交e保划扣明确失败
predicate: ca_fee_order.bocom_txn_sts = '01'
scope: 禁止重复划扣
evidence: CaFeeConstants.java
```