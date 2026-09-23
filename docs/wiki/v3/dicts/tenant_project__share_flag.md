---
type: dict
title: tenant_project.share_flag
page_key: tenant_project__share_flag
belong: dicts
status: draft
anchors: [tenant_project.share_flag]
sources: ['database_profile:tenant_project.share_flag', 'database_schema:tenant_project.share_flag']
created: '2026-09-21'
updated: '2026-09-23'
contract_version: '0.1'
related: [tenant_project]
---

# tenant_project.share_flag

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。
物理列 `tenant_project.share_flag`，表页 [[tables/tenant_project]]。

## 取值

```ground:dict
dict: tenant_project__share_flag
fields: [tenant_project.share_flag]
values:
  N: {trust: proposed, label: 否}
  Y: {trust: proposed, label: 是}
triage: keep
```
