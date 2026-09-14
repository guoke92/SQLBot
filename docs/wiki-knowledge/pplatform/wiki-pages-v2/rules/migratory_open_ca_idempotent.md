---
type: rule
title: 迁移企业开 CA 幂等
page_key: migratory_open_ca_idempotent
domain: 租户迁移
status: draft
aliases: [开 CA 幂等, openCa 判定]
oid: 1
scope:
  databases: ["<待确认：语义分析未给出物理库名>"]
sources:
  - "code:PlatFormMigratoryApplication.java#openCa"
  - "code:CustAccessAsyncApplication.java#openCa"
contract_version: "0.1"
belong: rules
---

开 CA 前按产品分支做幂等判定：AMS 看 `bs_register_status`，非 AMS 看 `ca_register_status`，已为 'Y' 直接返回；开通成功后 AMS 同时置 bs/ca 为 Y，其他仅置 ca 为 Y。这避免重复迁移时反复向签章中台注册。

```ground:rule
name: 迁移企业开 CA 幂等
content: "openCa 前判定：AMS 看 bs_register_status，非 AMS 看 ca_register_status，已为 'Y' 直接返回；开通成功后 AMS 同时置 bs/ca 为 Y，其他仅置 ca 为 Y"
impact: "避免重复向签章中台注册"
field_targets:
  - cust_company_info.ca_register_status
  - cust_company_info.bs_register_status
evidence: "code:PlatFormMigratoryApplication.java#openCa；CustAccessAsyncApplication.java#openCa"
```

## 需求背景

签章注册是有外部副作用的动作，重复迁移不得造成重复注册；同时 AMS 与自建签章体系并存，需分别判定。

## 版本演进

判定列由单列演进为按产品的双列（bs/ca），`need_register_ca` 仍会被上游值与字面量先后覆盖，判定口径以两列为准。

相关：[[cust_company_info]]、[[ams_migratory_dedup]]。