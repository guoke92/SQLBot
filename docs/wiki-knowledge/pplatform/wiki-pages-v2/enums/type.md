---
type: enum
title: type
page_key: type
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


# type

（权威枚举页：2 值，绑定方式 db-profile，主承载 cust_company_lifecycle_info.type；db 实测分布。）

```ground:enum
enum: type
fields: [cust_company_lifecycle_info.type]
values:
  "FRZ":
    label: "FRZ"
  "UNFRZ":
    label: "UNFRZ"
```
