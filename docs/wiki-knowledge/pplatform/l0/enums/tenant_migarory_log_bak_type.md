---
type: enum
title: tenant_migarory_log_bak_type
page_key: tenant_migarory_log_bak_type
belong: enums
status: draft
aliases: []
anchors:
- tenant_migarory_log_bak_type
sources:
- database_profile:tenant_migarory_log_bak.type
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
recall: true
---

# tenant_migarory_log_bak_type

L0 枚举候选：仅 profile 代码值，无代码 label。

## 取值

```ground:enum
enum: tenant_migarory_log_bak_type
fields:
- tenant_migarory_log_bak.type
values:
  migratoryProject:
    confidence: proposed
  PROJECT_SYNC:
    confidence: proposed
  CUST_PRODUCT_SYNC:
    confidence: proposed
  syncProject:
    confidence: proposed
  TENANT_SYNC:
    confidence: proposed
  syncProduct:
    confidence: proposed
  PRODUCT_SYNC:
    confidence: proposed
  migratoryCust:
    confidence: proposed
  migratoryTenant:
    confidence: proposed
  CREATED:
    confidence: proposed
  DELETED:
    confidence: proposed
  PROJECT_SYNC_VALIDATE:
    confidence: proposed
  TENANT_SYNC_VALIDATE:
    confidence: proposed
  EFFECTED:
    confidence: proposed
ambiguous: false
```
