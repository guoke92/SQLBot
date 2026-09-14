---
type: enum
title: change_type
page_key: change_type
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




# change_type

（权威枚举页：4 值，绑定方式 db-profile，主承载 cust_oper_change_record.change_type；db 实测分布。）

```ground:enum
enum: change_type
fields: [cust_oper_change_record.change_type]
values:
  "ASSET_AUDIT_SYNC":
    label: "ASSET_AUDIT_SYNC"
  "BATCH":
    label: "BATCH"
  "CUST_CHANGE_CALLBACK":
    label: "CUST_CHANGE_CALLBACK"
  "MANUAL":
    label: "MANUAL"
```
