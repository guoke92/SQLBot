---
type: enum
title: apply_type
page_key: apply_type
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




# apply_type

（权威枚举页：2 值，绑定方式 db-profile，主承载 cust_company_info.apply_type；db 实测分布。）

```ground:enum
enum: apply_type
fields: [cust_company_info.apply_type]
values:
  "add":
    label: "add"
  "update":
    label: "update"
```
