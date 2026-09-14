---
type: enum
title: type
page_key: tenant_migarory_log__type
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

（权威枚举页：14 值，绑定方式 db-profile，主承载 tenant_migarory_log.type；db 实测分布。）

```ground:enum
enum: tenant_migarory_log__type
fields: [tenant_migarory_log.type]
values:
  "CUST_PRODUCT_SYNC":
    label: "CUST_PRODUCT_SYNC"
  "PRODUCT_SYNC":
    label: "PRODUCT_SYNC"
  "PRODUCT_SYNC_VALIDATE":
    label: "PRODUCT_SYNC_VALIDATE"
  "PROJECT_QUERY":
    label: "PROJECT_QUERY"
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
  "migratoryOnTheWayCust":
    label: "migratoryOnTheWayCust"
  "migratoryProject":
    label: "migratoryProject"
  "migratoryTenant":
    label: "migratoryTenant"
  "syncProduct":
    label: "syncProduct"
  "syncProject":
    label: "syncProject"
```
