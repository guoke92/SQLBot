---
type: enum
title: company_type
page_key: ca_cfca_upgrade_report__company_type
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

（权威枚举页：6 值，绑定方式 db-profile，主承载 ca_cfca_upgrade_report.company_type；db 实测分布。）

```ground:enum
enum: ca_cfca_upgrade_report__company_type
fields: [ca_cfca_upgrade_report.company_type]
values:
  "CORE":
    label: "CORE"
  "FINANCE":
    label: "FINANCE"
  "PLATFORM_COMPANY":
    label: "PLATFORM_COMPANY"
  "PLATFORM_OPERATOR_COMPANY":
    label: "PLATFORM_OPERATOR_COMPANY"
  "PROJECT_COMPANY":
    label: "PROJECT_COMPANY"
  "SUPPLIER":
    label: "SUPPLIER"
```
