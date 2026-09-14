---
type: enum
title: type
page_key: tenant_migarory_log_bak__type
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

（权威枚举页：14 值，绑定方式 db-profile，主承载 tenant_migarory_log_bak.type；db 实测分布。）

```ground:enum
enum: tenant_migarory_log_bak__type
fields: [tenant_migarory_log_bak.type]
values:
  "CREATED":
    label: "CREATED"
  "CUST_PRODUCT_SYNC":
    label: "CUST_PRODUCT_SYNC"
  "DELETED":
    label: "DELETED"
  "EFFECTED":
    label: "EFFECTED"
  "PRODUCT_SYNC":
    label: "PRODUCT_SYNC"
  "PROJECT_SYNC":
    label: "PROJECT_SYNC"
  "PROJECT_SYNC_VALIDATE":
    label: "PROJECT_SYNC_VALIDATE"
  "TENANT_SYNC":
    label: "TENANT_SYNC"
  "TENANT_SYNC_VALIDATE":
    label: "TENANT_SYNC_VALIDATE"
  "migratoryCust":
    label: "migratoryCust"
  "migratoryProject":
    label: "migratoryProject"
  "migratoryTenant":
    label: "migratoryTenant"
  "syncProduct":
    label: "syncProduct"
  "syncProject":
    label: "syncProject"
```
