---
type: caliber
title: 交e保划扣成功
page_key: bocom_txn_sts_00
domain: CA证书收费
status: draft
aliases:
  - bocom_txn_sts = 00
  - 划扣成功
oid: 1
scope:
  databases:
    - unknown
sources:
  - db
  - code_path:CaFeeConstants.java
contract_version: "0.1"
belong: calibers
---

该口径指 [[ca_fee_order]] 中 `bocom_txn_sts = '00'`，表示交e保划扣成功。它用于**补单**与**幂等拦截**：订单已存在成功流水时不再重复扣款，见 [[bocom_idempotent_verify]]。

## 需求背景

交e保渠道存在回执延迟与重复发起风险，需要以银行响应状态为准做幂等，而非仅依赖本地订单状态。

## 版本演进

- v0（本页）：依据语义分析口径证据建立。

```ground:caliber
name: 交e保划扣成功
predicate: ca_fee_order.bocom_txn_sts = '00'
scope: 补单/幂等拦截
evidence: db + CaFeeConstants.java
```