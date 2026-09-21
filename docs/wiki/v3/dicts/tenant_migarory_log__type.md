---
type: dict
title: tenant_migarory_log.type
page_key: tenant_migarory_log__type
belong: dicts
status: draft
anchors: [tenant_migarory_log.type]
sources: ['database_profile:tenant_migarory_log.type']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [tenant_migarory_log]
---

# tenant_migarory_log.type

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 初审 hold：证据不足，保留待人工确认。
物理列 `tenant_migarory_log.type`，表页 [[tables/tenant_migarory_log]]。

## 取值

```ground:dict
dict: tenant_migarory_log__type
fields: [tenant_migarory_log.type]
values:
  migratoryProject: {trust: proposed}
  syncProject: {trust: proposed}
  migratoryCust: {trust: proposed}
  PROJECT_SYNC_VALIDATE: {trust: proposed}
  PROJECT_SYNC: {trust: proposed}
  CUST_PRODUCT_SYNC: {trust: proposed}
  TENANT_SYNC: {trust: proposed}
  TENANT_SYNC_VALIDATE: {trust: proposed}
  syncProduct: {trust: proposed}
  PROJECT_QUERY: {trust: proposed}
  migratoryTenant: {trust: proposed}
  migratoryOnTheWayCust: {trust: proposed}
  PRODUCT_SYNC: {trust: proposed}
  PRODUCT_SYNC_VALIDATE: {trust: proposed}
triage: hold
needs_review: true
```
