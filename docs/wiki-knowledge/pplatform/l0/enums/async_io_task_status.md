---
type: enum
title: async_io_task_status
page_key: async_io_task_status
belong: enums
status: draft
aliases: []
anchors:
- async_io_task_status
sources:
- database_profile:async_io_task.status
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
recall: true
---

# async_io_task_status

L0 枚举候选：仅 profile 代码值，无代码 label。

## 取值

```ground:enum
enum: async_io_task_status
fields:
- async_io_task.status
values:
  SUCCESS:
    confidence: proposed
  FAILED:
    confidence: proposed
  RUNNING:
    confidence: proposed
ambiguous: false
```
