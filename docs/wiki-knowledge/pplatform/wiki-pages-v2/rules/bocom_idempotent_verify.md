---
type: rule
title: 交e保划扣幂等与查证规则
page_key: bocom_idempotent_verify
domain: CA证书收费
status: draft
aliases:
  - 划扣幂等
  - 待查证补偿
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:CaFeePaymentApplication.java
  - code_path:CaFeeBocomPayReconcileService.java
contract_version: "0.1"
belong: rules
---

订单已有 `txnSts=00/01/02` 时拦截重复扣款；`02` 待查证由定时任务向银行查证，成功则补 `markPaid`，明确失败则禁止再次划扣。三个状态的口径见 [[bocom_txn_sts_00]]、[[bocom_txn_sts_01]]、[[bocom_txn_sts_02]]，并联动订单状态 [[ca_fee_order_status]]。

## 需求背景

渠道响应超时会产生资金状态不确定，若不冻结重试会造成重复出金；因此以「先查证、后收敛」替代「直接重试」。台账侧同时冻结人工编辑，见 [[ledger_edit_limit]]。

## 版本演进

- v0（本页）：依据语义分析规则证据建立。

```ground:rule
name: 交e保划扣幂等与查证规则
content: 订单已有 txnSts=00/01/02 时拦截重复扣款；02 待查证由定时任务向银行查证，成功则补 markPaid，明确失败则禁止再次划扣
impact: 防止重复支付和状态不一致
field_targets:
  - ca_fee_order.bocom_txn_sts
  - ca_fee_order.order_status
evidence: CaFeePaymentApplication.tryResolveByBocomVerify + CaFeeBocomPayReconcileService
```