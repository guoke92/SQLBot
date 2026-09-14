---
type: concept
title: 邀请码有效期
page_key: invitation_code_period
domain: notification
status: draft
aliases: [invitationCodePeriod]
oid: 1
scope:
  databases: []
sources:
  - db:cust_setting_config.invitation_code_period
  - db:cust_setting_config.invitation_code_period_unit
maps_to: cust_setting_config.invitation_code_period
field_targets:
  - cust_setting_config.invitation_code_period
  - cust_setting_config.invitation_code_period_unit
adjudication: boundary
also_confused_with:
  - invitation_code_sending_interval
contract_version: "0.1"
belong: concepts
field_targets: [cust_setting_config.invitation_code_period]
sources: ["enrich:wiki-admin"]
---

邀请码有效期指邀请码自发出起可用的时长。判定边界：invitation_code_period 是数值列，单位由 invitation_code_period_unit 决定，二者必须成对解读；与「邀请码重复发送时间间隔」（sending_interval / sending_interval_unti）是不同语义，不可混用。

## 需求背景
邀请码需要控制有效窗口并在重复发送上做限流，防止刷取与长期滞留可用码。

## 版本演进
- 需求文档提出「邀请码随机生成8位、30天有效」，代码中未见邀请码生成逻辑，DB 中 invitation_code_period=1，文档与实现一致性未证实，见 REVIEW。

相关：[[cust_setting_config]]
