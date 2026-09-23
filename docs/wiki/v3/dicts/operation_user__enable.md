---
type: dict
title: operation_user.enable
page_key: operation_user__enable
belong: dicts
status: draft
anchors: [operation_user.enable]
sources: ['database_profile:operation_user.enable', 'database_schema:operation_user.enable']
created: '2026-09-21'
updated: '2026-09-23'
contract_version: '0.1'
related: [operation_user]
---

# operation_user.enable

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。
物理列 `operation_user.enable`，表页 [[tables/operation_user]]。

## 取值

```ground:dict
dict: operation_user__enable
fields: [operation_user.enable]
values:
  Y: {trust: proposed, label: 启用}
  N: {trust: proposed, label: 停用}
triage: keep
```
