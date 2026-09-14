---
type: enum
title: company_type
page_key: ca_fee_order__company_type
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

（权威枚举页：3 值，绑定方式 db-profile，主承载 ca_fee_order.company_type；db 实测分布。）

```ground:enum
enum: ca_fee_order__company_type
fields: [ca_fee_order.company_type]
values:
  "CORE":
    label: "CORE"
  "PROJECT_COMPANY":
    label: "PROJECT_COMPANY"
  "SUPPLIER":
    label: "SUPPLIER"
```
