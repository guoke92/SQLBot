---
type: concept
title: 非关键信息变更审核
page_key: non_key_info_audit
domain: notification
status: draft
aliases: [needVerifyNoKey]
oid: 1
scope:
  databases: []
sources:
  - CustSettingConfigEnhanceService.java
  - db:cust_setting_config.need_verify_no_key
maps_to: cust_setting_config.need_verify_no_key = 'yes'
field_targets:
  - cust_setting_config.need_verify_no_key
  - cust_setting_config.key_word
  - cust_setting_config.no_key_word
adjudication: boundary
also_confused_with:
  - enterprise_auth_audit
contract_version: "0.1"
belong: concepts
sources: ["enrich:wiki-admin"]
---

非关键信息变更审核指企业对非关键信息字段的修改需要审核。判定边界：关键信息有变更时先返回需要审核，非关键信息再按此开关判断；关键与非关键字段清单分别存于 key_word / no_key_word。与 [[enterprise_auth_audit]] 互为边界。

## 需求背景
关键与非关键信息风险等级不同，需求侧要求分别配置审核策略。

## 版本演进
- 口径页见 [[non_key_info_audit_caliber]]，取值见 [[cust_setting_config_switch]]。

相关：[[cust_setting_config]]
