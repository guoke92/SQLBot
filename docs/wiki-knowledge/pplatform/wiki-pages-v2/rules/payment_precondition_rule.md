---
type: rule
title: 支付前置条件规则
page_key: payment_precondition_rule
domain: CA证书收费
status: draft
aliases: [requirePendingSignedOrder, confirmBocomPaid, 支付准入规则]
oid: 1
scope:
  databases: ["<物理库名>"]
sources:
  - code:CaFeePaymentApplication.java:requirePendingSignedOrder,confirmBocomPaid
contract_version: "0.1"
belong: rules
---

# 支付前置条件规则

## 业务定位

发起支付必须同时满足：**订单处于 `PENDING`**（[[calibers/pending_order]]）且**已签署收费协议 `agreement_signed='Y'`**（[[calibers/agreement_signed_order]]）。支付方式固定为交e保（`BOCOM`，见[[concepts/bocom]]）；划扣成功后把订单标记为 `PAID`。

两个条件缺一不可：未签协议不能付款，已支付/已关闭订单不能重复支付。协议签署状态流转见[[processes/ca_fee_agreement_sign]]，订单状态流转见[[processes/ca_fee_order_state]]。

## 需求背景

本次语义分析未提供需求文档主张（reqdoc 锚点），规则内容来自代码路径证据。

## 影响

约束支付流程。

## 版本演进

- 本次语义分析未提供与本规则相关的需求文档变更主张（uncovered），无 `(document_claim，未证实)` 条目。

```ground:rule
name: 支付前置条件规则
content: 订单必须处于 PENDING 且 agreement_signed='Y' 才能发起支付；支付方式为交e保（BOCOM）；划扣成功后标记订单为 PAID。
impact: 约束支付流程。
field_targets: [ca_fee_order.order_status, ca_fee_order.agreement_signed, ca_fee_order.pay_method]
evidence: "code_path:CaFeePaymentApplication.java:requirePendingSignedOrder,confirmBocomPaid"
```