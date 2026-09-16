---
type: enum
title: tenant_migarory_log_type
page_key: tenant_migarory_log_type
belong: enums
status: draft
aliases: []
anchors:
- tenant_migarory_log_type
sources:
- database_profile:tenant_migarory_log.type
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
recall: true
---

# tenant_migarory_log_type

L0 枚举候选：仅 profile 代码值，无代码 label。

## 取值

```ground:enum
enum: tenant_migarory_log_type
fields:
- tenant_migarory_log.type
values:
  migratoryProject:
    confidence: proposed
  syncProject:
    confidence: proposed
  migratoryCust:
    confidence: proposed
  PROJECT_SYNC_VALIDATE:
    confidence: proposed
  PROJECT_SYNC:
    confidence: proposed
  CUST_PRODUCT_SYNC:
    confidence: proposed
  TENANT_SYNC:
    confidence: proposed
  TENANT_SYNC_VALIDATE:
    confidence: proposed
  syncProduct:
    confidence: proposed
  PROJECT_QUERY:
    confidence: proposed
  migratoryTenant:
    confidence: proposed
  migratoryOnTheWayCust:
    confidence: proposed
  PRODUCT_SYNC:
    confidence: proposed
  PRODUCT_SYNC_VALIDATE:
    confidence: proposed
ambiguous: false
```
