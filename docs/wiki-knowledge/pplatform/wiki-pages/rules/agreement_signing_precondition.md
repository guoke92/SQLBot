---
type: rule
title: 协议签署前置条件
page_key: agreement_signing_precondition
belong: rules
domain: CA证书收费与订单
status: published
aliases: []
oid: 1

sources: ["code", "enrich:wiki-admin"]
contract_version: "0.1"
field_targets: [ca_fee_order.agreement_signed, ca_fee_order.order_status]
scope:
  databases: [lowcode_pplatform]
---

协议签署前置条件规则约束只有 PENDING 且协议未签署的订单可以签署收费协议。签署后 agreement_signed 置为 Y，下一步动作指向交e保支付页。

## 需求背景

支付前必须完成协议签署，确保合规留痕，并控制未签署协议订单不能进入支付流程。

## 版本演进

v0.1 草稿：来自 CaFeeAgreementApplication.signAgreement 的代码证据。

```ground:rule
name: 协议签署前置条件
content: "只有订单状态为PENDING且协议未签署时可签署，签署后agreement_signed=Y，nextAction=BOCOM_PAY_PAGE"
impact: "控制支付前必须签署协议"
field_targets:
  - ca_fee_order.order_status
  - ca_fee_order.agreement_signed
evidence: code_path:CaFeeAgreementApplication.signAgreement
```

相关：[[ca_fee_order]]、[[ca_fee_order_order_status]]、[[fee_agreement]]