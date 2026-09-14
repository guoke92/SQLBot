---
type: caliber
title: 收费协议已签署
page_key: agreement_signed_y
domain: CA证书收费
status: draft
aliases:
  - agreement_signed = Y
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:CaFeePaymentApplication.java
contract_version: "0.1"
belong: calibers
---

该口径指 [[ca_fee_order]] 中 `agreement_signed = 'Y'`，是交e保支付的**前置校验**条件，见 [[agreement_sign_prerequisite]]、[[ca_fee_order_agreement_signed]]。签署状态与协议版本字段的边界见 [[fee_agreement]]。

## 需求背景

收费协议签署是合规要求：未签署不允许进入开户与确认打款，故在支付入口以本口径拦截。

## 版本演进

- v0（本页）：依据语义分析口径证据建立。

```ground:caliber
name: 收费协议已签署
predicate: ca_fee_order.agreement_signed = 'Y'
scope: 交e保支付前置校验
evidence: CaFeePaymentApplication.java
```