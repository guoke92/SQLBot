---
type: rule
title: 协议签署模式映射
page_key: sign_mode_mapping
domain: 授权协议与电子授权
status: draft
aliases:
  - signMode 映射
  - 签署模式落库规则
oid: 1
scope:
  databases: [unknown]
sources:
  - code:AgreementMigratoryService.java
  - db:argeement_migratory_record
contract_version: "0.1"
belong: rules
---

迁移时把业务系统的 `signMode` 归一化为产融侧的 [[argeement_migratory_record]] 字典码，并补齐 `sign_type=SIGNED`、`business_type=cust_company_info`，使迁移后协议在产融侧的签署方式可追溯。线下口径见 [[agreement_sign_mode_offline]]。

```ground:rule
name: 协议签署模式映射
content: "迁移协议将业务系统 signMode 映射为 SignModeEnum：NO_SIGN=03 无需签署、OFF_LINE=02 线下、ON_LINE=01 线上；并落 sign_type=SIGNED、business_type=cust_company_info"
impact: "迁移后协议在产融侧的签署方式可追溯"
field_targets:
  - argeement_migratory_record.sign_mode
evidence: "code:AgreementMigratoryService.java:setMigrateContract"
```