---
type: concept
title: 企业认证审核
page_key: enterprise_auth_audit
domain: notification
status: draft
aliases: [needAuthVerify]
oid: 1
scope:
  databases: []
sources:
  - CustSettingConfigEnhanceService.java
  - db:cust_setting_config.need_auth_verify
maps_to: cust_setting_config.need_auth_verify = 'yes'
field_targets:
  - cust_setting_config.need_auth_verify
adjudication: boundary
also_confused_with:
  - non_key_info_audit
contract_version: "0.1"
belong: concepts
sources: ["enrich:wiki-admin"]
---

企业认证审核指企业在认证环节需要人工审核。判定边界：代码中 'no' 直接返回不需要审批；'yes' 继续判断。与 [[non_key_info_audit]] 互为边界，二者属于不同触发路径。

## 需求背景
认证涉主体资质，需求侧允许企业按风控要求决定是否引入人工审核。

## 版本演进
- 取值以字符串字面量存储，见 [[cust_setting_config_switch]]；口径页见 [[enterprise_auth_audit_caliber]]。

相关：[[cust_setting_config]]
