---
type: process
title: 异步导入导出任务
page_key: async_io_task__status
belong: processes
domain: remaining
status: draft
anchors: [async_io_task.status]
field_targets: [async_io_task.status]
sources: ['code_path:AsyncIoTaskManager.java:84', 'code_path:AsyncIoTaskManager.java:114',
  'code_path:AsyncIoTaskManager.java:122', 'code_path:AsyncIoTaskManager.java:147']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [async_io_task]
---

# 异步导入导出任务

钉 async_io_task.status。PENDING → RUNNING → SUCCESS/FAILED。
枚举无 displayName，不编中文 label。


```ground:process
process: 异步导入导出任务
field: async_io_task.status
entry: 异步导入导出
stages:
- stage: 创建
  transitions:
  - from: PENDING
    event: create
    to: PENDING
    evidence: code_path:AsyncIoTaskManager.java:84
- stage: 执行
  transitions:
  - from: PENDING
    event: claim
    to: RUNNING
    evidence: code_path:AsyncIoTaskManager.java:114
- stage: 结束
  transitions:
  - from: RUNNING
    event: success
    to: SUCCESS
    evidence: code_path:AsyncIoTaskManager.java:122
  - from: RUNNING
    event: fail
    to: FAILED
    evidence: code_path:AsyncIoTaskManager.java:147
```

## 页面链接

- [[tables/async_io_task]]
- [[dicts/async_io_task__status]]
