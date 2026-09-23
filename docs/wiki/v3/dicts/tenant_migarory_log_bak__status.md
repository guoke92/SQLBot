---
type: dict
title: tenant_migarory_log_bak.status
page_key: tenant_migarory_log_bak__status
belong: dicts
status: draft
anchors: [tenant_migarory_log_bak.status]
sources: ['database_profile:tenant_migarory_log_bak.status', 'database_schema:tenant_migarory_log_bak.status']
created: '2026-09-21'
updated: '2026-09-23'
contract_version: '0.1'
related: [tenant_migarory_log_bak]
---

# tenant_migarory_log_bak.status

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。
物理列 `tenant_migarory_log_bak.status`，表页 [[tables/tenant_migarory_log_bak]]。

## 取值

```ground:dict
dict: tenant_migarory_log_bak__status
fields: [tenant_migarory_log_bak.status]
values:
  Y: {trust: proposed, label: 是}
  N: {trust: proposed, label: 否}
triage: keep
```
