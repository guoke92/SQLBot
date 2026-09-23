---
type: dict
title: async_io_task.enable
page_key: async_io_task__enable
belong: dicts
status: draft
anchors: [async_io_task.enable]
sources: ['database_profile:async_io_task.enable', 'database_schema:async_io_task.enable']
created: '2026-09-23'
updated: '2026-09-23'
contract_version: '0.1'
related: [async_io_task]
---

# async_io_task.enable

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。
物理列 `async_io_task.enable`，表页 [[tables/async_io_task]]。

## 取值

```ground:dict
dict: async_io_task__enable
fields: [async_io_task.enable]
values:
  Y: {trust: proposed, label: 启用}
  N: {trust: proposed, label: 停用, evidence: 'agent_review:binary_switch_pair'}
triage: keep
```
