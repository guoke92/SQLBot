---
type: caliber
title: 已签署协议订单
page_key: calibers/agreement_signed_order
domain: CA证书收费
status: draft
aliases: [agreement_signed=Y, 协议已签订单]
oid: 1
scope:
  databases: ["<物理库名>"]
sources:
  - db:ca_fee_order
contract_version: "0.1"
---

# 已签署协议订单

## 业务定位

以[[tables/ca_fee_order]]的 `agreement_signed='Y'` 判定。该口径是**支付准入的前置条件之一**，与订单状态共同约束支付发起（见[[rules/payment_precondition_rule]]）。签署动作与版本号、签署时间、协议文件路径一并记录，签署状态自身的流转见[[processes/ca_fee_agreement_sign]]。

## 需求背景

本次语义分析未提供需求文档主张（reqdoc 锚点），口径来自库表字段取值。

## 版本演进

- 本次语义分析未提供与本口径相关的需求文档变更主张（uncovered），无 `(document_claim，未证实)` 条目。

```ground:caliber
name: 已签署协议订单
predicate: "ca_fee_order.agreement_signed = 'Y'"
scope: ca_fee_order
evidence: db
```