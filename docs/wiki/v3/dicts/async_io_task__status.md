---
type: dict
title: async_io_task.status
page_key: async_io_task__status
belong: dicts
status: draft
anchors: [async_io_task.status]
sources: ['database_profile:async_io_task.status']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
related: [async_io_task]
---

# async_io_task.status

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。
物理列 `async_io_task.status`，表页 [[tables/async_io_task]]。

## 取值

```ground:dict
dict: async_io_task__status
fields: [async_io_task.status]
values:
  SUCCESS: {trust: proposed}
  FAILED: {trust: proposed}
  RUNNING: {trust: proposed}
triage: keep
```
