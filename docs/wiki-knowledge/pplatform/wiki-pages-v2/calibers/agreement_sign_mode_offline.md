---
type: caliber
title: 线下签署协议
page_key: agreement_sign_mode_offline
domain: 授权协议与电子授权
status: draft
aliases:
  - sign_mode=02
  - 线下协议口径
oid: 1
scope:
  databases: [unknown]
sources:
  - db:argeement_migratory_record
  - code:AgreementMigratoryService.java
contract_version: "0.1"
belong: calibers
---

标识迁移协议在业务系统中的签署模式为线下（`SignModeEnum.OFF_LINE`）。与之并列的是 01 线上、03 无需签署，映射规则见 [[sign_mode_mapping]]。该口径用于迁移后追溯协议签署方式，与 `cust_company_info.need_register_ca` 等签章能力字段不是同一语义（见 [[electronic_seal_activation]]）。

```ground:caliber
name: 线下签署协议
predicate: "argeement_migratory_record.sign_mode = '02'"
scope: "协议签署模式为线下（SignModeEnum.OFF_LINE）"
evidence: "code:AgreementMigratoryService.java:setMigrateContract + db"
```