---
type: process
title: CA收费协议签署状态机
page_key: ca_fee_agreement_signed
domain: ca_cert_fee
status: published
aliases: []
oid: 1

sources: ["code", "db", "enrich:wiki-admin"]
contract_version: "0.1"
field_targets: [ca_fee_order.agreement_signed]
scope:
  databases: [lowcode_pplatform]
---

# CA收费协议签署状态机

业务定位：定义 `ca_fee_order.agreement_signed` 字段的布尔状态及其签署事件，控制协议签署环节。

## 需求背景

收费协议签署是缴费流程的前置环节，需要区分未签署和已签署两种状态，并记录签署动作的证据路径。

## 版本演进

当前状态简单，仅包含 N → Y 的单向转换，未来可能增加作废、重新签署等状态。

```ground:process
name: ca_fee_agreement_signed
field: ca_fee_order.agreement_signed
states:
  - value: N
    label: 未签署
    source: db_dist
  - value: Y
    label: 已签署
    source: db_dist
transitions:
  - from: N
    event: signAgreement
    to: Y
    evidence: code_path:CaFeeAgreementApplication.java:signAgreement
```

[[ca_fee_order]] · [[agreement_signing_precondition]]