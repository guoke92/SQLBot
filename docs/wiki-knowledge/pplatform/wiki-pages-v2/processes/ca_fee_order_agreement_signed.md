---
type: process
title: 收费协议签署状态机
page_key: ca_fee_order_agreement_signed
domain: CA证书收费
status: draft
aliases:
  - 协议签署状态
  - agreement_signed
oid: 1
scope:
  databases:
    - unknown
sources:
  - code
contract_version: "0.1"
belong: processes
---

收费协议签署状态机作用于 [[ca_fee_order]] 的 `agreement_signed`，是一个**单向开关**：`N` 未签署 → `Y` 已签署，不存在回退迁移。签署时同时绑定 `agreement_version`（签署时的协议版本），二者语义边界见 [[fee_agreement]]。

该状态是支付前置条件：交e保开户与确认打款前必须为 `Y`，否则抛出「请先签署收费协议」，见 [[agreement_sign_prerequisite]]，口径见 [[agreement_signed_y]]。

## 需求背景

CA 服务费属于新增商业模式，需要以订单为粒度留存收费协议的签署事实与版本，供支付前置校验与后续审计使用；协议签署与支付被显式解耦为两步。

## 版本演进

- v0（本页）：依据语义分析中的状态与迁移证据建立首版状态机。

```ground:process
name: 收费协议签署状态
field: ca_fee_order.agreement_signed
states:
  - value: N
    label: 未签署
    source: code_const
  - value: Y
    label: 已签署
    source: code_const
transitions:
  - from: N
    event: 签署收费协议 markAgreementSigned
    to: Y
    evidence: code_path:CaFeeOrderService.java:337 + CaFeeAgreementApplication.java
```