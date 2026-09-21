---
type: dict
title: operation_user.enable
page_key: operation_user__enable
belong: dicts
status: draft
anchors: [operation_user.enable]
sources: ['database_profile:operation_user.enable']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
related: [operation_user]
---

# operation_user.enable

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。
物理列 `operation_user.enable`，表页 [[tables/operation_user]]。

## 取值

```ground:dict
dict: operation_user__enable
fields: [operation_user.enable]
values:
  Y: {trust: proposed}
  N: {trust: proposed}
triage: keep
```
