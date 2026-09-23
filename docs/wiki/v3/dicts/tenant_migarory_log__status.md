---
type: dict
title: tenant_migarory_log.status
page_key: tenant_migarory_log__status
belong: dicts
status: draft
anchors: [tenant_migarory_log.status]
sources: ['database_profile:tenant_migarory_log.status', 'database_schema:tenant_migarory_log.status']
created: '2026-09-21'
updated: '2026-09-23'
contract_version: '0.1'
related: [tenant_migarory_log]
---

# tenant_migarory_log.status

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。
物理列 `tenant_migarory_log.status`，表页 [[tables/tenant_migarory_log]]。

## 取值

```ground:dict
dict: tenant_migarory_log__status
fields: [tenant_migarory_log.status]
values:
  Y: {trust: proposed, label: 是}
  N: {trust: proposed, label: 否}
triage: keep
```
