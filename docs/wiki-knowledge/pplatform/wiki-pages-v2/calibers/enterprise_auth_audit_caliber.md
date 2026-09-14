---
type: caliber
title: 企业认证需要审核
page_key: enterprise_auth_audit_caliber
domain: notification
status: draft
aliases: [needAuthVerify 口径]
oid: 1
scope:
  databases: []
sources:
  - CustSettingConfigEnhanceService.java
  - db:cust_setting_config.need_auth_verify
contract_version: "0.1"
belong: calibers
---

当 need_auth_verify='yes' 时，企业认证进入审核流程；代码中 'no' 直接返回不需要审批。术语定义见 [[enterprise_auth_audit]]，与其相邻的开关口径见 [[non_key_info_audit_caliber]]。

## 需求背景
认证涉企业主体资质，需求侧允许企业按自身风控要求决定是否引入人工审核环节。

## 版本演进
- 当前为字符串字面量判断，无枚举约束，取值见 [[cust_setting_config_switch]]。

```ground:caliber
name: 企业认证需要审核
predicate: cust_setting_config.need_auth_verify = 'yes'
scope: 企业变更/认证审核
evidence: CustSettingConfigEnhanceService.java + db
```