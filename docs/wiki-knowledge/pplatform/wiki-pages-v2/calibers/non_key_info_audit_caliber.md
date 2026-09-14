---
type: caliber
title: 非关键信息变更需要审核
page_key: non_key_info_audit_caliber
domain: notification
status: draft
aliases: [needVerifyNoKey 口径]
oid: 1
scope:
  databases: []
sources:
  - CustSettingConfigEnhanceService.java
  - db:cust_setting_config.need_verify_no_key
contract_version: "0.1"
belong: calibers
---

当 need_verify_no_key='yes' 时，非关键信息变更进入审核；关键信息有变更时优先返回需要审核，非关键信息再按此开关判断。术语定义见 [[non_key_info_audit_caliber]] 对应术语页 [[non_key_info_audit]]。

## 需求背景
企业信息中的关键信息与非关键信息风险等级不同，需求侧要求分别配置审核策略，避免为低风险变更引入高成本审核。

## 版本演进
- 当前为字符串字面量判断，无枚举约束，取值见 [[cust_setting_config_switch]]。

```ground:caliber
name: 非关键信息变更需要审核
predicate: cust_setting_config.need_verify_no_key = 'yes'
scope: 企业变更审核
evidence: CustSettingConfigEnhanceService.java + db
```