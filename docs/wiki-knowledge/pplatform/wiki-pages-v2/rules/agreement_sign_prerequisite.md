---
type: rule
title: 协议签署前置规则
page_key: agreement_sign_prerequisite
domain: CA证书收费
status: draft
aliases:
  - 请先签署收费协议
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:CaFeePaymentApplication.java
contract_version: "0.1"
belong: rules
---

交e保开户与确认打款前，订单必须 `agreement_signed=Y`；否则抛出「请先签署收费协议」。这是支付入口的硬前置，口径见 [[agreement_signed_y]]，状态机见 [[ca_fee_order_agreement_signed]]，术语边界见 [[fee_agreement]]。

## 需求背景

收费协议属于合规材料，不能在支付完成后补签；因此把签署作为支付的前置条件而非并行步骤。

## 版本演进

- v0（本页）：依据语义分析规则证据建立。

```ground:rule
name: 协议签署前置规则
content: 交e保开户和确认打款前，订单必须 agreement_signed=Y；否则抛出“请先签署收费协议”
impact: 收费协议是支付前置条件
field_targets:
  - ca_fee_order.agreement_signed
evidence: CaFeePaymentApplication.requirePendingSignedOrder
```