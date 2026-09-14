---
type: enum
title: company_type
page_key: cust_project_rel__company_type
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




# company_type

（权威枚举页：9 值，绑定方式 db-profile，主承载 cust_project_rel.company_type；db 实测分布。）

```ground:enum
enum: cust_project_rel__company_type
fields: [cust_project_rel.company_type]
values:
  "CORE":
    label: "CORE"
  "CORE_MANAGER":
    label: "CORE_MANAGER"
  "CORPORATION_COMPANY":
    label: "CORPORATION_COMPANY"
  "DEALER":
    label: "DEALER"
  "FINANCE":
    label: "FINANCE"
  "PLATFORM_OPERATOR_COMPANY":
    label: "PLATFORM_OPERATOR_COMPANY"
  "PLATFORM_OPREATOR_COMPANY":
    label: "PLATFORM_OPREATOR_COMPANY"
  "PROJECT_COMPANY":
    label: "PROJECT_COMPANY"
  "SUPPLIER":
    label: "SUPPLIER"
```
