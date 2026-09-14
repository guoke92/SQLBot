---
type: concept
title: 收费协议
page_key: fee_agreement
domain: CA证书收费
status: draft
aliases:
  - CA服务费收费协议
oid: 1
scope:
  databases:
    - unknown
sources:
  - code
contract_version: "0.1"
maps_to: ca_fee_order.agreement_signed
field_targets:
  - ca_fee_order.agreement_signed
  - ca_fee_order.agreement_version
adjudication: boundary
boundary: agreement_signed 表示是否已签；agreement_version 表示签署时绑定的版本
also_confused_with:
  - ca_fee_order.agreement_version
belong: concepts
field_targets: [ca_fee_order.agreement_signed]
sources: ["enrich:wiki-admin"]
---

「收费协议」是订单进入支付前的合规前置，签署事实落在 `ca_fee_order.agreement_signed`（状态机见 [[ca_fee_order_agreement_signed]]，口径见 [[agreement_signed_y]]、规则见 [[agreement_sign_prerequisite]]），签署时绑定的版本落在 `agreement_version`；项目侧另有 `ca_fee_project_config.agreement_version` 作为项目绑定的协议版本。

**边界（易混淆）**：`agreement_signed` 表达「是否已签」，`agreement_version` 表达「签的是哪一版」。台账或对外说明中若只写「协议已签署」，不应据此推定版本。

## 需求背景

收费协议需要按版本留痕以支持审计，且必须在交e保开户与确认打款之前完成签署，故在订单上同时保留布尔事实与版本号。

## 版本演进

- v0（本页）：建立术语桥与边界。

相关：[[ca_fee_order]]
