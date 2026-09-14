---
type: enum
title: electronic_auth_sign_status
page_key: cust_change_record__electronic_auth_sign_status
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




# electronic_auth_sign_status

（权威枚举页：2 值，绑定方式 db-profile，主承载 cust_change_record.electronic_auth_sign_status；db 实测分布。）

```ground:enum
enum: cust_change_record__electronic_auth_sign_status
fields: [cust_change_record.electronic_auth_sign_status]
values:
  "PENDING":
    label: "PENDING"
  "SIGNED":
    label: "SIGNED"
```
