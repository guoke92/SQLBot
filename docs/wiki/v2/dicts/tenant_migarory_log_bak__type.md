---
type: dict
title: tenant_migarory_log_bak.type
page_key: tenant_migarory_log_bak__type
belong: dicts
status: draft
anchors: [tenant_migarory_log_bak.type]
sources: ['database_profile:tenant_migarory_log_bak.type']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
related: [tenant_migarory_log_bak]
---

# tenant_migarory_log_bak.type

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 初审 hold：证据不足，保留待人工确认。
物理列 `tenant_migarory_log_bak.type`，表页 [[tables/tenant_migarory_log_bak]]。

## 取值

```ground:dict
dict: tenant_migarory_log_bak__type
fields: [tenant_migarory_log_bak.type]
values:
  migratoryProject: {trust: proposed}
  PROJECT_SYNC: {trust: proposed}
  CUST_PRODUCT_SYNC: {trust: proposed}
  syncProject: {trust: proposed}
  TENANT_SYNC: {trust: proposed}
  syncProduct: {trust: proposed}
  PRODUCT_SYNC: {trust: proposed}
  migratoryCust: {trust: proposed}
  migratoryTenant: {trust: proposed}
  CREATED: {trust: proposed}
  DELETED: {trust: proposed}
  PROJECT_SYNC_VALIDATE: {trust: proposed}
  TENANT_SYNC_VALIDATE: {trust: proposed}
  EFFECTED: {trust: proposed}
triage: hold
needs_review: true
```
