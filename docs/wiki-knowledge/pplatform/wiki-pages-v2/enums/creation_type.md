---
type: enum
title: creation_type
page_key: creation_type
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




# creation_type

（权威枚举页：3 值，绑定方式 db-profile，主承载 authorization_agreement.creation_type；db 实测分布。）

```ground:enum
enum: creation_type
fields: [authorization_agreement.creation_type]
values:
  "AUTO":
    label: "AUTO"
  "COMPANY_MANAGER_CHANGE_CODE":
    label: "COMPANY_MANAGER_CHANGE_CODE"
  "CUST_BUILD_INIT":
    label: "CUST_BUILD_INIT"
```
