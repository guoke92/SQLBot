---
type: dict
title: async_io_task.is_deleted
page_key: async_io_task__is_deleted
belong: dicts
status: draft
anchors: [async_io_task.is_deleted]
sources: ['database_profile:async_io_task.is_deleted', 'database_schema:async_io_task.is_deleted']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
related: [async_io_task]
---

# async_io_task.is_deleted

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。 初审 hold：证据不足，保留待人工确认。
物理列 `async_io_task.is_deleted`，表页 [[tables/async_io_task]]。

## 取值

```ground:dict
dict: async_io_task__is_deleted
fields: [async_io_task.is_deleted]
values:
  '0': {trust: proposed, label: 否, evidence: 'database_schema:async_io_task.is_deleted'}
  '1': {trust: proposed, label: 是, evidence: 'database_schema:async_io_task.is_deleted'}
triage: hold
needs_review: true
```
