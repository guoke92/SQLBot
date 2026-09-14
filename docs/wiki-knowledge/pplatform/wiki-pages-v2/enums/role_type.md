---
type: enum
title: role_type
page_key: role_type
domain: 基线
status: draft
aliases: []
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:extract-enums.yaml", "db:db-profile.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.1"
belong: enums
---




# role_type

（权威枚举页：13 值，绑定方式 db-profile，主承载 cust_role_info.role_type；db 实测分布。）

```ground:enum
enum: role_type
fields: [cust_role_info.role_type]
values:
  "\"CORE\"":
    label: "\"CORE\""
  "\"SUPPLIER\"":
    label: "\"SUPPLIER\""
  "CORE":
    label: "CORE"
  "CORE_ADMIN":
    label: "CORE_ADMIN"
  "CORE_MANAGER":
    label: "CORE_MANAGER"
  "CORE_SUB":
    label: "CORE_SUB"
  "CORPORATION_COMPANY":
    label: "CORPORATION_COMPANY"
  "DEALER":
    label: "DEALER"
  "FACTOR_COMPANY":
    label: "FACTOR_COMPANY"
  "FINANCE":
    label: "FINANCE"
  "PLATFORM_OPERATOR_COMPANY":
    label: "PLATFORM_OPERATOR_COMPANY"
  "PROJECT_COMPANY":
    label: "PROJECT_COMPANY"
  "SUPPLIER":
    label: "SUPPLIER"
```
